"""Job / requisition + ingestion endpoints."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.adapters.upload_adapter import RawUpload
from app.api.schemas import BatchOut, JobCreate, JobOut, JobUpdateRubric
from app.core.default_rubric import default_rubric, default_tier_thresholds
from app.db.database import get_db
from app.db.models import CandidateORM, IngestionBatchORM, JobORM
from app.domain.schemas import Rubric, TierThresholds
from app.services import audit
from app.services.pipeline import ingest_and_score_uploads

router = APIRouter(tags=["jobs"])

_ALLOWED_EXT = (".pdf", ".docx", ".txt", ".md")


def _job_out(db: Session, job: JobORM) -> JobOut:
    count = db.query(CandidateORM).filter(CandidateORM.job_id == job.id).count()
    return JobOut(
        id=job.id, title=job.title, description=job.description,
        rubric=Rubric(**job.rubric), tier_thresholds=TierThresholds(**job.tier_thresholds),
        created_at=job.created_at, candidate_count=count,
    )


@router.get("/default-rubric", response_model=dict)
def get_default_rubric():
    """Editable starting point for a new job's rubric (§3.1)."""
    return {
        "rubric": default_rubric().model_dump(),
        "tier_thresholds": default_tier_thresholds().model_dump(),
    }


@router.post("/jobs", response_model=JobOut, status_code=201)
def create_job(body: JobCreate, db: Session = Depends(get_db)):
    rubric = body.rubric or default_rubric()
    if rubric.weight_total() != 100:
        raise HTTPException(422, f"Weighted criteria must sum to 100 (got {rubric.weight_total()}).")
    thresholds = body.tier_thresholds or default_tier_thresholds()
    job = JobORM(
        title=body.title, description=body.description,
        rubric=rubric.model_dump(), tier_thresholds=thresholds.model_dump(),
    )
    db.add(job)
    db.commit()
    audit.log(db, actor="user", action="CREATE_JOB", job_id=job.id,
              after={"title": job.title}, reason="Job created")
    return _job_out(db, job)


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobORM).order_by(JobORM.created_at.desc()).all()
    return [_job_out(db, j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(JobORM, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return _job_out(db, job)


@router.put("/jobs/{job_id}/rubric", response_model=JobOut)
def update_rubric(job_id: str, body: JobUpdateRubric, db: Session = Depends(get_db)):
    job = db.get(JobORM, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if body.rubric.weight_total() != 100:
        raise HTTPException(422, f"Weighted criteria must sum to 100 (got {body.rubric.weight_total()}).")
    before = {"rubric": job.rubric, "tier_thresholds": job.tier_thresholds}
    job.rubric = body.rubric.model_dump()
    if body.tier_thresholds:
        job.tier_thresholds = body.tier_thresholds.model_dump()
    db.commit()
    audit.log(db, actor="user", action="UPDATE_RUBRIC", job_id=job.id,
              before=before, after={"rubric": job.rubric, "tier_thresholds": job.tier_thresholds},
              reason="Rubric edited")
    return _job_out(db, job)


@router.post("/jobs/{job_id}/candidates", response_model=BatchOut, status_code=202)
async def upload_candidates(
    job_id: str,
    background: BackgroundTasks,
    files: list[UploadFile],
    db: Session = Depends(get_db),
):
    """Bulk (or single) resume upload. Parses + scores in the background."""
    job = db.get(JobORM, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if not files:
        raise HTTPException(422, "No files provided")

    uploads: list[RawUpload] = []
    for f in files:
        name = f.filename or "resume"
        if not name.lower().endswith(_ALLOWED_EXT):
            raise HTTPException(422, f"Unsupported file type: {name} (PDF, DOCX, TXT)")
        uploads.append(RawUpload(filename=name, data=await f.read()))

    batch = IngestionBatchORM(job_id=job_id, status="QUEUED", total=len(uploads))
    db.add(batch)
    db.commit()

    background.add_task(ingest_and_score_uploads, job_id, uploads, batch.id)
    return BatchOut(id=batch.id, job_id=job_id, status=batch.status,
                    total=batch.total, processed=0, failed=0)


@router.get("/jobs/{job_id}/batches/{batch_id}", response_model=BatchOut)
def batch_status(job_id: str, batch_id: str, db: Session = Depends(get_db)):
    batch = db.get(IngestionBatchORM, batch_id)
    if not batch or batch.job_id != job_id:
        raise HTTPException(404, "Batch not found")
    return BatchOut(id=batch.id, job_id=batch.job_id, status=batch.status,
                    total=batch.total, processed=batch.processed, failed=batch.failed)

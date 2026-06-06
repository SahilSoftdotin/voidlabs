"""Ingest + scoring pipeline.

Designed for batches of hundreds: parsing + scoring of a batch runs in a
background worker thread with a progress-tracked ``IngestionBatch`` so the API
stays responsive. Each candidate is parsed, persisted, scored, and audited
independently — one bad resume never sinks the batch.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.adapters.upload_adapter import RawUpload, UploadAdapter
from app.db.database import SessionLocal
from app.db.models import (
    CandidateORM,
    IngestionBatchORM,
    JobORM,
    ScoreORM,
)
from app.domain.schemas import Candidate, Score, ScoreStatus
from app.services import audit, repository
from app.services.scorers import build_scorer
from app.services.scoring_engine import ScoringEngine


def _job_context(job: JobORM) -> str:
    return f"TITLE: {job.title}\n\nDESCRIPTION:\n{job.description}"


def score_candidate(
    db: Session,
    candidate: Candidate,
    job: JobORM,
    *,
    engine: ScoringEngine | None = None,
    commit: bool = True,
) -> Score:
    """Score one already-persisted candidate and persist + audit the result."""
    engine = engine or ScoringEngine(build_scorer())
    rubric = repository.rubric_from_orm(job)
    thresholds = repository.thresholds_from_orm(job)
    try:
        score = engine.score(
            candidate, job.id, rubric, _job_context(job), thresholds
        )
    except Exception as exc:  # noqa: BLE001 - record, never crash the batch
        score = Score(
            candidate_id=candidate.internal_id, job_id=job.id,
            status=ScoreStatus.ERROR, engine_version="", error=str(exc),
        )

    row = (
        db.query(ScoreORM)
        .filter(ScoreORM.candidate_id == candidate.internal_id)
        .one_or_none()
    )
    if row is None:
        row = ScoreORM(candidate_id=candidate.internal_id, job_id=job.id)
        db.add(row)
    repository.apply_score_to_orm(score, row)

    audit.log(
        db,
        actor="system",
        action=f"AUTO_SCORE:{score.status.value}",
        candidate_id=candidate.internal_id,
        job_id=job.id,
        after={
            "status": score.status.value,
            "total": score.total,
            "tier": score.tier.value if score.tier else None,
            "engine_version": score.engine_version,
            "knockouts": [k.model_dump() for k in score.knockout_results],
            "per_criterion": [c.model_dump() for c in score.per_criterion],
        },
        reason="Automated scoring run",
        commit=False,
    )
    if commit:
        db.commit()
    return score


def ingest_and_score_uploads(
    job_id: str, uploads: list[RawUpload], batch_id: str
) -> None:
    """Background worker: parse -> persist -> score each upload for a job."""
    db = SessionLocal()
    try:
        job = db.get(JobORM, job_id)
        batch = db.get(IngestionBatchORM, batch_id)
        if job is None or batch is None:
            return
        batch.status = "RUNNING"
        db.commit()

        adapter = UploadAdapter()
        engine = ScoringEngine(build_scorer())

        for raw in uploads:
            job = db.get(JobORM, job_id)  # refresh handle each iteration
            try:
                candidate = adapter.normalize(raw)
                db.add(repository.candidate_to_orm(candidate, job_id))
                audit.log(
                    db, actor="system", action="INGEST_CANDIDATE",
                    candidate_id=candidate.internal_id, job_id=job_id,
                    after={"source": candidate.source.value,
                           "source_ref_id": candidate.source_ref_id},
                    reason="Resume uploaded and normalized", commit=False,
                )
                db.commit()
                score_candidate(db, candidate, job, engine=engine, commit=True)
                db.get(IngestionBatchORM, batch_id).processed += 1
            except Exception:  # noqa: BLE001 - skip the bad file, keep going
                db.rollback()
                db.get(IngestionBatchORM, batch_id).failed += 1
            db.commit()

        batch = db.get(IngestionBatchORM, batch_id)
        batch.status = "DONE"
        db.commit()
    finally:
        db.close()

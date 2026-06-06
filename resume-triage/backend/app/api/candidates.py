"""Candidate dashboard, detail, override, and interview-question endpoints."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.schemas import (
    CalibrationRequest,
    InterviewQuestionsUpdate,
    OverrideRequest,
)
from app.config import get_settings
from app.db.database import get_db
from app.db.models import (
    CalibrationOutcomeORM,
    CandidateORM,
    JobORM,
    ScoreORM,
)
from app.domain.schemas import ScoreStatus, Tier
from app.services import audit, repository
from app.services.pipeline import score_candidate

router = APIRouter(tags=["candidates"])


def _row_summary(c: CandidateORM, s: ScoreORM | None) -> dict:
    return {
        "id": c.id,
        "source": c.source,
        "name": (c.contact or {}).get("full_name"),
        "source_ref_id": c.source_ref_id,
        "status": s.status if s else ScoreStatus.PENDING.value,
        "total": s.total if s else 0.0,
        "tier": s.tier if s else None,
        "engine_version": s.engine_version if s else "",
    }


@router.get("/jobs/{job_id}/candidates")
def list_candidates(
    job_id: str,
    db: Session = Depends(get_db),
    tier: str | None = Query(None, description="A | B | C"),
    min_score: float | None = None,
    max_score: float | None = None,
    status: str | None = Query(None, description="SCORED | KNOCKED_OUT | ..."),
    criterion_id: str | None = Query(None, description="Filter by per-criterion threshold"),
    criterion_min: float | None = Query(None, ge=0, le=5),
    search: str | None = None,
    sort: str = Query("total_desc", description="total_desc | total_asc | name"),
):
    """Ranked candidate list with filters/sort/search (§3.4)."""
    if not db.get(JobORM, job_id):
        raise HTTPException(404, "Job not found")

    rows = (
        db.query(CandidateORM).filter(CandidateORM.job_id == job_id).all()
    )
    items = []
    for c in rows:
        s = c.score
        if tier and (not s or s.tier != tier):
            continue
        if status and (not s or s.status != status):
            continue
        if min_score is not None and (not s or s.total < min_score):
            continue
        if max_score is not None and (not s or s.total > max_score):
            continue
        if criterion_id and criterion_min is not None:
            crit = next((pc for pc in (s.per_criterion if s else []) if pc["criterion_id"] == criterion_id), None)
            if not crit or crit["raw_score"] < criterion_min:
                continue
        if search:
            hay = " ".join([
                (c.contact or {}).get("full_name") or "",
                c.source_ref_id or "",
                " ".join(c.skills or []),
                c.raw_text or "",
            ]).lower()
            if search.lower() not in hay:
                continue
        items.append(_row_summary(c, s))

    if sort == "total_asc":
        items.sort(key=lambda x: x["total"])
    elif sort == "name":
        items.sort(key=lambda x: (x["name"] or "").lower())
    else:  # total_desc default — knocked-out sink to the bottom
        items.sort(key=lambda x: (x["status"] != ScoreStatus.KNOCKED_OUT.value, x["total"]), reverse=True)

    return {"job_id": job_id, "count": len(items), "candidates": items}


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Full detail: parsed resume + per-criterion breakdown + interview questions."""
    c = db.get(CandidateORM, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    candidate = repository.candidate_from_orm(c)
    score = repository.score_from_orm(c.score) if c.score else None
    return {
        "candidate": candidate.model_dump(),
        "score": score.model_dump() if score else None,
        "has_file": bool(c.original_file_ref),
    }


@router.get("/candidates/{candidate_id}/file")
def download_file(candidate_id: str, db: Session = Depends(get_db)):
    c = db.get(CandidateORM, candidate_id)
    if not c or not c.original_file_ref:
        raise HTTPException(404, "Original file not found")
    path = Path(get_settings().storage_dir) / c.original_file_ref
    if not path.exists():
        raise HTTPException(404, "Original file missing from storage")
    return FileResponse(path, filename=c.source_ref_id or c.original_file_ref)


@router.post("/candidates/{candidate_id}/rescore")
def rescore(candidate_id: str, db: Session = Depends(get_db)):
    c = db.get(CandidateORM, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    job = db.get(JobORM, c.job_id)
    candidate = repository.candidate_from_orm(c)
    score = score_candidate(db, candidate, job)
    return score.model_dump()


@router.post("/candidates/{candidate_id}/override")
def override_score(candidate_id: str, body: OverrideRequest, db: Session = Depends(get_db)):
    """Human override of a single criterion score (required reason, logged §3.4)."""
    c = db.get(CandidateORM, candidate_id)
    if not c or not c.score:
        raise HTTPException(404, "Candidate score not found")
    s = c.score
    per = list(s.per_criterion or [])
    target = next((pc for pc in per if pc["criterion_id"] == body.criterion_id), None)
    if not target:
        raise HTTPException(404, f"Criterion {body.criterion_id} not in this score")

    before = dict(target)
    if not target.get("overridden"):
        target["original_raw_score"] = target["raw_score"]
    target["raw_score"] = body.new_raw_score
    target["weighted_score"] = round(body.new_raw_score / 5.0 * target["weight"], 2)
    target["overridden"] = True
    target["justification"] = f"[Manual override] {body.reason}"

    s.per_criterion = per
    s.total = round(sum(pc["weighted_score"] for pc in per), 2)
    thresholds = repository.thresholds_from_orm(db.get(JobORM, c.job_id))
    s.tier = thresholds.tier_for(s.total).value
    # Flag from the ORM that this row changed (JSON reassignment handles it).
    db.add(s)
    audit.log(db, actor="user", action="OVERRIDE_SCORE",
              candidate_id=candidate_id, job_id=c.job_id,
              before=before, after=dict(target), reason=body.reason)
    return repository.score_from_orm(s).model_dump()


@router.post("/candidates/{candidate_id}/interview-questions/regenerate")
def regenerate_questions(candidate_id: str, db: Session = Depends(get_db)):
    """Regenerate the 5 manager interview questions on demand (§3.6)."""
    c = db.get(CandidateORM, candidate_id)
    if not c or not c.score:
        raise HTTPException(404, "Candidate score not found")
    job = db.get(JobORM, c.job_id)
    candidate = repository.candidate_from_orm(c)
    from app.services.scorers import build_scorer

    view = candidate.scoring_view()
    from app.services.bias import assert_scoring_view_clean

    assert_scoring_view_clean(candidate, view)
    scorer = build_scorer()
    questions = scorer.generate_interview_questions(
        view, f"TITLE: {job.title}\n\n{job.description}"
    )
    c.score.interview_questions = [q.model_dump() for q in questions]
    db.add(c.score)
    audit.log(db, actor="user", action="REGENERATE_INTERVIEW_QUESTIONS",
              candidate_id=candidate_id, job_id=c.job_id,
              reason="Manager regenerated interview questions")
    return {"interview_questions": c.score.interview_questions}


@router.put("/candidates/{candidate_id}/interview-questions")
def update_questions(candidate_id: str, body: InterviewQuestionsUpdate, db: Session = Depends(get_db)):
    """Manager edits/adds/removes questions before the interview (§3.6)."""
    c = db.get(CandidateORM, candidate_id)
    if not c or not c.score:
        raise HTTPException(404, "Candidate score not found")
    c.score.interview_questions = [q.model_dump() for q in body.questions]
    db.add(c.score)
    audit.log(db, actor="user", action="EDIT_INTERVIEW_QUESTIONS",
              candidate_id=candidate_id, job_id=c.job_id,
              reason="Manager edited interview questions")
    return {"interview_questions": c.score.interview_questions}


@router.post("/candidates/{candidate_id}/calibration")
def record_calibration(candidate_id: str, body: CalibrationRequest, db: Session = Depends(get_db)):
    """Calibration hook: record real interview/hire outcome vs score (§4)."""
    c = db.get(CandidateORM, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    rec = CalibrationOutcomeORM(
        candidate_id=candidate_id, job_id=c.job_id,
        outcome=body.outcome, notes=body.notes,
    )
    db.add(rec)
    audit.log(db, actor="user", action="RECORD_CALIBRATION",
              candidate_id=candidate_id, job_id=c.job_id,
              after={"outcome": body.outcome}, reason=body.notes or "Outcome recorded")
    return {"ok": True, "outcome": body.outcome}

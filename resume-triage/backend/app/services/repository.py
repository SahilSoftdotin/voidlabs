"""Mapping helpers between ORM rows and Pydantic domain objects."""
from __future__ import annotations

from app.db.models import CandidateORM, JobORM, ScoreORM
from app.domain.schemas import (
    Candidate,
    CandidateSource,
    Contact,
    Education,
    Rubric,
    Score,
    ScoreStatus,
    Tier,
    TierThresholds,
    WorkExperience,
)


def candidate_from_orm(row: CandidateORM) -> Candidate:
    return Candidate(
        internal_id=row.id,
        source=CandidateSource(row.source),
        source_ref_id=row.source_ref_id,
        contact=Contact(**(row.contact or {})),
        work_history=[WorkExperience(**w) for w in (row.work_history or [])],
        education=[Education(**e) for e in (row.education or [])],
        skills=list(row.skills or []),
        certifications=list(row.certifications or []),
        raw_text=row.raw_text or "",
        original_file_ref=row.original_file_ref,
        ingested_at=row.ingested_at,
    )


def candidate_to_orm(candidate: Candidate, job_id: str) -> CandidateORM:
    return CandidateORM(
        id=candidate.internal_id,
        job_id=job_id,
        source=candidate.source.value,
        source_ref_id=candidate.source_ref_id,
        contact=candidate.contact.model_dump(),
        work_history=[w.model_dump() for w in candidate.work_history],
        education=[e.model_dump() for e in candidate.education],
        skills=list(candidate.skills),
        certifications=list(candidate.certifications),
        raw_text=candidate.raw_text,
        original_file_ref=candidate.original_file_ref,
    )


def rubric_from_orm(row: JobORM) -> Rubric:
    return Rubric(**row.rubric) if row.rubric else Rubric()


def thresholds_from_orm(row: JobORM) -> TierThresholds:
    return TierThresholds(**row.tier_thresholds) if row.tier_thresholds else TierThresholds()


def apply_score_to_orm(score: Score, row: ScoreORM) -> None:
    row.status = score.status.value
    row.per_criterion = [c.model_dump() for c in score.per_criterion]
    row.knockout_results = [k.model_dump() for k in score.knockout_results]
    row.total = score.total
    row.tier = score.tier.value if score.tier else None
    row.engine_version = score.engine_version
    row.interview_questions = [q.model_dump() for q in score.interview_questions]
    row.error = score.error
    row.scored_at = score.scored_at


def score_from_orm(row: ScoreORM) -> Score:
    return Score(
        candidate_id=row.candidate_id,
        job_id=row.job_id,
        status=ScoreStatus(row.status),
        per_criterion=row.per_criterion or [],
        knockout_results=row.knockout_results or [],
        total=row.total,
        tier=Tier(row.tier) if row.tier else None,
        engine_version=row.engine_version,
        interview_questions=row.interview_questions or [],
        error=row.error,
        scored_at=row.scored_at,
    )

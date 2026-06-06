"""API request/response models."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.schemas import (
    InterviewQuestion,
    Rubric,
    TierThresholds,
)


class JobCreate(BaseModel):
    title: str
    description: str = ""
    rubric: Rubric | None = None  # defaults applied server-side if omitted
    tier_thresholds: TierThresholds | None = None


class JobUpdateRubric(BaseModel):
    rubric: Rubric
    tier_thresholds: TierThresholds | None = None


class JobOut(BaseModel):
    id: str
    title: str
    description: str
    rubric: Rubric
    tier_thresholds: TierThresholds
    created_at: datetime
    candidate_count: int = 0


class BatchOut(BaseModel):
    id: str
    job_id: str
    status: str
    total: int
    processed: int
    failed: int


class OverrideRequest(BaseModel):
    criterion_id: str
    new_raw_score: float = Field(ge=0, le=5)
    reason: str = Field(min_length=1)  # required rationale (logged)


class InterviewQuestionsUpdate(BaseModel):
    questions: list[InterviewQuestion]


class CalibrationRequest(BaseModel):
    outcome: str  # INTERVIEWED | HIRED | REJECTED | PASSED_ON | ...
    notes: str | None = None

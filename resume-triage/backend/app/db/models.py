"""SQLAlchemy ORM models.

Structured sub-documents (contact, rubric, per-criterion scores, etc.) are
stored as JSON columns — portable across SQLite (dev) and PostgreSQL (prod) —
and (de)serialized through the Pydantic domain schemas at the repository layer.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class JobORM(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    rubric: Mapped[dict] = mapped_column(JSON, default=dict)
    tier_thresholds: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidates: Mapped[list["CandidateORM"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class CandidateORM(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    source: Mapped[str] = mapped_column(String, default="UPLOAD")
    source_ref_id: Mapped[str | None] = mapped_column(String, nullable=True)

    contact: Mapped[dict] = mapped_column(JSON, default=dict)
    work_history: Mapped[list] = mapped_column(JSON, default=list)
    education: Mapped[list] = mapped_column(JSON, default=list)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    original_file_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped["JobORM"] = relationship(back_populates="candidates")
    score: Mapped["ScoreORM"] = relationship(
        back_populates="candidate", cascade="all, delete-orphan", uselist=False
    )


class ScoreORM(Base):
    __tablename__ = "scores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"), unique=True, index=True
    )
    job_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    per_criterion: Mapped[list] = mapped_column(JSON, default=list)
    knockout_results: Mapped[list] = mapped_column(JSON, default=list)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    tier: Mapped[str | None] = mapped_column(String, nullable=True)
    engine_version: Mapped[str] = mapped_column(String, default="")
    interview_questions: Mapped[list] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    scored_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    candidate: Mapped["CandidateORM"] = relationship(back_populates="score")


class AuditEntryORM(Base):
    __tablename__ = "audit_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    actor: Mapped[str] = mapped_column(String)  # "system" | "user"
    action: Mapped[str] = mapped_column(String)
    candidate_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    job_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    before: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CalibrationOutcomeORM(Base):
    """Calibration hook (§4): record real interview/hire outcomes vs scores so
    the rubric can be validated and tuned later."""

    __tablename__ = "calibration_outcomes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    candidate_id: Mapped[str] = mapped_column(String, index=True)
    job_id: Mapped[str] = mapped_column(String, index=True)
    outcome: Mapped[str] = mapped_column(String)  # e.g. INTERVIEWED / HIRED / REJECTED / PASSED_ON
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IngestionBatchORM(Base):
    """Tracks async batch ingest/scoring progress (designed for hundreds)."""

    __tablename__ = "ingestion_batches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    job_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="QUEUED")  # QUEUED/RUNNING/DONE
    total: Mapped[int] = mapped_column(default=0)
    processed: Mapped[int] = mapped_column(default=0)
    failed: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

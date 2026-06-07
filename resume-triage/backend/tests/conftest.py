"""Test fixtures. Force the deterministic mock scorer so tests run offline."""
from __future__ import annotations

import os

os.environ.setdefault("SCORING_BACKEND", "mock")
os.environ.setdefault("RESUME_NORMALIZER", "heuristic")
os.environ.setdefault("DATABASE_URL", "sqlite:///./storage/test_triage.db")

import pytest

from app.domain.schemas import (
    Candidate,
    CandidateSource,
    Contact,
    Education,
    WorkExperience,
)


@pytest.fixture
def sample_candidate() -> Candidate:
    return Candidate(
        internal_id="cand-1",
        source=CandidateSource.UPLOAD,
        source_ref_id="jane.pdf",
        contact=Contact(
            full_name="Jane Q. Applicant",
            email="jane@example.com",
            phone="555-123-4567",
            location="Austin, TX",
        ),
        work_history=[
            WorkExperience(
                title="Senior Backend Engineer",
                organization="Acme",
                is_current=True,
                highlights=[
                    "Cut p99 latency by 40% across 12 microservices",
                    "Led migration of 3 services to Python and FastAPI",
                ],
            ),
            WorkExperience(
                title="Backend Engineer",
                organization="Beta Corp",
                highlights=["Built REST APIs serving 2 million requests/day"],
            ),
        ],
        education=[
            Education(institution="Prestige University", degree="BS",
                      field_of_study="Computer Science"),
        ],
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        certifications=["AWS Solutions Architect"],
        raw_text="Jane Q. Applicant jane@example.com ... Python FastAPI PostgreSQL",
    )

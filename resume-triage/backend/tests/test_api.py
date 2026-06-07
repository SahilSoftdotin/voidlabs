"""End-to-end API flow: create job -> set rubric -> upload -> ranked list ->
detail -> override -> export -> audit. Uses the in-process mock scorer."""
from __future__ import annotations

import os

os.environ.setdefault("SCORING_BACKEND", "mock")
os.environ.setdefault("RESUME_NORMALIZER", "heuristic")
os.environ.setdefault("DATABASE_URL", "sqlite:///./storage/test_api.db")

import pytest
from fastapi.testclient import TestClient

from app.db.database import engine, init_db
from app.db.models import Base
from app.main import app

RESUME = b"""Jane Applicant
jane@example.com | 555-222-3333 | Austin, TX

Experience
Senior Backend Engineer at Acme 2021 - Present
- Cut p99 latency by 40% across 12 microservices
- Led migration of 3 services to Python and FastAPI
Backend Engineer at Beta 2018 - 2021
- Built REST APIs serving 2 million requests per day

Skills
Python, FastAPI, PostgreSQL, Docker, Kubernetes

Education
BS in Computer Science, Prestige University
"""


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_full_flow(client):
    # Create a job (default rubric applied)
    r = client.post("/api/jobs", json={
        "title": "Backend Engineer",
        "description": "Python, FastAPI, PostgreSQL, Docker, Kubernetes, microservices.",
    })
    assert r.status_code == 201, r.text
    job = r.json()
    job_id = job["id"]
    assert job["rubric"]["weighted_criteria"]

    # Bulk upload (single file here). BackgroundTasks run inline under TestClient.
    r = client.post(
        f"/api/jobs/{job_id}/candidates",
        files=[("files", ("jane.txt", RESUME, "text/plain"))],
    )
    assert r.status_code == 202, r.text
    batch = r.json()
    assert batch["total"] == 1

    # Batch should have completed
    r = client.get(f"/api/jobs/{job_id}/batches/{batch['id']}")
    assert r.json()["status"] == "DONE"
    assert r.json()["processed"] == 1

    # Ranked candidate list
    r = client.get(f"/api/jobs/{job_id}/candidates")
    data = r.json()
    assert data["count"] == 1
    cand = data["candidates"][0]
    assert cand["status"] == "SCORED"
    cid = cand["id"]

    # Detail: per-criterion breakdown + interview questions
    r = client.get(f"/api/candidates/{cid}")
    detail = r.json()
    assert detail["score"]["per_criterion"]
    assert len(detail["score"]["interview_questions"]) == 5
    # Bias: the scoring breakdown must not contain the name.
    import json as _json
    assert "jane" not in _json.dumps(detail["score"]).lower()

    # Override a criterion (required reason, logged)
    r = client.post(f"/api/candidates/{cid}/override", json={
        "criterion_id": "skills_match", "new_raw_score": 5.0,
        "reason": "Verified depth in FastAPI during screen call",
    })
    assert r.status_code == 200, r.text
    overridden = r.json()
    sm = next(c for c in overridden["per_criterion"] if c["criterion_id"] == "skills_match")
    assert sm["overridden"] and sm["raw_score"] == 5.0

    # Export CSV + JSON
    assert client.get(f"/api/jobs/{job_id}/export?format=csv").status_code == 200
    assert client.get(f"/api/jobs/{job_id}/export?format=json").status_code == 200

    # Audit log captured ingest + auto-score + override
    r = client.get(f"/api/jobs/{job_id}/audit")
    actions = {e["action"] for e in r.json()["entries"]}
    assert any(a.startswith("AUTO_SCORE") for a in actions)
    assert "OVERRIDE_SCORE" in actions
    assert "INGEST_CANDIDATE" in actions


def test_rubric_must_sum_to_100(client):
    r = client.post("/api/jobs", json={
        "title": "Bad rubric",
        "rubric": {"knockouts": [], "weighted_criteria": [
            {"id": "x", "name": "X", "weight": 50, "scoring_guidance": ""}
        ]},
    })
    assert r.status_code == 422

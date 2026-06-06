"""FastAPI application entrypoint.

Single-user MVP (no auth). Authentication/authorization (recruiter vs. hiring
manager roles) is a deliberate future seam — wire an auth dependency here.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import ENGINE_VERSION
from app.api import audit_export, candidates, jobs
from app.config import get_settings
from app.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.ensure_dirs()
    init_db()
    yield


app = FastAPI(
    title="Resume Scoring & Candidate Triage",
    version=ENGINE_VERSION,
    description="Scores and tiers resumes against a job-specific rubric. Triage, not auto-reject.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "engine_version": ENGINE_VERSION,
        "scoring_backend": "llm" if settings.use_llm_scoring else "mock",
        "normalizer": "llm" if settings.use_llm_normalizer else "heuristic",
    }


app.include_router(jobs.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(audit_export.router, prefix="/api")

"""Audit-log retrieval and ranked-results export (§3.4, §3.5)."""
from __future__ import annotations

import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AuditEntryORM, CandidateORM, JobORM, ScoreORM

router = APIRouter(tags=["audit & export"])


def _audit_out(e: AuditEntryORM) -> dict:
    return {
        "id": e.id, "actor": e.actor, "action": e.action,
        "candidate_id": e.candidate_id, "job_id": e.job_id,
        "before": e.before, "after": e.after, "reason": e.reason,
        "timestamp": e.timestamp.isoformat(),
    }


@router.get("/jobs/{job_id}/audit")
def job_audit(job_id: str, db: Session = Depends(get_db), limit: int = Query(500, le=5000)):
    entries = (
        db.query(AuditEntryORM).filter(AuditEntryORM.job_id == job_id)
        .order_by(AuditEntryORM.timestamp.desc()).limit(limit).all()
    )
    return {"job_id": job_id, "entries": [_audit_out(e) for e in entries]}


@router.get("/candidates/{candidate_id}/audit")
def candidate_audit(candidate_id: str, db: Session = Depends(get_db)):
    entries = (
        db.query(AuditEntryORM).filter(AuditEntryORM.candidate_id == candidate_id)
        .order_by(AuditEntryORM.timestamp.desc()).all()
    )
    return {"candidate_id": candidate_id, "entries": [_audit_out(e) for e in entries]}


def _export_rows(db: Session, job_id: str) -> list[dict]:
    pairs = (
        db.query(CandidateORM, ScoreORM)
        .outerjoin(ScoreORM, ScoreORM.candidate_id == CandidateORM.id)
        .filter(CandidateORM.job_id == job_id).all()
    )
    rows = []
    for c, s in pairs:
        row = {
            "candidate_id": c.id,
            "name": (c.contact or {}).get("full_name"),
            "source": c.source,
            "source_ref_id": c.source_ref_id,
            "status": s.status if s else "PENDING",
            "total": s.total if s else 0.0,
            "tier": s.tier if s else None,
            "engine_version": s.engine_version if s else "",
        }
        if s:
            for pc in s.per_criterion or []:
                row[f"crit:{pc['criterion_id']}"] = pc["raw_score"]
        rows.append(row)
    rows.sort(key=lambda r: (r["status"] != "KNOCKED_OUT", r["total"]), reverse=True)
    return rows


@router.get("/jobs/{job_id}/export")
def export_results(job_id: str, format: str = Query("csv", pattern="^(csv|json)$"),
                   db: Session = Depends(get_db)):
    if not db.get(JobORM, job_id):
        raise HTTPException(404, "Job not found")
    rows = _export_rows(db, job_id)
    if format == "json":
        return Response(json.dumps(rows, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="job_{job_id}_results.json"'})
    # CSV
    fieldnames: list[str] = []
    for r in rows:
        for k in r:
            if k not in fieldnames:
                fieldnames.append(k)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames or ["candidate_id"])
    writer.writeheader()
    writer.writerows(rows)
    return Response(buf.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="job_{job_id}_results.csv"'})

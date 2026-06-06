"""Audit log service (§3.5).

Every automated score, knockout decision, and human override is logged with a
timestamp, the inputs used, and a rationale. This is the EEOC / adverse-impact
defensibility trail.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import AuditEntryORM


def log(
    db: Session,
    *,
    actor: str,
    action: str,
    candidate_id: str | None = None,
    job_id: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
    reason: str | None = None,
    commit: bool = True,
) -> AuditEntryORM:
    entry = AuditEntryORM(
        actor=actor,
        action=action,
        candidate_id=candidate_id,
        job_id=job_id,
        before=before,
        after=after,
        reason=reason,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry

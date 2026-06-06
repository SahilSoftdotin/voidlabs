"""WorkdayAdapter — FUTURE integration. Clean seam only; do NOT build yet (§6).

When implemented, this becomes a drop-in ``CandidateSourceAdapter`` and the
scoring core does not change.

Integration notes (verify current API docs at integration time — these change):
  * Workday Recruiting via the Workday REST API + Reports-as-a-Service (RaaS).
  * Requires tenant config + credentials (OAuth 2.0 client-credentials).
  * Secrets come from env vars only (see ``app.adapters.auth``), never committed.

Implementation sketch:
  * ``fetch_candidates(job_ref)`` -> call the requisition's candidate RaaS report.
  * ``normalize(raw)`` -> map Workday's candidate/worker fields into ``Candidate``
    (contact -> Contact, work experience -> WorkExperience, etc.), setting
    ``source=WORKDAY`` and ``source_ref_id`` to the Workday candidate id.
"""
from __future__ import annotations

from app.domain.schemas import Candidate, CandidateSource


class WorkdayAdapter:  # pragma: no cover - not implemented in MVP
    source_name = CandidateSource.WORKDAY.value

    def fetch_candidates(self, job_ref: str, **kwargs) -> list[Candidate]:
        raise NotImplementedError(
            "Workday integration is a future seam. See module docstring; verify "
            "Workday REST + RaaS API docs and configure tenant credentials first."
        )

    def normalize(self, raw: object) -> Candidate:
        raise NotImplementedError("TODO: map Workday candidate fields -> Candidate")

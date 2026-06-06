"""LinkedInAdapter — FUTURE integration. Clean seam only; do NOT build yet (§6).

When implemented, this becomes a drop-in ``CandidateSourceAdapter`` and the
scoring core does not change.

Integration notes (verify current API docs at integration time — these change):
  * LinkedIn Talent Solutions / Recruiter System Connect (RSC) APIs.
  * Requires LinkedIn partner approval + OAuth (3-legged) authorization.
  * Secrets come from env vars only (see ``app.adapters.auth``), never committed.

Implementation sketch:
  * ``fetch_candidates(job_ref)`` -> pull applicants/sourced profiles for the job.
  * ``normalize(raw)`` -> map LinkedIn profile fields into ``Candidate`` with
    ``source=LINKEDIN`` and ``source_ref_id`` set to the LinkedIn member/urn id.
"""
from __future__ import annotations

from app.domain.schemas import Candidate, CandidateSource


class LinkedInAdapter:  # pragma: no cover - not implemented in MVP
    source_name = CandidateSource.LINKEDIN.value

    def fetch_candidates(self, job_ref: str, **kwargs) -> list[Candidate]:
        raise NotImplementedError(
            "LinkedIn integration is a future seam. See module docstring; verify "
            "LinkedIn Talent Solutions / RSC API docs, obtain partner approval, "
            "and configure OAuth credentials first."
        )

    def normalize(self, raw: object) -> Candidate:
        raise NotImplementedError("TODO: map LinkedIn profile fields -> Candidate")

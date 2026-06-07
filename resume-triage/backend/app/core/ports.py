"""Port interfaces (hexagonal / ports-and-adapters).

The scoring core depends ONLY on these abstractions and on the normalized
domain schema — never on a concrete vendor. Adding Workday or LinkedIn later is
a new implementation of ``CandidateSourceAdapter`` (and optionally
``ATSWriteAdapter``); the core does not change. This is what makes the
acceptance criterion "adding a new source requires only a new adapter" hold.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.schemas import (
    Candidate,
    CandidateScoringView,
    CriterionScore,
    InterviewQuestion,
    KnockoutResult,
    Rubric,
)


@runtime_checkable
class CandidateSourceAdapter(Protocol):
    """A source of candidates for a given job/requisition.

    MVP: ``UploadAdapter``. Future: ``WorkdayAdapter``, ``LinkedInAdapter``.
    """

    source_name: str

    def fetch_candidates(self, job_ref: str, **kwargs) -> list[Candidate]:
        """Pull raw candidates for a job and return them normalized."""
        ...

    def normalize(self, raw: object) -> Candidate:
        """Map one vendor-specific raw record into the normalized schema."""
        ...


@runtime_checkable
class Scorer(Protocol):
    """Pluggable scoring strategy (LLM-assisted or deterministic mock).

    Implementations receive ONLY the bias-safe ``CandidateScoringView``.
    Every method must return explainable output (a justification string).
    """

    engine_name: str

    def evaluate_knockouts(
        self, view: CandidateScoringView, rubric: Rubric
    ) -> list[KnockoutResult]:
        ...

    def score_criteria(
        self, view: CandidateScoringView, rubric: Rubric, job_context: str
    ) -> list[CriterionScore]:
        ...

    def generate_interview_questions(
        self, view: CandidateScoringView, job_context: str, n: int = 5
    ) -> list[InterviewQuestion]:
        ...


@runtime_checkable
class ATSWriteAdapter(Protocol):
    """(Future) push results / dispositions back into an ATS.

    Not implemented in the MVP — left as a clean seam (§6)."""

    target_name: str

    def push_disposition(self, job_ref: str, candidate_ref: str, disposition: str) -> None:
        ...

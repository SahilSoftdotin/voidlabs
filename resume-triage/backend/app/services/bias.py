"""Bias & compliance guard (§2, principle 3).

Two layers of defense:

1. Structural — the scorer is only ever handed a ``CandidateScoringView``,
   which has no field for any protected attribute (name, gender, age/DOB,
   photo, marital status, nationality) and drops institution names.

2. Runtime assertion — ``assert_scoring_view_clean`` re-checks that none of a
   candidate's known contact values leaked into the serialized view that goes
   to the scorer. This makes the guarantee testable and fails loudly if a
   future change accidentally widens the view.
"""
from __future__ import annotations

import json

from app.domain.schemas import Candidate, CandidateScoringView

# Names of attributes that must never be modeled or scored. Kept here as the
# single documented source of truth for audits / compliance review.
PROTECTED_ATTRIBUTES = (
    "name",
    "gender",
    "age",
    "date_of_birth",
    "dob",
    "photo",
    "marital_status",
    "nationality",
    "institution_prestige",
)


class BiasLeakError(RuntimeError):
    """Raised when identifying / protected data is found in the scoring view."""


def assert_scoring_view_clean(candidate: Candidate, view: CandidateScoringView) -> None:
    """Fail loudly if any contact/identity value leaked into the scoring view."""
    blob = json.dumps(view.model_dump(), default=str).lower()

    sensitive_values: list[str] = []
    c = candidate.contact
    for val in (c.full_name, c.email, c.phone, c.location):
        if val and len(val.strip()) >= 3:
            sensitive_values.append(val.strip().lower())
    # Institution names must not reach the scorer (no university-prestige bias).
    for edu in candidate.education:
        if edu.institution and len(edu.institution.strip()) >= 3:
            sensitive_values.append(edu.institution.strip().lower())

    leaked = [v for v in sensitive_values if v in blob]
    if leaked:
        raise BiasLeakError(
            "Protected/identifying data leaked into the scoring view: "
            + ", ".join(sorted(set(leaked)))
        )

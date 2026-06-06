"""Normalized, source-agnostic domain schemas.

Every candidate source (UPLOAD today; WORKDAY / LINKEDIN later) maps INTO these
shapes. The scoring core only ever sees this normalized model — never a vendor
payload — which is what lets new sources be added as drop-in adapters (§6).

Bias & compliance (§2, principle 3) is enforced structurally:
``Contact`` and university/institution names are stored for the human reviewer
but are deliberately kept OUT of the object the scorer reads. See
``Candidate.scoring_view`` and ``app.services.bias``.
"""
from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class CandidateSource(str, enum.Enum):
    UPLOAD = "UPLOAD"
    WORKDAY = "WORKDAY"
    LINKEDIN = "LINKEDIN"


class Tier(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class ScoreStatus(str, enum.Enum):
    PENDING = "PENDING"
    SCORED = "SCORED"
    KNOCKED_OUT = "KNOCKED_OUT"
    ERROR = "ERROR"


class KnockoutType(str, enum.Enum):
    """How a knockout filter is evaluated.

    Keep this list short and truly non-negotiable (§4 Stage 1)."""

    WORK_AUTHORIZATION = "WORK_AUTHORIZATION"
    REQUIRED_CERTIFICATION = "REQUIRED_CERTIFICATION"
    LOCATION_CONSTRAINT = "LOCATION_CONSTRAINT"
    REQUIRED_SKILL = "REQUIRED_SKILL"
    CUSTOM = "CUSTOM"


# ---------------------------------------------------------------------------
# Candidate sub-structures
# ---------------------------------------------------------------------------
class Contact(BaseModel):
    """Contact / identity info. Stored for the reviewer, EXCLUDED from scoring.

    Protected attributes (gender, age/DOB, photo, marital status, nationality)
    are intentionally NOT modeled here — the parser does not extract them, so
    they cannot leak into any downstream computation.
    """

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)


class WorkExperience(BaseModel):
    title: str | None = None
    organization: str | None = None
    start_date: str | None = None  # free-form ("2021", "Jan 2021") — source varies
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str | None = None  # stored, but EXCLUDED from scoring (no prestige bias)
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class Candidate(BaseModel):
    internal_id: str
    source: CandidateSource
    source_ref_id: str | None = None  # vendor id (Workday req candidate id, etc.)

    contact: Contact = Field(default_factory=Contact)
    work_history: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    raw_text: str = ""
    original_file_ref: str | None = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

    def scoring_view(self) -> "CandidateScoringView":
        """Project to the bias-safe view the scorer is allowed to read.

        Drops contact/identity and institution names. This is the single
        chokepoint that makes "scoring never reads protected attributes"
        enforceable and testable (acceptance criteria)."""
        return CandidateScoringView(
            candidate_id=self.internal_id,
            work_history=[
                WorkExperience(
                    title=w.title,
                    organization=w.organization,
                    start_date=w.start_date,
                    end_date=w.end_date,
                    is_current=w.is_current,
                    description=w.description,
                    highlights=list(w.highlights),
                )
                for w in self.work_history
            ],
            education=[
                # institution deliberately dropped — only degree/field count
                EducationScoringView(
                    degree=e.degree, field_of_study=e.field_of_study
                )
                for e in self.education
            ],
            skills=list(self.skills),
            certifications=list(self.certifications),
        )


# ---------------------------------------------------------------------------
# Bias-safe scoring projection
# ---------------------------------------------------------------------------
class EducationScoringView(BaseModel):
    degree: str | None = None
    field_of_study: str | None = None


class CandidateScoringView(BaseModel):
    """Exactly the fields the scoring engine + interview generator may read.

    Notably absent: any Contact field (name/email/phone/location), institution
    names, and there is no place for gender/age/DOB/photo/marital status/
    nationality. If it isn't here, the scorer cannot use it."""

    candidate_id: str
    work_history: list[WorkExperience] = Field(default_factory=list)
    education: list[EducationScoringView] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Rubric
# ---------------------------------------------------------------------------
class Knockout(BaseModel):
    id: str
    name: str
    type: KnockoutType = KnockoutType.CUSTOM
    description: str = ""
    # Free-form config, e.g. {"required_terms": ["RN license"]}.
    config: dict = Field(default_factory=dict)


class WeightedCriterion(BaseModel):
    id: str
    name: str
    weight: int = Field(ge=0, le=100)
    scoring_guidance: str = ""


class Rubric(BaseModel):
    knockouts: list[Knockout] = Field(default_factory=list)
    weighted_criteria: list[WeightedCriterion] = Field(default_factory=list)

    def weight_total(self) -> int:
        return sum(c.weight for c in self.weighted_criteria)


class TierThresholds(BaseModel):
    """Configurable A/B/C bands (§4 Stage 3)."""

    a_min: float = 75.0
    b_min: float = 55.0

    def tier_for(self, total: float) -> Tier:
        if total >= self.a_min:
            return Tier.A
        if total >= self.b_min:
            return Tier.B
        return Tier.C


# ---------------------------------------------------------------------------
# Scoring results (explainable, per §2 principle 5)
# ---------------------------------------------------------------------------
class CriterionScore(BaseModel):
    criterion_id: str
    criterion_name: str
    raw_score: float = Field(ge=0, le=5)  # 0–5
    weight: int
    weighted_score: float  # raw_score/5 * weight  -> contributes to 0–100 total
    justification: str
    overridden: bool = False
    original_raw_score: float | None = None


class KnockoutResult(BaseModel):
    knockout_id: str
    knockout_name: str
    passed: bool
    justification: str


class InterviewQuestion(BaseModel):
    question: str
    resume_item: str  # the specific resume item being probed (context for the manager)
    type: str  # "technical" | "behavioral"
    signal: str  # one line: what good vs. weak answers look like


class Score(BaseModel):
    candidate_id: str
    job_id: str
    status: ScoreStatus
    per_criterion: list[CriterionScore] = Field(default_factory=list)
    knockout_results: list[KnockoutResult] = Field(default_factory=list)
    total: float = 0.0
    tier: Tier | None = None
    engine_version: str = ""
    interview_questions: list[InterviewQuestion] = Field(default_factory=list)
    scored_at: datetime = Field(default_factory=datetime.utcnow)
    error: str | None = None

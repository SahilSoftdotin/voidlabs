"""Default rubric for a mid-level role.

Defaults are provided but fully editable per job (§3.1). Weights sum to 100.
Nothing here is hardcoded into the scoring engine — it is just a starting point
the API hands to the client, which can override it freely.
"""
from __future__ import annotations

from app.domain.schemas import (
    Knockout,
    KnockoutType,
    Rubric,
    TierThresholds,
    WeightedCriterion,
)

DEFAULT_CRITERIA = [
    WeightedCriterion(
        id="skills_match",
        name="Relevant skills / tools match",
        weight=30,
        scoring_guidance=(
            "Semantic overlap between the candidate's skills/tools and the role's "
            "required skills. Map synonyms and related concepts — do NOT reward exact "
            "keyword matching alone. 5 = covers nearly all required skills with depth; "
            "0 = little to no relevant overlap."
        ),
    ),
    WeightedCriterion(
        id="experience_depth",
        name="Depth & relevance of experience",
        weight=25,
        scoring_guidance=(
            "Years and depth in a similar role/domain. Weight relevance over raw tenure. "
            "Do NOT penalize employment gaps. 5 = strong, directly-relevant experience; "
            "0 = no relevant experience."
        ),
    ),
    WeightedCriterion(
        id="impact",
        name="Demonstrated impact",
        weight=20,
        scoring_guidance=(
            "Quantified achievements and outcomes, not just listed duties. Reward metrics, "
            "scale, and ownership. 5 = clear, quantified, role-relevant impact; "
            "0 = only generic responsibilities."
        ),
    ),
    WeightedCriterion(
        id="trajectory",
        name="Career trajectory",
        weight=10,
        scoring_guidance=(
            "Growth and increasing responsibility over time. 5 = clear upward trajectory; "
            "0 = no signal. Do NOT penalize gaps or non-linear paths in themselves."
        ),
    ),
    WeightedCriterion(
        id="education",
        name="Education & certifications",
        weight=10,
        scoring_guidance=(
            "Relevance of degree/field and certifications to the role ONLY. Ignore "
            "institution prestige entirely. 5 = directly relevant credentials; "
            "0 = none relevant."
        ),
    ),
    WeightedCriterion(
        id="clarity",
        name="Resume clarity & communication",
        weight=5,
        scoring_guidance=(
            "Structure, readability, and clear communication of the professional record. "
            "5 = well-structured and clear; 0 = disorganized/unclear."
        ),
    ),
]

DEFAULT_KNOCKOUTS = [
    Knockout(
        id="work_authorization",
        name="Work authorization",
        type=KnockoutType.WORK_AUTHORIZATION,
        description="Candidate must be authorized to work in the role's location.",
        config={"required_terms": ["authorized to work", "work authorization", "citizen", "permanent resident"]},
    ),
]


def default_rubric() -> Rubric:
    return Rubric(
        knockouts=[k.model_copy(deep=True) for k in DEFAULT_KNOCKOUTS],
        weighted_criteria=[c.model_copy(deep=True) for c in DEFAULT_CRITERIA],
    )


def default_tier_thresholds() -> TierThresholds:
    return TierThresholds()

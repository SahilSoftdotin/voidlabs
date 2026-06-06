"""Scoring engine: stages 1-3, weighting, knockouts, interview questions."""
from __future__ import annotations

from app.core.default_rubric import default_rubric, default_tier_thresholds
from app.core.ports import CandidateSourceAdapter, Scorer
from app.adapters.upload_adapter import UploadAdapter
from app.domain.schemas import (
    Knockout,
    KnockoutType,
    Rubric,
    ScoreStatus,
    WeightedCriterion,
)
from app.services.scorers.mock_scorer import MockScorer
from app.services.scoring_engine import ScoringEngine


def _engine() -> ScoringEngine:
    return ScoringEngine(MockScorer())


def test_default_rubric_weights_sum_to_100():
    assert default_rubric().weight_total() == 100


def test_full_score_is_explainable_and_in_range(sample_candidate):
    engine = _engine()
    score = engine.score(
        sample_candidate, "job-1", default_rubric(),
        "Backend engineer. Python, FastAPI, PostgreSQL, microservices.",
        default_tier_thresholds(),
    )
    assert score.status == ScoreStatus.SCORED
    assert 0.0 <= score.total <= 100.0
    # One score per criterion, each with a justification (explainability).
    assert len(score.per_criterion) == len(default_rubric().weighted_criteria)
    for c in score.per_criterion:
        assert c.justification
        assert 0.0 <= c.raw_score <= 5.0
        assert abs(c.weighted_score - c.raw_score / 5.0 * c.weight) < 0.01
    # total == sum of weighted contributions
    assert abs(score.total - sum(c.weighted_score for c in score.per_criterion)) < 0.01
    assert score.tier in {None} or score.tier.value in {"A", "B", "C"}


def test_relevant_candidate_scores_above_irrelevant(sample_candidate):
    engine = _engine()
    job = "Backend engineer. Python, FastAPI, PostgreSQL, Docker, Kubernetes, microservices."
    good = engine.score(sample_candidate, "j", default_rubric(), job, default_tier_thresholds())

    irrelevant = sample_candidate.model_copy(deep=True)
    irrelevant.skills = ["Floristry", "Watercolor", "Calligraphy"]
    irrelevant.work_history = []
    bad = engine.score(irrelevant, "j", default_rubric(), job, default_tier_thresholds())
    assert good.total > bad.total  # scored relative to THIS job


def test_knockout_excludes_but_does_not_delete(sample_candidate):
    rubric = Rubric(
        knockouts=[Knockout(
            id="cert", name="Must hold PMP",
            type=KnockoutType.REQUIRED_CERTIFICATION,
            config={"required_terms": ["pmp"]},
        )],
        weighted_criteria=default_rubric().weighted_criteria,
    )
    score = _engine().score(sample_candidate, "j", rubric,
                            "PM role", default_tier_thresholds())
    assert score.status == ScoreStatus.KNOCKED_OUT
    assert any(not k.passed for k in score.knockout_results)
    # Candidate object itself is untouched / still present (never deleted).
    assert sample_candidate.internal_id == "cand-1"
    assert score.knockout_results[0].justification  # explained


def test_interview_questions_generated(sample_candidate):
    score = _engine().score(
        sample_candidate, "j", default_rubric(),
        "Backend engineer, Python", default_tier_thresholds(),
    )
    qs = score.interview_questions
    assert len(qs) == 5
    types = {q.type for q in qs}
    assert "technical" in types and "behavioral" in types  # mix required
    for q in qs:
        assert q.question and q.resume_item and q.signal


def test_interview_questions_never_reference_protected_attrs(sample_candidate):
    score = _engine().score(
        sample_candidate, "j", default_rubric(),
        "Backend engineer", default_tier_thresholds(),
    )
    blob = " ".join(q.question + q.resume_item + q.signal for q in score.interview_questions).lower()
    assert "jane" not in blob
    assert "prestige university" not in blob


def test_custom_rubric_changes_score(sample_candidate):
    """Same resume scores differently under a different rubric (§2 principle 1)."""
    job = "Backend engineer, Python, FastAPI"
    base = _engine().score(sample_candidate, "j", default_rubric(), job, default_tier_thresholds())

    skills_only = Rubric(weighted_criteria=[
        WeightedCriterion(id="skills_match", name="Skills", weight=100,
                          scoring_guidance="skills"),
    ])
    alt = _engine().score(sample_candidate, "j", skills_only, job, default_tier_thresholds())
    assert alt.total != base.total


def test_upload_adapter_satisfies_port():
    adapter = UploadAdapter()
    assert isinstance(adapter, CandidateSourceAdapter)
    assert adapter.source_name == "UPLOAD"


def test_mock_scorer_satisfies_port():
    assert isinstance(MockScorer(), Scorer)

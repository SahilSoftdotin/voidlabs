"""Scoring engine — orchestrates the three stages (§4).

Stage 1: knockout filters -> pass/fail (failing excludes from scoring, but the
         candidate is kept visible, never deleted).
Stage 2: weighted 0-5 scoring -> 0-100 total.
Stage 3: tiering into A/B/C bands (thresholds configurable).

Plus the manager interview-question generator (§3.6).

The engine depends only on the ``Scorer`` port and the normalized schema. It
routes every candidate through ``Candidate.scoring_view()`` and asserts the
view is clean before any scoring happens.
"""
from __future__ import annotations

from app import ENGINE_VERSION
from app.core.ports import Scorer
from app.domain.schemas import (
    Candidate,
    Rubric,
    Score,
    ScoreStatus,
    TierThresholds,
)
from app.services.bias import assert_scoring_view_clean


class ScoringEngine:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    def score(
        self,
        candidate: Candidate,
        job_id: str,
        rubric: Rubric,
        job_context: str,
        thresholds: TierThresholds,
        with_interview_questions: bool = True,
    ) -> Score:
        view = candidate.scoring_view()
        # Defense-in-depth: prove no protected/identifying data reached the scorer.
        assert_scoring_view_clean(candidate, view)

        engine_version = f"{ENGINE_VERSION}+{self.scorer.engine_name}"

        # Stage 1 — knockouts
        knockouts = self.scorer.evaluate_knockouts(view, rubric)
        if any(not k.passed for k in knockouts):
            # Excluded from scoring, but kept fully visible.
            return Score(
                candidate_id=candidate.internal_id,
                job_id=job_id,
                status=ScoreStatus.KNOCKED_OUT,
                knockout_results=knockouts,
                total=0.0,
                tier=None,
                engine_version=engine_version,
            )

        # Stage 2 — weighted scoring
        per_criterion = self.scorer.score_criteria(view, rubric, job_context)
        total = round(sum(c.weighted_score for c in per_criterion), 2)

        # Stage 3 — tiering
        tier = thresholds.tier_for(total)

        questions = []
        if with_interview_questions:
            questions = self.scorer.generate_interview_questions(view, job_context)

        return Score(
            candidate_id=candidate.internal_id,
            job_id=job_id,
            status=ScoreStatus.SCORED,
            per_criterion=per_criterion,
            knockout_results=knockouts,
            total=total,
            tier=tier,
            engine_version=engine_version,
            interview_questions=questions,
        )

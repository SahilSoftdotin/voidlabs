"""Bias & compliance: the scorer must never read protected attributes."""
from __future__ import annotations

import json

import pytest

from app.domain.schemas import CandidateScoringView
from app.services.bias import (
    PROTECTED_ATTRIBUTES,
    BiasLeakError,
    assert_scoring_view_clean,
)


def test_scoring_view_excludes_contact_and_institution(sample_candidate):
    view = sample_candidate.scoring_view()
    blob = json.dumps(view.model_dump()).lower()
    # Name, email, phone, location must NOT appear.
    assert "jane" not in blob
    assert "jane@example.com" not in blob
    assert "555-123-4567" not in blob
    assert "austin" not in blob
    # Institution name (university prestige) must NOT appear.
    assert "prestige university" not in blob
    # Degree/field (allowed, relevant) ARE present.
    assert "computer science" in blob


def test_scoring_view_has_no_protected_fields(sample_candidate):
    view = sample_candidate.scoring_view()
    fields = set(CandidateScoringView.model_fields.keys())
    for attr in PROTECTED_ATTRIBUTES:
        assert attr not in fields


def test_assert_clean_passes_for_real_view(sample_candidate):
    view = sample_candidate.scoring_view()
    assert_scoring_view_clean(sample_candidate, view)  # must not raise


def test_assert_clean_catches_a_leak(sample_candidate):
    view = sample_candidate.scoring_view()
    # Simulate a regression that leaks the candidate's name into the view.
    view.skills.append("Jane Q. Applicant")
    with pytest.raises(BiasLeakError):
        assert_scoring_view_clean(sample_candidate, view)

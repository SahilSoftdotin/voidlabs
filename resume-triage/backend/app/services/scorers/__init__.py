"""Scorer implementations (pluggable behind ``app.core.ports.Scorer``)."""
from __future__ import annotations

from app.config import get_settings
from app.core.ports import Scorer
from app.services.scorers.mock_scorer import MockScorer


def build_scorer() -> Scorer:
    """Select a scorer based on configuration.

    auto -> LLM scorer when a key is present, else the deterministic mock.
    The mock keeps the whole app runnable and testable with no API key."""
    settings = get_settings()
    if settings.use_llm_scoring:
        try:
            from app.services.scorers.llm_scorer import LLMScorer

            return LLMScorer()
        except Exception:  # noqa: BLE001 - fall back rather than break ingestion
            return MockScorer()
    return MockScorer()

"""Thin wrapper over the Anthropic SDK for structured (JSON) responses.

Used for semantic skill matching, per-criterion scoring, and interview-question
generation. We ask the model for a structured JSON object (via
``output_config.format``) so every score stays explainable and machine-readable
(§4: "the prompt must return a structured per-criterion score with a short
justification string").

The default model is ``claude-opus-4-8``. The SDK reads ANTHROPIC_API_KEY from
the environment; the key is never passed through application state.
"""
from __future__ import annotations

import json

from app.config import get_settings


class LLMUnavailableError(RuntimeError):
    pass


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.llm_model
        if not settings.anthropic_api_key:
            raise LLMUnavailableError("ANTHROPIC_API_KEY is not configured")
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise LLMUnavailableError("anthropic SDK is not installed") from exc
        # Key resolved from the environment by the SDK.
        self._client = Anthropic()

    def structured(
        self,
        *,
        system: str,
        user: str,
        schema: dict,
        max_tokens: int = 4096,
    ) -> dict:
        """Run one request constrained to a JSON schema and return parsed JSON.

        Opus 4.8 uses structured outputs; we read the text block and json.loads
        it. (Tool-input style JSON can vary in escaping, so we always parse
        rather than string-match.)"""
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
        return json.loads(text)

"""Application configuration, sourced from environment / .env.

Config-driven by design (principle §6): no vendor names or rubric values are
hardcoded in the core. Secrets come from the environment only.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Persistence
    database_url: str = "sqlite:///./storage/triage.db"
    storage_dir: str = "./storage/uploads"

    # Scoring / normalization backend selection
    scoring_backend: str = "auto"  # auto | llm | mock
    resume_normalizer: str = "auto"  # auto | llm | heuristic

    # LLM
    anthropic_api_key: str | None = None
    llm_model: str = "claude-opus-4-8"

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def use_llm_scoring(self) -> bool:
        if self.scoring_backend == "llm":
            return True
        if self.scoring_backend == "mock":
            return False
        return bool(self.anthropic_api_key)  # auto

    @property
    def use_llm_normalizer(self) -> bool:
        if self.resume_normalizer == "llm":
            return True
        if self.resume_normalizer == "heuristic":
            return False
        return bool(self.anthropic_api_key)  # auto

    def ensure_dirs(self) -> None:
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        # SQLite file parent dir
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "", 1)
            parent = Path(db_path).parent
            if str(parent):
                parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()

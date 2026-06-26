"""Application configuration.

Configuration is loaded once at startup from environment variables and an
optional .env file. Keeping this separate from graph construction makes later
dependency injection and testing straightforward.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings for the incident investigator."""

    app_env: str = "development"
    log_level: str = "INFO"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    anthropic_api_key: str | None = None
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None


def _as_bool(value: str | None, default: bool = False) -> bool:
    """Convert common environment variable strings into booleans."""

    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    """Load application settings from .env and process environment."""

    load_dotenv()
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        langsmith_tracing=_as_bool(os.getenv("LANGSMITH_TRACING")),
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY") or None,
    )

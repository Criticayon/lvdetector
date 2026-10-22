"""LLM port and configuration shared by all adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

DEFAULT_TEMPERATURE = 0.5
DEFAULT_MAX_TOKENS = 8005


class LLMPort(Protocol):
    """Minimal chat-completion interface used by the analysis modules."""

    def complete(self, messages: list[dict], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """Return the stripped assistant response for ``messages``."""
        ...


@dataclass
class LLMConfig:
    """Connection and generation settings for an OpenAI-compatible endpoint."""

    api_key: str = ""
    base_url: str = ""
    model: str = ""
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS

    @classmethod
    def from_settings(cls) -> "LLMConfig":
        """Load the values from ``lvdetector.config.settings``."""
        from lvdetector.config.settings import API_KEY, BASE_URL, MODEL

        return cls(api_key=API_KEY, base_url=BASE_URL, model=MODEL)

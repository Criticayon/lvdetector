"""OpenAI-compatible chat client with lazy construction.

Importing this module never creates an SDK client and never touches the
network. The underlying ``OpenAI`` instance is built on first use, which keeps
offline tests and CLI ``--help`` free of API-key requirements.
"""

from __future__ import annotations

from threading import Lock

from lvdetector.llm.base import DEFAULT_MAX_TOKENS, LLMConfig

_default_client: "OpenAIChatClient | None" = None
_default_lock = Lock()


class OpenAIChatClient:
    """Thin adapter around ``openai.OpenAI``.

    Parameters: ``temperature=0.5``, a default ``max_tokens`` of 8005, and a
    stripped response string.
    """

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_settings()
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
        return self._client

    def complete(
        self,
        messages: list[dict],
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> str:
        """Send a chat completion and return the stripped message content."""
        client = self._ensure_client()
        resp = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()


def get_default_client() -> OpenAIChatClient:
    """Return the process-wide default client, creating it on first use."""
    global _default_client
    if _default_client is None:
        with _default_lock:
            if _default_client is None:
                _default_client = OpenAIChatClient()
    return _default_client


def reset_default_client() -> None:
    """Drop the cached client (useful for tests and config reloads)."""
    global _default_client
    with _default_lock:
        _default_client = None

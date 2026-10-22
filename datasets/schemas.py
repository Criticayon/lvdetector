"""Dataset-facing schemas and the pickle-safe batch payload."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lvdetector.domain.models import CodeSample


@dataclass
class BatchItem:
    """Plain-type payload exchanged with worker processes."""

    index: Any = None
    code: str = ""
    diff: str | None = None
    target: Any = None

    @classmethod
    def from_sample(cls, sample: CodeSample, diff: str | None = None) -> "BatchItem":
        return cls(
            index=sample.index,
            code=sample.code,
            diff=diff,
            target=sample.label,
        )

    @classmethod
    def from_payload(cls, payload: dict) -> "BatchItem":
        return cls(
            index=payload.get("index"),
            code=payload.get("code", ""),
            diff=payload.get("diff"),
            target=payload.get("target"),
        )

    def to_payload(self) -> dict:
        return {
            "index": self.index,
            "code": self.code,
            "diff": self.diff,
            "target": self.target,
        }


__all__ = ["BatchItem", "CodeSample"]

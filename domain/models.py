"""Domain records shared by the pipeline, parsers, and services.

Parsed artifacts are recorded on the side. They never rewrite the messages
that are sent to the LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from lvdetector.domain.enums import (
    FunctionCategory,
    GuardState,
    SinkVerdict,
    SourceKind,
    StepId,
)


@dataclass
class CodeSample:
    """A single function under analysis."""

    code: str
    index: Any = None
    label: Any = None
    file_name: str | None = None


@dataclass
class SinkRecord:
    """A candidate triggering statement parsed from Step 1."""

    number: int | None
    vuln_type: str
    statement: str
    raw: str = ""


@dataclass
class VariableRecord:
    """A key-variable dependency parsed from Step 2."""

    vuln_type: str = ""
    statement: str = ""
    key_variables: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class DependencyPair:
    """A sink/variable pair progressively enriched by Steps 3-5."""

    sink: str = ""
    key_variable: str = ""
    source: SourceKind = SourceKind.UNRESOLVED
    guard: GuardState = GuardState.UNRESOLVED
    verdict: SinkVerdict = SinkVerdict.UNRESOLVED
    trace: str = ""
    guard_statements: str = ""
    reasoning: str = ""


@dataclass
class StepOutput:
    """Raw prompt/response for one step, plus an optional parsed artifact."""

    step: StepId
    prompt: str
    response: str
    parsed: Any = None


@dataclass
class AnalysisResult:
    """The function-level result.

    ``payload`` is the exact object produced by Step 7 (or the error envelope
    ``{"error": ...}``). ``to_dict`` returns it unchanged so downstream
    consumers observe the JSON shape produced by the model.
    """

    payload: Any

    @classmethod
    def from_payload(cls, payload: Any) -> "AnalysisResult":
        return cls(payload=payload)

    @classmethod
    def from_error(cls, result_str: str) -> "AnalysisResult":
        return cls(payload={"error": result_str})

    @property
    def is_error(self) -> bool:
        return isinstance(self.payload, dict) and "error" in self.payload

    @property
    def is_latent(self) -> Any:
        if isinstance(self.payload, dict):
            return self.payload.get("is_latent")
        return None

    @property
    def category(self) -> str | None:
        if isinstance(self.payload, dict):
            value = self.payload.get("category")
            return value if isinstance(value, str) else None
        return None

    @property
    def rationale(self) -> str | None:
        if isinstance(self.payload, dict):
            value = self.payload.get("rationale")
            return value if isinstance(value, str) else None
        return None

    @property
    def function_category(self) -> FunctionCategory:
        return FunctionCategory.from_text(self.category)

    def to_dict(self) -> Any:
        """Return the original Step 7 payload without transformation."""
        return self.payload


@dataclass
class AnalysisContext:
    """Mutable state for one sample.

    ``messages`` is the only conversation that is ever sent to the model.
    ``step_outputs`` and the artifact lists are recorded on the side.
    """

    sample: CodeSample
    messages: list[dict] = field(default_factory=list)
    step_outputs: dict[StepId, StepOutput] = field(default_factory=dict)
    sinks: list[SinkRecord] = field(default_factory=list)
    variables: list[VariableRecord] = field(default_factory=list)
    dependencies: list[DependencyPair] = field(default_factory=list)
    final: AnalysisResult | None = None
    diff: str | None = None

    @classmethod
    def start(cls, sample: CodeSample, diff: str | None = None) -> "AnalysisContext":
        """Create a context seeded with the system prompt."""
        from lvdetector.config.settings import SYSTEM_PROMPT

        return cls(
            sample=sample,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}],
            diff=diff,
        )

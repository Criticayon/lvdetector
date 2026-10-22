"""Pipeline-facing context helpers.

The :class:`AnalysisContext` record itself lives in the domain layer so that
parsers and modules can depend on it without importing the orchestrator.
"""

from __future__ import annotations

from lvdetector.domain.models import AnalysisContext, CodeSample


def create_context(code_or_sample, diff: str | None = None) -> AnalysisContext:
    """Create a context from a code string or an existing sample."""
    if isinstance(code_or_sample, CodeSample):
        sample = code_or_sample
    else:
        sample = CodeSample(code=code_or_sample)
    return AnalysisContext.start(sample, diff)


__all__ = ["AnalysisContext", "create_context"]

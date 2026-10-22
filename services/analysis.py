"""Single-sample analysis service."""

from __future__ import annotations

from lvdetector.domain.models import AnalysisResult, CodeSample
from lvdetector.llm.base import LLMPort
from lvdetector.pipeline.orchestrator import AnalysisPipeline


class AnalysisService:
    """Thin facade over :class:`AnalysisPipeline`."""

    def __init__(self, client: LLMPort | None = None, pipeline: AnalysisPipeline | None = None):
        self._client = client
        self._pipeline = pipeline

    def _get_pipeline(self) -> AnalysisPipeline:
        if self._pipeline is None:
            self._pipeline = AnalysisPipeline(client=self._client)
        return self._pipeline

    def analyze_sample(self, sample: CodeSample, diff: str | None = None) -> AnalysisResult:
        return self._get_pipeline().run(sample, diff)

    def analyze(self, code: str, diff: str | None = None):
        """Return the Step 7 JSON dictionary for one function."""
        return self.analyze_sample(CodeSample(code=code), diff).to_dict()


def analyze_stepwise(code: str, diff: str | None = None):
    """Convenience wrapper around :class:`AnalysisService`."""
    return AnalysisService().analyze(code, diff)

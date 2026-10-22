"""Sequential executor for the three analysis modules."""

from __future__ import annotations

from lvdetector.domain.models import AnalysisContext, AnalysisResult, CodeSample
from lvdetector.llm.base import LLMPort
from lvdetector.llm.openai_client import get_default_client
from lvdetector.modules.context_analysis import ContextAnalysisModule
from lvdetector.modules.decision_logic import DecisionLogicModule
from lvdetector.modules.feature_extraction import FeatureExtractionModule
from lvdetector.prompts.registry import PromptRegistry


class AnalysisPipeline:
    """Run Module 1 -> Module 2 -> Module 3 on a single sample."""

    def __init__(
        self,
        modules=None,
        client: LLMPort | None = None,
        registry: PromptRegistry | None = None,
    ):
        self.client = client if client is not None else get_default_client()
        self.registry = registry or PromptRegistry()
        if modules is None:
            self.modules = [
                FeatureExtractionModule(self.client, self.registry),
                ContextAnalysisModule(self.client, self.registry),
                DecisionLogicModule(self.client, self.registry),
            ]
        else:
            self.modules = list(modules)

    def run(self, sample, diff: str | None = None) -> AnalysisResult:
        """Analyze a :class:`CodeSample` (or a raw code string)."""
        if not isinstance(sample, CodeSample):
            sample = CodeSample(code=sample)
        context = AnalysisContext.start(sample, diff)
        return self.run_context(context)

    def run_context(self, context: AnalysisContext) -> AnalysisResult:
        """Execute every module in order and return the Step 7 result."""
        for module in self.modules:
            module.run(context)
        if context.final is None:
            raise RuntimeError("Analysis pipeline finished without a final result")
        return context.final

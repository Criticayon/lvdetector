"""Module 1: Risk Anchoring (Steps 1-2)."""

from __future__ import annotations

from lvdetector.domain.enums import ModuleId, StepId
from lvdetector.domain.models import AnalysisContext
from lvdetector.llm.base import LLMPort
from lvdetector.modules.base import run_step
from lvdetector.parsing.sinks import parse_sinks
from lvdetector.parsing.variables import parse_variables
from lvdetector.prompts.registry import PromptRegistry


class FeatureExtractionModule:
    """Comprehensive sink identification followed by variable mapping."""

    name = ModuleId.FEATURE_EXTRACTION

    def __init__(self, client: LLMPort, registry: PromptRegistry | None = None):
        self.client = client
        self.registry = registry or PromptRegistry()

    def run(self, context: AnalysisContext) -> AnalysisContext:
        # Step 1: over-approximate sink identification.
        sinks = run_step(
            context,
            self.client,
            StepId.SINK_IDENTIFICATION,
            self.registry.render_step1(context.sample.code),
            parse_sinks,
        )
        context.sinks = sinks or []

        # Step 2: key-variable dependency mapping.
        variables = run_step(
            context,
            self.client,
            StepId.VARIABLE_MAPPING,
            self.registry.text(StepId.VARIABLE_MAPPING),
            parse_variables,
        )
        context.variables = variables or []
        return context

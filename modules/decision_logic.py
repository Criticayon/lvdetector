"""Module 3: Global Synthesis (Step 7).

The function-level label and category come exclusively from the Step 7 LLM
response. No deterministic aggregation is applied here.
"""

from __future__ import annotations

from lvdetector.domain.enums import ModuleId, StepId
from lvdetector.domain.models import AnalysisContext, AnalysisResult
from lvdetector.llm.base import LLMPort
from lvdetector.modules.base import run_step
from lvdetector.parsing.final import parse_final
from lvdetector.prompts.registry import PromptRegistry


class DecisionLogicModule:
    """Ask Step 7 for the function-level decision and parse it verbatim."""

    name = ModuleId.DECISION_LOGIC

    def __init__(self, client: LLMPort, registry: PromptRegistry | None = None):
        self.client = client
        self.registry = registry or PromptRegistry()

    def run(self, context: AnalysisContext) -> AnalysisContext:
        result = run_step(
            context,
            self.client,
            StepId.FUNCTION_DECISION,
            self.registry.text(StepId.FUNCTION_DECISION),
            parse_final,
        )

        if not isinstance(result, AnalysisResult):
            raw = context.step_outputs[StepId.FUNCTION_DECISION].response.strip()
            result = AnalysisResult.from_error(raw)

        context.final = result
        return context

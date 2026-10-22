"""Module 2: Semantic Reasoning (Steps 3-6)."""

from __future__ import annotations

from lvdetector.domain.enums import ModuleId, StepId
from lvdetector.domain.models import AnalysisContext, DependencyPair
from lvdetector.llm.base import LLMPort
from lvdetector.modules.base import run_step
from lvdetector.parsing.guards import parse_guards
from lvdetector.parsing.patch import parse_patch_relations
from lvdetector.parsing.sources import parse_sources
from lvdetector.parsing.verdicts import parse_verdicts
from lvdetector.prompts.registry import PromptRegistry


def _select_pair(
    pairs: list[DependencyPair],
    index: int,
    key_variable: str,
) -> DependencyPair | None:
    if key_variable:
        for pair in pairs:
            if pair.key_variable and pair.key_variable == key_variable:
                return pair
    if index < len(pairs):
        return pairs[index]
    return None


def merge_dependency_findings(
    sources: list[DependencyPair],
    guards: list[DependencyPair],
    verdicts: list[DependencyPair],
) -> list[DependencyPair]:
    """Join Step 3/4/5 findings by key variable, falling back to position."""
    merged = list(sources)

    for index, finding in enumerate(guards):
        target = _select_pair(merged, index, finding.key_variable)
        if target is None:
            merged.append(finding)
            continue
        target.guard = finding.guard
        target.guard_statements = finding.guard_statements
        if finding.key_variable and not target.key_variable:
            target.key_variable = finding.key_variable

    for index, finding in enumerate(verdicts):
        target = _select_pair(merged, index, finding.key_variable)
        if target is None:
            merged.append(finding)
            continue
        target.verdict = finding.verdict
        target.reasoning = finding.reasoning

    return merged


class ContextAnalysisModule:
    """Source inference, guard verification, synthesis, and patch alignment."""

    name = ModuleId.CONTEXT_ANALYSIS

    def __init__(self, client: LLMPort, registry: PromptRegistry | None = None):
        self.client = client
        self.registry = registry or PromptRegistry()

    def run(self, context: AnalysisContext) -> AnalysisContext:
        # Step 3: source-origin inference.
        sources = run_step(
            context,
            self.client,
            StepId.SOURCE_INFERENCE,
            self.registry.text(StepId.SOURCE_INFERENCE),
            parse_sources,
        )

        # Step 4: security-constraint verification. The template keeps the
        # literal {KEY_VARS} placeholder and is not formatted.
        guards = run_step(
            context,
            self.client,
            StepId.CONSTRAINT_VERIFICATION,
            self.registry.text(StepId.CONSTRAINT_VERIFICATION),
            parse_guards,
        )

        # Step 5: semantic synthesis.
        verdicts = run_step(
            context,
            self.client,
            StepId.SEMANTIC_SYNTHESIS,
            self.registry.text(StepId.SEMANTIC_SYNTHESIS),
            parse_verdicts,
        )

        # Step 6: semantic patch alignment. Always called exactly once; the
        # diff is appended only when one was supplied.
        run_step(
            context,
            self.client,
            StepId.PATCH_ALIGNMENT,
            self.registry.render_step6(context.diff),
            parse_patch_relations,
        )

        context.dependencies = merge_dependency_findings(
            sources or [],
            guards or [],
            verdicts or [],
        )
        return context

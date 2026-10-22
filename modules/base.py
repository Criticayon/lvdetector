"""Shared module protocol and the single-step conversation helper."""

from __future__ import annotations

from typing import Callable, Protocol

from lvdetector.domain.enums import ModuleId, StepId
from lvdetector.domain.models import AnalysisContext, StepOutput
from lvdetector.llm.base import LLMPort


class AnalysisModule(Protocol):
    """A pipeline stage that enriches the context in place."""

    name: ModuleId

    def run(self, context: AnalysisContext) -> AnalysisContext:
        ...


def run_step(
    context: AnalysisContext,
    client: LLMPort,
    step: StepId,
    prompt: str,
    parser: Callable | None = None,
):
    """Append one user/assistant exchange and record the raw step output.

    The conversation receives only the user prompt followed by the stripped
    model response. The parser runs afterwards, on the side, and any parsing
    failure is swallowed.
    """
    context.messages.append({"role": "user", "content": prompt})
    response = client.complete(context.messages)
    context.messages.append({"role": "assistant", "content": response})

    parsed = None
    if parser is not None:
        try:
            parsed = parser(response)
        except Exception:
            parsed = None

    context.step_outputs[step] = StepOutput(
        step=step,
        prompt=prompt,
        response=response,
        parsed=parsed,
    )
    return parsed

"""Prompt registry backed directly by ``lvdetector.config.settings`` constants.

The registry is a thin indirection layer so that prompts have exactly one
source of truth. It performs interpolation only for Step 1 (``{code}``).
Step 4 deliberately returns the template unchanged so the literal
``{KEY_VARS}`` placeholder is preserved.
"""

from __future__ import annotations

from lvdetector.domain.enums import StepId

import lvdetector.config.settings as settings


class PromptRegistry:
    """Map :class:`StepId` values to the verbatim prompt templates."""

    STEP_TEMPLATES = {
        StepId.SINK_IDENTIFICATION: settings.PROMPT_STEP1,
        StepId.VARIABLE_MAPPING: settings.PROMPT_STEP2,
        StepId.SOURCE_INFERENCE: settings.PROMPT_STEP3,
        StepId.CONSTRAINT_VERIFICATION: settings.PROMPT_STEP4,
        StepId.SEMANTIC_SYNTHESIS: settings.PROMPT_STEP5,
        StepId.PATCH_ALIGNMENT: settings.PROMPT_STEP6,
        StepId.FUNCTION_DECISION: settings.PROMPT_STEP7,
    }

    def __init__(self, templates=None, system_prompt: str | None = None):
        self._templates = dict(self.STEP_TEMPLATES)
        if templates is not None:
            self._templates.update(
                {self._coerce_step(step): text for step, text in templates.items()}
            )
        self._system_prompt = (
            settings.SYSTEM_PROMPT if system_prompt is None else system_prompt
        )

    @staticmethod
    def _coerce_step(step) -> StepId:
        if isinstance(step, StepId):
            return step
        return StepId(int(step))

    @property
    def system_prompt(self) -> str:
        """The system message text, unchanged from ``config.settings``."""
        return self._system_prompt

    def text(self, step) -> str:
        """Return the raw template for ``step``."""
        return self._templates[self._coerce_step(step)]

    def render(self, step, **kwargs) -> str:
        """Render a step prompt.

        Only Step 1 receives keyword substitution. Every other template is
        returned exactly as defined in ``lvdetector.config.settings``; in
        particular, Step 4 keeps its literal ``{KEY_VARS}`` placeholder.
        """
        resolved = self._coerce_step(step)
        template = self._templates[resolved]
        if resolved is StepId.SINK_IDENTIFICATION:
            return template.format(**kwargs)
        return template

    def render_step1(self, code: str) -> str:
        """Render Step 1 with the target function source code."""
        return self._templates[StepId.SINK_IDENTIFICATION].format(code=code)

    def render_step6(self, diff: str | None = None) -> str:
        """Render Step 6, appending the diff when one is provided."""
        template = self._templates[StepId.PATCH_ALIGNMENT]
        if diff:
            return template + "\n\ndiff:\n" + diff
        return template

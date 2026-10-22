"""Enumerations describing the layered analysis pipeline.

These values are used by the side-channel artifact records only. They never
alter the prompts or the conversation sent to the model.
"""

from enum import Enum


class ModuleId(str, Enum):
    """Identifiers for the three paper modules."""

    FEATURE_EXTRACTION = "feature_extraction"
    CONTEXT_ANALYSIS = "context_analysis"
    DECISION_LOGIC = "decision_logic"


class StepId(int, Enum):
    """The seven sequential analysis steps."""

    SINK_IDENTIFICATION = 1
    VARIABLE_MAPPING = 2
    SOURCE_INFERENCE = 3
    CONSTRAINT_VERIFICATION = 4
    SEMANTIC_SYNTHESIS = 5
    PATCH_ALIGNMENT = 6
    FUNCTION_DECISION = 7

    @property
    def module(self) -> ModuleId:
        """Return the module that owns this step."""
        if self.value <= 2:
            return ModuleId.FEATURE_EXTRACTION
        if self.value <= 6:
            return ModuleId.CONTEXT_ANALYSIS
        return ModuleId.DECISION_LOGIC


class SourceKind(str, Enum):
    """Source-origin verdict produced by Step 3."""

    KNOWN = "known"
    UNKNOWN = "unknown"
    UNRESOLVED = "unresolved"


class GuardState(str, Enum):
    """Guard-verification verdict produced by Step 4."""

    GUARDED = "guarded"
    UNGUARDED = "unguarded"
    UNRESOLVED = "unresolved"


class SinkVerdict(str, Enum):
    """Per-sink semantic verdict produced by Step 5."""

    LATENT = "latent"
    MANIFEST = "manifest"
    SAFE = "safe"
    UNRESOLVED = "unresolved"


class FunctionCategory(str, Enum):
    """Function-level categories emitted by Step 7."""

    LATENT = "latent vulnerability function"
    MANIFEST = "manifest vulnerability function"
    SAFE = "safe function"
    UNKNOWN = "unknown"

    @classmethod
    def from_text(cls, value: str | None) -> "FunctionCategory":
        """Map free-form Step 7 text to a known category."""
        text = (value or "").strip().lower()
        if "manifest" in text:
            return cls.MANIFEST
        if "latent" in text:
            return cls.LATENT
        if "safe" in text:
            return cls.SAFE
        return cls.UNKNOWN

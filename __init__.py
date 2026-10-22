"""LVDetector: a layered latent-vulnerability detection framework.

The public package exposes the domain model and the sequential analysis
pipeline. Lower-level layers (prompts, LLM adapters, parsers, datasets,
evaluation helpers) are importable from their respective subpackages.
"""

__version__ = "2.0.0"

from lvdetector.domain.enums import (
    FunctionCategory,
    GuardState,
    ModuleId,
    SinkVerdict,
    SourceKind,
    StepId,
)
from lvdetector.domain.models import (
    AnalysisContext,
    AnalysisResult,
    CodeSample,
    DependencyPair,
    SinkRecord,
    StepOutput,
    VariableRecord,
)
from lvdetector.pipeline.orchestrator import AnalysisPipeline

__all__ = [
    "__version__",
    "AnalysisContext",
    "AnalysisPipeline",
    "AnalysisResult",
    "CodeSample",
    "DependencyPair",
    "FunctionCategory",
    "GuardState",
    "ModuleId",
    "SinkRecord",
    "SinkVerdict",
    "SourceKind",
    "StepId",
    "StepOutput",
    "VariableRecord",
]

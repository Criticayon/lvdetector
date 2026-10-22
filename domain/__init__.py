"""Domain layer: enums and immutable data records shared across layers."""

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

__all__ = [
    "AnalysisContext",
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

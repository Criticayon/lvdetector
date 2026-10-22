"""Parse the Step 7 function-level decision.

The fallback is intentionally simple: invalid JSON returns
``{"error": <cleaned output>}`` and prints the decode error.
"""

from __future__ import annotations

import json

from lvdetector.domain.models import AnalysisResult
from lvdetector.parsing.common import strip_code_fences


def parse_final(text: str) -> AnalysisResult:
    """Parse Step 7 into an :class:`AnalysisResult`.

    The final label is whatever the LLM emitted; no deterministic aggregation
    happens here.
    """
    result_str = strip_code_fences(text)
    try:
        return AnalysisResult.from_payload(json.loads(result_str))
    except json.JSONDecodeError as exc:
        print(f"Failed to parse model output as JSON: {exc}")
        return AnalysisResult.from_error(result_str)

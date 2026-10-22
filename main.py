"""Command-line entry point for the LVDetector framework.

The implementation lives in the layered ``lvdetector`` package. The helpers
below are convenience wrappers around :class:`AnalysisService`, and the CLI is
provided by ``lvdetector.cli``.

Pipeline:
  Module 1: Risk Anchoring           (Steps 1-2)
  Module 2: Semantic Reasoning       (Steps 3-6)
  Module 3: Global Synthesis         (Step 7)
"""

import sys
from pathlib import Path

# Allow ``python main.py`` (from inside this folder) and
# ``python lvdetector/main.py`` (from the parent folder) to import the
# ``lvdetector`` package.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lvdetector.services.analysis import AnalysisService


def analyze_stepwise(code, diff=None):
    """
    Run the full 3-module pipeline on a single code sample.

    Args:
        code: Source code of the target function.
        diff: Optional patch diff for auxiliary alignment analysis.

    Returns:
        Parsed JSON verdict from Module 3.
    """
    return AnalysisService().analyze(code, diff)


def get_single_result(param):
    """
    Process a single sample (used by multiprocessing Pool).

    Args:
        param: Tuple of (index, code, diff, target).

    Returns:
        Dict with keys: index, func, analysis.
    """
    index, code, diff, target = param
    analysis_dict = analyze_stepwise(code, diff)

    return {
        "index": str(index),
        "func": code,
        "analysis": analysis_dict,
    }


def main():
    from lvdetector.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()

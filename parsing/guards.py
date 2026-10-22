"""Parse Step 4 output into guard-verification findings."""

from __future__ import annotations

import re

from lvdetector.domain.enums import GuardState
from lvdetector.domain.models import DependencyPair
from lvdetector.parsing.common import find_labeled_value, split_blocks


_BLOCK_START = (
    r"^\s*[-*]?\s*(?:\d+[\.\)]\s*)?(?:Key Variable|guard statements?)\s*[:：]?"
)
_VERDICT = r"^\s*[-*]?\s*Verdict\s*[:：]?"


def detect_guard(text: str) -> GuardState:
    """Map a free-form verdict fragment to a :class:`GuardState`."""
    if re.search(r"\bUnguarded\b", text or "", re.IGNORECASE):
        return GuardState.UNGUARDED
    if re.search(r"\bGuarded\b", text or "", re.IGNORECASE):
        return GuardState.GUARDED
    return GuardState.UNRESOLVED


def parse_guards(text: str) -> list[DependencyPair]:
    """Extract guard findings, optionally associated with a key variable."""
    pairs: list[DependencyPair] = []
    blocks = split_blocks(text, _BLOCK_START, _VERDICT)
    if not blocks and (text or "").strip():
        blocks = [text.strip()]
    for block in blocks:
        pairs.append(
            DependencyPair(
                key_variable=find_labeled_value(block, ["Key Variable"]),
                guard=detect_guard(block),
                guard_statements=find_labeled_value(
                    block, ["guard statements", "guard statement"]
                ),
            )
        )
    return pairs

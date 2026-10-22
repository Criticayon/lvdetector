"""Parse Step 3 output into source-origin findings."""

from __future__ import annotations

import re

from lvdetector.domain.enums import SourceKind
from lvdetector.domain.models import DependencyPair
from lvdetector.parsing.common import find_labeled_value, split_blocks


_KEY_VARIABLE = r"^\s*[-*]?\s*(?:\d+[\.\)]\s*)?Key Variable\s*[:：]"
_VERDICT = r"^\s*[-*]?\s*Verdict\s*[:：]?"


def detect_source(text: str) -> SourceKind:
    """Map a free-form verdict fragment to a :class:`SourceKind`."""
    if re.search(r"\bUnknown\s+Source\b", text or "", re.IGNORECASE):
        return SourceKind.UNKNOWN
    if re.search(r"\bKnown\s+Source\b", text or "", re.IGNORECASE):
        return SourceKind.KNOWN
    return SourceKind.UNRESOLVED


def parse_sources(text: str) -> list[DependencyPair]:
    """Extract one :class:`DependencyPair` per ``Key Variable`` block."""
    pairs: list[DependencyPair] = []
    blocks = split_blocks(text, _KEY_VARIABLE, _VERDICT)
    if not blocks and (text or "").strip():
        blocks = [text.strip()]
    for block in blocks:
        pairs.append(
            DependencyPair(
                key_variable=find_labeled_value(block, ["Key Variable"]),
                trace=find_labeled_value(block, ["Trace"]),
                source=detect_source(block),
            )
        )
    return pairs

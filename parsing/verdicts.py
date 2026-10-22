"""Parse Step 5 output into per-sink semantic verdicts."""

from __future__ import annotations

import re

from lvdetector.domain.enums import SinkVerdict
from lvdetector.domain.models import DependencyPair
from lvdetector.parsing.common import find_labeled_value, split_blocks


_BLOCK_START = r"^\s*[-*]?\s*(?:\d+[\.\)]\s*)?(?:Reasoning|Final State)\s*[:：]?"
_RESET = r"^\s*[-*]?\s*Final State\s*[:：]?"


def detect_verdict(text: str) -> SinkVerdict:
    """Map a free-form state fragment to a :class:`SinkVerdict`."""
    if re.search(r"\bManifest\s+Vulnerability\b", text or "", re.IGNORECASE):
        return SinkVerdict.MANIFEST
    if re.search(r"\bLatent\s+Vulnerability\b", text or "", re.IGNORECASE):
        return SinkVerdict.LATENT
    if re.search(r"\bSafe\b", text or "", re.IGNORECASE):
        return SinkVerdict.SAFE
    return SinkVerdict.UNRESOLVED


def parse_verdicts(text: str) -> list[DependencyPair]:
    """Extract semantic verdicts, one pair per reasoning block."""
    pairs: list[DependencyPair] = []
    blocks = split_blocks(text, _BLOCK_START, _RESET)
    if not blocks and (text or "").strip():
        blocks = [text.strip()]
    for block in blocks:
        pairs.append(
            DependencyPair(
                verdict=detect_verdict(block),
                reasoning=find_labeled_value(block, ["Reasoning"]),
            )
        )
    return pairs

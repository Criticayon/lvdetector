"""Small text helpers shared by the step parsers.

Every helper is deliberately tolerant: malformed model output yields an empty
or partial result instead of an exception. Parsing never changes the
conversation, so a failure cannot affect the final Step 7 verdict.
"""

from __future__ import annotations

import json
import re
from typing import Any

_NUMBERED_LINE = re.compile(
    r"^\s*(?:No\.\s*)?(\d+)\s*[\.\)、:]\s*(.+?)\s*$",
    re.IGNORECASE,
)
_NUMBERED_LINE_BARE = re.compile(r"^\s*(\d+)\s+(.+?)\s*$")


def strip_code_fences(text: str) -> str:
    """Remove a leading Markdown code fence and trailing backticks.

    This mirrors the Step 7 cleaning logic exactly.
    """
    result = (text or "").strip()
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:]).rstrip("`").strip()
    return result


def extract_json(text: str) -> Any:
    """Best-effort JSON extraction; returns ``None`` on failure."""
    candidate = strip_code_fences(text)
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(candidate[start : end + 1])
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def iter_lines(text: str):
    """Yield non-empty stripped lines."""
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped:
            yield stripped


def numbered_line(line: str):
    """Return ``(number, body)`` when a line starts with an index, else ``None``."""
    match = _NUMBERED_LINE.match(line) or _NUMBERED_LINE_BARE.match(line)
    if not match:
        return None
    return int(match.group(1)), match.group(2).strip()


def split_label(body: str):
    """Split ``vulnerability type + statement`` on the first separator."""
    text = (body or "").strip().lstrip("-*").strip()
    for separator in (":", "："):
        if separator in text:
            left, right = text.split(separator, 1)
            return left.strip(), right.strip()
    for separator in (" - ", " – ", " — ", "->", "→"):
        if separator in text:
            left, right = text.split(separator, 1)
            return left.strip(), right.strip()
    return "", text


def find_labeled_value(text: str, labels) -> str:
    """Return the value following the first ``label:`` line."""
    if isinstance(labels, str):
        labels = [labels]
    patterns = [re.compile(rf"{re.escape(label)}\s*[:：]\s*(.*)$", re.IGNORECASE) for label in labels]
    for line in (text or "").splitlines():
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                return match.group(1).strip()
    return ""


def split_blocks(text: str, start_pattern: str, reset_after_pattern: str | None = None):
    """Split text into blocks whose first line matches ``start_pattern``.

    A new block only begins once the current block contains a line matching
    ``reset_after_pattern`` (typically a ``Verdict`` line). This keeps labels
    such as ``Key Variable`` attached to the guard analysis that follows them.
    """
    start_re = re.compile(start_pattern, re.IGNORECASE)
    reset_re = re.compile(reset_after_pattern, re.IGNORECASE) if reset_after_pattern else None

    blocks: list[str] = []
    current: list[str] = []

    for line in (text or "").splitlines():
        if start_re.search(line):
            is_closed = bool(reset_re) and any(reset_re.search(item) for item in current)
            if current and (reset_re is None or is_closed):
                blocks.append("\n".join(current).strip())
                current = [line]
            elif current:
                current.append(line)
            else:
                current = [line]
        elif current:
            current.append(line)

    if current:
        blocks.append("\n".join(current).strip())
    return [block for block in blocks if block]

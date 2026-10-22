"""Parse Step 6 patch-alignment output."""

from __future__ import annotations

import re

from lvdetector.parsing.common import iter_lines

_RELATION = re.compile(r"\b(fix|introduction|irrelevant)\b", re.IGNORECASE)
_NUMBERED = re.compile(r"^\s*(\d+)\s*[\.\)、:]\s*(.+)$")


def parse_patch_relations(text: str) -> list[dict]:
    """Extract ``statement -> relation`` items; malformed lines are skipped."""
    relations: list[dict] = []
    for line in iter_lines(text):
        if not _RELATION.search(line):
            continue
        match = _NUMBERED.match(line)
        number = int(match.group(1)) if match else None
        body = match.group(2) if match else line
        relation_match = _RELATION.search(body)
        relation = relation_match.group(1).lower() if relation_match else "unknown"
        statement = body
        if relation_match:
            statement = body[: relation_match.start()].strip(" -:>→")
        reason = ""
        reason_match = re.search(r"\(([^)]*)\)", body)
        if reason_match:
            reason = reason_match.group(1).strip()
        relations.append(
            {
                "number": number,
                "statement": statement,
                "relation": relation,
                "reason": reason,
                "raw": line,
            }
        )
    return relations

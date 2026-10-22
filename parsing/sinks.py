"""Parse Step 1 output into over-approximated sink records."""

from __future__ import annotations

import re

from lvdetector.domain.models import SinkRecord
from lvdetector.parsing.common import iter_lines, numbered_line, split_label


def parse_sinks(text: str) -> list[SinkRecord]:
    """Extract numbered sink statements from a Step 1 response."""
    sinks: list[SinkRecord] = []
    for line in iter_lines(text):
        if re.match(r"^(?:No\.|Vulnerability Type|Output Format)\b", line, re.IGNORECASE):
            continue
        parsed = numbered_line(line)
        if parsed is None:
            continue
        number, body = parsed
        vuln_type, statement = split_label(body)
        sinks.append(
            SinkRecord(
                number=number,
                vuln_type=vuln_type,
                statement=statement,
                raw=line,
            )
        )
    return sinks

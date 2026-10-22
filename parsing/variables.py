"""Parse Step 2 output into sink-to-key-variable records."""

from __future__ import annotations

import re

from lvdetector.domain.models import VariableRecord
from lvdetector.parsing.common import iter_lines, split_label


_ARROW = re.compile(r"->|→")


def parse_variables(text: str) -> list[VariableRecord]:
    """Extract ``statement -> variable list`` relationships from Step 2."""
    records: list[VariableRecord] = []
    for line in iter_lines(text):
        if not _ARROW.search(line):
            continue
        left, right = _ARROW.split(line, maxsplit=1)
        left = left.strip().lstrip("-*").strip()
        left = re.sub(r"^\d+\s*[\.\)、:]\s*", "", left)
        vuln_type, statement = split_label(left)
        variables = [
            variable.strip().strip("[]").strip()
            for variable in re.split(r"[,，;；]", right)
            if variable.strip().strip("[]").strip()
        ]
        records.append(
            VariableRecord(
                vuln_type=vuln_type,
                statement=statement,
                key_variables=variables,
                raw=line,
            )
        )
    return records

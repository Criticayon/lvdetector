"""Result writers that preserve the original JSON/JSONL shapes."""

from __future__ import annotations

import json


class JsonResultWriter:
    """Write a list of results as pretty-printed UTF-8 JSON."""

    def __init__(self, path: str):
        self.path = path

    def write(self, results) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(results, handle, ensure_ascii=False, indent=2)


class JsonlResultWriter:
    """Append results as UTF-8 JSON Lines."""

    def __init__(self, path: str):
        self.path = path

    def append(self, results) -> None:
        with open(self.path, "a", encoding="utf-8") as handle:
            for result in results:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    def append_one(self, result) -> None:
        self.append([result])

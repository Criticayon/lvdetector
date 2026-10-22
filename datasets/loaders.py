"""Read-only dataset loaders for the existing experimental data.

The loaders never write to, rename, or move anything under
``testdata(RQ1)/`` or ``testdata(RQ3)/``.
"""

from __future__ import annotations

import json
import os

from lvdetector.domain.models import CodeSample


class JsonDatasetLoader:
    """Load the RQ1-style list-of-objects JSON schema."""

    def __init__(self, path: str):
        self.path = path

    def load(self) -> list[CodeSample]:
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        samples: list[CodeSample] = []
        for item in data:
            samples.append(
                CodeSample(
                    code=item.get("func", ""),
                    index=item.get("index", None),
                    label=item.get("label", ""),
                    file_name=item.get("file_name"),
                )
            )
        return samples


class FolderDatasetLoader:
    """Load every regular file in a folder as one code sample."""

    def __init__(self, folder: str):
        self.folder = folder

    def load(self) -> list[CodeSample]:
        samples: list[CodeSample] = []
        for filename in os.listdir(self.folder):
            file_path = os.path.join(self.folder, filename)
            if not os.path.isfile(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as handle:
                code = handle.read()
            samples.append(
                CodeSample(
                    code=code,
                    index=filename,
                    label=None,
                    file_name=filename,
                )
            )
        return samples

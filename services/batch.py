"""Batch execution with a top-level, pickle-safe worker.

Only plain payload dictionaries cross the process boundary. Each worker
process lazily constructs its own LLM client on first use, so importing this
module requires no credentials and spawning needs no pickled client.
"""

from __future__ import annotations

from multiprocessing import Pool

from tqdm import tqdm

from lvdetector.config.settings import RUNTIME
from lvdetector.datasets.schemas import BatchItem
from lvdetector.domain.models import CodeSample


def _analyze_worker(payload: dict) -> dict:
    """Analyze one payload in the current process."""
    from lvdetector.services.analysis import AnalysisService

    service = AnalysisService()
    analysis = service.analyze(payload.get("code", ""), payload.get("diff"))
    return {
        "index": str(payload.get("index")),
        "func": payload.get("code", ""),
        "analysis": analysis,
    }


class BatchRunner:
    """Run the analysis worker over many samples."""

    def __init__(
        self,
        processes: int = RUNTIME.processes,
        worker=_analyze_worker,
        show_progress: bool = True,
    ):
        self.processes = processes
        self.worker = worker
        self.show_progress = show_progress

    @staticmethod
    def _to_payload(item, diff: str | None) -> dict:
        if isinstance(item, BatchItem):
            payload = item.to_payload()
            if payload.get("diff") is None:
                payload["diff"] = diff
            return payload
        if isinstance(item, CodeSample):
            return {
                "index": item.index,
                "code": item.code,
                "diff": diff,
                "target": item.label,
            }
        if isinstance(item, dict):
            return {
                "index": item.get("index"),
                "code": item.get("code", item.get("func", "")),
                "diff": item.get("diff", diff),
                "target": item.get("target", item.get("label")),
            }
        return {"index": None, "code": str(item), "diff": diff, "target": None}

    def run(
        self,
        items,
        diff: str | None = None,
        desc: str = "Processing samples",
        unit: str = "sample",
    ) -> list[dict]:
        payloads = [self._to_payload(item, diff) for item in items]
        if not payloads:
            return []

        if self.processes <= 1:
            iterator = (self.worker(payload) for payload in payloads)
            return list(
                tqdm(
                    iterator,
                    total=len(payloads),
                    desc=desc,
                    unit=unit,
                    disable=not self.show_progress,
                )
            )

        with Pool(self.processes) as pool:
            return list(
                tqdm(
                    pool.imap_unordered(self.worker, payloads),
                    total=len(payloads),
                    desc=desc,
                    unit=unit,
                    disable=not self.show_progress,
                )
            )

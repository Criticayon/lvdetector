"""Command-line interface for LVDetector."""

from __future__ import annotations

import argparse
import os
import sys

from lvdetector.config.settings import RUNTIME
from lvdetector.datasets.loaders import FolderDatasetLoader, JsonDatasetLoader
from lvdetector.io.result_writer import JsonlResultWriter, JsonResultWriter
from lvdetector.services.batch import BatchRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LVDetector: Latent Vulnerability Detector (3-Module Pipeline)"
    )
    parser.add_argument(
        "--json", "-J",
        required=False,
        help="JSON file containing code samples to analyze.",
        default=None,
    )
    parser.add_argument(
        "--folder", "-F",
        required=False,
        help="Folder containing individual function source files.",
    )
    parser.add_argument(
        "--diff", "-d",
        required=False,
        help="Optional diff file for patch-alignment analysis.",
    )
    return parser


def _load_diff(path: str | None) -> str | None:
    if not path:
        return None
    if not os.path.exists(path):
        print("Error: Specified diff file does not exist.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Explicit --json wins, then explicit --folder, then the built-in RQ1
    # sample. This keeps `python main.py` working while making --folder usable.
    if not args.json and not args.folder:
        args.json = RUNTIME.default_json_input

    diff = _load_diff(args.diff)

    # ---- JSON Mode ----
    if args.json:
        if not os.path.exists(args.json):
            print("Error: Specified JSON file does not exist.")
            sys.exit(1)

        samples = JsonDatasetLoader(args.json).load()
        results = BatchRunner(processes=RUNTIME.processes).run(
            samples,
            diff=diff,
            desc="Processing samples",
            unit="sample",
        )

        output_file = RUNTIME.json_output_path
        JsonResultWriter(output_file).write(results)
        print(f"\nAll samples analyzed. Results saved to {output_file}")
        return

    # ---- Folder Mode ----
    if args.folder:
        if not os.path.exists(args.folder):
            print("Error: Specified folder does not exist.")
            sys.exit(1)

        samples = FolderDatasetLoader(args.folder).load()
        results = BatchRunner(processes=RUNTIME.processes).run(
            samples,
            diff=diff,
            desc="Processing files",
            unit="file",
        )

        output_path = RUNTIME.jsonl_output_path
        JsonlResultWriter(output_path).append(results)
        print(f"\nAll files analyzed. Results saved to {output_path}")


if __name__ == "__main__":
    main()

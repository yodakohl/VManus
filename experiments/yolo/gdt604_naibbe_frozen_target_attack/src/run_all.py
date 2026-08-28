#!/usr/bin/env python3
"""Run GDT604 from guarded query through the frozen held-folio decision."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from common import sha256_path
from pipeline import run_all, run_from_frozen_segmentation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--frozen-segmentation-dir", required=True, type=Path,
        help="Published pre-key segmentation directory; required for exact reproduction.",
    )
    parser.add_argument("--workers", type=int, default=min(9, os.cpu_count() or 1))
    parser.add_argument(
        "--keep-work-dir", type=Path,
        help="Optional explicit diagnostic work directory; default is auto-cleaned tempfile.",
    )
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        raise SystemExit("--workers must be between 1 and 32")
    if args.keep_work_dir is not None:
        outputs = run_from_frozen_segmentation(
            args.keep_work_dir, args.output_dir, args.reference_dir,
            args.frozen_segmentation_dir, args.workers,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="gdt604-work-") as temporary:
            outputs = run_from_frozen_segmentation(
                Path(temporary), args.output_dir, args.reference_dir,
                args.frozen_segmentation_dir, args.workers,
            )
    print(json.dumps(
        {name: {"path": path.name, "sha256": sha256_path(path)}
         for name, path in outputs.items()},
        indent=2, sort_keys=True,
    ))


if __name__ == "__main__":
    main()

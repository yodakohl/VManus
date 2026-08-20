#!/usr/bin/env python3
"""Merge independently run GDT396 decoder manifests without touching claims."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims-dir", type=Path, required=True)
    ap.add_argument("--input", type=Path, action="append", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    merged = []
    fields = None
    seen = set()
    for source in sorted(args.input):
        data = rows(source)
        with source.open(encoding="utf-8", newline="") as fh:
            current = tuple(csv.DictReader(fh, delimiter="\t").fieldnames or ())
        if fields is None:
            fields = current
        elif current != fields:
            raise ValueError("manifest field mismatch")
        for row in data:
            key = (row["decoder_id"], row["world_id"], row["surface_id"], row["corpus_seed"], row["representation_id"], row["table_name"])
            if key in seen:
                raise ValueError(f"duplicate claim cell {key}")
            seen.add(key)
            path = (args.claims_dir / row["relpath"]).resolve()
            if not path.is_relative_to(args.claims_dir.resolve()):
                raise ValueError("claim path escapes claims-dir")
            if not path.is_file() or sha256(path) != row["sha256"]:
                raise ValueError(f"claim binding mismatch {path}")
            merged.append(row)
    merged.sort(key=lambda row: tuple(row[key] for key in ("decoder_id", "world_id", "surface_id", "corpus_seed", "representation_id", "table_name")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(merged)
    print(args.output, len(merged), sha256(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

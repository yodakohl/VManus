#!/usr/bin/env python3
"""Emit both ordered portable meaning trace and fluent state-aware clause."""

from __future__ import annotations

import argparse
import csv
import importlib.util
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
ORDER_SAFE_READER = ROOT / "experiments/yolo/gdt438_order_safe_streaming_reader/src/order_safe_stream_read.py"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gdt438_order_safe_reader_for_dual_channel", ORDER_SAFE_READER)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


CATALOG_ROWS = {row["component_recipe"]: row for row in read_tsv(CATALOG)}


def stream_rows(input_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = BASE.stream_rows(input_rows)
    output: list[dict[str, object]] = []
    for row in rows:
        card = CATALOG_ROWS.get(str(row["component_recipe"]))
        literal = card["literal_reading_de"] if card else "KEINE LIZENZIERTE KERNFOLGE"
        clause = str(row["reader_clause_de"])
        readable = f"Kernfolge: {literal}. {clause}" if card else clause
        output.append({
            **row,
            "ordered_literal_reading_de": literal,
            "dual_channel_reading_de": readable,
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Ordered event TSV")
    parser.add_argument("--output", required=True, type=Path, help="Destination TSV")
    args = parser.parse_args()
    rows = stream_rows(read_tsv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    BASE.BASE.write_tsv(args.output, rows, list(rows[0]))
    print(f"WROTE {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

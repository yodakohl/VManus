#!/usr/bin/env python3
"""Read an ordered recipe stream while preserving component order in clauses."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_READER = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/src/stream_read.py"
ORDERED_RENDERER = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/src/ordered_renderer.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gdt436_base_stream_reader", BASE_READER)
ORDERED = load_module("gdt437_ordered_renderer_for_stream", ORDERED_RENDERER)


def stream_rows(input_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Run GDT436 state tracking, then render each licensed card in written order."""
    rows = BASE.stream_rows(input_rows)
    output: list[dict[str, object]] = []
    for row in rows:
        baseline_clause = str(row["reader_clause_de"])
        if str(row["reader_status"]).startswith("STOP"):
            output.append({
                **row,
                "baseline_reader_clause_de": baseline_clause,
                "order_repair_rule": "NO_READING__STATE_UNCHANGED",
                "clause_changed_by_order_repair": "NO",
            })
            continue
        atoms = str(row["component_recipe"]).split("+")
        explicit_actions = [] if row["explicit_action_roots"] == "NONE" else str(row["explicit_action_roots"]).split("|")
        inherited_action = "" if row["inherited_action_root"] == "NONE" else str(row["inherited_action_root"])
        inherited_argument = "" if row["inherited_argument_root"] == "NONE" else str(row["inherited_argument_root"])
        clause, rule = ORDERED.render_ordered_clause(
            str(row["register"]), atoms, explicit_actions, inherited_action, inherited_argument
        )
        output.append({
            **row,
            "reader_clause_de": clause,
            "baseline_reader_clause_de": baseline_clause,
            "order_repair_rule": rule,
            "clause_changed_by_order_repair": "YES" if clause != baseline_clause else "NO",
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Ordered event TSV")
    parser.add_argument("--output", required=True, type=Path, help="Destination TSV")
    args = parser.parse_args()
    rows = stream_rows(BASE.read_tsv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    BASE.write_tsv(args.output, rows, list(rows[0]))
    print(f"WROTE {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

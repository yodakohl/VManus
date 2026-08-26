#!/usr/bin/env python3
"""Explain why a visible component recipe passes or stops at the GDT441 gate."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"
DECK = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck/artifacts/gdt442_47_stop_rule_deck.tsv"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True, help="Ordered component recipe, e.g. A_ADDR+T+S+OR")
    parser.add_argument("--incoming-action", default="NONE", help="Current owner-local action head")
    parser.add_argument("--scope-incoming-action", default=None, help="Current statement-local scope head")
    parser.add_argument("--next-recipe", default="NONE", help="Optional one-card visible lookahead")
    args = parser.parse_args()

    reader = load_module("gdt441_reader_for_stop_explanation", READER_PATH)
    with DECK.open(encoding="utf-8", newline="") as handle:
        deck = {row["blocked_rule"]: row for row in csv.DictReader(handle, delimiter="\t")}
    gate = reader.gate_recipe(
        args.recipe.upper(), args.incoming_action.upper(), args.next_recipe.upper(),
        None if args.scope_incoming_action is None else args.scope_incoming_action.upper(),
    )
    blocked = [] if gate["blocked_factor_rules"] == "NONE" else gate["blocked_factor_rules"].split("|")
    explanation = {
        "recipe": args.recipe.upper(),
        **gate,
        "blocked_rule_explanations": [
            {
                "blocked_rule": rule,
                "factor_family": deck.get(rule, {}).get("factor_family", "UNSEEN_ATOM_OR_OUTSIDE_DECK"),
                "reader_decision": deck.get(rule, {}).get("reader_decision", "STOP"),
                "automatic_repair": "NONE",
            }
            for rule in blocked
        ],
        "occurrence_prediction": "NO__VISIBLE_RECIPE_REQUIRED",
    }
    print(json.dumps(explanation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

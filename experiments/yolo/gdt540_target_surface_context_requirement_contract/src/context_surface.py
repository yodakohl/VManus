#!/usr/bin/env python3
"""Inspect one GDT540 surface under an optional same-statement state."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
CONTRACT = (
    ROOT
    / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
    / "gdt540_145_surface_context_contract.tsv"
)


def roots(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply the GDT540 action/argument intake rule to one target surface."
    )
    parser.add_argument("surface")
    parser.add_argument("--active-action", default="NONE")
    parser.add_argument("--active-argument", default="NONE")
    args = parser.parse_args()

    with CONTRACT.open(encoding="utf-8", newline="") as handle:
        rows = {row["surface"]: row for row in csv.DictReader(handle, delimiter="\t")}
    row = rows.get(args.surface)
    if row is None:
        print(json.dumps({
            "status": "UNKNOWN_GDT540_TARGET_SURFACE",
            "surface": args.surface,
            "delegation": "GDT539_OR_LOWER_READER",
        }, ensure_ascii=False, indent=2))
        return 2

    visible_actions = roots(row["visible_action_roots"])
    visible_arguments = roots(row["visible_argument_roots"])
    active_action = "" if args.active_action == "NONE" else args.active_action
    active_argument = "" if args.active_argument == "NONE" else args.active_argument

    if visible_actions:
        resolved_action = visible_actions[-1]
        action_source = "VISIBLE_SURFACE"
    elif active_action:
        resolved_action = active_action
        action_source = "SAME_STATEMENT_STATE"
    else:
        resolved_action = "NONE"
        action_source = "MISSING"

    if visible_arguments:
        resolved_argument = visible_arguments[-1]
        argument_source = "VISIBLE_SURFACE"
    elif active_argument:
        resolved_argument = active_argument
        argument_source = "SAME_STATEMENT_STATE"
    else:
        resolved_argument = "NONE"
        argument_source = "OBJECTLESS"

    status = (
        "READY_FOR_CONTEXTUAL_WORKING_READING"
        if resolved_action != "NONE"
        else "NONVERBAL_FRAGMENT_ONLY__MISSING_ACTIVE_ACTION"
    )
    result = {
        "status": status,
        "surface": row["surface"],
        "recipe": row["final_recipe"],
        "observed_requirement_modes": row["observed_requirement_modes"],
        "visible_action_roots": row["visible_action_roots"],
        "visible_argument_roots": row["visible_argument_roots"],
        "input_active_action": args.active_action,
        "input_active_argument": args.active_argument,
        "resolved_action_root": resolved_action,
        "action_source": action_source,
        "resolved_argument_root": resolved_argument,
        "argument_source": argument_source,
        "future_action_contract": row["future_action_contract"],
        "future_argument_contract": row["future_argument_contract"],
        "new_page_intake_de": row["new_page_intake_de"],
        "guard": "WORKING_CONTEXT_INTAKE__NO_PLAINTEXT_OR_NEW_RECIPE_CLAIM",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

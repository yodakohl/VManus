#!/usr/bin/env python3
"""Replay an ordered recipe stream with optional visible recipe replacements."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
COMMAND_PATH = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMMAND = load_module("gdt455_integrated_intake", COMMAND_PATH)
SCOPE = COMMAND.CERTIFIER.LEGACY.READER.SCOPE


def atoms_of(recipe: str) -> list[str]:
    return [] if recipe in {"", "NONE", "EMPTY_RECIPE"} else recipe.split("+")


def same_scope(left: dict[str, str], right: dict[str, str]) -> bool:
    return (
        left["statement_id"] == right["statement_id"]
        and left["physical_page"] == right["physical_page"]
        and left["owner_de"] == right["owner_de"]
    )


def run_stream(
    source_rows: list[dict[str, str]],
    replacements: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Run left to right; stopped cards preserve their owner bank and scope."""
    replacements = replacements or {}
    rows = sorted(source_rows, key=lambda row: int(row["stream_ordinal"]))
    bank_action: dict[tuple[str, str], str] = {}
    bank_argument: dict[tuple[str, str], str] = {}
    seen_banks: set[tuple[str, str]] = set()
    scope_active: dict[str, dict[str, object] | None] = {}
    scope_ordinals: dict[str, int] = {}
    output: list[dict[str, object]] = []

    for index, source in enumerate(rows):
        event_id = source["event_id"]
        statement_id = source["statement_id"]
        bank = (source["physical_page"], source["owner_de"])
        recipe = replacements.get(event_id, source["component_recipe"]).upper()
        mutation = "YES" if event_id in replacements else "NO"
        next_recipe = "NONE"
        if index + 1 < len(rows) and same_scope(source, rows[index + 1]):
            next_event = rows[index + 1]
            next_recipe = replacements.get(next_event["event_id"], next_event["component_recipe"]).upper()

        action_before = bank_action.get(bank, "NONE")
        argument_before = bank_argument.get(bank, "NONE")
        previous_scope = scope_active.get(statement_id)
        scope_before = str(previous_scope["action"]) if previous_scope else "NONE"
        scope_ordinal = scope_ordinals.get(statement_id, 0) + 1
        scope_ordinals[statement_id] = scope_ordinal
        bank_was_new = bank not in seen_banks
        seen_banks.add(bank)

        certificate = COMMAND.issue_integrated_certificate(
            recipe,
            action_before,
            argument_before,
            scope_before,
            next_recipe,
        )
        decision = str(certificate["final_execution_decision"])
        if decision == "STOP":
            action_after = action_before
            argument_after = argument_before
            scope_after_object = previous_scope
        else:
            action_after = str(certificate["outgoing_action_v2"])
            argument_after = str(certificate["outgoing_argument_v2"])
            bank_action[bank] = action_after
            bank_argument[bank] = argument_after
            scope_after_object = SCOPE.active_after_card(
                atoms_of(recipe),
                {"event_id": event_id, "source_event_id": event_id},
                scope_ordinal,
                previous_scope,
            )
        scope_active[statement_id] = scope_after_object
        scope_after = str(scope_after_object["action"]) if scope_after_object else "NONE"

        output.append({
            "stream_ordinal": source["stream_ordinal"],
            "event_id": event_id,
            "statement_id": statement_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_de": source["owner_de"],
            "state_bank_id": f"{source['physical_page']}::{source['owner_de']}",
            "state_bank_was_new": "YES" if bank_was_new else "NO",
            "source_recipe": source["component_recipe"],
            "visible_recipe": recipe,
            "recipe_replaced": mutation,
            "visible_next_recipe": next_recipe,
            "incoming_action": action_before,
            "incoming_argument": argument_before,
            "scope_incoming_action": scope_before,
            "decision": decision,
            "execution_route": certificate["final_execution_route"],
            "blocked_factor_rules": certificate["blocked_factor_rules"],
            "stop_preserves_state": certificate["execution_stop_preserves_state"],
            "outgoing_action": action_after,
            "outgoing_argument": argument_after,
            "scope_outgoing_action": scope_after,
            "identity_status": certificate["identity_status"],
            "advisory_history_status": certificate["advisory_history_status"],
            "identity_can_override": "NO",
            "advisory_can_override": "NO",
            "other_bank_write_count": 0,
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--schedule", type=Path)
    args = parser.parse_args()
    replacements: dict[str, str] = {}
    if args.schedule:
        schedule_rows = read_tsv(args.schedule)
        replacements = {row["event_id"]: row["replacement_recipe"] for row in schedule_rows}
    write_tsv(args.output, run_stream(read_tsv(args.input), replacements))
    print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

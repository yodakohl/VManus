#!/usr/bin/env python3
"""Read an ordered event TSV with per-owner action/argument state banks."""

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
GDT416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/src/run.py"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get(row: dict[str, str], *names: str, default: str = "") -> str:
    for name in names:
        if name in row and row[name] != "":
            return row[name]
    return default


def stream_rows(input_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    compiler = load_module("gdt416_compiler", GDT416)
    catalog = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
    known_atoms = {row["atom"] for row in read_tsv(COMPONENTS)}
    active_action: dict[tuple[str, str], str] = {}
    active_argument: dict[tuple[str, str], str] = {}
    seen_banks: set[tuple[str, str]] = set()
    output: list[dict[str, object]] = []

    for ordinal, row in enumerate(input_rows, start=1):
        event_id = get(row, "global_running_event_id", "event_id", default=f"INPUT-E{ordinal:04d}")
        statement_id = get(row, "global_statement_id", "source_statement_id", "statement_id", default="UNASSIGNED_STATEMENT")
        page = get(row, "physical_page", "page")
        register = get(row, "register")
        owner = get(row, "owner_de", "owner")
        recipe = get(row, "component_recipe", "recipe").upper()
        surface = get(row, "surface", default="NONE")
        if not page or not register or not owner or not recipe:
            raise ValueError(f"Missing page/register/owner/recipe in row {ordinal}")
        atoms = recipe.split("+")
        unseen = [atom for atom in atoms if atom not in known_atoms]
        tier = catalog.get(recipe, {}).get("intake_tier", "T5_NO_LICENSED_RECIPE")
        key = (page, owner)
        action_before = active_action.get(key, "")
        argument_before = active_argument.get(key, "")
        bank_new = key not in seen_banks
        seen_banks.add(key)

        if unseen or tier == "T5_NO_LICENSED_RECIPE":
            output.append({
                "stream_ordinal": ordinal,
                "event_id": event_id,
                "statement_id": statement_id,
                "physical_page": page,
                "register": register,
                "owner_de": owner,
                "surface": surface,
                "component_recipe": recipe,
                "intake_tier": tier,
                "state_bank_was_new": "YES" if bank_new else "NO",
                "active_action_before": action_before or "NONE",
                "active_argument_before": argument_before or "NONE",
                "explicit_action_roots": "NONE",
                "explicit_argument_roots": "NONE",
                "inherited_action_root": "NONE",
                "inherited_argument_root": "NONE",
                "active_action_after": action_before or "NONE",
                "active_argument_after": argument_before or "NONE",
                "reader_status": "STOP__UNSEEN_ATOM" if unseen else "STOP__UNLICENSED_RECIPE",
                "reader_clause_de": "Keine Satzlesung; Zustand unverändert.",
            })
            continue

        explicit_actions = [atom for atom in atoms if atom in compiler.ACTION_ROOTS]
        explicit_arguments = [atom for atom in atoms if atom in compiler.ARGUMENT_ROOTS]
        inherited_action = ""
        action_after = action_before
        if explicit_actions:
            action_after = explicit_actions[-1]
        elif action_before and any(atom != "DY" for atom in atoms):
            inherited_action = action_before

        inherited_argument = ""
        argument_after = argument_before
        if explicit_arguments:
            argument_after = explicit_arguments[-1]
        elif argument_before and (explicit_actions or inherited_action) and atoms != ["DY"]:
            inherited_argument = argument_before

        if action_after:
            active_action[key] = action_after
        if argument_after:
            active_argument[key] = argument_after
        clause = compiler.render_clause(register, atoms, explicit_actions, inherited_action, inherited_argument)
        output.append({
            "stream_ordinal": ordinal,
            "event_id": event_id,
            "statement_id": statement_id,
            "physical_page": page,
            "register": register,
            "owner_de": owner,
            "surface": surface,
            "component_recipe": recipe,
            "intake_tier": tier,
            "state_bank_was_new": "YES" if bank_new else "NO",
            "active_action_before": action_before or "NONE",
            "active_argument_before": argument_before or "NONE",
            "explicit_action_roots": "|".join(explicit_actions) or "NONE",
            "explicit_argument_roots": "|".join(explicit_arguments) or "NONE",
            "inherited_action_root": inherited_action or "NONE",
            "inherited_argument_root": inherited_argument or "NONE",
            "active_action_after": action_after or "NONE",
            "active_argument_after": argument_after or "NONE",
            "reader_status": "READ_FROM_EXACT_RECIPE_AND_LEFT_CONTEXT",
            "reader_clause_de": clause,
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Ordered event TSV")
    parser.add_argument("--output", required=True, type=Path, help="Destination TSV")
    args = parser.parse_args()
    rows = stream_rows(read_tsv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(args.output, rows, list(rows[0]))
    print(f"WROTE {args.output} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

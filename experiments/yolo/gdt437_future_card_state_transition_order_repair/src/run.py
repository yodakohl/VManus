#!/usr/bin/env python3
"""Audit and repair order collapse in the 49-card state-transition deck."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair"
OUT = BASE / "artifacts"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
STREAM = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts/gdt436_4576_oracle_free_stream_readings.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts/gdt436_715_oracle_free_statement_readings.tsv"
ORDERED_RENDERER = BASE / "src/ordered_renderer.py"
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")


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


def transition(ordered, atoms: list[str], register: str, incoming_action: str, incoming_argument: str) -> dict[str, str]:
    compiler = ordered.COMPILER
    before_action = "" if incoming_action == "NONE" else incoming_action
    before_argument = "" if incoming_argument == "NONE" else incoming_argument
    actions = [atom for atom in atoms if atom in compiler.ACTION_ROOTS]
    arguments = [atom for atom in atoms if atom in compiler.ARGUMENT_ROOTS]
    inherited_action = ""
    outgoing_action = before_action
    if actions:
        outgoing_action = actions[-1]
    elif before_action and any(atom != "DY" for atom in atoms):
        inherited_action = before_action
    inherited_argument = ""
    outgoing_argument = before_argument
    if arguments:
        outgoing_argument = arguments[-1]
    elif before_argument and (actions or inherited_action) and atoms != ["DY"]:
        inherited_argument = before_argument
    baseline = compiler.render_clause(register, atoms, actions, inherited_action, inherited_argument)
    repaired, repair_rule = ordered.render_ordered_clause(register, atoms, actions, inherited_action, inherited_argument)
    return {
        "explicit_action_roots": "|".join(actions) or "NONE",
        "explicit_argument_roots": "|".join(arguments) or "NONE",
        "inherited_action_root": inherited_action or "NONE",
        "inherited_argument_root": inherited_argument or "NONE",
        "outgoing_action": outgoing_action or "NONE",
        "outgoing_argument": outgoing_argument or "NONE",
        "baseline_clause_de": baseline,
        "order_safe_clause_de": repaired,
        "order_repair_rule": repair_rule,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ordered = load_module("gdt437_ordered_renderer", ORDERED_RENDERER)
    stream_rows = read_tsv(STREAM)
    states = sorted({(row["active_action_before"], row["active_argument_before"]) for row in stream_rows})
    cards = [
        row for row in read_tsv(CATALOG)
        if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    ]

    matrix_rows: list[dict[str, object]] = []
    for card in sorted(cards, key=lambda row: row["component_recipe"]):
        atoms = card["component_recipe"].split("+")
        for incoming_action, incoming_argument in states:
            for register in REGISTERS:
                data = transition(ordered, atoms, register, incoming_action, incoming_argument)
                matrix_rows.append({
                    "component_recipe": card["component_recipe"],
                    "intake_tier": card["intake_tier"],
                    "register": register,
                    "incoming_action": incoming_action,
                    "incoming_argument": incoming_argument,
                    **data,
                    "clause_changed_by_order_repair": "YES" if data["baseline_clause_de"] != data["order_safe_clause_de"] else "NO",
                })
    write_tsv(OUT / "gdt437_12005_state_transition_matrix.tsv", matrix_rows, list(matrix_rows[0]))

    baseline_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    repaired_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for row in matrix_rows:
        common = (
            str(row["register"]), str(row["incoming_action"]), str(row["incoming_argument"]),
            str(row["outgoing_action"]), str(row["outgoing_argument"]),
        )
        baseline_groups[common + (str(row["baseline_clause_de"]),)].append(str(row["component_recipe"]))
        repaired_groups[common + (str(row["order_safe_clause_de"]),)].append(str(row["component_recipe"]))
    collision_rows: list[dict[str, object]] = []
    for index, (key, recipes) in enumerate(sorted(baseline_groups.items()), start=1):
        if len(recipes) < 2:
            continue
        repaired_signatures = {
            next(
                str(row["order_safe_clause_de"])
                for row in matrix_rows
                if row["component_recipe"] == recipe
                and row["register"] == key[0]
                and row["incoming_action"] == key[1]
                and row["incoming_argument"] == key[2]
            )
            for recipe in recipes
        }
        collision_rows.append({
            "collision_id": f"BC{len(collision_rows) + 1:03d}",
            "register": key[0],
            "incoming_action": key[1],
            "incoming_argument": key[2],
            "outgoing_action": key[3],
            "outgoing_argument": key[4],
            "baseline_clause_de": key[5],
            "colliding_recipes": "|".join(sorted(recipes)),
            "collision_recipe_count": len(recipes),
            "repaired_clause_count": len(repaired_signatures),
            "repair_status": "RESOLVED" if len(repaired_signatures) == len(recipes) else "STILL_COLLIDES",
        })
    write_tsv(OUT / "gdt437_245_baseline_collision_cells.tsv", collision_rows, list(collision_rows[0]))

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in matrix_rows:
        by_card[str(row["component_recipe"])].append(row)
    signature_rows: list[dict[str, object]] = []
    vectors: dict[str, tuple[tuple[str, ...], ...]] = {}
    for recipe, rows in sorted(by_card.items()):
        rows = sorted(rows, key=lambda row: (str(row["register"]), str(row["incoming_action"]), str(row["incoming_argument"])))
        vector = tuple((
            str(row["register"]), str(row["incoming_action"]), str(row["incoming_argument"]),
            str(row["outgoing_action"]), str(row["outgoing_argument"]), str(row["order_safe_clause_de"]),
        ) for row in rows)
        vectors[recipe] = vector
        digest = hashlib.sha256(json.dumps(vector, ensure_ascii=False).encode("utf-8")).hexdigest()
        sensitivity = {
            register: len({
                (str(row["outgoing_action"]), str(row["outgoing_argument"]), str(row["order_safe_clause_de"]))
                for row in rows if row["register"] == register
            })
            for register in REGISTERS
        }
        signature_rows.append({
            "component_recipe": recipe,
            "intake_tier": rows[0]["intake_tier"],
            "reachable_state_count": len(states),
            "register_count": len(REGISTERS),
            "transition_cell_count": len(rows),
            "order_repaired_cell_count": sum(row["clause_changed_by_order_repair"] == "YES" for row in rows),
            "state_sensitivity_per_register": "|".join(f"{register}:{sensitivity[register]}" for register in REGISTERS),
            "transition_signature_sha256": digest,
        })
    write_tsv(OUT / "gdt437_49_transition_signatures.tsv", signature_rows, list(signature_rows[0]))

    pair_rows: list[dict[str, object]] = []
    matrix_lookup = {
        (str(row["component_recipe"]), str(row["register"]), str(row["incoming_action"]), str(row["incoming_argument"])): row
        for row in matrix_rows
    }
    for left, right in itertools.combinations(sorted(vectors), 2):
        baseline_equal = 0
        repaired_equal = 0
        for incoming_action, incoming_argument in states:
            for register in REGISTERS:
                lrow = matrix_lookup[(left, register, incoming_action, incoming_argument)]
                rrow = matrix_lookup[(right, register, incoming_action, incoming_argument)]
                if (
                    lrow["outgoing_action"], lrow["outgoing_argument"], lrow["baseline_clause_de"]
                ) == (
                    rrow["outgoing_action"], rrow["outgoing_argument"], rrow["baseline_clause_de"]
                ):
                    baseline_equal += 1
                if (
                    lrow["outgoing_action"], lrow["outgoing_argument"], lrow["order_safe_clause_de"]
                ) == (
                    rrow["outgoing_action"], rrow["outgoing_argument"], rrow["order_safe_clause_de"]
                ):
                    repaired_equal += 1
        pair_rows.append({
            "left_recipe": left,
            "right_recipe": right,
            "comparison_cell_count": len(states) * len(REGISTERS),
            "baseline_equal_transition_count": baseline_equal,
            "order_safe_equal_transition_count": repaired_equal,
            "baseline_universal_collision": "YES" if baseline_equal == len(states) * len(REGISTERS) else "NO",
            "order_safe_universal_collision": "YES" if repaired_equal == len(states) * len(REGISTERS) else "NO",
        })
    write_tsv(OUT / "gdt437_1176_pairwise_signature_audit.tsv", pair_rows, list(pair_rows[0]))

    current_repairs: list[dict[str, object]] = []
    current_ordered_clause: dict[str, str] = {}
    for row in stream_rows:
        atoms = row["component_recipe"].split("+")
        actions = [] if row["explicit_action_roots"] == "NONE" else row["explicit_action_roots"].split("|")
        inherited_action = "" if row["inherited_action_root"] == "NONE" else row["inherited_action_root"]
        inherited_argument = "" if row["inherited_argument_root"] == "NONE" else row["inherited_argument_root"]
        repaired, rule = ordered.render_ordered_clause(row["register"], atoms, actions, inherited_action, inherited_argument)
        current_ordered_clause[row["event_id"]] = repaired
        if repaired == row["reader_clause_de"]:
            continue
        current_repairs.append({
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "inherited_action_root": row["inherited_action_root"],
            "old_clause_de": row["reader_clause_de"],
            "order_safe_clause_de": repaired,
            "repair_rule": rule,
            "meaning_change": "NO__RELATION_ARGUMENT_ORDER_ONLY",
        })
    write_tsv(OUT / "gdt437_68_current_order_repairs.tsv", current_repairs, list(current_repairs[0]))

    repaired_event_ids = {str(row["event_id"]) for row in current_repairs}
    statement_repair_rows: list[dict[str, object]] = []
    for statement in read_tsv(STATEMENTS):
        event_ids = statement["event_ids"].split("|")
        touched = [event_id for event_id in event_ids if event_id in repaired_event_ids]
        if not touched:
            continue
        new_reading = " ".join(current_ordered_clause[event_id] for event_id in event_ids)
        statement_repair_rows.append({
            "global_statement_id": statement["global_statement_id"],
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_de": statement["owner_de"],
            "event_count": statement["event_count"],
            "order_repaired_event_count": len(touched),
            "order_repaired_event_ids": "|".join(touched),
            "old_imperative_reading_de": statement["oracle_free_imperative_reading_de"],
            "order_safe_imperative_reading_de": new_reading,
            "meaning_change": "NO__RELATION_ARGUMENT_ORDER_ONLY",
        })
    write_tsv(OUT / "gdt437_59_current_statement_order_repairs.tsv", statement_repair_rows, list(statement_repair_rows[0]))

    repaired_collision_groups = [recipes for recipes in repaired_groups.values() if len(recipes) > 1]
    universal_baseline = [row for row in pair_rows if row["baseline_universal_collision"] == "YES"]
    universal_repaired = [row for row in pair_rows if row["order_safe_universal_collision"] == "YES"]
    result = {
        "status": "RELATION_ARGUMENT_ORDER_COLLISION_REPAIRED",
        "reachable_state_count": len(states),
        "main_future_card_count": len(cards),
        "register_count": len(REGISTERS),
        "transition_cell_count": len(matrix_rows),
        "baseline_collision_cell_count": len(collision_rows),
        "baseline_collision_recipe_pair": sorted({row["colliding_recipes"] for row in collision_rows}),
        "baseline_universal_pair_count": len(universal_baseline),
        "order_safe_collision_cell_count": len(repaired_collision_groups),
        "order_safe_universal_pair_count": len(universal_repaired),
        "unique_order_safe_transition_signature_count": len(set(vectors.values())),
        "current_event_order_repair_count": len(current_repairs),
        "current_statement_order_repair_count": len(statement_repair_rows),
        "pairwise_comparison_count": len(pair_rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt437_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

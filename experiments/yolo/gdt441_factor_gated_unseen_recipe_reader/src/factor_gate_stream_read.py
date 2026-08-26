#!/usr/bin/env python3
"""Read exact recipes first, then factor-licensed new combinations of known atoms."""

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
ORDERED_RENDERER = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/src/ordered_renderer.py"
SCOPE_PARSER = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/src/run.py"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
FOCUS = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_5051_focus_edge_portability.tsv"
PAIRS = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_649_adjacent_pair_portability.tsv"
CLOSES = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_639_close_edge_portability.tsv"


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


COMPILER = load_module("gdt416_compiler_for_factor_gate", GDT416)
ORDERED = load_module("gdt437_renderer_for_factor_gate", ORDERED_RENDERER)
SCOPE = load_module("gdt404_scope_parser_for_factor_gate", SCOPE_PARSER)
CATALOG_ROWS = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
COMPONENT_VALUES = {row["atom"]: row["working_value_de"] for row in read_tsv(COMPONENTS)}
KNOWN_ATOMS = set(COMPONENT_VALUES)
FOCUS_ROOTS = {"AIIN", "AIN", "AIR", "AL", "AR", "E", "EE", "EEE", "L", "OR", "Y"}
PORTABLE_FOCUS_EDGES = {
    row["focus_edge"] for row in read_tsv(FOCUS)
    if row["portability_status"] == "CROSS_PAGE_EXACT_FOCUS_EDGE"
}
LOCAL_FOCUS_EDGES = {
    row["focus_edge"] for row in read_tsv(FOCUS)
    if row["portability_status"] == "LOCAL_ACTION_FOCUS_EDGE"
}
LOCAL_OWNER_FOCUS_EDGES = {
    row["focus_edge"] for row in read_tsv(FOCUS)
    if row["portability_status"] == "LOCAL_OWNER_CHANNEL_ALLOWED"
}
PORTABLE_ACTION_PAIRS = {
    row["ordered_pair"] for row in read_tsv(PAIRS)
    if row["portability_status"] != "LOCAL_ADJACENT_PAIR"
}
LOCAL_ACTION_PAIRS = {
    row["ordered_pair"] for row in read_tsv(PAIRS)
    if row["portability_status"] == "LOCAL_ADJACENT_PAIR"
}
PORTABLE_CLOSE_TARGETS = {row["close_target_action"] for row in read_tsv(CLOSES)}


def get(row: dict[str, str], *names: str, default: str = "") -> str:
    for name in names:
        if name in row and row[name] != "":
            return row[name]
    return default


def ordered_literal(atoms: list[str]) -> str:
    return " · ".join(COMPONENT_VALUES[atom] for atom in atoms)


def gate_recipe(
    recipe: str,
    incoming_action: str = "NONE",
    next_recipe: str = "NONE",
    scope_incoming_action: str | None = None,
) -> dict[str, str]:
    atoms = recipe.split("+")
    unseen = [atom for atom in atoms if atom not in KNOWN_ATOMS]
    if unseen:
        return {
            "factor_gate_status": "STOP__UNSEEN_ATOM",
            "portable_factor_rules": "NONE",
            "amber_factor_rules": "NONE",
            "blocked_factor_rules": "UNSEEN:" + "|".join(unseen),
        }
    action_positions = [(index, atom) for index, atom in enumerate(atoms) if atom in COMPILER.ACTION_ROOTS]
    portable: list[str] = []
    amber: list[str] = []
    blocked: list[str] = []
    selectors: list[str] = []
    scope_action = incoming_action if scope_incoming_action is None else scope_incoming_action
    active = None if scope_action == "NONE" else {
        "action": scope_action,
        "event_id": "PREVIOUS",
        "card_ordinal": 0,
        "atom_ordinal": 0,
        "r_mode": "NONE",
    }
    next_atoms = [] if next_recipe == "NONE" else next_recipe.split("+")
    next_event = None if not next_atoms else {"event_id": "NEXT"}
    event = {"event_id": "CURRENT"}
    for index, focus in ((index, atom) for index, atom in enumerate(atoms) if atom in FOCUS_ROOTS):
        selection = SCOPE.choose_attachment(
            focus, index + 1, atoms, event, 1, active, next_event, next_atoms,
        )
        action = str(selection["action"] or "OWNER")
        selectors.append(SCOPE.selector_rule(focus, selection, atoms))
        edge = f"{action}<-{focus}"
        if edge in PORTABLE_FOCUS_EDGES or edge == "R<-E":
            portable.append("FOCUS:" + edge)
        elif edge in LOCAL_FOCUS_EDGES or edge in LOCAL_OWNER_FOCUS_EDGES:
            amber.append("FOCUS:" + edge)
        else:
            blocked.append("FOCUS:" + edge)
    for index in range(len(atoms) - 1):
        if atoms[index] not in COMPILER.ACTION_ROOTS or atoms[index + 1] not in COMPILER.ACTION_ROOTS:
            continue
        pair = f"{atoms[index]}>{atoms[index + 1]}"
        if pair in PORTABLE_ACTION_PAIRS:
            portable.append("PAIR:" + pair)
        elif pair in LOCAL_ACTION_PAIRS:
            amber.append("PAIR:" + pair)
        else:
            blocked.append("PAIR:" + pair)
    if "DY" in atoms:
        target = action_positions[-1][1] if action_positions else "" if incoming_action == "NONE" else incoming_action
        if not target:
            blocked.append("CLOSE:NO_ACTIVE_ACTION")
        elif target in PORTABLE_CLOSE_TARGETS:
            portable.append("CLOSE:" + target)
        else:
            blocked.append("CLOSE:" + target)
    status = "STOP__UNLICENSED_FACTOR" if blocked else "FACTOR_AMBER_LOCAL_APPENDIX" if amber else "FACTOR_GREEN_CROSS_PAGE"
    return {
        "factor_gate_status": status,
        "scope_selector_rules": "|".join(selectors) or "NONE",
        "portable_factor_rules": "|".join(portable) or "NONE",
        "amber_factor_rules": "|".join(amber) or "NONE",
        "blocked_factor_rules": "|".join(blocked) or "NONE",
    }


def stream_rows(input_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    active_action: dict[tuple[str, str], str] = {}
    active_argument: dict[tuple[str, str], str] = {}
    seen_banks: set[tuple[str, str]] = set()
    scope_active: dict[str, dict[str, object] | None] = {}
    scope_card_ordinals: dict[str, int] = {}
    output: list[dict[str, object]] = []
    for ordinal, row in enumerate(input_rows, start=1):
        event_id = get(row, "global_running_event_id", "event_id", default=f"INPUT-E{ordinal:04d}")
        statement_id = get(row, "global_statement_id", "source_statement_id", "statement_id", default=f"UNASSIGNED_STATEMENT_{ordinal:04d}")
        page = get(row, "physical_page", "page")
        register = get(row, "register")
        owner = get(row, "owner_de", "owner")
        recipe = get(row, "component_recipe", "recipe").upper()
        surface = get(row, "surface", default="NONE")
        if not page or not register or not owner or not recipe:
            raise ValueError(f"Missing page/register/owner/recipe in row {ordinal}")
        atoms = recipe.split("+")
        key = (page, owner)
        before_action = active_action.get(key, "")
        before_argument = active_argument.get(key, "")
        bank_new = key not in seen_banks
        seen_banks.add(key)
        previous_scope = scope_active.get(statement_id)
        scope_card_ordinal = scope_card_ordinals.get(statement_id, 0) + 1
        scope_card_ordinals[statement_id] = scope_card_ordinal
        next_recipe = "NONE"
        if ordinal < len(input_rows):
            candidate = input_rows[ordinal]
            candidate_statement = get(candidate, "global_statement_id", "source_statement_id", "statement_id", default=f"UNASSIGNED_STATEMENT_{ordinal + 1:04d}")
            candidate_page = get(candidate, "physical_page", "page")
            candidate_owner = get(candidate, "owner_de", "owner")
            if candidate_statement == statement_id and candidate_page == page and candidate_owner == owner:
                next_recipe = get(candidate, "component_recipe", "recipe", default="NONE").upper()
        factor = gate_recipe(
            recipe,
            before_action or "NONE",
            next_recipe,
            str(previous_scope["action"]) if previous_scope else "NONE",
        )
        card = CATALOG_ROWS.get(recipe)
        exact = card is not None
        accepted = exact or not factor["factor_gate_status"].startswith("STOP")
        if not accepted:
            output.append({
                "stream_ordinal": ordinal, "event_id": event_id, "statement_id": statement_id,
                "physical_page": page, "register": register, "owner_de": owner, "surface": surface,
                "component_recipe": recipe, "intake_tier": "T5_FACTOR_STOP",
                "recipe_source": "UNLICENSED_NEW_COMBINATION", "state_bank_was_new": "YES" if bank_new else "NO",
                "active_action_before": before_action or "NONE", "active_argument_before": before_argument or "NONE",
                "explicit_action_roots": "NONE", "explicit_argument_roots": "NONE",
                "inherited_action_root": "NONE", "inherited_argument_root": "NONE",
                "active_action_after": before_action or "NONE", "active_argument_after": before_argument or "NONE",
                **factor, "reader_status": factor["factor_gate_status"],
                "ordered_literal_reading_de": "KEINE LIZENZIERTE KERNFOLGE",
                "reader_clause_de": "Keine Satzlesung; Zustand unverändert.",
                "dual_channel_reading_de": "Keine Satzlesung; Zustand unverändert.",
            })
            continue

        explicit_actions = [atom for atom in atoms if atom in COMPILER.ACTION_ROOTS]
        explicit_arguments = [atom for atom in atoms if atom in COMPILER.ARGUMENT_ROOTS]
        inherited_action = ""
        after_action = before_action
        if explicit_actions:
            after_action = explicit_actions[-1]
        elif before_action and any(atom != "DY" for atom in atoms):
            inherited_action = before_action
        inherited_argument = ""
        after_argument = before_argument
        if explicit_arguments:
            after_argument = explicit_arguments[-1]
        elif before_argument and (explicit_actions or inherited_action) and atoms != ["DY"]:
            inherited_argument = before_argument
        if after_action:
            active_action[key] = after_action
        if after_argument:
            active_argument[key] = after_argument
        scope_active[statement_id] = SCOPE.active_after_card(
            atoms, {"event_id": event_id}, scope_card_ordinal, previous_scope,
        )
        clause, order_rule = ORDERED.render_ordered_clause(register, atoms, explicit_actions, inherited_action, inherited_argument)
        literal = card["literal_reading_de"] if card else ordered_literal(atoms)
        if exact:
            tier = card["intake_tier"]
            source = "EXACT_CATALOG_KEY"
            status = "READ_EXACT_CATALOG_WITH_LEFT_CONTEXT"
        else:
            tier = "T5B_FACTOR_GREEN" if factor["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" else "T5C_FACTOR_AMBER"
            source = "NEW_VISIBLE_RECIPE__KNOWN_FACTORS_ONLY"
            status = "READ_NEW_FACTOR_COMPOSITION" if tier == "T5B_FACTOR_GREEN" else "READ_NEW_FACTOR_COMPOSITION_AMBER"
        output.append({
            "stream_ordinal": ordinal, "event_id": event_id, "statement_id": statement_id,
            "physical_page": page, "register": register, "owner_de": owner, "surface": surface,
            "component_recipe": recipe, "intake_tier": tier, "recipe_source": source,
            "state_bank_was_new": "YES" if bank_new else "NO",
            "active_action_before": before_action or "NONE", "active_argument_before": before_argument or "NONE",
            "explicit_action_roots": "|".join(explicit_actions) or "NONE",
            "explicit_argument_roots": "|".join(explicit_arguments) or "NONE",
            "inherited_action_root": inherited_action or "NONE", "inherited_argument_root": inherited_argument or "NONE",
            "active_action_after": after_action or "NONE", "active_argument_after": after_argument or "NONE",
            **factor, "reader_status": status, "order_repair_rule": order_rule,
            "ordered_literal_reading_de": literal, "reader_clause_de": clause,
            "dual_channel_reading_de": f"Kernfolge: {literal}. {clause}",
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

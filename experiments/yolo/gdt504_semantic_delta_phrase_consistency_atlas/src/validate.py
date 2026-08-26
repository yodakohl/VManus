#!/usr/bin/env python3
"""Independently validate every GDT504 semantic-delta alignment and marker."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt504_semantic_delta_phrase_consistency_atlas"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G502 = ROOT / "experiments/yolo/gdt502_supported_frontier_comparison_cards/artifacts"

CARDS_IN = G502 / "gdt502_46_supported_frontier_cards.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
EXPANSIONS_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
CARDS_OUT = ART / "gdt504_46_semantic_delta_cards.tsv"
EFFECTS_OUT = ART / "gdt504_59_token_effect_checks.tsv"
OPERATIONS_OUT = ART / "gdt504_14_delta_operation_summary.tsv"
ATOMS_OUT = ART / "gdt504_10_atom_effect_summary.tsv"
REGISTERS_OUT = ART / "gdt504_5_register_delta_coverage.tsv"
DEPTH_OUT = ART / "gdt504_3_support_depth_summary.tsv"
READABLE_OUT = ART / "GDT504_SEMANTIC_DELTA_PHRASE_ATLAS.md"
RESULT_OUT = ART / "gdt504_result.json"
VALIDATION_OUT = ART / "gdt504_validation.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
PAIR_CHANNELS = {"ORDERED_PAIR_TARGET_REGISTER", "ORDERED_PAIR_OTHER_REGISTER"}
STATUS = "FORTY_SIX_PHRASE_DELTAS_RESOLVE_WITH_FIXED_VALUES__PAIR_FRAME_EDITS_REMAIN_SEPARATE"
GUARD = "EDITORIAL_SEMANTIC_DELTA_ONLY__NO_TARGET_OBSERVATION_OR_SURFACE_PREDICTION"

OP_ORDER = (
    "ADD_DESTINATION", "ADD_UNIT_ARGUMENT", "ADD_SECOND_POST_ARGUMENT",
    "EXPLICITIZE_INHERITED_POST", "ADD_SERIAL_ACTION", "ADD_SERIAL_ACTION_AND_GRADE",
    "COUNTED_REPEAT", "COUNTED_REPEAT_AND_EXPLICITIZE_POST",
    "PAIR_REPLACE_CARRIER_CONTEXT_WITH_POST", "PAIR_REPLACE_CARRIER_CONTEXT_WITH_GRADE",
    "PAIR_DROP_CONTINUATION", "PAIR_DROP_ORIGIN", "PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS",
    "PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS",
)


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def tokens(recipe: str) -> list[str]:
    return [] if recipe == "NONE" else recipe.split("+")


def token_text(items: list[str]) -> str:
    return "+".join(items) if items else "NONE"


def align(left: list[str], right: list[str]) -> list[tuple[int, int]]:
    matrix = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(len(left) - 1, -1, -1):
        for j in range(len(right) - 1, -1, -1):
            if left[i] == right[j]:
                matrix[i][j] = matrix[i + 1][j + 1] + 1
            else:
                matrix[i][j] = max(matrix[i + 1][j], matrix[i][j + 1])
    result: list[tuple[int, int]] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] == right[j] and matrix[i][j] == matrix[i + 1][j + 1] + 1:
            result.append((i, j))
            i += 1
            j += 1
        elif matrix[i + 1][j] >= matrix[i][j + 1]:
            i += 1
        else:
            j += 1
    return result


def marker(atom: str, register: str, expansions: dict[tuple[str, str], str], duplicate: bool) -> str:
    if duplicate:
        return "zweimal"
    special = {
        "CHD": "bearbeite", "E": "grad i", "O": "ausführung", "OL": "weiter",
        "AR": "ausgang", "D_ADDR": "bezeichneten stelle",
    }
    if atom == "CH":
        return "entnimm" if register in {"SOURCE_SECTION_T", "BIOLOGICAL"} else "nimm"
    if atom == "Y" and register == "SOURCE_SECTION_T":
        return "laufenden eintrag"
    return special.get(atom, expansions.get((atom, register), "")).casefold()


def phrase_has(text: str, needle: str) -> bool:
    return bool(needle) and needle.casefold() in text.casefold()


def operation(pair: bool, added: list[str], removed: list[str], support: list[str], inherited: str) -> str:
    if pair:
        mapping = {
            (("Y",), ("O", "OL")): "PAIR_REPLACE_CARRIER_CONTEXT_WITH_POST",
            (("E",), ("O", "AR")): "PAIR_REPLACE_CARRIER_CONTEXT_WITH_GRADE",
            ((), ("OL",)): "PAIR_DROP_CONTINUATION",
            ((), ("AR",)): "PAIR_DROP_ORIGIN",
            ((), ("OR", "Y")): "PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS",
            ((), ("OL", "D_ADDR", "Y")): "PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS",
        }
        return mapping[(tuple(added), tuple(removed))]
    if added == ["AL"]:
        return "ADD_DESTINATION"
    if added == ["OR"]:
        return "ADD_UNIT_ARGUMENT"
    if added == ["Y"]:
        return "EXPLICITIZE_INHERITED_POST" if inherited == "Y" else "ADD_SECOND_POST_ARGUMENT"
    actions = [item for item in added if item in ACTION_ROOTS]
    repeated = any(item in support for item in actions)
    if repeated and added == ["CH", "Y"]:
        return "COUNTED_REPEAT_AND_EXPLICITIZE_POST"
    if repeated and len(added) == 1:
        return "COUNTED_REPEAT"
    if actions and "E" in added:
        return "ADD_SERIAL_ACTION_AND_GRADE"
    if len(actions) == len(added) == 1:
        return "ADD_SERIAL_ACTION"
    raise KeyError((added, support, inherited))


def main() -> int:
    source_fields, source_cards = read_tsv(CARDS_IN)
    clause_fields, clauses = read_tsv(CLAUSES_IN)
    dictionary_fields, dictionary = read_tsv(DICTIONARY_IN)
    expansion_fields, expansion_rows = read_tsv(EXPANSIONS_IN)
    card_fields, cards = read_tsv(CARDS_OUT)
    effect_fields, effects = read_tsv(EFFECTS_OUT)
    operation_fields, operations = read_tsv(OPERATIONS_OUT)
    atom_fields, atoms = read_tsv(ATOMS_OUT)
    register_fields, registers = read_tsv(REGISTERS_OUT)
    depth_fields, depths = read_tsv(DEPTH_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("all_table_counts_exact", (len(source_cards), len(clauses), len(dictionary), len(expansion_rows), len(cards), len(effects), len(operations), len(atoms), len(registers), len(depths)) == (46, 4576, 46, 95, 46, 59, 14, 10, 5, 3), "46/4576/46/95 -> 46/59/14/10/5/3")
    check("source_schema_complete", {"comparison_card_id", "target_action_recipe", "support_recipe", "selected_old_clause_de"} <= set(source_fields), f"fields={len(source_fields)}")
    check("clause_schema_complete", {"component_recipe", "imperative_clause_de", "inherited_argument_root", "roundtrip_exact"} <= set(clause_fields), f"fields={len(clause_fields)}")
    check("dictionary_schema_complete", {"atom", "working_value_de"} <= set(dictionary_fields), f"fields={len(dictionary_fields)}")
    check("expansion_schema_complete", {"root", "register", "owner_local_expansion_de"} <= set(expansion_fields), f"fields={len(expansion_fields)}")
    check("card_schema_complete", {"semantic_delta_card_id", "target_only_tokens", "carrier_only_tokens", "delta_operation", "semantic_phrase_delta_consistent"} <= set(card_fields), f"fields={len(card_fields)}")
    check("effect_schema_complete", {"token_effect_id", "effect_side", "atom", "effect_check_passed"} <= set(effect_fields), f"fields={len(effect_fields)}")
    check("summary_schemas_complete", {"delta_operation", "card_count"} <= set(operation_fields) and {"atom", "total_effect_count"} <= set(atom_fields) and {"target_register", "semantic_delta_card_count"} <= set(register_fields) and {"support_depth", "card_count"} <= set(depth_fields), "four summary schemas")
    check("card_ids_sequential", [row["semantic_delta_card_id"] for row in cards] == [f"G504-D{i:02d}" for i in range(1, 47)], "D01..D46")
    check("effect_ids_sequential", [row["token_effect_id"] for row in effects] == [f"G504-E{i:03d}" for i in range(1, 60)], "E001..E059")
    check("operation_order_exact", [row["delta_operation"] for row in operations] == list(OP_ORDER), "14 fixed operations")
    check("register_order_exact", [row["target_register"] for row in registers] == list(REGISTERS), "five fixed registers")
    check("depth_order_exact", [row["support_depth"] for row in depths] == ["DIRECT_LOCAL_DELTA", "CROSS_REGISTER_NORMALIZED_DELTA", "PAIR_BACKBONE_FRAME_EDIT"], "three depths")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    expansions = {(row["root"], row["register"]): row["owner_local_expansion_de"] for row in expansion_rows}
    clauses_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_key[(row["component_recipe"], row["register"], row["imperative_clause_de"])].append(row)
    effects_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in effects:
        effects_by_card[row["source_comparison_card_id"]].append(row)

    expected_operations: Counter[str] = Counter()
    expected_depths: Counter[str] = Counter()
    expected_atom_sides: Counter[tuple[str, str]] = Counter()
    expected_registers: Counter[str] = Counter()
    shared_total = added_total = removed_total = 0
    for index, (source, card) in enumerate(zip(source_cards, cards), start=1):
        prefix = f"card_{index:02d}"
        left = tokens(source["target_action_recipe"])
        right = tokens(source["support_recipe"])
        pairs = align(left, right)
        left_used = {i for i, _j in pairs}
        right_used = {j for _i, j in pairs}
        shared = [left[i] for i, _j in pairs]
        added = [item for i, item in enumerate(left) if i not in left_used]
        removed = [item for j, item in enumerate(right) if j not in right_used]
        added_positions = ",".join(str(i + 1) for i in range(len(left)) if i not in left_used) or "NONE"
        removed_positions = ",".join(str(j + 1) for j in range(len(right)) if j not in right_used) or "NONE"
        pair_mode = source["support_channel"] in PAIR_CHANNELS
        witnesses = clauses_by_key[(source["support_recipe"], source["support_register"], source["selected_old_clause_de"])]
        inherited = {row["inherited_argument_root"] for row in witnesses}
        witness = sorted(witnesses, key=lambda row: row["global_running_event_id"])[0] if witnesses else None
        inherited_value = next(iter(inherited)) if len(inherited) == 1 else "MIXED"
        expected_operation = operation(pair_mode, added, removed, right, inherited_value)
        expected_depth = "PAIR_BACKBONE_FRAME_EDIT" if pair_mode else "DIRECT_LOCAL_DELTA" if source["support_register_relation"] == "SAME_REGISTER" else "CROSS_REGISTER_NORMALIZED_DELTA"
        expected_alignment = "ORDERED_PAIR_CARRIER_ALIGNMENT" if pair_mode else "EXACT_PARTIAL_RECIPE_EXTENSION"
        shared_total += len(shared)
        added_total += len(added)
        removed_total += len(removed)
        expected_operations[expected_operation] += 1
        expected_depths[expected_depth] += 1
        expected_registers[source["target_register"]] += 1

        check(f"{prefix}_source_join", card["source_comparison_card_id"] == source["comparison_card_id"] and card["target_matrix_cell_id"] == source["target_matrix_cell_id"] and card["target_action_recipe"] == source["target_action_recipe"] and card["support_recipe"] == source["support_recipe"], source["comparison_card_id"])
        check(f"{prefix}_alignment_exact", card["alignment_mode"] == expected_alignment and card["aligned_shared_tokens"] == token_text(shared) and card["target_only_positions"] == added_positions and card["target_only_tokens"] == token_text(added) and card["carrier_only_positions"] == removed_positions and card["carrier_only_tokens"] == token_text(removed), f"shared={shared},add={added},remove={removed}")
        check(f"{prefix}_partial_or_pair_rule", (pair_mode and witness is not None and witness["explicit_action_roots"].replace("|", "+") == source["ordered_action_pair"]) or (not pair_mode and not removed), expected_alignment)
        check(f"{prefix}_clause_roundtrip", bool(witnesses) and len(inherited) == 1 and all(row["roundtrip_exact"] == "YES" for row in witnesses) and card["selected_old_clause_de"] == source["selected_old_clause_de"] and card["source_inherited_argument_root"] == inherited_value and card["source_template"] == witness["template"], f"witnesses={len(witnesses)}")
        check(f"{prefix}_classification_exact", card["support_depth"] == expected_depth and card["delta_operation"] == expected_operation, f"{expected_depth}/{expected_operation}")
        check(f"{prefix}_fixed_target", card["target_current_default_phrase_de"] == source["target_current_default_phrase_de"] and card["target_phrase_changed"] == "NO" and card["target_evidence_status_retained"] == "COMPOSED_WORKING" and card["working_root_meaning_changed"] == "NO", source["target_current_default_phrase_de"])
        check(f"{prefix}_guards_exact", card["surface_prediction_made"] == card["occurrence_prediction_made"] == "NO" and card["guard"] == GUARD and card["source_roundtrip_exact"] == "YES", GUARD)

        card_effects = effects_by_card[source["comparison_card_id"]]
        check(f"{prefix}_effect_count", len(card_effects) == len(added) + len(removed) == int(card["token_effect_checks"]) == int(card["token_effect_checks_passed"]), f"effects={len(card_effects)}")
        expected_effects: list[tuple[str, str, str, bool, bool, str]] = []
        for atom in added:
            duplicate = atom in ACTION_ROOTS and atom in shared
            needle = marker(atom, source["target_register"], expansions, duplicate)
            expected_effects.append(("TARGET_ADD", atom, needle, phrase_has(source["selected_old_clause_de"], needle), phrase_has(source["target_current_default_phrase_de"], needle), source["target_register"]))
        for atom in removed:
            needle = marker(atom, source["support_register"], expansions, False)
            expected_effects.append(("CARRIER_REMOVE", atom, needle, phrase_has(source["selected_old_clause_de"], needle), phrase_has(source["target_current_default_phrase_de"], needle), source["support_register"]))
        effect_exact = len(card_effects) == len(expected_effects)
        for row, expected in zip(card_effects, expected_effects):
            side, atom, needle, source_has, target_has, register = expected
            passed = target_has if side == "TARGET_ADD" else source_has and not target_has
            effect_exact = effect_exact and row["effect_side"] == side and row["atom"] == atom and row["portable_value_de"] == values[atom] and row["realization_register"] == register and row["owner_local_value_de"] == expansions.get((atom, register), values[atom]) and row["phrase_marker_de"] == needle and row["source_phrase_contains_marker"] == ("YES" if source_has else "NO") and row["target_phrase_contains_marker"] == ("YES" if target_has else "NO") and row["effect_check_passed"] == ("YES" if passed else "NO") and row["guard"] == GUARD
            expected_atom_sides[(atom, side)] += 1
        check(f"{prefix}_effects_exact", effect_exact and card["semantic_phrase_delta_consistent"] == "YES", f"expected={expected_effects}")
        check(f"{prefix}_readable_present", source["selected_old_clause_de"] in readable and source["target_current_default_phrase_de"] in readable and expected_operation in readable, source["comparison_card_id"])

    check("global_alignment_totals", (shared_total, added_total, removed_total) == (100, 40, 19), f"{shared_total}/{added_total}/{removed_total}")
    check("all_effect_rows_pass", all(row["effect_check_passed"] == "YES" and row["guard"] == GUARD for row in effects), "59/59")

    operation_by_name = {row["delta_operation"]: row for row in operations}
    for name in OP_ORDER:
        row = operation_by_name[name]
        group = [card for card in cards if card["delta_operation"] == name]
        check(f"operation_{name}", int(row["card_count"]) == expected_operations[name] == len(group) and row["card_ids"] == "|".join(card["semantic_delta_card_id"] for card in group) and row["all_phrase_deltas_consistent"] == "YES" and row["guard"] == GUARD, f"count={len(group)}")

    atom_by_name = {row["atom"]: row for row in atoms}
    for atom, row in atom_by_name.items():
        add_count = expected_atom_sides[(atom, "TARGET_ADD")]
        remove_count = expected_atom_sides[(atom, "CARRIER_REMOVE")]
        check(f"atom_{atom}", row["portable_value_de"] == values[atom] and int(row["target_add_effect_count"]) == add_count and int(row["carrier_remove_effect_count"]) == remove_count and int(row["total_effect_count"]) == add_count + remove_count and row["all_effect_checks_passed"] == "YES" and row["guard"] == GUARD, f"add={add_count},remove={remove_count}")

    register_by_name = {row["target_register"]: row for row in registers}
    for register in REGISTERS:
        row = register_by_name[register]
        group = [card for card in cards if card["target_register"] == register]
        group_effects = [effect for effect in effects if effect["source_comparison_card_id"] in {card["source_comparison_card_id"] for card in group}]
        check(f"register_{register}", int(row["semantic_delta_card_count"]) == expected_registers[register] == len(group) and int(row["token_effect_check_count"]) == int(row["token_effect_checks_passed"]) == len(group_effects) and row["all_target_phrases_retained"] == "YES" and row["guard"] == GUARD, f"cards={len(group)},effects={len(group_effects)}")

    depth_by_name = {row["support_depth"]: row for row in depths}
    for depth, expected_count in (("DIRECT_LOCAL_DELTA", 22), ("CROSS_REGISTER_NORMALIZED_DELTA", 13), ("PAIR_BACKBONE_FRAME_EDIT", 11)):
        row = depth_by_name[depth]
        group = [card for card in cards if card["support_depth"] == depth]
        check(f"depth_{depth}", int(row["card_count"]) == expected_depths[depth] == expected_count == len(group) and int(row["target_added_token_count"]) == sum(len(tokens(card["target_only_tokens"])) for card in group) and int(row["carrier_removed_token_count"]) == sum(len(tokens(card["carrier_only_tokens"])) for card in group) and row["all_phrase_deltas_consistent"] == "YES" and row["guard"] == GUARD, f"count={len(group)}")

    expected_result = {
        "status": STATUS,
        "semantic_delta_cards": 46,
        "exact_partial_extension_cards": 35,
        "direct_local_delta_cards": 22,
        "cross_register_normalized_delta_cards": 13,
        "pair_backbone_frame_edit_cards": 11,
        "pair_carrier_context_replacement_cards": 2,
        "pair_carrier_context_stripping_cards": 9,
        "aligned_shared_tokens": 100,
        "target_added_token_effects": 40,
        "carrier_removed_token_effects": 19,
        "token_effect_checks": 59,
        "token_effect_checks_passed": 59,
        "semantic_phrase_delta_consistent_cards": 46,
        "delta_operation_classes": 14,
        "atom_effect_families": 10,
        "target_added_atom_families": 6,
        "carrier_removed_atom_families": 6,
        "inherited_argument_explicitization_cards": 5,
        "counted_repeat_cards": 5,
        "source_clause_roundtrips_exact": 46,
        "nonempty_target_registers": 4,
        "target_phrase_changes": 0,
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, json.dumps(expected_result, ensure_ascii=False, sort_keys=True))
    check("readable_status_guard_exact", STATUS in readable and GUARD in readable, "status and guard")

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

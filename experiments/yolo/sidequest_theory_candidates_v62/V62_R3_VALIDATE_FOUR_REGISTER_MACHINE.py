#!/usr/bin/env python3
"""Validate the V62 R3 four-register machine and reduced-model audit."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V60 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v60"
V61 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v61"
SOURCE_VALUES = V60 / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv"
SOURCE_STATEMENTS = V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
SOURCE_BOUNDARIES = V61 / "V61_SELECTED_46_LINE_BOUNDARIES.tsv"
FILES = {
    "transitions": HERE / "V62_R3_116_STATE_TRANSITIONS.tsv",
    "inventory": HERE / "V62_R3_REGISTER_INVENTORY.tsv",
    "errors": HERE / "V62_R3_IRREDUCIBLE_ERROR_AUDIT.tsv",
    "models": HERE / "V62_R3_REDUCED_REGISTER_MODELS.tsv",
}
VALIDATION = HERE / "V62_R3_VALIDATION.json"

REGISTERS = ("OWNER", "ACTIVE_ITEM/PREPARATION", "TARGET/STATION", "PREVIOUS_ITEM")
OPERATIONS = {"INTRODUCE", "CARRY", "RESUME", "RESET"}
RECORDS = {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
EXPECTED_ERROR_COUNTS = Counter(
    {
        "TARGET_INTRODUCTION_OVERWRITES_PRIOR_TARGET": 41,
        "PREVIOUS_REFERENT_CLASS_AMBIGUOUS": 19,
        "PREVIOUS_SLOT_OVERWRITTEN": 16,
        "TARGET_RESET_DISCARDS_PRIOR_TARGET": 16,
        "MULTIPLE_TARGETS_ONE_SLOT": 9,
        "OPEN_RECORD_END": 8,
        "TWO_INPUTS_ORDER_AMBIGUOUS": 6,
        "INFERRED_PREVIOUS_IDENTITY": 4,
        "TARGET_INFERRED_WITHOUT_EXACT_OR_LOCAL_CUE": 1,
        "REPEATED_ACTIVE_TRIGGER": 1,
        "UNRESOLVED_BOUNDARY": 1,
    }
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_state(text: str) -> dict[str, str]:
    state = {}
    for part in text.split(";"):
        key, value = part.split("=", 1)
        state[key] = value
    return state


def parse_set(text: str) -> set[str]:
    return set() if text == "NONE" else set(text.split(" | "))


def mnemonic_tokens(skeleton: str) -> list[str]:
    return re.findall(r"[A-ZÄÖÜ]+\?", skeleton)


def main() -> None:
    values = read_tsv(SOURCE_VALUES)
    statements = read_tsv(SOURCE_STATEMENTS)
    boundaries = read_tsv(SOURCE_BOUNDARIES)
    transitions = read_tsv(FILES["transitions"])
    inventory = read_tsv(FILES["inventory"])
    errors = read_tsv(FILES["errors"])
    models = read_tsv(FILES["models"])
    checks: dict[str, bool] = {}

    checks["source_counts_11_116_46"] = (len(values), len(statements), len(boundaries)) == (11, 116, 46)
    checks["output_counts_116_4_122_5"] = (len(transitions), len(inventory), len(errors), len(models)) == (116, 4, 122, 5)
    checks["scope_exact_11_records_7_pages"] = {row["record_unit_id"] for row in transitions} == RECORDS and {row["page"] for row in transitions} == PAGES
    source_by_id = {row["statement_id"]: row for row in statements}
    checks["statement_identity_and_order_preserved"] = [row["statement_id"] for row in transitions] == [row["statement_id"] for row in statements]
    checks["all_135_fields_and_381_events_in_selected_statements"] = (
        sum(len(row["constituent_fields"].split("|")) for row in transitions) == 135
        and sum(int(row["event_count"]) for row in statements) == 381
    )
    checks["complete_creative_reading_preserved"] = all(
        row["complete_creative_reading"] == source_by_id[row["statement_id"]]["concrete_workshop_reading"]
        and row["strongest_source_alternative"] == source_by_id[row["statement_id"]]["strongest_alternative"]
        for row in transitions
    )

    allowed_mnemonics = {row["selected_short_mnemonic"] for row in values}
    expected_mnemonic_counts = Counter({row["selected_short_mnemonic"]: int(row["occurrences"]) for row in values})
    observed_mnemonic_counts: Counter[str] = Counter()
    mnemonic_match = True
    for row in transitions:
        expected = mnemonic_tokens(source_by_id[row["statement_id"]]["selected_short_card_skeleton"])
        actual = [] if row["selected_mnemonic_triggers"] == "NONE" else row["selected_mnemonic_triggers"].split(" | ")
        mnemonic_match &= expected == actual and set(actual) <= allowed_mnemonics
        observed_mnemonic_counts.update(actual)
    checks["only_v60_exact_selected_mnemonics_used"] = mnemonic_match and observed_mnemonic_counts == expected_mnemonic_counts
    checks["exact_binding_contract_preserved"] = all(
        row["binding"] == "EXACT_JOINT_TUPLE_ID_ONLY" for row in values
    ) and all("NO_STRING_OR_COMPONENT_INHERITANCE" in row["card_binding_contract"] for row in transitions)

    state_sequence_ok = True
    record_first_seen: set[str] = set()
    last_post_by_record: dict[str, str] = {}
    owner_by_record: dict[str, str] = {}
    anonymous_ids_ok = True
    operations_ok = True
    for row in transitions:
        record = row["record_unit_id"]
        pre = parse_state(row["pre_state"])
        post = parse_state(row["post_state"])
        state_sequence_ok &= set(pre) == set(REGISTERS) and set(post) == set(REGISTERS)
        if record not in record_first_seen:
            state_sequence_ok &= all(value == "UNSET" for value in pre.values()) and row["entry_boundary_class"] == "RECORD_START"
            record_first_seen.add(record)
            owner_by_record[record] = post["OWNER"]
        else:
            state_sequence_ok &= row["pre_state"] == last_post_by_record[record]
            state_sequence_ok &= post["OWNER"] == owner_by_record[record]
        last_post_by_record[record] = row["post_state"]
        for register, value in post.items():
            if value == "UNSET":
                continue
            anonymous_ids_ok &= value.startswith(record + ":")
            if register == "OWNER":
                anonymous_ids_ok &= bool(re.fullmatch(re.escape(record) + r":O\d{2}", value))
            elif register in {"ACTIVE_ITEM/PREPARATION", "PREVIOUS_ITEM"}:
                anonymous_ids_ok &= bool(re.fullmatch(re.escape(record) + r":I\d{3}", value))
            else:
                anonymous_ids_ok &= bool(re.fullmatch(re.escape(record) + r":T\d{3}", value))
        operations_ok &= {
            row["owner_operation"],
            row["active_item_preparation_operation"],
            row["target_station_operation"],
            row["previous_item_operation"],
        } <= OPERATIONS
    checks["pre_post_state_chain_and_record_reset"] = state_sequence_ok and len(record_first_seen) == 11
    checks["anonymous_ids_strictly_record_local"] = anonymous_ids_ok
    checks["only_introduce_carry_resume_reset_operations"] = operations_ok
    checks["all_transition_contract_columns_complete"] = all(
        all(row[key].strip() for key in ("pre_state", "observed_triggers", "inferred_missing_slots", "owner_operation", "active_item_preparation_operation", "target_station_operation", "previous_item_operation", "operation_trace", "post_state", "backward_reconstructability", "complete_creative_reading"))
        for row in transitions
    )

    checks["transition_log_always_backward_reconstructable"] = all(row["backward_reconstructability"].startswith("TRANSITION_LOG=YES;") for row in transitions)
    post_only_counts = Counter(row["backward_reconstructable_from_post_state_only"] for row in transitions)
    checks["post_state_only_backward_counts_47_69"] = post_only_counts == Counter({"YES": 47, "NO": 69})
    checks["eight_open_record_ends_one_unresolved_boundary"] = (
        sum("OPEN_RECORD_END" in row["irreducible_ambiguity_codes"] for row in transitions) == 8
        and sum("UNRESOLVED_BOUNDARY" in row["irreducible_ambiguity_codes"] for row in transitions) == 1
    )

    transition_issue_pairs = {
        (row["statement_id"], code)
        for row in transitions
        for code in ([] if row["irreducible_ambiguity_codes"] == "NONE" else row["irreducible_ambiguity_codes"].split(" | "))
    }
    error_pairs = {(row["statement_id"], row["error_code"]) for row in errors}
    checks["error_audit_exactly_covers_transition_issues"] = transition_issue_pairs == error_pairs and len(error_pairs) == len(errors)
    error_counts = Counter(row["error_code"] for row in errors)
    checks["error_type_counts_frozen"] = error_counts == EXPECTED_ERROR_COUNTS
    checks["irreducible_and_recoverable_flags_complete"] = all(
        row["irreducible_with_four_registers"] in {"YES", "NO"}
        and row["impacts_post_state_backward_reconstruction"] in {"YES", "NO"}
        for row in errors
    ) and Counter(row["irreducible_with_four_registers"] for row in errors) == Counter({"NO": 73, "YES": 49})

    demand_by_statement = {row["statement_id"]: parse_set(row["silent_register_demand"]) for row in transitions}
    checks["silent_demands_use_only_four_registers"] = all(demand <= set(REGISTERS) for demand in demand_by_statement.values())
    inventory_by_register = {row["register"]: row for row in inventory}
    demand_counts = Counter(register for demand in demand_by_statement.values() for register in demand)
    checks["register_inventory_exact_and_demand_counts_match"] = set(inventory_by_register) == set(REGISTERS) and all(
        int(inventory_by_register[register]["silent_demand_statement_count"]) == demand_counts[register]
        for register in REGISTERS
    )
    checks["all_four_registers_have_necessity_witnesses"] = all(demand_counts[register] > 0 for register in REGISTERS)
    checks["silent_demand_counts_105_83_9_19"] = demand_counts == Counter({"OWNER": 105, "ACTIVE_ITEM/PREPARATION": 83, "PREVIOUS_ITEM": 19, "TARGET/STATION": 9})

    model_by_size = {int(row["register_count"]): row for row in models}
    checks["model_rows_exact_sizes_0_to_4"] = set(model_by_size) == {0, 1, 2, 3, 4}
    model_scores_ok = True
    strongest_ok = True
    for size, row in model_by_size.items():
        kept = parse_set(row["kept_registers"])
        covered = sum(demand <= kept for demand in demand_by_statement.values())
        missing = sum(len(demand - kept) for demand in demand_by_statement.values())
        model_scores_ok &= covered == int(row["statements_fully_generable"]) and 116 - covered == int(row["statements_failing"]) and missing == int(row["missing_silent_slot_instances"])
        all_scores = []
        for subset in itertools.combinations(REGISTERS, size):
            subset_set = set(subset)
            all_scores.append((sum(demand <= subset_set for demand in demand_by_statement.values()), -sum(len(demand - subset_set) for demand in demand_by_statement.values())))
        strongest_ok &= (covered, -missing) == max(all_scores)
    checks["reduced_model_scores_recomputed"] = model_scores_ok
    checks["reported_0_to_4_models_are_exhaustive_winners"] = strongest_ok
    checks["model_coverage_9_27_88_107_116"] = {size: int(row["statements_fully_generable"]) for size, row in model_by_size.items()} == {0: 9, 1: 27, 2: 88, 3: 107, 4: 116}
    checks["strongest_reduced_subsets_are_nested_owner_active_previous"] = (
        model_by_size[1]["kept_registers"] == "OWNER"
        and model_by_size[2]["kept_registers"] == "OWNER | ACTIVE_ITEM/PREPARATION"
        and model_by_size[3]["kept_registers"] == "OWNER | ACTIVE_ITEM/PREPARATION | PREVIOUS_ITEM"
    )
    checks["only_four_register_model_generates_all"] = all(int(model_by_size[size]["statements_failing"]) > 0 for size in (0, 1, 2, 3)) and int(model_by_size[4]["statements_failing"]) == 0

    boundary_ids = {row["boundary_id"] for row in boundaries}
    mentioned_boundary_ids = {
        part.split(":")[1]
        for row in transitions
        for part in ([] if row["source_boundary_triggers"] == "NONE" else row["source_boundary_triggers"].split(" | "))
    }
    checks["all_46_selected_boundaries_used"] = mentioned_boundary_ids == boundary_ids
    checks["no_page_host_schema"] = all(
        "page_host" not in key.casefold()
        for table in (transitions, inventory, errors, models)
        for key in table[0]
    )

    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "schema": "V62_R3_DETERMINISTIC_FOUR_REGISTER_MACHINE_V1",
        "status": "PASS" if not failed else "FAIL",
        "counts": {
            "selected_exact_card_values": len(values),
            "selected_source_statements": len(statements),
            "selected_line_boundaries": len(boundaries),
            "state_transitions": len(transitions),
            "registers": len(inventory),
            "error_audit_rows": len(errors),
            "irreducible_error_rows": sum(row["irreducible_with_four_registers"] == "YES" for row in errors),
            "post_state_only_backward_yes": post_only_counts["YES"],
            "post_state_only_backward_no": post_only_counts["NO"],
        },
        "silent_demand_counts": dict(demand_counts),
        "reduced_model_coverage": {str(size): int(row["statements_fully_generable"]) for size, row in sorted(model_by_size.items())},
        "error_type_counts": dict(error_counts),
        "checks": checks,
        "failed_checks": failed,
        "source_sha256": {
            "V60_selected_values": sha256(SOURCE_VALUES),
            "V61_selected_statements": sha256(SOURCE_STATEMENTS),
            "V61_selected_boundaries": sha256(SOURCE_BOUNDARIES),
        },
        "output_sha256": {name: sha256(path) for name, path in FILES.items()},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("FAIL: " + ", ".join(failed))
    print("PASS validation")
    print(json.dumps(result["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

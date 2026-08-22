#!/usr/bin/env python3
"""Validate the V61 R3 transaction/clause map against its frozen sources."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V60 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v60"
V59 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v59"

SOURCE_DECK = V60 / "V60_SELECTED_173_CARD_DICTIONARY.tsv"
SOURCE_EVENTS = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"
SOURCE_FIELDS = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
SOURCE_RECORDS = V59 / "V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv"

FILES = {
    "boundaries": HERE / "V61_R3_PHYSICAL_LOCUS_BOUNDARIES.tsv",
    "statements": HERE / "V61_R3_98_TRANSACTION_STATEMENTS.tsv",
    "field_assignment": HERE / "V61_R3_135_FIELD_ASSIGNMENT.tsv",
}
VALIDATION = HERE / "V61_R3_VALIDATION.json"
PROSE_RECORDS = {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    answer: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            answer.append(value)
    return answer


def main() -> None:
    deck = read_tsv(SOURCE_DECK)
    events = read_tsv(SOURCE_EVENTS)
    fields = read_tsv(SOURCE_FIELDS)
    records = read_tsv(SOURCE_RECORDS)
    boundaries = read_tsv(FILES["boundaries"])
    statements = read_tsv(FILES["statements"])
    assignment = read_tsv(FILES["field_assignment"])

    checks: dict[str, bool] = {}
    checks["source_counts_173_381_135_14"] = (len(deck), len(events), len(fields), len(records)) == (173, 381, 135, 14)
    checks["output_counts_46_98_135"] = (len(boundaries), len(statements), len(assignment)) == (46, 98, 135)
    checks["scope_exactly_11_prose_records_7_pages"] = (
        {row["record_unit_id"] for row in assignment} == PROSE_RECORDS
        and {row["page"] for row in assignment} == PROSE_PAGES
        and not any(row["record_unit_id"].startswith("A") for row in assignment + statements + boundaries)
    )
    checks["field_assignment_unique_complete_ordered"] = (
        [row["field_id"] for row in assignment] == [row["field_id"] for row in fields]
        and len({row["field_id"] for row in assignment}) == 135
    )
    source_field_by_id = {row["field_id"]: row for row in fields}
    checks["field_source_identity_preserved"] = all(
        all(
            row[new_key] == source_field_by_id[row["field_id"]][old_key]
            for new_key, old_key in (
                ("page", "page"),
                ("record_unit_id", "record_unit_id"),
                ("locus", "locus"),
                ("field_ordinal_in_locus", "field_ordinal_in_locus"),
                ("field_ordinal_in_record", "field_ordinal_in_record"),
                ("field_closure_status", "closure_status"),
                ("event_count", "event_count"),
                ("source_surface_sequence_display_only", "surface_sequence"),
                ("full_local_field_reading", "LOCAL_IATROMEDICAL_EXPANSION"),
            )
        )
        for row in assignment
    )
    checks["all_381_events_covered_once_by_fields"] = sum(int(row["event_count"]) for row in assignment) == 381

    assignment_by_field = {row["field_id"]: row for row in assignment}
    statement_by_id = {row["source_statement_id"]: row for row in statements}
    checks["statement_ids_unique"] = len(statement_by_id) == 98
    checks["every_statement_field_list_matches_assignment"] = all(
        all(assignment_by_field[field_id]["source_statement_id"] == row["source_statement_id"] for field_id in row["field_ids"].split("|"))
        and int(row["field_count"]) == len(row["field_ids"].split("|"))
        for row in statements
    )
    checks["statements_partition_135_fields"] = sorted(
        field_id for row in statements for field_id in row["field_ids"].split("|")
    ) == sorted(source_field_by_id)

    closure_shape_ok = True
    contiguity_ok = True
    for statement in statements:
        member_ids = statement["field_ids"].split("|")
        members = [source_field_by_id[field_id] for field_id in member_ids]
        closure_shape_ok &= all(field["closure_status"] == "OPEN" for field in members[:-1])
        expected_status = "COMMITTED" if members[-1]["closure_status"] == "TERMINAL" else "OPEN_DEFERRED_AT_RECORD_END"
        closure_shape_ok &= statement["transaction_status"] == expected_status
        record_fields = [row for row in fields if row["record_unit_id"] == statement["record_unit_id"]]
        ordinals = [int(field["field_ordinal_in_record"]) for field in members]
        contiguity_ok &= ordinals == list(range(ordinals[0], ordinals[0] + len(ordinals)))
        if expected_status == "OPEN_DEFERRED_AT_RECORD_END":
            closure_shape_ok &= member_ids[-1] == record_fields[-1]["field_id"]
    checks["terminal_commits_and_open_carries"] = closure_shape_ok
    checks["statement_fields_contiguous_within_record"] = contiguity_ok

    status_counts = Counter(row["transaction_status"] for row in statements)
    checks["statement_status_counts_90_committed_8_open"] = status_counts == Counter({"COMMITTED": 90, "OPEN_DEFERRED_AT_RECORD_END": 8})
    field_count_shape = Counter(int(row["field_count"]) for row in statements)
    checks["statement_field_shape_67_26_4_1"] = field_count_shape == Counter({1: 67, 2: 26, 3: 4, 4: 1})
    checks["cross_locus_statement_count_31"] = sum(row["crosses_physical_locus"] == "YES" for row in statements) == 31
    checks["transaction_columns_complete"] = all(
        all(row[key].strip() for key in ("inputs", "parameter_slots", "operation_slots", "state_slots", "relation_slots", "output", "carry_in", "carry_out", "full_executable_reading", "strongest_rival_segmentation"))
        for row in statements
    )

    fields_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for field in fields:
        fields_by_record[field["record_unit_id"]].append(field)
    expected_boundary_pairs: list[tuple[str, str, str, str, str]] = []
    for record, members in fields_by_record.items():
        loci = ordered_unique([field["locus"] for field in members])
        by_locus = {locus: [field for field in members if field["locus"] == locus] for locus in loci}
        for left_locus, right_locus in zip(loci, loci[1:]):
            left = by_locus[left_locus][-1]
            right = by_locus[right_locus][0]
            expected_boundary_pairs.append((record, left_locus, right_locus, left["field_id"], right["field_id"]))
    actual_boundary_pairs = [
        (row["record_unit_id"], row["left_locus"], row["right_locus"], row["left_last_field_id"], row["right_first_field_id"])
        for row in boundaries
    ]
    checks["all_46_inner_locus_boundaries_exactly_once"] = actual_boundary_pairs == expected_boundary_pairs and len(set(actual_boundary_pairs)) == 46
    expected_boundary_logic = all(
        (
            row["boundary_classification"] == "CONTINUE_OPEN_TRANSACTION"
            and row["same_source_statement"] == "YES"
            and row["left_source_statement_id"] == row["right_source_statement_id"]
        )
        if row["left_field_closure_status"] == "OPEN"
        else (
            row["boundary_classification"] == "RESET_AFTER_COMMIT"
            and row["same_source_statement"] == "NO"
            and row["left_source_statement_id"] != row["right_source_statement_id"]
        )
        for row in boundaries
    )
    checks["boundary_decision_is_exactly_closure_driven"] = expected_boundary_logic
    boundary_counts = Counter(row["boundary_classification"] for row in boundaries)
    checks["boundary_counts_37_continue_9_reset"] = boundary_counts == Counter({"CONTINUE_OPEN_TRANSACTION": 37, "RESET_AFTER_COMMIT": 9})
    checks["physical_line_not_sentence_demonstrated"] = boundary_counts["CONTINUE_OPEN_TRANSACTION"] > 0 and boundary_counts["RESET_AFTER_COMMIT"] > 0

    special = [row for row in boundaries if row["focus_status"] == "PRIMARY_F82R_3_TO_4"]
    checks["f82r_3_to_4_is_f050_f051_continuation"] = (
        len(special) == 1
        and special[0]["left_last_field_id"] == "F050"
        and special[0]["right_first_field_id"] == "F051"
        and special[0]["boundary_classification"] == "CONTINUE_OPEN_TRANSACTION"
        and special[0]["same_source_statement"] == "YES"
        and special[0]["repeated_exact_joint_tuple_across_boundary"] == "YES"
        and "RESUMPTIVE_DUPLICATE_HEADER_SPLIT" in special[0]["strongest_rival_segmentation"]
    )
    f83 = [row for row in boundaries if row["page"] == "f83r"]
    checks["f83r_mixed_boundary_pattern_21_14_7"] = (
        len(f83) == 21
        and Counter(row["boundary_classification"] for row in f83)
        == Counter({"CONTINUE_OPEN_TRANSACTION": 14, "RESET_AFTER_COMMIT": 7})
    )

    selected_by_id = {row["joint_tuple_id"]: row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for row in deck}
    selected_values = {value for value in selected_by_id.values() if value != "UNKNOWN"}
    checks["selected_deck_has_exactly_11_mnemonics"] = len(selected_values) == 11 and sum(value != "UNKNOWN" for value in selected_by_id.values()) == 11
    event_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        event_by_field[event["field_id"]].append(event)
    expected_assignment_slots = {}
    for field_id, members in event_by_field.items():
        slots = [
            f"E{event['event_serial']}:{event['joint_tuple_id']}:{event['ATOMIC_OR_WHOLE_CARD_MNEMONIC']}"
            for event in members
            if event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
        ]
        expected_assignment_slots[field_id] = " | ".join(slots) if slots else "NONE"
    checks["field_mnemonic_slots_are_exact_v60_bindings"] = all(
        row["selected_exact_mnemonic_slots"] == expected_assignment_slots[row["field_id"]] for row in assignment
    )
    checks["binding_contract_forbids_component_inheritance"] = all(
        "EXACT_JOINT_TUPLE_ID_ONLY" in row["binding_contract"] and "CARD_MEANING" in row["binding_contract"]
        for row in assignment + statements
    )
    checks["no_page_host_schema"] = all(
        "page_host" not in key.lower()
        for table in (boundaries, statements, assignment)
        for key in table[0]
    )
    checks["all_statements_publish_rival_segmentation"] = all(row["strongest_rival_segmentation"].strip() for row in statements)
    checks["all_boundaries_publish_rival_segmentation"] = all(row["strongest_rival_segmentation"].strip() for row in boundaries)
    record_context = {row["unit_id"]: row for row in records if row["unit_id"] in PROSE_RECORDS}
    checks["record_contexts_preserved_for_all_11"] = all(
        row["record_default_context"] == record_context[row["record_unit_id"]]["LOCAL_IATROMEDICAL_EXPANSION"]
        and row["record_nonmedical_rival_context"] == record_context[row["record_unit_id"]]["NONMEDICAL_RIVAL"]
        for row in statements
    )

    failed = [name for name, passed in checks.items() if not passed]
    per_record = {}
    for record in sorted(PROSE_RECORDS, key=lambda item: (item[0], int(item[1:]))):
        record_statements = [row for row in statements if row["record_unit_id"] == record]
        record_boundaries = [row for row in boundaries if row["record_unit_id"] == record]
        per_record[record] = {
            "fields": sum(row["record_unit_id"] == record for row in assignment),
            "statements": len(record_statements),
            "committed": sum(row["transaction_status"] == "COMMITTED" for row in record_statements),
            "open_deferred": sum(row["transaction_status"] == "OPEN_DEFERRED_AT_RECORD_END" for row in record_statements),
            "locus_boundaries": len(record_boundaries),
            "continuations": sum(row["boundary_classification"] == "CONTINUE_OPEN_TRANSACTION" for row in record_boundaries),
            "resets": sum(row["boundary_classification"] == "RESET_AFTER_COMMIT" for row in record_boundaries),
        }
    result = {
        "schema": "V61_R3_TRANSACTION_CLAUSE_MAP_V1",
        "status": "PASS" if not failed else "FAIL",
        "counts": {
            "prose_records": len(PROSE_RECORDS),
            "prose_pages": len(PROSE_PAGES),
            "source_events": len(events),
            "source_fields": len(fields),
            "source_statements": len(statements),
            "committed_statements": status_counts["COMMITTED"],
            "open_deferred_statements": status_counts["OPEN_DEFERRED_AT_RECORD_END"],
            "cross_locus_statements": sum(row["crosses_physical_locus"] == "YES" for row in statements),
            "inner_locus_boundaries": len(boundaries),
            "continued_locus_boundaries": boundary_counts["CONTINUE_OPEN_TRANSACTION"],
            "reset_locus_boundaries": boundary_counts["RESET_AFTER_COMMIT"],
            "f83r_boundaries": len(f83),
        },
        "per_record": per_record,
        "checks": checks,
        "failed_checks": failed,
        "source_sha256": {
            "V60_selected_deck": sha256(SOURCE_DECK),
            "V60_selected_events": sha256(SOURCE_EVENTS),
            "V59_fields": sha256(SOURCE_FIELDS),
            "V59_record_texts": sha256(SOURCE_RECORDS),
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

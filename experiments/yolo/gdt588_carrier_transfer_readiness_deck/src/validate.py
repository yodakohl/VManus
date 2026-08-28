#!/usr/bin/env python3
"""Validate GDT588 mobility, intake gates, packets, and reader repairs."""

from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from transfer_lib import (
    G583_RULES,
    INPUTS,
    MULTIPLICITY_REPAIRS,
    OUTPUTS,
    PACKET_CARD_DESCRIPTIONS,
    REGISTER_FALLBACK_FORMS,
    ROOT_ORDER,
    STATUS,
    TIER_CELL,
    TIER_EXACT,
    TIER_PRIVATE,
    TIER_REGISTER,
    cell_key,
    classify,
    exact_key,
    future_host_reading,
    mobility_maps,
    read_tsv,
    register_root_key,
    root_multiset,
    sha256,
)


def main() -> int:
    source = {name: read_tsv(path) for name, path in INPUTS.items() if path.suffix == ".tsv"}
    rows = {
        name: read_tsv(path)
        for name, path in OUTPUTS.items()
        if path.suffix == ".tsv" and name != "validation"
    }
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))
    contract = json.loads(OUTPUTS["contract"].read_text(encoding="utf-8"))
    book = OUTPUTS["book"].read_text(encoding="utf-8")
    deck = OUTPUTS["deck"].read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({
            "check_ordinal": len(checks) + 1,
            "check_id": check_id,
            "status": "PASS" if condition else "FAIL",
            "detail": detail,
        })

    assignments_587 = source["assignments_587"]
    actions = source["actions_584"]
    mobility = rows["assignments"]
    selections = rows["selections"]
    cells = rows["cells"]
    gates = rows["rule_gate"]
    matrix = rows["future_cells"]
    fallbacks = rows["fallbacks"]
    packet_cards = rows["packet_cards"]
    special_hosts = rows["special_hosts"]
    special_shapes = rows["special_shapes"]
    repairs = rows["repairs"]
    pages = rows["pages"]
    statements = rows["statements"]
    local_cards = rows["local_cards"]

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check("INPUT_HASHES", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, "six fixed inputs")
    check("CONTRACT_NO_NEW_PAGE", contract["new_pages"] == "NONE" and contract["surface_parser"] == "NONE", "no pages or surface parser")

    source_ids = [row["carrier_slot_id"] for row in assignments_587]
    mobility_ids = [row["carrier_slot_id"] for row in mobility]
    check("ASSIGNMENT_COUNT", len(mobility) == 1243, str(len(mobility)))
    check("ASSIGNMENT_ORDER", mobility_ids == source_ids, "1243 ordered carrier slots")
    check("UNIQUE_ASSIGNMENTS", len(set(mobility_ids)) == 1243, str(len(set(mobility_ids))))
    check("ASSIGNMENT_FIELDS_PROJECT", all(
        (old["physical_page"], old["register"], old["gdt584_rule_id"], old["carrier_root"], old["gdt587_lemma_de"])
        == (new["physical_page"], new["register"], new["gdt584_rule_id"], new["carrier_root"], new["gdt587_lemma_de"])
        for old, new in zip(assignments_587, mobility)
    ), "page/register/rule/root/lemma exact")

    maps = mobility_maps(assignments_587)
    layer_maps = mobility_maps(assignments_587, same_layer=True)
    expected_tiers = [classify(row, maps)[0] for row in assignments_587]
    expected_layer_tiers = [classify(row, layer_maps)[0] for row in assignments_587]
    check("TIER_RECOMPUTE", [row["transfer_tier"] for row in mobility] == expected_tiers, "all four-way tiers")
    check("SAME_LAYER_TIER_RECOMPUTE", [row["same_layer_transfer_tier"] for row in mobility] == expected_layer_tiers, "all same-layer tiers")
    tier_counts = Counter(expected_tiers)
    layer_counts = Counter(expected_layer_tiers)
    check("TIER_COUNTS", tier_counts == {TIER_EXACT: 970, TIER_CELL: 146, TIER_REGISTER: 121, TIER_PRIVATE: 6}, str(tier_counts))
    check("SAME_LAYER_TIER_COUNTS", layer_counts == {TIER_EXACT: 942, TIER_CELL: 152, TIER_REGISTER: 135, TIER_PRIVATE: 14}, str(layer_counts))
    check("NO_SELF_PAGE_SUPPORT", all(row["physical_page"] not in row["tier_supporting_pages"].split("|") for row in mobility), "all 1243")
    check("EXACT_SUPPORT_NONEMPTY", all((row["strict_exact_foreign_pages"] != "NONE") == (row["transfer_tier"] == TIER_EXACT) for row in mobility), "970 exact rows")
    cell_rows: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in assignments_587:
        cell_rows[cell_key(row)].append(row)
    same_cell_lemma_ok = all(
        any(
            candidate["physical_page"] != row["physical_page"]
            and candidate["gdt587_lemma_de"] == row["gdt587_lemma_de"]
            for candidate in cell_rows[cell_key(row)]
        )
        for row in assignments_587
        if expected_tiers[int(row["assignment_ordinal"]) - 1] == TIER_CELL
    )
    check("SAME_CELL_RETAINS_LEMMA", same_cell_lemma_ok, "146/146")
    private_rows = [row for row, tier in zip(assignments_587, expected_tiers) if tier == TIER_PRIVATE]
    check("PRIVATE_SOURCE_AIN_ONLY", len(private_rows) == 6 and {(row["register"], row["carrier_root"]) for row in private_rows} == {("SOURCE_SECTION_T", "AIN")}, "six source AIN")

    grouped_selections: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in assignments_587:
        grouped_selections[exact_key(row)].append(row)
    check("SELECTION_SIGNATURE_COUNT", len(selections) == len(grouped_selections) == 268, str(len(selections)))
    check("SELECTION_SLOT_TOTAL", sum(int(row["assignment_count"]) for row in selections) == 1243, str(sum(int(row["assignment_count"]) for row in selections)))
    check("MOBILE_SELECTION_TYPES", sum(int(row["page_count"]) > 1 for row in selections) == 103, "103 multi-page / 165 singleton")
    strongest = max(selections, key=lambda row: (int(row["page_count"]), int(row["assignment_count"])))
    check("STRONGEST_SELECTION", strongest["register"] == "HERBAL" and strongest["gdt584_rule_id"] == "T_PHYSICAL_BROAD" and strongest["carrier_root"] == "Y" and int(strongest["page_count"]) == 11, f"{strongest['gdt584_rule_id']} {strongest['page_count']} pages")

    source_cell_set = {cell_key(row) for row in assignments_587}
    output_cell_set = {(row["register"], row["gdt584_rule_id"], row["carrier_root"]) for row in cells}
    check("CELL_COUNT", len(cells) == 136, str(len(cells)))
    check("CELL_SET", output_cell_set == source_cell_set, "136 exact observed cells")
    check("CELL_SLOT_TOTAL", sum(int(row["assignment_count"]) for row in cells) == 1243, str(sum(int(row["assignment_count"]) for row in cells)))
    cell_profiles = Counter(row["cell_mobility_profile"] for row in cells)
    check("CELL_PROFILES", cell_profiles == {
        "EVERY_ASSIGNMENT_EXACT_OTHER_PAGE": 25,
        "PARTIAL_EXACT_OTHER_PAGE": 48,
        "CROSS_PAGE_CELL_DIFFERENT_SIGNATURES": 10,
        "SINGLE_PAGE_CELL_REGISTER_ROOT_FALLBACK": 51,
        "TRULY_PAGE_PRIVATE_CELL": 2,
    }, str(cell_profiles))
    private_cells = [row for row in cells if row["cell_mobility_profile"] == "TRULY_PAGE_PRIVATE_CELL"]
    check("PRIVATE_CELLS", {(row["register"], row["gdt584_rule_id"], row["carrier_root"]) for row in private_cells} == {
        ("SOURCE_SECTION_T", "SH_SOURCE_REST", "AIN"),
        ("SOURCE_SECTION_T", "T_SOURCE_FIX", "AIN"),
    }, "two source AIN cells")

    gate_counts = Counter(row["gate_class"] for row in gates)
    check("RULE_GATE_COUNT", len(gates) == 38, str(len(gates)))
    check("RULE_GATE_CLASSES", gate_counts == {"AUTO_CONTEXT": 27, "SOURCE_ID_BOUND": 2, "MANUAL_GDT584_OVERRIDE": 9}, str(gate_counts))
    source_bound = {row["rule_id"] for row in gates if row["gate_class"] == "SOURCE_ID_BOUND"}
    check("SOURCE_BOUND_RULES", source_bound == {"SH_CH_BRIDGE_HOLD", "S_BIO_CHD_CARRIER_SELECT"}, str(source_bound))
    known_g583 = {rule.rule_id for rule in G583_RULES.RULES}
    manual_expected = {
        row["gdt584_rule_id"] for row in actions
        if row["gdt584_rule_id"] not in known_g583
        and any(a["gdt584_rule_id"] == row["gdt584_rule_id"] for a in assignments_587)
    }
    manual_output = {row["rule_id"] for row in gates if row["gate_class"] == "MANUAL_GDT584_OVERRIDE"}
    check("MANUAL_GATE_SET", manual_output == manual_expected, f"{len(manual_output)} carrier-active overrides")

    check("FALLBACK_COUNT", len(fallbacks) == 20, str(len(fallbacks)))
    fallback_decisions = Counter(row["decision"] for row in fallbacks)
    check("FALLBACK_PROFILE", fallback_decisions == {"REGISTER_INVARIANT": 10, "KEEP_BROAD": 10}, str(fallback_decisions))
    check("FALLBACK_KEYS", {(row["register"], row["carrier_root"]) for row in fallbacks} == set(REGISTER_FALLBACK_FORMS), "five registers × four roots")
    check("FALLBACK_FORMS", all(
        row["decision"] == REGISTER_FALLBACK_FORMS[(row["register"], row["carrier_root"])]["decision"]
        and row["lemma_de"] == REGISTER_FALLBACK_FORMS[(row["register"], row["carrier_root"])]["lemma"]
        for row in fallbacks
    ), "20 declared forms")

    check("FUTURE_MATRIX_COUNT", len(matrix) == 220, str(len(matrix)))
    matrix_counts = Counter(row["matrix_state"] for row in matrix)
    check("FUTURE_MATRIX_PROFILE", matrix_counts == {"OBSERVED_CELL": 111, "REGISTER_INVARIANT": 53, "KEEP_BROAD": 56}, str(matrix_counts))
    auto_pairs = {
        (register, rule.rule_id)
        for rule in G583_RULES.RULES if not rule.source_ids
        for register in rule.registers
    }
    check("AUTO_PAIR_COUNT", len(auto_pairs) == 55, str(len(auto_pairs)))
    check("MATRIX_KEYS", {(row["register"], row["automatic_gdt583_rule_id"], row["carrier_root"]) for row in matrix} == {
        (register, rule, root) for register, rule in auto_pairs for root in ROOT_ORDER
    }, "55 × four roots")
    matrix_by_register = defaultdict(Counter)
    for row in matrix:
        matrix_by_register[row["register"]][row["matrix_state"]] += 1
    check("MATRIX_REGISTER_PROFILES", dict(matrix_by_register) == {
        "SOURCE_SECTION_T": Counter({"OBSERVED_CELL": 12, "REGISTER_INVARIANT": 7, "KEEP_BROAD": 5}),
        "HERBAL": Counter({"OBSERVED_CELL": 35, "REGISTER_INVARIANT": 12, "KEEP_BROAD": 17}),
        "CELESTIAL": Counter({"OBSERVED_CELL": 14, "REGISTER_INVARIANT": 14}),
        "BIOLOGICAL": Counter({"OBSERVED_CELL": 29, "KEEP_BROAD": 11}),
        "PHARMA": Counter({"OBSERVED_CELL": 21, "REGISTER_INVARIANT": 20, "KEEP_BROAD": 23}),
    }, str(dict(matrix_by_register)))

    check("PACKET_CARD_COUNT", len(packet_cards) == len(PACKET_CARD_DESCRIPTIONS) == 8, str(len(packet_cards)))
    check("PACKET_CARD_SET", {row["gdt587_packet_rule_id"] for row in packet_cards} == set(PACKET_CARD_DESCRIPTIONS), "eight bounded packets")
    packet_slot_profile = {row["gdt587_packet_rule_id"]: int(row["old_carrier_slot_count"]) for row in packet_cards}
    check("PACKET_SLOT_PROFILE", packet_slot_profile == {
        "BIOLOGICAL_BATH_FILL": 18,
        "BIOLOGICAL_BODY_PART": 9,
        "BIOLOGICAL_FLOW_PACKET": 19,
        "CELESTIAL_POSITION_SEGMENT_VALUE": 18,
        "HP_EXTRACT_OF_MATERIAL": 47,
        "HP_MEASURE_FOR_MATERIAL": 3,
        "SOURCE_LIQUID_FROM_MATERIAL": 2,
        "SOURCE_PART_OF_MATERIAL": 5,
    }, str(packet_slot_profile))
    check("AUTO_PACKET_SLOTS", sum(int(row["auto_rule_carrier_slot_count"]) for row in packet_cards) == 118, str(sum(int(row["auto_rule_carrier_slot_count"]) for row in packet_cards)))

    by_governor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments_587:
        if row["gdt587_packet_rule_id"] != "DEFAULT_GDT584_OBJECT_COMPOSITION":
            by_governor[row["primary_governor_key"]].append(row)
    for members in by_governor.values():
        members.sort(key=lambda row: int(row["assignment_ordinal"]))
    output_host_by_key = {row["primary_governor_key"]: row for row in special_hosts}
    check("SPECIAL_HOST_COUNT", len(special_hosts) == len(by_governor) == 74, str(len(special_hosts)))
    check("SPECIAL_CARRIER_TOTAL", sum(int(row["written_carrier_slot_count"]) for row in special_hosts) == 121, str(sum(int(row["written_carrier_slot_count"]) for row in special_hosts)))
    check("SPECIAL_HOST_SET", set(output_host_by_key) == set(by_governor), "74 exact governors")
    check("ROOT_SEQUENCE_RECONSTRUCTION", all(
        output_host_by_key[key]["written_root_sequence"] == "+".join(row["carrier_root"] for row in members)
        for key, members in by_governor.items()
    ), "ordered assignment rows")
    check("ROOT_MULTISET_RECONSTRUCTION", all(
        output_host_by_key[key]["written_root_multiset"] == root_multiset(members)
        for key, members in by_governor.items()
    ), "74 multiplicity-aware multisets")
    check("SPECIAL_LAYER_PROFILE", Counter(row["layer_profile"] for row in special_hosts) == {"RUNNING_ATOM": 71, "LOCAL_COMPONENT": 3}, str(Counter(row["layer_profile"] for row in special_hosts)))
    transfer_counts = Counter(row["multiset_transfer_status"] for row in special_hosts)
    check("PACKET_MULTISET_TRANSFER", transfer_counts == {"SAME_PACKET_MULTISET_OTHER_PAGE": 55, "PACKET_MULTISET_PAGE_PRIVATE": 19}, str(transfer_counts))
    check("SPECIAL_SHAPE_COUNT", len(special_shapes) == 34, str(len(special_shapes)))
    repeated = [row for row in special_hosts if row["repeated_root"] == "YES"]
    check("REPEATED_ROOT_HOSTS", len(repeated) == 13, str(len(repeated)))
    check("SET_SIGNATURE_LOSES_COUNTS", all("*2" in row["written_root_multiset"] and "*" not in row["presence_signature"] for row in repeated), "13 set-like old signatures")

    repair_by_id = {row["reader_unit_id"]: row for row in repairs}
    check("REPAIR_COUNT", len(repairs) == 13, str(len(repairs)))
    check("REPAIR_ID_SET", set(repair_by_id) == set(MULTIPLICITY_REPAIRS), "eleven statements plus two local cards")
    check("REPAIR_TEXT", all(
        row["gdt587_reader_clause_de"] == MULTIPLICITY_REPAIRS[row["reader_unit_id"]]["old"]
        and row["gdt588_count_safe_clause_de"] == MULTIPLICITY_REPAIRS[row["reader_unit_id"]]["new"]
        and "×2" in row["gdt588_count_safe_clause_de"]
        for row in repairs
    ), "13 explicit count-safe clauses")
    check("REPAIR_TARGETS_REPEATED", all(
        output_host_by_key[row["primary_governor_key"]]["repeated_root"] == "YES" for row in repairs
    ), "13 repeated hosts")

    old_statement = {row["statement_id"]: row for row in source["statements_587"]}
    old_local = {row["source_event_id"]: row for row in source["local_cards_587"]}
    statement_by_id = {row["statement_id"]: row for row in statements}
    local_by_id = {row["source_event_id"]: row for row in local_cards}
    check("STATEMENT_COUNT", len(statements) == 793 and set(statement_by_id) == set(old_statement), "793 exact IDs")
    check("LOCAL_COUNT", len(local_cards) == 744 and set(local_by_id) == set(old_local), "744 exact IDs")
    check("STATEMENT_BASES", all(row["gdt588_base_reader_de"] == old_statement[row["statement_id"]]["gdt587_primary_reader_de"] for row in statements), "793 GDT587 bases")
    check("LOCAL_BASES", all(row["gdt588_base_reader_de"] == old_local[row["source_event_id"]]["gdt587_primary_reader_de"] for row in local_cards), "744 GDT587 bases")
    check("CHANGED_STATEMENTS", {row["statement_id"] for row in statements if row["gdt588_multiplicity_repair"] == "YES"} == {key for key in MULTIPLICITY_REPAIRS if key.startswith("G407-S")}, "eleven exact statements")
    check("CHANGED_LOCAL", {row["source_event_id"] for row in local_cards if row["gdt588_multiplicity_repair"] == "YES"} == {key for key in MULTIPLICITY_REPAIRS if key.startswith("P912-E")}, "two exact cards")
    check("UNCHANGED_STATEMENTS", all(
        row["gdt588_primary_reader_de"] == old_statement[row["statement_id"]]["gdt587_primary_reader_de"]
        for row in statements if row["gdt588_multiplicity_repair"] == "NO"
    ), "782 byte-exact reader values")
    check("UNCHANGED_LOCAL", all(
        row["gdt588_primary_reader_de"] == old_local[row["source_event_id"]]["gdt587_primary_reader_de"]
        for row in local_cards if row["gdt588_multiplicity_repair"] == "NO"
    ), "742 byte-exact reader values")
    check("NEW_REPAIR_TEXT_INSTALLED", all(
        MULTIPLICITY_REPAIRS[key]["new"] in (
            statement_by_id[key]["gdt588_primary_reader_de"] if key in statement_by_id
            else local_by_id[key]["gdt588_primary_reader_de"]
        ) for key in MULTIPLICITY_REPAIRS
    ), "all thirteen clauses")

    check("PAGE_COUNT", len(pages) == 30, str(len(pages)))
    check("PAGE_ASSIGNMENT_TOTAL", sum(int(row["carrier_assignment_count"]) for row in pages) == 1243, str(sum(int(row["carrier_assignment_count"]) for row in pages)))
    check("PAGE_PACKET_TOTAL", sum(int(row["special_packet_host_count"]) for row in pages) == 74, str(sum(int(row["special_packet_host_count"]) for row in pages)))
    check("PAGE_REPAIR_TOTAL", sum(int(row["multiplicity_repair_count"]) for row in pages) == 13, str(sum(int(row["multiplicity_repair_count"]) for row in pages)))
    check("ONLY_F1R_PRIVATE", [row["physical_page"] for row in pages if int(row["page_private_register_root_count"])] == ["f1r"], "f1r only")

    clean_body = future_host_reading(
        action_root="SH", register="BIOLOGICAL", carrier_roots=["Y"],
        direct_tokens=[], host_tokens=["Y"], previous_action="NONE", next_action="NONE",
    )
    blocked_body = future_host_reading(
        action_root="SH", register="BIOLOGICAL", carrier_roots=["Y"],
        direct_tokens=[], host_tokens=["Y", "AL"], previous_action="NONE", next_action="NONE",
    )
    repeated_flow = future_host_reading(
        action_root="S", register="BIOLOGICAL", carrier_roots=["Y", "Y"],
        direct_tokens=[], host_tokens=["Y", "AL"], previous_action="NONE", next_action="NONE",
    )
    check("INTAKE_CLEAN_BODY", clean_body["automatic_gdt583_rule_id"] == "SH_BIO_BATHE" and clean_body["slot_readings"][0]["working_lemma_de"] == "Körper", str(clean_body["slot_readings"][0]))
    check("INTAKE_BLOCKED_BODY", blocked_body["automatic_gdt583_rule_id"] == "SH_BIO_BATHE" and blocked_body["slot_readings"][0]["working_lemma_de"] == "Stationsansatz", str(blocked_body["slot_readings"][0]))
    check("INTAKE_REPEAT_COUNT", repeated_flow["written_root_sequence"] == "Y+Y" and repeated_flow["written_root_multiset"] == "Y*2" and "Strom ×2" in repeated_flow["carrier_count_trace_de"], repeated_flow["carrier_count_trace_de"])
    check("INTAKE_NO_MANUAL_OVERRIDE", all(item["lookup_route"] != "MANUAL_GDT584_OVERRIDE" for item in repeated_flow["slot_readings"]), repeated_flow["action_gate"])

    check("BOOK_HEADER", book.startswith("# GDT588 — vollständiger mengenfester 30-Seiten-Arbeitsleser"), "book header")
    check("BOOK_PAGE_COUNT", book.count("\n## f") == 30, str(book.count("\n## f")))
    check("BOOK_COUNT_MARKERS", book.count("×2") >= 14, str(book.count("×2")))
    check("DECK_HEADLINES", all(text in deck for text in ("970", "1.116/1.243", "111 beobachtete", "Dreizehn")), "mobility, matrix, repairs")

    result_checks = {
        "assignment_count": 1243,
        "strict_selection_signature_count": 268,
        "mobile_strict_selection_signature_count": 103,
        "cell_count": 136,
        "rule_gate_count": 38,
        "future_cell_matrix_count": 220,
        "register_root_fallback_count": 20,
        "packet_card_count": 8,
        "special_packet_host_count": 74,
        "special_packet_carrier_count": 121,
        "special_packet_shape_count": 34,
        "repeated_root_special_host_count": 13,
        "multiplicity_repair_count": 13,
        "changed_statement_count": 11,
        "changed_local_card_count": 2,
        "complete_statement_count": 793,
        "complete_local_card_count": 744,
        "page_count": 30,
    }
    check("RESULT_SCALARS", all(result[key] == value for key, value in result_checks.items()), str(result_checks))

    rebuild_paths = [path for name, path in OUTPUTS.items() if name != "validation" and path.exists()]
    before = {str(path): sha256(path) for path in rebuild_paths}
    subprocess.run(
        ["python3", str(Path(__file__).with_name("run.py"))],
        cwd=Path(__file__).resolve().parents[5],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    after = {str(path): sha256(path) for path in rebuild_paths}
    check("BYTE_IDENTICAL_REBUILD", before == after, f"{len(before)} output files")

    failed = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT588",
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failed),
        "fail_count": len(failed),
        "checks": checks,
    }
    OUTPUTS["validation"].write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

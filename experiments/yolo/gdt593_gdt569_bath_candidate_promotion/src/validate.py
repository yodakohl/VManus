#!/usr/bin/env python3
"""Validate GDT593's twelve stable-root AIN/OR promotions."""

from __future__ import annotations

import csv
import json
from collections import Counter

from model import (
    BATH_PAGES,
    INPUTS,
    OUTPUTS,
    STATUS,
    build,
    load_inputs,
    render_reader,
    sha256,
    tsv_bytes,
)


EXPECTED_TARGETS = {
    "G407-E1560", "G407-E1717", "G407-E1778", "G407-E1781",
    "G407-E2608", "G407-E2828", "G407-E2997", "G407-E2998",
    "G407-E3134", "G407-E3314", "G407-E3315", "G407-E3628",
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})
        if not passed:
            raise RuntimeError(f"validation failed: {name}: {observed}")

    inputs = load_inputs()
    rebuilt = build(inputs)
    promotions = read_tsv(OUTPUTS["promotions"])
    actions = read_tsv(OUTPUTS["actions"])
    promoted_statements = read_tsv(OUTPUTS["promoted_statements"])
    statements = read_tsv(OUTPUTS["statements"])
    pages = read_tsv(OUTPUTS["pages"])
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))

    check("status", result["status"] == STATUS, result["status"])
    check("promotion_population", len(promotions) == 12, len(promotions))
    check("action_population", len(actions) == 254, len(actions))
    check("statement_population", len(statements) == 793, len(statements))
    check("promoted_statement_population", len(promoted_statements) == 12, len(promoted_statements))
    check("page_population", len(pages) == 6, len(pages))
    check("page_set", {row["physical_page"] for row in actions} == BATH_PAGES, sorted({row["physical_page"] for row in actions}))
    check("no_f84_actions", not any(row["physical_page"].lower().startswith("f84") for row in actions), "checked")
    check("no_f84_statements", not any(row["physical_page"].lower().startswith("f84") for row in statements), "checked")

    target_ids = {row["target_event_id"] for row in promotions}
    root_profile = Counter(row["gdt569_inherited_argument_root"] for row in promotions)
    object_profile = Counter(row["gdt593_object_class"] for row in promotions)
    source_profile = Counter(row["gdt581_lexical_source_kind"] for row in promotions)
    span_profile = Counter(row["reference_span"] for row in promotions)
    final_profile = Counter(row["gdt593_object_class"] for row in actions)
    check("target_set", target_ids == EXPECTED_TARGETS, sorted(target_ids))
    check("target_ids_unique", len(target_ids) == len(promotions), len(target_ids))
    check("target_statements_unique", len({row["target_statement_id"] for row in promotions}) == 12, "12")
    check("root_profile", root_profile == {"AIN": 8, "OR": 4}, dict(root_profile))
    check("promotion_object_profile", object_profile == {"PORTION": 8, "BATH_UNIT": 4}, dict(object_profile))
    check("source_profile", source_profile == {"SAME_STATEMENT_EVENT": 6, "OWNER_DEFAULT": 6}, dict(source_profile))
    check(
        "span_profile",
        span_profile == {
            "SAME_STATEMENT_VISIBLE_SOURCE": 5,
            "SAME_STATEMENT_SOURCE_ACROSS_READER_RESET": 1,
            "OWNER_DEFAULT_WITH_PRIOR_WRITTEN_CONTEXT_WITNESS": 6,
        },
        dict(span_profile),
    )
    check(
        "final_object_profile",
        final_profile == {"BODY": 53, "STATION": 81, "BATH_OBJECT": 95, "BATH_UNIT": 13, "PORTION": 12},
        dict(final_profile),
    )

    check("all_prior_witnesses", all(1 <= int(row["context_witness_event_distance"]) <= 5 for row in promotions), [result["context_witness_event_distance_min"], result["context_witness_event_distance_max"]])
    check("all_same_physical_paragraph", all(row["same_physical_paragraph"] == "YES" for row in promotions), "12/12")
    check("canonical_source_kind_parity", all((row["canonical_source_event_id"] == "OWNER") == (row["gdt581_lexical_source_kind"] == "OWNER_DEFAULT") for row in promotions), "12/12")
    check("owner_defaults_not_donors", all(row["source_disposition"] == "CONTEXT_WITNESS_NOT_OBJECT_SOURCE" for row in promotions if row["gdt581_lexical_source_kind"] == "OWNER_DEFAULT"), "6/6")
    check("written_sources_canonical", all(row["source_disposition"] == "CANONICAL_WRITTEN_SOURCE" for row in promotions if row["gdt581_lexical_source_kind"] == "SAME_STATEMENT_EVENT"), "6/6")
    check("exact_root_identity", all(row["gdt569_inherited_argument_root"] in row["gdt581_lexical_source_key"] for row in promotions), "12/12")
    check("gdt569_context_carry", all(row["gdt569_argument_source_type"] == "CONTEXT_CARRY" for row in promotions), "12/12")
    check("old_route_exact", all(row["gdt592_previous_route"] == "COLD_BATH_OBJECT_DEFAULT" for row in promotions), "12/12")
    check("old_class_exact", all(row["gdt592_previous_class"] == "BATH_OBJECT" for row in promotions), "12/12")
    check("old_clause_retained", all(row["retained_gdt592_badegut_clause_de"] == row["gdt592_previous_clause_de"] for row in promotions), "12/12")
    check("new_clause_no_generic", all("das zu badende Gut" not in row["gdt593_completed_clause_de"] for row in promotions), "12/12")
    check("anaphoric_realizations", sum(row["reference_realization"] == "ANAPHORIC_SAME_OBJECT_SCOPE" for row in promotions) == 5, "5")
    check("reset_type_realizations", sum(row["reference_realization"] == "DEFINITE_TARGET_TYPE_AFTER_RESET" for row in promotions) == 7, "7")
    check("ain_forms", all(row["gdt593_object_form_de"] in {"dieselbe Anwendungsportion", "die Anwendungsportion"} for row in promotions if row["gdt569_inherited_argument_root"] == "AIN"), "8/8")
    check("or_forms", all(row["gdt593_object_form_de"] in {"dieselbe Stationseinheit", "die Badeinheit"} for row in promotions if row["gdt569_inherited_argument_root"] == "OR"), "4/4")
    check("anaphoric_form_scope", all(row["gdt593_object_form_de"].startswith("dieselbe ") == (row["reference_span"] == "SAME_STATEMENT_VISIBLE_SOURCE") for row in promotions), "12/12")
    check("or_same_class_alternative", all(row["retained_same_class_alternative_de"] != "NOT_APPLICABLE" for row in promotions if row["gdt569_inherited_argument_root"] == "OR"), "4/4")
    check("or_local_station_unit", {row["target_event_id"] for row in promotions if row["gdt593_object_form_de"] == "dieselbe Stationseinheit"} == {"G407-E1560", "G407-E2997"}, "E1560/E2997")
    check("or_reset_bath_unit", {row["target_event_id"] for row in promotions if row["gdt593_object_form_de"] == "die Badeinheit"} == {"G407-E2828", "G407-E2998"}, "E2828/E2998")
    check("ain_no_unit_alternative", all(row["retained_same_class_alternative_de"] == "NOT_APPLICABLE" for row in promotions if row["gdt569_inherited_argument_root"] == "AIN"), "8/8")
    check("reader_occurrences_resolved", all(int(row["reader_clause_occurrence_index"]) >= 1 for row in promotions), "12/12")

    reset_rows = [row for row in promotions if row["reference_span"] == "SAME_STATEMENT_SOURCE_ACROSS_READER_RESET"]
    check("single_direct_reset", [row["target_event_id"] for row in reset_rows] == ["G407-E3314"], [row["target_event_id"] for row in reset_rows])
    check("owner_default_count", sum(row["canonical_source_event_id"] == "OWNER" for row in promotions) == 6, "6")
    check("grade_two_ain", {row["target_event_id"] for row in promotions if row["gdt569_inherited_argument_root"] == "AIN" and "Grad II" in row["gdt593_completed_clause_de"]} == {"G407-E2608"}, "E2608")
    check("grade_two_or", {row["target_event_id"] for row in promotions if row["gdt569_inherited_argument_root"] == "OR" and "Grad II" in row["gdt593_completed_clause_de"]} == {"G407-E2828", "G407-E2998"}, "E2828/E2998")

    changed_actions = [row for row in actions if row["gdt593_clause_changed"] == "YES"]
    retained_actions = [row for row in actions if row["gdt593_clause_changed"] == "NO"]
    changed_statements = [row for row in statements if row["gdt593_reader_changed"] == "YES"]
    retained_statements = [row for row in statements if row["gdt593_reader_changed"] == "NO"]
    check("changed_actions", len(changed_actions) == 12, len(changed_actions))
    check("retained_actions", len(retained_actions) == 242, len(retained_actions))
    check("changed_statements", len(changed_statements) == 12, len(changed_statements))
    check("retained_statements", len(retained_statements) == 781, len(retained_statements))
    check("changed_action_target_parity", {row["source_event_id"] for row in changed_actions} == target_ids, "12 exact")
    check("changed_statement_target_parity", {row["statement_id"] for row in changed_statements} == {row["target_statement_id"] for row in promotions}, "12 exact")
    check("remaining_cold_defaults", sum(row["gdt593_selection_route"] == "COLD_BATH_OBJECT_DEFAULT" for row in actions) == 93, "93")
    check("remaining_y_candidates", result["remaining_y_specific_candidate_count"] == 49, result["remaining_y_specific_candidate_count"])

    source_actions = {row["action_slot_id"]: row for row in inputs["gdt592_actions"]}
    source_statements = {row["statement_id"]: row for row in inputs["gdt592_statements"]}
    check("retained_action_clauses_byte_equal", all(row["gdt593_completed_clause_de"] == source_actions[row["action_slot_id"]]["gdt592_completed_clause_de"] for row in retained_actions), "242/242")
    check("retained_statement_text_byte_equal", all(row["gdt593_primary_reader_de"] == source_statements[row["statement_id"]]["gdt592_primary_reader_de"] for row in retained_statements), "781/781")
    check("changed_statements_single_patch", all(row["gdt593_promotion_count"] == "1" for row in changed_statements), "12/12")

    check("result_root_profile", result["promotion_root_profile"] == dict(sorted(root_profile.items())), result["promotion_root_profile"])
    check("result_object_profile", result["promotion_object_profile"] == dict(sorted(object_profile.items())), result["promotion_object_profile"])
    check("result_final_profile", result["final_object_profile"] == dict(sorted(final_profile.items())), result["final_object_profile"])
    check("result_input_hashes", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, "exact")

    for name in ("promotions", "actions", "promoted_statements", "statements", "pages"):
        check(f"byte_rebuild_{name}", OUTPUTS[name].read_bytes() == tsv_bytes(rebuilt[name]), "exact")
    check("byte_rebuild_reader", OUTPUTS["reader"].read_text(encoding="utf-8") == render_reader(rebuilt), "exact")
    check("byte_rebuild_result", result == rebuilt["result"], "exact")

    validation = {
        "experiment_id": "GDT593",
        "status": "PASS",
        "experiment_status": STATUS,
        "check_count": len(checks),
        "passed_count": sum(bool(row["passed"]) for row in checks),
        "failed_count": sum(not bool(row["passed"]) for row in checks),
        "checks": checks,
    }
    OUTPUTS["validation"].write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

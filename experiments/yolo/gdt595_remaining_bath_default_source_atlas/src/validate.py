#!/usr/bin/env python3
"""Validate GDT595 populations, source rules, patches, and byte rebuild."""

from __future__ import annotations

import json
from collections import Counter

from model import (
    AIIN_FILL_EXPECTED,
    BATH_PAGES,
    COLD_EXPECTED,
    DEFINITE_BODY_DEFAULT,
    DEPENDENT_CARRY_EXPECTED,
    INPUTS,
    LATE_Y_BODY_EXPECTED,
    LATE_Y_EXPECTED,
    LEFTWARD_ANAPHORA,
    MANUAL_RESIDUALS,
    MODEL_C_BODY,
    MODEL_C_STATION,
    OUTPUTS,
    RIGHTWARD_COMPLEMENT,
    RIGHT_COMPLEMENT_CORRECTIONS,
    SELECTED_BODY,
    SELECTED_PORTION,
    SELECTED_STATION,
    SELECTED_UNIT,
    STATUS,
    TIED_LOCAL_PACKET,
    WORKSHOP_BODY,
    WORKSHOP_PORTION,
    WORKSHOP_STATION,
    WORKSHOP_UNIT,
    build,
    load_inputs,
    render_reader,
    sha256,
    tsv_bytes,
)


def main() -> int:
    inputs = load_inputs()
    rebuilt = build(inputs)
    cards = rebuilt["source_cards"]
    comparison = rebuilt["model_comparison"]
    residuals = rebuilt["residuals"]
    propagations = rebuilt["propagations"]
    actions = rebuilt["actions"]
    statements = rebuilt["statements"]
    changed_statements = rebuilt["changed_statements"]
    pages = rebuilt["pages"]
    result = rebuilt["result"]

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "observed": observed})
        if not passed:
            raise AssertionError(f"{name}: {observed!r}")

    check("status_exact", result["status"] == STATUS, result["status"])
    check("card_count", len(cards) == 44, len(cards))
    check("comparison_count", len(comparison) == 44, len(comparison))
    check("residual_count", len(residuals) == 6, len(residuals))
    check("propagation_count", len(propagations) == 2, len(propagations))
    check("action_count", len(actions) == 254, len(actions))
    check("statement_count", len(statements) == 793, len(statements))
    check("page_count", len(pages) == 6, len(pages))

    target_ids = {row["target_event_id"] for row in cards}
    check("cold_target_set", target_ids == COLD_EXPECTED, sorted(target_ids))
    check("unique_action_slots", len({row["action_slot_id"] for row in cards}) == 44, "44/44")
    check("card_ordinals", [int(row["source_card_ordinal"]) for row in cards] == list(range(1, 45)), "1..44")
    check("comparison_ordinals", [int(row["comparison_ordinal"]) for row in comparison] == list(range(1, 45)), "1..44")

    frame_profile = Counter(row["source_kind"] for row in cards)
    check("frame_profile", frame_profile == {
        "AIIN_FILL_CONTEXT": 20,
        "SAME_EVENT_LATE_Y_PACKET": 18,
        "NO_AIIN_OR_SAME_EVENT_Y_CONTEXT": 6,
    }, dict(frame_profile))
    fill_ids = {row["target_event_id"] for row in cards if row["source_kind"] == "AIIN_FILL_CONTEXT"}
    late_ids = {row["target_event_id"] for row in cards if row["source_kind"] == "SAME_EVENT_LATE_Y_PACKET"}
    bare_ids = {row["target_event_id"] for row in cards if row["source_kind"] == "NO_AIIN_OR_SAME_EVENT_Y_CONTEXT"}
    check("fill_set", fill_ids == AIIN_FILL_EXPECTED, sorted(fill_ids))
    check("late_y_set", late_ids == LATE_Y_EXPECTED, sorted(late_ids))
    check("bare_set", bare_ids == set(MANUAL_RESIDUALS), sorted(bare_ids))
    check("frame_partition", fill_ids | late_ids | bare_ids == COLD_EXPECTED and not (fill_ids & late_ids or fill_ids & bare_ids or late_ids & bare_ids), "exact disjoint")

    direction_profile = Counter(row["primary_object_source_direction"] for row in cards)
    check("direction_profile", direction_profile == {
        "LEFTWARD_ANAPHORA": 21,
        "RIGHTWARD_SHARED_COMPLEMENT": 8,
        "BIDIRECTIONAL_PACKET_TIEBREAK": 1,
        "DEFINITE_BODY_DEFAULT": 14,
    }, dict(direction_profile))
    check("left_set", {row["target_event_id"] for row in cards if row["primary_object_source_direction"] == "LEFTWARD_ANAPHORA"} == LEFTWARD_ANAPHORA, sorted(LEFTWARD_ANAPHORA))
    check("right_set", {row["target_event_id"] for row in cards if row["primary_object_source_direction"] == "RIGHTWARD_SHARED_COMPLEMENT"} == RIGHTWARD_COMPLEMENT, sorted(RIGHTWARD_COMPLEMENT))
    check("tie_set", {row["target_event_id"] for row in cards if row["primary_object_source_direction"] == "BIDIRECTIONAL_PACKET_TIEBREAK"} == TIED_LOCAL_PACKET, sorted(TIED_LOCAL_PACKET))
    check("default_set", {row["target_event_id"] for row in cards if row["primary_object_source_direction"] == "DEFINITE_BODY_DEFAULT"} == DEFINITE_BODY_DEFAULT, sorted(DEFINITE_BODY_DEFAULT))

    direct_profile = Counter(row["gdt595_object_class"] for row in cards)
    check("direct_profile", direct_profile == {"BODY": 16, "STATION": 23, "PORTION": 3, "BATH_UNIT": 2}, dict(direct_profile))
    check("selected_body_set", {row["target_event_id"] for row in cards if row["gdt595_object_class"] == "BODY"} == SELECTED_BODY, sorted(SELECTED_BODY))
    check("selected_station_set", {row["target_event_id"] for row in cards if row["gdt595_object_class"] == "STATION"} == SELECTED_STATION, sorted(SELECTED_STATION))
    check("selected_portion_set", {row["target_event_id"] for row in cards if row["gdt595_object_class"] == "PORTION"} == SELECTED_PORTION, sorted(SELECTED_PORTION))
    check("selected_unit_set", {row["target_event_id"] for row in cards if row["gdt595_object_class"] == "BATH_UNIT"} == SELECTED_UNIT, sorted(SELECTED_UNIT))

    workshop_profile = Counter(row["workshop_model_class"] for row in cards)
    model_c_profile = Counter(row["model_c_class"] for row in cards)
    check("workshop_profile", workshop_profile == {"BODY": 20, "STATION": 19, "PORTION": 3, "BATH_UNIT": 2}, dict(workshop_profile))
    check("workshop_sets", {row["target_event_id"] for row in cards if row["workshop_model_class"] == "BODY"} == WORKSHOP_BODY and {row["target_event_id"] for row in cards if row["workshop_model_class"] == "STATION"} == WORKSHOP_STATION and {row["target_event_id"] for row in cards if row["workshop_model_class"] == "PORTION"} == WORKSHOP_PORTION and {row["target_event_id"] for row in cards if row["workshop_model_class"] == "BATH_UNIT"} == WORKSHOP_UNIT, "exact")
    check("model_c_profile", model_c_profile == {"BODY": 23, "STATION": 21}, dict(model_c_profile))
    check("model_c_sets", {row["target_event_id"] for row in cards if row["model_c_class"] == "BODY"} == MODEL_C_BODY and {row["target_event_id"] for row in cards if row["model_c_class"] == "STATION"} == MODEL_C_STATION, "exact")
    correction_ids = {row["target_event_id"] for row in cards if row["hybrid_changed_from_workshop"] == "YES"}
    check("four_workshop_corrections", correction_ids == RIGHT_COMPLEMENT_CORRECTIONS, sorted(correction_ids))
    check("corrections_body_to_station", all(row["workshop_model_class"] == "BODY" and row["gdt595_object_class"] == "STATION" for row in cards if row["target_event_id"] in correction_ids), "4/4")

    fill_profile = Counter(row["gdt595_object_class"] for row in cards if row["target_event_id"] in AIIN_FILL_EXPECTED)
    late_profile = Counter(row["gdt595_object_class"] for row in cards if row["target_event_id"] in LATE_Y_EXPECTED)
    bare_profile = Counter(row["gdt595_object_class"] for row in cards if row["target_event_id"] in bare_ids)
    check("fill_object_profile", fill_profile == {"BODY": 12, "STATION": 7, "PORTION": 1}, dict(fill_profile))
    check("late_y_object_profile", late_profile == {"BODY": 2, "STATION": 13, "PORTION": 2, "BATH_UNIT": 1}, dict(late_profile))
    check("bare_object_profile", bare_profile == {"BODY": 2, "STATION": 3, "BATH_UNIT": 1}, dict(bare_profile))
    check("late_y_body_set", {row["target_event_id"] for row in cards if row["target_event_id"] in LATE_Y_EXPECTED and row["gdt595_object_class"] == "BODY"} == LATE_Y_BODY_EXPECTED, sorted(LATE_Y_BODY_EXPECTED))
    check("rightward_profile", Counter(row["gdt595_object_class"] for row in cards if row["target_event_id"] in RIGHTWARD_COMPLEMENT) == {"BODY": 2, "STATION": 6}, "2 body / 6 station")

    left_rows = [row for row in cards if row["primary_object_source_direction"] == "LEFTWARD_ANAPHORA"]
    right_rows = [row for row in cards if row["primary_object_source_direction"] == "RIGHTWARD_SHARED_COMPLEMENT"]
    default_rows = [row for row in cards if row["primary_object_source_direction"] == "DEFINITE_BODY_DEFAULT"]
    check("left_sources_named", all(row["primary_object_source_slot_ids"].startswith("RUNNING:") for row in left_rows), "21/21")
    check("left_forms_anaphoric", all(row["gdt595_object_form_de"].startswith(("denselben", "dieselbe")) for row in left_rows), "21/21")
    check("right_sources_same_event", all(row["primary_object_source_slot_ids"].startswith(f"RUNNING:{row['target_event_id']}@") for row in right_rows), "8/8")
    check("right_forms_definite", all(not row["gdt595_object_form_de"].startswith(("denselben", "dieselbe")) for row in right_rows), "8/8")
    check("default_body_only", all(row["gdt595_object_class"] == "BODY" and row["gdt595_object_form_de"] == "den Körper" and row["primary_object_source_slot_ids"] == "NO_PRIMARY_OBJECT_SOURCE" for row in default_rows), "14/14")
    check("tie_station_definite", all(row["gdt595_object_class"] == "STATION" and row["gdt595_object_form_de"] == "den Stationsansatz" and "LEFT:" in row["primary_object_source_slot_ids"] and "RIGHT:" in row["primary_object_source_slot_ids"] for row in cards if row["target_event_id"] in TIED_LOCAL_PACKET), "1/1")
    check("frame_slots_resolved", all(row["frame_evidence_slot_ids"] and row["frame_evidence_slot_ids"] != "PENDING" for row in cards), "44/44")
    check("reader_occurrences_resolved", all(int(row["reader_clause_occurrence_index"]) >= 1 for row in cards), "44/44")

    check("old_badegut_exact", all("das zu badende Gut" in row["gdt594_previous_clause_de"] for row in cards), "44/44")
    check("new_badegut_absent", all("zu badende Gut" not in row["gdt595_completed_clause_de"] for row in cards), "44/44")
    check("selected_form_in_clause", all(row["gdt595_object_form_de"] in row["gdt595_completed_clause_de"] for row in cards), "44/44")
    check("badegut_rival_retained", all(row["retained_badegut_clause_de"] == row["gdt594_previous_clause_de"] for row in cards), "44/44")
    check("body_rival_complete", all("Körper" in row["retained_body_clause_de"] for row in cards), "44/44")
    check("station_rival_complete", all("Stationsansatz" in row["retained_station_clause_de"] for row in cards), "44/44")
    check("portion_rival_complete", all("Anwendungsportion" in row["retained_portion_clause_de"] for row in cards), "44/44")
    check("unit_rival_complete", all("Badeinheit" in row["retained_unit_clause_de"] for row in cards), "44/44")

    propagation_map = {row["target_event_id"]: row["carry_source_event_id"] for row in propagations}
    check("propagation_map", propagation_map == DEPENDENT_CARRY_EXPECTED, propagation_map)
    check("propagation_occurrences", all(int(row["reader_clause_occurrence_index"]) >= 1 for row in propagations), "2/2")
    prop_by_event = {row["target_event_id"]: row for row in propagations}
    check("e3219_body_carry", prop_by_event["G407-E3219"]["source_resolved_class"] == "BODY" and prop_by_event["G407-E3219"]["gdt595_completed_clause_de"] == "Halte denselben Körper im Bad auf Grad I", prop_by_event["G407-E3219"]["gdt595_completed_clause_de"])
    check("e3489_station_carry", prop_by_event["G407-E3489"]["source_resolved_class"] == "STATION" and prop_by_event["G407-E3489"]["gdt595_completed_clause_de"] == "Halte denselben Stationsansatz im Bad auf Grad I", prop_by_event["G407-E3489"]["gdt595_completed_clause_de"])

    final_profile = Counter(row["gdt595_object_class"] for row in actions)
    check("final_profile", final_profile == {"BODY": 100, "STATION": 122, "PORTION": 15, "BATH_UNIT": 15, "FLOW": 2}, dict(final_profile))
    check("no_bath_object_class", final_profile.get("BATH_OBJECT", 0) == 0, final_profile.get("BATH_OBJECT", 0))
    check("no_cold_route", not any(row["gdt595_selection_route"] == "COLD_BATH_OBJECT_DEFAULT" for row in actions), "0")
    changed_actions = [row for row in actions if row["gdt595_clause_changed"] == "YES"]
    retained_actions = [row for row in actions if row["gdt595_clause_changed"] == "NO"]
    check("changed_actions", len(changed_actions) == 46, len(changed_actions))
    check("retained_actions", len(retained_actions) == 208, len(retained_actions))
    check("changed_action_set", {row["source_event_id"] for row in changed_actions} == COLD_EXPECTED | set(DEPENDENT_CARRY_EXPECTED), sorted(row["source_event_id"] for row in changed_actions))
    check("changed_action_no_generic", all("zu badende Gut" not in row["gdt595_completed_clause_de"] for row in changed_actions), "46/46")

    source_actions_by_slot = {row["action_slot_id"]: row for row in inputs["gdt594_actions"]}
    check("action_order_retained", [row["action_slot_id"] for row in actions] == [row["action_slot_id"] for row in inputs["gdt594_actions"]], "exact")
    check("retained_action_byte_equal", all(row["gdt595_completed_clause_de"] == source_actions_by_slot[row["action_slot_id"]]["gdt594_completed_clause_de"] for row in retained_actions), "208/208")
    old_gdt594_changes = [row for row in actions if row["gdt594_clause_changed"] == "YES"]
    check("gdt594_changes_retained", len(old_gdt594_changes) == 49 and all(row["gdt595_clause_changed"] == "NO" and row["gdt595_completed_clause_de"] == row["gdt594_completed_clause_de"] for row in old_gdt594_changes), "49/49")
    old_gdt593_changes = [row for row in actions if row["gdt593_clause_changed"] == "YES"]
    check("gdt593_changes_retained", len(old_gdt593_changes) == 12 and all(row["gdt595_clause_changed"] == "NO" for row in old_gdt593_changes), "12/12")

    check("changed_statement_count", len(changed_statements) == 42, len(changed_statements))
    check("retained_statement_count", len(statements) - len(changed_statements) == 751, len(statements) - len(changed_statements))
    patch_count_profile = Counter(int(row["gdt595_completion_count"]) for row in changed_statements)
    check("statement_patch_profile", patch_count_profile == {1: 39, 2: 2, 3: 1}, dict(patch_count_profile))
    check("triple_patch_statement", {row["statement_id"] for row in changed_statements if int(row["gdt595_completion_count"]) == 3} == {"G407-S502"}, [row["statement_id"] for row in changed_statements if int(row["gdt595_completion_count"]) == 3])
    check("double_patch_statements", {row["statement_id"] for row in changed_statements if int(row["gdt595_completion_count"]) == 2} == {"G407-S565", "G407-S583"}, [row["statement_id"] for row in changed_statements if int(row["gdt595_completion_count"]) == 2])
    source_statements_by_id = {row["statement_id"]: row for row in inputs["gdt594_statements"]}
    retained_statements = [row for row in statements if row["gdt595_reader_changed"] == "NO"]
    check("statement_order_retained", [row["statement_id"] for row in statements] == [row["statement_id"] for row in inputs["gdt594_statements"]], "exact")
    check("retained_statement_byte_equal", all(row["gdt595_primary_reader_de"] == source_statements_by_id[row["statement_id"]]["gdt594_primary_reader_de"] for row in retained_statements), "751/751")
    check("primary_reader_no_badegut", all("zu badende Gut" not in row["gdt595_primary_reader_de"] for row in statements), "793/793")
    statements_by_id = {row["statement_id"]: row for row in statements}
    check("s502_occurrence_safe", "Halte den Körper im Bad bei der angegebenen Füllung auf Grad I. Halte denselben Körper im Bad auf Grad I" in statements_by_id["G407-S502"]["gdt595_primary_reader_de"] and statements_by_id["G407-S502"]["gdt595_primary_reader_de"].count("Halte den Körper im Bad auf Grad I") >= 1, statements_by_id["G407-S502"]["gdt595_primary_reader_de"])
    check("s565_carry_safe", statements_by_id["G407-S565"]["gdt595_primary_reader_de"].count("denselben Stationsansatz im Bad auf Grad I") == 2, statements_by_id["G407-S565"]["gdt595_primary_reader_de"])
    check("s583_duplicate_clause_safe", statements_by_id["G407-S583"]["gdt595_primary_reader_de"].count("Halte den Stationsansatz im Bad auf Grad I") == 2, statements_by_id["G407-S583"]["gdt595_primary_reader_de"])
    card_by_event = {row["target_event_id"]: row for row in cards}
    check("s583_occurrence_indices", int(card_by_event["G407-E3560"]["reader_clause_occurrence_index"]) == 1 and int(card_by_event["G407-E3563"]["reader_clause_occurrence_index"]) == 2, {event: card_by_event[event]["reader_clause_occurrence_index"] for event in ("G407-E3560", "G407-E3563")})
    check("e3664_e3673_safe", statements_by_id["G407-S616"]["gdt595_primary_reader_de"].count("Stationsansatz im Bad auf Grad I") == 3 and "Halte denselben Stationsansatz" in statements_by_id["G407-S616"]["gdt595_primary_reader_de"], statements_by_id["G407-S616"]["gdt595_primary_reader_de"])

    check("page_set", {row["physical_page"] for row in pages} == BATH_PAGES, sorted(row["physical_page"] for row in pages))
    check("page_action_sum", sum(int(row["bath_action_count"]) for row in pages) == 254, sum(int(row["bath_action_count"]) for row in pages))
    check("page_direct_sum", sum(int(row["direct_completion_count"]) for row in pages) == 44, sum(int(row["direct_completion_count"]) for row in pages))
    check("page_propagation_sum", sum(int(row["dependent_propagation_count"]) for row in pages) == 2, sum(int(row["dependent_propagation_count"]) for row in pages))
    check("no_forbidden_output_rows", all(not row["physical_page"].lower().startswith("f84") for collection in (cards, residuals, propagations, actions, statements, pages) for row in collection), "none")

    historical = rebuilt["historical_sources"]
    check("historical_source_count", len(historical) == 5, len(historical))
    check("historical_source_ids", {row["source_id"] for row in historical} == {"HIST01", "HIST02", "HIST03", "HIST04", "HIST05"}, sorted(row["source_id"] for row in historical))
    check("historical_https_urls", all(row["source_url"].startswith("https://") for row in historical), [row["source_url"] for row in historical])
    check("historical_transfer_limits", all(row["transfer_limit"] for row in historical), "5/5")

    check("comparison_target_parity", {row["target_event_id"] for row in comparison} == COLD_EXPECTED, "44 exact")
    check("comparison_selected_parity", all(row["selected_hybrid_class"] == card_by_event[row["target_event_id"]]["gdt595_object_class"] for row in comparison), "44/44")
    check("comparison_rivals_complete", all(row["body_rival_de"] and row["station_rival_de"] and row["portion_rival_de"] and row["unit_rival_de"] for row in comparison), "44/44")

    check("result_direct_profile", result["direct_completion_object_profile"] == dict(sorted(direct_profile.items())), result["direct_completion_object_profile"])
    check("result_final_profile", result["final_object_profile"] == dict(sorted(final_profile.items())), result["final_object_profile"])
    check("result_no_cold", result["remaining_cold_bath_object_default_count"] == 0, result["remaining_cold_bath_object_default_count"])
    check("result_no_bath_object", result["remaining_bath_object_class_count"] == 0, result["remaining_bath_object_class_count"])
    check("result_changed_actions", result["changed_action_count"] == 46, result["changed_action_count"])
    check("result_changed_statements", result["changed_statement_count"] == 42, result["changed_statement_count"])
    check("result_hybrid_corrections", set(result["hybrid_changed_from_workshop_event_ids"]) == RIGHT_COMPLEMENT_CORRECTIONS, result["hybrid_changed_from_workshop_event_ids"])
    check("result_input_hashes", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, "exact")

    for name in (
        "source_cards", "model_comparison", "residuals", "propagations",
        "actions", "changed_statements", "statements", "pages",
    ):
        check(f"byte_rebuild_{name}", OUTPUTS[name].read_bytes() == tsv_bytes(rebuilt[name]), "exact")
    check("byte_rebuild_reader", OUTPUTS["reader"].read_text(encoding="utf-8") == render_reader(rebuilt), "exact")
    check("byte_rebuild_result", json.loads(OUTPUTS["result"].read_text(encoding="utf-8")) == result, "exact")

    validation = {
        "experiment_id": "GDT595",
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

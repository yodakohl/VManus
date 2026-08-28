#!/usr/bin/env python3
"""Validate GDT594's 49 occurrence-level Y bath completions."""

from __future__ import annotations

import csv
import json
from collections import Counter

from model import (
    BATH_PAGES,
    INPUTS,
    MANUAL_FLOW_OPERATIONAL,
    MANUAL_FRAGMENTED_CONTROL,
    MANUAL_TWO_WAY,
    OUTPUTS,
    STATUS,
    build,
    load_inputs,
    render_reader,
    sha256,
    tsv_bytes,
)


EXPECTED_TARGETS = {
    "G407-E1431", "G407-E1520", "G407-E1563", "G407-E1565",
    "G407-E1569", "G407-E1582", "G407-E1584", "G407-E1590",
    "G407-E1658", "G407-E1699", "G407-E1702", "G407-E1706",
    "G407-E1723", "G407-E1776", "G407-E1814", "G407-E2457",
    "G407-E2537", "G407-E2612", "G407-E2628", "G407-E2783",
    "G407-E2788", "G407-E2792", "G407-E2822", "G407-E2824",
    "G407-E2839", "G407-E2869", "G407-E2897", "G407-E2917",
    "G407-E3017", "G407-E3049", "G407-E3079", "G407-E3090",
    "G407-E3097", "G407-E3216", "G407-E3332", "G407-E3399",
    "G407-E3404", "G407-E3426", "G407-E3460", "G407-E3556",
    "G407-E3570", "G407-E3580", "G407-E3581", "G407-E3662",
    "G407-E3673", "G407-E3684", "G407-E3695", "G407-E3740",
    "G407-E3768",
}
LOCAL_STATION = {
    "G407-E1520", "G407-E1563", "G407-E1569", "G407-E1699",
    "G407-E1706", "G407-E1723", "G407-E1814", "G407-E2612",
    "G407-E2792", "G407-E2839", "G407-E2897", "G407-E3079",
    "G407-E3090", "G407-E3097", "G407-E3426", "G407-E3673",
    "G407-E3684",
}
LOCAL_FLOW = {"G407-E1590", "G407-E2869"}
LOCAL_BODY = {"G407-E1658"}
READER_RESET = {"G407-E1431", "G407-E3768"}
SEMANTIC_HOST_RESET = {
    "G407-E1431", "G407-E1658", "G407-E3426", "G407-E3673",
    "G407-E3768",
}
HOST_ATOM_SCOPE_CONFLICT = {"G407-E1658", "G407-E3426", "G407-E3673"}
PHYSICAL_PARAGRAPH_CROSSINGS = {"G407-E2537", "G407-E2628"}
GRADE_TWO = {
    "G407-E1565", "G407-E1582", "G407-E2788", "G407-E2897",
    "G407-E3556",
}
RESET_BODY = EXPECTED_TARGETS - LOCAL_STATION - LOCAL_FLOW - LOCAL_BODY
MULTI_ACTION_TARGETS = {
    "G407-E1569", "G407-E1590", "G407-E1814", "G407-E2457",
    "G407-E2783", "G407-E3017", "G407-E3399", "G407-E3581",
}
MULTI_CANDIDATE_LOCI = {
    "f75r.16": {"G407-E1563", "G407-E1565", "G407-E1569"},
    "f75r.18": {"G407-E1582", "G407-E1584"},
    "f75r.31": {"G407-E1702", "G407-E1706"},
    "f81r.18": {"G407-E2822", "G407-E2824"},
    "f83r.14": {"G407-E3580", "G407-E3581"},
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
    candidates = read_tsv(OUTPUTS["candidates"])
    actions = read_tsv(OUTPUTS["actions"])
    changed_statements = read_tsv(OUTPUTS["changed_statements"])
    statements = read_tsv(OUTPUTS["statements"])
    pages = read_tsv(OUTPUTS["pages"])
    boundary_cases = read_tsv(OUTPUTS["boundary_cases"])
    scope_conflicts = read_tsv(OUTPUTS["scope_conflicts"])
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))

    check("status", result["status"] == STATUS, result["status"])
    check("candidate_population", len(candidates) == 49, len(candidates))
    check("action_population", len(actions) == 254, len(actions))
    check("statement_population", len(statements) == 793, len(statements))
    check("changed_statement_population", len(changed_statements) == 49, len(changed_statements))
    check("boundary_case_population", len(boundary_cases) == 2, len(boundary_cases))
    check("scope_conflict_population", len(scope_conflicts) == 3, len(scope_conflicts))
    check("page_population", len(pages) == 6, len(pages))
    check("page_set", {row["physical_page"] for row in actions} == BATH_PAGES, sorted({row["physical_page"] for row in actions}))
    check("no_f84_actions", not any(row["physical_page"].lower().startswith("f84") for row in actions), "checked")
    check("no_f84_candidates", not any(row["physical_page"].lower().startswith("f84") for row in candidates), "checked")
    check("no_f84_statements", not any(row["physical_page"].lower().startswith("f84") for row in statements), "checked")

    target_ids = {row["target_event_id"] for row in candidates}
    check("target_set", target_ids == EXPECTED_TARGETS, sorted(target_ids))
    check("target_ids_unique", len(target_ids) == len(candidates), len(target_ids))
    check("target_action_slots_unique", len({row["action_slot_id"] for row in candidates}) == 49, "49")
    check("target_governors_unique", len({row["target_primary_governor_key"] for row in candidates}) == 49, "49")
    check("target_statements_unique", len({row["target_statement_id"] for row in candidates}) == 49, "49")

    action_roots = {"T", "SH", "CHD", "S", "K", "CH", "OK", "R", "P"}
    observed_multi_action = {
        row["target_event_id"] for row in candidates
        if sum(atom in action_roots for atom in row["target_recipe"].split("+")) > 1
    }
    check("multi_action_target_set", observed_multi_action == MULTI_ACTION_TARGETS, sorted(observed_multi_action))
    observed_multi_loci = {}
    for locus in {row["target_locus"] for row in candidates}:
        members = {row["target_event_id"] for row in candidates if row["target_locus"] == locus}
        if len(members) > 1:
            observed_multi_loci[locus] = members
    check("multi_candidate_loci", observed_multi_loci == MULTI_CANDIDATE_LOCI, {key: sorted(value) for key, value in observed_multi_loci.items()})
    surface_profile = Counter(row["target_surface"] for row in candidates)
    check("target_surface_profile", surface_profile == {"shedy": 31, "dshedy": 5, "sheedy": 5, "okshedy": 2, "qokshedy": 2, "sshedy": 2, "sheckhedy": 1, "rshedy": 1}, dict(surface_profile))

    exact_source_targets = {
        row["source_event_id"] for row in inputs["gdt593_actions"]
        if row["gdt569_parallel_relation"]
        == "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT"
        and row["gdt569_inherited_argument_root"] == "Y"
        and row["gdt593_selection_route"] == "COLD_BATH_OBJECT_DEFAULT"
    }
    check("candidate_predicate_exact", exact_source_targets == target_ids, sorted(exact_source_targets))
    source_candidate_rows = [
        row for row in inputs["gdt593_actions"] if row["source_event_id"] in target_ids
    ]
    check("candidate_hosts_empty", all(row["carrier_slot_count"] == "0" and row["carrier_slot_ids"] == "NONE" for row in source_candidate_rows), "49/49")
    check("candidate_no_aiin_fill", all(row["aiin_fill_present"] == "NO" for row in source_candidate_rows), "49/49")
    check("candidate_no_body_blocker", all(row["body_blockers_present"] == "NONE" for row in source_candidate_rows), "49/49")
    check("root_y_only", all(row["gdt569_inherited_argument_root"] == "Y" for row in candidates), "49/49")
    check("gdt569_context_carry", all(row["gdt569_argument_source_type"] == "CONTEXT_CARRY" for row in candidates), "49/49")
    check("old_route_exact", all(row["gdt593_previous_route"] == "COLD_BATH_OBJECT_DEFAULT" for row in candidates), "49/49")
    check("old_class_exact", all(row["gdt593_previous_class"] == "BATH_OBJECT" for row in candidates), "49/49")

    source_profile = Counter(row["gdt581_lexical_source_kind"] for row in candidates)
    scope_profile = Counter(row["scope_class"] for row in candidates)
    object_profile = Counter(row["gdt594_object_class"] for row in candidates)
    final_profile = Counter(row["gdt594_object_class"] for row in actions)
    meaning_profile = Counter(row["context_witness_meaning_source"] for row in candidates)
    context_profile = Counter(row["context_witness_class"] for row in candidates)
    manual_profile = Counter(row["manual_reader_disposition"] for row in candidates)
    check("source_profile", source_profile == {"SAME_STATEMENT_EVENT": 22, "OWNER_DEFAULT": 27}, dict(source_profile))
    check("scope_profile", scope_profile == {"SAME_OBJECT_SCOPE": 20, "SAME_STATEMENT_READER_RESET": 2, "OWNER_DEFAULT_RESET": 27}, dict(scope_profile))
    check("completion_object_profile", object_profile == {"STATION": 17, "FLOW": 2, "BODY": 30}, dict(object_profile))
    check("final_object_profile", final_profile == {"BODY": 83, "STATION": 98, "BATH_OBJECT": 46, "BATH_UNIT": 13, "PORTION": 12, "FLOW": 2}, dict(final_profile))
    check("meaning_source_profile", meaning_profile == {"GDT590_EXACT_ACTION_CONDITIONED_WITNESS": 27, "GDT582_EXACT_WRITTEN_SLOT_WITNESS": 22}, dict(meaning_profile))
    check("context_witness_class_profile", context_profile == {"STATION": 42, "BODY": 5, "FLOW": 2}, dict(context_profile))
    check("manual_reader_profile", manual_profile == {"STRAIGHTFORWARD_WORKING_READING": 35, "READABLE_TWO_WAY": 11, "FLOW_MUST_BE_READ_OPERATIONALLY": 2, "SURROUNDING_CONTROL_PROSE_FRAGMENTED": 1}, dict(manual_profile))

    station_ids = {row["target_event_id"] for row in candidates if row["gdt594_object_class"] == "STATION"}
    flow_ids = {row["target_event_id"] for row in candidates if row["gdt594_object_class"] == "FLOW"}
    body_ids = {row["target_event_id"] for row in candidates if row["gdt594_object_class"] == "BODY"}
    check("local_station_set", station_ids == LOCAL_STATION, sorted(station_ids))
    check("local_flow_set", flow_ids == LOCAL_FLOW, sorted(flow_ids))
    check("body_set", body_ids == RESET_BODY | LOCAL_BODY, sorted(body_ids))
    check("reader_reset_set", {row["target_event_id"] for row in boundary_cases} == READER_RESET, [row["target_event_id"] for row in boundary_cases])
    check("host_atom_scope_conflict_set", {row["target_event_id"] for row in scope_conflicts} == HOST_ATOM_SCOPE_CONFLICT, [row["target_event_id"] for row in scope_conflicts])
    check("physical_paragraph_crossings", {row["target_event_id"] for row in candidates if row["same_physical_paragraph"] == "NO"} == PHYSICAL_PARAGRAPH_CROSSINGS, [row["target_event_id"] for row in candidates if row["same_physical_paragraph"] == "NO"])
    check("grade_two_set", {row["target_event_id"] for row in candidates if "Grad II" in row["gdt594_completed_clause_de"]} == GRADE_TWO, sorted(row["target_event_id"] for row in candidates if "Grad II" in row["gdt594_completed_clause_de"]))
    check("old_clause_grade_profile", Counter("II" if "Grad II" in row["gdt593_previous_clause_de"] else "I" for row in candidates) == {"I": 44, "II": 5}, "44/5")
    check("candidate_page_profile", Counter(row["physical_page"] for row in candidates) == {"f75r": 15, "f77r": 4, "f81r": 9, "f81v": 5, "f82r": 5, "f83r": 11}, dict(Counter(row["physical_page"] for row in candidates)))
    witness_targets = {}
    for witness in {row["context_witness_event_id"] for row in candidates}:
        members = {row["target_event_id"] for row in candidates if row["context_witness_event_id"] == witness}
        if len(members) > 1:
            witness_targets[witness] = members
    check("shared_witness_fanouts", witness_targets == {
        "G407-E1562": {"G407-E1563", "G407-E1565"},
        "G407-E1577": {"G407-E1582", "G407-E1584"},
        "G407-E1696": {"G407-E1699", "G407-E1702"},
        "G407-E2817": {"G407-E2822", "G407-E2824"},
        "G407-E3394": {"G407-E3399", "G407-E3404"},
        "G407-E3578": {"G407-E3580", "G407-E3581"},
    }, {key: sorted(value) for key, value in witness_targets.items()})

    local = [row for row in candidates if row["scope_class"] == "SAME_OBJECT_SCOPE"]
    direct_resets = [row for row in candidates if row["scope_class"] == "SAME_STATEMENT_READER_RESET"]
    owner_resets = [row for row in candidates if row["scope_class"] == "OWNER_DEFAULT_RESET"]
    check("local_same_statement", all(row["gdt581_lexical_source_kind"] == "SAME_STATEMENT_EVENT" and row["context_witness_statement_distance"] == "0" for row in local), "20/20")
    check("local_no_reader_reset", all(row["intervening_reader_reset_count"] == "0" and row["intervening_reader_reset_host_keys"] == "NONE" for row in local), "20/20")
    check("local_source_is_witness", all(row["canonical_source_event_id"] == row["context_witness_event_id"] for row in local), "20/20")
    check("local_source_leftward", all(int(row["canonical_source_host_ordinal_in_statement"]) < int(row["target_host_ordinal_in_statement"]) for row in local), "20/20")
    check("reader_resets_same_statement", all(row["gdt581_lexical_source_kind"] == "SAME_STATEMENT_EVENT" and row["context_witness_statement_distance"] == "0" for row in direct_resets), "2/2")
    check("reader_resets_visible", all(int(row["intervening_reader_reset_count"]) >= 1 and row["intervening_reader_reset_host_keys"] != "NONE" for row in direct_resets), "2/2")
    check("semantic_host_reset_set", {row["target_event_id"] for row in candidates if int(row["semantic_host_reset_count"]) > 0} == SEMANTIC_HOST_RESET, sorted(SEMANTIC_HOST_RESET))
    check("conflicts_are_post_cut_local", all(row["scope_class"] == "SAME_OBJECT_SCOPE" and row["semantic_host_reset_count"] == "1" and row["intervening_reader_reset_count"] == "0" for row in scope_conflicts), "3/3")
    check("conflicts_retain_host_model", all(row["retained_semantic_host_scope_alternative_de"] == "Halte den Körper im Bad auf Grad I" for row in scope_conflicts), "3/3")
    check("conflict_gdt559_inheritance", all(row["gdt559_transition_outcome"] == "NEXT_INHERITS_CURRENT_ARGUMENT" and row["gdt559_transition_event_id"] == row["context_witness_event_id"] for row in scope_conflicts), "3/3")
    check("gdt559_direct_target_set", {row["next_event_id"] for row in inputs["gdt559_transitions"] if row["next_event_id"] in target_ids and row["successor_outcome"] == "NEXT_INHERITS_CURRENT_ARGUMENT"} == {"G407-E1590", "G407-E3426", "G407-E3673"}, "E1590/E3426/E3673")
    check("nonconflicts_no_gdt559_override", all(row["gdt559_transition_event_id"] == "NOT_APPLICABLE" for row in candidates if row["target_event_id"] not in HOST_ATOM_SCOPE_CONFLICT), "46/46")
    check("conflict_written_order", all(row["source_written_atom_coordinate"] != "NOT_APPLICABLE" and row["target_written_atom_coordinate"] != "NOT_APPLICABLE" for row in scope_conflicts), "3/3")
    check("owner_resets_are_owner_defaults", all(row["gdt581_lexical_source_kind"] == "OWNER_DEFAULT" and row["canonical_source_event_id"] == "OWNER" for row in owner_resets), "27/27")
    check("owner_witness_not_donor", all(row["source_disposition"] == "CONTEXT_WITNESS_NOT_OBJECT_SOURCE" and int(row["context_witness_statement_distance"]) >= 1 for row in owner_resets), "27/27")
    check("paragraph_crossings_are_owner_resets", all(row["scope_class"] == "OWNER_DEFAULT_RESET" for row in candidates if row["same_physical_paragraph"] == "NO"), "2/2")
    check("all_witnesses_prior", all(1 <= int(row["context_witness_event_distance"]) <= 10 for row in candidates), [result["context_witness_event_distance_min"], result["context_witness_event_distance_max"]])

    check("station_local_lemmas", all(row["context_witness_lemma_de"] == "Stationsansatz" and row["gdt594_object_form_de"] == "denselben Stationsansatz" for row in candidates if row["gdt594_object_class"] == "STATION"), "17/17")
    check("flow_local_lemmas", all(row["context_witness_lemma_de"] == "Strom" and row["gdt594_object_form_de"] == "denselben Strom" for row in candidates if row["gdt594_object_class"] == "FLOW"), "2/2")
    check("flow_operational_phrase", all("denselben Strom im Badbetrieb" in row["gdt594_completed_clause_de"] for row in candidates if row["gdt594_object_class"] == "FLOW"), "2/2")
    check("local_body_form", {row["target_event_id"] for row in candidates if row["gdt594_object_form_de"] == "denselben Körper"} == LOCAL_BODY, sorted(LOCAL_BODY))
    check("body_reset_forms", all(row["gdt594_object_form_de"] == "den Körper" for row in candidates if row["target_event_id"] in RESET_BODY), "29/29")
    check("anaphoric_local_only", all((row["reference_realization"] == "ANAPHORIC_SAME_OBJECT_SCOPE") == (row["scope_class"] == "SAME_OBJECT_SCOPE") for row in candidates), "49/49")
    check("no_generic_in_new_clause", all("das zu badende Gut" not in row["gdt594_completed_clause_de"] for row in candidates), "49/49")

    check("badegut_rival_exact", all(row["retained_gdt593_badegut_clause_de"] == row["gdt593_previous_clause_de"] and "das zu badende Gut" in row["retained_gdt593_badegut_clause_de"] for row in candidates), "49/49")
    check("gdt569_rival_retained", all(row["retained_gdt569_context_clause_de"] and "denselben Stationsposten" in row["retained_gdt569_context_clause_de"] for row in candidates), "49/49")
    check("body_alternative_channel", all((row["retained_body_alternative_de"] == "SELECTED_PRIMARY") == (row["gdt594_object_class"] == "BODY") for row in candidates), "49/49")
    check("station_alternative_channel", all((row["retained_station_alternative_de"] == "SELECTED_PRIMARY") == (row["gdt594_object_class"] == "STATION") for row in candidates), "49/49")
    check("flow_alternative_channel", all((row["retained_flow_alternative_de"] == "SELECTED_PRIMARY") == (row["gdt594_object_class"] == "FLOW") for row in candidates), "49/49")
    check("reader_occurrences_resolved", all(int(row["reader_clause_occurrence_index"]) >= 1 for row in candidates), "49/49")

    check("manual_two_way_set", {row["target_event_id"] for row in candidates if row["manual_reader_disposition"] == "READABLE_TWO_WAY"} == MANUAL_TWO_WAY, sorted(MANUAL_TWO_WAY))
    check("manual_flow_set", {row["target_event_id"] for row in candidates if row["manual_reader_disposition"] == "FLOW_MUST_BE_READ_OPERATIONALLY"} == MANUAL_FLOW_OPERATIONAL, sorted(MANUAL_FLOW_OPERATIONAL))
    check("manual_fragmented_set", {row["target_event_id"] for row in candidates if row["manual_reader_disposition"] == "SURROUNDING_CONTROL_PROSE_FRAGMENTED"} == MANUAL_FRAGMENTED_CONTROL, sorted(MANUAL_FRAGMENTED_CONTROL))

    changed_actions = [row for row in actions if row["gdt594_clause_changed"] == "YES"]
    retained_actions = [row for row in actions if row["gdt594_clause_changed"] == "NO"]
    output_changed_statements = [row for row in statements if row["gdt594_reader_changed"] == "YES"]
    retained_statements = [row for row in statements if row["gdt594_reader_changed"] == "NO"]
    check("changed_actions", len(changed_actions) == 49, len(changed_actions))
    check("retained_actions", len(retained_actions) == 205, len(retained_actions))
    check("changed_statements", len(output_changed_statements) == 49, len(output_changed_statements))
    check("retained_statements", len(retained_statements) == 744, len(retained_statements))
    check("changed_action_target_parity", {row["source_event_id"] for row in changed_actions} == target_ids, "49 exact")
    check("changed_statement_target_parity", {row["statement_id"] for row in output_changed_statements} == {row["target_statement_id"] for row in candidates}, "49 exact")
    check("changed_statement_file_parity", {row["statement_id"] for row in changed_statements} == {row["statement_id"] for row in output_changed_statements}, "49 exact")
    check("changed_statements_single_patch", all(row["gdt594_y_completion_count"] == "1" for row in output_changed_statements), "49/49")
    target_statement_ids = {row["target_statement_id"] for row in candidates}
    candidate_statement_action_counts = Counter(
        row["statement_id"] for row in actions if row["statement_id"] in target_statement_ids
    )
    check("three_bath_action_target_statements", {statement for statement, count in candidate_statement_action_counts.items() if count == 3} == {"G407-S122", "G407-S616"}, {statement: count for statement, count in candidate_statement_action_counts.items() if count == 3})
    e3664 = [row for row in actions if row["source_event_id"] == "G407-E3664"]
    e3673 = [row for row in actions if row["source_event_id"] == "G407-E3673"]
    check("e3673_occurrence_safe_patch", len(e3664) == 1 and len(e3673) == 1 and e3664[0]["gdt594_clause_changed"] == "NO" and e3664[0]["gdt594_completed_clause_de"] == "Halte das zu badende Gut im Bad auf Grad I" and e3673[0]["gdt594_completed_clause_de"] == "Halte denselben Stationsansatz im Bad auf Grad I", {"E3664": e3664[0]["gdt594_completed_clause_de"] if e3664 else "MISSING", "E3673": e3673[0]["gdt594_completed_clause_de"] if e3673 else "MISSING"})

    source_actions = {row["action_slot_id"]: row for row in inputs["gdt593_actions"]}
    source_statements = {row["statement_id"]: row for row in inputs["gdt593_statements"]}
    check("action_order_retained", [row["action_slot_id"] for row in actions] == [row["action_slot_id"] for row in inputs["gdt593_actions"]], "exact")
    check("statement_order_retained", [row["statement_id"] for row in statements] == [row["statement_id"] for row in inputs["gdt593_statements"]], "exact")
    check("retained_action_clauses_byte_equal", all(row["gdt594_completed_clause_de"] == source_actions[row["action_slot_id"]]["gdt593_completed_clause_de"] for row in retained_actions), "205/205")
    check("retained_statement_text_byte_equal", all(row["gdt594_primary_reader_de"] == source_statements[row["statement_id"]]["gdt593_primary_reader_de"] for row in retained_statements), "744/744")

    prior_promotions = [row for row in actions if row["gdt593_clause_changed"] == "YES"]
    check("gdt593_promotions_retained", len(prior_promotions) == 12 and all(row["gdt594_clause_changed"] == "NO" and row["gdt594_completed_clause_de"] == row["gdt593_completed_clause_de"] for row in prior_promotions), "12/12")
    check("old_conflicts_retained", all(row["gdt594_clause_changed"] == "NO" for row in actions if row["source_event_id"] in {"G407-E1719", "G407-E2481"}), "E1719/E2481")
    e3243 = [row for row in actions if row["source_event_id"] == "G407-E3243"]
    check("e3243_two_action_slots", len(e3243) == 2 and len({row["action_slot_id"] for row in e3243}) == 2 and all(row["gdt594_clause_changed"] == "NO" for row in e3243), [row["action_slot_id"] for row in e3243])

    cold = [row for row in actions if row["gdt594_selection_route"] == "COLD_BATH_OBJECT_DEFAULT"]
    cold_profile = Counter((row["gdt569_inherited_argument_root"], row["gdt569_parallel_relation"]) for row in cold)
    check("remaining_cold_defaults", len(cold) == 44, len(cold))
    check("remaining_cold_profile", cold_profile == {("AIIN", "GDT569_CARRY_FILL_PARALLEL"): 17, ("NOT_APPLICABLE", "NO_GDT569_STATE_ROW"): 27}, {"|".join(key): value for key, value in cold_profile.items()})
    check("remaining_specific_candidates_zero", result["remaining_gdt569_specific_candidate_count"] == 0, result["remaining_gdt569_specific_candidate_count"])

    check("result_source_profile", result["source_kind_profile"] == dict(sorted(source_profile.items())), result["source_kind_profile"])
    check("result_scope_profile", result["scope_profile"] == dict(sorted(scope_profile.items())), result["scope_profile"])
    check("result_object_profile", result["completion_object_profile"] == dict(sorted(object_profile.items())), result["completion_object_profile"])
    check("result_final_profile", result["final_object_profile"] == dict(sorted(final_profile.items())), result["final_object_profile"])
    check("result_manual_profile", result["manual_reader_profile"] == dict(sorted(manual_profile.items())), result["manual_reader_profile"])
    check("result_reader_reset_set", set(result["same_statement_reader_reset_event_ids"]) == READER_RESET, result["same_statement_reader_reset_event_ids"])
    check("result_semantic_host_reset_set", set(result["semantic_host_reset_event_ids"]) == SEMANTIC_HOST_RESET, result["semantic_host_reset_event_ids"])
    check("result_host_atom_conflict_set", set(result["host_atom_scope_conflict_event_ids"]) == HOST_ATOM_SCOPE_CONFLICT, result["host_atom_scope_conflict_event_ids"])
    check("result_paragraph_crossing_set", set(result["physical_paragraph_crossing_event_ids"]) == PHYSICAL_PARAGRAPH_CROSSINGS, result["physical_paragraph_crossing_event_ids"])
    check("result_input_hashes", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, "exact")

    for name in (
        "candidates",
        "actions",
        "changed_statements",
        "statements",
        "pages",
        "boundary_cases",
        "scope_conflicts",
    ):
        check(f"byte_rebuild_{name}", OUTPUTS[name].read_bytes() == tsv_bytes(rebuilt[name]), "exact")
    check("byte_rebuild_reader", OUTPUTS["reader"].read_text(encoding="utf-8") == render_reader(rebuilt), "exact")
    check("byte_rebuild_result", result == rebuilt["result"], "exact")

    validation = {
        "experiment_id": "GDT594",
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

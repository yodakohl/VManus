#!/usr/bin/env python3
"""Validate GDT597's six-page population, state cuts, cards, and byte rebuild."""

from __future__ import annotations

import json
from collections import Counter, defaultdict

from model import (
    ACTION_DEFAULTS,
    COMPATIBLE_CLASSES,
    INPUTS,
    OUTPUTS,
    PAGES,
    STATUS,
    build,
    is_cut,
    load_inputs,
    sha256,
    tsv_bytes,
)


EXPECTED_TYPING = {
    "T01_WRITTEN_TYPED_OBJECT": 219,
    "T02_ACTION_INTERNAL_OBJECT": 40,
    "T03_BOUND_COMPATIBLE_REFERENCE": 81,
    "T04_STABLE_CLASS_DEFAULT": 6,
    "T05_WORKPIECE_DEFAULT": 50,
}
EXPECTED_REFERENCE = {
    "Q01_LEFT_COMPATIBLE_ANAPHORIC": 77,
    "Q02_RIGHT_SAME_EVENT_DEFINITE": 4,
    "Q03_LOCAL_OR_DEFAULT_DEFINITE": 315,
}
EXPECTED_RULES = {
    "CHD_BIO_TREAT": 199,
    "S_BIO_DIVERT": 32,
    "S_REST_SELECT": 72,
    "T_AFTER_SH_COOL": 7,
    "T_BIO_RELATION_REGULATE": 1,
    "T_BIO_STATION_REGULATE": 52,
    "T_PHYSICAL_GRADE_TEMPER": 33,
}
EXPECTED_CLASSES = {
    "BODY": 13,
    "BODY_PART": 3,
    "CONDITION": 16,
    "FLOW": 34,
    "MEASURE": 24,
    "PORTION": 19,
    "STATION": 277,
    "UNIT": 10,
}
EXPECTED_PAGES = {"f75r": 60, "f77r": 67, "f81r": 47, "f81v": 53, "f82r": 53, "f83r": 116}
EXPECTED_LONG = {
    "ACTION:G407-E2585@3:T",
    "ACTION:G407-E2765@2:CHD",
    "ACTION:G407-E3147@1:CHD",
    "ACTION:G407-E3159@2:CHD",
    "ACTION:G407-E3200@3:T",
    "ACTION:G407-E3266@2:CHD",
    "ACTION:G407-E3281@2:CHD",
    "ACTION:G407-E3707@1:T",
    "ACTION:G407-E3749@1:S",
}
EXPECTED_RIGHT = {
    "ACTION:G407-E1628@1:S",
    "ACTION:G407-E2755@2:S",
    "ACTION:G407-E3243@1:S",
    "ACTION:G407-E3341@1:S",
}


def main() -> int:
    inputs = load_inputs()
    built = build(inputs)
    replay = built["replay"]
    result = built["result"]
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "observed": observed})
        if not passed:
            raise AssertionError(f"{name}: {observed!r}")

    check("status_exact", result["status"] == STATUS, result["status"])
    check("action_count", len(replay) == 396, len(replay))
    check("unique_governors", len({row["primary_governor_key"] for row in replay}) == 396, len({row["primary_governor_key"] for row in replay}))
    check("unique_action_slots", len({row["action_slot_id"] for row in replay}) == 396, len({row["action_slot_id"] for row in replay}))
    check("ordinal_sequence", [int(row["action_ordinal"]) for row in replay] == list(range(1, 397)), "1..396")
    check("statement_count", len({row["statement_id"] for row in replay}) == 219, len({row["statement_id"] for row in replay}))
    check("page_set", {row["physical_page"] for row in replay} == set(PAGES), sorted({row["physical_page"] for row in replay}))
    check("page_profile", Counter(row["physical_page"] for row in replay) == EXPECTED_PAGES, Counter(row["physical_page"] for row in replay))
    check("no_forbidden_page", all(not row["physical_page"].startswith("f84") for row in replay), "none")
    check("root_profile", Counter(row["action_root"] for row in replay) == {"CHD": 199, "S": 104, "T": 93}, Counter(row["action_root"] for row in replay))
    check("rule_profile", Counter(row["gdt584_rule_id"] for row in replay) == EXPECTED_RULES, Counter(row["gdt584_rule_id"] for row in replay))
    check("written_count", sum(row["written_carrier_count"] != "0" for row in replay) == 219, result["written_action_count"])
    check("carrierless_count", sum(row["written_carrier_count"] == "0" for row in replay) == 177, result["carrierless_action_count"])
    check("written_root_profile", Counter(row["action_root"] for row in replay if row["written_carrier_count"] != "0") == {"CHD": 115, "S": 45, "T": 59}, Counter(row["action_root"] for row in replay if row["written_carrier_count"] != "0"))
    check("carrierless_rule_profile", Counter(row["gdt584_rule_id"] for row in replay if row["written_carrier_count"] == "0") == {"CHD_BIO_TREAT": 84, "S_BIO_DIVERT": 24, "S_REST_SELECT": 35, "T_AFTER_SH_COOL": 1, "T_BIO_RELATION_REGULATE": 1, "T_BIO_STATION_REGULATE": 16, "T_PHYSICAL_GRADE_TEMPER": 16}, Counter(row["gdt584_rule_id"] for row in replay if row["written_carrier_count"] == "0"))

    typing = Counter(row["typing_card_id"] for row in replay)
    reference = Counter(row["reference_scope_card_id"] for row in replay)
    classes = Counter(row["object_class"] for row in replay)
    routes = Counter(row["selection_route"] for row in replay)
    check("typing_card_count", len(built["typing_cards"]) == 5, len(built["typing_cards"]))
    check("typing_profile", typing == EXPECTED_TYPING, typing)
    check("reference_card_count", len(built["reference_cards"]) == 3, len(built["reference_cards"]))
    check("reference_profile", reference == EXPECTED_REFERENCE, reference)
    check("object_class_profile", classes == EXPECTED_CLASSES, classes)
    check("route_profile", routes == {"WRITTEN_GDT589_PACKET": 219, "LEFT_COMPATIBLE_TYPED_SOURCE": 77, "RIGHT_SAME_EVENT_COMPATIBLE_SOURCE": 4, "ACTION_INTERNAL_FLOW_DEFAULT": 24, "ACTION_INTERNAL_CONDITION_DEFAULT": 16, "ACTION_RULE_TYPED_DEFAULT": 56}, routes)
    check("typing_partition", sum(typing.values()) == 396, sum(typing.values()))
    check("reference_partition", sum(reference.values()) == 396, sum(reference.values()))
    check("macro_partition", result["written_action_count"] + result["left_reference_count"] + result["right_reference_count"] + result["action_default_count"] == 396, result)
    check("reference_modes", Counter(row["reference_mode"] for row in replay) == {"ANAPHORIC": 77, "DEFINITE": 319}, Counter(row["reference_mode"] for row in replay))
    check("grammatical_gender_profile", Counter(row["grammatical_gender"] for row in replay) == {"MASCULINE": 322, "FEMININE": 47, "NEUTER": 27}, Counter(row["grammatical_gender"] for row in replay))

    check("all_clauses_nonempty", all(row["gdt597_completed_clause_de"].strip() for row in replay), "396/396")
    check("all_carrierless_np_visible", all(row["rendered_object_np_de"] in row["gdt597_completed_clause_de"] for row in replay if row["written_carrier_count"] == "0"), "177/177")
    check("carrierless_no_generic_chd", all("Behandle den Ansatz" not in row["gdt597_completed_clause_de"] for row in replay if row["written_carrier_count"] == "0"), "none")
    check("carrierless_no_empty_temper", all(not row["gdt597_completed_clause_de"].startswith(("Temperiere auf", "Temperiere in", "Temperiere zur")) for row in replay if row["written_carrier_count"] == "0"), "none")
    check("default_replaceable", all(row["default_is_replaceable"] == "YES" for row in replay), "396/396")
    check("gender_complete", all(row["grammatical_gender"] in {"MASCULINE", "FEMININE", "NEUTER"} for row in replay), "396/396")
    check("determiner_complete", all(row["determiner_de"] for row in replay), "396/396")
    check("determiner_cell_count", len(built["determiner_cells"]) == 6, len(built["determiner_cells"]))
    check("all_determiner_cells_observed", all(row["observed_in_gdt597"] == "YES" for row in built["determiner_cells"]), [(row["reference_mode"], row["grammatical_gender"], row["occurrence_count"]) for row in built["determiner_cells"]])
    check("determiner_cell_population", sum(int(row["occurrence_count"]) for row in built["determiner_cells"]) == 396, sum(int(row["occurrence_count"]) for row in built["determiner_cells"]))
    check("neuter_pair", {(row["reference_mode"], row["determiner_de"], row["occurrence_count"]) for row in built["determiner_cells"] if row["grammatical_gender"] == "NEUTER"} == {("DEFINITE", "das", "24"), ("ANAPHORIC", "dasselbe", "3")}, [(row["reference_mode"], row["determiner_de"], row["occurrence_count"]) for row in built["determiner_cells"] if row["grammatical_gender"] == "NEUTER"])
    check("observed_object_form_count", len(built["object_forms"]) == 18, len(built["object_forms"]))
    check("object_form_population", sum(int(row["occurrence_count"]) for row in built["object_forms"]) == 396, sum(int(row["occurrence_count"]) for row in built["object_forms"]))

    left = [row for row in replay if row["reference_scope_card_id"] == "Q01_LEFT_COMPATIBLE_ANAPHORIC"]
    right = [row for row in replay if row["reference_scope_card_id"] == "Q02_RIGHT_SAME_EVENT_DEFINITE"]
    check("left_count", len(left) == 77, len(left))
    check("left_anaphoric", all(row["reference_mode"] == "ANAPHORIC" and row["rendered_object_np_de"].startswith(("denselben ", "dieselbe ", "dasselbe ")) for row in left), "77/77")
    check("left_distance_range", {int(row["source_distance_hosts"]) for row in left} <= {1, 2, 3, 4}, Counter(row["source_distance_hosts"] for row in left))
    check("right_set", {row["primary_governor_key"] for row in right} == EXPECTED_RIGHT, sorted(row["primary_governor_key"] for row in right))
    check("right_rule", all(row["gdt584_rule_id"] == "S_REST_SELECT" and row["object_class"] in {"BODY", "STATION"} for row in right) and Counter(row["object_class"] for row in right) == {"BODY": 1, "STATION": 3}, Counter(row["object_class"] for row in right))
    check("right_definite", all(row["reference_mode"] == "DEFINITE" for row in right), "2/2")

    host_by_key = {row["primary_governor_key"]: row for row in inputs["hosts"]}
    statement_hosts: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inputs["hosts"]:
        statement_hosts[row["statement_id"]].append(row)
    for rows in statement_hosts.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))
    host_position = {
        row["primary_governor_key"]: (row["statement_id"], index, row)
        for statement_id, rows in statement_hosts.items()
        for index, row in enumerate(rows)
    }
    geometry_ok = True
    cut_ok = True
    for row in left + right:
        target_statement, target_index, target_host = host_position[row["primary_governor_key"]]
        source_statement, source_index, source_host = host_position[row["source_pointer"]]
        geometry_ok &= target_statement == source_statement
        if row in left:
            geometry_ok &= source_index < target_index
            cut_ok &= not any(is_cut(host) for host in statement_hosts[target_statement][source_index + 1:target_index])
        else:
            geometry_ok &= source_index > target_index and source_host["anchor_event_id"] == target_host["anchor_event_id"]
    check("reference_same_statement_geometry", geometry_ok, "81/81")
    check("left_never_crosses_ot_dy", cut_ok, "77/77")
    check("all_reference_sources_named", all(row["source_pointer"] in host_by_key for row in left + right), "81/81")
    check("reference_compatibility", all(row["object_class"] in COMPATIBLE_CLASSES[row["gdt584_rule_id"]] for row in left + right), "81/81")

    carrierless_divert = [row for row in replay if row["gdt584_rule_id"] == "S_BIO_DIVERT" and row["written_carrier_count"] == "0"]
    carrierless_station = [row for row in replay if row["gdt584_rule_id"] == "T_BIO_STATION_REGULATE" and row["written_carrier_count"] == "0"]
    check("divert_internal_flow_24", len(carrierless_divert) == 24 and all(row["object_lemma_de"] == "Strom" and row["selection_route"] == "ACTION_INTERNAL_FLOW_DEFAULT" for row in carrierless_divert), len(carrierless_divert))
    check("station_internal_condition_16", len(carrierless_station) == 16 and all(row["object_lemma_de"] == "Stationsbedingung" and row["selection_route"] == "ACTION_INTERNAL_CONDITION_DEFAULT" for row in carrierless_station), len(carrierless_station))
    replay_by_key = {row["primary_governor_key"]: row for row in replay}
    check("cool_same_event_sh", replay_by_key["ACTION:G407-E3013@4:T"]["source_pointer"] == "ACTION:G407-E3013@2:SH" and replay_by_key["ACTION:G407-E3013@4:T"]["object_lemma_de"] == "Stationsansatz", replay_by_key["ACTION:G407-E3013@4:T"])
    check("relation_same_event_sh", replay_by_key["ACTION:G407-E3488@3:T"]["source_pointer"] == "ACTION:G407-E3488@1:SH" and replay_by_key["ACTION:G407-E3488@3:T"]["object_lemma_de"] == "Stationsansatz", replay_by_key["ACTION:G407-E3488@3:T"])
    check("temper_portion_e1728", replay_by_key["ACTION:G407-E1728@3:T"]["object_lemma_de"] == "Anwendungsportion", replay_by_key["ACTION:G407-E1728@3:T"]["gdt597_completed_clause_de"])
    check("temper_portion_e1740", replay_by_key["ACTION:G407-E1740@2:T"]["object_lemma_de"] == "Anwendungsportion", replay_by_key["ACTION:G407-E1740@2:T"]["gdt597_completed_clause_de"])
    check("e2585_body_blocker", replay_by_key["ACTION:G407-E2585@3:T"]["selection_blocker"] == "NEW_BATCH_MARKER_BLOCKS_BODY_REFERENCE" and replay_by_key["ACTION:G407-E2585@3:T"]["object_lemma_de"] == "Stationsansatz", replay_by_key["ACTION:G407-E2585@3:T"])
    check("e2765_used_portion_blocker", replay_by_key["ACTION:G407-E2765@2:CHD"]["selection_blocker"] == "COMPLETED_APPLICATION_BLOCKS_USED_PORTION_REFERENCE" and replay_by_key["ACTION:G407-E2765@2:CHD"]["object_lemma_de"] == "Stationsansatz", replay_by_key["ACTION:G407-E2765@2:CHD"])
    check("e3147_internal_flow_blocker", replay_by_key["ACTION:G407-E3147@1:CHD"]["selection_blocker"] == "DIVERTED_INTERNAL_FLOW_DOES_NOT_BECOME_TREATMENT_PATIENT" and replay_by_key["ACTION:G407-E3147@1:CHD"]["object_lemma_de"] == "Stationsansatz", replay_by_key["ACTION:G407-E3147@1:CHD"])
    check("e3200_two_measure_barrier", replay_by_key["ACTION:G407-E3200@3:T"]["selection_blocker"] == "TWO_MEASURE_PARAMETERS_BLOCK_FAR_PARTICIPANT_REFERENCE" and replay_by_key["ACTION:G407-E3200@3:T"]["object_lemma_de"] == "Stationsansatz" and replay_by_key["ACTION:G407-E3200@3:T"]["reference_scope_card_id"] == "Q03_LOCAL_OR_DEFAULT_DEFINITE", replay_by_key["ACTION:G407-E3200@3:T"])
    check("e3707_one_measure_skip", replay_by_key["ACTION:G407-E3707@1:T"]["source_pointer"] == "ACTION:G407-E3705@1:OK" and replay_by_key["ACTION:G407-E3707@1:T"]["object_lemma_de"] == "Stationsansatz", replay_by_key["ACTION:G407-E3707@1:T"])
    check("e3749_completed_transfer_blocker", replay_by_key["ACTION:G407-E3749@1:S"]["selection_blocker"] == "COMPLETED_TRANSFER_BLOCKS_OLD_PORTION_SELECTION" and replay_by_key["ACTION:G407-E3749@1:S"]["object_lemma_de"] == "Stationseinheit", replay_by_key["ACTION:G407-E3749@1:S"])

    check("default_card_count", len(built["default_cards"]) == 7, len(built["default_cards"]))
    check("compatibility_card_count", len(built["compatibility_cards"]) == 7, len(built["compatibility_cards"]))
    check("all_rules_have_default", {row["gdt584_rule_id"] for row in built["default_cards"]} == set(ACTION_DEFAULTS), sorted(row["gdt584_rule_id"] for row in built["default_cards"]))
    check("all_rules_have_compatibility", {row["gdt584_rule_id"] for row in built["compatibility_cards"]} == set(COMPATIBLE_CLASSES), sorted(row["gdt584_rule_id"] for row in built["compatibility_cards"]))
    check("long_reference_set", {row["primary_governor_key"] for row in built["long_references"]} == EXPECTED_LONG, sorted(row["primary_governor_key"] for row in built["long_references"]))
    check("rejected_candidate_count", len(built["rejected_candidates"]) == 11, len(built["rejected_candidates"]))
    check("six_condition_measure_skips", sum(row["reason"] == "INCOMPATIBLE_WITH_ACTION_RULE" for row in built["rejected_candidates"]) == 6, Counter(row["reason"] for row in built["rejected_candidates"]))
    check("one_new_batch_blocker", sum(row["reason"] == "NEW_BATCH_MARKER_BLOCKS_BODY_REFERENCE" for row in built["rejected_candidates"]) == 1, Counter(row["reason"] for row in built["rejected_candidates"]))
    check("four_manual_scope_barriers", Counter(row["reason"] for row in built["rejected_candidates"])["COMPLETED_APPLICATION_BLOCKS_USED_PORTION_REFERENCE"] == 1 and Counter(row["reason"] for row in built["rejected_candidates"])["DIVERTED_INTERNAL_FLOW_DOES_NOT_BECOME_TREATMENT_PATIENT"] == 1 and Counter(row["reason"] for row in built["rejected_candidates"])["TWO_MEASURE_PARAMETERS_BLOCK_FAR_PARTICIPANT_REFERENCE"] == 1 and Counter(row["reason"] for row in built["rejected_candidates"])["COMPLETED_TRANSFER_BLOCKS_OLD_PORTION_SELECTION"] == 1, Counter(row["reason"] for row in built["rejected_candidates"]))
    check("manual_workshop_review_count", len(built["workshop_reviews"]) == 17, len(built["workshop_reviews"]))
    check("manual_workshop_unique_targets", len({row["primary_governor_key"] for row in built["workshop_reviews"]}) == 17, len({row["primary_governor_key"] for row in built["workshop_reviews"]}))
    check("manual_workshop_class_profile", Counter(row["review_class"] for row in built["workshop_reviews"]) == {"OBJECT_RIVAL": 4, "SCOPE_BLOCKER": 4, "SAME_EVENT_BINDING": 2, "PATIENT_COMPATIBILITY": 1, "PARAMETER_SKIP": 3, "PARAMETER_BARRIER": 1, "OBJECT_SCOPE_RIVAL": 1, "FLOW_EXCEPTION": 1}, Counter(row["review_class"] for row in built["workshop_reviews"]))

    check("page_artifact_count", len(built["pages"]) == 6, len(built["pages"]))
    check("page_artifact_sum", sum(int(row["action_count"]) for row in built["pages"]) == 396, sum(int(row["action_count"]) for row in built["pages"]))
    check("result_profiles", result["typing_card_profile"] == EXPECTED_TYPING and result["reference_scope_card_profile"] == EXPECTED_REFERENCE and result["object_class_profile"] == EXPECTED_CLASSES, result)
    check("guard_host_count", result["guard_stats"]["gdt584_hosts"] == {"selected": 2272, "skipped_forbidden": 0, "skipped_not_allowed": 4017}, result["guard_stats"]["gdt584_hosts"])
    check("guard_slot_count", result["guard_stats"]["gdt582_slots"] == {"selected": 4924, "skipped_forbidden": 0, "skipped_not_allowed": 10965}, result["guard_stats"]["gdt582_slots"])
    check("guard_g587_count", result["guard_stats"]["gdt587_hosts"] == {"selected": 1669, "skipped_forbidden": 0, "skipped_not_allowed": 3616}, result["guard_stats"]["gdt587_hosts"])
    check("guard_g589_count", result["guard_stats"]["gdt589_hosts"] == {"selected": 330, "skipped_forbidden": 0, "skipped_not_allowed": 623}, result["guard_stats"]["gdt589_hosts"])
    check("input_hashes", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, result["input_sha256"])

    for name in ("typing_cards", "reference_cards", "default_cards", "compatibility_cards", "determiner_cells", "object_forms", "replay", "pages", "long_references", "rejected_candidates", "workshop_reviews"):
        check(f"byte_rebuild_{name}", OUTPUTS[name].read_bytes() == tsv_bytes(built[name]), "exact")
    check("byte_rebuild_phrasebook", OUTPUTS["phrasebook"].read_text(encoding="utf-8") == built["phrasebook"], "exact")
    check("byte_rebuild_result", json.loads(OUTPUTS["result"].read_text(encoding="utf-8")) == result, "exact")
    public_bytes = b"".join(
        OUTPUTS[name].read_bytes() for name in ("typing_cards", "reference_cards", "default_cards", "compatibility_cards", "determiner_cells", "object_forms", "replay", "pages", "long_references", "rejected_candidates", "workshop_reviews", "phrasebook", "result")
    )
    local_path_prefix = b"/" + b"home" + b"/"
    check("no_absolute_local_path", local_path_prefix not in public_bytes, "none")

    validation = {
        "experiment_id": "GDT597",
        "status": "PASS",
        "experiment_status": STATUS,
        "check_count": len(checks),
        "passed_count": sum(row["passed"] for row in checks),
        "failed_count": sum(not row["passed"] for row in checks),
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

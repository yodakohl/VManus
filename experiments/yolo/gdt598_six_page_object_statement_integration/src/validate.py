#!/usr/bin/env python3
"""Validate GDT598 population, exact patching, statement composition, and rebuild."""

from __future__ import annotations

import json
from collections import Counter

from model import (
    ACTION_ROOTS,
    INPUTS,
    OUTPUTS,
    PAGES,
    STATUS,
    build,
    load_inputs,
    sha256,
    tsv_bytes,
)


EXPECTED_ACTION_ROOTS = {
    "CH": 196, "CHD": 199, "K": 159, "OK": 285, "P": 55,
    "R": 52, "S": 104, "SH": 300, "T": 93,
}
EXPECTED_COMPLETED_ROOTS = {"CHD": 199, "S": 104, "SH": 254, "T": 93}
EXPECTED_GAP_ROOTS = {"CH": 196, "K": 159, "OK": 285, "P": 55, "R": 52, "SH": 46}
EXPECTED_CLASSES = {
    "BODY": 113, "BODY_PART": 3, "CONDITION": 16, "FLOW": 36,
    "MEASURE": 24, "PORTION": 34, "STATION": 399, "UNIT": 25,
}
EXPECTED_PAGES = {
    "f75r": (64, 439, 288, 121, 167),
    "f77r": (55, 395, 235, 114, 121),
    "f81r": (37, 280, 144, 73, 71),
    "f81v": (43, 326, 208, 86, 122),
    "f82r": (46, 357, 240, 93, 147),
    "f83r": (68, 475, 328, 163, 165),
}


def main() -> int:
    inputs = load_inputs()
    built = build(inputs)
    hosts = built["host_edition"]
    completed = built["completed_actions"]
    gaps = built["gaps"]
    statements = built["statements"]
    result = built["result"]
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "observed": observed})
        if not passed:
            raise AssertionError(f"{name}: {observed!r}")

    check("status_exact", result["status"] == STATUS, result["status"])
    check("page_set", {row["physical_page"] for row in hosts} == set(PAGES), sorted({row["physical_page"] for row in hosts}))
    check("no_forbidden_page", all(not row["physical_page"].startswith("f84") for row in hosts), "none")
    check("host_count", len(hosts) == 2272, len(hosts))
    check("host_ordinals_unique", len({row["host_ordinal_global"] for row in hosts}) == 2272, len({row["host_ordinal_global"] for row in hosts}))
    check("host_order", [int(row["host_ordinal_global"]) for row in hosts] == sorted(int(row["host_ordinal_global"]) for row in hosts), "ascending")
    check("statement_count", len(statements) == 313, len(statements))
    check("statement_ids_unique", len({row["statement_id"] for row in statements}) == 313, len({row["statement_id"] for row in statements}))
    action_hosts = [row for row in hosts if row["action_root"] in ACTION_ROOTS]
    non_action_hosts = [row for row in hosts if row["action_root"] not in ACTION_ROOTS]
    check("action_count", len(action_hosts) == 1443, len(action_hosts))
    check("action_slot_unique", len({row["action_slot_id"] for row in action_hosts}) == 1443, len({row["action_slot_id"] for row in action_hosts}))
    check("action_governor_unique", len({row["primary_governor_key"] for row in action_hosts}) == 1443, len({row["primary_governor_key"] for row in action_hosts}))
    check("action_root_profile", Counter(row["action_root"] for row in action_hosts) == EXPECTED_ACTION_ROOTS, Counter(row["action_root"] for row in action_hosts))
    check("non_action_count", len(non_action_hosts) == 829, len(non_action_hosts))
    check("non_action_profile", Counter(row["action_root"] for row in non_action_hosts) == {"CONTROL": 676, "FRAME": 153}, Counter(row["action_root"] for row in non_action_hosts))

    check("completed_count", len(completed) == 650, len(completed))
    check("gap_count", len(gaps) == 793, len(gaps))
    check("action_partition", len(completed) + len(gaps) == len(action_hosts), (len(completed), len(gaps)))
    completed_keys = {row["primary_governor_key"] for row in completed}
    gap_keys = {row["primary_governor_key"] for row in gaps}
    check("completion_gap_disjoint", not completed_keys & gap_keys, len(completed_keys & gap_keys))
    check("completion_root_profile", Counter(row["action_root"] for row in completed) == EXPECTED_COMPLETED_ROOTS, Counter(row["action_root"] for row in completed))
    check("gap_root_profile", Counter(row["action_root"] for row in gaps) == EXPECTED_GAP_ROOTS, Counter(row["action_root"] for row in gaps))
    check("completion_layer_profile", Counter(row["completion_layer"] for row in completed) == {"GDT596_SH_OBJECT_PHRASEBOOK": 254, "GDT597_NONSH_OBJECT_PHRASEBOOK": 396}, Counter(row["completion_layer"] for row in completed))
    check("completion_class_profile", Counter(row["object_class"] for row in completed) == EXPECTED_CLASSES, Counter(row["object_class"] for row in completed))
    check("all_completed_objects_named", all(row["object_lemma_de"] not in {"", "UNRESOLVED"} and row["rendered_object_np_de"] not in {"", "UNRESOLVED"} for row in completed), "650/650")
    check("all_completed_clauses_nonempty", all(row["gdt598_integrated_clause_de"].strip() for row in completed), "650/650")
    check("all_gaps_explicit", all(row["gap_route"] in {"WRITTEN_PARTICIPANT_PACKET_AVAILABLE", "AIIN_ONLY_PARAMETER__OBJECT_STILL_NEEDED", "CARRIERLESS_DEFAULT_OR_REFERENCE_NEEDED"} for row in gaps), "793/793")
    check("gap_route_profile", Counter(row["gap_route"] for row in gaps) == {"WRITTEN_PARTICIPANT_PACKET_AVAILABLE": 298, "AIIN_ONLY_PARAMETER__OBJECT_STILL_NEEDED": 46, "CARRIERLESS_DEFAULT_OR_REFERENCE_NEEDED": 449}, Counter(row["gap_route"] for row in gaps))
    check("written_gap_slot_count", sum(int(row["written_carrier_count"]) for row in gaps) == 410, sum(int(row["written_carrier_count"]) for row in gaps))
    check("written_gap_slot_distribution", Counter(row["written_carrier_count"] for row in gaps) == {"0": 449, "1": 295, "2": 39, "3": 4, "4": 5, "5": 1}, Counter(row["written_carrier_count"] for row in gaps))
    check("gap_profile_count", len(built["gap_profiles"]) == 7, len(built["gap_profiles"]))
    check("gap_profile_sum", sum(int(row["gap_count"]) for row in built["gap_profiles"]) == 793, sum(int(row["gap_count"]) for row in built["gap_profiles"]))
    check("nonbath_sh_split", Counter(row["gdt584_rule_id"] for row in gaps if row["action_root"] == "SH") == {"SH_REST_HOLD": 44, "SH_CH_BRIDGE_HOLD": 2}, Counter(row["gdt584_rule_id"] for row in gaps if row["action_root"] == "SH"))

    bath_by_key = {
        f"ACTION:{row['action_slot_id'].removeprefix('RUNNING:')}:SH": row
        for row in inputs["baths"]
    }
    nonsh_by_key = {row["primary_governor_key"]: row for row in inputs["nonsh"]}
    host_by_key = {row["primary_governor_key"]: row for row in action_hosts}
    check("gdt596_key_join", set(bath_by_key) <= set(host_by_key) and len(bath_by_key) == 254, len(bath_by_key))
    check("gdt597_key_join", set(nonsh_by_key) <= set(host_by_key) and len(nonsh_by_key) == 396, len(nonsh_by_key))
    check("source_layers_disjoint", not set(bath_by_key) & set(nonsh_by_key), len(set(bath_by_key) & set(nonsh_by_key)))
    check("gdt596_clause_exact", all(host_by_key[key]["gdt598_integrated_clause_de"] == row["gdt596_reconstructed_clause_de"] for key, row in bath_by_key.items()), "254/254")
    check("gdt597_clause_exact", all(host_by_key[key]["gdt598_integrated_clause_de"] == row["gdt597_completed_clause_de"] for key, row in nonsh_by_key.items()), "396/396")
    check("unpatched_hosts_upstream_exact", all(row["gdt598_integrated_clause_de"] == row["gdt584_upstream_clause_de"] for row in hosts if row["integration_status"] != "COMPLETED_OBJECT_ACTION"), "1622/1622")
    check("changed_host_count", sum(row["clause_changed"] == "YES" for row in hosts) == 420, sum(row["clause_changed"] == "YES" for row in hosts))
    changed_layer_profile = Counter(
        f"{row['completion_layer']}|{row['clause_changed']}" for row in completed
    )
    check("changed_layer_profile", changed_layer_profile == {"GDT596_SH_OBJECT_PHRASEBOOK|YES": 218, "GDT596_SH_OBJECT_PHRASEBOOK|NO": 36, "GDT597_NONSH_OBJECT_PHRASEBOOK|YES": 202, "GDT597_NONSH_OBJECT_PHRASEBOOK|NO": 194}, changed_layer_profile)

    check("statement_host_sum", sum(int(row["host_count"]) for row in statements) == 2272, sum(int(row["host_count"]) for row in statements))
    check("statement_action_sum", sum(int(row["action_count"]) for row in statements) == 1443, sum(int(row["action_count"]) for row in statements))
    check("statement_completed_sum", sum(int(row["completed_object_action_count"]) for row in statements) == 650, sum(int(row["completed_object_action_count"]) for row in statements))
    check("statement_gap_sum", sum(int(row["remaining_action_gap_count"]) for row in statements) == 793, sum(int(row["remaining_action_gap_count"]) for row in statements))
    check("statement_coverage_profile", Counter(row["coverage_state"] for row in statements) == {"ALL_ACTIONS_OBJECT_COMPLETE": 71, "MIXED_COMPLETED_AND_GAP_ACTIONS": 229, "GAP_ONLY_ACTIONS": 13}, Counter(row["coverage_state"] for row in statements))
    check("completed_layer_statement_count", sum(int(row["completed_object_action_count"]) > 0 for row in statements) == 300, sum(int(row["completed_object_action_count"]) > 0 for row in statements))
    check("changed_statement_count", sum(int(row["changed_host_count"]) > 0 for row in statements) == 258, sum(int(row["changed_host_count"]) > 0 for row in statements))
    check("changed_host_statement_sum", sum(int(row["changed_host_count"]) for row in statements) == 420, sum(int(row["changed_host_count"]) for row in statements))
    check("paragraph_structure_preserved", all(row["paragraph_count_preserved"] == "YES" for row in statements), "313/313")
    check("statement_readers_nonempty", all(row["gdt598_integrated_reader_de"].strip() for row in statements), "313/313")

    check("completed_event_count", result["completed_event_count"] == 610, result["completed_event_count"])
    check("multi_action_event_count", len(built["multi_action_events"]) == 36, len(built["multi_action_events"]))
    check("multi_action_event_size_profile", Counter(row["completed_action_count"] for row in built["multi_action_events"]) == {"2": 33, "3": 2, "4": 1}, Counter(row["completed_action_count"] for row in built["multi_action_events"]))
    check("cross_layer_event_collision_count", sum(row["join_hazard_class"] == "CROSS_LAYER_EVENT_COLLISION" for row in built["multi_action_events"]) == 20, sum(row["join_hazard_class"] == "CROSS_LAYER_EVENT_COLLISION" for row in built["multi_action_events"]))
    check("multi_event_action_excess", sum(int(row["completed_action_count"]) - 1 for row in built["multi_action_events"]) == 40, sum(int(row["completed_action_count"]) - 1 for row in built["multi_action_events"]))
    check("exact_slot_join_guard", all(row["required_join_key"] == "EXACT_ACTION_SLOT_ID__EVENT_ID_IS_NOT_UNIQUE" for row in built["multi_action_events"]), "36/36")
    check("unsafe_string_group_count", len(built["string_hazards"]) == 10, len(built["string_hazards"]))
    check("unsafe_string_action_count", sum(int(row["affected_action_count"]) for row in built["string_hazards"]) == 240, sum(int(row["affected_action_count"]) for row in built["string_hazards"]))
    check("distinct_upstream_clause_count", result["distinct_completed_upstream_clause_count"] == 154, result["distinct_completed_upstream_clause_count"])
    check("exact_slot_string_guard", all(row["required_join_key"] == "EXACT_ACTION_SLOT_ID__CLAUSE_STRING_REPLACEMENT_IS_UNSAFE" for row in built["string_hazards"]), "10/10")

    check("local_card_count", len(built["local_cards"]) == 40, len(built["local_cards"]))
    check("local_card_page_profile", Counter(row["physical_page"] for row in built["local_cards"]) == {"f75r": 10, "f77r": 11, "f81v": 2, "f82r": 13, "f83r": 4}, Counter(row["physical_page"] for row in built["local_cards"]))
    check("local_name_override_hosts", sum(int(row["name_override_count"]) > 0 for row in built["local_cards"]) == 5, sum(int(row["name_override_count"]) > 0 for row in built["local_cards"]))
    check("local_name_override_slots", sum(int(row["name_override_count"]) for row in built["local_cards"]) == 7, sum(int(row["name_override_count"]) for row in built["local_cards"]))
    check("local_running_inheritance_forbidden", all(row["running_statement_link_status"] == "NONE__LOCAL_CARD_GUARD_FORBIDS_RUNNING_SENTENCE_INHERITANCE" and row["integration_route"] == "SEPARATE_LOCAL_APPENDIX__NEVER_INHERIT_INTO_RUNNING_STATEMENT" for row in built["local_cards"]), "40/40")
    check("manual_review_count", len(built["manual_reviews"]) == 40, len(built["manual_reviews"]))
    check("manual_review_layer_profile", Counter(row["source_layer"] for row in built["manual_reviews"]) == {"GDT596_SH_OBJECT_PHRASEBOOK": 23, "GDT597_NONSH_OBJECT_PHRASEBOOK": 17}, Counter(row["source_layer"] for row in built["manual_reviews"]))
    check("manual_review_namespace_unique", len({row["namespaced_review_id"] for row in built["manual_reviews"]}) == 40, len({row["namespaced_review_id"] for row in built["manual_reviews"]}))
    check("native_review_id_collisions", sum(count > 1 for count in Counter(row["native_review_id"] for row in built["manual_reviews"]).values()) == 17, Counter(row["native_review_id"] for row in built["manual_reviews"]))

    check("page_count", len(built["pages"]) == 6, len(built["pages"]))
    page_observed = {
        row["physical_page"]: tuple(int(row[name]) for name in (
            "statement_count", "host_count", "action_count",
            "completed_object_action_count", "remaining_action_gap_count",
        ))
        for row in built["pages"]
    }
    check("page_profiles", page_observed == EXPECTED_PAGES, page_observed)
    check("page_statement_sum", sum(values[0] for values in page_observed.values()) == 313, sum(values[0] for values in page_observed.values()))
    check("page_action_partition", all(values[3] + values[4] == values[2] for values in page_observed.values()), page_observed)

    check("guard_host_count", result["guard_stats"]["gdt584_hosts"] == {"selected": 2272, "skipped_forbidden": 0, "skipped_not_allowed": 4017}, result["guard_stats"]["gdt584_hosts"])
    check("guard_slot_count", result["guard_stats"]["gdt582_slots"] == {"selected": 4924, "skipped_forbidden": 0, "skipped_not_allowed": 10965}, result["guard_stats"]["gdt582_slots"])
    check("guard_local_card_count", result["guard_stats"]["gdt586_local_cards"] == {"selected": 40, "skipped_forbidden": 0, "skipped_not_allowed": 704}, result["guard_stats"]["gdt586_local_cards"])
    check("input_hashes", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, result["input_sha256"])
    check("result_profiles", result["completed_root_profile"] == EXPECTED_COMPLETED_ROOTS and result["remaining_root_profile"] == EXPECTED_GAP_ROOTS and result["completed_object_class_profile"] == EXPECTED_CLASSES, result)

    for name in ("completed_actions", "host_edition", "statements", "gaps", "gap_profiles", "multi_action_events", "string_hazards", "local_cards", "manual_reviews", "pages"):
        check(f"byte_rebuild_{name}", OUTPUTS[name].read_bytes() == tsv_bytes(built[name]), "exact")
    check("byte_rebuild_reader", OUTPUTS["reader"].read_text(encoding="utf-8") == built["reader"], "exact")
    check("byte_rebuild_result", json.loads(OUTPUTS["result"].read_text(encoding="utf-8")) == result, "exact")
    public_bytes = b"".join(
        OUTPUTS[name].read_bytes()
        for name in ("completed_actions", "host_edition", "statements", "gaps", "gap_profiles", "multi_action_events", "string_hazards", "local_cards", "manual_reviews", "pages", "reader", "result")
    )
    local_path_prefix = b"/" + b"home" + b"/"
    check("no_absolute_local_path", local_path_prefix not in public_bytes, "none")

    validation = {
        "experiment_id": "GDT598",
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

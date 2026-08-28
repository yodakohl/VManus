#!/usr/bin/env python3
"""Validate GDT596 factorization, phrase rendering, and byte rebuild."""

from __future__ import annotations

import json
from collections import Counter

from model import INPUTS, OUTPUTS, STATUS, build, load_inputs, sha256, tsv_bytes


EXPECTED_TYPING = {
    "T01_WRITTEN_TYPED_OBJECT": 100,
    "T02_BLOCKER_STATION": 25,
    "T03_BOUND_TYPED_REFERENCE": 74,
    "T04_STABLE_AIN_OR_TYPE": 12,
    "T05_BODY_FIRST_DEFAULT": 43,
}
EXPECTED_REFERENCE = {
    "Q01_LEFT_ANAPHORIC": 70,
    "Q02_RIGHT_OR_TIE_DEFINITE": 9,
    "Q03_LOCAL_OR_DEFAULT_DEFINITE": 175,
}
EXPECTED_OBJECTS = {"BODY": 100, "STATION": 122, "PORTION": 15, "BATH_UNIT": 15, "FLOW": 2}
EXPECTED_MODIFIERS = {
    "M01_FILL": 11,
    "M02_APPLY": 11,
    "M03_GRADE_III": 1,
    "M04_GRADE_II": 61,
    "M05_GRADE_I": 166,
    "M06_FINE": 2,
    "M07_NEW_BATCH": 3,
    "M08_MAIN_SITE": 4,
    "M09_SIDE_SITE": 1,
    "M10_WORK_SITE": 24,
    "M11_END_SITE": 2,
    "M12_TARGET": 12,
    "M13_SOURCE": 8,
    "M14_CONTACT": 31,
    "M15_PATH": 1,
}
EXPECTED_RIVALS = {
    "G407-E2863", "G407-E3224", "G407-E3523",
    "G407-E3533", "G407-E3563", "G407-E3664",
}
EXPECTED_MULTI = {
    "G407-E1433", "G407-E1599", "G407-E1611", "G407-E1648",
    "G407-E1795", "G407-E2476", "G407-E2778",
}
EXPECTED_SECOND = {"G407-E1433", "G407-E1648", "G407-E1795"}


def main() -> int:
    inputs = load_inputs()
    built = build(inputs)
    replay = built["replay"]
    typing_cards = built["typing_cards"]
    reference_cards = built["reference_cards"]
    object_forms = built["object_forms"]
    modifier_cards = built["modifier_cards"]
    modifier_sequences = built["modifier_sequences"]
    workshop_reviews = built["workshop_reviews"]
    pages = built["pages"]
    result = built["result"]
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "observed": observed})
        if not passed:
            raise AssertionError(f"{name}: {observed!r}")

    check("status_exact", result["status"] == STATUS, result["status"])
    check("action_count", len(replay) == 254, len(replay))
    check("unique_action_slots", len({row["action_slot_id"] for row in replay}) == 254, len({row["action_slot_id"] for row in replay}))
    check("unique_source_events", len({row["source_event_id"] for row in replay}) == 253, len({row["source_event_id"] for row in replay}))
    check("statement_population", len({row["statement_id"] for row in replay}) == 177, len({row["statement_id"] for row in replay}))
    check("ordinal_sequence", [int(row["bath_action_ordinal"]) for row in replay] == list(range(1, 255)), "1..254")
    check("page_count", len(pages) == 6, len(pages))
    check("page_set", {row["physical_page"] for row in pages} == {"f75r", "f77r", "f81r", "f81v", "f82r", "f83r"}, sorted(row["physical_page"] for row in pages))
    check("all_typing_cards_on_all_pages", all(len(row["typing_card_profile"].split("|")) == 5 for row in pages), [row["typing_card_profile"] for row in pages])
    check("right_scope_on_five_pages", sum("Q02_RIGHT_OR_TIE_DEFINITE" in row["reference_scope_profile"] for row in pages) == 5, [row["physical_page"] for row in pages if "Q02_RIGHT_OR_TIE_DEFINITE" in row["reference_scope_profile"]])
    check("no_f84", all(not row["physical_page"].lower().startswith("f84") for row in replay), "none")

    typing_profile = Counter(row["typing_card_id"] for row in replay)
    reference_profile = Counter(row["reference_scope_card_id"] for row in replay)
    object_profile = Counter(row["object_class"] for row in replay)
    check("typing_card_count", len(typing_cards) == 5, len(typing_cards))
    check("typing_profile", typing_profile == EXPECTED_TYPING, dict(typing_profile))
    check("reference_card_count", len(reference_cards) == 3, len(reference_cards))
    check("reference_profile", reference_profile == EXPECTED_REFERENCE, dict(reference_profile))
    check("object_profile", object_profile == EXPECTED_OBJECTS, dict(object_profile))
    check("typing_partition", sum(typing_profile.values()) == 254, sum(typing_profile.values()))
    check("reference_partition", sum(reference_profile.values()) == 254, sum(reference_profile.values()))

    expected_typing_classes = {
        "T01_WRITTEN_TYPED_OBJECT": {"BODY": 52, "STATION": 40, "BATH_UNIT": 6, "PORTION": 2},
        "T02_BLOCKER_STATION": {"STATION": 25},
        "T03_BOUND_TYPED_REFERENCE": {"STATION": 57, "BODY": 5, "PORTION": 5, "BATH_UNIT": 5, "FLOW": 2},
        "T04_STABLE_AIN_OR_TYPE": {"PORTION": 8, "BATH_UNIT": 4},
        "T05_BODY_FIRST_DEFAULT": {"BODY": 43},
    }
    for card_id, expected in expected_typing_classes.items():
        observed = Counter(row["object_class"] for row in replay if row["typing_card_id"] == card_id)
        check(f"class_profile_{card_id}", observed == expected, dict(observed))

    expected_reference_classes = {
        "Q01_LEFT_ANAPHORIC": {"STATION": 50, "PORTION": 8, "BATH_UNIT": 7, "BODY": 3, "FLOW": 2},
        "Q02_RIGHT_OR_TIE_DEFINITE": {"STATION": 7, "BODY": 2},
        "Q03_LOCAL_OR_DEFAULT_DEFINITE": {"BODY": 95, "STATION": 65, "BATH_UNIT": 8, "PORTION": 7},
    }
    for card_id, expected in expected_reference_classes.items():
        observed = Counter(row["object_class"] for row in replay if row["reference_scope_card_id"] == card_id)
        check(f"reference_class_profile_{card_id}", observed == expected, dict(observed))

    cross = Counter((row["typing_card_id"], row["reference_scope_card_id"]) for row in replay)
    expected_cross = {
        ("T01_WRITTEN_TYPED_OBJECT", "Q03_LOCAL_OR_DEFAULT_DEFINITE"): 100,
        ("T02_BLOCKER_STATION", "Q03_LOCAL_OR_DEFAULT_DEFINITE"): 25,
        ("T03_BOUND_TYPED_REFERENCE", "Q01_LEFT_ANAPHORIC"): 65,
        ("T03_BOUND_TYPED_REFERENCE", "Q02_RIGHT_OR_TIE_DEFINITE"): 9,
        ("T04_STABLE_AIN_OR_TYPE", "Q01_LEFT_ANAPHORIC"): 5,
        ("T04_STABLE_AIN_OR_TYPE", "Q03_LOCAL_OR_DEFAULT_DEFINITE"): 7,
        ("T05_BODY_FIRST_DEFAULT", "Q03_LOCAL_OR_DEFAULT_DEFINITE"): 43,
    }
    check("typing_reference_cross", cross == expected_cross, {"|".join(key): value for key, value in cross.items()})
    check("occupied_cross_cells", len(cross) == 7, len(cross))

    written_y = [row for row in replay if row["upstream_selection_route"] == "WRITTEN_Y_GDT590"]
    check("written_y_count", len(written_y) == 92, len(written_y))
    check("written_y_clean_body", sum(row["typing_token"] == "Y_CLEAR_BODY" and row["object_class"] == "BODY" for row in written_y) == 52, Counter(row["typing_token"] for row in written_y))
    check("written_y_blocked_station", sum(row["typing_token"] == "Y_BLOCKED_STATION" and row["object_class"] == "STATION" for row in written_y) == 40, Counter(row["typing_token"] for row in written_y))
    written_or = [row for row in replay if row["upstream_selection_route"] == "WRITTEN_OR_UNIT"]
    written_ain = [row for row in replay if row["upstream_selection_route"] == "WRITTEN_AIN_PORTION"]
    check("written_or_unit", len(written_or) == 6 and all(row["object_class"] == "BATH_UNIT" for row in written_or), len(written_or))
    check("written_ain_portion", len(written_ain) == 2 and all(row["object_class"] == "PORTION" for row in written_ain), len(written_ain))
    blocker = [row for row in replay if row["typing_card_id"] == "T02_BLOCKER_STATION"]
    check("blocker_station_only", all(row["object_class"] == "STATION" and row["typing_token"] == "BLOCKER_STATION" for row in blocker), "25/25")
    check("body_default_only", all(row["object_class"] == "BODY" and row["typing_token"] == "BODY_FIRST_DEFAULT" for row in replay if row["typing_card_id"] == "T05_BODY_FIRST_DEFAULT"), "43/43")

    anaphoric = [row for row in replay if row["reference_mode"] == "ANAPHORIC"]
    definite = [row for row in replay if row["reference_mode"] == "DEFINITE"]
    check("reference_mode_profile", Counter(row["reference_mode"] for row in replay) == {"ANAPHORIC": 70, "DEFINITE": 184}, Counter(row["reference_mode"] for row in replay))
    check("anaphoric_forms", all(row["rendered_object_np_de"].startswith(("dieselbe ", "denselben ")) for row in anaphoric), "70/70")
    check("definite_forms", all(row["rendered_object_np_de"].startswith(("die ", "den ")) for row in definite), "184/184")
    check("left_is_anaphoric", all(row["reference_mode"] == "ANAPHORIC" for row in replay if row["reference_scope_card_id"] == "Q01_LEFT_ANAPHORIC"), "70/70")
    check("right_or_tie_is_definite", all(row["reference_mode"] == "DEFINITE" for row in replay if row["reference_scope_card_id"] == "Q02_RIGHT_OR_TIE_DEFINITE"), "9/9")
    check("right_eight_plus_tie", Counter(row["upstream_selection_route"] for row in replay if row["reference_scope_card_id"] == "Q02_RIGHT_OR_TIE_DEFINITE") == {"SAME_EVENT_RIGHTWARD_SHARED_COMPLEMENT": 8, "STATION_PORTION_PACKET_RIGHT_STATION_TIEBREAK": 1}, "8+1")
    check("left_sources_named", all(row["scope_source_pointer"] not in {"DEFAULT:BODY", ""} for row in replay if row["reference_scope_card_id"] == "Q01_LEFT_ANAPHORIC"), "70/70")

    check("object_form_card_count", len(object_forms) == 11, len(object_forms))
    check("lemma_count", len({row["object_lemma_de"] for row in replay}) == 7, sorted({row["object_lemma_de"] for row in replay}))
    expected_forms = {
        "den Körper": 97,
        "denselben Körper": 3,
        "den Stationsansatz": 72,
        "denselben Stationsansatz": 50,
        "die Anwendungsportion": 7,
        "dieselbe Anwendungsportion": 8,
        "die Badeinheit": 8,
        "dieselbe Badeinheit": 1,
        "dieselbe Becken- oder Körpereinheit": 2,
        "dieselbe Stationseinheit": 4,
        "denselben Strom": 2,
    }
    check("object_form_profile", Counter(row["rendered_object_np_de"] for row in replay) == expected_forms, Counter(row["rendered_object_np_de"] for row in replay))
    check("selected_np_exact", all(row["rendered_object_np_de"] in row["gdt596_reconstructed_clause_de"] for row in replay), "254/254")
    check("fill_never_object_class", all(row["object_class"] != "FILL" and "Füllung" not in row["object_lemma_de"] for row in replay), "254/254")

    check("participant_profile", Counter(row["participant_count"] for row in replay) == {"1": 247, "2": 6, "3": 1}, Counter(row["participant_count"] for row in replay))
    check("multi_participant_set", {row["source_event_id"] for row in replay if int(row["participant_count"]) > 1} == EXPECTED_MULTI, sorted(row["source_event_id"] for row in replay if int(row["participant_count"]) > 1))
    check("selected_position_profile", Counter(row["selected_participant_position"] for row in replay) == {"1": 251, "2": 3}, Counter(row["selected_participant_position"] for row in replay))
    check("selected_second_set", {row["source_event_id"] for row in replay if row["selected_participant_position"] == "2"} == EXPECTED_SECOND, sorted(row["source_event_id"] for row in replay if row["selected_participant_position"] == "2"))
    check("participant_order_replayed", all(row["exact_replay"] == "YES" for row in replay), "254/254")

    check("bath_frame_profile", Counter(row["bath_frame"] for row in replay) == {"BAD": 252, "BADBETRIEB": 2}, Counter(row["bath_frame"] for row in replay))
    flow_rows = [row for row in replay if row["object_class"] == "FLOW"]
    check("flow_badbetrieb", len(flow_rows) == 2 and all(row["bath_frame"] == "BADBETRIEB" for row in flow_rows), [row["source_event_id"] for row in flow_rows])
    check("badbetrieb_flow_only", all(row["object_class"] == "FLOW" for row in replay if row["bath_frame"] == "BADBETRIEB"), "2/2")

    check("modifier_card_count", len(modifier_cards) == 15, len(modifier_cards))
    modifier_profile = {row["modifier_card_id"]: int(row["occurrence_count"]) for row in modifier_cards}
    check("modifier_profile", modifier_profile == EXPECTED_MODIFIERS, modifier_profile)
    check("modifier_occurrence_sum", sum(modifier_profile.values()) == 338, sum(modifier_profile.values()))
    check("modifier_sequence_count", len(modifier_sequences) == 40, len(modifier_sequences))
    check("modifier_sequence_population", sum(int(row["occurrence_count"]) for row in modifier_sequences) == 254, sum(int(row["occurrence_count"]) for row in modifier_sequences))
    check("modifier_nonpatient", all(row["patient_selecting"] == "NO" for row in modifier_cards), "15/15")
    check("fill_grade_binding_present", any(row["modifier_id_sequence"].startswith("M01_FILL|M05_GRADE_I") for row in modifier_sequences), "yes")

    check("exact_replay_count", sum(row["exact_replay"] == "YES" for row in replay) == 254, sum(row["exact_replay"] == "YES" for row in replay))
    check("zero_exceptions", not any(row["exact_replay"] != "YES" for row in replay), "0")
    check("clause_byte_equality", all(row["gdt595_clause_de"] == row["gdt596_reconstructed_clause_de"] for row in replay), "254/254")
    check("page_replay_sum", sum(int(row["exact_replay_count"]) for row in pages) == 254, sum(int(row["exact_replay_count"]) for row in pages))
    check("rival_set", {row["source_event_id"] for row in replay if row["host_attachment_rival"] == "YES"} == EXPECTED_RIVALS, sorted(row["source_event_id"] for row in replay if row["host_attachment_rival"] == "YES"))
    check("rival_defaults_survive", all(row["default_survives_with_rival"] == "YES" for row in replay if row["host_attachment_rival"] == "YES"), "6/6")

    check("workshop_review_count", len(workshop_reviews) == 23, len(workshop_reviews))
    check("workshop_review_unique_events", len({row["event_id"] for row in workshop_reviews}) == 23, len({row["event_id"] for row in workshop_reviews}))
    check("workshop_review_classes", Counter(row["review_class"] for row in workshop_reviews) == {"STYLE_SCOPE_ONLY": 16, "OBJECT_RIVAL": 6, "BINDING_MECHANISM_RIVAL": 1}, Counter(row["review_class"] for row in workshop_reviews))
    check("workshop_immediate_forks", {row["event_id"] for row in workshop_reviews if row["immediate_object_fork"] == "YES"} == {"G407-E2952", "G407-E3224"}, sorted(row["event_id"] for row in workshop_reviews if row["immediate_object_fork"] == "YES"))
    check("workshop_binding_fork", {row["event_id"] for row in workshop_reviews if row["review_class"] == "BINDING_MECHANISM_RIVAL"} == {"G407-E3523"}, [row["event_id"] for row in workshop_reviews if row["review_class"] == "BINDING_MECHANISM_RIVAL"])
    check("workshop_current_clause_match", all(row["current_clause_matches_replay"] == "YES" for row in workshop_reviews), "23/23")
    check("workshop_defaults_retained", all(row["default_retained"] == "YES" for row in workshop_reviews), "23/23")
    check("style_cards_no_object_rival", all(row["object_rival_clause_de"] == "NONE" for row in workshop_reviews if row["review_class"] == "STYLE_SCOPE_ONLY"), "16/16")
    check("rival_cards_have_clause", all(row["object_rival_clause_de"] != "NONE" for row in workshop_reviews if row["review_class"] != "STYLE_SCOPE_ONLY"), "7/7")

    check("result_action_count", result["action_count"] == 254, result["action_count"])
    check("result_exact_count", result["exact_replay_count"] == 254, result["exact_replay_count"])
    check("result_exception_count", result["exception_count"] == 0, result["exception_count"])
    check("result_typing_profile", result["typing_card_profile"] == EXPECTED_TYPING, result["typing_card_profile"])
    check("result_macro_operators", result["macro_operator_profile"] == {"D_HOST_DEFAULT": 68, "R_COPY_TYPED_REFERENCE": 74, "T_READ_TYPED_CARRIER_OR_ROOT": 112}, result["macro_operator_profile"])
    check("result_reference_profile", result["reference_scope_card_profile"] == EXPECTED_REFERENCE, result["reference_scope_card_profile"])
    check("result_object_profile", result["object_class_profile"] == EXPECTED_OBJECTS, result["object_class_profile"])
    check("result_reference_modes", result["reference_mode_profile"] == {"ANAPHORIC": 70, "DEFINITE": 184}, result["reference_mode_profile"])
    check("result_primitives", result["phrasebook_primitive_count"] == 39, result["phrasebook_primitive_count"])
    check("result_rivals", set(result["host_attachment_rival_event_ids"]) == EXPECTED_RIVALS, result["host_attachment_rival_event_ids"])
    check("result_workshop_profile", result["workshop_review_class_profile"] == {"BINDING_MECHANISM_RIVAL": 1, "OBJECT_RIVAL": 6, "STYLE_SCOPE_ONLY": 16}, result["workshop_review_class_profile"])
    check("result_immediate_forks", result["immediate_object_fork_count"] == 2, result["immediate_object_fork_count"])
    check("result_workshop_defaults", result["workshop_review_defaults_retained_count"] == 23, result["workshop_review_defaults_retained_count"])
    check("result_input_hashes", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, result["input_sha256"])

    for name in ("typing_cards", "reference_cards", "object_forms", "modifier_cards", "modifier_sequences", "workshop_reviews", "replay", "pages"):
        check(f"byte_rebuild_{name}", OUTPUTS[name].read_bytes() == tsv_bytes(built[name]), "exact")
    check("byte_rebuild_phrasebook", OUTPUTS["phrasebook"].read_text(encoding="utf-8") == built["phrasebook"], "exact")
    check("byte_rebuild_result", json.loads(OUTPUTS["result"].read_text(encoding="utf-8")) == result, "exact")

    validation = {
        "experiment_id": "GDT596",
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

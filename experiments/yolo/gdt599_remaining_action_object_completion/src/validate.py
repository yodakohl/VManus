#!/usr/bin/env python3
"""Validate GDT599 populations, state rules, and byte-reproducible artifacts."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

from model import (
    ACTION_ROOTS,
    COMPATIBLE_CLASSES,
    DETERMINERS,
    GENDER_BY_LEMMA,
    OUTPUTS,
    Q_MARKER,
    Q_MARKER_ACCUSATIVE,
    build,
    is_cut,
    load_inputs,
    tsv_bytes,
)


EXPECTED_ROUTES = {
    "EXACT_CH_TO_SH_BRIDGE": 2,
    "LEFT_COMPATIBLE_AFTER_OT_DY": 207,
    "MANUAL_PATH_FLOW_OVERRIDE": 7,
    "MANUAL_Q_INPUT_ROOT_DEFAULT": 1,
    "MANUAL_Q_UNIT_CONTENT": 1,
    "MANUAL_SAMPLE_FROM_BODY_PART": 1,
    "MANUAL_TRANSIENT_MEASURE_HANDOFF": 1,
    "OWN_AIIN_ONLY_PARAMETER": 46,
    "OWN_WRITTEN_PARTICIPANT": 297,
    "RIGHT_SAME_EVENT_COMPLETED_OR_ROOT_DEFAULT": 21,
    "RIGHT_SAME_EVENT_WRITTEN_PARTICIPANT": 155,
    "ROOT_DEFAULT": 54,
}

EXPECTED_OBJECTS = {
    "BODY": 31,
    "BODY_PART": 1,
    "CONDITION": 10,
    "FLOW": 13,
    "MEASURE": 47,
    "PORTION": 96,
    "STATION": 573,
    "UNIT": 22,
}


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def main() -> int:
    inputs = load_inputs()
    built = build(inputs)
    result = built["result"]
    replay = built["replay"]
    checks: list[str] = []
    source_host_rows = inputs["hosts"]
    gap_rows = inputs["gaps"]

    require(len(replay) == 793, "793 remaining action slots replayed", checks)
    require(len(built["actions"]) == 1443, "1443 complete action hosts", checks)
    require(len(built["hosts"]) == 2272, "2272 complete statement hosts", checks)
    require(
        len({row["host_ordinal_global"] for row in source_host_rows}) == 2272,
        "2272 source host ordinals are unique",
        checks,
    )
    require(
        len({row["action_slot_id"] for row in gap_rows}) == 793
        and len({row["action_slot_id"] for row in replay}) == 793
        and len({row["action_slot_id"] for row in built["actions"]}) == 1443,
        "gap, replay, and complete-action slot identities are unique",
        checks,
    )
    require(
        {row["action_slot_id"] for row in gap_rows}
        == {row["action_slot_id"] for row in replay},
        "replay covers exactly the 793 GDT598 gap slots",
        checks,
    )
    gap_packet_profile = Counter(
        "CARRIERLESS"
        if row["written_carrier_roots"] == "NONE"
        else "AIIN_ONLY"
        if set(row["written_carrier_roots"].split("+")) == {"AIIN"}
        else "PARTICIPANT_PACKET"
        for row in gap_rows
    )
    require(
        gap_packet_profile
        == Counter({"CARRIERLESS": 449, "PARTICIPANT_PACKET": 298, "AIIN_ONLY": 46}),
        "GDT598 gap substrate profile remains 449 + 298 + 46",
        checks,
    )
    # OWNER and FRAME governors can legitimately repeat their descriptive key.
    # The global host ordinal is the lossless one-to-one identity of this stream.
    source_hosts = {row["host_ordinal_global"]: row for row in source_host_rows}
    require(all(
        row["gdt598_integrated_clause_de"] == source_hosts[row["host_ordinal_global"]]["gdt598_integrated_clause_de"]
        for row in built["hosts"]
    ), "GDT598 source clause column remains byte-identical", checks)
    require(len(built["statements"]) == 313, "313 complete statements", checks)
    require(all(row["coverage_state"] == "ALL_ACTIONS_OBJECT_COMPLETE" for row in built["statements"]), "all statements are object-complete", checks)
    require(all(row["remaining_action_gap_count"] == "0" for row in built["statements"]), "zero statement action gaps", checks)
    require(all(row["paragraph_count_preserved"] == "YES" for row in built["statements"]), "all paragraph boundaries preserved", checks)
    require(
        (
            sum(int(row["host_count"]) for row in built["statements"]),
            sum(int(row["action_count"]) for row in built["statements"]),
            sum(int(row["gdt599_new_completion_count"]) for row in built["statements"]),
        )
        == (2272, 1443, 793),
        "statement populations sum to 2272 hosts, 1443 actions, and 793 new completions",
        checks,
    )
    require(
        (
            sum(int(row["statement_count"]) for row in built["pages"]),
            sum(int(row["action_count"]) for row in built["pages"]),
            sum(int(row["gdt598_retained_complete_count"]) for row in built["pages"]),
            sum(int(row["gdt599_new_complete_count"]) for row in built["pages"]),
        )
        == (313, 1443, 650, 793),
        "six page profiles sum to 313 statements and the 650 + 793 action split",
        checks,
    )
    require(
        sum(int(row["occurrence_count"]) for row in built["typing_cards"]) == 793
        and sum(int(row["occurrence_count"]) for row in built["reference_cards"]) == 793
        and sum(int(row["target_occurrence_count"]) for row in built["defaults"]) == 793
        and sum(int(row["default_used_count"]) for row in built["defaults"]) == 54
        and sum(int(row["reference_occurrence_count"]) for row in built["compatibility"]) == 385,
        "route, reference, default, and compatibility card totals reconcile",
        checks,
    )

    require(Counter(row["selection_route"] for row in replay) == Counter(EXPECTED_ROUTES), "selection route profile exact", checks)
    require(Counter(row["object_class"] for row in replay) == Counter(EXPECTED_OBJECTS), "object class profile exact", checks)
    require(Counter(row["reference_scope_card_id"] for row in replay) == Counter({
        "Q01_LEFT_ANAPHORIC": 210,
        "Q02_RIGHT_DEFINITE": 176,
        "Q03_LOCAL_OR_DEFAULT_DEFINITE": 407,
    }), "reference scope profile exact", checks)
    require(Counter(row["input_role"] for row in replay) == Counter({
        "PARTICIPANT": 736,
        "TRANSIENT_MEASURE_PATIENT": 1,
        "MEASURE_ARGUMENT": 46,
        "CONDITION_PARAMETER": 10,
    }), "participant and parameter roles remain distinct", checks)
    require(
        Counter(row["reference_mode"] for row in replay)
        == Counter({"DEFINITE": 583, "ANAPHORIC": 210}),
        "reference modes reconcile to 583 definite and 210 anaphoric objects",
        checks,
    )
    expected_mode_by_card = {
        "Q01_LEFT_ANAPHORIC": "ANAPHORIC",
        "Q02_RIGHT_DEFINITE": "DEFINITE",
        "Q03_LOCAL_OR_DEFAULT_DEFINITE": "DEFINITE",
    }
    require(
        all(
            row["reference_mode"] == expected_mode_by_card[row["reference_scope_card_id"]]
            for row in replay
        ),
        "every reference card selects its declared reference mode",
        checks,
    )
    require(
        all(row["object_lemma_de"] in GENDER_BY_LEMMA for row in replay),
        "every replay object lemma has an explicit grammatical gender",
        checks,
    )
    require(
        all(
            row["grammatical_gender"] == GENDER_BY_LEMMA[row["object_lemma_de"]]
            and row["determiner_de"]
            == DETERMINERS[(row["reference_mode"], row["grammatical_gender"])]
            and row["rendered_object_np_de"]
            == f"{row['determiner_de']} {row['object_lemma_de']}"
            for row in replay
        ),
        "gender, determiner, and rendered object NP agree on all 793 rows",
        checks,
    )
    require(
        Counter(row["state_commit_channel"] for row in replay)
        == Counter({"PARTICIPANT": 737, "PARAMETER": 56}),
        "state commits retain 737 participant and 56 parameter channels",
        checks,
    )

    control_profile = Counter(
        row["primary_governor_key"].rsplit(":", 1)[-1]
        for row in source_host_rows
        if row["action_root"] == "CONTROL"
    )
    require(
        control_profile == Counter({"OT": 106, "OL": 264, "DY": 306}),
        "control population remains OT 106, OL 264, and DY 306",
        checks,
    )
    statement_sequences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_host_rows:
        statement_sequences[row["statement_id"]].append(row)
    for rows in statement_sequences.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))
    action_positions: dict[str, tuple[str, int, int, dict[str, str]]] = {}
    for statement_id, rows in statement_sequences.items():
        cut_ordinal = 0
        for index, row in enumerate(rows):
            if is_cut(row):
                cut_ordinal += 1
            if row["action_root"] in ACTION_ROOTS:
                action_positions[row["primary_governor_key"]] = (
                    statement_id,
                    index,
                    cut_ordinal,
                    row,
                )
    require(
        len(action_positions) == 1443,
        "all 1443 action governor keys are unique within the host stream",
        checks,
    )
    require(
        Counter(int(row["cut_ordinal_in_statement"]) for row in replay)
        == Counter({0: 656, 1: 111, 2: 20, 3: 6}),
        "replay cut ordinals retain the exact 656/111/20/6 profile",
        checks,
    )
    require(
        all(
            int(row["cut_ordinal_in_statement"])
            == action_positions[row["primary_governor_key"]][2]
            for row in replay
        ),
        "every replay row records its recomputed OT/DY cut ordinal",
        checks,
    )
    action_pointer_rows = [row for row in replay if row["source_pointer"].startswith("ACTION:")]
    pseudo_pointer_rows = [row for row in replay if not row["source_pointer"].startswith("ACTION:")]
    require(
        len(action_pointer_rows) == 729 and len(pseudo_pointer_rows) == 64,
        "source population is 729 action pointers plus 64 local/default pointers",
        checks,
    )
    require(
        all(row["source_pointer"] in action_positions for row in action_pointer_rows),
        "all 729 action source pointers resolve in the fixed host stream",
        checks,
    )
    require(
        all(int(row["source_distance_hosts"]) == 0 for row in pseudo_pointer_rows),
        "all 64 local/default pseudo-sources have zero host distance",
        checks,
    )
    require(
        all(
            action_positions[row["primary_governor_key"]][0]
            == action_positions[row["source_pointer"]][0]
            and action_positions[row["primary_governor_key"]][2]
            == action_positions[row["source_pointer"]][2]
            for row in action_pointer_rows
        ),
        "no action source pointer crosses a statement or OT/DY cut",
        checks,
    )
    require(
        all(
            int(row["source_distance_hosts"])
            == abs(
                action_positions[row["primary_governor_key"]][1]
                - action_positions[row["source_pointer"]][1]
            )
            for row in action_pointer_rows
        ),
        "all action source distances reproduce exactly",
        checks,
    )
    require(
        all(
            action_positions[row["source_pointer"]][1]
            < action_positions[row["primary_governor_key"]][1]
            for row in action_pointer_rows
            if row["reference_scope_card_id"] == "Q01_LEFT_ANAPHORIC"
        )
        and all(
            action_positions[row["source_pointer"]][1]
            > action_positions[row["primary_governor_key"]][1]
            for row in action_pointer_rows
            if row["reference_scope_card_id"] == "Q02_RIGHT_DEFINITE"
        ),
        "Q01 action pointers are strictly left and Q02 action pointers strictly right",
        checks,
    )
    right_event_routes = {
        "RIGHT_SAME_EVENT_WRITTEN_PARTICIPANT",
        "RIGHT_SAME_EVENT_COMPLETED_OR_ROOT_DEFAULT",
    }
    require(
        all(
            action_positions[row["primary_governor_key"]][3]["anchor_event_id"]
            == action_positions[row["source_pointer"]][3]["anchor_event_id"]
            for row in action_pointer_rows
            if row["selection_route"] in right_event_routes
        ),
        "all right-event sources remain inside their target anchor event",
        checks,
    )
    ol_crossing_count = 0
    for row in action_pointer_rows:
        statement_id, target_index, _target_cut, _target_source = action_positions[
            row["primary_governor_key"]
        ]
        source_index = action_positions[row["source_pointer"]][1]
        lower, upper = sorted((target_index, source_index))
        if any(
            candidate["action_root"] == "CONTROL"
            and candidate["primary_governor_key"].endswith(":OL")
            for candidate in statement_sequences[statement_id][lower + 1:upper]
        ):
            ol_crossing_count += 1
    require(
        ol_crossing_count == 39,
        "exactly 39 source pointers continue across non-cutting OL controls",
        checks,
    )
    action_by_key = {row["primary_governor_key"]: row for row in built["actions"]}
    q_transition_by_key = {
        row["primary_governor_key"]: row for row in built["q_transitions"]
    }
    require(
        all(
            (row["object_class"], row["object_lemma_de"])
            in (
                {
                    (
                        action_by_key[row["source_pointer"]]["object_class"],
                        action_by_key[row["source_pointer"]]["object_lemma_de"],
                    )
                }
                | (
                    {("STATION", "Stationsansatz")}
                    if row["source_pointer"] in q_transition_by_key
                    and row["selection_route"] != "EXACT_CH_TO_SH_BRIDGE"
                    else set()
                )
            )
            for row in action_pointer_rows
        ),
        "every action pointer copies its source input or committed Q result object",
        checks,
    )
    reference_typing_cards = {
        "T03_EXACT_CH_SH_BRIDGE",
        "T04_RIGHT_SAME_EVENT_WRITTEN",
        "T05_LEFT_COMPATIBLE_STATE",
        "T06_RIGHT_BOUNDED_COMPLETED_OR_DEFAULT",
    }
    reference_typed_rows = [
        row for row in replay if row["typing_card_id"] in reference_typing_cards
    ]
    require(
        len(reference_typed_rows) == 385
        and all(
            row["object_class"] in COMPATIBLE_CLASSES[row["action_root"]]
            for row in reference_typed_rows
        ),
        "all 385 referenced objects satisfy their target-root compatibility card",
        checks,
    )
    bridge_rows = [
        row for row in replay if row["typing_card_id"] == "T03_EXACT_CH_SH_BRIDGE"
    ]
    require(
        len(bridge_rows) == 2
        and all(
            row["source_distance_hosts"] == "1"
            and action_by_key[row["source_pointer"]]["action_root"] == "CH"
            for row in bridge_rows
        ),
        "both exact SH bridges copy the immediately preceding CH input",
        checks,
    )

    forbidden_values = {"UNRESOLVED", "UNFILLED", "TODO", ""}
    resolved_fields = (
        "selection_route", "source_pointer", "object_class", "object_lemma_de",
        "rendered_object_np_de", "gdt599_completed_clause_de",
    )
    require(
        all(row[field] not in forbidden_values for row in replay for field in resolved_fields),
        "all replay object and clause fields resolved",
        checks,
    )
    require(not any("Halte den Zustand" in row["gdt599_completed_clause_de"] for row in replay), "no generic SH Zustand remains", checks)
    complete_action_fields = (
        "object_class", "object_lemma_de", "rendered_object_np_de", "typing_card_id",
        "reference_scope_card_id", "reference_mode", "gdt599_complete_clause_de",
    )
    complete_action_forbidden = forbidden_values | {"NONE", "NOT_APPLICABLE"}
    require(
        all(
            row[field] not in complete_action_forbidden
            for row in built["actions"]
            for field in complete_action_fields
        ),
        "all 1443 complete-action object and clause fields are resolved",
        checks,
    )
    malformed_clause = re.compile(
        r"  +|\s+,|,\s*,|\b(?:den|die|das|denselben|dieselbe|dasselbe) "
        r"(?:den|die|das|denselben|dieselbe|dasselbe)\b|"
        r"\b(?:TODO|UNFILLED|UNRESOLVED|NOT_APPLICABLE)\b"
    )
    require(
        all(
            row["gdt599_complete_clause_de"] == row["gdt599_complete_clause_de"].strip()
            and malformed_clause.search(row["gdt599_complete_clause_de"]) is None
            and "Halte den Zustand" not in row["gdt599_complete_clause_de"]
            for row in built["actions"]
        ),
        "all complete-action clauses pass the mechanical insertion hygiene scan",
        checks,
    )
    require(
        all(
            row["rendered_object_np_de"] in row["gdt599_completed_clause_de"]
            for row in replay
            if row["written_carrier_count"] == "0"
        ),
        "all 449 carrierless completions visibly render their selected object NP",
        checks,
    )

    aiin = built["aiin_bindings"]
    require(len(aiin) == 46, "46 AIIN-only quantity bindings", checks)
    require(Counter(row["substrate_object_class"] for row in aiin) == Counter({
        "STATION": 38, "PORTION": 4, "NOT_APPLICABLE": 4,
    }), "AIIN substrate profile 38 station + 4 portion + 4 R measures", checks)
    require(sum(row["consecutive_quantity"] == "YES" for row in aiin) == 3, "three consecutive quantities rendered as further amounts", checks)
    require(sum(row["substrate_override_id"] != "NONE" for row in aiin) == 1, "one explicit AIIN substrate override", checks)
    require(all("Stations- oder Badmaß" not in row["quantity_clause_de"] for row in aiin), "abstract AIIN surface removed from all 46 quantity clauses", checks)
    aiin_action_sources = [
        row for row in aiin if row["substrate_source_pointer"].startswith("ACTION:")
    ]
    require(
        len(aiin_action_sources) == 36
        and all(row["substrate_source_pointer"] in action_positions for row in aiin_action_sources),
        "all 36 action-backed AIIN substrate pointers resolve",
        checks,
    )
    require(
        all(
            action_positions[row["primary_governor_key"]][0]
            == action_positions[row["substrate_source_pointer"]][0]
            and action_positions[row["primary_governor_key"]][2]
            == action_positions[row["substrate_source_pointer"]][2]
            for row in aiin_action_sources
        ),
        "no AIIN substrate pointer crosses a statement or OT/DY cut",
        checks,
    )
    require(
        all(
            action_positions[row["substrate_source_pointer"]][1]
            < action_positions[row["primary_governor_key"]][1]
            for row in aiin_action_sources
            if row["substrate_selection_route"] == "LEFT_LIVE_SUBSTRATE"
        )
        and all(
            action_positions[row["substrate_source_pointer"]][1]
            > action_positions[row["primary_governor_key"]][1]
            for row in aiin_action_sources
            if row["substrate_selection_route"].startswith("RIGHT_")
        ),
        "AIIN left and right substrate routes point in their declared direction",
        checks,
    )
    require(
        all(
            action_positions[row["primary_governor_key"]][3]["anchor_event_id"]
            == action_positions[row["substrate_source_pointer"]][3]["anchor_event_id"]
            for row in aiin_action_sources
            if row["substrate_selection_route"] == "RIGHT_SAME_EVENT_WRITTEN_SUBSTRATE"
        ),
        "same-event AIIN substrate routes remain in their anchor event",
        checks,
    )
    require(
        {
            row["primary_governor_key"]
            for row in aiin
            if row["consecutive_quantity"] == "YES"
        }
        == {
            "ACTION:G407-E2601@1:OK",
            "ACTION:G407-E2990@1:OK",
            "ACTION:G407-E3199@1:OK",
        },
        "consecutive-quantity wording occurs only at E2601, E2990, and E3199",
        checks,
    )

    require(len(built["manual_decisions"]) == 11, "eleven explicit workshop decisions", checks)
    require(
        Counter(
            row["manual_override_id"]
            for row in replay
            if row["manual_override_id"] != "NONE"
        )
        == Counter({f"W{index:02d}": 1 for index in range(1, 12)}),
        "manual workshop IDs W01 through W11 occur exactly once",
        checks,
    )
    require(
        {
            row["primary_governor_key"]
            for row in aiin
            if row["substrate_override_id"] == "A01"
        }
        == {"ACTION:G407-E2936@1:OK"},
        "AIIN substrate override A01 applies only to E2936",
        checks,
    )
    require(all(
        int(row["source_distance_hosts"]) == 0
        for row in replay
        if row["manual_override_id"] != "NONE" and not row["source_pointer"].startswith("ACTION:")
    ), "non-action manual pseudo-sources have zero host distance", checks)
    require(len(built["propagation_effects"]) == 3, "three override propagation effects", checks)
    require({row["primary_governor_key"] for row in built["propagation_effects"]} == {
        "ACTION:G407-E2617@1:OK", "ACTION:G407-E2938@1:OK", "ACTION:G407-E3237@1:R",
    }, "propagation effects hit only E2617, E2938, and E3237", checks)

    require(len(built["q_transitions"]) == 24, "24 action Q input-to-result transitions", checks)
    require(sum(row["completion_layer"] == "GDT599_REMAINING_COMPLETION" for row in built["q_transitions"]) == 15, "15 new GDT599 Q transitions", checks)
    require(result["q_circular_right_station_target_count"] == 9, "nine circular right-station targets blocked", checks)
    require(result["q_circular_right_station_unique_source_count"] == 9, "nine unique circular target-source pairs blocked", checks)
    require(result["frame_q_history_transition_count"] == 0, "FRAME-Q never changes action history", checks)
    require(result["action_q_split_result_clause_count"] == 24, "all 24 action-Q clauses split input from result", checks)
    q_keys = {row["primary_governor_key"] for row in built["q_transitions"]}
    action_q_source_keys = {
        row["primary_governor_key"]
        for row in source_host_rows
        if row["action_root"] in ACTION_ROOTS and Q_MARKER in row["gdt598_integrated_clause_de"]
    }
    require(
        q_keys == action_q_source_keys and len(q_keys) == 24,
        "Q transition keys equal the complete fixed action-Q source population",
        checks,
    )
    require(
        all(
            row["result_object_class"] == "STATION"
            and row["result_object_lemma_de"] == "Stationsansatz"
            and row["commit_order"] == "READ_INPUT_THEN_COMMIT_RESULT"
            and row["frame_q_changes_history"] == "NO__ACTION_Q_ONLY"
            for row in built["q_transitions"]
        ),
        "all Q transitions commit Station only after reading their input",
        checks,
    )
    q_hosts = [row for row in built["hosts"] if row["primary_governor_key"] in q_keys]
    require(
        all(
            row["gdt599_complete_clause_de"].count(";") == 1
            and row["gdt599_complete_clause_de"].count(Q_MARKER_ACCUSATIVE) == 1
            and "; übernimm " in row["gdt599_complete_clause_de"]
            for row in q_hosts
        ),
        "every action-Q host has exactly one explicit accusative result clause",
        checks,
    )
    require(all("als neuer Bad- oder Stationsansatz" not in row["gdt599_complete_clause_de"].split(";", 1)[0] for row in q_hosts), "no Q result remains embedded in its input clause", checks)
    require(
        not any(
            Q_MARKER_ACCUSATIVE in row["gdt599_complete_clause_de"]
            for row in built["hosts"]
            if row["action_root"] in ACTION_ROOTS
            and row["primary_governor_key"] not in q_keys
        ),
        "no non-Q action receives a Q result clause",
        checks,
    )
    frame_q_source_rows = [
        row
        for row in source_host_rows
        if row["action_root"] == "FRAME" and Q_MARKER in row["gdt598_integrated_clause_de"]
    ]
    complete_host_by_ordinal = {
        row["host_ordinal_global"]: row for row in built["hosts"]
    }
    require(
        len(frame_q_source_rows) == 3
        and all(
            complete_host_by_ordinal[row["host_ordinal_global"]]["gdt599_complete_clause_de"]
            == row["gdt598_integrated_clause_de"]
            for row in frame_q_source_rows
        ),
        "all three FRAME-Q clauses remain unchanged and outside action history",
        checks,
    )
    replay_q_rows = [row for row in replay if row["q_result_transition"] == "YES"]
    require(
        len(replay_q_rows) == 15
        and all(
            row["state_commit_object_class"] == "STATION"
            and row["state_commit_object_lemma_de"] == "Stationsansatz"
            and row["state_commit_channel"] == "PARTICIPANT"
            for row in replay_q_rows
        ),
        "all 15 new action-Q rows commit a participant Station result",
        checks,
    )

    require(len(built["clause_polish"]) == 3, "three explicit local clause-polish decisions", checks)
    require(
        {row["polish_id"] for row in built["clause_polish"]} == {"C02", "C03", "C04"},
        "clause-polish IDs are exactly C02, C03, and C04",
        checks,
    )
    require(all(row["object_lemma_de"] in row["final_clause_de"] for row in built["clause_polish"]), "clause polish preserves its declared object lemma", checks)
    sample = next(row for row in replay if row["primary_governor_key"] == "ACTION:G407-E2616@3:CH")
    sample_follower = next(row for row in replay if row["primary_governor_key"] == "ACTION:G407-E2617@1:OK")
    require(sample["object_class"] == "PORTION" and sample["object_lemma_de"] == "Probe" and "Probe" in sample["gdt599_completed_clause_de"], "E2616 sample is typed and rendered as Probe", checks)
    require(sample_follower["object_lemma_de"] == "Probe" and "Probe" in sample_follower["gdt599_completed_clause_de"], "E2617 consumes the propagated Probe", checks)

    require(len(built["local_cards"]) == 40, "40 local cards retained separately", checks)
    require(all(row["integration_route"] == "SEPARATE_LOCAL_APPENDIX__NEVER_INHERIT_INTO_RUNNING_STATEMENT" for row in built["local_cards"]), "local cards never inherit into statements", checks)
    require(len(built["manual_reviews"]) == 40, "40 inherited GDT596/GDT597 reviews retained", checks)

    replay_by_slot = {row["action_slot_id"]: row for row in replay}
    action_by_slot = {row["action_slot_id"]: row for row in built["actions"]}
    replay_action_field_pairs = (
        ("object_class", "object_class"),
        ("object_lemma_de", "object_lemma_de"),
        ("rendered_object_np_de", "rendered_object_np_de"),
        ("typing_card_id", "typing_card_id"),
        ("reference_scope_card_id", "reference_scope_card_id"),
        ("reference_mode", "reference_mode"),
        ("source_pointer", "source_pointer"),
        ("gdt599_completed_clause_de", "gdt599_complete_clause_de"),
    )
    require(
        all(
            replay_row[left_field] == action_by_slot[slot][right_field]
            for slot, replay_row in replay_by_slot.items()
            for left_field, right_field in replay_action_field_pairs
        ),
        "all 793 replay objects, sources, and clauses join exactly into the action edition",
        checks,
    )
    action_host_fields = (
        "primary_governor_key", "action_slot_id", "object_class", "object_lemma_de",
        "rendered_object_np_de", "typing_card_id", "reference_scope_card_id",
        "reference_mode", "source_pointer", "gdt599_complete_clause_de",
    )
    require(
        all(
            action_row[field]
            == complete_host_by_ordinal[action_row["host_ordinal_global"]][field]
            for action_row in built["actions"]
            for field in action_host_fields
        ),
        "all 1443 action rows join exactly into the complete host edition",
        checks,
    )

    expected_artifact_names = {"README.md"} | {
        path.name for name, path in OUTPUTS.items() if name != "validation"
    }
    actual_artifact_names = {
        path.name for path in OUTPUTS["result"].parent.iterdir() if path.is_file()
    }
    require(
        not (actual_artifact_names - (expected_artifact_names | {OUTPUTS["validation"].name}))
        and not (expected_artifact_names - actual_artifact_names),
        "artifact directory contains every canonical output and no obsolete output names",
        checks,
    )

    row_outputs = (
        "replay", "actions", "hosts", "statements", "typing_cards", "reference_cards", "defaults",
        "compatibility", "q_transitions", "manual_decisions", "propagation_effects", "aiin_bindings", "clause_polish",
        "review_queue", "pages", "local_cards", "manual_reviews",
    )
    for name in row_outputs:
        require(OUTPUTS[name].read_bytes() == tsv_bytes(built[name]), f"artifact byte-reproduces: {OUTPUTS[name].name}", checks)
    require(OUTPUTS["reader"].read_text(encoding="utf-8") == built["reader"], "reader byte-reproduces", checks)
    expected_result_text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    require(
        OUTPUTS["result"].read_text(encoding="utf-8") == expected_result_text,
        "result JSON byte-reproduces",
        checks,
    )

    validation = {
        "experiment_id": "GDT599",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_status": result["status"],
    }
    OUTPUTS["validation"].write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

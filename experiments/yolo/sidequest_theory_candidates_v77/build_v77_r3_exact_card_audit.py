#!/usr/bin/env python3
"""Build V77 R3 exact-card attestation and occurrence audit.

The historical inventory and central target manifest are pre-existing frozen
inputs.  This builder never selects cards from semantic outcomes and never
uses tuple coordinates, substrings, stems, sounds, PAGE_HOST, or sealed pages.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
V69 = YOLO / "sidequest_theory_candidates_v69"

SOURCE_INVENTORY = HERE / "V77_R3_FROZEN_SOURCE_INVENTORY.tsv"
SOURCE_FREEZE = HERE / "V77_R3_SOURCE_FREEZE.json"
TARGET_FREEZE = HERE / "V77_TARGET_FREEZE.tsv"
DICTIONARY = V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
EVENTS = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"

SOURCE_HASH = "375aee41178e7c333a6bf43b479d5fd400e62524be0d919c26160892de2881fa"
TARGET_HASH = "2b5659f9d7cd213fc22842c38e38388061096b9407723628bb82bb0a51ce1dd7"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


CONTROL_META = {
    "MASS?": {
        "gloss": "QUANTITY_OR_PARAMETER?",
        "invariance": "APPARENT_CROSS_HERBAL_BIO_CONSISTENCY__LEGACY_EXPANSIONS_ARE_CIRCULAR",
        "confound": "PARAMETER_PLACEMENT_PLUS_SURFACE_DAIIN_FORMAL_SUBSET",
        "poly": "ONE_EXACT_CARD_HAS_MNEMONIC_AND_SURFACE_SPECIFIC_FORMAL_CHANNEL",
        "false_friend": "SRC037 uses numeric code 10 for the place Mediolanum; a numeric code is not an entry meaning quantity. No quantitas/mensura entry occurs in the frozen inventory.",
    },
    "ANWENDEN?": {
        "gloss": "APPLY_OR_USE?",
        "invariance": "APPARENT_CROSS_HERBAL_BIO_CONSISTENCY__LEGACY_EXPANSIONS_ARE_CIRCULAR",
        "confound": "TARGET_ADJACENCY_AND_BROAD_ACTION_DEFAULT",
        "poly": "INTERNAL_USE_TOPICAL_USE_REPEAT_AND_STATION_USE_COLLAPSED_BY_BROAD_HANDLE",
        "false_friend": "No facere/uti/applicare or comparable operation entry occurs in the frozen source inventory.",
    },
    "BEREIT?": {
        "gloss": "READY_OR_RELEASED_STATE?",
        "invariance": "FAIL_NARROW_INVARIANCE__H2_PHENOLOGICAL_OPENING_VS_CHARGE_TEST_STATE",
        "confound": "STATE_GATE_POSITION_AND_EXEMPLAR_ENDPOINT",
        "poly": "PHENOLOGICAL_TIMING_AND_PROCESS_READINESS_SHARE_ONE_BROAD_HANDLE",
        "false_friend": "SRC031 pax and SRC032 guerra are diplomatic topics, not generic ready/released states.",
    },
    "ANSATZ?": {
        "gloss": "CURRENT_WORKING_ITEM?",
        "invariance": "PARTIAL_CROSS_HERBAL_BIO__OPEN_SET_REPEAT_AND_CONTINUATION_NOT_ATOMICALLY_SEPARATED",
        "confound": "ACTIVE_REGISTER_PLACEMENT",
        "poly": "OPEN_NEW_ITEM_REPEAT_ITEM_AND_CONTINUE_ITEM_COLLAPSED",
        "false_friend": "No preparation/stock/current-item entry occurs in the frozen source inventory.",
    },
    "ZIEL?": {
        "gloss": "TARGET_OR_DESTINATION?",
        "invariance": "APPARENT_CROSS_HERBAL_BIO_CONSISTENCY__TARGETS_WERE_SUPPLIED_BY_LEGACY_REGISTER_MODEL",
        "confound": "RELATION_SLOT_AND_LOCAL_PLACEMENT_SHORTCUT",
        "poly": "BODY_SITE_STATION_AND_ABSTRACT_TARGET_COLLAPSED",
        "false_friend": "Place entries SRC021/SRC022/SRC036/SRC037 name external places; they do not attest an abstract destination-slot word.",
    },
    "KLAR?": {
        "gloss": "CLEAR_OR_ENDPOINT_STATE?",
        "invariance": "FAIL_NARROW_INVARIANCE__H3_CLEAR_FILTRATE_VS_BIO_GENERIC_TEST_STATE",
        "confound": "PRE_TERMINAL_STATE_CHECK_AND_FILTER_CONTEXT",
        "poly": "SPECIFIC_CLARITY_AND_GENERIC_READINESS_COLLAPSED",
        "false_friend": "No clarus/clear/endpoint entry occurs in the frozen source inventory.",
    },
    "VORIGES?": {
        "gloss": "PREVIOUS_ITEM?",
        "invariance": "TWO_CROSS_SECTION_OCCURRENCES_ONLY__LEGACY_REGISTER_EXPANSION_CONSISTENT_BUT_UNPOWERED",
        "confound": "PREDECESSOR_RECURRENCE_AND_RECORD_POSITION",
        "poly": "NO_CONTRADICTION_VISIBLE_AT_N2_BUT_ATOMICITY_UNTESTED",
        "false_friend": "No anaphoric/previous-item entry occurs in the frozen source inventory.",
    },
    "ANTEIL?": {
        "gloss": "SELECTED_PORTION?",
        "invariance": "TWO_CROSS_SECTION_OCCURRENCES_ONLY__LEGACY_EXPANSION_CONSISTENT_BUT_UNPOWERED",
        "confound": "SELECTION_SLOT_AND_LOCAL_PARTITION_CONTEXT",
        "poly": "PLANT_FRACTION_AND_BIO_CHARGE_COLLAPSED_AT_N2",
        "false_friend": "No pars/portion/select entry occurs in the frozen source inventory.",
    },
    "TEMPERIEREN?": {
        "gloss": "TEMPER_OR_ADJUST_CONDITION?",
        "invariance": "NOT_TESTABLE_CROSS_SECTION__BIO_ONLY",
        "confound": "BIO_REGISTER_AND_ASSUMED_HEAT_STATION",
        "poly": "BROAD_CONDITION_ADJUSTMENT_IS_NOT_DISTINGUISHED_FROM_HEATING",
        "false_friend": "No heat/temperature/condition-adjustment entry occurs in the frozen source inventory.",
    },
    "SPÜLEN?": {
        "gloss": "FLUSH_OR_WASH?",
        "invariance": "NOT_TESTABLE_CROSS_SECTION__BIO_ONLY_AND_8_OF_8_TERMINAL",
        "confound": "PERFECT_TERMINAL_CLOSE_CONFOUND",
        "poly": "ACTION_CANNOT_BE_SEPARATED_FROM_GENERIC_TERMINAL_OPERATION",
        "false_friend": "No lavare/flush/wash entry occurs in the frozen source inventory.",
    },
    "ABLASSEN?": {
        "gloss": "DRAIN_OR_DISCHARGE?",
        "invariance": "NOT_TESTABLE_CROSS_SECTION__BIO_ONLY_AND_8_OF_8_TERMINAL",
        "confound": "PERFECT_TERMINAL_CLOSE_CONFOUND",
        "poly": "ACTION_CANNOT_BE_SEPARATED_FROM_GENERIC_TERMINAL_OPERATION",
        "false_friend": "No drain/discharge/outlet entry occurs in the frozen source inventory.",
    },
    "STANDARDSLOT_SETZEN": {
        "gloss": "NONE__FORMAL_OPERATION",
        "invariance": "FORMAL_CHANNEL_REPEATS_CROSS_SECTION__NO_WORD_TEST",
        "confound": "PARAMETER_PLACEMENT_AND_ACTIVE_ITEM_CONTEXT",
        "poly": "FORMAL_PROMPT_ONLY",
        "false_friend": "A diplomatic nomenclator entry cannot attest an editorial slot-setting label without an exact matching entry; none exists.",
    },
    "LOKALEN_RELATIONSSLOT_SETZEN": {
        "gloss": "NONE__FORMAL_OPERATION",
        "invariance": "FORMAL_CHANNEL_REPEATS_CROSS_SECTION__NO_WORD_TEST",
        "confound": "TARGET_PLACEMENT_AND_RELATION_CONTEXT",
        "poly": "FORMAL_PROMPT_ONLY",
        "false_friend": "Place/person nomenclator entries are stored values, not evidence for an abstract relation-slot operation.",
    },
    "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": {
        "gloss": "NONE__FORMAL_OPERATION",
        "invariance": "FORMAL_CHANNEL_REPEATS_CROSS_SECTION__NO_WORD_TEST",
        "confound": "HIGH_FREQUENCY_ACTIVE_PREVIOUS_REGISTER_CONTEXT",
        "poly": "FORMAL_PROMPT_ONLY",
        "false_friend": "No link/current-state operation entry occurs in the frozen source inventory.",
    },
}


def control_label(card: dict[str, str]) -> str:
    mnemonic = card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
    if mnemonic != "UNKNOWN":
        return mnemonic
    return card["strict_control_prompt"].replace("SURFACE_DAIIN_ONLY:", "")


def position(index: int, total: int) -> str:
    if total == 1:
        return "SINGLE"
    if index == 0:
        return "START"
    if index == total - 1:
        return "END"
    return "MIDDLE"


def event_assessment(label: str, event: dict[str, str], selection_class: str) -> str:
    if selection_class == "TOP10_RECURRENT_NONCONTROL":
        return "NO_GLOSS_PROPOSED__NEGATIVE_CONTROL_OCCURRENCE"
    if label in {"SPÜLEN?", "ABLASSEN?"}:
        return "TERMINAL_CLOSE_CONFOUND__ACTION_NOT_IDENTIFIED"
    if label == "KLAR?":
        return "LEGACY_CLEAR_CONTEXT" if event["record_unit_id"].startswith("H") else "BIO_GENERIC_TEST_STATE__STRAINS_CLEAR_GLOSS"
    if label == "BEREIT?" and event["event_serial"] == "16":
        return "PHENOLOGICAL_OPENING__STRAINS_CHARGE_READY_GLOSS"
    if label in {"STANDARDSLOT_SETZEN", "LOKALEN_RELATIONSSLOT_SETZEN", "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN"}:
        return "FORMAL_REPETITION_ONLY__NOT_A_WORD_TEST"
    if label in {"VORIGES?", "ANTEIL?"}:
        return "LEGACY_EXPANSION_CONSISTENT_BUT_N2_AND_CIRCULAR"
    if label == "TEMPERIEREN?":
        return "BIO_ONLY_LEGACY_EXPANSION_CONSISTENT_BUT_CIRCULAR"
    return "LEGACY_EXPANSION_CONSISTENT_BUT_CIRCULAR"


def final_decision(card: dict[str, str], selection_class: str) -> tuple[str, str, str]:
    mnemonic = card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
    formal = card["strict_control_prompt"]
    if selection_class == "TOP10_RECURRENT_NONCONTROL":
        return "EXEMPLAR_VALUE_UNKNOWN", "NONE", "NO_GLOSS_PROPOSED"
    lexical = "EXEMPLAR_VALUE_UNKNOWN" if mnemonic != "UNKNOWN" else "NOT_APPLICABLE"
    formal_decision = "FORMAL_LABEL_NOT_WORD" if formal != "NONE" else "NONE"
    portable = "FORMAL_LABEL_NOT_WORD" if lexical == "NOT_APPLICABLE" else "EXEMPLAR_VALUE_UNKNOWN"
    return portable, formal_decision, "NO_EXACT_SOURCE_CATEGORY_MATCH"


def main() -> None:
    assert sha(SOURCE_INVENTORY) == SOURCE_HASH
    assert sha(TARGET_FREEZE) == TARGET_HASH
    source_rows = read_tsv(SOURCE_INVENTORY)
    assert len(source_rows) == 37
    freeze = json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
    assert freeze["inventory_sha256"] == SOURCE_HASH

    target = read_tsv(TARGET_FREEZE)
    cards = {row["joint_tuple_id"]: row for row in read_tsv(DICTIONARY)}
    events = read_tsv(EVENTS)
    assert len(target) == 24
    assert sum(int(row["occurrences"]) for row in target) == 197
    selected_ids = {row["joint_tuple_id"] for row in target}
    assert len(selected_ids) == 24

    # Reproduce the target manifest from frequency/ID only as a leakage check.
    controls = {cid for cid, row in cards.items() if row["V69_FINAL_CONTROL_CLASS"] != "UNKNOWN_EXEMPLAR_WHOLE_CARD"}
    ranked_noncontrols = sorted(
        (row for row in cards.values() if row["V69_FINAL_CONTROL_CLASS"] == "UNKNOWN_EXEMPLAR_WHOLE_CARD"),
        key=lambda row: (-int(row["occurrences"]), row["joint_tuple_id"]),
    )[:10]
    assert controls == {row["joint_tuple_id"] for row in target if row["selection_class"] == "V69_REUSABLE_CONTROL"}
    assert [row["joint_tuple_id"] for row in ranked_noncontrols] == [row["joint_tuple_id"] for row in target if row["selection_class"] == "TOP10_RECURRENT_NONCONTROL"]

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_field[event["field_id"]].append(event)
        by_statement[event["statement_id"]].append(event)
        by_record[event["record_unit_id"]].append(event)
        by_locus[event["locus"]].append(event)
    index_in = {}
    for groups in (by_field, by_statement, by_record, by_locus):
        for key, group in groups.items():
            for idx, event in enumerate(group):
                index_in[(id(groups), event["event_serial"])] = (idx, len(group))

    target_by_id = {row["joint_tuple_id"]: row for row in target}
    decision_rows: list[dict[str, object]] = []
    occurrence_rows: list[dict[str, object]] = []

    for manifest in target:
        cid = manifest["joint_tuple_id"]
        card = cards[cid]
        selection_class = manifest["selection_class"]
        label = control_label(card) if selection_class == "V69_REUSABLE_CONTROL" else "NONE"
        meta = CONTROL_META[label] if selection_class == "V69_REUSABLE_CONTROL" else {
            "gloss": "UNKNOWN",
            "invariance": "NO_GLOSS_TO_TEST",
            "confound": "FREQUENCY_SELECTED_NEGATIVE_CONTROL",
            "poly": "UNKNOWN_WHOLE_CARD__LOCAL_CONTEXT_DIVERSITY_RETAINED",
            "false_friend": "No source match was sought from spelling or surface resemblance; no gloss was proposed.",
        }
        portable, formal_decision, documentary = final_decision(card, selection_class)
        card_events = [event for event in events if event["joint_tuple_id"] == cid]
        assert len(card_events) == int(manifest["occurrences"]) == int(card["occurrences"])
        h_count = sum(event["record_unit_id"].startswith("H") for event in card_events)
        b_count = len(card_events) - h_count
        terminal_count = sum(event["terminal_status"] == "TERMINAL" for event in card_events)
        assessment_counts = Counter(event_assessment(label, event, selection_class) for event in card_events)
        surface_count = len({event["surface_display_only"] for event in card_events})

        decision_rows.append(
            {
                "target_rank": manifest["target_rank"],
                "selection_class": selection_class,
                "selection_rule": manifest["selection_rule"],
                "joint_tuple_id": cid,
                "surface_examples_display_only": manifest["surface_examples"],
                "occurrences": len(card_events),
                "pages": "|".join(sorted({event["page"] for event in card_events})),
                "records": "|".join(sorted({event["record_unit_id"] for event in card_events})),
                "fields": len({event["field_id"] for event in card_events}),
                "herbal_occurrences": h_count,
                "biological_occurrences": b_count,
                "cross_section_power": "BOTH" if h_count and b_count else ("HERBAL_ONLY" if h_count else "BIO_ONLY"),
                "terminal_occurrences": terminal_count,
                "terminal_fraction": f"{terminal_count / len(card_events):.6f}",
                "distinct_surface_renderings": surface_count,
                "legacy_mnemonic_handle": card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                "strict_formal_prompt": card["strict_control_prompt"],
                "atomic_minimal_gloss_tested": meta["gloss"],
                "exact_source_match_ids": "NONE",
                "exact_source_entry": "NONE",
                "exact_source_code": "NONE",
                "documentary_match_result": documentary,
                "occurrence_invariance_result": meta["invariance"],
                "occurrence_assessment_counts": "|".join(f"{key}:{value}" for key, value in sorted(assessment_counts.items())),
                "close_or_placement_confound": meta["confound"],
                "whole_card_polyfunctionality_stress": meta["poly"],
                "false_friend_audit": meta["false_friend"],
                "portable_dictionary_decision": portable,
                "formal_channel_decision": formal_decision,
                "codebook_attested_category": "NO",
                "decision_reason": "No frozen 1379 nomenclator entry matches the proposed minimal category; occurrence regularity alone cannot satisfy documentary attestation.",
                "semantic_ceiling": "NO_WORD_STEM_SOUND_LANGUAGE_PAGE_HOST_OR_DECIPHERMENT",
            }
        )

        record_group = by_record[card_events[0]["record_unit_id"]] if card_events else []
        for event in card_events:
            fi, fn = index_in[(id(by_field), event["event_serial"])]
            si, sn = index_in[(id(by_statement), event["event_serial"])]
            ri, rn = index_in[(id(by_record), event["event_serial"])]
            li, ln = index_in[(id(by_locus), event["event_serial"])]
            record_events = by_record[event["record_unit_id"]]
            previous_id = record_events[ri - 1]["joint_tuple_id"] if ri else "RECORD_START"
            next_id = record_events[ri + 1]["joint_tuple_id"] if ri + 1 < rn else "RECORD_END"
            occurrence_rows.append(
                {
                    "audit_occurrence_id": f"O{len(occurrence_rows)+1:03d}",
                    "target_rank": manifest["target_rank"],
                    "selection_class": selection_class,
                    "joint_tuple_id": cid,
                    "event_serial": event["event_serial"],
                    "section": "HERBAL" if event["record_unit_id"].startswith("H") else "BIOLOGICAL",
                    "page": event["page"],
                    "record_unit_id": event["record_unit_id"],
                    "locus": event["locus"],
                    "field_id": event["field_id"],
                    "statement_id": event["statement_id"],
                    "surface_display_only": event["surface_display_only"],
                    "formal_formula_opaque": event["formal_formula_opaque"],
                    "terminal_status": event["terminal_status"],
                    "line_position": position(li, ln),
                    "field_position": position(fi, fn),
                    "statement_position": position(si, sn),
                    "record_position": position(ri, rn),
                    "previous_exact_tuple_in_record": previous_id,
                    "next_exact_tuple_in_record": next_id,
                    "strict_formal_prompt": event["strict_formal_prompt"],
                    "legacy_selected_mnemonic": event["selected_exact_mnemonic"],
                    "parse_status": event["parse_status"],
                    "legacy_iatromedical_expansion_not_evidence": event["iatromedical_source_segment"],
                    "legacy_practical_expansion_not_evidence": event["practical_source_segment"],
                    "atomic_minimal_gloss_tested": meta["gloss"],
                    "occurrence_assessment": event_assessment(label, event, selection_class),
                    "close_confound_flag": "YES" if event["terminal_status"] == "TERMINAL" else "NO",
                    "source_attestation_match": "NONE",
                    "portable_dictionary_decision": portable,
                    "semantic_ceiling": "OCCURRENCE_AUDIT_NOT_TRANSLATION",
                }
            )

    assert len(decision_rows) == 24
    assert len(occurrence_rows) == 197
    assert [int(row["event_serial"]) for row in occurrence_rows] == [int(row["event_serial"]) for manifest in target for row in events if row["joint_tuple_id"] == manifest["joint_tuple_id"]]

    withdrawal_rows: list[dict[str, object]] = []
    for decision in decision_rows:
        if decision["selection_class"] != "V69_REUSABLE_CONTROL":
            continue
        cid = str(decision["joint_tuple_id"])
        card = cards[cid]
        mnemonic = card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        if mnemonic != "UNKNOWN":
            withdrawal_rows.append(
                {
                    "withdrawal_id": f"W{len(withdrawal_rows)+1:02d}",
                    "joint_tuple_id": cid,
                    "channel_type": "LEGACY_MNEMONIC",
                    "legacy_handle_or_prompt": mnemonic,
                    "old_portable_status": "PROVISIONAL_UNATTESTED_MNEMONIC",
                    "atomic_minimal_gloss_tested": CONTROL_META[mnemonic]["gloss"],
                    "source_match_ids": "NONE",
                    "occurrence_result": CONTROL_META[mnemonic]["invariance"],
                    "action": "WITHDRAW_AS_PORTABLE_WORD",
                    "replacement": "EXEMPLAR_VALUE_UNKNOWN",
                    "reason": "Exact contemporary entry absent; structural recurrence and legacy exemplar prose cannot substitute for documentary attestation.",
                    "future_print_rule": "BRACKET_OCCURRENCE_EXPANSION_OR_PRINT_UNKNOWN",
                }
            )
        formal = card["strict_control_prompt"]
        if formal != "NONE":
            normalized = formal.replace("SURFACE_DAIIN_ONLY:", "")
            withdrawal_rows.append(
                {
                    "withdrawal_id": f"W{len(withdrawal_rows)+1:02d}",
                    "joint_tuple_id": cid,
                    "channel_type": "FORMAL_PROMPT",
                    "legacy_handle_or_prompt": formal,
                    "old_portable_status": "FORMAL_CHANNEL_NEVER_A_WORD",
                    "atomic_minimal_gloss_tested": "NONE__FORMAL_OPERATION",
                    "source_match_ids": "NONE",
                    "occurrence_result": CONTROL_META[normalized]["invariance"] if normalized in CONTROL_META else CONTROL_META["MASS?"]["invariance"],
                    "action": "RETAIN_ONLY_AS_FORMAL_NONWORD_LABEL",
                    "replacement": "FORMAL_LABEL_NOT_WORD",
                    "reason": "The prompt is an editorial execution label; codebook attestation is neither present nor a license to lexicalize it.",
                    "future_print_rule": "ALWAYS_PREFIX_FORMAL_AND_STATE_NOT_A_WORD",
                }
            )
    assert len(withdrawal_rows) == 15

    write_tsv(HERE / "V77_R3_DECISION_TABLE.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(HERE / "V77_R3_OCCURRENCE_AUDIT.tsv", occurrence_rows, list(occurrence_rows[0]))
    write_tsv(HERE / "V77_R3_WITHDRAWALS.tsv", withdrawal_rows, list(withdrawal_rows[0]))

    outputs = ["V77_R3_DECISION_TABLE.tsv", "V77_R3_OCCURRENCE_AUDIT.tsv", "V77_R3_WITHDRAWALS.tsv"]
    summary = {
        "round": "V77_R3",
        "status": "BUILT",
        "target_manifest_sha256": TARGET_HASH,
        "source_inventory_sha256": SOURCE_HASH,
        "scope": {
            "candidate_cards": len(decision_rows),
            "control_cards": sum(row["selection_class"] == "V69_REUSABLE_CONTROL" for row in decision_rows),
            "frequency_noncontrols": sum(row["selection_class"] == "TOP10_RECURRENT_NONCONTROL" for row in decision_rows),
            "occurrences": len(occurrence_rows),
            "source_entries": len(source_rows),
        },
        "portable_decisions": dict(Counter(str(row["portable_dictionary_decision"]) for row in decision_rows)),
        "formal_nonword_channels": sum(row["formal_channel_decision"] == "FORMAL_LABEL_NOT_WORD" for row in decision_rows),
        "codebook_attested_categories": 0,
        "withdrawal_rows": len(withdrawal_rows),
        "decision": "ZERO_PORTABLE_WORDS__11_MNEMONICS_TO_UNKNOWN__4_FORMAL_CHANNELS_NONWORD",
        "sealed": ["f84", "f84r"],
        "forbidden_feature_use": {"stems": 0, "sounds": 0, "PAGE_HOST": 0, "substring_semantics": 0},
        "output_sha256": {name: sha(HERE / name) for name in outputs},
    }
    (HERE / "V77_R3_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

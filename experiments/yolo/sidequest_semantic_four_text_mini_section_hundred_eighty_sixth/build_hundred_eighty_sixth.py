#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AB = ROOT / "experiments/yolo/sidequest_semantic_third_scribe_grammar_hundred_eightieth/HUNDRED_EIGHTIETH_29_TOKEN_SLOT_PARSE.tsv"
A_FIELDS = ROOT / "experiments/yolo/sidequest_semantic_forward_writing_hundred_seventy_eighth/HUNDRED_SEVENTY_EIGHTH_5_FIELD_WRITING_EXERCISE.tsv"
C_TOKENS = ROOT / "experiments/yolo/sidequest_semantic_reopen_forward_writing_hundred_eighty_second/HUNDRED_EIGHTY_SECOND_19_TOKEN_REOPEN_ENCODING.tsv"
C_FIELDS = ROOT / "experiments/yolo/sidequest_semantic_reopen_forward_writing_hundred_eighty_second/HUNDRED_EIGHTY_SECOND_3_FIELD_REOPEN_EXERCISE.tsv"
B_TOKENS = ROOT / "experiments/yolo/sidequest_semantic_full_slot_lexicon_hundred_eighty_fourth/HUNDRED_EIGHTY_FOURTH_CORRECTED_16_TOKEN_SECOND_EXERCISE.tsv"
B_FIELDS = ROOT / "experiments/yolo/sidequest_semantic_full_slot_lexicon_hundred_eighty_fourth/HUNDRED_EIGHTY_FOURTH_CORRECTED_5_FIELD_SECOND_EXERCISE.tsv"
D_TOKENS = ROOT / "experiments/yolo/sidequest_semantic_zero_overlap_fourth_writing_hundred_eighty_fifth/HUNDRED_EIGHTY_FIFTH_25_TOKEN_ZERO_OVERLAP_ENCODING.tsv"
D_FIELDS = ROOT / "experiments/yolo/sidequest_semantic_zero_overlap_fourth_writing_hundred_eighty_fifth/HUNDRED_EIGHTY_FIFTH_5_FIELD_FOURTH_EXERCISE.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_full_slot_lexicon_hundred_eighty_fourth/HUNDRED_EIGHTY_FOURTH_173_CARD_SIX_SLOT_LEXICON.tsv"


SECTION_ORDER = [
    ("A", "A_CLEAR_EXTRACT_DOUBLE_PASS", "MASTER_SUPPLIED_CLEAR_EXTRACT", 5),
    ("C", "C_REOPEN_THREE_PACKET", "PREVIOUS_A_BATCH_WITH_CLEAR_EXTRACT_SUBCALL", 3),
    ("B", "B_STOCK_SPLIT_CORRECTED", "STORED_REMAINDER_FROM_C", 5),
    ("D", "D_ADDITIVE_FOLLOW_BATCH", "NEW_ADDITIVE_BATCH", 5),
]


HANDOFFS = [
    ("H0", "SECTION_START", "A", "MASTER_ASSIGNS_CLEAR_EXTRACT", "clear extract batch is the initial active owner", "EXPLICIT_EDITORIAL_OWNER"),
    ("H1", "A", "C", "dchol", "load A as the previous active batch", "EXPLICIT_CARD_CARRY"),
    ("H2", "C", "B", "talam dchol", "load C's stored remainder as the previous stock", "EXPLICIT_DOUBLE_CARD_CARRY"),
    ("H3", "B", "D", "chor", "start a new additive batch after the split workflow", "OWNER_RESET_REQUIRES_MASTER_OR_PICTURE"),
]


STATE_ROWS = [
    ("A", 1, "CLEAR_EXTRACT_A", "MEASURED_CLEAR_EXTRACT", "UNSET", "UNSET", "OPEN_CARRY"),
    ("A", 2, "CLEAR_EXTRACT_A", "WARMED_INSERT_TRANSFER", "INHERITED", "INSERT", "CLOSED"),
    ("A", 3, "CLEAR_EXTRACT_A", "AFTER_PASS_1", "INHERITED", "PASS_STATION", "CLOSED"),
    ("A", 4, "CLEAR_EXTRACT_A", "AFTER_PASS_2", "INHERITED", "PASS_STATION", "CLOSED"),
    ("A", 5, "CLEAR_EXTRACT_A", "TARGET_WASH_COMPLETE", "TARGET_1", "WASH", "CLOSED_SECTION_OUTPUT_A"),
    ("C", 1, "PREVIOUS_A_BATCH", "CLEAR_EXTRACT_PASSED_ONCE", "TARGET_1", "INSERT_PASS", "CLOSED"),
    ("C", 2, "PREVIOUS_A_BATCH", "TARGET_2_WASH_COMPLETE", "TARGET_2", "WASH", "CLOSED"),
    ("C", 3, "PREVIOUS_A_BATCH", "REMAINDER_STORED_READY", "STORAGE", "STORAGE", "CLOSED_SECTION_OUTPUT_C"),
    ("B", 1, "STORED_REMAINDER_C", "DIVIDED_PORTIONS_1_2", "UNSET", "STORAGE", "OPEN_CARRY"),
    ("B", 2, "STORED_REMAINDER_C", "PORTION_1_COOLED", "UNSET", "COOL", "CLOSED"),
    ("B", 3, "STORED_REMAINDER_C", "PORTION_1_STORED_READY", "STORAGE", "STORAGE", "CLOSED"),
    ("B", 4, "STORED_REMAINDER_C", "PORTION_2_TARGET_1_CONTACT", "TARGET_1", "CONTACT", "CLOSED"),
    ("B", 5, "STORED_REMAINDER_C", "TARGET_2_WASH_COMPLETE", "TARGET_2", "WASH", "CLOSED_SECTION_OUTPUT_B"),
    ("D", 1, "NEW_ADDITIVE_BATCH_D", "ADDITIVES_BRIEFLY_PREPARED", "UNSET", "PREPARATION", "OPEN_CARRY"),
    ("D", 2, "NEW_ADDITIVE_BATCH_D", "SETTLED_AT_TARGET", "TARGET_1", "SETTLE", "CLOSED"),
    ("D", 3, "FOLLOW_BATCH_D1", "TRANSFERRED_AT_WORK_STAGE", "TARGET_2", "TRANSFER", "CLOSED"),
    ("D", 4, "FOLLOW_BATCH_D1", "LONG_CONTACT_DRAINED", "TARGET_2", "DRAIN", "CLOSED"),
    ("D", 5, "FOLLOW_BATCH_D2", "LONG_COLLECTION_DRAWN_OFF", "COLLECTOR", "COLLECTION", "CLOSED_SECTION_OUTPUT_D"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = {row["master_card_id"]: row for row in read(LEXICON)}
    ab = read(AB)
    a_tokens = [row for row in ab if row["exercise"] == "A_CLEAR_EXTRACT_DOUBLE_PASS"]
    b_slot = {int(row["exercise_token_order"]): row["grammar_slot"] for row in ab if row["exercise"] == "B_STOCK_TWO_TARGET"}
    b_corrected = read(B_TOKENS)
    b_overrides = {"MC100": "G6", "MC107": "G2", "MC026": "G4"}

    normalized = []
    for row in a_tokens:
        normalized.append(("A", int(row["field"]), int(row["exercise_token_order"]), 1, row["grammar_slot"], row["master_card_id"], row["surface"], row["dictionary_value_de"]))
    for row in read(C_TOKENS):
        normalized.append(("C", int(row["field"]), int(row["token_order"]), int(row["micro_packet"]), row["grammar_slot"], row["master_card_id"], row["chosen_visible_surface"], row["dictionary_value_de"]))
    for row in b_corrected:
        order = int(row["token_order"])
        normalized.append(("B", int(row["corrected_field"]), order, 1, b_overrides.get(row["master_card_id"], b_slot[order]), row["master_card_id"], row["surface"], row["dictionary_value_de"]))
    for row in read(D_TOKENS):
        normalized.append(("D", int(row["field"]), int(row["token_order"]), 1, row["grammar_slot"], row["master_card_id"], row["surface"], row["dictionary_value_de"]))

    section_rank = {section: rank for rank, (section, _, _, _) in enumerate(SECTION_ORDER, start=1)}
    normalized.sort(key=lambda row: (section_rank[row[0]], row[2]))
    field_offset = {"A": 0, "C": 5, "B": 8, "D": 13}
    token_rows = []
    for section, field, local_order, packet, slot, card_id, surface, value in normalized:
        global_field_number = field_offset[section] + field
        token_rows.append(
            {
                "global_token_order": len(token_rows) + 1,
                "section": section,
                "local_token_order": local_order,
                "local_field": field,
                "global_field_id": f"N{global_field_number:02d}",
                "micro_packet": packet,
                "grammar_slot": slot,
                "master_card_id": card_id,
                "surface": surface,
                "value_de": value,
                "finality_rule": lexicon[card_id]["finality_rule"],
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SIXTH_73_TOKEN_MINI_SECTION.tsv", token_rows)

    field_sources = {
        "A": read(A_FIELDS),
        "C": read(C_FIELDS),
        "B": read(B_FIELDS),
        "D": read(D_FIELDS),
    }
    field_rows = []
    for section, name, owner, field_count in SECTION_ORDER:
        for source in field_sources[section]:
            local_field = int(source["field"])
            global_field = field_offset[section] + local_field
            sequence = source.get("visible_card_sequence") or source.get("visible_sequence")
            reading = source.get("strict_atomic_reading_de") or source.get("fluent_reading_de") or source.get("corrected_reading_de")
            section_tokens = [row for row in token_rows if row["section"] == section and int(row["local_field"]) == local_field]
            field_rows.append(
                {
                    "global_field_id": f"N{global_field:02d}",
                    "section": section,
                    "section_name": name,
                    "local_field": local_field,
                    "owner_register": owner,
                    "visible_sequence": sequence,
                    "reading_de": reading,
                    "field_status": source["field_status"],
                    "micro_packets": len({int(row["micro_packet"]) for row in section_tokens}),
                    "event_count": len(section_tokens),
                }
            )
        if len(field_sources[section]) != field_count:
            raise ValueError(section)
    write(OUT / "HUNDRED_EIGHTY_SIXTH_18_FIELD_MINI_SECTION.tsv", field_rows)

    handoff_rows = [
        {
            "handoff_id": hid,
            "from_section": source,
            "to_section": target,
            "visible_carrier": carrier,
            "register_effect_de": effect,
            "handoff_type": htype,
        }
        for hid, source, target, carrier, effect, htype in HANDOFFS
    ]
    write(OUT / "HUNDRED_EIGHTY_SIXTH_4_OWNER_HANDOFFS.tsv", handoff_rows)

    state_rows = []
    for section, local_field, owner, batch, target, station, disposition in STATE_ROWS:
        global_field = field_offset[section] + local_field
        state_rows.append(
            {
                "global_field_id": f"N{global_field:02d}",
                "section": section,
                "local_field": local_field,
                "owner_before": owner,
                "batch_or_portion_after": batch,
                "target_after": target,
                "station_after": station,
                "field_disposition": disposition,
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SIXTH_18_FIELD_REGISTER_TRACE.tsv", state_rows)

    section_rows = []
    for section, name, owner, _ in SECTION_ORDER:
        rows = [row for row in token_rows if row["section"] == section]
        fs = [row for row in field_rows if row["section"] == section]
        section_rows.append(
            {
                "section": section,
                "section_name": name,
                "initial_owner": owner,
                "tokens": len(rows),
                "distinct_cards": len({row["master_card_id"] for row in rows}),
                "fields": len(fs),
                "micro_packets": sum(int(row["micro_packets"]) for row in fs),
                "open_fields": sum(row["field_status"] == "OPEN" for row in fs),
                "closed_fields": sum(row["field_status"] == "CLOSED" for row in fs),
            }
        )
    write(OUT / "HUNDRED_EIGHTY_SIXTH_4_SECTION_SUMMARY.tsv", section_rows)

    summary = {
        "input_hashes": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in [AB, A_FIELDS, C_TOKENS, C_FIELDS, B_TOKENS, B_FIELDS, D_TOKENS, D_FIELDS, LEXICON]},
        "sections": len(section_rows),
        "tokens": len(token_rows),
        "distinct_cards": len({row["master_card_id"] for row in token_rows}),
        "fields": len(field_rows),
        "micro_packets": sum(int(row["micro_packets"]) for row in field_rows),
        "open_fields": sum(row["field_status"] == "OPEN" for row in field_rows),
        "closed_fields": sum(row["field_status"] == "CLOSED" for row in field_rows),
        "owner_handoffs": len(handoff_rows),
        "new_card_values": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

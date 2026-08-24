#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
DUPLICATES = ROOT / "experiments/yolo/sidequest_semantic_duplicate_card_grammar_two_hundred_twenty_sixth/TWO_HUNDRED_TWENTY_SIXTH_SIX_DUPLICATE_PAIRS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = {row["event_id"]: row for row in read(EVENTS)}
    duplicates = read(DUPLICATES)
    pair = next(row for row in duplicates if row["duplicate_id"] == "DUP02")

    pair_rows = []
    for slot, event_id in enumerate((pair["first_event"], pair["second_event"]), 1):
        source = events[event_id]
        pair_rows.append({
            "slot": slot,
            "event_id": event_id,
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "exact_card_value_de": "Ansatz",
            "active_register": "CURRENT_FOLLOW_ON" if slot == 1 else "PREVIOUS_PRIMARY",
            "instance_reading_de": "Folgeansatz" if slot == 1 else "voriger Pressauszug",
            "surface_wrapper_semantics": "NONE_RENDERER_ONLY",
        })
    write("FOUR_HUNDRED_SECOND_OR_PAIR_BINDING.tsv", pair_rows)

    paraphrases = [
        ("P1_SAME_PLANT_TWO_PROCESSES", "erster Pressauszug", "Folgeansatz aus demselben Pflanzenvorrat", "STRONGEST", "fits H2-S001/S002 order"),
        ("P2_OLD_AND_NEW_BATCH", "voriger Ansatz", "neu eröffneter Folgeansatz", "STRONG", "uses OL+OR and OT+OR explicitly"),
        ("P3_TWO_SUPPLY_VESSELS", "Ansatz aus Vorratsgefäß A", "Ansatz aus Vorratsgefäß B", "POSSIBLE", "requires learned vessels not visible in the cards"),
        ("P4_ONE_BATCH_REASSERTED", "laufender Ansatz", "derselbe Ansatz nochmals bestätigt", "RIVAL", "possible but wastes the open-pair grammar"),
    ]
    write("FOUR_HUNDRED_SECOND_FOUR_PARAPHRASES.tsv", [
        {"paraphrase_id": pid, "or_slot_1": one, "or_slot_2": two, "ranking": rank, "reason": reason}
        for pid, one, two, rank, reason in paraphrases
    ])

    contrast_rows = []
    for row in duplicates:
        contrast_rows.append({
            "duplicate_id": row["duplicate_id"],
            "visible_pair": row["visible_pair"],
            "boundary_class": row["boundary_class"],
            "source_token_count": row["source_token_count"],
            "workshop_rule": row["selected_rule"],
            "reading_de": row["pair_reading_de"],
        })
    write("FOUR_HUNDRED_SECOND_SIX_DUPLICATION_CONTRASTS.tsv", contrast_rows)

    registers = [
        {"step": 1, "event": "E019", "primary_register": "PRESSED_PRIMARY", "follow_on_register": "EMPTY", "action": "first extract exists"},
        {"step": 2, "event": "E024", "primary_register": "PRESSED_PRIMARY", "follow_on_register": "FOLLOW_ON_FRAME", "action": "open second register"},
        {"step": 3, "event": "E028", "primary_register": "PREVIOUS_PRIMARY", "follow_on_register": "CURRENT_FOLLOW_ON", "action": "make both registers jointly available"},
        {"step": 4, "event": "E033", "primary_register": "PREVIOUS_PRIMARY", "follow_on_register": "CURRENT_FOLLOW_ON", "action": "read OR slot 1 from current register"},
        {"step": 5, "event": "E034", "primary_register": "PREVIOUS_PRIMARY", "follow_on_register": "CURRENT_FOLLOW_ON", "action": "read OR slot 2 from remaining previous register"},
        {"step": 6, "event": "E035", "primary_register": "COMBINED_VESSEL_POST", "follow_on_register": "CLOSED_INTO_COMBINATION", "action": "Y resumes combined item"},
    ]
    write("FOUR_HUNDRED_SECOND_REGISTER_TRACE.tsv", registers)

    summary = {
        "status": "PASS",
        "or_pair_events": 2,
        "same_exact_card": len({row["joint_tuple_id"] for row in pair_rows}) == 1,
        "paraphrases": len(paraphrases),
        "duplicate_contrasts": len(contrast_rows),
        "decision": "TWO_INSTANCES_FROM_ACTIVE_REGISTER_ORDER_NOT_SURFACE_WRAPPER",
    }
    (HERE / "FOUR_HUNDRED_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

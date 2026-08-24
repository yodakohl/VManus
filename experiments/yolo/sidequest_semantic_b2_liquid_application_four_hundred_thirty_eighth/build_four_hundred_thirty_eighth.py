#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b2_grade_ladder_four_hundred_thirty_seventh"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_THIRTY_SEVENTH_REVISED_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_SEVENTH_REVISED_B2_22_STATEMENTS.tsv")
    revisions = {
        "0ab57b7166de99db3a55": ("L+CH+Y", "dies abziehen", "OUTWARD+SEPARATE+CURRENT"),
        "5fca8fc3dee57e1d8c1f": ("L+CHE+EE+Y", "dies länger abziehen", "OUTWARD+SEPARATE+LONG+CURRENT"),
        "29e0eb222ef2fb99523a": ("L+AR", "von dort abführen", "OUTWARD+SOURCE"),
        "98bdc4244c84cbef3321": ("RSHE+AL", "Waschflüssigkeit an die Stelle", "WASH_LIQUID+TARGET"),
    }
    for row in events:
        if row["joint_tuple_id"] in revisions:
            row["small_value_de"] = revisions[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "B2_PREDICTED_LIQUID_APPLICATION_COMPOSITION"
    write("FOUR_HUNDRED_THIRTY_EIGHTH_REVISED_B2_62_EVENTS.tsv", events)

    fluent = {
        "B2-S012": "Dies abziehen, den Klarauszug kurz bereithalten, länger ansetzen, dies länger abziehen, auf Maß bringen, dies vollständig ansetzen und schließen.",
        "B2-S014": "Von dort abführen.",
        "B2-S017": "Waschflüssigkeit an die Stelle und zur zweiten Öffnung führen; schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_THIRTY_EIGHTH_REVISED_B2_22_STATEMENTS.tsv", statements)

    liquid_deck = [
        {"surface": "dshedy", "events": 1, "construction_status": "LEARNED_WHOLE_CARD", "small_value_de": "Frischwasser; Schluss", "note": "D is not promoted to fresh globally"},
        {"surface": "tshey", "events": 1, "construction_status": "LEARNED_WHOLE_CARD", "small_value_de": "Spülwasser", "note": "local rinse-liquid card"},
        {"surface": "rsheal", "events": 1, "construction_status": "PRODUCTIVE_RSHE+AL", "small_value_de": "Waschflüssigkeit an die Stelle", "note": "old invisible warmth removed"},
        {"surface": "rshedy", "events": 1, "construction_status": "LEARNED_WHOLE_CARD", "small_value_de": "Waschung; Schluss", "note": "local wash close"},
        {"surface": "cheey|shey", "events": 4, "construction_status": "PORTABLE_RECURRENT_WHOLE_CARD", "small_value_de": "Klarauszug", "note": "H3 B2 B4 exact card; no free EY gloss"},
        {"surface": "solkaiin", "events": 1, "construction_status": "LEARNED_WHOLE_CARD", "small_value_de": "Seihtuch", "note": "cloth/tool card, not SOLK plus AIIN"},
        {"surface": "lchy", "events": 1, "construction_status": "PRODUCTIVE_L+CH+Y", "small_value_de": "dies abziehen", "note": "short direct outward separation"},
        {"surface": "lcheey", "events": 1, "construction_status": "PRODUCTIVE_L+CHE+EE+Y", "small_value_de": "dies länger abziehen", "note": "old invisible wet target removed"},
        {"surface": "lar", "events": 1, "construction_status": "PRODUCTIVE_L+AR", "small_value_de": "von dort abführen", "note": "old invisible lower outlet removed"},
    ]
    write("FOUR_HUNDRED_THIRTY_EIGHTH_NINE_LIQUID_APPLICATION_CARDS.tsv", liquid_deck)

    targets = []
    for joint_id, (composition, value, role) in revisions.items():
        row = [row for row in events if row["joint_tuple_id"] == joint_id][0]
        targets.append({
            "event_id": row["event_id"], "surface": row["surface"], "joint_tuple_id": joint_id,
            "composition": composition, "old_value_removed": {
                "lchy": "den laufenden Posten abziehen", "lcheey": "benetzte Stelle",
                "lar": "unterer Ablauf", "rsheal": "Warmwasser",
            }[row["surface"]], "new_value_de": value, "role": role,
        })
    write("FOUR_HUNDRED_THIRTY_EIGHTH_FOUR_REVISIONS.tsv", targets)

    dictionary = read("FOUR_HUNDRED_THIRTY_SEVENTH_B2_46_CARD_DICTIONARY.tsv")
    new_ids = set(revisions)
    clear_id = [row["joint_tuple_id"] for row in events if row["surface"] == "cheey"][0]
    event_by_card: dict[str, list[dict[str, str]]] = {}
    for row in events:
        event_by_card.setdefault(row["joint_tuple_id"], []).append(row)
    for row in dictionary:
        joint_id = row["joint_tuple_id"]
        if joint_id in new_ids:
            row["drawer"] = "B2_PRODUCTIVE_COMPOSITION"
        elif joint_id == clear_id:
            row["drawer"] = "PORTABLE_RECURRENT_WHOLE_CARD"
        row["small_values_de"] = "|".join(sorted({event["small_value_de"] for event in event_by_card[joint_id]}))
    write("FOUR_HUNDRED_THIRTY_EIGHTH_B2_46_CARD_DICTIONARY.tsv", dictionary)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "liquid_cards": len(liquid_deck),
        "new_compositions": len(new_ids),
        "B1_transfer_cards": sum(row["drawer"] == "B1_TRANSFER" for row in dictionary),
        "B2_productive_cards": sum(row["drawer"] == "B2_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "portable_recurrent_whole_cards": sum(row["drawer"] == "PORTABLE_RECURRENT_WHOLE_CARD" for row in dictionary),
        "B2_local_cards": sum(row["drawer"] == "B2_LOCAL_WHOLE_CARD" for row in dictionary),
    }
    (HERE / "FOUR_HUNDRED_THIRTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

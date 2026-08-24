#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b5_b6_complete_four_hundred_forty_fifth"

COMPOSITIONS = {
    "601b77449028deed39de": ("OT+CHD+DY", "danach umsetzen; Schluss"),
    "00d8ebe3c68294eeac39": ("CHD+AL", "an der Stelle umsetzen"),
    "fcc1deda9e24ec268eb0": ("AIIIN_GRADE_2", "zweite Stufe"),
    "1bfd786e6b8b63734a59": ("SOLK+EE+Y", "laenger auffangen"),
    "3e9c7f217843b588489d": ("RAL+Y", "dies abkuehlen"),
    "97ddca78c9ebcc956d04": ("L_TRANSFER+AL+OR", "Ansatz zur Stelle fuehren"),
}

WHOLES = {
    "8c97dfde96fbc78e3355": "warm",
    "43eb9aa12959b4d5cdc9": "roh",
}

FLUENT = {
    "B5-S001": "Danach umsetzen und schliessen.",
    "B5-S002": "Den Ansatz umsetzen und schliessen.",
    "B5-S003": "An der Absetzstelle weiterfuehren, warm halten, an dieser Stelle umsetzen, auf Mass bringen, fortsetzen, die zweite Stufe einstellen und den laufenden Posten umsetzen.",
    "B6-S001": "Den Rohansatz laenger auffangen, diesen abkuehlen und fortsetzen; auf Mass bringen, durch das Tuch fuehren und den Ansatz zur bezeichneten Stelle fuehren.",
}


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_FORTY_FIFTH_B5_B6_20_EVENT_INTERLINEAR.tsv")
    for row in events:
        joint_id = row["joint_tuple_id"]
        if joint_id in COMPOSITIONS:
            row["small_value_de"] = COMPOSITIONS[joint_id][1]
            row["lexicon_source"] = "B5_B6_PRODUCTIVE_COMPOSITION"
        elif joint_id in WHOLES:
            row["small_value_de"] = WHOLES[joint_id]
            row["lexicon_source"] = "B5_B6_LOCAL_WHOLE_CARD"
    write("FOUR_HUNDRED_FORTY_SIXTH_FINAL_20_EVENTS.tsv", events)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        statements.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "card_sequence_de": " > ".join(row["small_value_de"] for row in rows),
            "continuous_reading_de": FLUENT[statement_id],
            "record_restart_before": "YES" if statement_id == "B6-S001" else "NO",
        })
    write("FOUR_HUNDRED_FORTY_SIXTH_FINAL_FOUR_STATEMENTS.tsv", statements)

    composition_rows = []
    for joint_id, (composition, value) in COMPOSITIONS.items():
        row = next(row for row in events if row["joint_tuple_id"] == joint_id)
        composition_rows.append({
            "record_unit_id": row["record_unit_id"],
            "event_id": row["event_id"],
            "surface": row["surface"],
            "joint_tuple_id": joint_id,
            "composition": composition,
            "small_value_de": value,
            "removed_old_overreading": {
                "fcc1deda9e24ec268eb0": "Oeffnung",
                "3e9c7f217843b588489d": "erste Oeffnung",
                "97ddca78c9ebcc956d04": "bloss bezeichnete Stelle",
            }.get(joint_id, "NONE"),
        })
    write("FOUR_HUNDRED_FORTY_SIXTH_SIX_NEW_COMPOSITIONS.tsv", composition_rows)

    whole_rows = []
    for joint_id, value in WHOLES.items():
        row = next(row for row in events if row["joint_tuple_id"] == joint_id)
        whole_rows.append({
            "record_unit_id": row["record_unit_id"],
            "event_id": row["event_id"],
            "surface": row["surface"],
            "joint_tuple_id": joint_id,
            "small_value_de": value,
            "why_not_segmented": "keine portable Innenwurzel; kurze gelernte Zustandskarte",
        })
    write("FOUR_HUNDRED_FORTY_SIXTH_TWO_LOCAL_WHOLE_CARDS.tsv", whole_rows)

    first_order = {joint_id: min(int(row["order"]) for row in events if row["joint_tuple_id"] == joint_id) for joint_id in {row["joint_tuple_id"] for row in events}}
    dictionary = []
    for joint_id in sorted(first_order, key=first_order.get):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        if joint_id in COMPOSITIONS:
            drawer = "B5_B6_PRODUCTIVE_COMPOSITION"
            composition = COMPOSITIONS[joint_id][0]
        elif joint_id in WHOLES:
            drawer = "B5_B6_LOCAL_WHOLE_CARD"
            composition = "MEMORIZED"
        else:
            drawer = "B1_B2_B3_B4_TRANSFER"
            composition = "TRANSFERRED_AS_UNIT"
        dictionary.append({
            "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows),
            "records": "|".join(sorted({row["record_unit_id"] for row in rows})),
            "drawer": drawer,
            "composition": composition,
            "small_values_de": "|".join(sorted({row["small_value_de"] for row in rows})),
        })
    write("FOUR_HUNDRED_FORTY_SIXTH_FINAL_16_CARD_DICTIONARY.tsv", dictionary)

    pocket = [
        "# B5/B6 pocket dictionary",
        "",
        "## Productive additions",
        "",
        "- OT+CHD+DY = danach umsetzen; Schluss",
        "- CHD+AL = an der Stelle umsetzen",
        "- AIIIN = zweite Stufe",
        "- SOLK+EE+Y = laenger auffangen",
        "- RAL+Y = dies abkuehlen",
        "- L...+AL+OR = Ansatz zur Stelle fuehren",
        "",
        "## Learned whole cards",
        "",
        "- LOL = warm",
        "- QEKY = roh",
        "",
        "B6 starts a new record. No state crosses E372 -> E373.",
    ]
    (HERE / "FOUR_HUNDRED_FORTY_SIXTH_POCKET_DICTIONARY.md").write_text("\n".join(pocket) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "cards": len(dictionary),
        "transfer_cards": sum(row["drawer"] == "B1_B2_B3_B4_TRANSFER" for row in dictionary),
        "productive_cards": sum(row["drawer"] == "B5_B6_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "local_whole_cards": sum(row["drawer"] == "B5_B6_LOCAL_WHOLE_CARD" for row in dictionary),
        "transfer_events": sum(int(row["events"]) for row in dictionary if row["drawer"] == "B1_B2_B3_B4_TRANSFER"),
        "productive_events": sum(int(row["events"]) for row in dictionary if row["drawer"] == "B5_B6_PRODUCTIVE_COMPOSITION"),
        "local_whole_events": sum(int(row["events"]) for row in dictionary if row["drawer"] == "B5_B6_LOCAL_WHOLE_CARD"),
    }
    (HERE / "FOUR_HUNDRED_FORTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

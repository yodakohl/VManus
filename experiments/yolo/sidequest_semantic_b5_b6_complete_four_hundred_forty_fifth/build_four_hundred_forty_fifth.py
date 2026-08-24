#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

DECKS = (
    ("B1", ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv", "small_value_de"),
    ("B2", ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_46_CARD_DICTIONARY.tsv", "small_values_de"),
    ("B3", ROOT / "experiments/yolo/sidequest_semantic_b3_local_tournament_four_hundred_forty_second/FOUR_HUNDRED_FORTY_SECOND_FINAL_B3_52_CARD_DICTIONARY.tsv", "small_values_de"),
    ("B4", ROOT / "experiments/yolo/sidequest_semantic_b4_productive_completion_four_hundred_forty_fourth/FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_34_CARD_DICTIONARY.tsv", "small_values_de"),
)

NEW_VALUES = {
    "601b77449028deed39de": "Folgeumsetzung; Schluss",
    "8c97dfde96fbc78e3355": "warm",
    "00d8ebe3c68294eeac39": "an der Stelle umsetzen",
    "fcc1deda9e24ec268eb0": "zweite Oeffnungsstufe",
    "1bfd786e6b8b63734a59": "laenger auffangen",
    "43eb9aa12959b4d5cdc9": "roh",
    "3e9c7f217843b588489d": "erste Oeffnung",
    "97ddca78c9ebcc956d04": "bezeichnete Stelle",
}

FLUENT = {
    "B5-S001": "Die Folgeumsetzung ausfuehren und schliessen.",
    "B5-S002": "Den Ansatz umsetzen und schliessen.",
    "B5-S003": "An der Stelle absetzen, die Stelle halten und fortsetzen, warm halten, an der Stelle umsetzen, auf Mass bringen, fortsetzen, die zweite Oeffnungsstufe setzen und dies umsetzen.",
    "B6-S001": "Laenger auffangen; den rohen Posten an der ersten Oeffnung fortsetzen, auf Mass bringen, weiterfuehren, durch das Tuch fuehren, dies an die bezeichnete Stelle bringen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {name}")
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    prior: dict[str, tuple[str, str]] = {}
    surfaces: dict[str, set[str]] = defaultdict(set)
    for deck, path, value_column in DECKS:
        for row in read(path):
            prior[row["joint_tuple_id"]] = (deck, row[value_column])
            surfaces[row["joint_tuple_id"]].update(row["surfaces"].split("|"))

    source = [row for row in read(BASE) if row["record_unit_id"] in {"B5", "B6"}]
    events: list[dict[str, object]] = []
    for order, row in enumerate(source, 1):
        joint_id = row["joint_tuple_id"]
        if joint_id in prior:
            deck, value = prior[joint_id]
            lexicon_source = f"{deck}_LATEST_PRIOR_TRANSFER"
        else:
            deck, value = "NONE", NEW_VALUES[joint_id]
            lexicon_source = f"{row['record_unit_id']}_LOCAL_UNANALYSED_CARD"
        events.append({
            "order": order,
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface_display"],
            "joint_tuple_id": joint_id,
            "small_value_de": value,
            "lexicon_source": lexicon_source,
            "record_restart_before": "YES" if row["event_id"] == "E373" else "NO",
        })
    write("FOUR_HUNDRED_FORTY_FIFTH_B5_B6_20_EVENT_INTERLINEAR.tsv", events)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_statement[str(row["statement_id"])].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        statements.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "events": len(rows),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "fields": "|".join(dict.fromkeys(str(row["field_id"]) for row in rows)),
            "card_sequence_de": " > ".join(str(row["small_value_de"]) for row in rows),
            "continuous_reading_de": FLUENT[statement_id],
            "record_restart_before": "YES" if statement_id == "B6-S001" else "NO",
        })
    write("FOUR_HUNDRED_FORTY_FIFTH_FOUR_STATEMENTS.tsv", statements)

    prior_ids = sorted({str(row["joint_tuple_id"]) for row in events if str(row["joint_tuple_id"]) in prior}, key=lambda joint_id: min(int(row["order"]) for row in events if row["joint_tuple_id"] == joint_id))
    transfer_rows = []
    for joint_id in prior_ids:
        matching = [row for row in events if row["joint_tuple_id"] == joint_id]
        transfer_rows.append({
            "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({str(row["surface"]) for row in matching})),
            "events": len(matching),
            "event_ids": "|".join(str(row["event_id"]) for row in matching),
            "latest_source_deck": prior[joint_id][0],
            "fixed_value_de": prior[joint_id][1],
        })
    write("FOUR_HUNDRED_FORTY_FIFTH_EIGHT_PRIOR_TRANSFERS.tsv", transfer_rows)

    new_rows = []
    for joint_id in NEW_VALUES:
        matching = [row for row in events if row["joint_tuple_id"] == joint_id]
        new_rows.append({
            "record_unit_id": matching[0]["record_unit_id"],
            "event_id": matching[0]["event_id"],
            "surface": matching[0]["surface"],
            "joint_tuple_id": joint_id,
            "current_local_value_de": NEW_VALUES[joint_id],
            "next_question": "PRODUCTIVE_OR_WHOLE_CARD",
        })
    write("FOUR_HUNDRED_FORTY_FIFTH_EIGHT_NEW_CARDS.tsv", new_rows)

    summary = {
        "status": "PASS",
        "records": 2,
        "events": len(events),
        "statements": len(statements),
        "unique_cards": len({row["joint_tuple_id"] for row in events}),
        "prior_transfer_cards": len(transfer_rows),
        "prior_transfer_events": sum(int(row["events"]) for row in transfer_rows),
        "new_cards": len(new_rows),
        "new_events": sum(1 for row in events if row["joint_tuple_id"] in NEW_VALUES),
        "record_restart": "E372_TO_E373",
    }
    (HERE / "FOUR_HUNDRED_FORTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

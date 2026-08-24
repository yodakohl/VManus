#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_biological_local_cleanup_four_hundred_forty_eighth"

PROMOTIONS = {
    "1645e612504fcef59ced": ("OK+AIN", "eine Portion zugeben"),
    "87411f84689b4f93a303": ("OK+CHD+DY", "Ansatz umsetzen; Schluss"),
    "07913ef9b1fb773cd325": ("OK+CHED+DY", "Ansatz umsetzen; Schluss"),
    "a7af89ab31ce5e247395": ("Y+T+E+Y", "dies kurz fuellen"),
    "a8f891de626fc00028e9": ("O+CTH+E+OL", "kurz bereit fortsetzen"),
    "348e81ba084c5acdb32b": ("SH+E+CTH+ED+CHY", "dies kurz bereit umsetzen"),
    "80ebbbbf238eee9f0aef": ("T+Y", "dies fuellen"),
}

FLUENT = {
    "B1-S015": "Dies kurz fuellen, den Ansatz umsetzen und schliessen.",
    "B2-S005": "Dies an die Stelle setzen, das Auffangmass einstellen, durchfuehren, zweimal bemessen, kurz bereit fortsetzen, dies laenger waermen, abfuehren und schliessen.",
    "B3-S011": "Dies kurz bereit umsetzen, verwenden, nochmals umsetzen und dies aus der Quelle nehmen.",
    "B3-S034": "Auf Sollstand bringen, bereitstellen, dies fuellen, das naechste Mass nehmen, dies an der Stelle fortsetzen, kurz absetzen und schliessen.",
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
    events = read("FOUR_HUNDRED_FORTY_EIGHTH_281_EVENT_EDITION.tsv")
    for row in events:
        if row["joint_tuple_id"] in PROMOTIONS:
            row["small_value_de"] = PROMOTIONS[row["joint_tuple_id"]][1]
            row["union_drawer"] = "PRODUCTIVE_COMPOSITION"
    write("FOUR_HUNDRED_FORTY_NINTH_281_EVENT_EDITION.tsv", events)

    dictionary = read("FOUR_HUNDRED_FORTY_EIGHTH_124_CARD_DICTIONARY.tsv")
    values = {row["joint_tuple_id"]: row["small_value_de"] for row in events}
    for row in dictionary:
        if row["joint_tuple_id"] in PROMOTIONS:
            row["small_value_de"] = values[row["joint_tuple_id"]]
            row["union_drawer"] = "PRODUCTIVE_COMPOSITION"
            row["origin_drawer"] = "PASS449_WHOLE_CARD_PROMOTION"
    write("FOUR_HUNDRED_FORTY_NINTH_124_CARD_DICTIONARY.tsv", dictionary)

    event_by_id = {row["event_id"]: row for row in events}
    statements = read("FOUR_HUNDRED_FORTY_EIGHTH_97_STATEMENT_EDITION.tsv")
    for row in statements:
        statement_events = [event_by_id[event_id] for event_id in row["event_ids"].split("|")]
        row["card_sequence_de"] = " > ".join(event["small_value_de"] for event in statement_events)
        if row["statement_id"] in FLUENT:
            row["continuous_reading_de"] = FLUENT[row["statement_id"]]
    write("FOUR_HUNDRED_FORTY_NINTH_97_STATEMENT_EDITION.tsv", statements)

    promotion_rows = []
    previous_cards = {row["joint_tuple_id"]: row for row in read("FOUR_HUNDRED_FORTY_EIGHTH_124_CARD_DICTIONARY.tsv")}
    for joint_id, (composition, value) in PROMOTIONS.items():
        old = previous_cards[joint_id]
        promotion_rows.append({
            "joint_tuple_id": joint_id, "surfaces": old["surfaces"], "events": old["events"],
            "event_ids": old["event_ids"], "previous_drawer": old["union_drawer"],
            "composition": composition, "previous_value_de": old["small_value_de"], "selected_value_de": value,
        })
    write("FOUR_HUNDRED_FORTY_NINTH_SEVEN_PROMOTIONS.tsv", promotion_rows)

    residual = [row for row in dictionary if row["union_drawer"] != "PRODUCTIVE_COMPOSITION"]
    for row in residual:
        row["memorization_rule"] = "LEARN_EXACT_CARD_AS_ONE_SHORT_WORD"
    write("FOUR_HUNDRED_FORTY_NINTH_SIX_WHOLE_CARDS.tsv", residual)

    root_rows = [
        {"root": "T", "value_de": "fuellen", "forms": "YTEY|CHETY", "contrast": "E grades the short YTEY form"},
        {"root": "CTH", "value_de": "bereit", "forms": "OCTHEOL|SHECTHEDCHY", "contrast": "OL continues; CHD transfers"},
        {"root": "OK", "value_de": "ansetzen", "forms": "OKAIN|QOKCHDY|OKCHEDY", "contrast": "argument AIN or operation CHD/CHED"},
    ]
    write("FOUR_HUNDRED_FORTY_NINTH_THREE_CLOSING_PARADIGMS.tsv", root_rows)

    summary = {
        "status": "PASS", "cards": len(dictionary), "events": len(events), "statements": len(statements),
        "promotions": len(PROMOTIONS), "productive_cards": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in dictionary),
        "portable_whole_cards": sum(row["union_drawer"] == "PORTABLE_LEARNED_WHOLE_CARD" for row in dictionary),
        "local_whole_cards": sum(row["union_drawer"] == "RECORD_LOCAL_LEARNED_WHOLE_CARD" for row in dictionary),
        "productive_events": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in events),
        "whole_card_events": sum(row["union_drawer"] != "PRODUCTIVE_COMPOSITION" for row in events),
    }
    (HERE / "FOUR_HUNDRED_FORTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

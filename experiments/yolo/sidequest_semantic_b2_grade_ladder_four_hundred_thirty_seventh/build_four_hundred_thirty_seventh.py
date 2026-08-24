#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b2_directional_composition_four_hundred_thirty_sixth"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_THIRTY_SIXTH_REVISED_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_SIXTH_REVISED_B2_22_STATEMENTS.tsv")
    grades = {
        "08bd5ca0c2ad137a056d": ("OK+E+Y", "ANSETZEN", "KURZ", "OPEN", "kurz ansetzen", "B1_TRANSFER"),
        "0275fbf14e07935b0a45": ("OK+EE+Y", "ANSETZEN", "LAENGER", "OPEN", "länger ansetzen", "B1_TRANSFER"),
        "7d25241b0e56c836372a": ("OK+EE+DY", "ANSETZEN", "LAENGER", "CLOSE", "länger ansetzen; Schluss", "B2_NEW"),
        "d25110e0d8488927278f": ("OK+EEE+DY", "ANSETZEN", "VOLL", "CLOSE", "vollständig ansetzen; Schluss", "B2_NEW"),
        "5d5e0b288cf36864ed9d": ("OT+EE+Y", "HALTEN", "LAENGER", "OPEN", "nächsten Posten länger halten", "B2_NEW"),
        "ff178343c18e287ce3b7": ("OT+EE+DY", "HALTEN", "LAENGER", "CLOSE", "nächsten Schritt länger halten; Schluss", "B2_NEW"),
        "f0db6d30cd34f4cb2a4d": ("CHK+EE+Y", "WAERMEN", "LAENGER", "OPEN", "dies länger wärmen", "B2_NEW"),
        "6b89d6dd70635bc60fe0": ("CTH+E+Y", "BEREITHALTEN", "KURZ", "OPEN", "dies kurz bereithalten", "B2_NEW"),
    }
    for row in events:
        if row["joint_tuple_id"] in grades:
            row["small_value_de"] = grades[row["joint_tuple_id"]][4]
            if grades[row["joint_tuple_id"]][5] == "B2_NEW":
                row["lexicon_source"] = "B2_PREDICTED_GRADE_COMPOSITION"
    write("FOUR_HUNDRED_THIRTY_SEVENTH_REVISED_B2_62_EVENTS.tsv", events)

    fluent = {
        "B2-S005": "Dies an die Stelle setzen, durch Seihtuch und Durchlass führen, bemessen, dieselbe Einstellung halten, dies länger wärmen, abziehen und schließen.",
        "B2-S006": "Den nächsten Posten länger halten, an die Stelle setzen, kurz durchführen und verwenden.",
        "B2-S012": "Dies abziehen, den Klarauszug kurz bereithalten, länger ansetzen, die benetzte Stelle auf Maß bringen, dies vollständig ansetzen und schließen.",
        "B2-S016": "An der Stelle von dort hinausführen, gleiche Anteile und Maß setzen, den nächsten Posten länger halten, bemessen, kurz ansetzen, hineinführen und schließen.",
        "B2-S020": "Den nächsten Schritt länger halten und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_THIRTY_SEVENTH_REVISED_B2_22_STATEMENTS.tsv", statements)

    ladder = []
    for joint_id, (composition, operation, grade, endpoint, value, source) in grades.items():
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        ladder.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "composition": composition, "operation": operation, "grade": grade,
            "endpoint": endpoint, "small_value_de": value, "source": source,
        })
    write("FOUR_HUNDRED_THIRTY_SEVENTH_B2_GRADE_LADDER.tsv", ladder)

    dictionary = read("FOUR_HUNDRED_THIRTY_SIXTH_B2_46_CARD_DICTIONARY.tsv")
    new_ids = {joint_id for joint_id, row in grades.items() if row[5] == "B2_NEW"}
    event_by_card: dict[str, list[dict[str, str]]] = {}
    for row in events:
        event_by_card.setdefault(row["joint_tuple_id"], []).append(row)
    for row in dictionary:
        if row["joint_tuple_id"] in new_ids:
            row["drawer"] = "B2_PRODUCTIVE_COMPOSITION"
            row["small_values_de"] = "|".join(sorted({event["small_value_de"] for event in event_by_card[row["joint_tuple_id"]]}))
    write("FOUR_HUNDRED_THIRTY_SEVENTH_B2_46_CARD_DICTIONARY.tsv", dictionary)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements),
        "grade_cards": len(ladder), "grade_events": sum(int(row["events"]) for row in ladder),
        "new_grade_compositions": len(new_ids),
        "B2_productive_cards": sum(row["drawer"] == "B2_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "B2_local_cards": sum(row["drawer"] == "B2_LOCAL_WHOLE_CARD" for row in dictionary),
    }
    (HERE / "FOUR_HUNDRED_THIRTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

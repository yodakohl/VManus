#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b4_station_article_four_hundred_forty_third"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_FORTY_THIRD_B4_47_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_FORTY_THIRD_B4_16_STATEMENTS.tsv")
    transfer = read("FOUR_HUNDRED_FORTY_THIRD_NINETEEN_B1_B2_B3_TRANSFERS.tsv")
    compositions = {
        "1b1ffdd869fb1429ad03": ("OL+DY", "fortsetzen; Schluss"),
        "21ed2873b71e57269c08": ("CH+CKH+AL", "Durchlassstelle"),
        "232195d6ff2f326322f7": ("OK+OL", "Fortsetzung einsetzen"),
        "2c1a5fd92b9e3c762242": ("CHK+EE+Y", "dies länger wärmen"),
        "42cdc187d5b9ffc60063": ("SOLK+E+Y", "kurz auffangen"),
        "8aedd154964a78e555d6": ("D+AIR+Y+DY", "Laufflüssigkeit abschließen"),
        "92e43836d82f98bf02d3": ("SH+EE+Y", "dies länger halten"),
        "b958a512ca6a3559e86e": ("L+K+E+DY", "kurz abführen; Schluss"),
        "daf32e6db9e04413ce7f": ("OK+EE+OL", "länger fortsetzen"),
        "e2eb77ca9d9e1a8ba29a": ("OL+CHE+Y", "dies weiterführen"),
        "eb2e4bc143f623ee03ac": ("OK+Y+LDDY", "dies befestigen; Schluss"),
        "ecce30bc8dcc400bf2c8": ("O+CKH+E+Y", "dies kurz durchführen"),
        "faf321940aed922846a9": ("OT+CHEY", "nächster Posten"),
    }
    local_values = {
        "53cd0637c6820ba5e91f": "Tuch",
        "883a6708116c342cb10b": "Ausguss",
    }
    for row in events:
        if row["joint_tuple_id"] in compositions:
            row["small_value_de"] = compositions[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "B4_PREDICTED_PRODUCTIVE_COMPOSITION"
        elif row["joint_tuple_id"] in local_values:
            row["small_value_de"] = local_values[row["joint_tuple_id"]]
            row["lexicon_source"] = "B4_LOCAL_WHOLE_CARD"
    write("FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_47_EVENTS.tsv", events)

    fluent = {
        "B4-S002": "Dies weiterführen, länger ansetzen, dann kurz ansetzen und schließen.",
        "B4-S003": "Dies umsetzen, an die Folgestelle gehen, den nächsten Posten länger ansetzen, dies verwenden, fortsetzen, kurz absetzen und schließen.",
        "B4-S004": "Dies befestigen und schließen.",
        "B4-S005": "Durch das Tuch führen, dies umsetzen, länger ansetzen und schließen.",
        "B4-S008": "Auf Maß bringen, dies länger wärmen und halten, kurz ansetzen und schließen.",
        "B4-S010": "Fortsetzen und schließen.",
        "B4-S011": "Auf Maß bringen, kurz wärmen, länger fortsetzen, eine Portion zugeben, dies umsetzen, fortsetzen, kurz abführen und schließen.",
        "B4-S013": "Die Fortsetzung einsetzen, kurz absetzen und schließen.",
        "B4-S014": "Den Ansatz und diesen Posten kurz durchführen, die Laufflüssigkeit abschließen.",
        "B4-S015": "Eine Portion und den Klarauszug mit einer weiteren Portion zur Durchlassstelle bringen; nach dem Besitzerwechsel kurz auffangen, hinausführen und schließen.",
        "B4-S016": "Eine weitere Portion an die Stelle und zum Ausguss geben, kurz absetzen und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_16_STATEMENTS.tsv", statements)

    table = []
    for joint_id, (composition, value) in compositions.items():
        row = [row for row in events if row["joint_tuple_id"] == joint_id][0]
        table.append({
            "event_id": row["event_id"], "surface": row["surface"], "joint_tuple_id": joint_id,
            "composition": composition, "small_value_de": value,
        })
    write("FOUR_HUNDRED_FORTY_FOURTH_THIRTEEN_NEW_COMPOSITIONS.tsv", table)

    local = []
    for joint_id, value in local_values.items():
        row = [row for row in events if row["joint_tuple_id"] == joint_id][0]
        local.append({"event_id": row["event_id"], "surface": row["surface"], "joint_tuple_id": joint_id, "small_value_de": value})
    write("FOUR_HUNDRED_FORTY_FOURTH_TWO_LOCAL_WHOLE_CARDS.tsv", local)

    transferred_ids = {row["joint_tuple_id"] for row in transfer}
    dictionary = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events}, key=lambda jid: min(int(row["order"]) for row in events if row["joint_tuple_id"] == jid)):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        drawer = "B1_B2_B3_TRANSFER" if joint_id in transferred_ids else ("B4_PRODUCTIVE_COMPOSITION" if joint_id in compositions else "B4_LOCAL_WHOLE_CARD")
        dictionary.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "drawer": drawer, "small_values_de": "|".join(sorted({row["small_value_de"] for row in rows})),
        })
    write("FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_34_CARD_DICTIONARY.tsv", dictionary)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "cards": len(dictionary),
        "transfer_cards": sum(row["drawer"] == "B1_B2_B3_TRANSFER" for row in dictionary),
        "productive_cards": sum(row["drawer"] == "B4_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "local_cards": sum(row["drawer"] == "B4_LOCAL_WHOLE_CARD" for row in dictionary),
        "transfer_events": sum(int(row["events"]) for row in dictionary if row["drawer"] == "B1_B2_B3_TRANSFER"),
        "productive_events": sum(int(row["events"]) for row in dictionary if row["drawer"] == "B4_PRODUCTIVE_COMPOSITION"),
        "local_events": sum(int(row["events"]) for row in dictionary if row["drawer"] == "B4_LOCAL_WHOLE_CARD"),
    }
    (HERE / "FOUR_HUNDRED_FORTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

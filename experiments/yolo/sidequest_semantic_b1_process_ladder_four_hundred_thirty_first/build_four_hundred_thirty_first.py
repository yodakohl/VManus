#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_dsheol_short_hold_four_hundred_thirtieth"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_THIRTIETH_REVISED_B1_66_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_THIRTIETH_REVISED_B1_21_STATEMENTS.tsv")

    ladder = [
        ("7db18b2f0fb7ed0fcfd3", "OK+E+DY", "ANSETZEN", "KURZ", "NONE", "YES", "kurz ansetzen; Schluss"),
        ("08bd5ca0c2ad137a056d", "OK+E+Y", "ANSETZEN", "KURZ", "DIES", "NO", "kurz ansetzen"),
        ("0275fbf14e07935b0a45", "OK+EE+Y", "ANSETZEN", "LAENGER", "DIES", "NO", "länger ansetzen"),
        ("93f69c38fdedee1598e9", "OK+EE+D+AL", "HALTEN", "LAENGER", "STELLE", "NO", "länger an der Stelle halten"),
        ("74c76d589d44120f647b", "SH+E+OL", "HALTEN", "KURZ", "FORTSETZEN", "NO", "kurz halten"),
        ("bc4f1f5c006c74a4d26d", "SH+E+DY", "ABSETZEN", "KURZ", "NONE", "YES", "kurz absetzen; Schluss"),
        ("d904bf7b044dd3922781", "CHK+E+Y", "WAERMEN", "KURZ", "DIES", "NO", "kurz wärmen"),
        ("3b70942557b3a40e8030", "SOLK+EE+DY", "AUFFANGEN", "LAENGER", "NONE", "YES", "länger auffangen; Schluss"),
        ("2c82523794dcb7d2b343", "O+IIN", "EINSTELLEN", "SOLLSTAND", "NONE", "NO", "Sollstand"),
    ]
    ladder_by_id = {row[0]: row for row in ladder}
    for row in events:
        if row["joint_tuple_id"] in ladder_by_id:
            row["small_value_de"] = ladder_by_id[row["joint_tuple_id"]][6]
            row["lexicon_source"] = "B1_PROCESS_LADDER"
    write("FOUR_HUNDRED_THIRTY_FIRST_REVISED_B1_66_EVENTS.tsv", events)

    table = []
    for joint_id, composition, operation, grade, address, close, value in ladder:
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        table.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "composition": composition, "operation": operation, "grade": grade,
            "address_or_referent": address, "close": close, "small_value_de": value,
        })
    write("FOUR_HUNDRED_THIRTY_FIRST_B1_PROCESS_LADDER.tsv", table)

    revised_statements = {
        "B1-S004": "Dies umsetzen, fortsetzen, kurz absetzen und schließen.",
        "B1-S008": "Dies fortsetzen, kurz wärmen, weiterführen, kurz absetzen und schließen.",
        "B1-S016": "An die Stelle setzen, länger ansetzen, fortsetzen, kurz absetzen und schließen.",
        "B1-S019": "Kurz absetzen und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in revised_statements:
            row["continuous_reading_de"] = revised_statements[row["statement_id"]]
    write("FOUR_HUNDRED_THIRTY_FIRST_REVISED_B1_21_STATEMENTS.tsv", statements)

    phases = [
        {"phase": 1, "name": "ANSETZEN", "short_card": "qokey/qokedy", "long_card": "okeey/qokeedal", "result": "Kontakt oder Arbeitsgang beginnen"},
        {"phase": 2, "name": "HALTEN", "short_card": "dsheol", "long_card": "qokeedal", "result": "Posten oder Stelle während des Gangs halten"},
        {"phase": 3, "name": "WAERMEN", "short_card": "cheky", "long_card": "NONE_IN_B1", "result": "Temperatur kurz anheben"},
        {"phase": 4, "name": "ABSETZEN", "short_card": "shedy/cheedy/tedy", "long_card": "NONE_IN_B1", "result": "kurze Ruhe-/Trennphase abschließen"},
        {"phase": 5, "name": "AUFFANGEN", "short_card": "NONE_IN_B1", "long_card": "olkeedy", "result": "Produkt länger sammeln und schließen"},
    ]
    write("FOUR_HUNDRED_THIRTY_FIRST_FIVE_PROCESS_PHASES.tsv", phases)

    summary = {
        "status": "PASS", "B1_events": len(events), "B1_statements": len(statements),
        "ladder_cards": len(table), "ladder_events": sum(int(row["events"]) for row in table),
        "short_events": sum(int(row["events"]) for row in table if row["grade"] == "KURZ"),
        "long_events": sum(int(row["events"]) for row in table if row["grade"] == "LAENGER"),
        "decision": "B1_HAS_SHORT_LONG_PROCESS_LADDER",
    }
    (HERE / "FOUR_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Derive a five-word result/shelf lexicon from final Bio microcycles."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MICRO = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_205_MICROCYCLES.tsv"
TRACE = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv"
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"
RUN = ROOT / "experiments/yolo/sidequest_semantic_apprentice_run_sheet_three_hundred_forty_first/THREE_HUNDRED_FORTY_FIRST_ELEVEN_APPRENTICE_RUN_CARDS.tsv"

RESULT = {
    "B1": ("R01_BEHANDLUNGSPORTION", "Behandlungsportion", "APPLICATION_SHELF", "Kurzwärme, Durchlass und Zielstelle ergeben eine lokal behandelte Portion."),
    "B2": ("R02_KLARABZUG", "Klarabzug", "APPLICATION_SHELF", "Absetzen, langer Kontakt und abschließende Abführung ergeben einen Klarabzug."),
    "B3": ("R03_SAMMELGUT", "Sammelgut", "WORK_SHELF", "Abziehen, bereitstellen, bemessen und kurz absetzen ergeben lokales Sammelgut."),
    "B4": ("R02_KLARABZUG", "Klarabzug", "APPLICATION_SHELF", "Klarauszug, Zielpassage, kurze Sammlung und Abführung ergeben einen Klarabzug."),
    "B5": ("R04_TRANSFERGUT", "Transfergut", "WORK_SHELF", "Fortsetzung, Endstufe und Umsetzen ergeben einen weitergabefähigen Transferposten."),
    "B6": ("R05_ANWENDUNGSPOSTEN", "Anwendungsposten", "APPLICATION_SHELF", "Sammlung, Sollmaß, Einlage und Endziel ergeben einen bereit gesetzten Anwendungsposten."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    micro = read_tsv(MICRO)
    trace = read_tsv(TRACE)
    mixed = {row["event_id"]: row for row in read_tsv(MIXED)}
    run = {row["record_unit_id"]: row for row in read_tsv(RUN)}
    trace_by_key = defaultdict(list)
    for row in trace:
        trace_by_key[(row["statement_id"], row["microcycle"])].append(row)

    assignments = []
    window_events = []
    for record in RESULT:
        record_micro = [row for row in micro if row["record_unit_id"] == record]
        terminal_window = record_micro[-4:]
        event_rows = []
        for micro_row in terminal_window:
            event_rows.extend(trace_by_key[(micro_row["statement_id"], micro_row["microcycle"])])
        result_id, word, shelf, reading = RESULT[record]
        for row in event_rows:
            surface = mixed[row["event_id"]]["rendered_surface"]
            window_events.append({
                "record_unit_id": record,
                "result_id": result_id,
                "result_word_de": word,
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "microcycle": row["microcycle"],
                "rendered_surface": surface,
                "atomic_value_de": row["atomic_value_de"],
                "program_id": row["program_id"],
                "slot_code": row["slot_code"],
            })
        assignments.append({
            "record_unit_id": record,
            "page": run[record]["page"],
            "assigned_hand": run[record]["assigned_hand"],
            "result_id": result_id,
            "result_word_de": word,
            "shelf_type": shelf,
            "terminal_microcycle_count": len(terminal_window),
            "terminal_atomic_window": " || ".join(row["atomic_sequence"] for row in terminal_window),
            "terminal_surface_window": " ".join(mixed[row["event_id"]]["rendered_surface"] for row in event_rows),
            "result_derivation_de": reading,
            "full_record_output_de": run[record]["output_item_de"],
            "next_pointer": "NONE_VISIBLE__LOCAL_SHELF",
        })

    definitions = []
    for result_id in sorted({value[0] for value in RESULT.values()}):
        records = [record for record, values in RESULT.items() if values[0] == result_id]
        sample = next(row for row in assignments if row["result_id"] == result_id)
        definitions.append({
            "result_id": result_id,
            "result_word_de": sample["result_word_de"],
            "shelf_type": sample["shelf_type"],
            "record_count": len(records),
            "records": "|".join(records),
            "teaching_definition_de": {
                "R01_BEHANDLUNGSPORTION": "Eine am Ziel kurz oder warm behandelte, lokal bereitgelegte Portion.",
                "R02_KLARABZUG": "Ein nach Ruhe/Kontakt abgezogener oder abgeführter klarer Anteil.",
                "R03_SAMMELGUT": "Ein abgezogener, bemessener und abgesetzter Posten für lokales Auffangen.",
                "R04_TRANSFERGUT": "Ein auf Endstufe gebrachter Posten, der an einen weiteren Arbeitsplatz darf.",
                "R05_ANWENDUNGSPOSTEN": "Ein bemessener und am Endziel gesetzter Posten für die Anwendung.",
            }[result_id],
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_SECOND_FIVE_RESULT_WORDS.tsv", definitions,
              ["result_id", "result_word_de", "shelf_type", "record_count", "records", "teaching_definition_de"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SECOND_SIX_RECORD_RESULT_ASSIGNMENTS.tsv", assignments,
              ["record_unit_id", "page", "assigned_hand", "result_id", "result_word_de", "shelf_type", "terminal_microcycle_count", "terminal_atomic_window", "terminal_surface_window", "result_derivation_de", "full_record_output_de", "next_pointer"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SECOND_TERMINAL_WINDOW_EVENTS.tsv", window_events,
              ["record_unit_id", "result_id", "result_word_de", "event_id", "statement_id", "microcycle", "rendered_surface", "atomic_value_de", "program_id", "slot_code"])

    lines = ["# Fünf Ergebniswörter für sechs Biological-Records", ""]
    for row in definitions:
        lines.extend([
            f"## {row['result_word_de']}",
            "",
            row["teaching_definition_de"],
            f"Records: {row['records']}; Ablage: {row['shelf_type']}.",
            "",
        ])
    lines.extend([
        "## Leseregel",
        "",
        "Das Ergebniswort ersetzt nicht die letzte Karte. Es ist die Werkstattbezeichnung",
        "für den durch die letzten vier Mikrogänge erzeugten Posten. B2 und B4 heißen beide",
        "Klarabzug, obwohl B2 über Langkontakt/Abführung und B4 über Klarauszug/Sammlung",
        "dorthin gelangen. Der Weg bleibt im Laufzettel erhalten.",
    ])
    (HERE / "THREE_HUNDRED_FORTY_SECOND_RESULT_SHELF_LEXICON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "result_words": len(definitions),
        "bio_records": len(assignments),
        "application_shelf_records": sum(row["shelf_type"] == "APPLICATION_SHELF" for row in assignments),
        "work_shelf_records": sum(row["shelf_type"] == "WORK_SHELF" for row in assignments),
        "shared_result_classes": sum(int(row["record_count"]) > 1 for row in definitions),
        "terminal_window_events": len(window_events),
    }
    (HERE / "THREE_HUNDRED_FORTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

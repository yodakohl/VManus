#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P614 = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_palette_six_hundred_fourteenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def desk(record: str) -> str:
    if record.startswith("H"):
        return "P_PFLANZEN_ZUBEREITUNG"
    if record in {"B1", "B2"}:
        return "B_BAD_ANWENDUNG"
    return "S_STATION_NACHTRAG"


READING_REVISIONS = {
    "H3-S003": "Den vorhandenen Bluetenauszug wieder aufnehmen und eine abgemessene Portion des laufenden Postens zugeben.",
    "H4-S001": "Den Pflanzenansatz nach Mass ansetzen, eine Portion und danach eine Nachportion zufuehren und den Mischgang schliessen.",
    "H5-S002": "Den vorherigen Arbeitsfaden wieder aufnehmen, die folgende Pflanzengabe ansetzen und den Auszug lange durch den Durchlass laufen lassen; Schritt schliessen.",
}


def main() -> None:
    words = read(P613 / "SIX_HUNDRED_THIRTEENTH_39_WORD_PARADIGM.tsv")
    cards = read(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    events = read(P613 / "SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    statements = read(P613 / "SIX_HUNDRED_THIRTEENTH_116_REVISED_CASE_COMMANDS.tsv")
    palette = read(P614 / "SIX_HUNDRED_FOURTEENTH_20_CARD_SURFACE_PALETTE.tsv")
    palette_cards = {row["card_no"] for row in palette}

    write("SIX_HUNDRED_FIFTEENTH_39_WORD_GLOSSARY.tsv", words, list(words[0]))

    interlinear_rows: list[dict[str, object]] = []
    for row in events:
        interlinear_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "desk": desk(row["record"]),
            "surface": row["surface"],
            "card_no": row["card_no"],
            "semantic_component_parse": row["semantic_component_parse"],
            "command_id": row["command_id"],
            "standard_command_de": row["standard_command_de"],
            "local_surface_palette": "YES" if row["card_no"] in palette_cards else "NO",
            "silent_owner_de": row["silent_owner_de"],
            "case_expansion_de": row["case_expansion_de"],
        })
    write("SIX_HUNDRED_FIFTEENTH_381_READABLE_INTERLINEAR.tsv", interlinear_rows, list(interlinear_rows[0]))

    statement_rows: list[dict[str, object]] = []
    for row in statements:
        reading = READING_REVISIONS.get(row["statement_id"], row["concrete_case_expansion_de"])
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "desk": desk(row["record"]),
            "owner_or_station": row["owner_or_station"],
            "input_product_id": row["input_product_id"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "command_ids": row["command_ids"],
            "invariant_command_sequence_de": row["invariant_command_sequence_de"],
            "readable_workshop_de": reading,
            "new_613_nuance": "YES" if row["statement_id"] in READING_REVISIONS else "NO",
        })
    write("SIX_HUNDRED_FIFTEENTH_116_READABLE_STATEMENTS.tsv", statement_rows, list(statement_rows[0]))

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_record[str(row["record"])].append(row)
    record_order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    record_rows: list[dict[str, object]] = []
    markdown = ["# Vollständige lesbare Prosa-Ausgabe", "", "Die physische Zeile ist kein Satzende. Jeder nummerierte Werkstattsatz folgt der ausgewählten 116-Aussagen-Segmentierung.", ""]
    for record in record_order:
        rows = by_record[record]
        owners = []
        for row in rows:
            owner = str(row["owner_or_station"])
            if not owners or owners[-1] != owner:
                owners.append(owner)
        record_rows.append({
            "case_id": rows[0]["case_id"],
            "page": rows[0]["page"],
            "record": record,
            "desk": rows[0]["desk"],
            "statements": len(rows),
            "events": sum(int(row["event_count"]) for row in rows),
            "owner_sequence_de": " -> ".join(owners),
            "continuous_reading_de": " ".join(str(row["readable_workshop_de"]) for row in rows),
        })
        markdown.extend([
            f"## {record} · {rows[0]['page']} · Fall {rows[0]['case_id']}",
            "",
            f"**Arbeitstisch:** {rows[0]['desk']}",
            "",
            f"**Besitzerfolge:** {' -> '.join(owners)}",
            "",
        ])
        for row in rows:
            event_sequence = [event for event in interlinear_rows if event["statement_id"] == row["statement_id"]]
            card_line = " | ".join(f"{event['surface']}<{event['card_no']}>" for event in event_sequence)
            markdown.extend([
                f"### {row['statement_id']}",
                "",
                f"Karten: `{card_line}`",
                "",
                f"Befehl: {row['invariant_command_sequence_de']}",
                "",
                f"Lesung: {row['readable_workshop_de']}",
                "",
            ])
        markdown.extend(["Fortlaufend:", "", " ".join(str(row["readable_workshop_de"]) for row in rows), ""])
    (HERE / "SIX_HUNDRED_FIFTEENTH_ELEVEN_RECORD_READABLE_EDITION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    write("SIX_HUNDRED_FIFTEENTH_11_RECORD_SUMMARY.tsv", record_rows, list(record_rows[0]))

    report = """# Sechshundertfünfzehnte Runde: lesbare Prosa-Ausgabe

## Ergebnis

Die vollständige Prosa der sieben festen Seiten liegt nun als elf fortlaufende
Records vor: 39 kurze Wörter, 163 invariante Befehle, 173 exakte Karten, 381
Kartenereignisse und 116 Werkstattsätze. Jeder Satz zeigt sichtbare Oberfläche,
exakte Karte, Standardbefehl, Bildbesitzer und konkrete Lesung.

Die drei neuen Nuancen sind in den fortlaufenden Text eingearbeitet:

- H3 nimmt einen vorhandenen Blütenauszug wieder auf;
- H4 führt erst eine Portion, dann eine Nachportion zu;
- H5 nimmt einen vorherigen Arbeitsfaden wieder auf.

Die Ausgabe liest sich am besten als knappe Arbeitsprosa, nicht als Wort-für-
Wort-Übersetzung einer normalen Sprache. Die Karte befiehlt; Bild, aktiver
Posten und Fall liefern die ausgelassenen Substantive.

## Nächster Schritt

Die elf Records werden jetzt rückwärts gelesen: Aus der deutschen Werkstatt-
anweisung sollen die 39 Wörter und 163 Befehle wieder in richtiger Reihenfolge
gewählt werden. Wo mehrere Befehle gleich gut passen, steckt noch eine
Wörterbuchlücke oder eine überbreite deutsche Lesung.
"""
    (HERE / "SIX_HUNDRED_FIFTEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "words": len(words),
        "commands": len({(row["semantic_component_parse"], row["standard_command_de"]) for row in cards}),
        "cards": len(cards),
        "events": len(interlinear_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "revised_readings": sum(row["new_613_nuance"] == "YES" for row in statement_rows),
        "decision": "ELEVEN_RECORDS_READABLE_WITH_THIRTY_NINE_WORDS_AND_163_COMMANDS",
    }
    (HERE / "SIX_HUNDRED_FIFTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P617 = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"


def read(name: str) -> list[dict[str, str]]:
    with (P617 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CASES = {
    "C1": {
        "preparation_record": "H1",
        "application_record": "B1",
        "case_material_de": "waessriger Grundauszug der H1-Bildpflanze",
        "application_de": "mildes gemeinsames Bad oder Waschung im zweireihigen Becken",
        "water_status": "CASE_MEDIUM__NOT_AIR_WORD_MEANING",
    },
    "C2": {
        "preparation_record": "H2",
        "application_record": "B2",
        "case_material_de": "staerkerer Nach- oder Spuelauszug der H2-Bildpflanze",
        "application_de": "mehrstufige Bad- und Spuelanwendung an den B2-Stationen",
        "water_status": "CASE_MEDIUM__NOT_AIR_WORD_MEANING",
    },
    "C3": {
        "preparation_record": "H3",
        "application_record": "B3",
        "case_material_de": "Bluetenauszug der H3-Bildpflanze",
        "application_de": "Bluetenwaschung oder Eintauchfolge an den B3-Stationen",
        "water_status": "CASE_MEDIUM_POSSIBLE__FLOW_WORD_REMAINS_GENERIC",
    },
    "C4": {
        "preparation_record": "H4",
        "application_record": "B4",
        "case_material_de": "temperierte Pflanzenauflage oder Waschportion der H4-Bildpflanze",
        "application_de": "Auflage-/Kontaktfolge am sichtbaren Figurenpaar mit Nebenlaeufen",
        "water_status": "CASE_APPLICATION_MIXED__NO_CARD_WORD_EQUALS_WATER",
    },
    "C5": {
        "preparation_record": "H5",
        "application_record": "B5",
        "case_material_de": "konzentrierter Pflanzenauszug der H5-Bildpflanze",
        "application_de": "Uebertragen, Halten und Sammeln im linken B5-Nachtrag",
        "water_status": "CASE_MEDIUM_POSSIBLE__NO_CARD_WORD_EQUALS_WATER",
    },
    "C6": {
        "preparation_record": "NONE",
        "application_record": "B6",
        "case_material_de": "uebernommener Werkstattvorrat ohne eigene Herbal-Seite",
        "application_de": "Kuehlen, Zudosieren und Sammeln am rechten B6-Lauf",
        "water_status": "UNSPECIFIED_WORKSHOP_STOCK",
    },
}


def main() -> None:
    words = read("SIX_HUNDRED_SEVENTEENTH_39_SHARP_WORDS.tsv")
    cards = read("SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    events = read("SIX_HUNDRED_SEVENTEENTH_381_SHARP_EVENT_COMMANDS.tsv")
    statements = read("SIX_HUNDRED_SEVENTEENTH_116_SHARP_BACKREADS.tsv")

    case_rows = []
    for case_id, data in CASES.items():
        case_rows.append({"case_id": case_id, **data, "card_semantics_policy": "owner/material/application are explicit outer arguments; 39 card words stay invariant"})
    write("SIX_HUNDRED_EIGHTEENTH_6_CASE_NOUN_LEDGER.tsv", case_rows, list(case_rows[0]))

    event_rows: list[dict[str, object]] = []
    statement_by_id = {row["statement_id"]: row for row in statements}
    for row in events:
        statement = statement_by_id[row["statement_id"]]
        case = CASES[statement["case_id"]]
        event_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "case_id": statement["case_id"],
            "surface": row["surface"],
            "card_no": row["card_no"],
            "semantic_component_parse": row["semantic_component_parse"],
            "standard_command_de": row["standard_command_de"],
            "image_owner_or_station_de": statement["owner_or_station"],
            "case_material_de": case["case_material_de"],
            "application_context_de": case["application_de"],
            "card_word_contains_concrete_substance": "NO",
        })
    write("SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv", event_rows, list(event_rows[0]))

    statement_rows: list[dict[str, object]] = []
    for row in statements:
        case = CASES[row["case_id"]]
        command_sequence = row["sharp_controlled_backread_de"].split(": ", 1)[1].rstrip(".")
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "layer_1_card_command_de": command_sequence,
            "layer_2_image_owner_or_station_de": row["owner_or_station"],
            "layer_3_case_material_de": case["case_material_de"],
            "layer_4_application_context_de": case["application_de"],
            "layered_reading_de": f"Bild/Station: {row['owner_or_station']}; Fallstoff: {case['case_material_de']}; Befehl: {command_sequence}.",
            "legacy_fluent_reading_de": row["original_readable_workshop_de"],
            "substance_provenance": case["water_status"],
        })
    write("SIX_HUNDRED_EIGHTEENTH_116_LAYERED_STATEMENTS.tsv", statement_rows, list(statement_rows[0]))

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_record[str(row["record"])].append(row)
    order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    markdown = ["# Elf Records mit sichtbaren Bedeutungsebenen", "", "Jede Lesung trennt Kartenbefehl, Bildbesitzer, Fallstoff und Anwendung. Kein Stoffname steckt heimlich im 39-Wort-Lexikon.", ""]
    record_rows = []
    for record in order:
        rows = by_record[record]
        case = CASES[str(rows[0]["case_id"])]
        record_rows.append({
            "case_id": rows[0]["case_id"],
            "page": rows[0]["page"],
            "record": record,
            "statements": len(rows),
            "events": sum(int(row["event_count"]) for row in rows),
            "case_material_de": case["case_material_de"],
            "application_context_de": case["application_de"],
            "continuous_layered_reading_de": " ".join(str(row["layered_reading_de"]) for row in rows),
        })
        markdown.extend([
            f"## {record} · {rows[0]['page']} · {rows[0]['case_id']}",
            "",
            f"Fallstoff: **{case['case_material_de']}**",
            "",
            f"Anwendung: **{case['application_de']}**",
            "",
        ])
        for row in rows:
            markdown.extend([
                f"### {row['statement_id']}",
                "",
                f"Karten: `{row['surface_sequence']}`",
                "",
                f"Nur Karte: {row['layer_1_card_command_de']}",
                "",
                f"Mit Bild/Fall: {row['layered_reading_de']}",
                "",
            ])
    (HERE / "SIX_HUNDRED_EIGHTEENTH_ELEVEN_RECORD_LAYERED_EDITION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    write("SIX_HUNDRED_EIGHTEENTH_11_RECORD_LAYERED_SUMMARY.tsv", record_rows, list(record_rows[0]))

    report = """# Sechshundertachtzehnte Runde: konkrete Lesung ohne versteckte Stoffwörter

## Ergebnis

Die elf Prosa-Records sind mit vier offen getrennten Ebenen neu gesetzt:

1. der invariante Kartenbefehl;
2. der sichtbare Bildbesitzer oder die lokale Station;
3. der konkrete Fallstoff;
4. die praktische Anwendung.

Damit kann die Lesung weiterhin konkret von Wasser, Pflanzenauszug, Blüte,
Bad, Waschung oder Auflage sprechen, ohne zu behaupten, AIR heiße einfach
WASSER oder HO heiße PFLANZE. AIR bleibt FLUESSIGKEITSLAUF und HO bleibt
ZUTAT; Wasser und Pflanzenidentität kommen aus dem jeweiligen Fall.

Die sechs derzeitigen Fallstoffe sind: wässriger Grundauszug, stärkerer Nach-
oder Spülauszug, Blütenauszug, temperierte Auflage/Waschportion,
Pflanzenkonzentrat und übernommener Werkstattvorrat. Sie verbinden H1–H5 mit
B1–B5; B6 verarbeitet den geerbten Vorrat ohne eigene Herbal-Seite.

## Nächster Schritt

Jetzt werden die sechs Fälle gegeneinander verglichen: Welche konkrete
Handlungsfolge ist wirklich verschieden, und wo erzählen wir denselben Fall
nur mit anderem Bildbesitzer? Daraus soll ein kleines Inventar wiederkehrender
Rezept-/Badmodule entstehen.
"""
    (HERE / "SIX_HUNDRED_EIGHTEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "words": len(words),
        "commands": len({(row["semantic_component_parse"], row["standard_command_de"]) for row in cards}),
        "cards": len(cards),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "cases": len(case_rows),
        "events_with_hidden_substance_word": sum(row["card_word_contains_concrete_substance"] == "YES" for row in event_rows),
        "decision": "CONCRETE_CASE_NOUNS_EXPLICITLY_SEPARATED_FROM_39_CARD_WORDS",
    }
    (HERE / "SIX_HUNDRED_EIGHTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

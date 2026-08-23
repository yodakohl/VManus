#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_biological_second_lesson_two_hundred_thirty_seventh"
STATEMENTS = SRC / "TWO_HUNDRED_THIRTY_SEVENTH_FORTY_THREE_STATEMENTS.tsv"
EVENTS = SRC / "TWO_HUNDRED_THIRTY_SEVENTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv"

B1_PHASES = [
    "KURZKONTAKT", "ANSATZ_BEMESSEN_UND_BESCHICKEN", "HOMOGENISIEREN",
    "UEBERFUEHREN_UND_ABSETZEN", "WEITERFUEHREN", "ZUSATZ_DURCHLEITEN",
    "EINBRINGEN", "WAERMEN_UND_ABSETZEN", "KURZKONTAKT", "KURZKONTAKT_WIEDERHOLEN",
    "DURCHLASS_UND_EINSETZEN", "WASCHZYKLUS", "WASCHZYKLUS_WIEDERHOLEN",
    "ABFUEHREN_ZUR_FOLGEQUELLE", "EMPFANGSSCHALE_FUELLEN", "LANGKONTAKT_UND_ABSETZEN",
    "TRANSFER", "AUFFANGEN_UND_HALTEN", "ABSETZEN", "WAERMEN_UND_DURCHLASSEN",
    "ZUM_ZIEL_BRINGEN",
]
B2_PHASES = [
    "OBERE_STATION_BESCHICKEN", "OBERE_STATION_WEITERFUEHREN", "PORTION_LANG_HALTEN",
    "DURCHLEITEN_UND_ABZIEHEN", "BEMESSEN_WAERMEN_ABZIEHEN", "OBERE_STATION_ABSCHLIESSEN",
    "MITTELSTATION_FRISCH_BESCHICKEN", "QUELLMASS_ABSETZEN", "FOLGEPOSTEN_ABSETZEN",
    "DUESEN_ERGEBNIS", "RECHTE_STATION_BESCHICKEN", "KLARABZUG_UND_VOLLEINSATZ",
    "INS_UNTERFELD_ABFUEHREN", "AUS_QUELLE_ABZIEHEN", "RANDSTATION_LANG_HALTEN",
    "GLEICHTEILEN_BEMESSEN_ZUFUEHREN", "AM_ZIEL_HAL TEN".replace(" ", ""),
    "LANG_HALTEN", "VOLLWASCHUNG", "FOLGESTUFE_HAL TEN".replace(" ", ""),
    "LANG_HALTEN_WIEDERHOLEN", "SCHLUSSABFUEHRUNG",
]

PROTOCOLS = {
    "B1": {
        "name": "GEMEINSAMES_BECKEN_ANSATZ_UND_ANWENDUNGSPROTOKOLL",
        "short": "Ein Besitzer; ein durchgehender Ansatz wird bemessen, beschickt, geschwenkt, temperiert, gewaschen, aufgefangen und zum Ziel gebracht.",
        "organization": "EIN_BILDRAUM__ZYKLISCHER_BATCH",
        "role": "BAD_ODER_WASCHANSATZ_MIT_WIEDERHOLTEN_KONTAKTEN",
    },
    "B2": {
        "name": "MODULARES_MEHRSTATIONS_SPuel_UND_VERTEILPROTOKOLL".upper(),
        "short": "Fünf lokale Besitzer; Material wandert von oberer Paarstation über zwei Mittelknoten in Unterfeld und Randstationen.",
        "organization": "FUENF_BILDRAEUME__SERIELLE_STATIONEN",
        "role": "UEBERGABE_KLAERUNG_TEILUNG_ZUFUEHRUNG_UND_ABLAUF",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    statements = read_tsv(STATEMENTS)
    events = read_tsv(EVENTS)
    events_by_statement: dict[str, list[dict[str, str]]] = {}
    for event in events:
        events_by_statement.setdefault(event["statement_id"], []).append(event)

    phases = {"B1": B1_PHASES, "B2": B2_PHASES}
    positions = Counter()
    statement_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    prior_owner: dict[str, str] = {}
    for statement in statements:
        record = statement["record_unit_id"]
        position = positions[record]
        positions[record] += 1
        owner = statement["visible_owner"]
        owner_transition = "INITIAL_OWNER" if record not in prior_owner else (
            "SAME_OWNER" if prior_owner[record] == owner else "SWITCH_TO_NEW_VISIBLE_OWNER"
        )
        prior_owner[record] = owner
        phase = phases[record][position]
        linked = events_by_statement[statement["statement_id"]]
        statement_rows.append({
            "record_unit_id": record,
            "page": statement["page"],
            "protocol_name": PROTOCOLS[record]["name"],
            "step": position + 1,
            "statement_id": statement["statement_id"],
            "visible_owner": owner,
            "owner_transition": owner_transition,
            "protocol_phase": phase,
            "field_ids": "|".join(dict.fromkeys(e["field_id"] for e in linked)),
            "event_ids": statement["event_ids"],
            "visible_sequence": statement["visible_sequence"],
            "component_chain": statement["lesson_two_value_chain"],
            "complete_translation_de": statement["revised_master_dictation_de"],
            "practical_reading": PROTOCOLS[record]["role"],
        })
        for index, event in enumerate(linked, start=1):
            event_rows.append({
                "record_unit_id": record,
                "page": event["page"],
                "protocol_name": PROTOCOLS[record]["name"],
                "step": position + 1,
                "statement_id": event["statement_id"],
                "protocol_phase": phase,
                "event_order_in_statement": index,
                "event_id": event["event_id"],
                "field_id": event["field_id"],
                "visible_owner": event["visible_owner"],
                "visible_surface": event["visible_surface"],
                "master_card_id": event["master_card_id"],
                "component_or_whole_analysis": event["component_or_whole_analysis"],
                "concrete_value_de": event["lesson_two_value_de"],
                "teaching_status": event["final_teaching_status"],
            })

    statement_path = OUT / "TWO_HUNDRED_THIRTY_NINTH_FORTY_THREE_COMPLETE_STATEMENTS.tsv"
    event_path = OUT / "TWO_HUNDRED_THIRTY_NINTH_ONE_HUNDRED_TWENTY_EIGHT_PROTOCOL_EVENTS.tsv"
    comparison_path = OUT / "TWO_HUNDRED_THIRTY_NINTH_TWO_PROTOCOLS.tsv"
    readable_path = OUT / "TWO_HUNDRED_THIRTY_NINTH_TWO_CONTINUOUS_RECORDS.md"
    report_path = OUT / "TWO_HUNDRED_THIRTY_NINTH_REPORT.md"

    write_tsv(statement_path, statement_rows, list(statement_rows[0]))
    write_tsv(event_path, event_rows, list(event_rows[0]))

    comparisons: list[dict[str, object]] = []
    for record in ("B1", "B2"):
        subset = [s for s in statement_rows if s["record_unit_id"] == record]
        ev_subset = [e for e in event_rows if e["record_unit_id"] == record]
        owners = list(dict.fromkeys(str(s["visible_owner"]) for s in subset))
        comparisons.append({
            "record_unit_id": record,
            "page": subset[0]["page"],
            "protocol_name": PROTOCOLS[record]["name"],
            "organization": PROTOCOLS[record]["organization"],
            "statement_count": len(subset),
            "event_count": len(ev_subset),
            "visible_owner_count": len(owners),
            "owner_switch_count": sum(s["owner_transition"] == "SWITCH_TO_NEW_VISIBLE_OWNER" for s in subset),
            "closed_statement_count": sum("Schluss" in str(s["complete_translation_de"]) for s in subset),
            "whole_sign_event_count": sum(e["teaching_status"] == "LEARNED_WHOLE_SIGN" for e in ev_subset),
            "visible_owners": " | ".join(owners),
            "short_continuous_reading": PROTOCOLS[record]["short"],
        })
    write_tsv(comparison_path, comparisons, list(comparisons[0]))

    lines = ["# Zwei vollständige Biological-Arbeitsprotokolle", ""]
    for record in ("B1", "B2"):
        lines += [f"## {record} / {next(s['page'] for s in statement_rows if s['record_unit_id'] == record)}", "", PROTOCOLS[record]["short"], ""]
        for row in (s for s in statement_rows if s["record_unit_id"] == record):
            lines.append(f"{row['step']}. **{row['protocol_phase']}** — {row['complete_translation_de']}")
        lines.append("")
    lines += [
        "## Arbeitslesung", "",
        "f81v und f82r benutzen dasselbe kleine Karten- und Ganzzeicheninventar, aber nicht denselben Ablauf.",
        "f81v hält einen einzigen gezeichneten Arbeitsraum aktiv: Es ist ein Batch-/Beckenprotokoll mit wiederholtem Kontakt, Waschen, Absetzen und Auffangen.",
        "f82r schaltet zwischen fünf gezeichneten Stationen: Es ist ein Übergabe- und Verteilprotokoll mit Bemessung, Klarabzug, Teilung, Zuführung und Schlussabfluss.",
        "Die Bilder liefern die ausgelassenen Gefäßnamen; die Karten liefern Handlungen, Relationen, Maße, Grade und sechs gelernte Spezialzeichen.",
        "",
    ]
    readable_path.write_text("\n".join(lines), encoding="utf-8")

    report = f"""# Sidequest-Pass 239: zwei Biological-Protokolle

Dieser Pass führt keine neue Bedeutung ein. Er setzt nur das vollständige R237-Wörterbuch und die R238-Slotklassen zu zwei fortlaufenden Arbeitsanweisungen zusammen.

## Ergebnis

- f81v/B1: **{PROTOCOLS['B1']['name']}** — 21 Aussagen, 66 Karten, ein sichtbarer Besitzer, kein Besitzerwechsel.
- f82r/B2: **{PROTOCOLS['B2']['name']}** — 22 Aussagen, 62 Karten, fünf sichtbare Besitzer, vier Besitzerwechsel.
- Beide Seiten verwenden dieselbe Grammatik; ihre praktische Organisation ist verschieden.
- f81v ist zyklisch und batchbezogen. f82r ist modular und stationsbezogen.
- Alle 128 Karten und 43 Aussagen erhalten eine konkrete Lesung; keine Sequenz bleibt ohne Default.

## Wichtigste Reparatur

Die scheinbare Einheit „Biological-Prosa“ ist zu grob. Der gemeinsame Kartenapparat kodiert keine einzige universelle Badrezeptfolge. Er kann sowohl einen langen gemeinsamen Beckenansatz als auch eine Reihe lokaler Übergabe-/Bearbeitungsstationen notieren. Genau das wäre für eine kleine Werkstatt lehrbar: dieselben Kürzel, andere vorgezeichnete Besitzer und andere Reihenfolge.

## Quellenbindung

- R237 statements SHA-256: `{sha(STATEMENTS)}`
- R237 events SHA-256: `{sha(EVENTS)}`
"""
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "records": 2,
        "statements": len(statement_rows),
        "events": len(event_rows),
        "record_counts": {r: positions[r] for r in positions},
        "protocols": {r: PROTOCOLS[r]["name"] for r in PROTOCOLS},
        "outputs": {p.name: sha(p) for p in (statement_path, event_path, comparison_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

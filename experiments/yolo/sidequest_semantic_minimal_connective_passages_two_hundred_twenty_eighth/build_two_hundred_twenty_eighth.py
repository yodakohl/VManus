#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_combined_reference_parser_two_hundred_twenty_seventh/TWO_HUNDRED_TWENTY_SEVENTH_357_READING_UNITS.tsv"

PASSAGES = {
    "P_H2": {
        "title": "f10r H2 — Ansatz- und Mengenfolge",
        "translation": "Auszugsansatz bereit. Ansatz nach Sollvorgabe; Folgeposten bereit. Dieser und dieser Posten: den zweiten auf Sollwert setzen und als denselben aktiv halten. Folgeansatz; im selben Ansatz weiter, Sollwert davon. Im Zubereitungsgefäß erster und zweiter Ansatz; denselben Posten durch die Bearbeitungsstufe führen und halten; Zugabemaß.",
        "connectives": [("und", 2, "Paar und Handlungsfolge"), ("nach", 1, "Sollvorbereitung anbinden"), ("auf", 1, "Wertzuweisung"), ("als", 1, "Referentenrückkehr"), ("im", 2, "lokaler Besitzer"), ("durch", 1, "Bearbeitungsstufe")],
    },
    "P_B3": {
        "title": "f83r B3-S001–S016 — obere und mittlere Stationsfolge",
        "translation": "Oben lange sammeln; Schluss. Danach dorthin und lange wärmen; Schluss. Bestand auf Sollwert setzen, als denselben weiterführen, abführen; Schluss. Davon bemessen und zur Folgestelle; in die runde Station überführen; Schluss. Posten übertragen, am Ziel einsetzen und weiterführen; Schluss. Bemessen, überführen, lange einwirken; Schluss. Abführen; Schluss. Einsetzen. Zum Ziel zuführen, kurz fortsetzen; Schluss. Vorbereitung übertragen, einsetzen, überführen, am Quellposten halten. Ansatz kurz absetzen; Schluss. Portion bemessen, kurz vorbereiten, kurz einwirken; Schluss. In den Lauf einsetzen, lange absetzen; Schluss. Abführen; Schluss. Abzug einführen; Schluss.",
        "connectives": [("und", 3, "Handlungsfolgen"), ("auf", 1, "Wertzuweisung"), ("als", 1, "Referentenrückkehr"), ("zur", 1, "Folgeziel"), ("in", 2, "lokale Station oder Lauf"), ("am", 2, "Ziel- und Quellposten"), ("zum", 1, "Zielrichtung")],
    },
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    units = read(SOURCE)
    selected: list[dict[str, object]] = []
    for row in units:
        passage = None
        if row["record_unit_id"] == "H2":
            passage = "P_H2"
        elif row["record_unit_id"] == "B3":
            statement_numbers = [int(value.rsplit("S", 1)[1]) for value in row["statement_ids"].split("|")]
            if max(statement_numbers) <= 16:
                passage = "P_B3"
        if passage:
            selected.append({
                "passage_id": passage,
                "passage_unit_order": sum(item["passage_id"] == passage for item in selected) + 1,
                **row,
            })
    write(OUT / "TWO_HUNDRED_TWENTY_EIGHTH_FIFTY_READING_UNITS.tsv", selected)

    passage_rows: list[dict[str, object]] = []
    connective_rows: list[dict[str, object]] = []
    for passage_id, spec in PASSAGES.items():
        rows = [row for row in selected if row["passage_id"] == passage_id]
        passage_rows.append({
            "passage_id": passage_id,
            "title": spec["title"],
            "record_unit_id": rows[0]["record_unit_id"],
            "first_statement": rows[0]["statement_ids"].split("|")[0],
            "last_statement": rows[-1]["statement_ids"].split("|")[-1],
            "visible_cards": sum(int(row["visible_card_count"]) for row in rows),
            "source_tokens": sum(int(row["source_token_count"]) for row in rows),
            "reading_units": len(rows),
            "composite_units": sum(row["unit_kind"] != "ATOMIC_CARD" for row in rows),
            "literal_unit_chain": " || ".join(str(row["construction_reading_de"]) for row in rows),
            "minimal_connective_translation_de": spec["translation"],
            "added_connective_occurrences": sum(item[1] for item in spec["connectives"]),
        })
        for connective, count, reason in spec["connectives"]:
            connective_rows.append({
                "passage_id": passage_id,
                "connective_de": connective,
                "occurrences": count,
                "purpose": reason,
                "changes_card_meaning": "NO",
            })
    write(OUT / "TWO_HUNDRED_TWENTY_EIGHTH_TWO_CONTINUOUS_PASSAGES.tsv", passage_rows)
    write(OUT / "TWO_HUNDRED_TWENTY_EIGHTH_ADDED_CONNECTIVES.tsv", connective_rows)

    lines = [
        "# Zwei Passagen mit minimalen Bindewörtern",
        "",
        "Die eckige Werkstattlogik bleibt nominal und knapp. Hinzugefügt werden nur deutsche Verhältniswörter; kein zusätzliches Stoff-, Körper- oder Krankheitsnomen.",
        "",
    ]
    for row in passage_rows:
        lines.extend([
            f"## {row['title']}",
            "",
            f"**Karten:** {row['visible_cards']} sichtbar → {row['source_tokens']} Quelltoken → {row['reading_units']} Leseeinheiten.",
            "",
            f"**Wörtliche Einheiten:** {row['literal_unit_chain']}",
            "",
            f"**Lesung:** {row['minimal_connective_translation_de']}",
            "",
        ])
    lines.extend([
        "## Was der Fluss jetzt sagt",
        "",
        "f10r H2 klingt wie ein komprimierter Ansatz- und Mengenabschnitt: vorbereitete Ansätze, zwei parallel gesetzte Posten, Sollwert, Bearbeitungsstufe, Zugabemaß. f83r B3 klingt wie ein lokales Stationsprogramm: sammeln, wärmen, Sollwert halten, abführen, übertragen, einwirken und absetzen. Diese Lesung behauptet keinen geschlossenen oder gerichteten Gesamtwasserkreislauf.",
    ])
    (OUT / "TWO_HUNDRED_TWENTY_EIGHTH_TWO_READABLE_PASSAGES.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "passages": len(passage_rows),
        "selected_reading_units": len(selected),
        "visible_cards": sum(int(row["visible_cards"]) for row in passage_rows),
        "source_tokens": sum(int(row["source_tokens"]) for row in passage_rows),
        "composite_units": sum(int(row["composite_units"]) for row in passage_rows),
        "connective_types": len(connective_rows),
        "connective_occurrences": sum(int(row["occurrences"]) for row in connective_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

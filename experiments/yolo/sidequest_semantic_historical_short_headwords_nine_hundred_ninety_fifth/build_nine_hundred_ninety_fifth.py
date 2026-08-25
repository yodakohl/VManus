#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P993 = HERE.parent / "sidequest_semantic_canonical_scribe_workshop_fifth_edition_nine_hundred_ninety_third"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (P993 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOT_REVISIONS = {
    "R-AIIN": {
        "old": "SOLLWERT",
        "new": "MASS",
        "material": "nach vorgeschriebenem Maß",
        "station": "nach vorgeschriebenem Maß",
        "celestial": "eingetragenes Maß oder Tabellenwert",
    },
    "R-AIN": {
        "old": "EINHEIT",
        "new": "PORTION",
        "material": "eine Portion",
        "station": "eine Füllung oder Portion",
        "celestial": "eine Tabellen- oder Ringzelle",
    },
    "R-OR": {
        "old": "ARBEITSSATZ",
        "new": "ANSATZ",
        "material": "der laufende Ansatz",
        "station": "laufende Anordnung oder Stationsfassung",
        "celestial": "Eintragsgruppe",
    },
    "R-T": {
        "old": "EINSTELLEN",
        "new": "STELLEN",
        "material": "Menge, Dauer oder Stufe stellen",
        "station": "Stufe oder Stellung setzen",
        "celestial": "Stellung oder Grad setzen",
    },
    "R-R": {
        "old": "MARKIEREN",
        "new": "MERKEN",
        "material": "Teilgang oder Zustand merken",
        "station": "Stationszustand merken",
        "celestial": "Platz oder Zustand merken",
    },
    "R-CARRIER_Q": {
        "old": "START",
        "new": "BEGINN",
        "material": "einen neuen Ansatz beginnen",
        "station": "eine neue Stationszelle beginnen",
        "celestial": "eine neue Reihe beginnen",
    },
}

TEXT_REPLACEMENTS = [
    ("SOLLMASS", "MASS"),
    ("SOLLWERT", "MASS"),
    ("TEILMENGE", "PORTION"),
    ("ARBEITSSATZ", "ANSATZ"),
    ("EINTRAGSSATZ", "EINTRAGSGRUPPE"),
    ("EINSTELLEN", "STELLEN"),
    ("MARKIEREN", "MERKEN"),
    ("START", "BEGINN"),
]


def revise_text(value: str) -> str:
    revised = value
    for old, new in TEXT_REPLACEMENTS:
        revised = revised.replace(old, new)
    return revised


def main() -> None:
    codebook = read_tsv("PASS993_159_COMPLETE_CODEBOOK.tsv")
    roots = read_tsv("PASS993_53_PORTABLE_ROOTS.tsv")
    events = read_tsv("PASS993_2511_EVENT_INTERLINEAR.tsv")
    clauses = read_tsv("PASS993_354_NATURAL_CLAUSE_EDITION.tsv")
    bio_phrases = read_tsv("PASS993_1280_BIOLOGICAL_EVENT_PHRASES.tsv")

    revision_rows: list[dict[str, str]] = []
    for row in roots:
        revision = ROOT_REVISIONS.get(row["root_id"])
        if not revision:
            continue
        old = row["atomic_meaning_de"]
        row["atomic_meaning_de"] = revision["new"]
        row["material_workshop_expansion_de"] = revision["material"]
        row["station_workshop_expansion_de"] = revision["station"]
        row["celestial_relational_expansion_de"] = revision["celestial"]
        revision_rows.append(
            {
                "root_id": row["root_id"],
                "recognition_form": row["recognition_form"],
                "old_atomic_value_de": old,
                "new_atomic_value_de": revision["new"],
                "reason_de": "kurzes werkstattgeeignetes Hauptwort statt moderner oder aufgeblähter Fachsprache",
            }
        )

    for row in codebook:
        revision = ROOT_REVISIONS.get(row["teaching_unit_id"])
        if revision:
            row["spoken_value_de"] = revision["new"]
        for field in ("concrete_context_values_de", "teaching_rule_de"):
            row[field] = revise_text(row[field])

    for row in events:
        row["complete_working_reading_de"] = revise_text(row["complete_working_reading_de"])

    for row in clauses:
        row["complete_working_translation_de"] = revise_text(row["complete_working_translation_de"])

    phrase_repairs = {
        "ANSATZ verwenden": "den laufenden Ansatz verwenden",
        "MERKEN verwenden": "den Zustand merken",
        "MASS verwenden": "nach Maß arbeiten",
        "PORTION verwenden": "eine Portion verwenden",
        "STELLEN verwenden": "die Stufe stellen",
        "BEGINN verwenden": "einen neuen Gang beginnen",
    }
    for row in bio_phrases:
        row["reconciled_card_reading_de"] = revise_text(row["reconciled_card_reading_de"])
        phrase = revise_text(row["natural_event_phrase_de"])
        for old, new in phrase_repairs.items():
            phrase = phrase.replace(old, new)
        row["natural_event_phrase_de"] = phrase

    write_tsv("PASS995_159_SHORT_HEADWORD_CODEBOOK.tsv", codebook)
    write_tsv("PASS995_53_SHORT_PORTABLE_ROOTS.tsv", roots)
    write_tsv("PASS995_2511_REVISED_EVENT_INTERLINEAR.tsv", events)
    write_tsv("PASS995_354_REVISED_NATURAL_CLAUSES.tsv", clauses)
    write_tsv("PASS995_1280_REVISED_BIOLOGICAL_EVENT_PHRASES.tsv", bio_phrases)
    write_tsv("PASS995_SIX_HEADWORD_REVISIONS.tsv", revision_rows)

    summary = {
        "status": "PASS",
        "revised_headwords": len(revision_rows),
        "codebook_units": len(codebook),
        "roots": len(roots),
        "events": len(events),
        "clauses": len(clauses),
        "biological_event_phrases": len(bio_phrases),
        "new_atomic_values": [row["new_atomic_value_de"] for row in revision_rows],
    }
    (HERE / "PASS995_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = """# Pass 995 — kurze Werkstattwörter

## Ergebnis

Sechs moderne oder unnötig aufgeblähte deutsche Arbeitsglossen wurden
gekürzt:

- `AIIN`: **SOLLWERT → MASS**;
- `AIN`: **EINHEIT → PORTION**;
- `OR`: **ARBEITSSATZ → ANSATZ**;
- `T`: **EINSTELLEN → STELLEN**;
- `R`: **MARKIEREN → MERKEN**;
- `CARRIER_Q`: **START → BEGINN**.

Das ist kein neuer Bedeutungsfund, sondern die sprachlich bessere Fassung
derselben sechs Werkstattfunktionen. Die neuen Hauptwörter sind kurz,
sprechbar und in Rezept-, Listen- oder Werkstattprosa leichter vorstellbar.
Registerabhängige Erweiterungen bleiben erlaubt: MASS kann im Himmelsregister
ein Tabellenwert sein, PORTION eine Zelle und ANSATZ eine Eintragsgruppe.

## Gewinn für die Lesung

Statt `ARBEITSSATZ verwenden` liest der Lehrling nun `den laufenden Ansatz
verwenden`; statt `MARKIEREN verwenden` `den Zustand merken`. Die natürlichen
Sätze bleiben erhalten, aber das Taschenwörterbuch klingt weniger wie ein
modernes Maschinenhandbuch.

## Aktuelle Kernformel

> POSTEN → NEHMEN/GEBEN → MASS oder PORTION → QUELLE/ZIEL →
> STELLEN/HALTEN/LEITEN → MERKEN → SCHLUSS.

Die volle Ausgabe bleibt bei 159 Einheiten, 53 Wurzeln, 2.511 Ereignissen und
354 Aussagen. Es wurde keine neue Wurzel und kein neuer Manuskriptinhalt
erfunden.
"""
    (HERE / "PASS995_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

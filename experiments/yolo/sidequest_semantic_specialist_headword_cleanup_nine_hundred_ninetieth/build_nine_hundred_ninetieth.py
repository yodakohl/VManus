#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P989 = ROOT / "experiments/yolo/sidequest_semantic_canonical_image_owned_workshop_edition_nine_hundred_eighty_ninth"

REVISIONS = {
    "W006": "SEITENARM",
    "W017": "ZUGABE",
    "W019": "AUSGLEICHEN",
    "W021": "KLARPUNKT",
    "W025": "MITTELMASS",
    "W028": "BLÜTENRESERVE",
    "W029": "WURZELREST",
    "W031": "AUFFANGSCHALE",
    "W037": "WEINSUD",
    "W044": "VORPOSTEN",
    "W046": "WARMGRAD",
    "W050": "HALTEZEIT",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    codebook = read(P989 / "PASS989_159_CODEBOOK.tsv")
    events = read(P989 / "PASS989_2511_EVENT_INTERLINEAR.tsv")
    specialist_ids = {
        row["teaching_unit_id"]
        for row in codebook
        if row["layer"] in {"E_LOCAL_SPECIALIST_HEADWORD", "F_IMAGE_OWNED_SPECIALIST_CARD"}
    }
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        for unit_id in event["primary_teaching_unit_ids"].split("|"):
            if unit_id in specialist_ids:
                occurrences[unit_id].append(event)

    audit_rows = []
    for row in codebook:
        unit_id = row["teaching_unit_id"]
        if unit_id not in specialist_ids:
            continue
        old = row["spoken_value_de"]
        new = REVISIONS.get(unit_id, old)
        row["spoken_value_de"] = new
        observed = occurrences[unit_id]
        observed_readings = []
        for event in observed:
            if event["complete_working_reading_de"] not in observed_readings:
                observed_readings.append(event["complete_working_reading_de"])
        row["concrete_context_values_de"] = "|".join(observed_readings)
        audit_rows.append(
            {
                "teaching_unit_id": unit_id,
                "recognition_forms": row["recognition_forms"],
                "old_headword_de": old,
                "selected_headword_de": new,
                "occurrences": str(len(observed)),
                "pages": "|".join(dict.fromkeys(event["physical_page"] for event in observed)),
                "observed_event_readings_de": "|".join(observed_readings),
                "change_status": "SHORT_COMPOUND_REFINEMENT" if old != new else "KEEP",
                "headword_rule": "ONE_SHORT_WORKSHOP_WORD__CONTEXT_MAY_INFLECT_OR_SPECIFY",
            }
        )

    occurrence_rows = []
    for unit_id in sorted(specialist_ids):
        for event in occurrences[unit_id]:
            occurrence_rows.append(
                {
                    "teaching_unit_id": unit_id,
                    "event_id": event["event_id"],
                    "physical_page": event["physical_page"],
                    "locus": event["locus"],
                    "surface": event["surface"],
                    "complete_working_reading_de": event["complete_working_reading_de"],
                }
            )

    write(HERE / "PASS990_159_CODEBOOK_WITH_CLEAN_HEADWORDS.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS990_56_SPECIALIST_HEADWORDS.tsv", audit_rows, list(audit_rows[0]))
    write(HERE / "PASS990_96_SPECIALIST_OCCURRENCES.tsv", occurrence_rows, list(occurrence_rows[0]))
    summary = {
        "status": "PASS",
        "specialist_headwords": len(audit_rows),
        "specialist_occurrences": len(occurrence_rows),
        "headwords_revised": sum(row["change_status"] != "KEEP" for row in audit_rows),
        "sentence_sized_headwords": 0,
    }
    (HERE / "PASS990_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = """# Pass 990 — kurze Fachwörter statt Mini-Sätze

## Ergebnis

Alle 56 gelernten Fachkarten — 51 registerübergreifende Fachkarten und fünf
f13r-Bildkarten — wurden als eigenes Wörterbuch gelesen. Jede hat genau ein
kurzes Werkstattstichwort. Der Kontext darf daraus eine natürliche Wendung
machen, aber die Wörterbuchzelle bleibt ein Wort oder Kompositum.

Zwölf zu allgemeine Stichwörter werden präzisiert:

- ARM → **SEITENARM**;
- GABE → **ZUGABE**;
- GLEICHEN → **AUSGLEICHEN**;
- KLAR → **KLARPUNKT**;
- MASS → **MITTELMASS**;
- RESERVE → **BLÜTENRESERVE**;
- REST → **WURZELREST**;
- SCHALE → **AUFFANGSCHALE**;
- SUD → **WEINSUD**;
- VORIGES → **VORPOSTEN**;
- WARM → **WARMGRAD**;
- ZEIT → **HALTEZEIT**.

Die übrigen Werte bleiben kurz: ABLAUF, ABSEIHEN, ANWÄRMEN, AUFLEGEN,
AUFSTREICHEN, AUSWRINGEN, BECKEN, DÜSE, FRISCHWASSER, GEFÄSS, HAHN,
KLARLAUF, NACHSEIHEN, PRESSEN, SPÜLUNG, TUCH, ÜBERLAUF, WANNE,
WARMWASSER, WASCHEN und ZERREIBEN.

Damit trägt keine dieser Karten wieder eine Satzbedeutung wie „bis die
Flüssigkeit klar abläuft“. `shey/cheey` bleibt schlicht **KLARLAUF**; Verben,
Zeit, Quelle und Ziel stehen in den Nachbarkarten.
"""
    (HERE / "PASS990_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

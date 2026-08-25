#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P984 = ROOT / "experiments/yolo/sidequest_semantic_53_root_plain_dictionary_nine_hundred_eighty_fourth"
P985 = ROOT / "experiments/yolo/sidequest_semantic_canonical_image_owned_workshop_edition_nine_hundred_eighty_fifth"
P986 = ROOT / "experiments/yolo/sidequest_semantic_root_codebook_reconciliation_nine_hundred_eighty_sixth"
P987 = ROOT / "experiments/yolo/sidequest_semantic_biological_natural_station_edition_nine_hundred_eighty_seventh"
P988 = ROOT / "experiments/yolo/sidequest_semantic_f88r_six_six_four_label_alignment_nine_hundred_eighty_eighth"

SHORT_LABELS = {
    "D001": "WURZELBÜNDEL",
    "D002": "SPINDELWURZEL",
    "D003": "FASERWURZELBÜNDEL",
    "D004": "KNOLLENWURZEL",
    "D005": "SCHLINGWURZEL",
    "D006": "LANZETTBLATT",
    "D007": "GABELWURZELSTOCK",
    "D008": "HÄNGEWURZEL",
    "D009": "ZAHNKÖRPER",
    "D010": "FASERWURZELSTOCK",
    "D011": "FLECKKNOLLE",
    "D012": "BLATTZWEIG",
    "D013": "WURZELKRONE",
    "D014": "KRIECHSTOCK",
    "D015": "SCHNITTKÖRPER",
    "D016": "SPEICHERTEIL",
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
    roots = read(P984 / "PASS984_53_PORTABLE_ROOT_DICTIONARY.tsv")
    codebook = read(P986 / "PASS986_159_RECONCILED_CODEBOOK.tsv")
    events = read(P986 / "PASS986_2511_RECONCILED_EVENT_INTERLINEAR.tsv")
    clauses = read(P986 / "PASS986_354_RECONCILED_CLAUSES.tsv")
    addresses = read(P985 / "PASS985_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read(P985 / "PASS985_14_PAGE_READABLE_EDITION.tsv")
    bio_clauses = read(P987 / "PASS987_318_BIOLOGICAL_NATURAL_CLAUSES.tsv")
    bio_pages = read(P987 / "PASS987_FOUR_BIOLOGICAL_PAGE_READINGS.tsv")
    labels = read(P988 / "PASS988_16_F88R_VISUAL_INGREDIENT_LABELS.tsv")
    batches = read(P988 / "PASS988_THREE_SILENT_VESSEL_BATCHES.tsv")

    label_by_unit = {row["teaching_unit_id"]: row for row in labels}
    label_by_event = {row["event_id"]: row for row in labels}
    bio_clause_by_id = {row["clause_id"]: row for row in bio_clauses}
    bio_page_by_id = {row["physical_page"]: row for row in bio_pages}

    for row in codebook:
        unit_id = row["teaching_unit_id"]
        if unit_id in label_by_unit:
            label = label_by_unit[unit_id]
            row["spoken_value_de"] = SHORT_LABELS[unit_id]
            row["concrete_context_values_de"] = label["cautious_visible_material_class_de"]
            row["teaching_rule_de"] = (
                "Als lokalen Namen des direkt benachbarten sichtbaren Zutatenkörpers lernen; "
                "das Gefäß besitzt die Charge stumm, die Karte nicht in Operationswurzeln zerlegen."
            )

    for row in events:
        if row["event_id"] in label_by_event:
            unit_id = row["primary_teaching_unit_ids"]
            row["complete_working_reading_de"] = SHORT_LABELS[unit_id]

    for row in clauses:
        if row["clause_id"] in bio_clause_by_id:
            natural = bio_clause_by_id[row["clause_id"]]
            row["complete_working_translation_de"] = natural["natural_workshop_reading_de"]
            row["reading_source"] = natural["rewrite_mode"]

    for row in addresses:
        row["portable_card_reading_de"] = row["portable_card_reading_de"].replace("DIES", "POSTEN").replace("SCHLIESSEN", "SCHLUSS")
        if row["event_id"] in label_by_event:
            label = label_by_event[row["event_id"]]
            row["owner_id"] = label["batch_id"]
            row["visible_owner_de"] = "stummes Gefäß mit Zutatenreihe " + label["batch_id"]
            row["local_address_reading_de"] = SHORT_LABELS[label["teaching_unit_id"]] + ": " + label["cautious_visible_material_class_de"]
            row["diagram_model"] = "THREE_SILENT_VESSEL_BATCHES_6_6_4"

    for row in pages:
        page = row["physical_page"]
        if page in bio_page_by_id:
            row["complete_working_translation_de"] = bio_page_by_id[page]["complete_natural_page_reading_de"]
        elif page == "f88r":
            row["complete_working_translation_de"] = (
                "Drei stumme Gefäße besitzen drei Zutatenreihen mit sechs, sechs und vier gelernten Etiketten. "
                "Die bezeichneten Wurzel-, Knollen-, Blatt- und Speicherposten werden portionsweise in den jeweils benachbarten "
                "Gefäßansatz gegeben; die folgende Prosa setzt, hält, leitet und schließt jede Charge."
            )

    write(HERE / "PASS989_159_CODEBOOK.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS989_2511_EVENT_INTERLINEAR.tsv", events, list(events[0]))
    write(HERE / "PASS989_53_ROOT_DICTIONARY.tsv", roots, list(roots[0]))
    write(HERE / "PASS989_354_COMPLETE_CLAUSE_EDITION.tsv", clauses, list(clauses[0]))
    write(HERE / "PASS989_501_LOCAL_ADDRESS_LEDGER.tsv", addresses, list(addresses[0]))
    write(HERE / "PASS989_14_PAGE_READABLE_EDITION.tsv", pages, list(pages[0]))
    write(HERE / "PASS989_16_F88R_INGREDIENT_LABELS.tsv", labels, list(labels[0]))
    write(HERE / "PASS989_THREE_F88R_BATCHES.tsv", batches, list(batches[0]))

    theory = """# Pass 989 — aktuelle kanonische Sidequest-Arbeitsausgabe

## Arbeitsmodell

Die vierzehn Seiten werden als bildadressiertes Werkstattbuch gelesen:

> Pflanzenstoff wählen → im Gefäß zubereiten → in Bad, Auflage oder lokaler
> Station anwenden → Himmelsplatz oder Arbeitsklasse nachschlagen.

## Schreibsystem

Ein Lehrling lernt 159 Einheiten: 53 portable Bedeutungswurzeln, drei lokale
Diagrammzeichen, dreißig häufige Formelkarten, 51 Fachkarten, fünf lokale
f13r-Bildteilkarten, sechzehn f88r-Zutatennamen und eine Regel zum Kopieren
ganzer Bild- oder Ringadressen. Die längste gelernte Karte gewinnt; sonst werden
die kurzen Wurzeln von links nach rechts gelesen.

Das Wörterbuch ist jetzt intern einheitlich: `Y=POSTEN`, `DY=SCHLUSS`,
`OR=ARBEITSSATZ`, `CARRIER_Q=START`. Formelkarten verwenden genau dieselben
atomaren Werte.

## Biological

Alle 1.280 Biological-Ereignisse sind in 318 flüssige Werkstattaussagen
eingebunden. Die Seiten zeigen lokale Becken-, Leitungs-, Bade-, Halte- und
Anwendungsstationen. Sichtbare Verbindungen gelten innerhalb der jeweiligen
Vignette; es wird kein einziger geschlossener Seitenkreislauf erfunden.

## f88r

Die erneute Originalbildlesung ergibt sechzehn Zutatenetiketten in Reihen
6+6+4. Die drei großen Gefäße sind stumme Chargenbesitzer, keine drei sicher
beschrifteten Textüberschriften. Die Etiketten erhalten kurze Sichtklassen wie
WURZELBÜNDEL, SPINDELWURZEL, KNOLLENWURZEL, LANZETTBLATT, BLATTZWEIG,
WURZELKRONE und SPEICHERTEIL; ein botanischer Artname wird nicht erzwungen.

## Stärkster fortlaufender Auszug

`tshol schoal cfhy shfydaiin cphy shey tchody`

> Vom Blütenkraut einen Sudansatz bilden, auswringen, die vorgeschriebene
> Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; Schluss.

`shey` bedeutet dabei nur KLARLAUF, nicht den ganzen Satz.

## Umfang

- 2.511 sichtbare Gruppen auf 14 Seiten;
- 2.010 laufende Textgruppen in 354 Aussagen;
- 501 lokale Bild-, Stations- und Ringadressen;
- 159 gelernte Einheiten und 53 portable Wurzeln;
- jede Gruppe, Aussage und Seite mit einer konkreten Arbeitslesung.

Dies ist die beste kreative Werkstatttheorie des festen Vierzehnseitenkorpus,
keine behauptete historische Entzifferung.
"""
    (HERE / "PASS989_CURRENT_WORKING_THEORY.md").write_text(theory, encoding="utf-8")

    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "roots": len(roots),
        "events": len(events),
        "clauses": len(clauses),
        "addresses": len(addresses),
        "pages": len(pages),
        "biological_clauses_naturalized": len(bio_clauses),
        "biological_events_bound": sum(int(row["event_count"]) for row in bio_clauses),
        "f88_labels": len(labels),
        "f88_batch_shape": [int(row["label_count"]) for row in batches],
    }
    (HERE / "PASS989_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

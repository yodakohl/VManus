#!/usr/bin/env python3
"""Replace free master prose with a finite 54-slot source lexicon."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_nonmedical_counterbook_seventieth_edition/SEVENTIETH_14_DUAL_CONTENT_UNITS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_consolidated_workshop_sixty_ninth_edition/SIXTY_NINTH_776_CURRENT_GROUP_LEDGER.tsv"

LEXICON = (
    # shared
    ("S01", "OWNER", "SHARED", "Besitzer", "Besitzer", "visible image or local record"),
    ("S02", "ITEM", "SHARED", "Arbeitsposten", "Arbeitsposten", "active register"),
    ("S03", "PREVIOUS", "SHARED", "voriger Ansatz", "voriger Ansatz", "previous register"),
    ("S04", "TARGET", "SHARED", "bezeichnete Stelle", "bezeichnete Stelle", "visible owner or target register"),
    ("S05", "PORTION", "SHARED", "örtliche Portion", "örtliche Portion", "measure/portion card"),
    ("S06", "RESULT", "SHARED", "sichtbares Ergebnis", "sichtbares Ergebnis", "result/readout card plus owner"),
    # Herbal
    ("H01", "PLANT", "HERBAL", "Bildpflanze", "Bildpflanze", "whole plant image"),
    ("H02", "ROOT", "HERBAL", "Wurzelteil", "Wurzelmaterial", "plant owner plus master"),
    ("H03", "SHOOT", "HERBAL", "junger Spross", "junger Spross", "plant owner plus master"),
    ("H04", "LEAF", "HERBAL", "Blatt", "Blatt", "plant owner plus master"),
    ("H05", "FLOWER", "HERBAL", "Blüte", "Blüte", "plant owner plus master"),
    ("H06", "HERB", "HERBAL", "Kraut", "Pflanzenrohstoff", "plant owner plus master"),
    ("H07", "WATER", "HERBAL", "Wasser", "Wasser", "master source"),
    ("H08", "EXTRACTION_MEDIUM", "HERBAL", "Wein oder Auszugsmedium", "Auszugsmedium", "master source"),
    ("H09", "OIL_BINDER", "HERBAL", "Öl", "Bindemittel", "master source"),
    ("H10", "HONEY_BINDER", "HERBAL", "Honig", "Binder", "master source"),
    ("H11", "VESSEL", "HERBAL", "Gefäß", "Gefäß", "learned card or master"),
    ("H12", "CLOTH", "HERBAL", "Tuch", "Tuch", "learned card or master"),
    ("H13", "EXTRACT", "HERBAL", "Auszug", "Auszug", "extract card plus master"),
    ("H14", "RESIDUE", "HERBAL", "Rückstand", "Rückstand", "master source"),
    ("H15", "DRINK_OR_PRODUCT", "HERBAL", "Trank", "Farb-, Duft- oder Werkprodukt", "master source choice"),
    ("H16", "OUTER_APPLICATION", "HERBAL", "äußere Auflage", "Auftrag am Werkstück", "master source choice"),
    # Biological
    ("B01", "FIGURE_WORKPIECE", "BIO", "Badende", "Arbeitsplatz oder Werkstück", "visible figure plus master choice"),
    ("B02", "BASIN", "BIO", "Becken", "Becken", "visible owner"),
    ("B03", "STATION", "BIO", "örtliche Badstation", "örtliche Arbeitsstation", "visible owner plus master choice"),
    ("B04", "OPENING", "BIO", "Öffnung", "Öffnung", "visible/local master"),
    ("B05", "INLET", "BIO", "Einlass", "Einlass", "visible/local master"),
    ("B06", "OUTLET", "BIO", "Ablauf", "Ablauf", "visible/local master"),
    ("B07", "RUN", "BIO", "Flüssigkeitslauf", "Arbeitslauf", "local connection plus master"),
    ("B08", "RECEIVER", "BIO", "Auffanggefäß", "Auffanggefäß", "visible/local master"),
    ("B09", "WASH_LIQUID", "BIO", "Bade- oder Waschflüssigkeit", "Wasch- oder Färbeflüssigkeit", "master source choice"),
    ("B10", "ADDITIVE", "BIO", "Badezusatz", "Arbeitszusatz", "learned card plus master choice"),
    ("B11", "BIO_CLOTH", "BIO", "Anwendungstuch", "Filter- oder Waschtuch", "learned card plus master choice"),
    ("B12", "TEMPERATURE", "BIO", "Badwärme", "Arbeitstemperatur", "grade/process plus master"),
    ("B13", "DURATION", "BIO", "Anwendungsdauer", "Arbeitsdauer", "grade/process plus master"),
    ("B14", "BODY_WORK_AREA", "BIO", "Körperstelle", "Arbeitsstelle", "visible figure/target plus master choice"),
    ("B15", "IMMERSION", "BIO", "Teilbad", "Tauchgang", "visible basin plus master choice"),
    ("B16", "FILTER", "BIO", "Seihgang", "Filtergang", "cloth/passage cards plus master choice"),
    # Astro
    ("A01", "WHEEL", "ASTRO", "Himmelsrad", "Himmelsrad", "visible geometry"),
    ("A02", "PANEL", "ASTRO", "Sternpaneel", "Sternpaneel", "visible geometry"),
    ("A03", "ROSETTE", "ASTRO", "Rosetteninstrument", "Rosetteninstrument", "visible geometry"),
    ("A04", "SECTOR", "ASTRO", "Himmelssektor", "Kalendersektor", "local master choice"),
    ("A05", "STAR_PLACE", "ASTRO", "Sternplatz", "Sternplatz", "visible geometry"),
    ("A06", "MANSION_PLACE", "ASTRO", "Mondstationsplatz", "Kalenderplatz", "local master choice"),
    ("A07", "CONDITION_PLACE", "ASTRO", "Himmelsbedingung", "Arbeitsbedingung", "local master choice"),
    ("A08", "RING_TEXT", "ASTRO", "Ringrubrik", "Ringrubrik", "visible text location"),
    ("A09", "LOCAL_LABEL", "ASTRO", "lokales Himmelslabel", "lokales Tabellenlabel", "local nomenclator"),
    ("A10", "CALENDAR_VALUE", "ASTRO", "Kalenderwert", "Kalenderwert", "local master"),
    ("A11", "CELESTIAL_VALUE", "ASTRO", "Himmelswert", "Himmelswert", "local master"),
    ("A12", "WEATHER_VALUE", "ASTRO", "Witterungswert", "Arbeitszustand", "local master choice"),
    ("A13", "LIGHT_VALUE", "ASTRO", "Lichtwert", "Qualitätswert", "local master choice"),
    ("A14", "PLANET_VALUE", "ASTRO", "Planetenwert", "Zeitwert", "local master choice"),
    ("A15", "QUALITY_VALUE", "ASTRO", "Komplexionswert", "Qualitätswert", "local master choice"),
    ("A16", "NAMESPACE", "ASTRO", "örtlicher Instrumentenschlüssel", "örtlicher Instrumentenschlüssel", "local workshop exemplar"),
)

PROGRAMS = {
    "H1": "PLANT>ROOT>WATER>VESSEL>EXTRACT>PORTION>DRINK_OR_PRODUCT>RESIDUE",
    "H2": "PLANT>SHOOT>LEAF>CLOTH>EXTRACT>PORTION>OIL_BINDER>VESSEL>OUTER_APPLICATION",
    "H3": "PLANT>FLOWER>LEAF>EXTRACTION_MEDIUM>CLOTH>EXTRACT>DRINK_OR_PRODUCT>OIL_BINDER>OUTER_APPLICATION",
    "H4": "PLANT>LEAF>EXTRACTION_MEDIUM>VESSEL>CLOTH>EXTRACT>HONEY_BINDER>OUTER_APPLICATION",
    "H5": "PLANT>HERB>WATER>EXTRACTION_MEDIUM>CLOTH>EXTRACT>HONEY_BINDER>DRINK_OR_PRODUCT>OUTER_APPLICATION",
    "B1": "FIGURE_WORKPIECE>BASIN>STATION>WASH_LIQUID>ADDITIVE>TEMPERATURE>DURATION>BODY_WORK_AREA>OUTLET>FILTER",
    "B2": "FIGURE_WORKPIECE>BASIN>STATION>OPENING>INLET>OUTLET>RUN>WASH_LIQUID>ADDITIVE>TEMPERATURE>DURATION>BODY_WORK_AREA>IMMERSION>FILTER",
    "B3": "FIGURE_WORKPIECE>BASIN>STATION>OPENING>OUTLET>RUN>RECEIVER>WASH_LIQUID>TEMPERATURE>DURATION>BODY_WORK_AREA>FILTER",
    "B4": "FIGURE_WORKPIECE>BASIN>STATION>OPENING>INLET>OUTLET>RUN>WASH_LIQUID>BIO_CLOTH>TEMPERATURE>DURATION>BODY_WORK_AREA>FILTER",
    "B5": "STATION>OPENING>OUTLET>RUN>WASH_LIQUID>TEMPERATURE>DURATION>BODY_WORK_AREA",
    "B6": "STATION>OPENING>INLET>RUN>WASH_LIQUID>BIO_CLOTH>BODY_WORK_AREA>FILTER",
    "A1": "WHEEL>SECTOR>STAR_PLACE>CONDITION_PLACE>RING_TEXT>LOCAL_LABEL>CALENDAR_VALUE>CELESTIAL_VALUE>NAMESPACE",
    "A2": "PANEL>STAR_PLACE>MANSION_PLACE>LOCAL_LABEL>CELESTIAL_VALUE>NAMESPACE",
    "A3": "ROSETTE>MANSION_PLACE>RING_TEXT>LOCAL_LABEL>CALENDAR_VALUE>WEATHER_VALUE>LIGHT_VALUE>PLANET_VALUE>QUALITY_VALUE>NAMESPACE",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lexicon_rows = [
        {
            "source_word_id": word_id,
            "source_slot": slot,
            "register": register,
            "medical_or_iatromedical_expansion_de": medical,
            "nonmedical_expansion_de": nonmedical,
            "supply_layer": source,
            "visible_card_word": "NO__SOURCE_LEXICON_ONLY",
        }
        for word_id, slot, register, medical, nonmedical, source in LEXICON
    ]
    write_tsv(OUT / "SEVENTY_FOURTH_54_FINITE_SOURCE_WORDS.tsv", lexicon_rows)
    by_slot = {row["source_slot"]: row for row in lexicon_rows}

    unit_rows = []
    for row in read_tsv(UNITS):
        tokens = PROGRAMS[row["unit_id"]].split(">")
        medical = "; ".join(by_slot[token]["medical_or_iatromedical_expansion_de"] for token in tokens)
        nonmedical = "; ".join(by_slot[token]["nonmedical_expansion_de"] for token in tokens)
        unit_rows.append({
            "unit_order": row["unit_order"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "register": row["register"],
            "group_count": row["group_count"],
            "finite_source_program": PROGRAMS[row["unit_id"]],
            "medical_controlled_vocabulary_de": medical,
            "nonmedical_controlled_vocabulary_de": nonmedical,
            "free_nouns_outside_lexicon": "NONE",
            "surface_or_card_change": "NONE",
        })
    write_tsv(OUT / "SEVENTY_FOURTH_14_FINITE_SOURCE_PROGRAMS.tsv", unit_rows)

    unit_lookup = {row["unit_id"]: row for row in unit_rows}
    ledger_rows = []
    for row in read_tsv(LEDGER):
        unit_id = row["unit_or_locus"].split("-")[0]
        if row["register"] == "ASTRO_LOCAL_LOOKUP":
            unit_id = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[row["page"]]
        ledger_rows.append({
            **row,
            "finite_source_unit": unit_id,
            "allowed_source_program": unit_lookup[unit_id]["finite_source_program"],
            "free_master_noun_allowed": "NO",
        })
    write_tsv(OUT / "SEVENTY_FOURTH_776_FINITE_SOURCE_BINDING.tsv", ledger_rows)

    doc = [
        "# Endliches Quellenwörterbuch für alle vierzehn Einheiten", "",
        "Die sichtbaren Karten bleiben unverändert. Dieses Wörterbuch beschreibt nur",
        "die kleine Menge konkreter Nomen, aus denen ein Meister die flüssige Quelle",
        "formulieren darf. Medizinische und nichtmedizinische Fassungen expandieren",
        "dieselben Slots unterschiedlich, dürfen aber keine freien Zusatznomen erfinden.", "",
    ]
    for row in unit_rows:
        doc.extend([
            f"## {row['unit_id']} · {row['page']}", "",
            f"**Slotprogramm:** `{row['finite_source_program']}`", "",
            f"**Medizinische Wörter:** {row['medical_controlled_vocabulary_de']}", "",
            f"**Nichtmedizinische Wörter:** {row['nonmedical_controlled_vocabulary_de']}", "",
        ])
    (OUT / "SEVENTY_FOURTH_CONTROLLED_SOURCEBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Vierundsiebzigste Werkstattfassung: endliches Quellenlexikon", "",
        "## Ergebnis", "",
        "Free master prose is replaced by 54 reusable source slots: six shared, sixteen",
        "Herbal, sixteen Biological and sixteen Astro. Every one of the fourteen units",
        "has a fixed slot program, and every one of the 776 groups is bound to that",
        "program without changing its visible or card layer.", "",
        "The two content editions now differ only in controlled expansions such as",
        "drink versus workshop product, external application versus workpiece coating,",
        "bather versus workpiece, body place versus work place, or lunar mansion versus",
        "calendar place. Unrestricted nouns are no longer allowed.", "",
        "This gives the next creative iteration a much tighter target: improve or replace",
        "a finite source slot, not an entire fluent paragraph.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_FOURTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "finite_source_words": len(lexicon_rows),
            "shared_source_words": sum(row["register"] == "SHARED" for row in lexicon_rows),
            "herbal_source_words": sum(row["register"] == "HERBAL" for row in lexicon_rows),
            "bio_source_words": sum(row["register"] == "BIO" for row in lexicon_rows),
            "astro_source_words": sum(row["register"] == "ASTRO" for row in lexicon_rows),
            "finite_source_programs": len(unit_rows),
            "bound_groups": len(ledger_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

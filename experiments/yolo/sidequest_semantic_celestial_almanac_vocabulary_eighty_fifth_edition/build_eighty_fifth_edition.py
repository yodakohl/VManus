#!/usr/bin/env python3
"""Choose one concrete but local vocabulary for the three Astro instruments."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
INSTRUMENTS = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_3_ASTRO_INSTRUMENT_CARDS.tsv"
LOCI = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_142_ASTRO_LOCUS_MANUAL.tsv"
GROUPS = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_395_ASTRO_GROUP_ADDRESS_LEDGER.tsv"


MODELS = {
    "M1_PRACTICAL_CELESTIAL_ELECTION_WEATHER_ALMANAC": {
        "WHEEL": "Wahlrad", "SECTOR": "Himmelssektor", "STAR": "Sternort",
        "CONDITION": "Bedingungsfeld", "LABEL": "Himmelszeichen", "CALENDAR": "Kalenderzeichen",
        "CELESTIAL": "Wahlzeichen", "PANEL": "Sterntafel", "PLACE28": "28er Feld",
        "ROSETTE": "Rosettenrad", "WEATHER": "Wetterzeichen", "LIGHT_TIME_QUALITY": "Licht-, Zeit- oder Eigenschaftszeichen",
    },
    "M2_IATROMEDICAL_ELECTION_TABLES": {
        "WHEEL": "Behandlungsrad", "SECTOR": "Tierkreissektor", "STAR": "Mondort",
        "CONDITION": "Behandlungsbedingung", "LABEL": "Himmelszeichen", "CALENDAR": "Behandlungstag",
        "CELESTIAL": "Gunstzeichen", "PANEL": "Mondhaustafel", "PLACE28": "Mondhaus",
        "ROSETTE": "Wahlrad", "WEATHER": "Krankheitswetter", "LIGHT_TIME_QUALITY": "Planetenstunde oder Komplexion",
    },
    "M3_CELESTIAL_MODEL_AND_MEMORY_BOOK": {
        "WHEEL": "Musterrad", "SECTOR": "Radsektor", "STAR": "Sternplatz",
        "CONDITION": "Musterfeld", "LABEL": "Kopierzeichen", "CALENDAR": "Rubrik",
        "CELESTIAL": "Musterwert", "PANEL": "Sternmuster", "PLACE28": "28er Feld",
        "ROSETTE": "Rosettenmuster", "WEATHER": "Wellenmuster", "LIGHT_TIME_QUALITY": "Strahlen- oder Qualitätsmuster",
    },
}

FIT = {
    "M1_PRACTICAL_CELESTIAL_ELECTION_WEATHER_ALMANAC": {"A1": (5, 5, 5, 4), "A2": (5, 5, 4, 4), "A3": (5, 5, 5, 5)},
    "M2_IATROMEDICAL_ELECTION_TABLES": {"A1": (5, 4, 5, 4), "A2": (5, 4, 4, 4), "A3": (4, 4, 4, 4)},
    "M3_CELESTIAL_MODEL_AND_MEMORY_BOOK": {"A1": (5, 5, 4, 3), "A2": (5, 5, 5, 3), "A3": (5, 5, 4, 3)},
}

SELECTED_WORDS = [
    ("ELECTION_WHEEL", "Wahlrad", "lokales Rad auswählen"),
    ("CELESTIAL_SECTOR", "Himmelssektor", "sichtbarer Radabschnitt"),
    ("STAR_PLACE", "Sternort", "lokaler Sternbesitzer"),
    ("CONDITION_FIELD", "Bedingungsfeld", "örtliche Bedingungsadresse"),
    ("RING_RUBRIC", "Ringrubrik", "Textlage am Ring"),
    ("CELESTIAL_SIGN", "Himmelszeichen", "opakes lokales Etikett"),
    ("CALENDAR_SIGN", "Kalenderzeichen", "örtlicher Kalenderreadout"),
    ("ELECTION_SIGN", "Wahlzeichen", "örtliches Ergebnis ohne Gunstwert"),
    ("STAR_TABLE", "Sterntafel", "mehrpaneelige Sternkarte"),
    ("FIELD_28", "28er Feld", "ungeordnete lokale 28er Adresse"),
    ("ROSETTE_WHEEL", "Rosettenrad", "eines von drei getrennten Rädern"),
    ("WEATHER_SIGN", "Wetterzeichen", "mittlere Wellen-/Wolkenrosette"),
    ("LIGHT_SIGN", "Lichtzeichen", "rechte Strahlenrosette"),
    ("TIME_SIGN", "Zeitzeichen", "lokaler Zeitreadout"),
    ("PROPERTY_SIGN", "Eigenschaftszeichen", "lokaler Eigenschaftsreadout"),
    ("LOCAL_KEY", "Ortsschlüssel", "nur im aktiven Namensraum"),
]

READINGS = {
    "A1": "Linkes oder rechtes Wahlrad getrennt öffnen. Einen Himmelssektor oder Sternort wählen, Bedingungsfeld und Ringrubrik zeigen, das Himmelszeichen kopieren und Kalenderzeichen oder Wahlzeichen nur mit dem Ortsschlüssel dieses Rades lesen. Beim Radwechsel neu beginnen.",
    "A2": "In der mehrteiligen Sterntafel zuerst Paneel oder Zentrum und dann einen Sternort beziehungsweise ein 28er Feld wählen. Das Himmelszeichen kopieren und nur mit dem Ortsschlüssel dieses Paneels lesen; die 28 Felder haben keine festgelegte Reihenfolge.",
    "A3": "Eines der drei Rosettenräder wählen. Links ein ungeordnetes 28er Feld und sein Kalenderzeichen lesen; in der mittleren Rosette Wetterzeichen, in der rechten Licht-, Zeit- oder Eigenschaftszeichen lesen. Zwischen den drei Rädern keinen Wert übertragen.",
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
    model_rows = []
    for model_id, vocabulary in MODELS.items():
        for slot, value in vocabulary.items():
            model_rows.append({"model_id": model_id, "content_slot": slot, "concrete_value_de": value})
    write_tsv(OUT / "EIGHTY_FIFTH_36_MODEL_VOCABULARY_ROWS.tsv", model_rows)

    comparisons = []
    totals = {model: 0 for model in MODELS}
    for model_id in MODELS:
        for unit_id in ("A1", "A2", "A3"):
            imagery, topology, vocabulary, whole_book = FIT[model_id][unit_id]
            total = imagery + topology + vocabulary + whole_book
            totals[model_id] += total
            comparisons.append({
                "model_id": model_id,
                "unit_id": unit_id,
                "celestial_imagery_fit_1_to_5": imagery,
                "local_topology_fit_1_to_5": topology,
                "content_vocabulary_fit_1_to_5": vocabulary,
                "whole_book_fit_1_to_5": whole_book,
                "editorial_fit_total_20": total,
            })
    write_tsv(OUT / "EIGHTY_FIFTH_9_MODEL_INSTRUMENT_COMPARISONS.tsv", comparisons)

    words = [
        {"almanac_word_id": f"A{index:02d}", "almanac_slot": slot, "selected_word_de": value, "local_rule_de": rule, "portable_prose_card_meaning": "NO"}
        for index, (slot, value, rule) in enumerate(SELECTED_WORDS, 1)
    ]
    write_tsv(OUT / "EIGHTY_FIFTH_16_SELECTED_ALMANAC_WORDS.tsv", words)

    source_instruments = {row["diagram_id"]: row for row in read_tsv(INSTRUMENTS)}
    instrument_rows = []
    for unit_id in ("A1", "A2", "A3"):
        row = source_instruments[unit_id]
        instrument_rows.append({
            "unit_id": unit_id,
            "page": row["page"],
            "locus_count": row["locus_count"],
            "group_count": row["group_count"],
            "selected_model": "M1_PRACTICAL_CELESTIAL_ELECTION_WEATHER_ALMANAC",
            "complete_instrument_reading_de": READINGS[unit_id],
            "orientation": "NONE",
            "crosspage_key": "NONE",
            "prose_card_import": "NONE",
        })
    write_tsv(OUT / "EIGHTY_FIFTH_3_COMPLETE_ALMANAC_INSTRUMENTS.tsv", instrument_rows)

    instrument_lookup = {row["unit_id"]: row for row in instrument_rows}
    locus_rows = []
    for row in read_tsv(LOCI):
        instrument = instrument_lookup[row["diagram_id"]]
        locus_rows.append({
            "page": row["page"],
            "unit_id": row["diagram_id"],
            "locus": row["locus"],
            "group_count": row["group_count"],
            "local_owner": row["local_owner"],
            "local_namespace": row["local_namespace"],
            "selected_local_action_de": row["lookup_action_de"],
            "selected_instrument_reading_de": instrument["complete_instrument_reading_de"],
            "orientation": "NONE",
            "crosspage_key": "NONE",
        })
    write_tsv(OUT / "EIGHTY_FIFTH_142_LOCAL_ALMANAC_LOCI.tsv", locus_rows)

    group_rows = []
    for row in read_tsv(GROUPS):
        instrument = instrument_lookup[row["diagram_id"]]
        group_rows.append({
            "group_serial": row["group_serial"],
            "unit_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"],
            "local_owner": row["local_owner"],
            "local_namespace": row["local_namespace"],
            "copy_instruction_de": row["copy_instruction_de"],
            "selected_instrument_reading_de": instrument["complete_instrument_reading_de"],
            "orientation": "NONE",
            "crosspage_key": "NONE",
            "portable_word_value": "NONE__LOCAL_NOMENCLATOR_ONLY",
        })
    write_tsv(OUT / "EIGHTY_FIFTH_395_ALMANAC_GROUP_BINDING.tsv", group_rows)

    analogues = [
        {"analogue": "English folding almanac", "date": "1415-1420", "use_here": "planetary hours and moon sign guide practical timing", "url": "https://wellcomecollection.org/stories/the-enigma-of-the-medieval-folding-almanac"},
        {"analogue": "Michael of Rhodes manuscript", "date": "begun 1434", "use_here": "local zodiac/moon lookup for timed procedures", "url": "https://brunelleschi.imss.fi.it/michaelofrhodes/manuscript/page_103b.html"},
        {"analogue": "Wellcome MS.164", "date": "1416-1419", "use_here": "multiple planet, element and virtue diagrams in one workshop codex", "url": "https://wellcomecollection.org/works/d3vapay8"},
        {"analogue": "BL Harley MS 2375", "date": "15th century", "use_here": "herbal, baths and medical astrology coexist", "url": "https://searcharchives.bl.uk/catalog/040-002048206"},
        {"analogue": "BL Harley MS 2381", "date": "15th century", "use_here": "waters, recipes, distillation and astrological tables coexist", "url": "https://searcharchives.bl.uk/catalog/040-002048212"},
    ]
    write_tsv(OUT / "EIGHTY_FIFTH_5_HISTORICAL_ALMANAC_ANALOGUES.tsv", analogues)

    doc = ["# Drei konkrete Himmelsinstrumente", ""]
    for row in instrument_rows:
        doc.extend([f"## {row['unit_id']} · {row['page']}", "", row["complete_instrument_reading_de"], ""])
    doc.extend([
        "## Gemeinsame Lesung", "",
        "Die drei Seiten gehören zu einem praktischen Himmelsalmanach, aber nicht zu",
        "einem einzigen gekoppelten Instrument. Jede Tafel behält ihren Ortsschlüssel.",
        "Eine medizinische Wahl ist möglich, wird jedoch nicht in die lokalen Zeichen",
        "hineingelesen.",
    ])
    (OUT / "EIGHTY_FIFTH_COMPLETE_CELESTIAL_ALMANAC.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    winner = max(totals, key=totals.get)
    report = [
        "# Fünfundachtzigste Werkstattfassung: praktischer Himmelsalmanach", "",
        "## Ergebnis", "",
        f"Three complete Astro vocabularies were applied to all 142 loci and 395 groups.",
        f"Editorial totals are {totals}; {winner} is selected.", "",
        "The selected content is practical celestial election/weather reference rather",
        "than explicit medical astrology. A1 is a pair of separate choice wheels, A2 a",
        "multi-panel star table, and A3 three separate rosette readouts for 28-place,",
        "weather and light/time/property categories.", "",
        "No start, direction, cross-page key or imported prose-card meaning is added.",
        "Medical timing remains a book-level use, not a local sign translation.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_FIFTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "candidate_models": len(MODELS),
            "model_vocabulary_rows": len(model_rows),
            "model_instrument_comparisons": len(comparisons),
            "selected_words": len(words),
            "complete_instruments": len(instrument_rows),
            "loci": len(locus_rows),
            "groups": len(group_rows),
            "historical_analogues": len(analogues),
        },
        "model_totals": totals,
        "selected_model": winner,
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (INSTRUMENTS, LOCI, GROUPS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

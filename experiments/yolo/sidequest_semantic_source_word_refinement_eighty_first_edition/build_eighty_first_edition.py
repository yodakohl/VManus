#!/usr/bin/env python3
"""Rank all finite source words and replace the clumsiest working values."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_selected_workshop_eightieth_edition/EIGHTIETH_54_SELECTED_SOURCE_LEXICON.tsv"
LICENSES = ROOT / "experiments/yolo/sidequest_semantic_selected_workshop_eightieth_edition/EIGHTIETH_43_CARD_SOURCE_LICENSES.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_selected_workshop_eightieth_edition/EIGHTIETH_14_CONTROLLED_UNIT_EDITION.tsv"
EVENT_AUDIT = ROOT / "experiments/yolo/sidequest_semantic_card_source_crosswalk_seventy_seventh_edition/SEVENTY_SEVENTH_381_EVENT_LICENSE_AUDIT.tsv"


REVISIONS = {
    "EXTRACTION_MEDIUM": ("Auszugsflüssigkeit", "Das Kompositum sagt Stoffrolle und bleibt kürzer als eine freie Weinannahme."),
    "OIL_BINDER": ("Trägerstoff", "Ein konkreter technischer Rollenname ersetzt den abstrakten Träger."),
    "HONEY_BINDER": ("Bindestoff", "Der Rollenname ist kurz und verlangt weder Honig noch Leim."),
    "DRINK_OR_PRODUCT": ("Mittel", "Mittel funktioniert als Arznei- oder Werkmittel und ist kein modernes Endproduktetikett."),
    "FILTER": ("Seihgang", "Die Arbeitssprache braucht einen Vorgang statt des infiniten Filtern."),
    "MANSION_PLACE": ("28er Feld", "Das Wort benennt die sichtbare Adresse ohne Mondstationsclaim."),
    "CONDITION_PLACE": ("Bedingungsfeld", "Der lokale Platz ist ein Feld mit Bedingung, nicht die Bedingung selbst."),
    "LOCAL_LABEL": ("Himmelszeichen", "Zeichen ist natürlicher als das moderne Label und bleibt bildnah."),
    "WEATHER_VALUE": ("Wetterzeichen", "Die mittlere Rosette wird als Wetterzeichen gelesen, nicht als abstrakter Wert."),
    "LIGHT_VALUE": ("Lichtzeichen", "Das Strahlenmotiv liefert ein Zeichen, keinen metrischen Lichtwert."),
    "PLANET_VALUE": ("Zeitzeichen", "Ohne identifizierten Planeten bleibt die temporale Zeichenrolle."),
    "QUALITY_VALUE": ("Eigenschaft", "Eine lokale Eigenschaft ist verständlicher als ein Qualitätswert."),
}

DIRECT_VISIBLE = {
    "PLANT", "ROOT", "SHOOT", "LEAF", "FLOWER", "HERB", "FIGURE_WORKPIECE",
    "BASIN", "STATION", "OPENING", "INLET", "OUTLET", "RUN", "RECEIVER",
    "WHEEL", "PANEL", "ROSETTE", "SECTOR", "STAR_PLACE", "MANSION_PLACE",
    "RING_TEXT", "LOCAL_LABEL",
}
VISIBLE_PLUS_CARD = {
    "OWNER", "TARGET", "PORTION", "RESULT", "VESSEL", "CLOTH", "EXTRACT",
    "BIO_CLOTH", "BODY_WORK_AREA", "IMMERSION", "FILTER", "CONDITION_PLACE",
}
CARD_OR_REGISTER = {"ITEM", "PREVIOUS", "ADDITIVE", "TEMPERATURE", "DURATION", "NAMESPACE"}


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
    lexicon = read_tsv(LEXICON)
    units = read_tsv(UNITS)
    license_entries = Counter()
    for row in read_tsv(LICENSES):
        if row["licensed_source_slots"] != "NONE":
            for slot in row["licensed_source_slots"].split(","):
                license_entries[slot] += 1
    event_exposures = Counter()
    for row in read_tsv(EVENT_AUDIT):
        if row["licensed_source_slots_in_this_unit"] != "NONE":
            for slot in row["licensed_source_slots_in_this_unit"].split(";"):
                event_exposures[slot] += 1
    unit_uses: dict[str, list[str]] = defaultdict(list)
    weighted_uses = Counter()
    for row in units:
        for slot in row["source_slot_program"].split(">"):
            unit_uses[slot].append(row["unit_id"])
            weighted_uses[slot] += int(row["group_count"])

    rows = []
    revised_lexicon = []
    for row in lexicon:
        slot = row["source_slot"]
        current = row["selected_source_value_de"]
        revised, reason = REVISIONS.get(slot, (current, "Der kurze aktuelle Wert bleibt verständlich und wird beibehalten."))
        if slot in DIRECT_VISIBLE:
            provenance = "DIRECT_VISIBLE_OWNER_OR_GEOMETRY"
            confidence = 5 if slot not in {"RUN", "MANSION_PLACE", "LOCAL_LABEL"} else 4
        elif slot in VISIBLE_PLUS_CARD:
            provenance = "VISIBLE_CONTEXT_PLUS_CARD"
            confidence = 4
        elif slot in CARD_OR_REGISTER:
            provenance = "CARD_OR_REGISTER_ONLY"
            confidence = 3
        else:
            provenance = "MASTER_SELECTED_CONTENT"
            confidence = 2
        action = "REVISE_PLAINER" if slot in REVISIONS else "KEEP"
        rows.append({
            "source_word_id": row["source_word_id"],
            "source_slot": slot,
            "register": row["register"],
            "current_value_de": current,
            "revised_value_de": revised,
            "action": action,
            "provenance_class": provenance,
            "working_confidence_1_to_5": confidence,
            "unit_uses": ";".join(unit_uses[slot]) or "NONE",
            "unit_use_count": len(unit_uses[slot]),
            "group_weighted_program_exposure": weighted_uses[slot],
            "licensing_dictionary_entries": license_entries[slot],
            "licensing_prose_events": event_exposures[slot],
            "reason_de": reason,
        })
        revised_lexicon.append({
            **row,
            "eighty_first_selected_value_de": revised,
            "eighty_first_action": action,
            "eighty_first_provenance": provenance,
            "eighty_first_working_confidence_1_to_5": confidence,
        })
    write_tsv(OUT / "EIGHTY_FIRST_54_SOURCE_WORD_RANKING.tsv", rows)
    write_tsv(OUT / "EIGHTY_FIRST_54_REFINED_SOURCE_LEXICON.tsv", revised_lexicon)

    revisions = [row for row in rows if row["action"] == "REVISE_PLAINER"]
    write_tsv(OUT / "EIGHTY_FIRST_12_SOURCE_WORD_REVISIONS.tsv", revisions)

    doc = ["# Verfeinertes Quellenwörterbuch", ""]
    for register in ("SHARED", "HERBAL", "BIO", "ASTRO"):
        doc.extend([f"## {register}", ""])
        for row in rows:
            if row["register"] != register:
                continue
            marker = "→" if row["action"] == "REVISE_PLAINER" else "="
            doc.append(f"- `{row['source_slot']}`: {row['current_value_de']} {marker} **{row['revised_value_de']}** ({row['provenance_class']}, {row['working_confidence_1_to_5']}/5)")
        doc.append("")
    (OUT / "EIGHTY_FIRST_REFINED_SOURCE_DICTIONARY.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Einundachtzigste Werkstattfassung: Quellenwort-Verfeinerung", "",
        "## Ergebnis", "",
        "All 54 source words are ranked by visible, card, register or master supply.",
        "Twelve awkward or overly modern values are replaced with plainer workshop",
        "terms: Auszugsflüssigkeit, Trägerstoff, Bindestoff, Mittel, Seihgang, 28er",
        "Feld, Bedingungsfeld, Himmelszeichen, Wetterzeichen, Lichtzeichen, Zeitzeichen",
        "and Eigenschaft.", "",
        "The revision changes no card/root meaning. It improves only the vocabulary that",
        "owner and unit program may supply after the card has opened a licensed slot.", "",
        "The weakest remaining content words are water and the unnamed contents of",
        "medium, carrier, binder, result and celestial readout slots. Those remain",
        "creative defaults rather than decoded lexemes.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_FIRST_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    provenance_counts = Counter(row["provenance_class"] for row in rows)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "source_words": len(rows),
            "revisions": len(revisions),
            **dict(sorted(provenance_counts.items())),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LEXICON, LICENSES, UNITS, EVENT_AUDIT)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

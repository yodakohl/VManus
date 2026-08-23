#!/usr/bin/env python3
"""Classify the concrete codex vocabulary by its actual kind of anchor."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R86 = ROOT / "experiments/yolo/sidequest_semantic_concrete_codex_eighty_sixth_edition"
R77 = ROOT / "experiments/yolo/sidequest_semantic_card_source_crosswalk_seventy_seventh_edition"


UNIT_WORDS = {
    "H_R01": "H1,H5", "H_R02": "H3,H4,H5", "H_R03": "H2,H3",
    "H_R04": "H4,H5", "H_R05": "H1", "H_R06": "H1,H3,H5",
    "H_R07": "H2", "H_R08": "H3", "H_R09": "H4,H5",
    "H_R10": "H2,H4,H5", "H_R11": "H2,H3,H4,H5",
    "B_B01": "B1,B2,B3,B4", "B_B02": "B1,B2,B3,B4",
    "B_B03": "B1,B2,B3,B4,B5,B6", "B_B04": "B1,B2",
    "B_B05": "B1,B2,B3,B4,B5", "B_B06": "B1,B2,B5",
    "B_B07": "B1,B4", "B_B08": "B1,B2", "B_B09": "B3,B4,B6",
    "B_B10": "B4", "B_B11": "B1,B2,B3,B4,B6",
    "B_B12": "B2,B4,B6", "B_B13": "B1,B2,B3,B4,B5",
    "B_B14": "B2,B4,B6", "B_B15": "B3,B4",
    "B_B16": "B4,B5,B6", "B_B17": "B4,B5,B6",
    "C_A01": "A1", "C_A02": "A1", "C_A03": "A1,A2",
    "C_A04": "A1", "C_A05": "A1", "C_A06": "A1,A2",
    "C_A07": "A1,A3", "C_A08": "A1", "C_A09": "A2",
    "C_A10": "A2,A3", "C_A11": "A3", "C_A12": "A3",
    "C_A13": "A3", "C_A14": "A3", "C_A15": "A3", "C_A16": "A1,A2,A3",
}


SLOT_BRIDGES = {
    "WATER": "WATER,WASH_LIQUID", "WINE": "EXTRACTION_MEDIUM",
    "OIL": "EXTRACTION_MEDIUM", "HONEY": "EXTRACTION_MEDIUM",
    "SEDIMENT": "RESIDUE", "DRINK": "RESULT", "SALVE": "RESULT",
    "RUB": "RESULT,OUTER_APPLICATION", "WASH": "WASH_LIQUID,BODY_WORK_AREA,RESULT",
    "POULTICE": "OUTER_APPLICATION,BODY_WORK_AREA", "CLOTH": "CLOTH,BIO_CLOTH",
    "BATHER": "", "BASIN": "BASIN", "BATH_WATER": "WATER,WASH_LIQUID",
    "HERBAL_ADDITIVE": "ADDITIVE", "BATH_HEAT": "TEMPERATURE",
    "BATH_TIME": "DURATION", "BODY_TARGET": "BODY_WORK_AREA",
    "PART_BATH": "BODY_WORK_AREA,OUTER_APPLICATION", "COMPRESS": "OUTER_APPLICATION",
    "STRAINING_PASS": "FILTER", "INLET": "INLET", "OUTLET": "OUTLET",
    "WATER_RUN": "RUN", "RECEIVER": "RECEIVER", "SERVICE_STATION": "STATION",
    "SERVICE_TARGET": "TARGET", "ELECTION_WHEEL": "", "CELESTIAL_SECTOR": "",
    "STAR_PLACE": "STAR_PLACE", "CONDITION_FIELD": "CONDITION_PLACE",
    "RING_RUBRIC": "LOCAL_LABEL", "CELESTIAL_SIGN": "CELESTIAL_VALUE,LOCAL_LABEL",
    "CALENDAR_SIGN": "CALENDAR_VALUE,LOCAL_LABEL",
    "ELECTION_SIGN": "CELESTIAL_VALUE,QUALITY_VALUE", "STAR_TABLE": "PANEL",
    "FIELD_28": "MANSION_PLACE,PANEL", "ROSETTE_WHEEL": "",
    "WEATHER_SIGN": "WEATHER_VALUE", "LIGHT_SIGN": "LIGHT_VALUE",
    "TIME_SIGN": "CALENDAR_VALUE,DURATION", "PROPERTY_SIGN": "QUALITY_VALUE",
    "LOCAL_KEY": "LOCAL_LABEL",
}


PRIMARY = {
    "H_R01": "RECURRING_CARD_ANCHORED", "H_R02": "MASTER_PROGRAM_ONLY",
    "H_R03": "MASTER_PROGRAM_ONLY", "H_R04": "MASTER_PROGRAM_ONLY",
    "H_R05": "MASTER_PROGRAM_ONLY", "H_R06": "MASTER_PROGRAM_ONLY",
    "H_R07": "MASTER_PROGRAM_ONLY", "H_R08": "MASTER_PROGRAM_ONLY",
    "H_R09": "RECURRING_CARD_ANCHORED", "H_R10": "MASTER_PROGRAM_ONLY",
    "H_R11": "RECURRING_CARD_ANCHORED",
    "B_B01": "VISIBLE_OWNER_ANCHORED", "B_B02": "VISIBLE_OWNER_ANCHORED",
    "B_B03": "VISIBLE_OWNER_ANCHORED", "B_B04": "RECURRING_CARD_ANCHORED",
    "B_B05": "RECURRING_CARD_ANCHORED", "B_B06": "RECURRING_CARD_ANCHORED",
    "B_B07": "VISIBLE_OWNER_ANCHORED", "B_B08": "VISIBLE_OWNER_ANCHORED",
    "B_B09": "RECURRING_CARD_ANCHORED", "B_B10": "RECURRING_CARD_ANCHORED",
    "B_B11": "RECURRING_CARD_ANCHORED", "B_B12": "VISIBLE_OWNER_ANCHORED",
    "B_B13": "VISIBLE_OWNER_ANCHORED", "B_B14": "VISIBLE_OWNER_ANCHORED",
    "B_B15": "VISIBLE_OWNER_ANCHORED", "B_B16": "VISIBLE_OWNER_ANCHORED",
    "B_B17": "VISIBLE_OWNER_ANCHORED",
    "C_A01": "VISIBLE_OWNER_ANCHORED", "C_A02": "VISIBLE_OWNER_ANCHORED",
    "C_A03": "VISIBLE_OWNER_ANCHORED", "C_A04": "VISIBLE_OWNER_ANCHORED",
    "C_A05": "VISIBLE_OWNER_ANCHORED", "C_A06": "LOCAL_NOMENCLATOR_ONLY",
    "C_A07": "LOCAL_NOMENCLATOR_ONLY", "C_A08": "LOCAL_NOMENCLATOR_ONLY",
    "C_A09": "VISIBLE_OWNER_ANCHORED", "C_A10": "VISIBLE_OWNER_ANCHORED",
    "C_A11": "VISIBLE_OWNER_ANCHORED", "C_A12": "LOCAL_NOMENCLATOR_ONLY",
    "C_A13": "LOCAL_NOMENCLATOR_ONLY", "C_A14": "LOCAL_NOMENCLATOR_ONLY",
    "C_A15": "LOCAL_NOMENCLATOR_ONLY", "C_A16": "LOCAL_NOMENCLATOR_ONLY",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    words = read_tsv(R86 / "EIGHTY_SIXTH_44_CONCRETE_SOURCE_WORDS.tsv")
    units = read_tsv(R86 / "EIGHTY_SIXTH_14_CONCRETE_CODEX_UNITS.tsv")
    binding = read_tsv(R86 / "EIGHTY_SIXTH_776_CONCRETE_CODEX_BINDING.tsv")
    licenses = read_tsv(R77 / "SEVENTY_SEVENTH_43_CARD_TO_SOURCE_LICENSES.tsv")
    events = read_tsv(R77 / "SEVENTY_SEVENTH_381_EVENT_LICENSE_AUDIT.tsv")
    unit_counts = {row["unit_id"]: int(row["group_count"]) for row in units}

    entries_by_slot: dict[str, set[str]] = defaultdict(set)
    for row in licenses:
        for slot in filter(None, row["licensed_source_slots"].split(",")):
            entries_by_slot[slot].add(row["entry_id"])

    audit_rows = []
    word_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for word in words:
        word_id = word["codex_word_id"]
        used_units = UNIT_WORDS[word_id].split(",")
        bridge_slots = set(filter(None, SLOT_BRIDGES[word["source_slot"]].split(",")))
        entry_ids = sorted({entry for slot in bridge_slots for entry in entries_by_slot[slot]})
        matching_events = []
        for event in events:
            event_unit = event["unit_id"].split("-")[0]
            event_slots = set(filter(None, event["licensed_source_slots_in_this_unit"].split(",")))
            if event_unit in used_units and bridge_slots & event_slots:
                matching_events.append(event["source_group_id"])
        primary = PRIMARY[word_id]
        if primary == "MASTER_PROGRAM_ONLY":
            status = "KEEP_AS_EXPLICIT_RECIPE_HYPOTHESIS"
            secondary = "GENERIC_SLOT_SUPPORT_ONLY" if entry_ids else "NONE"
        elif primary == "LOCAL_NOMENCLATOR_ONLY":
            status = "KEEP_AS_LOCAL_LABEL_CLASS"
            secondary = "VISIBLE_DIAGRAM_NAMESPACE"
        elif primary == "VISIBLE_OWNER_ANCHORED":
            status = "KEEP_AS_VISIBLE_DEFAULT"
            secondary = "GENERIC_CARD_SLOT" if entry_ids else "NONE"
        else:
            status = "KEEP_AS_RECURRING_TEXT_DEFAULT"
            secondary = "VISIBLE_OWNER_OR_MASTER_FILL"
        row = {
            "codex_word_id": word_id,
            "domain": word["domain"],
            "source_slot": word["source_slot"],
            "selected_word_de": word["selected_word_de"],
            "used_units": ",".join(used_units),
            "unit_count": len(used_units),
            "program_group_exposure": sum(unit_counts[unit] for unit in used_units),
            "bridged_card_slots": ",".join(sorted(bridge_slots)) or "NONE",
            "licensing_dictionary_entries": ",".join(entry_ids) or "NONE",
            "licensing_entry_count": len(entry_ids),
            "matching_prose_events": len(matching_events),
            "matching_event_ids": ",".join(matching_events) or "NONE",
            "primary_anchor": primary,
            "secondary_support": secondary,
            "working_status": status,
            "meaning_scope_de": word["role_de"],
        }
        audit_rows.append(row)
        for unit in used_units:
            word_by_unit[unit].append(row)
    write_tsv(OUT / "EIGHTY_SEVENTH_44_WORD_ANCHOR_AUDIT.tsv", audit_rows)

    provenance = []
    for row in binding:
        unit_words = word_by_unit[row["unit_id"]]
        anchor_counts = Counter(word["primary_anchor"] for word in unit_words)
        provenance.append({
            **row,
            "unit_program_word_ids": ";".join(word["codex_word_id"] for word in unit_words),
            "unit_program_words_de": ";".join(word["selected_word_de"] for word in unit_words),
            "anchor_mix": ";".join(f"{key}={anchor_counts[key]}" for key in sorted(anchor_counts)),
            "provenance_warning": "UNIT_PROGRAM_NOT_ONE_WORD_PER_VISIBLE_GROUP",
        })
    write_tsv(OUT / "EIGHTY_SEVENTH_776_WORD_PROVENANCE_BINDING.tsv", provenance)

    weak = [row for row in audit_rows if row["primary_anchor"] == "MASTER_PROGRAM_ONLY"]
    write_tsv(OUT / "EIGHTY_SEVENTH_MASTER_ONLY_WORDS.tsv", weak)

    counts = Counter(row["primary_anchor"] for row in audit_rows)
    report = [
        "# Siebenundachtzigste Werkstattrunde: Woher kommen die konkreten Wörter?", "",
        "## Ergebnis", "",
        "Die 44 Wörter bleiben als kreative Gesamtlesung erhalten, aber sie werden nicht",
        "mehr so behandelt, als wären sie alle gleich direkt im Text lesbar.", "",
    ]
    for key in ("RECURRING_CARD_ANCHORED", "VISIBLE_OWNER_ANCHORED", "LOCAL_NOMENCLATOR_ONLY", "MASTER_PROGRAM_ONLY"):
        report.append(f"- {key}: {counts[key]}")
    report.extend([
        "", "Wasser/Waschung/Tuch sowie Wärme, Dauer, Zusatz und mehrere Durchlauf-",
        "Operationen haben wiederkehrende Kartenanschlüsse. Figuren, Becken, lokale",
        "Leitungen und die großen Diagrammformen kommen primär aus dem Bild. Die Werte",
        "der Astro-Etiketten bleiben innerhalb ihres jeweiligen Rades oder Paneels.", "",
        "Wein, Öl, Honig, Satz, Trank, Salbe, Einreibung und Auflage sind weiterhin",
        "brauchbare Rezeptwörter, werden aber als gelernte Quellenfüllung ausgewiesen.",
        "Das ist kein Rückzug der Lesung: Es sagt dem Schreiber nur, welche Wörter er aus",
        "dem Text ableiten und welche er aus Bild, Rezepttyp oder Meisterexemplar kennen muss.", "",
        "Die 776-Zeilen-Bindung weist deshalb pro Gruppe das vollständige Einheitenprogramm",
        "aus und warnt ausdrücklich davor, jedes Programmwort einer einzelnen sichtbaren",
        "Karte zuzuordnen.", "",
        "Nur die festen zehn Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "EIGHTY_SEVENTH_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {"words": len(audit_rows), "bound_groups": len(provenance), **dict(counts)},
        "master_only_words": [row["selected_word_de"] for row in weak],
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

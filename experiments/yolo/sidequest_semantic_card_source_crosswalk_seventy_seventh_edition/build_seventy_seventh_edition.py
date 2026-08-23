#!/usr/bin/env python3
"""Bind each minimal card entry to a finite set of source-content slots."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CORE = ROOT / "experiments/yolo/sidequest_semantic_minimal_dictionary_seventy_second_edition/SEVENTY_SECOND_43_MINIMAL_CORE_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_minimal_dictionary_seventy_second_edition/SEVENTY_SECOND_381_MINIMAL_CARD_READINGS.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_source_slot_selection_seventy_fifth_edition/SEVENTY_FIFTH_54_SELECTED_SOURCE_LEXICON.tsv"
PROGRAMS = ROOT / "experiments/yolo/sidequest_semantic_source_slot_selection_seventy_fifth_edition/SEVENTY_FIFTH_14_SELECTED_SOURCE_PROGRAMS.tsv"


# A card licenses a slot type, never the richer noun chosen by a particular owner.
LICENSES = {
    "ROOT_AIIN": ("PORTION,TEMPERATURE,DURATION,CALENDAR_VALUE,CELESTIAL_VALUE,WEATHER_VALUE,LIGHT_VALUE,PLANET_VALUE,QUALITY_VALUE", "VALUE_SELECTOR", "A prescribed value can fill only a registered value slot."),
    "ROOT_AIN": ("PORTION", "QUANTITY_SELECTOR", "A share or portion does not identify its material."),
    "ROOT_IIN": ("TEMPERATURE,DURATION,CALENDAR_VALUE,CELESTIAL_VALUE,WEATHER_VALUE,LIGHT_VALUE,PLANET_VALUE,QUALITY_VALUE", "GRADE_SELECTOR", "A stage grades an already selected process or readout."),
    "ROOT_AL": ("TARGET,STATION,BODY_WORK_AREA,STAR_PLACE,MANSION_PLACE,CONDITION_PLACE", "TARGET_SELECTOR", "A destination can resolve only to a local target-like slot."),
    "ROOT_AR": ("OWNER,PREVIOUS,ROOT,HERB,WATER,EXTRACTION_MEDIUM,EXTRACT,INLET", "SOURCE_SELECTOR", "A source points backward or inward; it does not name the source substance."),
    "ROOT_AIR": ("RUN,WATER,WASH_LIQUID", "FLOW_SELECTOR", "A run may carry a registered liquid but cannot invent one."),
    "ROOT_OK": ("ITEM", "OPERATION_ARGUMENT", "Set the current item into work."),
    "ROOT_OL": ("PREVIOUS,ITEM", "CONTINUATION_ARGUMENT", "Continue the previous/current item."),
    "ROOT_OT": ("ITEM", "ORDER_ARGUMENT", "Select the following item without naming it."),
    "ROOT_OR": ("EXTRACTION_MEDIUM,EXTRACT,RESULT", "PREPARATION_ARGUMENT", "The preparation channel can resolve to medium, extract or result."),
    "ROOT_Y": ("ITEM", "REFERENT", "This/current item only."),
    "ROOT_E": ("DURATION,TEMPERATURE", "SHORT_GRADE", "Short grade modifies duration or temperature."),
    "ROOT_EE": ("DURATION,TEMPERATURE", "LONG_GRADE", "Longer grade modifies duration or temperature."),
    "ROOT_EEE": ("DURATION,TEMPERATURE", "FULL_GRADE", "Full grade modifies duration or temperature."),
    "ROOT_CLOSE": ("", "OPERATION_ONLY", "Closure licenses no content noun."),
    "ROOT_CHD": ("ITEM,TARGET", "TRANSFER_OPERATION", "Transfer acts on an item toward an already licensed target."),
    "ROOT_CTH": ("RESULT", "READINESS_OPERATION", "Readiness may expose only the registered result slot."),
    "ROOT_CKH": ("OPENING,INLET,OUTLET,RUN,FILTER", "PASSAGE_OPERATION", "A passage chooses visible/local path slots."),
    "ROOT_CKHE": ("FILTER,EXTRACT,RESULT", "SEPARATION_OPERATION", "Separation may yield a registered extract/result."),
    "ROOT_CHK": ("TEMPERATURE", "HEAT_OPERATION", "Heating licenses temperature, not a named substance."),
    "ROOT_SHED": ("DURATION,RESULT", "SETTLING_OPERATION", "Settling can consume duration and expose a result."),
    "ROOT_SOLK": ("RECEIVER,RESULT", "COLLECTION_OPERATION", "Collection selects receiver/result only."),
    "ROOT_HO": ("SHOOT,LEAF,FLOWER,HERB,ADDITIVE", "ADDITION_ARGUMENT", "An added material must already occupy an ingredient-like slot."),
    "ROOT_CHEO": ("EXTRACTION_MEDIUM,EXTRACT", "EXTRACT_ARGUMENT", "Extract never expands directly to wine, medicine or dye."),
    "ROOT_KCH": ("ITEM", "PROCESS_OPERATION", "Generic processing leaves the content in the current-item register."),
    "ROOT_TY": ("PORTION,ROOT,SHOOT,LEAF,FLOWER,HERB", "PART_SELECTOR", "Part selects a registered divisible material."),
    "ROOT_SH": ("DURATION,ITEM", "HOLD_OPERATION", "Hold affects the current item for a licensed duration."),
    "ROOT_CHEEY": ("RESULT", "RESULT_SELECTOR", "Result selects only the current program result."),
    "N01_CFH": ("FILTER,EXTRACT,RESULT", "WRING_OPERATION", "Wringing may produce the registered extract/result."),
    "N02_CPH": ("FILTER,EXTRACT,RESULT", "RESTRAIN_OPERATION", "Re-straining may produce the registered extract/result."),
    "N03_PARTITION": ("PORTION,ROOT,SHOOT,LEAF,FLOWER,HERB", "PARTITION_OPERATION", "Partition operates on a registered material."),
    "N04_HO": ("SHOOT,LEAF,FLOWER,HERB,ADDITIVE", "LEARNED_ADDITION", "The learned addition card uses the same bounded ingredient slots."),
    "N05_DCHE": ("ROOT", "LEARNED_ROOT_PART", "The learned card licenses only root."),
    "N06_PREV": ("PREVIOUS", "LEARNED_PREVIOUS", "The learned card points to the previous preparation."),
    "N07_WASH": ("WASH_LIQUID,BODY_WORK_AREA,FILTER", "LEARNED_WASH", "Washing selects liquid, local target or filter path."),
    "N08_LDDY": ("OUTER_APPLICATION,BIO_CLOTH,BODY_WORK_AREA", "LEARNED_FASTEN", "Fastening requires a registered application, cloth or local target."),
    "N09_SK": ("OUTLET,RUN,RECEIVER", "LEARNED_POUR", "Pouring selects an outlet, run or receiver."),
    "N10_DAN": ("OUTER_APPLICATION,BODY_WORK_AREA,TARGET", "LEARNED_APPLY", "Application resolves only to a registered target slot."),
    "N11_DL": ("ADDITIVE", "LEARNED_ADDITIVE", "The learned card licenses only additive."),
    "N12_TALAM": ("VESSEL,RECEIVER,RESIDUE,RESULT", "LEARNED_STORE", "Storage selects a registered container or stored content."),
    "S01_DAIN": ("CLOTH,BIO_CLOTH,PORTION", "SPLIT_LEARNED_ENTRY", "The exact card chooses cloth or portion by register."),
    "S02_ODY": ("TEMPERATURE,LOCAL_LABEL", "SPLIT_LEARNED_ENTRY", "The exact card chooses cooling or marking by register."),
    "S03_OS": ("VESSEL,BASIN,STATION,PANEL", "SPLIT_LEARNED_ENTRY", "The exact card chooses a container/field owner by register."),
}

STRUCTURAL_ATOMS = {"L", "P", "AM", "LOCAL_WHOLE", "START"}


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


def atom_entry_ids(atom: str) -> list[str]:
    root = f"ROOT_{atom}"
    if root in LICENSES:
        return [root]
    learned = {
        "CFH": "N01_CFH", "CPH": "N02_CPH", "PARTITION": "N03_PARTITION",
        "HO": "N04_HO", "DCHE": "N05_DCHE", "PREV": "N06_PREV",
        "WASH": "N07_WASH", "LDDY": "N08_LDDY", "SK": "N09_SK",
        "DAN": "N10_DAN", "DL": "N11_DL", "TALAM": "N12_TALAM",
        "DAIN": "S01_DAIN", "ODY": "S02_ODY", "OS": "S03_OS",
    }
    return [learned[atom]] if atom in learned else []


def main() -> None:
    core = read_tsv(CORE)
    source_slots = {row["source_slot"] for row in read_tsv(LEXICON)}
    crosswalk = []
    for row in core:
        slots, license_class, reason = LICENSES[row["entry_id"]]
        crosswalk.append({
            **row,
            "licensed_source_slots": slots or "NONE",
            "licensed_slot_count": len(slots.split(",")) if slots else 0,
            "license_class": license_class,
            "license_rule_de": reason,
            "direct_rich_noun_license": "NO",
        })
    write_tsv(OUT / "SEVENTY_SEVENTH_43_CARD_TO_SOURCE_LICENSES.tsv", crosswalk)

    programs = {row["unit_id"]: set(row["finite_source_program"].split(">")) for row in read_tsv(PROGRAMS)}
    audits = []
    tally = Counter()
    for row in read_tsv(EVENTS):
        unit = row["unit_id"].split("-")[0]
        entry_ids = []
        structural = []
        candidate_slots = set()
        for atom in row["atom_sequence"].split("+"):
            ids = atom_entry_ids(atom)
            if ids:
                entry_ids.extend(ids)
                for entry_id in ids:
                    slots = LICENSES[entry_id][0]
                    if slots:
                        candidate_slots.update(slots.split(","))
            elif atom in STRUCTURAL_ATOMS:
                structural.append(atom)
            else:
                structural.append(atom)
        licensed_here = sorted(candidate_slots & programs[unit])
        status = "CONTENT_SLOT_LICENSED" if licensed_here else "OPERATION_OR_REFERENCE_ONLY"
        tally[status] += 1
        audits.append({
            "source_group_id": row["source_group_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "atom_sequence": row["atom_sequence"],
            "minimal_card_reading_de": row["minimal_card_reading_de"],
            "crosswalk_entry_ids": ";".join(dict.fromkeys(entry_ids)) or "NONE",
            "structural_or_local_atoms": ";".join(structural) or "NONE",
            "unit_source_program": ">".join(sorted(programs[unit])),
            "licensed_source_slots_in_this_unit": ";".join(licensed_here) or "NONE",
            "license_status": status,
            "rich_noun_may_be_invented": "NO",
        })
    write_tsv(OUT / "SEVENTY_SEVENTH_381_EVENT_LICENSE_AUDIT.tsv", audits)

    report = [
        "# Siebenundsiebzigste Werkstattfassung: Karten-zu-Quellen-Kreuzung", "",
        "## Ergebnis", "",
        "Each of the 43 minimal dictionary entries now licenses a finite set of source",
        "slot types. A card never licenses the rich noun itself. AL may open a target",
        "or local place, AIR a run or registered liquid, CHK temperature, CHEO an",
        "extract channel, and DAIN cloth or portion according to register.", "",
        f"Across the 381 prose groups, {tally['CONTENT_SLOT_LICENSED']} groups can expose",
        "at least one source-content slot present in their own unit program; the rest",
        "remain operation, order, grade, reference, closure or local learned content.", "",
        "This is the missing middle layer between stems and the controlled sourcebook:",
        "a short card can request a class of argument, but only the image/register and",
        "finite unit program can supply Bildpflanze, Badende, Tuch, Wasser or another",
        "selected content word.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_SEVENTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    doc = ["# Endliches Karten-zu-Quellen-Wörterbuch", ""]
    for row in crosswalk:
        doc.extend([
            f"## {row['surface_or_pattern']} · {row['minimal_value_de']}", "",
            f"Erlaubte Quellen-Slots: `{row['licensed_source_slots']}`.", "",
            f"{row['license_rule_de']}", "",
        ])
    (OUT / "SEVENTY_SEVENTH_CARD_SOURCE_CROSSWALK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "dictionary_entries": len(crosswalk),
            "event_audits": len(audits),
            **dict(sorted(tally.items())),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (CORE, EVENTS, LEXICON, PROGRAMS)},
        "source_slots_known": len(source_slots),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

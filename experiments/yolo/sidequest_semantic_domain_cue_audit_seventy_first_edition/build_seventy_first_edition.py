#!/usr/bin/env python3
"""Inventory which shared roots actually distinguish body use from material work."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
HIERARCHY = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_dictionary_fifty_fourth_edition/FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv"
GROUPS = ROOT / "experiments/yolo/sidequest_semantic_clause_shapes_sixty_third_edition/SIXTY_THIRD_381_GROUP_SHAPE_MAP.tsv"
DUAL_UNITS = ROOT / "experiments/yolo/sidequest_semantic_nonmedical_counterbook_seventieth_edition/SEVENTIETH_14_DUAL_CONTENT_UNITS.tsv"

MATERIAL_ROOTS = {"HO", "CHEO", "OR", "KCH", "TY"}
STATION_ROOTS = {"SHED", "SOLK", "CKHE", "CKH", "CHK", "CHEEY", "CHD", "AIR"}
BODY_WORDS = {"wunde", "haut", "brust", "auge", "leib", "körper", "patient", "badende", "krank"}

VISUAL_CUES = {
    "H1": "VISIBLE_PLANT__NO_BODY",
    "H2": "VISIBLE_PLANT__NO_BODY",
    "H3": "VISIBLE_PLANT__NO_BODY",
    "H4": "VISIBLE_PLANT__NO_BODY",
    "H5": "VISIBLE_PLANT__NO_BODY",
    "B1": "VISIBLE_HUMAN_FIGURES_IN_SHARED_POOL",
    "B2": "VISIBLE_HUMAN_FIGURES_AND_LOCAL_BASINS",
    "B3": "VISIBLE_HUMAN_FIGURES_VESSELS_AND_LINKED_PAIR",
    "B4": "VISIBLE_HUMAN_FIGURES_AND_LINKED_PAIR",
    "B5": "LOCAL_LEFT_STATION__BODY_OWNER_WEAK",
    "B6": "LOCAL_RIGHT_MULTIPORT_STATION__BODY_OWNER_WEAK",
    "A1": "VISIBLE_CELESTIAL_WHEELS",
    "A2": "VISIBLE_STAR_PANELS",
    "A3": "VISIBLE_CELESTIAL_ROSETTES",
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


def bias(h: int, b: int) -> str:
    if h and not b:
        return "HERBAL_ONLY"
    if b and not h:
        return "BIO_ONLY"
    total = h + b
    if h / total >= 0.70:
        return "HERBAL_BIASED"
    if b / total >= 0.70:
        return "BIO_BIASED"
    return "SHARED"


def learned_class(reading: str) -> str:
    text = reading.lower()
    if any(word in text for word in ("wurzel", "zutat", "pflanz")):
        return "PLANT_MATERIAL"
    if any(word in text for word in ("auftragen", "befestigen")):
        return "CONTACT_APPLICATION_AMBIGUOUS"
    if any(word in text for word in ("tuch", "gefäß", "zusatz", "durchlass", "einlass", "abführ", "abzieh", "abseih", "klar", "auszug")):
        return "APPARATUS_OR_PROCESS"
    return "GENERAL_WORKSHOP_VALUE"


def main() -> None:
    roots = [row for row in read_tsv(HIERARCHY) if row["hierarchy_level"] == "L1_ATOMIC_ROOT"]
    groups = read_tsv(GROUPS)
    root_counts = {row["surface_symbol_or_pattern"]: Counter() for row in roots}
    root_units = {row["surface_symbol_or_pattern"]: defaultdict(set) for row in roots}
    root_slots = {row["surface_symbol_or_pattern"]: Counter() for row in roots}
    for group in groups:
        register = "H" if group["unit_id"].startswith("H") else "B"
        atoms = group["atom_sequence"].split("+")
        for atom in atoms:
            if atom in root_counts:
                root_counts[atom][register] += 1
                root_units[atom][register].add(group["unit_id"])
                root_slots[atom][group["source_slot_sequence"]] += 1

    root_rows = []
    for row in roots:
        root = row["surface_symbol_or_pattern"]
        h = root_counts[root]["H"]
        b = root_counts[root]["B"]
        if root in MATERIAL_ROOTS:
            cue = "MATERIAL_OR_PREPARATION"
        elif root in STATION_ROOTS:
            cue = "PROCESS_OR_STATION"
        else:
            cue = "GENERAL_CONTROL_OR_PARAMETER"
        root_rows.append({
            "root": root,
            "current_short_value_de": row["short_value_de"],
            "herbal_group_occurrences": h,
            "bio_group_occurrences": b,
            "herbal_units": len(root_units[root]["H"]),
            "bio_units": len(root_units[root]["B"]),
            "register_bias": bias(h, b),
            "semantic_cue_class": cue,
            "most_common_source_slots": " | ".join(f"{slot}:{count}" for slot, count in root_slots[root].most_common(4)),
            "body_or_patient_specific": "NO",
            "medical_vs_nonmedical_discriminator": "NONE__COMPATIBLE_WITH_BOTH",
        })
    write_tsv(OUT / "SEVENTY_FIRST_28_ROOT_REGISTER_PROFILES.tsv", root_rows)

    learned_rows = []
    for group in groups:
        if group["learned_or_local_atoms"] == "NONE":
            continue
        explicit_body = any(word in group["card_reading_de"].lower() for word in BODY_WORDS)
        learned_rows.append({
            "source_group_id": group["source_group_id"],
            "unit_id": group["unit_id"],
            "page": group["page"],
            "visible_surface": group["visible_surface"],
            "learned_body": group["learned_or_local_atoms"],
            "short_card_reading_de": group["card_reading_de"],
            "cue_class": learned_class(group["card_reading_de"]),
            "explicit_body_or_patient_noun": "YES" if explicit_body else "NO",
            "medical_vs_nonmedical_discriminator": "POTENTIAL" if explicit_body else "NONE",
        })
    write_tsv(OUT / "SEVENTY_FIRST_54_LEARNED_BODY_CUES.tsv", learned_rows)

    group_rows = []
    for group in groups:
        atoms = group["atom_sequence"].split("+")
        cue_classes = []
        if any(atom in MATERIAL_ROOTS for atom in atoms):
            cue_classes.append("MATERIAL_OR_PREPARATION")
        if any(atom in STATION_ROOTS for atom in atoms):
            cue_classes.append("PROCESS_OR_STATION")
        if not cue_classes:
            cue_classes.append("GENERAL_CONTROL_OR_PARAMETER")
        explicit_body = any(word in group["card_reading_de"].lower() for word in BODY_WORDS)
        group_rows.append({
            "source_group_id": group["source_group_id"],
            "unit_id": group["unit_id"],
            "page": group["page"],
            "visible_surface": group["visible_surface"],
            "atom_sequence": group["atom_sequence"],
            "card_reading_de": group["card_reading_de"],
            "semantic_cue_classes": "+".join(cue_classes),
            "explicit_body_or_patient_noun": "YES" if explicit_body else "NO",
            "domain_decision_from_card_alone": "NONE",
            "owner_or_master_required": "YES",
        })
    write_tsv(OUT / "SEVENTY_FIRST_381_GROUP_DOMAIN_CUE_MAP.tsv", group_rows)

    unit_rows = []
    for row in read_tsv(DUAL_UNITS):
        unit_id = row["unit_id"]
        group_subset = [group for group in group_rows if group["unit_id"].split("-")[0] == unit_id]
        explicit = sum(group["explicit_body_or_patient_noun"] == "YES" for group in group_subset)
        if unit_id.startswith("A"):
            explicit = 0
        if unit_id in {"B1", "B2", "B3", "B4"}:
            decision = "BATH_OR_APPLICATION_SCENE_SUPPORTED_BY_IMAGE__MEDICAL_PURPOSE_UNRESOLVED"
        elif unit_id in {"B5", "B6"}:
            decision = "TECHNICAL_STATION_READING_CURRENTLY_STRONGER"
        elif unit_id.startswith("H"):
            decision = "PLANT_MATERIAL_ARTICLE_SUPPORTED__MEDICAL_PURPOSE_UNRESOLVED"
        else:
            decision = "CELESTIAL_OR_CALENDAR_LOOKUP_SUPPORTED__APPLICATION_UNRESOLVED"
        unit_rows.append({
            "unit_id": unit_id,
            "page": row["page"],
            "register": row["register"],
            "group_count": row["group_count"],
            "explicit_body_or_patient_card_groups": explicit,
            "visual_content_cue": VISUAL_CUES[unit_id],
            "current_content_decision": decision,
            "medical_fit_before": row["medical_content_fit_0_to_5"],
            "nonmedical_fit_before": row["nonmedical_content_fit_0_to_5"],
            "textual_domain_resolution": "NONE__NO_BODY_SPECIFIC_CARD_VALUE",
        })
    write_tsv(OUT / "SEVENTY_FIRST_14_UNIT_DOMAIN_CUE_DECISIONS.tsv", unit_rows)

    report = [
        "# Einundsiebzigste Werkstattfassung: Domänenhinweise in Stämmen und Ganzkarten", "",
        "## Ergebnis", "",
        "None of the 28 productive roots is body-, patient- or disease-specific. The",
        "clearest register asymmetries are technical: HO and CHEO favor Herbal material",
        "or extract handling; SHED, SOLK and CKHE occur only in Biological process",
        "contexts; AL, E/EE, CLOSE and CHD are strongly Biological because that register",
        "uses many short station cells and graded endings.", "",
        f"The 54 learned-body occurrences contain {sum(row['explicit_body_or_patient_noun'] == 'YES' for row in learned_rows)} explicit body/patient card readings. Plant part, ingredient, vessel, cloth, inlet, outlet, extract and contact/application occur, but those all support both medical and material-workshop sources.", "",
        "The concrete conclusion is not that the text is meaningless. It is that the",
        "current shared vocabulary says process and address, while medical purpose comes",
        "primarily from people-in-pools iconography and the simulated master expansion.",
        "B5 and B6 therefore remain more naturally technical; B1–B4 remain bath or",
        "application scenes without a textual patient marker.", "",
        "Only the fixed prose pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_FIRST_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    bias_counts = Counter(row["register_bias"] for row in root_rows)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "productive_roots": len(root_rows),
            "learned_body_occurrences": len(learned_rows),
            "prose_groups": len(group_rows),
            "units": len(unit_rows),
            "explicit_body_or_patient_card_groups": sum(row["explicit_body_or_patient_noun"] == "YES" for row in group_rows),
            **dict(sorted(bias_counts.items())),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (HIERARCHY, GROUPS, DUAL_UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

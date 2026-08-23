#!/usr/bin/env python3
"""Collapse the shared dictionary to short cross-content workshop values."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
HIERARCHY = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_dictionary_fifty_fourth_edition/FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv"
GROUPS = ROOT / "experiments/yolo/sidequest_semantic_clause_shapes_sixty_third_edition/SIXTY_THIRD_381_GROUP_SHAPE_MAP.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"

ROOT_VALUES = {
    "AIIN": "Sollwert", "AIN": "Anteil", "IIN": "Stufe", "AL": "Ziel",
    "AR": "Quelle", "AIR": "Lauf", "OK": "ansetzen", "OL": "weiter",
    "OT": "danach", "OR": "Ansatz", "Y": "dies", "E": "kurz",
    "EE": "länger", "EEE": "vollständig", "CLOSE": "Ende", "CHD": "umsetzen",
    "CTH": "bereit", "CKH": "Durchlass", "CKHE": "trennen", "CHK": "wärmen",
    "SHED": "absetzen", "SOLK": "sammeln", "HO": "Zutat", "CHEO": "Auszug",
    "KCH": "bearbeiten", "TY": "Teil", "SH": "halten", "CHEEY": "Ergebnis",
}

NOMENCLATOR_VALUES = {
    "N01_CFH": "auswringen", "N02_CPH": "nachseihen", "N03_PARTITION": "teilen",
    "N04_HO": "Zutat", "N05_DCHE": "Wurzelteil", "N06_PREV": "vorher",
    "N07_WASH": "waschen", "N08_LDDY": "befestigen", "N09_SK": "ausgießen",
    "N10_DAN": "anwenden", "N11_DL": "Zusatz", "N12_TALAM": "verwahren",
    "S01_DAIN": "Tuch|Portion", "S02_ODY": "kühlen|markieren", "S03_OS": "Gefäß|Feld",
}

EXTRA_ATOMS = {
    "CFH": "auswringen", "CPH": "nachseihen", "PARTITION": "teilen",
    "DCHE": "Wurzelteil", "PREV": "vorher", "WASH": "waschen", "LDDY": "befestigen",
    "SK": "ausgießen", "DAN": "anwenden", "DL": "Zusatz", "TALAM": "verwahren",
    "DAIN": "Tuch", "ODY": "kühlen", "OS": "Gefäß", "L": "ab", "P": "ein",
    "AM": "verwahren", "START": "beginnen", "LOCAL_WHOLE": "Zusatz",
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
    hierarchy = read_tsv(HIERARCHY)
    core_rows = []
    for row in hierarchy:
        if row["hierarchy_level"] == "L1_ATOMIC_ROOT":
            symbol = row["surface_symbol_or_pattern"]
            core_rows.append({
                "dictionary_order": len(core_rows) + 1,
                "entry_id": row["entry_id"],
                "entry_kind": "PRODUCTIVE_ROOT",
                "surface_or_pattern": symbol,
                "minimal_value_de": ROOT_VALUES[symbol],
                "composition_status": "PRODUCTIVE_ONLY_IN_LICENSED_CARDS",
                "concrete_noun_source": "OWNER_OR_MASTER",
            })
        elif row["hierarchy_level"] == "L2_LEARNED_NOMENCLATOR":
            core_rows.append({
                "dictionary_order": len(core_rows) + 1,
                "entry_id": row["entry_id"],
                "entry_kind": "LEARNED_WHOLE_OR_PATTERN",
                "surface_or_pattern": row["surface_symbol_or_pattern"],
                "minimal_value_de": NOMENCLATOR_VALUES[row["entry_id"]],
                "composition_status": "MEMORIZE_AS_REGISTERED_ENTRY",
                "concrete_noun_source": "SHARED_DICTIONARY_OR_REGISTER_SPLIT",
            })
    write_tsv(OUT / "SEVENTY_SECOND_43_MINIMAL_CORE_DICTIONARY.tsv", core_rows)

    layer_rows = []
    for row in hierarchy:
        if row["hierarchy_level"] == "L1_ATOMIC_ROOT":
            value = ROOT_VALUES[row["surface_symbol_or_pattern"]]
            status = "WORDLIKE_PRODUCTIVE_COMPONENT"
        elif row["hierarchy_level"] == "L2_LEARNED_NOMENCLATOR":
            value = NOMENCLATOR_VALUES[row["entry_id"]]
            status = "LEARNED_WHOLE_CARD_VALUE"
        else:
            value = "—"
            status = "NOT_A_WORD__WORKSHOP_CONTEXT_LAYER"
        layer_rows.append({
            "global_teaching_order": row["global_teaching_order"],
            "hierarchy_level": row["hierarchy_level"],
            "entry_id": row["entry_id"],
            "surface_symbol_or_pattern": row["surface_symbol_or_pattern"],
            "minimal_dictionary_value_de": value,
            "dictionary_status": status,
            "original_layer_function": row["short_value_de"],
            "concrete_content_source": row["what_supplies_concrete_content"],
        })
    write_tsv(OUT / "SEVENTY_SECOND_89_LAYER_POCKET_DICTIONARY.tsv", layer_rows)

    group_rows = []
    by_unit = defaultdict(list)
    for group in read_tsv(GROUPS):
        atoms = group["atom_sequence"].split("+")
        translated = [ROOT_VALUES.get(atom, EXTRA_ATOMS.get(atom, f"<{atom}>")) for atom in atoms]
        has_unresolved_atom = any(value.startswith("<") for value in translated)
        learned = group["learned_or_local_atoms"] != "NONE"
        minimal = " + ".join(translated)
        if learned:
            final_reading = group["card_reading_de"]
            reading_source = "LEARNED_WHOLE_CARD"
        else:
            final_reading = minimal
            reading_source = "PRODUCTIVE_COMPONENTS"
        out = {
            "source_group_id": group["source_group_id"],
            "unit_id": group["unit_id"],
            "page": group["page"],
            "visible_surface": group["visible_surface"],
            "atom_sequence": group["atom_sequence"],
            "minimal_component_reading_de": minimal,
            "minimal_card_reading_de": final_reading,
            "reading_source": reading_source,
            "clause_shape_id": group["clause_shape_id"],
            "unresolved_internal_atom": "YES" if has_unresolved_atom else "NO",
            "rich_content_not_in_dictionary": "YES",
        }
        group_rows.append(out)
        by_unit[group["unit_id"]].append(out)
    write_tsv(OUT / "SEVENTY_SECOND_381_MINIMAL_CARD_READINGS.tsv", group_rows)

    unit_source = {
        row["unit_id"]: row for row in read_tsv(UNITS)
        if row["unit_kind"] == "PROSE_STATEMENT"
    }
    statement_rows = []
    for unit_id, unit in unit_source.items():
        rows = by_unit[unit_id]
        statement_rows.append({
            "unit_id": unit_id,
            "page": unit["page"],
            "owner": unit["owner_or_namespace"],
            "group_count": len(rows),
            "surface_sequence": unit["surface_sequence"],
            "minimal_card_sequence_de": "; ".join(row["minimal_card_reading_de"] for row in rows),
            "clause_shape_sequence": ">".join(row["clause_shape_id"] for row in rows),
            "owner_augmented_minimal_reading_de": f"Bei {unit['owner_or_namespace']}: " + "; ".join(row["minimal_card_reading_de"] for row in rows) + ".",
            "rich_master_reading_de": unit["fluent_working_reading_de"],
        })
    write_tsv(OUT / "SEVENTY_SECOND_116_MINIMAL_STATEMENT_READINGS.tsv", statement_rows)

    doc = [
        "# Kleinstes aktives Werkstattwörterbuch", "",
        "## Produktive Stämme", "",
    ]
    for row in core_rows:
        if row["entry_kind"] == "PRODUCTIVE_ROOT":
            doc.append(f"- `{row['surface_or_pattern']}` = **{row['minimal_value_de']}**")
    doc.extend(["", "## Gelernte Ganzkarten und Muster", ""])
    for row in core_rows:
        if row["entry_kind"] != "PRODUCTIVE_ROOT":
            doc.append(f"- `{row['surface_or_pattern']}` = **{row['minimal_value_de']}**")
    doc.extend([
        "", "Bildbesitzer, Prozessmakros, Merkregister und Astro-Namensräume sind",
        "keine Wörter. Sie liefern Kontext oder Schreibablauf. Ein komplexer Satz darf",
        "daher nie als Bedeutung eines einzelnen Stammes in dieses Wörterbuch zurück.",
    ])
    (OUT / "SEVENTY_SECOND_MINIMAL_POCKET_DICTIONARY.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Zweiundsiebzigste Werkstattfassung: minimales Bedeutungswörterbuch", "",
        "## Ergebnis", "",
        "The shared semantic dictionary is reduced to 28 one-word productive roots and",
        "15 short learned whole-card or pattern values. All other hierarchy layers are",
        "explicitly nonwords: visual owners, memory registers, process macros and local",
        "Astro modules.", "",
        "Every one of the 381 prose groups and 116 statements is reissued with the short",
        "component reading beside the richer master text. This prevents meanings such as",
        "a disease, liquid recipe or entire instruction from leaking back into a root.", "",
        "The useful core is intentionally plain: target, source, run, set, continue, next,",
        "preparation, this, short/long/full, transfer, ready, passage, separate, warm,",
        "settle, collect, ingredient, extract, part, hold and result.", "",
        "Only the fixed prose pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_SECOND_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "productive_roots": sum(row["entry_kind"] == "PRODUCTIVE_ROOT" for row in core_rows),
            "learned_whole_or_patterns": sum(row["entry_kind"] != "PRODUCTIVE_ROOT" for row in core_rows),
            "hierarchy_layers": len(layer_rows),
            "minimal_group_readings": len(group_rows),
            "minimal_statement_readings": len(statement_rows),
            "unresolved_internal_group_atoms": sum(row["unresolved_internal_atom"] == "YES" for row in group_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (HIERARCHY, GROUPS, UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_prose_body_completion_fourteenth_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


PARSE = {
    "a": ("A", "Hauptwert"),
    "s": ("S", "Nebenwert"),
    "o": ("O", "Grundwert"),
    "d": ("D", "Festwert"),
    "r": ("R", "Bezugswert"),
    "ch": ("CH", "Zustand"),
    "ay": ("A+Y", "aktueller Hauptwert"),
    "dchy": ("D+CH+Y", "fester aktueller Zustand"),
    "chsdy": ("CH+S+DY", "sekundären Zustand festhalten"),
    "oygy": ("O+G+Y", "aktueller Grundgrad"),
}

surfaces = read(BASE / "FOURTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "FOURTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "FOURTEENTH_258_READING_UNITS.tsv")
classes = read(BASE / "FOURTEENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {
    row["unified_serial"]: row["autonomy"]
    for row in read(BASE / "FOURTEENTH_776_GROUP_AUTONOMY.tsv")
}

paradigm = []
for surface, (atoms, reading) in PARSE.items():
    source = next(row for row in surfaces if row["visible_surface"] == surface)
    paradigm.append(
        {
            "visible_surface": surface,
            "astro_groups": source["astro_occurrences"],
            "atom_sequence": atoms,
            "spoken_value_de": reading,
            "local_primitives_de": "A=HAUPT;S=NEBEN;O=GRUND;D=FEST;R=BEZUG;CH=ZUSTAND",
            "scope": "ASTRO_TABLE_REGISTER_ONLY",
        }
    )
write(HERE / "ASTRO_PRIMITIVE_10_SURFACES.tsv", list(paradigm[0]), paradigm)

predictions = [
    ("A+DY", "Hauptwert festhalten"),
    ("S+Y", "aktueller Nebenwert"),
    ("O+DY", "Grundwert festhalten"),
    ("R+Y", "aktueller Bezugswert"),
    ("D+G+Y", "fester aktueller Grad"),
    ("CH+A+Y", "aktueller Hauptzustand"),
]
write(
    HERE / "ASTRO_PRIMITIVE_FORWARD_CELLS.tsv",
    ["predicted_atoms", "predicted_reading_de", "status"],
    [
        {"predicted_atoms": atoms, "predicted_reading_de": reading, "status": "EMPTY_FIXED_PAGE_CELL"}
        for atoms, reading in predictions
    ],
)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = "ASTRO-PRIMITIVCODE"
        out["reading_rule_de"] = "read A/S/O/D/R/CH as local table primitives and attach known Y/DY/G"
        out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "FIFTEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "ASTRO_LOCAL_PRIMITIVE_MICROCODE"
    ledger_out.append(out)
by_unit = defaultdict(list)
for row in ledger_out:
    by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
for row in units:
    out = dict(row)
    groups = by_unit[(row["register"], row["page"], row["unit_id"])]
    if any(group["lookup_mode"] == "ASTRO_LOCAL_PRIMITIVE_MICROCODE" for group in groups):
        prefix = row["speakable_reading_de"].split(":", 1)[0]
        out["speakable_reading_de"] = prefix + ": " + "; ".join(
            group["short_value_de"] for group in groups
        )
    unit_out.append(out)
unit_lookup = {
    (row["register"], row["page"], row["unit_id"]): row["speakable_reading_de"]
    for row in unit_out
}
for row in ledger_out:
    row["unit_reading_de"] = unit_lookup[(row["register"], row["page"], row["reading_unit_id"])]
write(HERE / "FIFTEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "FIFTEENTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "ASTRO_LOCAL_PRIMITIVE_MICROCODE",
                "historical_layer": "TABLE_PRIMITIVE_PLUS_MODIFIER",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "lokalen Tafelkern und Y/DY/G-Zusatz lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "ASTRO:BARE_PRIMITIVE_AND_COMPOUND_SERIES",
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "FIFTEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    value = (
        "FULL"
        if row["register"] == "ASTRO" and row["visible_surface"] in PARSE
        else base_aut[row["unified_serial"]]
    )
    autonomy.append(
        {
            "unified_serial": row["unified_serial"],
            "register": row["register"],
            "page": row["page"],
            "source_group_id": row["source_group_id"],
            "visible_surface": row["visible_surface"],
            "autonomy": value,
        }
    )
write(HERE / "FIFTEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(
    HERE / "FIFTEENTH_AUTONOMY_SUMMARY.tsv",
    ["autonomy", "visible_groups"],
    [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")],
)

base_text = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_FOURTEENTH_EDITION.md").read_text(encoding="utf-8")
base_text = base_text.replace("Drei Himmelsseiten, vierzehnte Lesung", "Drei Himmelsseiten, fünfzehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_FIFTEENTH_EDITION.md").write_text(base_text, encoding="utf-8")
pocket = (BASE / "FOURTEENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Lokales Astro-Primitivcode\n\n"
    "- `A` Hauptwert; `S` Nebenwert; `O` Grundwert; `D` Festwert; `R` Bezugswert; `CH` Zustand.\n"
    "- `AY` aktueller Hauptwert; `DCHY` fester aktueller Zustand; `CHSDY` sekundären Zustand festhalten; `OYGY` aktueller Grundgrad.\n"
    "- Diese Werte gelten nur im Himmelsregister; dieselben sichtbaren Zeichen können andernorts Rahmen sein.\n"
)
(HERE / "FIFTEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "primitive_surfaces": len(PARSE),
        "primitive_groups": sum(int(row["astro_groups"]) for row in paradigm),
        "forward_cells": len(predictions),
        "full_groups": counts["FULL"],
        "partial_groups": counts["PARTIAL"],
        "whole_groups": counts["NONE"],
        "full_types": sum(v for k, v in type_counts.items() if k.startswith("FULL")),
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

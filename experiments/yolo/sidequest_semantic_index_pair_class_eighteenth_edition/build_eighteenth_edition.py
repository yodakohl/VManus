#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_phase_selection_seventeenth_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PARSE = {
    "doiir": ("D+O+IIR", "fester Grundindex", "IIR=INDEX"),
    "saiir": ("S+A+IIR", "Hauptindex des Nebenfelds", "IIR=INDEX"),
    "oparchy": ("OP+AR", "Quelle des Paarfelds", "OP=PAAR/GEGENFELD"),
    "opcheeol": ("OP+EE+OL", "Paarfeld länger fortsetzen", "OP=PAAR/GEGENFELD"),
    "opcholdy": ("OP+OL+DY", "Paarfeld fortsetzen und festhalten", "OP=PAAR/GEGENFELD"),
    "opodchol": ("OP+OD+OL", "markiertes Paarfeld fortsetzen", "OP=PAAR/GEGENFELD"),
    "qopchy": ("OP+CH+Y", "aktueller Zustand des Paarfelds", "OP=PAAR/GEGENFELD"),
    "qkoy": ("K+O+Y", "aktuelle Grundklasse", "K=KLASSE"),
    "chky": ("CH+K+Y", "aktuellen Klassenzustand setzen", "K=KLASSE"),
    "tochso": ("T+O+CH+S", "sekundärer Grundzustand der Phase", "KNOWN_PRIMITIVES"),
    "ofydy": ("O+Y+DY", "aktuellen Grundwert festhalten", "F=REGISTERED_FRAME"),
}

surfaces = read(BASE / "SEVENTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "SEVENTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "SEVENTEENTH_258_READING_UNITS.tsv")
classes = read(BASE / "SEVENTEENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {row["unified_serial"]: row["autonomy"] for row in read(BASE / "SEVENTEENTH_776_GROUP_AUTONOMY.tsv")}

paradigm = []
for surface, (atoms, reading, family) in PARSE.items():
    source = next(row for row in surfaces if row["visible_surface"] == surface)
    old = next(row for row in classes if row["visible_surface"] == surface)
    paradigm.append(
        {
            "visible_surface": surface,
            "astro_groups": source["astro_occurrences"],
            "previous_autonomy": old["composition_autonomy"],
            "family": family,
            "atom_sequence": atoms,
            "spoken_value_de": reading,
        }
    )
write(HERE / "INDEX_PAIR_CLASS_11_SURFACES.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading, family = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = family
        out["reading_rule_de"] = "read local IIR/OP/K or the listed known-primitive composition"
        out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "EIGHTEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in PARSE:
        atoms, reading, family = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "ASTRO_LOCAL_INDEX_PAIR_CLASS_MICROCODE"
    ledger_out.append(out)
by_unit = defaultdict(list)
for row in ledger_out:
    by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
for row in units:
    out = dict(row)
    groups = by_unit[(row["register"], row["page"], row["unit_id"])]
    if any(group["lookup_mode"] == "ASTRO_LOCAL_INDEX_PAIR_CLASS_MICROCODE" for group in groups):
        prefix = row["speakable_reading_de"].split(":", 1)[0]
        out["speakable_reading_de"] = prefix + ": " + "; ".join(group["short_value_de"] for group in groups)
    unit_out.append(out)
unit_lookup = {(row["register"], row["page"], row["unit_id"]): row["speakable_reading_de"] for row in unit_out}
for row in ledger_out:
    row["unit_reading_de"] = unit_lookup[(row["register"], row["page"], row["reading_unit_id"])]
write(HERE / "EIGHTEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "EIGHTEENTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading, family = PARSE[row["visible_surface"]]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "ASTRO_LOCAL_INDEX_PAIR_CLASS_MICROCODE",
                "historical_layer": "TABLE_PRIMITIVE_PLUS_MODIFIER",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "IIR/OP/K oder bekannte Primitivfolge lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "ASTRO:INDEX_PAIR_CLASS_SERIES",
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "EIGHTEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    value = "FULL" if row["register"] == "ASTRO" and row["visible_surface"] in PARSE else base_aut[row["unified_serial"]]
    autonomy.append({"unified_serial": row["unified_serial"], "register": row["register"], "page": row["page"], "source_group_id": row["source_group_id"], "visible_surface": row["visible_surface"], "autonomy": value})
write(HERE / "EIGHTEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(HERE / "EIGHTEENTH_AUTONOMY_SUMMARY.tsv", ["autonomy", "visible_groups"], [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")])

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_SEVENTEENTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, siebzehnte Lesung", "Drei Himmelsseiten, achtzehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_EIGHTEENTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "SEVENTEENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Index, Paarfeld und Klasse\n\n"
    "- `IIR` — **INDEX**; `OP` — **PAAR-/GEGENFELD**; `K` — **KLASSE**, nur im Astroregister.\n"
    "- `OFYDY` wird schlicht `O+Y+DY`: aktuellen Grundwert festhalten; die alte Lichtglosse entfällt.\n"
    "- `TOCHSO` ist eine Folge bekannter Primitiva für den sekundären Grundzustand einer Phase.\n"
)
(HERE / "EIGHTEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "revised_surfaces": len(PARSE),
        "newly_full_surfaces": sum(row["previous_autonomy"] == "NONE" for row in paradigm),
        "full_groups": counts["FULL"],
        "whole_groups": counts["NONE"],
        "full_types": sum(v for k, v in type_counts.items() if k.startswith("FULL")),
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

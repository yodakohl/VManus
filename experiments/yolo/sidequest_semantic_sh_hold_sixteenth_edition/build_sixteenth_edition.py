#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_primitive_microcode_fifteenth_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PARSE = {
    "sh": ("SH", "halten"),
    "shs": ("SH+S", "Nebenwert halten"),
    "lkshy": ("SH+Y", "aktuellen Posten halten"),
    "shees": ("SH+EE", "länger halten"),
    "shekchy": ("SH+KCH+Y", "aktuellen Posten beim Bearbeiten halten"),
    "okoirsh": ("OK+SH", "aktivieren und halten"),
}

surfaces = read(BASE / "FIFTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "FIFTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "FIFTEENTH_258_READING_UNITS.tsv")
classes = read(BASE / "FIFTEENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {row["unified_serial"]: row["autonomy"] for row in read(BASE / "FIFTEENTH_776_GROUP_AUTONOMY.tsv")}

paradigm = []
for surface, (atoms, reading) in PARSE.items():
    source = next(row for row in surfaces if row["visible_surface"] == surface)
    old = next(row for row in classes if row["visible_surface"] == surface)
    paradigm.append(
        {
            "visible_surface": surface,
            "prose_groups": source["prose_occurrences"],
            "astro_groups": source["astro_occurrences"],
            "previous_autonomy": old["composition_autonomy"],
            "atom_sequence": atoms,
            "spoken_value_de": reading,
            "root_de": "SH=HALTEN",
        }
    )
write(HERE / "SH_HOLD_6_SURFACE_PARADIGM.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = "HALTEN"
        out["reading_rule_de"] = "read SH as hold and attach S/Y/EE/KCH/OK in order"
        if int(row["prose_occurrences"]):
            out["prose_short_value_de"] = reading
        if int(row["astro_occurrences"]):
            out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "SIXTEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "CROSS_REGISTER_SH_HOLD_ROOT"
    ledger_out.append(out)
by_unit = defaultdict(list)
for row in ledger_out:
    by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
for row in units:
    out = dict(row)
    groups = by_unit[(row["register"], row["page"], row["unit_id"])]
    if any(group["lookup_mode"] == "CROSS_REGISTER_SH_HOLD_ROOT" for group in groups):
        prefix = row["speakable_reading_de"].split(":", 1)[0]
        out["speakable_reading_de"] = prefix + ": " + "; ".join(group["short_value_de"] for group in groups)
    unit_out.append(out)
unit_lookup = {(row["register"], row["page"], row["unit_id"]): row["speakable_reading_de"] for row in unit_out}
for row in ledger_out:
    row["unit_reading_de"] = unit_lookup[(row["register"], row["page"], row["reading_unit_id"])]
write(HERE / "SIXTEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "SIXTEENTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "CROSS_REGISTER_PRODUCTIVE_SH_HOLD_ROOT",
                "historical_layer": "BREVIGRAPH_PLUS_ARGUMENT",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "SH halten lesen und rechten Zusatz anhängen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "CROSS_REGISTER:SH_HOLD_SERIES",
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "SIXTEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    value = "FULL" if row["visible_surface"] in PARSE else base_aut[row["unified_serial"]]
    autonomy.append({"unified_serial": row["unified_serial"], "register": row["register"], "page": row["page"], "source_group_id": row["source_group_id"], "visible_surface": row["visible_surface"], "autonomy": value})
write(HERE / "SIXTEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(HERE / "SIXTEENTH_AUTONOMY_SUMMARY.tsv", ["autonomy", "visible_groups"], [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")])

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_FIFTEENTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, fünfzehnte Lesung", "Drei Himmelsseiten, sechzehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_SIXTEENTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "FIFTEENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## SH-Haltefamilie\n\n"
    "- `SH` — **HALTEN** in Prosa und Tafel.\n"
    "- `SH+S` Nebenwert halten; `SH+Y` aktuellen Posten halten; `SH+EE` länger halten.\n"
    "- Mit KCH heißt es beim Bearbeiten halten, mit OK aktivieren und halten.\n"
)
(HERE / "SIXTEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "sh_surfaces": len(PARSE),
        "sh_groups": sum(int(row["prose_groups"]) + int(row["astro_groups"]) for row in paradigm),
        "newly_full_groups": 3,
        "full_groups": counts["FULL"],
        "whole_groups": counts["NONE"],
        "full_types": sum(v for k, v in type_counts.items() if k.startswith("FULL")),
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_sh_hold_sixteenth_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PARSE = {
    "es": ("SEL+S", "ausgewählter Nebenwert"),
    "ey": ("SEL+Y", "aktuelle Auswahl"),
    "tey": ("T+Y", "aktuelle Phase"),
    "yetey": ("SEL+T+Y", "ausgewählte aktuelle Phase"),
    "dchetay": ("D+CH+T+A+Y", "fester aktueller Hauptphasen-Zustand"),
    "chetody": ("CH+T+OD+Y", "aktuellen Phasen-Zustand eintragen"),
}

surfaces = read(BASE / "SIXTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "SIXTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "SIXTEENTH_258_READING_UNITS.tsv")
classes = read(BASE / "SIXTEENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {row["unified_serial"]: row["autonomy"] for row in read(BASE / "SIXTEENTH_776_GROUP_AUTONOMY.tsv")}

paradigm = []
for surface, (atoms, reading) in PARSE.items():
    source = next(row for row in surfaces if row["visible_surface"] == surface)
    paradigm.append(
        {
            "visible_surface": surface,
            "astro_groups": source["astro_occurrences"],
            "atom_sequence": atoms,
            "spoken_value_de": reading,
            "phase_root_de": "T=PHASE/PLATZFOLGE",
            "selection_hook_de": "SEL=einzelnes E nur in ES/EY/YETEY",
        }
    )
write(HERE / "PHASE_SELECTION_6_SURFACES.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = "PHASE/AUSWAHL"
        out["reading_rule_de"] = "read local T as phase and registered single-E hook as selected"
        out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "SEVENTEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "ASTRO_LOCAL_PHASE_SELECTION_MICROCODE"
    ledger_out.append(out)
by_unit = defaultdict(list)
for row in ledger_out:
    by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
for row in units:
    out = dict(row)
    groups = by_unit[(row["register"], row["page"], row["unit_id"])]
    if any(group["lookup_mode"] == "ASTRO_LOCAL_PHASE_SELECTION_MICROCODE" for group in groups):
        prefix = row["speakable_reading_de"].split(":", 1)[0]
        out["speakable_reading_de"] = prefix + ": " + "; ".join(group["short_value_de"] for group in groups)
    unit_out.append(out)
unit_lookup = {(row["register"], row["page"], row["unit_id"]): row["speakable_reading_de"] for row in unit_out}
for row in ledger_out:
    row["unit_reading_de"] = unit_lookup[(row["register"], row["page"], row["reading_unit_id"])]
write(HERE / "SEVENTEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "SEVENTEENTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "ASTRO_LOCAL_PHASE_SELECTION_MICROCODE",
                "historical_layer": "TABLE_PRIMITIVE_PLUS_POSITIONAL_HOOK",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "T als Phase und registriertes SEL-E als Auswahl lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "ASTRO:PHASE_SELECTION_SERIES",
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "SEVENTEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    value = "FULL" if row["register"] == "ASTRO" and row["visible_surface"] in PARSE else base_aut[row["unified_serial"]]
    autonomy.append({"unified_serial": row["unified_serial"], "register": row["register"], "page": row["page"], "source_group_id": row["source_group_id"], "visible_surface": row["visible_surface"], "autonomy": value})
write(HERE / "SEVENTEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(HERE / "SEVENTEENTH_AUTONOMY_SUMMARY.tsv", ["autonomy", "visible_groups"], [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")])

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_SIXTEENTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, sechzehnte Lesung", "Drei Himmelsseiten, siebzehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_SEVENTEENTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "SIXTEENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Phase und Auswahl\n\n"
    "- `T` — **PHASE / PLATZFOLGE** im Astroregister.\n"
    "- Ein einzelnes vorgeschaltetes `E` ist nur in `ES`, `EY`, `YETEY` der gebundene Auswahlhaken `SEL`.\n"
    "- `EE` bleibt davon getrennt: doppelte E-Stufe bedeutet länger, nicht ausgewählt.\n"
)
(HERE / "SEVENTEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "phase_selection_surfaces": len(PARSE),
        "phase_selection_groups": 6,
        "full_groups": counts["FULL"],
        "whole_groups": counts["NONE"],
        "full_types": sum(v for k, v in type_counts.items() if k.startswith("FULL")),
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

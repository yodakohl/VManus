#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_cheey_readout_eighth_edition"


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
    "ydaiin": ("YD+AIIN", "Sollwert der aktiven Zeile"),
    "ydam": ("YD+AM", "Aspekt der aktiven Zeile"),
    "ydchos": ("YD+HO", "Eingangsposten der aktiven Zeile"),
    "ydoly": ("YD+OL", "aktive Zeile fortsetzen"),
}

surfaces = read(BASE / "EIGHTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "EIGHTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "EIGHTH_258_READING_UNITS.tsv")
classes = read(BASE / "EIGHTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {
    row["unified_serial"]: row["autonomy"]
    for row in read(BASE / "EIGHTH_776_GROUP_AUTONOMY.tsv")
}

paradigm = []
for surface, (atoms, reading) in PARSE.items():
    row = next(item for item in surfaces if item["visible_surface"] == surface)
    paradigm.append(
        {
            "visible_surface": surface,
            "astro_groups": row["astro_occurrences"],
            "owner_span": "f67r2 left local fields and left outer-ring text",
            "revised_atom_sequence": atoms,
            "local_root_de": "AKTIVE/NOTIERTE ZEILE",
            "spoken_value_de": reading,
            "apprentice_rule_de": "YD hält die gewählte Tabellenzeile aktiv; lies den rechten Kern darin",
        }
    )
write(HERE / "YD_4_SURFACE_PARADIGM.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = "AKTIVE/NOTIERTE ZEILE"
        out["reading_rule_de"] = (
            "lies YD als aktive Tabellenzeile und den folgenden bekannten Kern darin"
        )
        out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "NINTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
changed_groups = 0
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "ASTRO_LOCAL_YD_ACTIVE_ROW"
        changed_groups += 1
    ledger_out.append(out)

by_unit = defaultdict(list)
for row in ledger_out:
    by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
changed_units = 0
for row in units:
    out = dict(row)
    groups = by_unit[(row["register"], row["page"], row["unit_id"])]
    if any(group["lookup_mode"] == "ASTRO_LOCAL_YD_ACTIVE_ROW" for group in groups):
        prefix = row["speakable_reading_de"].split(":", 1)[0]
        out["speakable_reading_de"] = prefix + ": " + "; ".join(
            group["short_value_de"] for group in groups
        )
        changed_units += 1
    unit_out.append(out)
unit_lookup = {
    (row["register"], row["page"], row["unit_id"]): row["speakable_reading_de"]
    for row in unit_out
}
for row in ledger_out:
    row["unit_reading_de"] = unit_lookup[
        (row["register"], row["page"], row["reading_unit_id"])
    ]
write(HERE / "NINTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "NINTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["classification"] = "ASTRO_LOCAL_PRODUCTIVE_YD_ROW_ROOT"
        out["historical_layer"] = "LOCAL_TABLE_ROOT_PLUS_BREVIGRAPH"
        out["composition_autonomy"] = "FULL_WITH_OWNER"
        out["apprentice_action_de"] = "aktive YD-Zeile halten und rechten Kern lesen"
        out["memorized_body_or_residue"] = "NONE"
        out["classification_evidence"] = "ASTRO_LOCAL:YD_ACTIVE_ROW"
        out["short_spoken_value_de"] = reading
    class_out.append(out)
write(HERE / "NINTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

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
write(HERE / "NINTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
autonomy_counts = Counter(row["autonomy"] for row in autonomy)
write(
    HERE / "NINTH_AUTONOMY_SUMMARY.tsv",
    ["autonomy", "visible_groups"],
    [
        {"autonomy": value, "visible_groups": autonomy_counts[value]}
        for value in ("FULL", "PARTIAL", "NONE")
    ],
)

base_text = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_EIGHTH_EDITION.md").read_text(
    encoding="utf-8"
)
prose = base_text.split("## Teil II", 1)[0].rstrip()
edition = prose + "\n\n---\n\n## Teil II — Drei Himmelsseiten, neunte Lesung\n\n"
for page in ("f67r2", "f68r1", "f69v"):
    edition += f"### {page}\n\n"
    for row in unit_out:
        if row["register"] == "ASTRO" and row["page"] == page:
            edition += f"- `{row['unit_id']}` — {row['speakable_reading_de']}\n"
    edition += "\n"
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_NINTH_EDITION.md").write_text(
    edition.rstrip() + "\n", encoding="utf-8"
)

pocket = (BASE / "EIGHTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Aktive Tabellenzeile\n\n"
    "- `YD` — **AKTIVE / NOTIERTE ZEILE** im linken f67r2-Register.\n"
    "- `YD+AIIN` Sollwert der Zeile; `YD+AM` ihr Aspekt; `YD+HO` ihr Eingang; "
    "`YD+OL` die Zeile fortsetzen.\n"
    "- YD ist ein gelernter lokaler Körper, keine globale Zerlegung Y+D.\n"
)
(HERE / "NINTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "yd_surfaces": len(PARSE),
        "yd_groups": changed_groups,
        "changed_units": changed_units,
        "surfaces": len(surface_out),
        "groups": len(ledger_out),
        "units": len(unit_out),
        "full_groups": autonomy_counts["FULL"],
        "partial_groups": autonomy_counts["PARTIAL"],
        "whole_groups": autonomy_counts["NONE"],
        "full_types": sum(
            value for key, value in type_counts.items() if key.startswith("FULL")
        ),
        "partial_types": type_counts["PARTIAL"],
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))

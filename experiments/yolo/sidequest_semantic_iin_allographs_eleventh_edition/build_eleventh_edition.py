#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_ee_grade_tenth_edition"


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
    "choaiin": ("HO+AIIN", "Eingangsposten mit Sollwert"),
    "dadaiin": ("AIIN", "Sollwert"),
    "doiin": ("IIN", "Tabellenstufe"),
    "oiin": ("IIN", "Tabellenstufe"),
    "oiinar": ("IIN+AR", "Stufe mit Quellenbezug"),
    "okaiiin": ("OK+IIN", "Stufe aktivieren"),
    "qokoaiin": ("OK+AIIN", "Sollwert aktivieren"),
    "todaiin": ("AIIN", "Sollwert"),
}

surfaces = read(BASE / "TENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "TENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "TENTH_258_READING_UNITS.tsv")
classes = read(BASE / "TENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {
    row["unified_serial"]: row["autonomy"]
    for row in read(BASE / "TENTH_776_GROUP_AUTONOMY.tsv")
}

paradigm = []
for surface, (atoms, reading) in PARSE.items():
    source = next(row for row in surfaces if row["visible_surface"] == surface)
    old_class = next(
        row for row in classes if row["visible_surface"] == surface
    )["composition_autonomy"]
    paradigm.append(
        {
            "visible_surface": surface,
            "astro_groups": source["astro_occurrences"],
            "previous_autonomy": old_class,
            "revised_atom_sequence": atoms,
            "stem_value_de": "AIIN=SOLLWERT; IIN=STUFE",
            "spoken_value_de": reading,
            "frame_rule": "remaining leading material is a registered allograph frame, not a word",
        }
    )
write(HERE / "IIN_AIIN_8_ALLOGRAPHS.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = "SOLLWERT/STUFE"
        out["reading_rule_de"] = "ignore registered frame and read visible IIN/AIIN plus known core"
        out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "ELEVENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "ASTRO_REGISTERED_IIN_AIIN_ALLOGRAPH"
    ledger_out.append(out)

by_unit = defaultdict(list)
for row in ledger_out:
    by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
for row in units:
    out = dict(row)
    groups = by_unit[(row["register"], row["page"], row["unit_id"])]
    if any(group["lookup_mode"] == "ASTRO_REGISTERED_IIN_AIIN_ALLOGRAPH" for group in groups):
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
    row["unit_reading_de"] = unit_lookup[
        (row["register"], row["page"], row["reading_unit_id"])
    ]
write(HERE / "ELEVENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "ELEVENTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading = PARSE[row["visible_surface"]]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "REGISTERED_IIN_AIIN_ALLOGRAPH",
                "historical_layer": "BREVIGRAPH_WITH_SCRIBAL_FRAME",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "Schreibrahmen erkennen und IIN/AIIN lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "ASTRO:IIN_AIIN_FRAME_SERIES",
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "ELEVENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

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
write(HERE / "ELEVENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(
    HERE / "ELEVENTH_AUTONOMY_SUMMARY.tsv",
    ["autonomy", "visible_groups"],
    [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")],
)

base_text = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_TENTH_EDITION.md").read_text(encoding="utf-8")
prose = base_text.split("## Teil II", 1)[0].rstrip()
edition = prose + "\n\n---\n\n## Teil II — Drei Himmelsseiten, elfte Lesung\n\n"
for page in ("f67r2", "f68r1", "f69v"):
    edition += f"### {page}\n\n"
    for row in unit_out:
        if row["register"] == "ASTRO" and row["page"] == page:
            edition += f"- `{row['unit_id']}` — {row['speakable_reading_de']}\n"
    edition += "\n"
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_ELEVENTH_EDITION.md").write_text(
    edition.rstrip() + "\n", encoding="utf-8"
)

pocket = (BASE / "TENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Acht IIN/AIIN-Allographen\n\n"
    "- `doiin/oiin` — **STUFE**; `dadaiin/todaiin` — **SOLLWERT**.\n"
    "- `oiinar` — Stufe mit Quelle; `choaiin` — Eingang mit Sollwert.\n"
    "- `okaiiin/qokoaiin` — Stufe bzw. Sollwert aktivieren.\n"
)
(HERE / "ELEVENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "allographs": len(PARSE),
        "groups": len(ledger_out),
        "full_groups": counts["FULL"],
        "partial_groups": counts["PARTIAL"],
        "whole_groups": counts["NONE"],
        "full_types": sum(v for k, v in type_counts.items() if k.startswith("FULL")),
        "partial_types": type_counts["PARTIAL"],
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))

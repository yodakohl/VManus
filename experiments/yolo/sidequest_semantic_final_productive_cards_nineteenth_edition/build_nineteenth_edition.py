#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_index_pair_class_eighteenth_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PARSE = {
    "cho": ("HO", "Eingangsposten oder Zutat", "CROSS_REGISTER"),
    "sho": ("HO", "Zutat", "PROSE_ALLOGRAPH"),
    "ches": ("PARTITION", "teilen", "PROSE_TECHNICAL_BODY"),
    "dchol": ("PREV+OL", "vorigen Posten fortsetzen", "PROSE_ALLOGRAPH"),
    "schol": ("PREV+OL", "vorigen Posten fortsetzen", "PROSE_ALLOGRAPH"),
    "lsho": ("WASH+START", "Waschgang beginnen", "PROSE_TECHNICAL_BODY"),
    "ocphy": ("O+CPH_ASTRO+Y", "aktuelle Grundauswahl", "REGISTER_SPLIT_CPH"),
}

surfaces = read(BASE / "EIGHTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "EIGHTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "EIGHTEENTH_258_READING_UNITS.tsv")
classes = read(BASE / "EIGHTEENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {row["unified_serial"]: row["autonomy"] for row in read(BASE / "EIGHTEENTH_776_GROUP_AUTONOMY.tsv")}

paradigm = []
for surface, (atoms, reading, mode) in PARSE.items():
    source = next(row for row in surfaces if row["visible_surface"] == surface)
    paradigm.append(
        {
            "visible_surface": surface,
            "prose_groups": source["prose_occurrences"],
            "astro_groups": source["astro_occurrences"],
            "mode": mode,
            "atom_sequence": atoms,
            "spoken_value_de": reading,
        }
    )
write(HERE / "FINAL_PRODUCTIVE_7_SURFACES.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading, mode = PARSE[row["visible_surface"]]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = mode
        out["reading_rule_de"] = "read the listed learned body and its productive relation or argument"
        if int(row["prose_occurrences"]):
            out["prose_short_value_de"] = reading
        if int(row["astro_occurrences"]):
            out["astro_short_values_de"] = reading
    surface_out.append(out)
write(HERE / "NINETEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading, mode = PARSE[row["visible_surface"]]
        out["atom_sequence"] = atoms
        out["short_value_de"] = reading
        out["lookup_mode"] = "FINAL_PRODUCTIVE_BODY_OR_REGISTER_SPLIT"
    ledger_out.append(out)
write(HERE / "NINETEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "NINETEENTH_258_READING_UNITS.tsv", list(units[0]), units)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in PARSE:
        atoms, reading, mode = PARSE[row["visible_surface"]]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "FINAL_PRODUCTIVE_BODY_OR_REGISTER_SPLIT",
                "historical_layer": "TECHNICAL_BODY_PLUS_ARGUMENT",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "Fachkörper abrufen und bekannten Zusatz lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": mode,
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "NINETEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    value = "FULL" if row["visible_surface"] in PARSE else base_aut[row["unified_serial"]]
    autonomy.append({"unified_serial": row["unified_serial"], "register": row["register"], "page": row["page"], "source_group_id": row["source_group_id"], "visible_surface": row["visible_surface"], "autonomy": value})
write(HERE / "NINETEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(HERE / "NINETEENTH_AUTONOMY_SUMMARY.tsv", ["autonomy", "visible_groups"], [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")])

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_EIGHTEENTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, achtzehnte Lesung", "Drei Himmelsseiten, neunzehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_NINETEENTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "EIGHTEENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Letzte produktive Fachkarten\n\n"
    "- `CHO/SHO` — Eingangs-/Zutatenkarte; `CHES` — teilen; `DCHOL/SCHOL` — Voriges fortsetzen; `LSHO` — Waschgang beginnen.\n"
    "- `OCPHY` — aktuelle Grundauswahl; CPH ist hier ein Astro-Auswahlkörper, in Prosa weiterhin Nachseihen.\n"
    "- Danach bleiben nur DL und TALAM als ganze Prosa-Wörter sowie dain/ody/os als drei Prosa-Seiten der Registersplits.\n"
)
(HERE / "NINETEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "revised_surfaces": len(PARSE),
        "revised_groups": sum(int(row["prose_groups"]) + int(row["astro_groups"]) for row in paradigm),
        "full_groups": counts["FULL"],
        "whole_groups": counts["NONE"],
        "full_types": sum(v for k, v in type_counts.items() if k.startswith("FULL")),
        "whole_types": type_counts["NONE"],
        "split_types": type_counts["REGISTER_SPLIT"],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

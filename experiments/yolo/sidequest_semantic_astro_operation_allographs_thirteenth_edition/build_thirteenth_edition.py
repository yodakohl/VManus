#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_relational_allographs_twelfth_edition"


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


surfaces = read(BASE / "TWELFTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "TWELFTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "TWELFTH_258_READING_UNITS.tsv")
classes = read(BASE / "TWELFTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {
    row["unified_serial"]: row["autonomy"]
    for row in read(BASE / "TWELFTH_776_GROUP_AUTONOMY.tsv")
}

selected = [
    row
    for row in classes
    if row["register_status"] == "ASTRO_ONLY"
    and row["composition_autonomy"] == "PARTIAL"
]
TARGETS = {row["visible_surface"] for row in selected}

paradigm = []
for row in sorted(selected, key=lambda item: item["visible_surface"]):
    dictionary = next(
        item for item in surfaces if item["visible_surface"] == row["visible_surface"]
    )
    paradigm.append(
        {
            "visible_surface": row["visible_surface"],
            "astro_groups": dictionary["astro_occurrences"],
            "atom_sequence": row["common_atom_sequences"],
            "spoken_value_de": row["short_spoken_value_de"],
            "registered_shell_de": "lokaler Schreiberrahmen um bekannte Operations- oder Argumentkerne",
            "apprentice_rule_de": "Form im Register erkennen, Hülle abziehen, bekannte Kerne in Reihenfolge sprechen",
        }
    )
write(HERE / "ASTRO_OPERATIONAL_46_ALLOGRAPHS.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in TARGETS:
        out["common_nucleus_de"] = "REGISTRIERTE OPERATIONS-/ARGUMENTKARTE"
        out["reading_rule_de"] = "strip registered shell and read the known atom sequence"
    surface_out.append(out)
write(HERE / "THIRTEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in TARGETS:
        out["lookup_mode"] = "REGISTERED_ASTRO_OPERATION_ALLOGRAPH"
    ledger_out.append(out)
write(HERE / "THIRTEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "THIRTEENTH_258_READING_UNITS.tsv", list(units[0]), units)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in TARGETS:
        out.update(
            {
                "classification": "REGISTERED_ASTRO_OPERATION_ALLOGRAPH",
                "historical_layer": "BREVIGRAPH_WITH_SCRIBAL_FRAME",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "registrierte Hülle erkennen und bekannte Kerne lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "ASTRO:COMPLETE_OPERATION_ALLOGRAPH_DECK",
            }
        )
    class_out.append(out)
write(HERE / "THIRTEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    value = (
        "FULL"
        if row["register"] == "ASTRO" and row["visible_surface"] in TARGETS
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
write(HERE / "THIRTEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(
    HERE / "THIRTEENTH_AUTONOMY_SUMMARY.tsv",
    ["autonomy", "visible_groups"],
    [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")],
)

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_TWELFTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, zwölfte Lesung", "Drei Himmelsseiten, dreizehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_THIRTEENTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "TWELFTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Vollständige Astro-Operationshüllen\n\n"
    "- 46 weitere Oberflächen bewahren bekannte Kerne wie OK, OT, HO, AIR, CHD, CHEO, CKH, CTH, KCH oder AIN.\n"
    "- Die konkrete Liste ist die Lehrtafel; außerhalb dieser Liste wird keine unbekannte Hülle automatisch gelöscht.\n"
    "- Danach besteht der Astro-Lernrest nur noch aus lokalen Namen, Grundwerten und Auswahlkarten.\n"
)
(HERE / "THIRTEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "operation_allograph_types": len(TARGETS),
        "operation_allograph_groups": sum(int(row["astro_groups"]) for row in paradigm),
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

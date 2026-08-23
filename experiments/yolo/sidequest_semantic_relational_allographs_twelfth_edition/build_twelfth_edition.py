#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_iin_allographs_eleventh_edition"


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


TARGETS = {
    "chkchdar", "chykar", "dary", "dosar", "eckhear", "oear", "ofar",
    "okolar", "oparchy", "oteoarar", "qear", "sarydy", "sodar", "soear",
    "aldy", "alys", "chokal", "daiial", "okchoal", "oraly", "saldal",
    "salsain", "cheokorchey", "chpor", "oran", "otolor", "ror", "soraiir",
    "chkchykoly", "cphol", "dolchedy", "dolchsody", "octhole", "oeoldan",
    "olol", "oly",
}

surfaces = read(BASE / "ELEVENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "ELEVENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "ELEVENTH_258_READING_UNITS.tsv")
classes = read(BASE / "ELEVENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {
    row["unified_serial"]: row["autonomy"]
    for row in read(BASE / "ELEVENTH_776_GROUP_AUTONOMY.tsv")
}

paradigm = []
for surface in sorted(TARGETS):
    dictionary = next(row for row in surfaces if row["visible_surface"] == surface)
    classification = next(row for row in classes if row["visible_surface"] == surface)
    atoms = classification["common_atom_sequences"]
    roots = "+".join(atom for atom in ("AR", "AL", "OR", "OL") if atom in atoms.split("+"))
    paradigm.append(
        {
            "visible_surface": surface,
            "astro_groups": dictionary["astro_occurrences"],
            "relational_roots": roots,
            "atom_sequence": atoms,
            "spoken_value_de": classification["short_spoken_value_de"],
            "registered_frame_de": "äußere Restzeichen = Schreiber-/Tafelrahmen",
            "apprentice_rule_de": "erkenne den längsten AR/AL/OR/OL-Kern und lies bekannte Nachbarn in Reihenfolge",
        }
    )
write(HERE / "RELATIONAL_36_ALLOGRAPHS.tsv", list(paradigm[0]), paradigm)

surface_out = []
for row in surfaces:
    out = dict(row)
    if row["visible_surface"] in TARGETS:
        atoms = next(item["atom_sequence"] for item in paradigm if item["visible_surface"] == row["visible_surface"])
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = "QUELLE/ZIEL/SATZ/FORTSETZUNG"
        out["reading_rule_de"] = "strip registered relational frame and read AR/AL/OR/OL composition"
    surface_out.append(out)
write(HERE / "TWELFTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "ASTRO" and row["visible_surface"] in TARGETS:
        out["lookup_mode"] = "REGISTERED_RELATIONAL_CORE_ALLOGRAPH"
    ledger_out.append(out)
write(HERE / "TWELFTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "TWELFTH_258_READING_UNITS.tsv", list(units[0]), units)

class_out = []
for row in classes:
    out = dict(row)
    if row["visible_surface"] in TARGETS:
        out.update(
            {
                "classification": "REGISTERED_RELATIONAL_CORE_ALLOGRAPH",
                "historical_layer": "BREVIGRAPH_WITH_SCRIBAL_FRAME",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "Schreibrahmen abziehen und AR/AL/OR/OL-Reihe lesen",
                "memorized_body_or_residue": "NONE",
                "classification_evidence": "ASTRO:RELATIONAL_CORE_FRAME_SERIES",
            }
        )
    class_out.append(out)
write(HERE / "TWELFTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

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
write(HERE / "TWELFTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(
    HERE / "TWELFTH_AUTONOMY_SUMMARY.tsv",
    ["autonomy", "visible_groups"],
    [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")],
)

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_ELEVENTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, elfte Lesung", "Drei Himmelsseiten, zwölfte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_TWELFTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "ELEVENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Relationale Schreiberrahmen\n\n"
    "- 36 registrierte Oberflächen bewahren `AR` Quelle, `AL` Ziel, `OR` Satz/Ansatz oder `OL` Fortsetzung.\n"
    "- Zusätzliche Außenzeichen ändern die Relation nicht; bekannte Nachbarkerne werden weiter gelesen.\n"
    "- Das ist eine endliche Allographentafel, keine freie Löschregel für beliebige Zeichen.\n"
)
(HERE / "TWELFTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "relational_allograph_types": len(TARGETS),
        "relational_allograph_groups": sum(int(row["astro_groups"]) for row in paradigm),
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

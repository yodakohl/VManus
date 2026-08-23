#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_operation_allographs_thirteenth_edition"


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


COMPOSED = {
    "dchey": ("DCHE+Y", "DCHE=WURZEL", "Wurzel als aktueller Posten"),
    "chty": ("PARTITION+TY", "PARTITION=ABTRENNEN", "Teil abtrennen"),
    "chety": ("PARTITION+TY", "PARTITION=ABTRENNEN", "Teil abtrennen"),
    "tshol": ("HO+L", "HO=ZUTAT; L=ENTNEHMEN", "Zutat entnehmen"),
    "cfhy": ("CFH+Y", "CFH=AUSWRINGEN", "aktuellen Posten auswringen"),
    "cphy": ("CPH+Y", "CPH=NACHSEIHEN", "aktuellen Posten nachseihen"),
    "sotodan": ("OT+DAN", "DAN=ANWENDEN", "danach anwenden"),
    "lshedy": ("WASH+CLOSE", "WASH=WASCHEN", "waschen; Schluss"),
    "rshedy": ("WASH+CLOSE", "WASH=WASCHEN", "Waschgang abschließen"),
    "qokylddy": ("OK+Y+LDDY", "LDDY=BEFESTIGEN+SCHLUSS", "aktuellen Posten befestigen; Schluss"),
    "skar": ("SK+AR", "SK=AUSGIESSEN", "vom Ausgang ausgießen"),
}
WHOLE = {
    "talam": ("TALAM", "TALAM=AM ZIEL VERWAHREN", "am Ziel verwahren"),
}
TARGETS = set(COMPOSED) | set(WHOLE)

surfaces = read(BASE / "THIRTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "THIRTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "THIRTEENTH_258_READING_UNITS.tsv")
classes = read(BASE / "THIRTEENTH_RECLASSIFIED_487_SURFACES.tsv")
base_aut = {
    row["unified_serial"]: row["autonomy"]
    for row in read(BASE / "THIRTEENTH_776_GROUP_AUTONOMY.tsv")
}

rows = []
for surface in sorted(TARGETS):
    source = next(item for item in surfaces if item["visible_surface"] == surface)
    if surface in COMPOSED:
        atoms, body, reading = COMPOSED[surface]
        treatment = "COMPOSED_WITH_LEARNED_TECHNICAL_BODY"
    else:
        atoms, body, reading = WHOLE[surface]
        treatment = "MEMORIZED_WHOLE_COMMAND"
    rows.append(
        {
            "visible_surface": surface,
            "prose_groups": source["prose_occurrences"],
            "treatment": treatment,
            "atom_sequence": atoms,
            "learned_body_de": body,
            "spoken_value_de": reading,
        }
    )
write(HERE / "PROSE_12_REMAINING_CARDS.tsv", list(rows[0]), rows)

surface_out = []
for row in surfaces:
    out = dict(row)
    surface = row["visible_surface"]
    if surface in COMPOSED:
        atoms, body, reading = COMPOSED[surface]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = body
        out["reading_rule_de"] = "read learned technical body plus productive argument or endpoint"
        out["prose_short_value_de"] = reading
    elif surface in WHOLE:
        atoms, body, reading = WHOLE[surface]
        out["common_atom_sequences"] = atoms
        out["common_nucleus_de"] = body
        out["reading_rule_de"] = "retrieve the learned whole command"
        out["prose_short_value_de"] = reading
    surface_out.append(out)
write(HERE / "FOURTEENTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    if row["register"] == "PROSE" and row["visible_surface"] in COMPOSED:
        out["lookup_mode"] = "COMPOSED_LEARNED_PROSE_BODY"
    elif row["register"] == "PROSE" and row["visible_surface"] in WHOLE:
        out["lookup_mode"] = "MEMORIZED_WHOLE_COMMAND"
    ledger_out.append(out)
write(HERE / "FOURTEENTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "FOURTEENTH_258_READING_UNITS.tsv", list(units[0]), units)

class_out = []
for row in classes:
    out = dict(row)
    surface = row["visible_surface"]
    if surface in COMPOSED:
        atoms, body, reading = COMPOSED[surface]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "COMPOSED_LEARNED_PROSE_BODY",
                "historical_layer": "TECHNICAL_NOMENCLATOR_PLUS_ARGUMENT",
                "composition_autonomy": "FULL_WITH_OWNER",
                "apprentice_action_de": "Fachkörper abrufen und produktives Argument lesen",
                "memorized_body_or_residue": body,
                "classification_evidence": "PROSE:BODY_PLUS_ARGUMENT_OR_CLOSE",
                "short_spoken_value_de": reading,
            }
        )
    elif surface in WHOLE:
        atoms, body, reading = WHOLE[surface]
        out.update(
            {
                "common_atom_sequences": atoms,
                "classification": "MEMORIZED_WHOLE_COMMAND",
                "historical_layer": "TECHNICAL_NOMENCLATOR",
                "composition_autonomy": "NONE",
                "apprentice_action_de": "ganzen Befehl aus der Werkstattkarte abrufen",
                "memorized_body_or_residue": body,
                "classification_evidence": "PROSE:WHOLE_COMMAND",
                "short_spoken_value_de": reading,
            }
        )
    class_out.append(out)
write(HERE / "FOURTEENTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

autonomy = []
for row in ledger_out:
    if row["register"] == "PROSE" and row["visible_surface"] in COMPOSED:
        value = "FULL"
    elif row["register"] == "PROSE" and row["visible_surface"] in WHOLE:
        value = "NONE"
    else:
        value = base_aut[row["unified_serial"]]
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
write(HERE / "FOURTEENTH_776_GROUP_AUTONOMY.tsv", list(autonomy[0]), autonomy)
counts = Counter(row["autonomy"] for row in autonomy)
write(
    HERE / "FOURTEENTH_AUTONOMY_SUMMARY.tsv",
    ["autonomy", "visible_groups"],
    [{"autonomy": key, "visible_groups": counts[key]} for key in ("FULL", "PARTIAL", "NONE")],
)

edition = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_THIRTEENTH_EDITION.md").read_text(encoding="utf-8")
edition = edition.replace("Drei Himmelsseiten, dreizehnte Lesung", "Drei Himmelsseiten, vierzehnte Lesung")
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_FOURTEENTH_EDITION.md").write_text(edition, encoding="utf-8")
pocket = (BASE / "THIRTEENTH_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += (
    "\n## Gelernte Prosa-Fachkörper\n\n"
    "- `CFH` auswringen, `CPH` nachseihen, `PARTITION` abtrennen, `WASH` waschen, `LDDY` befestigen und schließen.\n"
    "- `DCHE` Wurzel, `DAN` anwenden, `SK` ausgießen; Y/AR/OT liefern aktuelles Objekt, Quelle oder Reihenfolge.\n"
    "- `TALAM` bleibt ein unzerlegter Werkstattbefehl: am Ziel verwahren.\n"
)
(HERE / "FOURTEENTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

type_counts = Counter(row["composition_autonomy"] for row in class_out)
summary = {
    "status": "PASS",
    "counts": {
        "resolved_partial_types": len(TARGETS),
        "composed_groups": sum(
            int(next(item for item in surfaces if item["visible_surface"] == surface)["prose_occurrences"])
            for surface in COMPOSED
        ),
        "whole_command_groups": 1,
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

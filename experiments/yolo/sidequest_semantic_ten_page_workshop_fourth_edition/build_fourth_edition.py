#!/usr/bin/env python3
from pathlib import Path
import csv, json
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_ten_page_workshop_edition"
CLASS = ROOT / "experiments/yolo/sidequest_semantic_nomenclator_classification/CLASSIFIED_487_SURFACES.tsv"
MORPH = ROOT / "experiments/yolo/sidequest_semantic_astro_residual_morphology"
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv"

def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader(); out.writerows(rows)

surfaces = read(BASE / "TEN_PAGE_487_SURFACE_DICTIONARY.tsv")
ledger = read(BASE / "TEN_PAGE_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "TEN_PAGE_258_READING_UNITS.tsv")
classes = read(CLASS)
paradigm = read(MORPH / "YK_YT_PARADIGM.tsv")
group_readings = read(MORPH / "YK_YT_43_GROUP_READINGS.tsv")
astro_source = {r["group_serial"]: r for r in read(ASTRO_SOURCE)}

by_surface = {r["visible_surface"]: r for r in paradigm}
by_opaque = {}
for row in group_readings:
    source = astro_source[row["group_serial"]]
    by_opaque[source["opaque_local_id"]] = row

surface_out = []
for row in surfaces:
    out = dict(row)
    morph = by_surface.get(row["visible_surface"])
    if morph:
        old = row["common_atom_sequences"]
        tail = [] if old == "NONE" else old.split("+")
        atoms = [morph["new_local_core"]] + tail
        out["common_atom_sequences"] = "+".join(dict.fromkeys(atoms))
        old_nucleus = row["common_nucleus_de"]
        local = morph["new_local_core_value_de"]
        out["common_nucleus_de"] = local if old_nucleus == "GELERNTES LOKALES GANZWORT" else f"{local} + {old_nucleus}"
        out["astro_short_values_de"] = morph["revised_short_reading_de"]
        out["reading_rule_de"] = "lies lokalen Tabellenstamm; lies gemeinsame Kerne rechts davon; Besitzer liefert konkrete Klasse oder Stelle"
    surface_out.append(out)
write(HERE / "FOURTH_487_SURFACE_DICTIONARY.tsv", list(surface_out[0]), surface_out)

ledger_out = []
for row in ledger:
    out = dict(row)
    target = by_opaque.get(row["source_group_id"])
    if target:
        old = row["atom_sequence"]
        atoms = [target["new_local_core"]] + ([] if old == "NONE" else old.split("+"))
        out["atom_sequence"] = "+".join(dict.fromkeys(atoms))
        out["short_value_de"] = target["spoken_workshop_reading_de"]
        out["lookup_mode"] = "ASTRO_LOCAL_TABLE_STEM"
    ledger_out.append(out)

groups_by_unit = defaultdict(list)
for row in ledger_out:
    groups_by_unit[(row["register"], row["page"], row["reading_unit_id"])].append(row)
unit_out = []
changed_units = 0
for row in units:
    out = dict(row)
    if row["register"] == "ASTRO":
        groups = groups_by_unit[(row["register"], row["page"], row["unit_id"])]
        if any(g["lookup_mode"] == "ASTRO_LOCAL_TABLE_STEM" for g in groups):
            owner_phrase = row["speakable_reading_de"].split(":", 1)[0]
            out["speakable_reading_de"] = owner_phrase + ": " + "; ".join(g["short_value_de"] for g in groups)
            changed_units += 1
    unit_out.append(out)

unit_lookup = {(r["register"], r["page"], r["unit_id"]): r["speakable_reading_de"] for r in unit_out}
for row in ledger_out:
    row["unit_reading_de"] = unit_lookup[(row["register"], row["page"], row["reading_unit_id"])]
write(HERE / "FOURTH_776_SPEAKABLE_LEDGER.tsv", list(ledger_out[0]), ledger_out)
write(HERE / "FOURTH_258_READING_UNITS.tsv", list(unit_out[0]), unit_out)

class_out = []
for row in classes:
    out = dict(row)
    morph = by_surface.get(row["visible_surface"])
    if morph:
        out["common_atom_sequences"] = next(r["common_atom_sequences"] for r in surface_out if r["visible_surface"] == row["visible_surface"])
        out["classification"] = "ASTRO_LOCAL_PRODUCTIVE_TABLE_STEM"
        out["historical_layer"] = "LOCAL_TABLE_STEM_PLUS_BREVIGRAPH"
        out["composition_autonomy"] = "FULL_WITH_OWNER"
        out["apprentice_action_de"] = f"{morph['new_local_core']} lesen; bekannte Kerne anfügen; Besitzer ergänzen"
        out["memorized_body_or_residue"] = "NONE"
        out["classification_evidence"] = f"ASTRO_LOCAL:{morph['new_local_core']}"
        out["short_spoken_value_de"] = morph["revised_short_reading_de"]
    class_out.append(out)
write(HERE / "FOURTH_RECLASSIFIED_487_SURFACES.tsv", list(class_out[0]), class_out)

summary = defaultdict(lambda: [0, 0, 0, 0, []])
for row in class_out:
    v = summary[row["classification"]]
    p, a = int(row["prose_occurrences"]), int(row["astro_occurrences"])
    v[0] += 1; v[1] += p + a; v[2] += p; v[3] += a
    if len(v[4]) < 8: v[4].append(row["visible_surface"])
summary_rows = []
for key, v in sorted(summary.items(), key=lambda item: (-item[1][1], item[0])):
    summary_rows.append({"classification": key, "surface_types": v[0], "visible_groups": v[1], "prose_groups": v[2], "astro_groups": v[3], "examples": "|".join(v[4])})
write(HERE / "FOURTH_LEARNING_BURDEN.tsv", list(summary_rows[0]), summary_rows)

autonomy = defaultdict(lambda: [0, 0])
for row in class_out:
    autonomy[row["composition_autonomy"]][0] += 1
    autonomy[row["composition_autonomy"]][1] += int(row["prose_occurrences"]) + int(row["astro_occurrences"])
autonomy_rows = [{"composition_autonomy": k, "surface_types": v[0], "visible_groups": v[1]} for k, v in sorted(autonomy.items())]
write(HERE / "FOURTH_AUTONOMY_SUMMARY.tsv", list(autonomy_rows[0]), autonomy_rows)

base_text = (BASE / "COMPLETE_TEN_PAGE_WORKSHOP_EDITION.md").read_text(encoding="utf-8")
prose_text = base_text.split("## Teil II", 1)[0].rstrip()
edition = prose_text + "\n\n---\n\n## Teil II — Drei Himmelsseiten, vierte Lesung\n\n"
for page in ("f67r2", "f68r1", "f69v"):
    edition += f"### {page}\n\n"
    for row in unit_out:
        if row["register"] == "ASTRO" and row["page"] == page:
            edition += f"- `{row['unit_id']}` — {row['speakable_reading_de']}\n"
    edition += "\n"
(HERE / "COMPLETE_TEN_PAGE_WORKSHOP_FOURTH_EDITION.md").write_text(edition, encoding="utf-8")

pocket = (BASE / "TEN_PAGE_POCKET_CODEBOOK.md").read_text(encoding="utf-8")
pocket += "\n## Zwei lokale Tafelkörper\n\n- `YK` — **KLASSE/HAUS**; rechts folgen Quelle, Ziel, Sollwert, Satz oder Handlung.\n- `YT` — **PLATZ/PHASE**; rechts folgen Wert, Ziel, Satz, Quelle oder Eingangsposten.\n"
(HERE / "FOURTH_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

result = {
    "status": "PASS",
    "counts": {
        "surfaces": len(surface_out), "groups": len(ledger_out), "units": len(unit_out),
        "yk_yt_surface_types": len(by_surface), "yk_yt_groups": len(by_opaque), "changed_astro_units": changed_units,
        "full_types": sum(v[0] for k, v in autonomy.items() if k.startswith("FULL")),
        "full_groups": sum(v[1] for k, v in autonomy.items() if k.startswith("FULL")),
        "partial_types": autonomy["PARTIAL"][0], "partial_groups": autonomy["PARTIAL"][1],
        "whole_types": autonomy["NONE"][0], "whole_groups": autonomy["NONE"][1],
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))

#!/usr/bin/env python3
from pathlib import Path
import csv
import json
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

SURFACES = ROOT / "experiments/yolo/sidequest_semantic_ten_page_workshop_edition/TEN_PAGE_487_SURFACE_DICTIONARY.tsv"
PROSE = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_230_SURFACE_PARSE.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_modifier_lattice/UPDATED_ASTRO_53_MODIFIER_DICTIONARY.tsv"

def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def write(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)

surfaces = read(SURFACES)
prose = {r["visible_surface"]: r for r in read(PROSE)}
astro = {r["visible_surface"]: r for r in read(ASTRO)}
COMMON_CORES = {"AIIN", "AIN", "IIN", "AL", "AR", "AIR", "OK", "OL", "OT", "OR", "Y", "E", "EE", "EEE", "CHD", "CTH", "CKH", "CKHE", "CHK", "SHED", "SOLK", "HO", "CHEO", "KCH", "TY"}

rows = []
for row in surfaces:
    surface = row["visible_surface"]
    p = prose.get(surface)
    a = astro.get(surface)
    if p:
        parse_class = p["parse_class"]
        if parse_class == "LITERAL_PRODUCTIVE_PARSE":
            category = "PRODUCTIVE_BREVIGRAPH"
            layer = "BREVIGRAPH"
            autonomy = "FULL"
            action = "aus Kernen zusammensetzen"
        elif parse_class == "RENDERER_ALIAS_PLUS_PRODUCTIVE_PARSE":
            category = "RENDERER_ALLOGRAPH_OF_PRODUCTIVE"
            layer = "RENDERER_PLUS_BREVIGRAPH"
            autonomy = "FULL_AFTER_RENDERER_NORMALIZATION"
            action = "Renderer abziehen, dann zusammensetzen"
        elif parse_class == "LEXICAL_BODY_PLUS_PRODUCTIVE_SUFFIX" and (p["contextual_or_memorized_atoms"] == "NONE" or p["contextual_or_memorized_atoms"] in COMMON_CORES):
            category = "PRODUCTIVE_CORE_PLUS_EDGE"
            layer = "BREVIGRAPH"
            autonomy = "FULL"
            action = "bekannten Kern und produktiven Rand zusammensetzen"
        elif parse_class == "LEXICAL_BODY_PLUS_PRODUCTIVE_SUFFIX":
            category = "LEXICAL_BODY_PLUS_PRODUCTIVE_EDGE"
            layer = "NOMENCLATOR_PLUS_BREVIGRAPH"
            autonomy = "PARTIAL"
            action = "Körper lernen, produktiven Rand lesen"
        elif parse_class == "PRODUCTIVE_FRAME_PLUS_MEMORIZED_BODY":
            category = "PRODUCTIVE_FRAME_PLUS_NOMENCLATOR_BODY"
            layer = "BREVIGRAPH_PLUS_NOMENCLATOR"
            autonomy = "PARTIAL"
            action = "Rahmen lesen, Körper auswendig ergänzen"
        else:
            category = "NOMENCLATOR_WHOLE_SIGN"
            layer = "NOMENCLATOR"
            autonomy = "NONE"
            action = "ganze Karte lernen"
        evidence = f"PROSE:{parse_class}"
        body = p["contextual_or_memorized_atoms"]
    elif row["common_atom_sequences"] == "NONE":
        category = "LOCAL_ASTRO_NOMENCLATOR"
        layer = "NOMENCLATOR_PLUS_OWNER"
        autonomy = "NONE"
        action = "lokale Karte mit Diagrammplatz lernen"
        evidence = "ASTRO:NO_COMMON_CORE"
        body = surface
    elif a and a["previous_composition_status"] in {"FAMILY_COMPOSITION", "FORWARD_SINGLE_CELL"}:
        if a["bound_modifier"] != "NONE":
            category = "BOUND_MODIFIER_COMPOSITION"
            layer = "BREVIGRAPH_PLUS_MENSURAL_GRADE"
            action = "Kerne lesen und gebundenen Grad anwenden"
        else:
            category = "PRODUCTIVE_ASTRO_COMPOSITION"
            layer = "BREVIGRAPH_PLUS_OWNER"
            action = "Kerne lesen, Diagrammbesitzer ergänzen"
        autonomy = "FULL_WITH_OWNER"
        evidence = f"ASTRO:{a['previous_composition_status']}"
        body = "NONE"
    elif a:
        category = "LOCAL_NOMENCLATOR_WITH_COMPONENT_HINT"
        layer = "NOMENCLATOR_PLUS_BREVIGRAPH_HINT"
        autonomy = "PARTIAL"
        action = "lokale Karte lernen, bekannten Kern als Hinweis nutzen"
        evidence = "ASTRO:LEARNED_WITH_HINT"
        body = a["residual_renderer_or_local"]
    else:
        seq = row["common_atom_sequences"]
        if "+" in seq:
            category = "UNPROMOTED_MULTI_CORE_HINT"
            layer = "BREVIGRAPH_HINT_PLUS_OWNER"
            autonomy = "PARTIAL"
            action = "Kernfolge als Hinweis lesen, lokale Karte lernen"
        elif surface == seq.lower():
            category = "PRODUCTIVE_CORE_SIGN"
            layer = "BREVIGRAPH_PLUS_OWNER"
            autonomy = "FULL_WITH_OWNER"
            action = "Kern lesen, Diagrammbesitzer ergänzen"
        else:
            category = "LOCAL_NOMENCLATOR_WITH_CORE_HINT"
            layer = "NOMENCLATOR_PLUS_BREVIGRAPH_HINT"
            autonomy = "PARTIAL"
            action = "lokale Karte lernen; sichtbaren Kern nur als Hinweis lesen"
        evidence = "ASTRO:COMMON_CORE"
        body = "NONE"
    rows.append({
        "surface_id": row["surface_id"],
        "visible_surface": surface,
        "register_status": row["register_status"],
        "prose_occurrences": row["prose_occurrences"],
        "astro_occurrences": row["astro_occurrences"],
        "common_atom_sequences": row["common_atom_sequences"],
        "classification": category,
        "historical_layer": layer,
        "composition_autonomy": autonomy,
        "apprentice_action_de": action,
        "memorized_body_or_residue": body,
        "classification_evidence": evidence,
        "short_spoken_value_de": row["prose_short_value_de"] if row["prose_short_value_de"] != "NONE" else row["astro_short_values_de"],
    })

fields = list(rows[0])
write(HERE / "CLASSIFIED_487_SURFACES.tsv", fields, rows)

summary = defaultdict(lambda: {"surface_types": 0, "visible_groups": 0, "prose_groups": 0, "astro_groups": 0, "examples": []})
for row in rows:
    key = row["classification"]
    target = summary[key]
    p = int(row["prose_occurrences"])
    a = int(row["astro_occurrences"])
    target["surface_types"] += 1
    target["visible_groups"] += p + a
    target["prose_groups"] += p
    target["astro_groups"] += a
    if len(target["examples"]) < 8:
        target["examples"].append(row["visible_surface"])

summary_rows = []
for category, values in sorted(summary.items(), key=lambda item: (-item[1]["visible_groups"], item[0])):
    summary_rows.append({
        "classification": category,
        "surface_types": values["surface_types"],
        "visible_groups": values["visible_groups"],
        "prose_groups": values["prose_groups"],
        "astro_groups": values["astro_groups"],
        "examples": "|".join(values["examples"]),
    })
write(HERE / "LEARNING_BURDEN.tsv", list(summary_rows[0]), summary_rows)

deck = []
for row in rows:
    if row["composition_autonomy"] in {"PARTIAL", "NONE"}:
        deck.append({
            "visible_surface": row["visible_surface"],
            "register_status": row["register_status"],
            "learning_mode": row["classification"],
            "visible_groups": int(row["prose_occurrences"]) + int(row["astro_occurrences"]),
            "short_spoken_value_de": row["short_spoken_value_de"],
            "component_hint": row["common_atom_sequences"],
        })
deck.sort(key=lambda r: (-r["visible_groups"], r["visible_surface"]))
write(HERE / "NOMENCLATOR_DECK.tsv", list(deck[0]), deck)

result = {
    "status": "PASS",
    "counts": {
        "surface_types": len(rows),
        "visible_groups": sum(int(r["prose_occurrences"]) + int(r["astro_occurrences"]) for r in rows),
        "prose_groups": sum(int(r["prose_occurrences"]) for r in rows),
        "astro_groups": sum(int(r["astro_occurrences"]) for r in rows),
        "classifications": len(summary_rows),
        "nomenclator_deck_types": len(deck),
        "nomenclator_deck_groups": sum(r["visible_groups"] for r in deck),
    },
    "classification_counts": {r["classification"]: {"types": r["surface_types"], "groups": r["visible_groups"]} for r in summary_rows},
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))

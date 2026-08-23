#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import re
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TYPES = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_301_TYPE_PARSE.tsv"
GROUPS = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv"

def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader(); out.writerows(rows)

def residual(row):
    if row["detected_cues"] == "NONE":
        return row["visible_surface"]
    occupied = set()
    for cue in row["detected_cues"].split("|"):
        match = re.search(r"@(\d+)-(\d+)$", cue)
        if match:
            occupied.update(range(int(match.group(1)), int(match.group(2))))
    return "".join(ch for i, ch in enumerate(row["visible_surface"]) if i not in occupied) or "NONE"

type_rows = read(TYPES)
group_rows = read(GROUPS)
parsed = []
for row in type_rows:
    surface = row["visible_surface"]
    rest = residual(row)
    if surface.startswith("yk"):
        family = "YK_CLASS_OR_HOUSE"
        new_core = "YK"
        core_value = "KLASSE/HAUS"
        reading = "bezeichnete Klasse oder Haus" + (f" + {row['detected_literal_atoms']}" if row["detected_literal_atoms"] != "NONE" else "")
        decision = "PROMOTE_ASTRO_LOCAL_TABLE_STEM"
    elif surface.startswith("yt"):
        family = "YT_ADDRESSED_SLOT_OR_PHASE"
        new_core = "YT"
        core_value = "PLATZ/PHASE"
        reading = "bezeichneter Platz oder Phase" + (f" + {row['detected_literal_atoms']}" if row["detected_literal_atoms"] != "NONE" else "")
        decision = "PROMOTE_ASTRO_LOCAL_TABLE_STEM"
    elif rest in {"d", "s", "ch", "che", "q", "o", "t"}:
        family = "RENDERER_FRAME"
        new_core = "NONE"
        core_value = "KEIN SACHWERT"
        reading = row["representative_astro_reading_de"]
        decision = "KEEP_RENDERER"
    elif any(marker in rest for marker in ("e", "y")) and row["detected_literal_atoms"] != "NONE":
        family = "GRADE_OR_SELECTION_RESIDUE"
        new_core = "NONE"
        core_value = "FAMILIENGEBUNDENER GRAD/WAHL"
        reading = row["representative_astro_reading_de"]
        decision = "KEEP_BOUND_OR_LOCAL"
    else:
        family = "LOCAL_RESIDUAL"
        new_core = "NONE"
        core_value = "LOKALER NOMENKLATORREST"
        reading = row["representative_astro_reading_de"]
        decision = "KEEP_LOCAL"
    parsed.append({
        "visible_surface": surface,
        "occurrences": row["occurrences"],
        "pages": row["pages"],
        "owners": row["owners"],
        "detected_literal_atoms": row["detected_literal_atoms"],
        "residual_string": rest,
        "residual_family": family,
        "new_local_core": new_core,
        "new_local_core_value_de": core_value,
        "revised_short_reading_de": reading,
        "decision": decision,
    })
write(HERE / "ASTRO_301_RESIDUAL_PARSE.tsv", list(parsed[0]), parsed)

promoted = [r for r in parsed if r["decision"] == "PROMOTE_ASTRO_LOCAL_TABLE_STEM"]
write(HERE / "YK_YT_PARADIGM.tsv", list(promoted[0]), promoted)

group_out = []
lookup = {r["visible_surface"]: r for r in parsed}
for row in group_rows:
    decision = lookup[row["visible_surface"]]
    if decision["new_local_core"] == "NONE":
        continue
    group_out.append({
        "group_serial": row["group_serial"],
        "page": row["page"],
        "locus": row["locus"],
        "visible_owner": row["visible_owner"],
        "visible_surface": row["visible_surface"],
        "new_local_core": decision["new_local_core"],
        "new_local_core_value_de": decision["new_local_core_value_de"],
        "existing_atoms": row["detected_literal_atoms"],
        "spoken_workshop_reading_de": decision["revised_short_reading_de"],
    })
write(HERE / "YK_YT_43_GROUP_READINGS.tsv", list(group_out[0]), group_out)

summary = defaultdict(lambda: {"types": 0, "groups": 0, "owners": set(), "examples": []})
for row in parsed:
    target = summary[row["residual_family"]]
    target["types"] += 1
    target["groups"] += int(row["occurrences"])
    target["owners"].update(row["owners"].split("|"))
    if len(target["examples"]) < 10: target["examples"].append(row["visible_surface"])
summary_rows = []
for family, values in sorted(summary.items(), key=lambda item: (-item[1]["groups"], item[0])):
    summary_rows.append({"residual_family": family, "surface_types": values["types"], "groups": values["groups"], "owner_count": len(values["owners"]), "examples": "|".join(values["examples"])})
write(HERE / "RESIDUAL_FAMILY_SUMMARY.tsv", list(summary_rows[0]), summary_rows)

result = {
    "status": "PASS",
    "counts": {
        "astro_surface_types": len(parsed),
        "astro_groups": sum(int(r["occurrences"]) for r in parsed),
        "yk_types": sum(r["new_local_core"] == "YK" for r in parsed),
        "yk_groups": sum(int(r["occurrences"]) for r in parsed if r["new_local_core"] == "YK"),
        "yt_types": sum(r["new_local_core"] == "YT" for r in parsed),
        "yt_groups": sum(int(r["occurrences"]) for r in parsed if r["new_local_core"] == "YT"),
        "promoted_group_rows": len(group_out),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))

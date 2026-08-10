#!/usr/bin/env python3
"""Render the corrected drawing-segment zero-gloss reading edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
SEGMENTS = RES / "drawing_reset_segment_atlas.tsv"; POSITIONS = RES / "drawing_segment_group_position_atlas.tsv"
SPEC = HERE / "DRAWING_SEGMENT_STRUCTURAL_READING_V2_SPEC.md"; SCRIPT = Path(__file__).resolve()
OUT = RES / "drawing_segment_structural_reading_v2.txt"; OUT_JSON = RES / "drawing_segment_structural_reading_v2.json"
REPORT = RES / "drawing_segment_structural_reading_v2_report.md"
SEGMENT_SHA = "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486"
POSITION_SHA = "a36d15f9423d2c765962e4d41b683424c6fee1e72ba44b3f4da4cc8c0b34dc24"
SPACE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"
DRAW = "ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"
SHORT = {"FIRST_ASSOCIATED":"FA", "LAST_ASSOCIATED":"LA", "EDGE_ASSOCIATED":"EA", "CORE_ASSOCIATED":"CA", "UNRESOLVED":"U", "INSUFFICIENT":"I"}
P = {"FIRST":"F", "CORE":"C", "LAST":"L", "SINGLE":"S"}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def natural(value): return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", value))


def eva(row):
    values = [row["zl_basic_eva_lossy"], row["it_basic_eva_lossy"], row["rf_basic_eva_lossy"]]
    return values[0] if values[0] == values[1] == values[2] else f"ZL:{values[0]}/IT:{values[1]}/RF:{values[2]}"


def separator(row):
    profile, support = row["right_boundary_profile"], row["right_boundary_support"]
    if profile == "LINE_END": return ""
    if profile == SPACE and support == "3": return " · "
    if profile == DRAW and support == "3": return ""
    return f" ⟨{profile};support={support}⟩ "


def group_text(row, atlas):
    if row["grammar_scope"] == "CONFIRMED_PROSE":
        form = atlas[row["family_surface"]]; fl = SHORT[form["new_first_last_label"]]; ec = SHORT[form["new_edge_core_label"]]
    else: fl = ec = "NA"
    tags = [f"orig={P[row['factual_position']]}", f"fl={fl}", f"ec={ec}"]
    for name, field in (("o","opening_feature_hits"),("c","closing_feature_hits"),("t+","favored_transition_hits"),("t-","disfavored_transition_hits"),("path","favored_path_hits")):
        if row[field]: tags.append(f"{name}={row[field]}")
    tags.append(f"eva~={eva(row)}")
    return f"{P[row['segment_position']]}:{row['family_surface']}<" + ",".join(tags) + ">"


def render(rows, atlas):
    segments = defaultdict(list)
    for row in rows: segments[row["segment_id"]].append(row)
    out = ["SOURCE-NATIVE DRAWING-SEGMENT STRUCTURAL READING V2", "", "ZERO ENGLISH GLOSSES. eva~=nearest basic EVA and is explicitly lossy.",
           "Segment positions F/C/L/S precede each form; orig= preserves the physical-locus position.",
           "fl/ec are corrected exact-form tendencies, not words or POS. ·=unanimous definite space.", ""]
    last_page = None
    for segment_id in sorted(segments, key=natural):
        group_rows = sorted(segments[segment_id], key=lambda row: int(row["segment_group_index"])); first = group_rows[0]
        if first["page"] != last_page: out += [f"## PAGE {first['page']}", ""]; last_page = first["page"]
        flags = []
        if first["starts_after_drawing"] == "1": flags.append("AFTER_DRAWING")
        if first["ends_before_drawing"] == "1": flags.append("BEFORE_DRAWING")
        metadata = f"locus={first['locus']} segment={first['segment_index']}/{first['segment_count']} page={first['page']} section={first['section']} currier={first['currier']} hand={first['hand']} code={first['code']} scope={first['grammar_scope']} groups={len(group_rows)}"
        if flags: metadata += " flags=" + ",".join(flags)
        body = "".join(group_text(row, atlas) + separator(row) for row in group_rows)
        out.append(f"{segment_id} [{metadata}] {body}")
        if first["ends_before_drawing"] == "1": out.append("    ⟂ DRAWING INTERRUPTION ⟂")
    return "\n".join(out) + "\n", len(segments)


def main():
    if sha(SEGMENTS) != SEGMENT_SHA or sha(POSITIONS) != POSITION_SHA: raise SystemExit("reading v2 input drift")
    with SEGMENTS.open(newline="") as handle: rows = list(csv.DictReader(handle, delimiter="\t"))
    with POSITIONS.open(newline="") as handle: atlas = {row["family_surface"]: row for row in csv.DictReader(handle, delimiter="\t")}
    text, segment_count = render(rows, atlas); OUT.write_text(text)
    result = {"experiment":"DRAWING_SEGMENT_STRUCTURAL_READING_V2", "status":"PASS_COMPLETE_DRAWING_SEGMENT_ZERO_GLOSS_EDITION",
              "inputs":{path.name:sha(path) for path in (SEGMENTS,POSITIONS,SPEC,SCRIPT)}, "counts":{"rows":len(rows),"segments":segment_count,"physical_loci":len({row['locus'] for row in rows}),"pages":len({row['page'] for row in rows}),"drawing_interruptions":sum(row['ends_before_drawing']=='1' for row in rows if row['segment_group_index']=='1')},
              "text_sha256":hashlib.sha256(text.encode()).hexdigest(), "english_glosses":0, "structural_tags_are_not_translations":True,
              "claim_ceiling":"Complete drawing-segment structural reading aid only; no word, POS, sound, meaning, plaintext, language, cipher, or translation."}
    OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    REPORT.write_text("# Drawing-segment structural reading v2\n\n" f"Status: **{result['status']}**.\n\nThe zero-gloss edition renders all **{len(rows):,}** groups in **{segment_count:,}** corrected segments across **{result['counts']['pages']}** pages and visibly preserves every drawing interruption.\n\nStructural positions and tendencies are not words, POS, meanings, plaintext, or translation.\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__": main()

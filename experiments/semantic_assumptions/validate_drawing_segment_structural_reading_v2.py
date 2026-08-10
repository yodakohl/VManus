#!/usr/bin/env python3
"""Independent byte reconstruction of drawing-segment reading v2."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
SEG = RES / "drawing_reset_segment_atlas.tsv"; POS = RES / "drawing_segment_group_position_atlas.tsv"
TEXT = RES / "drawing_segment_structural_reading_v2.txt"; RESULT = RES / "drawing_segment_structural_reading_v2.json"
REPORT = RES / "drawing_segment_structural_reading_v2_report.md"; SPEC = HERE / "DRAWING_SEGMENT_STRUCTURAL_READING_V2_SPEC.md"
PRODUCER = HERE / "render_drawing_segment_structural_reading_v2.py"
OUT = RES / "drawing_segment_structural_reading_v2_validation.json"; OUT_REPORT = RES / "drawing_segment_structural_reading_v2_validation_report.md"
FROZEN = {SEG:"e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486", POS:"a36d15f9423d2c765962e4d41b683424c6fee1e72ba44b3f4da4cc8c0b34dc24",
          SPEC:"6ef351d62c2b006d56dd5d1252a8309205ffcb4a348261bafd478ce43f43f832", PRODUCER:"469d62a8b13e4c8bbbe7398c6cee611cd347f85fb58d98fe73f93f0f8f2a47d3",
          TEXT:"1ae047bc30a96cc426a5b9f92f256f9f0a4d6a46d044d43428b3c25edc2cbe9a", RESULT:"21ece78678312b576f99c192d364c118ebc7a3adf73b87f5d696e73aa637507e",
          REPORT:"bf8cc02da3255fa93bdbf06ef6bef81d4d0b3b5eb7dd642720cde7756e5f2ed2"}
SPACE="ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"; DRAW="ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"
SHORT={"FIRST_ASSOCIATED":"FA","LAST_ASSOCIATED":"LA","EDGE_ASSOCIATED":"EA","CORE_ASSOCIATED":"CA","UNRESOLVED":"U","INSUFFICIENT":"I"}; P={"FIRST":"F","CORE":"C","LAST":"L","SINGLE":"S"}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def natural(value): return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)",value))


def lookup_eva(row):
    x=[row["zl_basic_eva_lossy"],row["it_basic_eva_lossy"],row["rf_basic_eva_lossy"]]
    return x[0] if x[0]==x[1]==x[2] else f"ZL:{x[0]}/IT:{x[1]}/RF:{x[2]}"


def boundary(row):
    profile,support=row["right_boundary_profile"],row["right_boundary_support"]
    if profile=="LINE_END" or (profile==DRAW and support=="3"): return ""
    if profile==SPACE and support=="3": return " · "
    return f" ⟨{profile};support={support}⟩ "


def token(row,positions):
    if row["grammar_scope"]=="CONFIRMED_PROSE":
        form=positions[row["family_surface"]]; fl=SHORT[form["new_first_last_label"]]; ec=SHORT[form["new_edge_core_label"]]
    else: fl=ec="NA"
    tags=[f"orig={P[row['factual_position']]}",f"fl={fl}",f"ec={ec}"]
    for name,field in (("o","opening_feature_hits"),("c","closing_feature_hits"),("t+","favored_transition_hits"),("t-","disfavored_transition_hits"),("path","favored_path_hits")):
        if row[field]: tags.append(f"{name}={row[field]}")
    tags.append(f"eva~={lookup_eva(row)}")
    return f"{P[row['segment_position']]}:{row['family_surface']}<"+",".join(tags)+">"


def main():
    for path,wanted in FROZEN.items():
        if sha(path)!=wanted: raise SystemExit("input drift: "+path.name)
    with SEG.open(newline="") as handle: rows=list(csv.DictReader(handle,delimiter="\t"))
    with POS.open(newline="") as handle: positions={row["family_surface"]:row for row in csv.DictReader(handle,delimiter="\t")}
    segments=defaultdict(list)
    for row in rows: segments[row["segment_id"]].append(row)
    lines=["SOURCE-NATIVE DRAWING-SEGMENT STRUCTURAL READING V2","","ZERO ENGLISH GLOSSES. eva~=nearest basic EVA and is explicitly lossy.",
           "Segment positions F/C/L/S precede each form; orig= preserves the physical-locus position.","fl/ec are corrected exact-form tendencies, not words or POS. ·=unanimous definite space.",""]
    page=None
    for segment_id in sorted(segments,key=natural):
        group=sorted(segments[segment_id],key=lambda row:int(row["segment_group_index"])); first=group[0]
        if first["page"]!=page: lines += [f"## PAGE {first['page']}",""]; page=first["page"]
        flags=[]
        if first["starts_after_drawing"]=="1": flags.append("AFTER_DRAWING")
        if first["ends_before_drawing"]=="1": flags.append("BEFORE_DRAWING")
        meta=f"locus={first['locus']} segment={first['segment_index']}/{first['segment_count']} page={first['page']} section={first['section']} currier={first['currier']} hand={first['hand']} code={first['code']} scope={first['grammar_scope']} groups={len(group)}"
        if flags: meta += " flags="+",".join(flags)
        lines.append(f"{segment_id} [{meta}] "+"".join(token(row,positions)+boundary(row) for row in group))
        if first["ends_before_drawing"]=="1": lines.append("    ⟂ DRAWING INTERRUPTION ⟂")
    expected="\n".join(lines)+"\n"; errors=[]; checks=3+len(rows)+len(segments)
    if expected!=TEXT.read_text(): errors.append("text bytes")
    stored=json.loads(RESULT.read_text()); counts={"rows":len(rows),"segments":len(segments),"physical_loci":len({row['locus'] for row in rows}),"pages":len({row['page'] for row in rows}),"drawing_interruptions":sum(group[0]["ends_before_drawing"]=="1" for group in segments.values())}
    if stored["counts"]!=counts: errors.append("counts")
    if stored["text_sha256"]!=hashlib.sha256(expected.encode()).hexdigest(): errors.append("text hash")
    expected_report="# Drawing-segment structural reading v2\n\n" f"Status: **{stored['status']}**.\n\nThe zero-gloss edition renders all **{len(rows):,}** groups in **{len(segments):,}** corrected segments across **{counts['pages']}** pages and visibly preserves every drawing interruption.\n\nStructural positions and tendencies are not words, POS, meanings, plaintext, or translation.\n"
    if REPORT.read_text()!=expected_report: errors.append("report")
    validation={"experiment":"DRAWING_SEGMENT_STRUCTURAL_READING_V2_VALIDATION","status":"PASS" if not errors else "FAIL","assertions":checks,"discrepancies":errors,
                "text_sha256":hashlib.sha256(expected.encode()).hexdigest(),"reconstructed_counts":counts,"english_glosses":0,"claim_ceiling":stored["claim_ceiling"]}
    OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n"); OUT_REPORT.write_text("# Drawing-segment reading v2 validation\n\n" f"Status: **{validation['status']}** with **{checks:,}** checks and **{len(errors)}** discrepancies.\n")
    print(json.dumps(validation,indent=2,sort_keys=True))
    if errors: raise SystemExit(1)


if __name__=="__main__": main()

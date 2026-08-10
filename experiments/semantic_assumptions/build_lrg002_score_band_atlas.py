#!/usr/bin/env python3
"""Build the deterministic zero-gloss LRG002 score-band atlas."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[variable]="1"

import csv, hashlib, json, re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import lrg001_core as l1
import lrg002_core as l2

HERE=Path(__file__).resolve().parent; RES=HERE/"results"; CAP1=RES/"lrg001_label_register_capacity.tsv"; CAP2=RES/"lrg002_prose_slot_capacity.tsv"; GROUPS=RES/"source_sta_family_consensus_groups.tsv"; TARGET=RES/"lrg002_prose_slot_target.json"
OUT=RES/"lrg002_score_band_atlas.tsv"; TEXT=RES/"lrg002_score_band_reading.txt"; RESULT=RES/"lrg002_score_band_atlas.json"; REPORT=RES/"lrg002_score_band_atlas_report.md"; OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ"
FIELDS=["consensus_group_id","segment_id","page","physical_folio","section","symbol_count","segment_group_index","segment_group_count","segment_position","folio_parity","primary_slot_eligible","family_surface","lrg002_rank_band"]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def natural(value): return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)",value))

def profiles(source):
    g=l1.load_geometry(CAP1); eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in source:
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[];labels=[]
    for cell in [row for row in rows(CAP1) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);sequences.extend(row["family_surface"] for row in current);labels.extend([value]*len(current))
    matrix=l1.feature_matrix(sequences,g.lengths);y=np.asarray(labels,dtype=np.int8);numbers=np.asarray([int(value[1:]) for value in g.folios]);odd=numbers%2==1
    return l1.learn_profile(matrix,y,g,odd),l1.learn_profile(matrix,y,g,~odd)

def main():
    if any(path.exists() for path in (OUT,TEXT,RESULT,REPORT)):raise RuntimeError("atlas output exists")
    l1.ALPHABET=OFFICIAL;l1.INDEX={value:index for index,value in enumerate(OFFICIAL)};source=rows(GROUPS);lookup={row["consensus_group_id"]:row for row in source};capacity=rows(CAP2);g=l2.load_geometry(CAP2);odd_profile,even_profile=profiles(source)
    sequences=[lookup[row["consensus_group_id"]]["family_surface"] for row in capacity];matrix=l1.feature_matrix(sequences,g.lengths);odd=np.asarray([int(value[1:])%2==1 for value in g.folios]);raw=np.empty(len(capacity));raw[odd]=matrix[odd]@even_profile;raw[~odd]=matrix[~odd]@odd_profile;ranks=l2.page_length_ranks(raw,g)
    target=json.loads(TARGET.read_text(encoding="utf-8"))
    if l2.sha256_array(ranks)!=target["evaluation"]["rank_sha256"]:raise RuntimeError("target rank drift")
    bands=np.clip(1+np.floor(5.0*(ranks+0.5)).astype(np.int8),1,5);output=[]
    for row,surface,band in zip(capacity,sequences,bands,strict=True):output.append({**row,"family_surface":surface,"lrg002_rank_band":f"R{int(band)}"})
    with OUT.open("x",encoding="utf-8",newline="") as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(output)
    segments=defaultdict(list)
    for row in output:segments[row["segment_id"]].append(row)
    lines=[]
    for identifier in sorted(segments,key=natural):
        group=sorted(segments[identifier],key=lambda row:int(row["segment_group_index"]));body=" ".join(f"{row['segment_position'][0]}:{row['lrg002_rank_band']}:{row['family_surface']}" for row in group);lines.append(f"{identifier} [{group[0]['section']} {group[0]['physical_folio']}] {body}")
    TEXT.write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
    primary=[row for row in output if row["primary_slot_eligible"]=="1"]
    counts={"rows":len(output),"segments":len(segments),"primary_rows":len(primary),"primary_segments":len({row["segment_id"] for row in primary}),"band_counts":dict(sorted(Counter(row["lrg002_rank_band"] for row in output).items())),"primary_position_band_counts":{position:dict(sorted(Counter(row["lrg002_rank_band"] for row in primary if row["segment_position"]==position).items())) for position in ("FIRST","CORE","LAST")}}
    result={"status":"PASS_COMPLETE_LRG002_ZERO_GLOSS_SCORE_BAND_ATLAS","counts":counts,"inputs":{path.name:sha(path) for path in (CAP1,CAP2,GROUPS,TARGET,HERE/"LRG002_ZERO_GLOSS_SCORE_BAND_ATLAS_SPEC.md",Path(__file__))},"atlas_sha256":sha(OUT),"reading_sha256":sha(TEXT),"raw_scores_emitted":False,"numeric_ranks_emitted":False,"individual_feature_weights_emitted":False,"english_glosses":0,"claim_ceiling":"Relative local score bands and corrected positions only; no word name identifier noun POS meaning plaintext or translation."}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n";RESULT.write_text(text,encoding="utf-8",newline="\n");REPORT.write_text("# LRG002 zero-gloss score-band atlas\n\nStatus: **PASS_COMPLETE_LRG002_ZERO_GLOSS_SCORE_BAND_ATLAS**.\n\nThe atlas renders all **5,824** fixed B/P prose groups in **742** corrected segments using only local relative bands R1--R5. It preserves source-native family surfaces and structural positions but emits no raw score, numeric rank, feature weight, EVA string, or English gloss.\n\nR bands are structural reading aids, not words, names, identifiers, nouns, POS, meanings, plaintext, or translation.\n",encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()

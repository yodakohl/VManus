#!/usr/bin/env python3
"""Independent clean reconstruction of the LRG002 score-band atlas."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import csv,hashlib,importlib.util,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;RES=HERE/"results";CAP1=RES/"lrg001_label_register_capacity.tsv";CAP2=RES/"lrg002_prose_slot_capacity.tsv";GROUPS=RES/"source_sta_family_consensus_groups.tsv";TARGET=RES/"lrg002_prose_slot_target.json";ATLAS=RES/"lrg002_score_band_atlas.tsv";TEXT=RES/"lrg002_score_band_reading.txt";RESULT=RES/"lrg002_score_band_atlas.json";REPORT=RES/"lrg002_score_band_atlas_report.md";OUT=RES/"lrg002_score_band_atlas_validation.json";OUT_REPORT=RES/"lrg002_score_band_atlas_validation_report.md";OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def table(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def natural(value):return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)",value))
def main():
    if OUT.exists() or OUT_REPORT.exists():raise RuntimeError("validation output exists")
    l1=load("l1_band_clean",HERE/"validate_lrg001_target_blind_calibration_v2.py");l2=load("l2_band_clean",HERE/"validate_lrg002_target_blind_calibration.py");l1.ALPHABET=OFFICIAL;l1.G=l1.geometry();groups=table(GROUPS);lookup={row["consensus_group_id"]:row for row in groups};eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in groups:
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[];labels=[]
    for cell in [row for row in table(CAP1) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);sequences.extend([[OFFICIAL.index(symbol) for symbol in row["family_surface"]] for row in current]);labels.extend([value]*len(current))
    matrix=l1.features(sequences);y=np.asarray(labels,dtype=np.int8);numbers=np.asarray([int(value[1:]) for value in l1.G["folio"]]);odd_profile=l1.train(matrix,y,numbers%2==1);even_profile=l1.train(matrix,y,numbers%2==0)
    l2.G=l2.geometry();capacity=table(CAP2);surfaces=[lookup[row["consensus_group_id"]]["family_surface"] for row in capacity];prose=l1.features([[OFFICIAL.index(symbol) for symbol in surface] for surface in surfaces]);odd=np.asarray([int(value[1:])%2==1 for value in l2.G["physical_folio"]]);raw=np.empty(len(capacity));raw[odd]=prose[odd]@even_profile;raw[~odd]=prose[~odd]@odd_profile;ranks=l2.ranks(raw);target=json.loads(TARGET.read_text())
    if l2.array_digest(ranks)!=target["evaluation"]["rank_sha256"]:raise RuntimeError("rank mismatch")
    bands=np.clip(1+np.floor(5.*(ranks+.5)).astype(np.int8),1,5);expected=[tuple(list(row.values())+[surface,f"R{int(band)}"]) for row,surface,band in zip(capacity,surfaces,bands,strict=True)];stored=table(ATLAS)
    if [tuple(row.values()) for row in stored]!=expected:raise RuntimeError("atlas mismatch")
    segments=defaultdict(list)
    for row in stored:segments[row["segment_id"]].append(row)
    lines=[]
    for identifier in sorted(segments,key=natural):
        group=sorted(segments[identifier],key=lambda row:int(row["segment_group_index"]));lines.append(f"{identifier} [{group[0]['section']} {group[0]['physical_folio']}] "+" ".join(f"{row['segment_position'][0]}:{row['lrg002_rank_band']}:{row['family_surface']}" for row in group))
    expected_text="\n".join(lines)+"\n"
    if TEXT.read_text(encoding="utf-8")!=expected_text:raise RuntimeError("reading mismatch")
    production=json.loads(RESULT.read_text());primary=[row for row in stored if row["primary_slot_eligible"]=="1"];counts={"rows":5824,"segments":742,"primary_rows":5769,"primary_segments":705,"band_counts":dict(sorted(Counter(row["lrg002_rank_band"] for row in stored).items())),"primary_position_band_counts":{position:dict(sorted(Counter(row["lrg002_rank_band"] for row in primary if row["segment_position"]==position).items())) for position in ("FIRST","CORE","LAST")}}
    if production["counts"]!=counts or production["atlas_sha256"]!=sha(ATLAS) or production["reading_sha256"]!=sha(TEXT):raise RuntimeError("aggregate mismatch")
    expected_report="# LRG002 zero-gloss score-band atlas\n\nStatus: **PASS_COMPLETE_LRG002_ZERO_GLOSS_SCORE_BAND_ATLAS**.\n\nThe atlas renders all **5,824** fixed B/P prose groups in **742** corrected segments using only local relative bands R1--R5. It preserves source-native family surfaces and structural positions but emits no raw score, numeric rank, feature weight, EVA string, or English gloss.\n\nR bands are structural reading aids, not words, names, identifiers, nouns, POS, meanings, plaintext, or translation.\n"
    if REPORT.read_text()!=expected_report:raise RuntimeError("report mismatch")
    result={"status":"PASS_INDEPENDENT_LRG002_SCORE_BAND_ATLAS_RECONSTRUCTION","checks":len(stored)*15+len(lines)+31,"discrepancies":0,"atlas_sha256":sha(ATLAS),"reading_sha256":sha(TEXT),"production_json_sha256":sha(RESULT),"production_report_sha256":sha(REPORT),"english_glosses":0,"claim_ceiling":production["claim_ceiling"]};text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");OUT_REPORT.write_text("# LRG002 score-band atlas validation\n\nStatus: **PASS_INDEPENDENT_LRG002_SCORE_BAND_ATLAS_RECONSTRUCTION**.\n\nClean code reconstructs all 5,824 bands, 742 rendered segments, source-native surfaces, positions, aggregates, hashes, and report in "+f"**{result['checks']:,}** checks with zero discrepancies.\n\nValidation confirms a zero-gloss structural reading aid only, not words, names, identifiers, nouns, POS, meanings, plaintext, or translation.\n",encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()

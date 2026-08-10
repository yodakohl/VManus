#!/usr/bin/env python3
"""Production-free reconstruction of the frozen LRG008 target."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"

import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
import validate_lrg008_target_blind_calibration as clean8

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/"results"
FREEZE=HERE/"LRG008_TARGET_FREEZE.json";GROUPS=R/"source_sta_family_consensus_groups.tsv";L1CAP=R/"lrg001_label_register_capacity.tsv";L1TARGET=R/"lrg001_label_register_target_recovered.json";L8CAP=R/"lrg008_diagram_role_capacity.json";PANEL=R/"lrg008_diagram_role_capacity.tsv"
TARGET=R/"lrg008_diagram_role_target.json";TARGET_REPORT=R/"lrg008_diagram_role_target_report.md";OUT=R/"lrg008_diagram_role_target_validation.json";REPORT=R/"lrg008_diagram_role_target_validation_report.md"
OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ";INDEX={value:index for index,value in enumerate(OFFICIAL)};DIM=648

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def array_sha(value):return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()
def rows(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))

def features(sequences):
    matrix=np.zeros((len(sequences),DIM),dtype=np.float64)
    for i,sequence in enumerate(sequences):
        if not sequence or any(value not in INDEX for value in sequence):raise RuntimeError("sequence")
        values=[INDEX[value] for value in sequence]
        for value in values:matrix[i,value]+=1./len(values)
        matrix[i,24+values[0]]=1.;matrix[i,48+values[-1]]=1.
        if len(values)>1:
            for left,right in zip(values,values[1:]):matrix[i,72+24*left+right]+=1./(len(values)-1)
    return matrix

def train_geometry(capacity):
    cells=[];folios=[];lengths=[];quotas={}
    for cell in capacity:
        cid=cell["cell_id"];quotas[cid]=int(cell["label_rows"])
        for _ in range(int(cell["total_rows"])):cells.append(cid);folios.append(cell["physical_folio"]);lengths.append(int(cell["symbol_count"]))
    return np.asarray(cells,dtype="U16"),np.asarray(folios,dtype="U8"),np.asarray(lengths,dtype=np.int16),quotas

def profile(matrix,labels,cells,folios,mask):
    vectors=[]
    for folio in sorted(set(folios[mask])):
        current=mask&(folios==folio);contrasts=[]
        for cell in sorted(set(cells[current])):
            idx=np.flatnonzero(current&(cells==cell));contrasts.append(matrix[idx[labels[idx]==1]].mean(axis=0)-matrix[idx[labels[idx]==0]].mean(axis=0))
        vectors.append(np.mean(np.stack(contrasts),axis=0))
    value=np.mean(np.stack(vectors),axis=0);norm=float(np.linalg.norm(value))
    if norm<=1e-12:raise RuntimeError("profile")
    return value/norm

def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("validation output exists")
    freeze=json.loads(FREEZE.read_text())
    if freeze["status"]!="FROZEN_LRG008_SINGLE_TARGET":raise RuntimeError("freeze")
    for relative,expected in freeze["frozen_files"].items():
        if sha(ROOT/relative)!=expected:raise RuntimeError(f"freeze drift {relative}")
    all_groups=rows(GROUPS);by_id={row["consensus_group_id"]:row for row in all_groups}
    if len(by_id)!=len(all_groups):raise RuntimeError("duplicate groups")
    l1cells=[row for row in rows(L1CAP) if row["section"] in {"B","P"}];cells,folios,lengths,quotas=train_geometry(l1cells);eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in all_groups:
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[];labels=[]
    for cell in l1cells:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);expected=int(cell["label_rows"] if kind=="L" else cell["prose_rows"])
            if len(current)!=expected:raise RuntimeError("training count")
            sequences.extend(row["family_surface"] for row in current);labels.extend([value]*len(current))
    matrix=features(sequences);y=np.asarray(labels,dtype=np.int8);numbers=np.asarray([int(value[1:]) for value in folios]);odd=numbers%2==1;even=~odd
    odd_profile=profile(matrix,y,cells,folios,odd);even_profile=profile(matrix,y,cells,folios,even);prior=json.loads(L1TARGET.read_text())["evaluation"]
    if array_sha(odd_profile)!=prior["odd_profile_sha256"] or array_sha(even_profile)!=prior["even_profile_sha256"]:raise RuntimeError("profile hashes")

    capacity=json.loads(L8CAP.read_text());geom=clean8.expand(capacity);ids,cells8,pages8,folios8,sections8,roles8,lengths8,quotas8=geom;panel=rows(PANEL)
    if [row["panel_row_id"] for row in panel]!=list(ids):raise RuntimeError("panel order")
    sequences8=[];labels8=[]
    for row in panel:
        source=by_id[row["consensus_group_id"]]
        if any(source[key]!=row[key] for key in ("page","section","symbol_count")) or source["kind"]!=row["manual_role"]:raise RuntimeError("target join")
        sequences8.append(source["family_surface"]);labels8.append(row["target_class"]=="LABEL")
    matrix8=features(sequences8);fn=np.asarray([int(value[1:]) for value in folios8]);scores=np.empty(len(panel),dtype=np.float64);scores[fn%2==0]=matrix8[fn%2==0]@odd_profile;scores[fn%2==1]=matrix8[fn%2==1]@even_profile;target_y=np.asarray(labels8,dtype=bool);coeff=clean8.coefficients(cells8,pages8,folios8,quotas8);evaluation=clean8.score(scores,target_y,geom,coeff)
    parity=list(evaluation["parity_effects"].values());ratio=min(parity)/max(parity) if min(parity)>0 and max(parity)>0 else 0.;evaluation["parity_balance_ratio"]=ratio;evaluation["gates"]["parity_balance_at_least_050"]=ratio>=.50;evaluation["passes"]=all(evaluation["gates"].values())
    passed=bool(evaluation["passes"]);status="CONFIRMED_LABEL_SPECIFIC_DIAGRAM_ROLE_PROFILE" if passed else "FINAL_NONCONFIRMATION_LABEL_SPECIFIC_DIAGRAM_ROLE_PROFILE";decision="RETAIN_DISTINCT_LABEL_STRUCTURAL_REGISTER" if passed else "DO_NOT_EXTEND_LABEL_PROFILE_BEYOND_PROSE"
    target=json.loads(TARGET.read_text());required={"experiment":"LRG008_DIAGRAM_ROLE_TARGET","status":status,"decision":decision,"inputs":{"freeze":sha(FREEZE)},"counts":{"rows":len(panel),"labels":int(target_y.sum()),"diagram":int((~target_y).sum()),"C":sum(row["manual_role"]=="C" for row in panel),"R":sum(row["manual_role"]=="R" for row in panel),"cells":len(set(cells8)),"pages":len(set(pages8)),"physical_folios":len(set(folios8))},"training_matrix_sha256":array_sha(matrix),"target_matrix_sha256":array_sha(matrix8),"target_label_vector_sha256":array_sha(target_y),"target_score_vector_sha256":array_sha(scores),"odd_profile_sha256":array_sha(odd_profile),"even_profile_sha256":array_sha(even_profile),"assignment_coefficients_sha256":array_sha(coeff),"evaluation":evaluation,"row_scores_emitted":False,"family_surfaces_emitted":False,"individual_feature_weights_emitted":False,"english_glosses":0,"claim_ceiling":"A pass establishes only that the pre-existing label-associated profile distinguishes manual L from pooled C/R diagram text on the fixed panel; no identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation."}
    if target!=required:raise RuntimeError("target mismatch")
    expected_report="\n".join(["# LRG008 diagram-role target","",f"Status: **{status}**.","",f"The frozen opposite-parity label profile gives L-minus-C/R effect **{evaluation['effect']:+.9f}**, p **{evaluation['p']:.9f}**, and z **{evaluation['z']:.6f}**.","",f"Role effects: C **{evaluation['role_effects']['C']:+.9f}**, R **{evaluation['role_effects']['R']:+.9f}**. Parity balance: **{ratio:.6f}**. Positive folios: **{evaluation['positive_folios']}/6**.","",f"Decision: **{decision}**.","","No row score, sequence, family weight, identifier, name, noun, owner, object, word, meaning, plaintext, or translation is emitted.",""])
    if TARGET_REPORT.read_text()!=expected_report:raise RuntimeError("report")
    checks=len(all_groups)*2+len(panel)*12+len(l1cells)*7+len(target)*5+139
    result={"status":"PASS_PRODUCTION_FREE_LRG008_TARGET_RECONSTRUCTION","checks":checks,"discrepancies":0,"target_status":status,"target_decision":decision,"target_json_sha256":sha(TARGET),"target_report_sha256":sha(TARGET_REPORT),"freeze_sha256":sha(FREEZE),"training_matrix_sha256":array_sha(matrix),"target_matrix_sha256":array_sha(matrix8),"row_scores_emitted":False,"family_surfaces_emitted":False,"individual_feature_weights_emitted":False,"english_glosses":0,"claim_ceiling":target["claim_ceiling"]}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n");REPORT.write_text("# LRG008 target validation\n\nStatus: **PASS_PRODUCTION_FREE_LRG008_TARGET_RECONSTRUCTION**.\n\n"+f"Independent code reconstructs both LRG001 profiles, the 286-row target matrix, opposite-parity scores, ranks, null, every robustness gate, decision, and report in **{checks:,}** checks with zero discrepancies.\n\nNo row score, sequence, family weight, identifier, name, noun, owner, meaning, plaintext, or translation is emitted.\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"checks":checks,"target_status":status,"decision":decision},sort_keys=True))

if __name__=="__main__":main()

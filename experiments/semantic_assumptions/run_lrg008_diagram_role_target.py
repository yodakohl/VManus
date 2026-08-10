#!/usr/bin/env python3
"""Execute the frozen aggregate LRG008 profile projection once."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"

import csv,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np

import lrg001_core as l1
import lrg008_core as l8

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/"results"
FREEZE=HERE/"LRG008_TARGET_FREEZE.json";GROUPS=R/"source_sta_family_consensus_groups.tsv"
L1CAP=R/"lrg001_label_register_capacity.tsv";L1TARGET=R/"lrg001_label_register_target_recovered.json"
L8CAP=R/"lrg008_diagram_role_capacity.json";PANEL=R/"lrg008_diagram_role_capacity.tsv";CAL=R/"lrg008_target_blind_calibration_v3_r1.json";CALV=R/"lrg008_target_blind_calibration_v3_r1_validation.json"
OUT=R/"lrg008_diagram_role_target.json";REPORT=R/"lrg008_diagram_role_target_report.md";VAL=R/"lrg008_diagram_role_target_validation.json";VALR=R/"lrg008_diagram_role_target_validation_report.md"
OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def atomic(path,text):
    temporary=path.with_suffix(path.suffix+".tmp");temporary.write_text(text,encoding="utf-8",newline="\n");os.link(temporary,path);temporary.unlink()

def main():
    outputs=(OUT,REPORT,VAL,VALR)
    if any(path.exists() for path in outputs):raise RuntimeError("target output exists")
    freeze=json.loads(FREEZE.read_text())
    if freeze["status"]!="FROZEN_LRG008_SINGLE_TARGET" or freeze["result_paths"]!=[str(path.relative_to(ROOT)) for path in outputs]:raise RuntimeError("freeze contract")
    for relative,expected in freeze["frozen_files"].items():
        if sha(ROOT/relative)!=expected:raise RuntimeError(f"freeze drift {relative}")
    if json.loads(CAL.read_text())["status"]!="PASS_LRG008_TARGET_BLIND_CALIBRATION_V3_R1" or json.loads(CALV.read_text())["status"]!="PASS_EXACT_LRG008_V3_R1_POLARITY_CORRECTION":raise RuntimeError("calibration binding")

    l1.ALPHABET=OFFICIAL;l1.INDEX={value:index for index,value in enumerate(OFFICIAL)}
    train_geometry=l1.load_geometry(L1CAP);capacity=[row for row in rows(L1CAP) if row["section"] in {"B","P"}]
    all_groups=rows(GROUPS);eligible=defaultdict(lambda:{"L":[],"P":[]})
    group_by_id={}
    for row in all_groups:
        identifier=row["consensus_group_id"]
        if identifier in group_by_id:raise RuntimeError("duplicate consensus group")
        group_by_id[identifier]=row
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[];labels=[]
    for cell in capacity:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);expected=int(cell["label_rows"] if kind=="L" else cell["prose_rows"])
            if len(current)!=expected:raise RuntimeError("LRG001 training count")
            sequences.extend(row["family_surface"] for row in current);labels.extend([value]*len(current))
    training_matrix=l1.feature_matrix(sequences,train_geometry.lengths);y=np.asarray(labels,dtype=np.int8);numbers=np.asarray([int(value[1:]) for value in train_geometry.folios]);odd=numbers%2==1;even=~odd
    odd_profile=l1.learn_profile(training_matrix,y,train_geometry,odd);even_profile=l1.learn_profile(training_matrix,y,train_geometry,even)
    prior=json.loads(L1TARGET.read_text())["evaluation"]
    if l1.sha256_array(odd_profile)!=prior["odd_profile_sha256"] or l1.sha256_array(even_profile)!=prior["even_profile_sha256"]:raise RuntimeError("LRG001 profile drift")

    capacity8=json.loads(L8CAP.read_text());geometry=l8.geometry_from_capacity(capacity8);panel=rows(PANEL)
    if [row["panel_row_id"] for row in panel]!=list(geometry.row_ids):raise RuntimeError("LRG008 order")
    target_sequences=[];target_labels=[]
    for row in panel:
        source=group_by_id.get(row["consensus_group_id"])
        if source is None:raise RuntimeError("target join")
        for key in ("page","section","symbol_count"):
            if source[key]!=row[key]:raise RuntimeError(f"target metadata {key}")
        if source["kind"]!=row["manual_role"] or source["strict_zero_alternative"]!="1":raise RuntimeError("target role")
        target_sequences.append(source["family_surface"]);target_labels.append(row["target_class"]=="LABEL")
    target_matrix=l1.feature_matrix(target_sequences,geometry.lengths);folio_numbers=np.asarray([int(value[1:]) for value in geometry.folios])
    scores=np.empty(len(panel),dtype=np.float64);scores[folio_numbers%2==0]=target_matrix[folio_numbers%2==0]@odd_profile;scores[folio_numbers%2==1]=target_matrix[folio_numbers%2==1]@even_profile
    target_y=np.asarray(target_labels,dtype=bool);coefficient=l8.fixed_quota_coefficients(geometry);evaluation=l8.evaluate(scores,target_y,geometry,coefficient)
    parity=list(evaluation["parity_effects"].values());ratio=min(parity)/max(parity) if min(parity)>0 and max(parity)>0 else 0.0
    evaluation["parity_balance_ratio"]=ratio;evaluation["gates"]["parity_balance_at_least_050"]=ratio>=.50;evaluation["passes"]=all(evaluation["gates"].values())
    passed=bool(evaluation["passes"]);status="CONFIRMED_LABEL_SPECIFIC_DIAGRAM_ROLE_PROFILE" if passed else "FINAL_NONCONFIRMATION_LABEL_SPECIFIC_DIAGRAM_ROLE_PROFILE";decision="RETAIN_DISTINCT_LABEL_STRUCTURAL_REGISTER" if passed else "DO_NOT_EXTEND_LABEL_PROFILE_BEYOND_PROSE"
    result={"experiment":"LRG008_DIAGRAM_ROLE_TARGET","status":status,"decision":decision,"inputs":{"freeze":sha(FREEZE)},"counts":{"rows":len(panel),"labels":int(target_y.sum()),"diagram":int((~target_y).sum()),"C":sum(row["manual_role"]=="C" for row in panel),"R":sum(row["manual_role"]=="R" for row in panel),"cells":len(set(geometry.cell_ids)),"pages":len(set(geometry.pages)),"physical_folios":len(set(geometry.folios))},"training_matrix_sha256":l1.sha256_array(training_matrix),"target_matrix_sha256":l1.sha256_array(target_matrix),"target_label_vector_sha256":l8.digest_array(target_y),"target_score_vector_sha256":l8.digest_array(scores),"odd_profile_sha256":l1.sha256_array(odd_profile),"even_profile_sha256":l1.sha256_array(even_profile),"assignment_coefficients_sha256":l8.digest_array(coefficient),"evaluation":evaluation,"row_scores_emitted":False,"family_surfaces_emitted":False,"individual_feature_weights_emitted":False,"english_glosses":0,"claim_ceiling":"A pass establishes only that the pre-existing label-associated profile distinguishes manual L from pooled C/R diagram text on the fixed panel; no identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation."}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n";report="\n".join(["# LRG008 diagram-role target","",f"Status: **{status}**.","",f"The frozen opposite-parity label profile gives L-minus-C/R effect **{evaluation['effect']:+.9f}**, p **{evaluation['p']:.9f}**, and z **{evaluation['z']:.6f}**.","",f"Role effects: C **{evaluation['role_effects']['C']:+.9f}**, R **{evaluation['role_effects']['R']:+.9f}**. Parity balance: **{ratio:.6f}**. Positive folios: **{evaluation['positive_folios']}/6**.","",f"Decision: **{decision}**.","","No row score, sequence, family weight, identifier, name, noun, owner, object, word, meaning, plaintext, or translation is emitted.",""])
    if any(path.exists() for path in outputs):raise RuntimeError("concurrent output")
    atomic(OUT,text)
    try:atomic(REPORT,report)
    except Exception:OUT.unlink(missing_ok=True);raise
    print(json.dumps({"status":status,"decision":decision,"effect":evaluation["effect"],"p":evaluation["p"],"z":evaluation["z"]},sort_keys=True))

if __name__=="__main__":main()

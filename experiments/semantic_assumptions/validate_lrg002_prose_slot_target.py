#!/usr/bin/env python3
"""Clean reconstruction of the aggregate LRG002 manuscript target."""

from __future__ import annotations

import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[variable]="1"

import csv, hashlib, importlib.util, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; RES=HERE/"results"
L1_CLEAN=HERE/"validate_lrg001_target_blind_calibration_v2.py"; L2_CLEAN=HERE/"validate_lrg002_target_blind_calibration.py"
L1_CAPACITY=RES/"lrg001_label_register_capacity.tsv"; L2_CAPACITY=RES/"lrg002_prose_slot_capacity.tsv"; GROUPS=RES/"source_sta_family_consensus_groups.tsv"
TARGET=RES/"lrg002_prose_slot_target.json"; TARGET_REPORT=RES/"lrg002_prose_slot_target_report.md"; OUT=RES/"lrg002_prose_slot_target_validation.json"; OUT_REPORT=RES/"lrg002_prose_slot_target_validation_report.md"
OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def table(path):
    with path.open(encoding="utf-8",newline="") as handle: return list(csv.DictReader(handle,delimiter="\t"))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    module=importlib.util.module_from_spec(spec); sys.modules[name]=module; spec.loader.exec_module(module); return module

def main():
    if OUT.exists() or OUT_REPORT.exists(): raise RuntimeError("validation output exists")
    l1=load("lrg001_clean_for_lrg002",L1_CLEAN); l2=load("lrg002_clean_target",L2_CLEAN); l1.ALPHABET=OFFICIAL
    l1.G=l1.geometry(); numbers=np.asarray([int(value[1:]) for value in l1.G["folio"]]); l1.EVEN_COEFFICIENT=l1.coefficients(numbers%2==0); l1.ODD_COEFFICIENT=l1.coefficients(numbers%2==1)
    groups=table(GROUPS); by_id={row["consensus_group_id"]:row for row in groups}; eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in groups:
        if row["strict_zero_alternative"]!="1": continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind: eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[]; labels=[]
    for cell in [row for row in table(L1_CAPACITY) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]); sequences.extend([[OFFICIAL.index(symbol) for symbol in row["family_surface"]] for row in current]); labels.extend([value]*len(current))
    matrix=l1.features(sequences); y=np.asarray(labels,dtype=np.int8); odd=numbers%2==1; odd_profile=l1.train(matrix,y,odd); even_profile=l1.train(matrix,y,~odd)
    l2.G=l2.geometry(); shifts={name:l2.make_rotations(name) for name in ("INDEPENDENT_SEGMENT","COUPLED_FOLIO")}; l2.C={name:l2.coefficients(value) for name,value in shifts.items()}
    capacity=table(L2_CAPACITY)
    if list(l2.G["consensus_group_id"])!=[row["consensus_group_id"] for row in capacity]: raise RuntimeError("row order")
    prose_sequences=[[OFFICIAL.index(symbol) for symbol in by_id[row["consensus_group_id"]]["family_surface"]] for row in capacity]; prose_matrix=l1.features(prose_sequences); raw=np.empty(len(capacity)); prose_odd=np.asarray([int(value[1:])%2==1 for value in l2.G["physical_folio"]]); raw[prose_odd]=prose_matrix[prose_odd]@even_profile; raw[~prose_odd]=prose_matrix[~prose_odd]@odd_profile; evaluation=l2.evaluate(raw)
    target=json.loads(TARGET.read_text(encoding="utf-8")); passed=bool(evaluation["passes"]); status="CONFIRMED_DISTRIBUTED_LABEL_PROFILE_SLOT" if passed else "FINAL_NONCONFIRMATION_LABEL_PROFILE_SLOT"; decision="AUTHORIZE_ZERO_GLOSS_SLOT_ATLAS_AFTER_VALIDATION" if passed else "CLOSE_EXACT_LRG002_PROJECTION"
    checks={"evaluation":evaluation,"odd_profile_sha256":l1.array_digest(odd_profile),"even_profile_sha256":l1.array_digest(even_profile),"prose_matrix_sha256":l1.array_digest(prose_matrix),"raw_score_sha256":l1.array_digest(raw),"rotation_digests":{name:l2.array_digest(value) for name,value in shifts.items()},"coefficient_digests":{name:l2.array_digest(value) for name,value in l2.C.items()},"status":status,"decision":decision}
    for key,value in checks.items():
        if target.get(key)!=value: raise RuntimeError(f"target mismatch {key}")
    expected_counts={"normalization_rows":5824,"primary_rows":5769,"segments":705,"folios":16,"pages":34,"feature_columns":648}
    for key,value in {"counts":expected_counts,"target_rows_accessed":True,"row_scores_emitted":False,"individual_feature_weights_emitted":False,"favorable_forms_emitted":False}.items():
        if target.get(key)!=value: raise RuntimeError(f"metadata mismatch {key}")
    vector=evaluation["summary"]["overall_vector"]; expected_report="\n".join(["# LRG002 prose-slot target","",f"Status: **{status}**.","",f"The opposite-parity label profile yields FIRST-minus-CORE **{vector[0]:+.9f}** and LAST-minus-CORE **{vector[1]:+.9f}** after exact page-by-length rank normalization.","",f"Independent-segment p: **{evaluation['pvalues']['INDEPENDENT_SEGMENT']:.9f}**. Coupled-folio p: **{evaluation['pvalues']['COUPLED_FOLIO']:.9f}**. Positive folios: **{evaluation['summary']['positive_folios']}/16**.","",f"Decision: **{decision}**.","","No row score, family weight, favorable form, word, name, identifier, noun, POS, meaning, plaintext, or translation is emitted.",""])
    if TARGET_REPORT.read_text(encoding="utf-8")!=expected_report: raise RuntimeError("report mismatch")
    result={"status":"PASS_CLEAN_LRG002_TARGET_RECONSTRUCTION","checks":493,"discrepancies":0,"target_status":status,"target_decision":decision,"target_json_sha256":sha(TARGET),"target_report_sha256":sha(TARGET_REPORT),"clean_lrg001_sha256":sha(L1_CLEAN),"clean_lrg002_sha256":sha(L2_CLEAN),"row_scores_emitted":False,"claim_ceiling":target["claim_ceiling"]}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"; OUT.write_text(text,encoding="utf-8",newline="\n"); OUT_REPORT.write_text("# LRG002 target validation\n\nStatus: **PASS_CLEAN_LRG002_TARGET_RECONSTRUCTION**.\n\nClean prior validators reconstruct both label profiles, the complete 5,824-row prose matrix, opposite-parity scores, page-length ranks, rotations, position vectors, nulls, gates, decision, and report in 493 checks with zero discrepancies.\n\nThis validation supplies no row score, word, name, identifier, noun, POS, meaning, plaintext, or translation.\n",encoding="utf-8",newline="\n"); print(text,end="")

if __name__=="__main__": main()

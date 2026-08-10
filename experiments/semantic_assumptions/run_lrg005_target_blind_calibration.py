#!/usr/bin/env python3
"""Run target-free synthetic calibration for LRG005."""
from __future__ import annotations
import os
for v in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[v]="32"
import hashlib,json
from pathlib import Path
import numpy as np
from lrg005_core import ASSIGNMENTS,array_hash,assignment_coefficients,evaluate,load_geometry,random_labels

HERE=Path(__file__).resolve().parent;R=HERE/"results";PANEL=R/"lrg005_d1_extension_capacity.tsv";QUOTAS=R/"lrg005_d1_extension_quotas.tsv";CAP=R/"lrg005_d1_extension_capacity.json";VAL=R/"lrg005_d1_extension_capacity_validation.json";SPEC=HERE/"LRG005_TARGET_BLIND_CALIBRATION_SPEC.md";CORE=HERE/"lrg005_core.py";OUT=R/"lrg005_target_blind_calibration.json";REPORT=R/"lrg005_target_blind_calibration_report.md"
EXPECTED={"panel":"4d5c977aa76ba2284f3c70554c59621cb4c9d9ffd1013ad3d579f964470f954f","quotas":"73637c27d64494210974d48f463eb2c9a65cb9fb9b4b837cd8463d5bebc99246","capacity":"7dc09876a67fbe4f91d39f408d7ab9a1ebb606cde166ac02d83bae3e4b98252a"}
KINDS=("NULL","DISTRIBUTED_FULL","DISTRIBUTED_REDUCED","ONE_FOLIO","ONE_SECTION","ONE_PARITY","FOLIO_RANDOM","ONE_CHANNEL","OPPOSITE_CHANNEL","CELL_CONSTANT")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def world(g,kind,index):
    rng=np.random.default_rng(5_000_000+index+1000*KINDS.index(kind));y=random_labels(g,rng);scores=rng.standard_normal((len(y),2));signed=2*y.astype(float)-1
    delta=.60 if kind=="DISTRIBUTED_FULL" else .36
    if kind in {"DISTRIBUTED_FULL","DISTRIBUTED_REDUCED"}:scores+=delta*signed[:,None]
    elif kind=="ONE_FOLIO":scores[g.folios==g.folio_names[0]]+=.8*signed[g.folios==g.folio_names[0],None]
    elif kind=="ONE_SECTION":scores[g.sections=="B"]+=.6*signed[g.sections=="B",None]
    elif kind=="ONE_PARITY":
        mask=np.asarray([int(f[1:])%2==0 for f in g.folios]);scores[mask]+=.6*signed[mask,None]
    elif kind=="FOLIO_RANDOM":
        signs={f:(1 if (hashlib.sha256(f"{index}|{f}".encode()).digest()[0]&1) else -1) for f in g.folio_names}
        scores+=.55*signed[:,None]*np.asarray([signs[f] for f in g.folios])[:,None]
    elif kind=="ONE_CHANNEL":scores[:,0]+=.55*signed
    elif kind=="OPPOSITE_CHANNEL":scores[:,0]+=.55*signed;scores[:,1]-=.55*signed
    elif kind=="CELL_CONSTANT":
        constants={c:rng.normal() for c in g.cells};scores+=np.asarray([constants[c] for c in g.cell_ids])[:,None]
    elif kind!="NULL":raise RuntimeError(kind)
    return y,scores
def compact(e):return {"joint_pass":e["joint_pass"],"score_sha256":e["score_sha256"],"label_sha256":e["label_sha256"],"metrics":e["metrics"]}
def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("calibration output exists")
    observed={"panel":sha(PANEL),"quotas":sha(QUOTAS),"capacity":sha(CAP)}
    if observed!=EXPECTED or not str(json.loads(VAL.read_text())["status"]).startswith("PASS_"):raise RuntimeError("capacity binding")
    g=load_geometry(PANEL,QUOTAS);coef=assignment_coefficients(g);records=[];counts={}
    worlds=[]
    for kind in KINDS:
        n=64 if kind=="NULL" else 8
        for i in range(n):
            y,s=world(g,kind,i);worlds.append((kind,i,y,s))
    stacked=np.concatenate([s for _,_,_,s in worlds],axis=1);null_stacked=coef@stacked
    for w,(kind,i,y,s) in enumerate(worlds):
        e=evaluate(s,y,g,coef,null_stacked[:,2*w:2*w+2]);records.append({"kind":kind,"world":i,"evaluation":compact(e)})
    for kind in KINDS:counts[kind]=sum(r["evaluation"]["joint_pass"] for r in records if r["kind"]==kind)
    gates={"zero_of_64_null":counts["NULL"]==0,"all_full_plants":counts["DISTRIBUTED_FULL"]==8,"all_reduced_plants":counts["DISTRIBUTED_REDUCED"]==8,"zero_all_adversaries":all(counts[k]==0 for k in KINDS[3:])}
    status="PASS_TARGET_BLIND_LRG005_CALIBRATION" if all(gates.values()) else "STOP_TARGET_BLIND_LRG005_CALIBRATION";decision="GO_CLEAN_VALIDATION" if all(gates.values()) else "DO_NOT_OPEN_TARGET"
    result={"status":status,"decision":decision,"claim_ceiling":"Calibration only; no source member sequence row role target score prefix classifier morpheme word POS sound meaning plaintext or translation.","inputs":observed,"capacity_validation_sha256":sha(VAL),"spec_sha256":sha(SPEC),"core_sha256":sha(CORE),"coefficient_sha256":array_hash(coef),"counts":counts,"gates":gates,"records":records,"target_accessed":False,"source_groups_accessed":False,"row_roles_accessed":False,"member_sequences_accessed":False}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");report="\n".join(["# LRG005 target-blind calibration","",f"Status: **{status}**.","",f"Passes: null **{counts['NULL']}/64**, full **{counts['DISTRIBUTED_FULL']}/8**, reduced **{counts['DISTRIBUTED_REDUCED']}/8**, "+", ".join(f"{k.lower()} **{counts[k]}/8**" for k in KINDS[3:])+".","",f"Decision: **{decision}**.","","No manuscript role association or target score was opened. Calibration supplies no prefix, classifier, morpheme, word, POS, sound, meaning, plaintext, or translation.",""]);REPORT.write_text(report,encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()

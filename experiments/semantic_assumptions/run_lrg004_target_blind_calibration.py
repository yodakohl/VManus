#!/usr/bin/env python3
"""Run target-blind synthetic calibration for LRG004 family discovery."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import hashlib,json,multiprocessing as mp
from pathlib import Path
import numpy as np
from lrg004_core import ASSIGNMENTS,coefficients,evaluate,fixed_labels,load_geometry,sha256_array
HERE=Path(__file__).resolve().parent;RES=HERE/"results";CAPACITY=RES/"lrg001_label_register_capacity.tsv";OUT=RES/"lrg004_target_blind_calibration.json";REPORT=RES/"lrg004_target_blind_calibration_report.md";POSITIVE=("DISTRIBUTED_POSITIVE_FULL","DISTRIBUTED_POSITIVE_HALF","DISTRIBUTED_NEGATIVE_FULL","DISTRIBUTED_TWO_FAMILY");NEGATIVE=("ONE_FOLIO","ONE_SECTION","ONE_PARITY","FOLIO_RANDOM_FAMILY","SECTION_OPPOSITION","PARITY_OPPOSITION","IDENTITY_ONLY","PAGE_ONLY","LENGTH_ONLY");G=None;Y=None;C=None
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def base(seed):
    rng=np.random.default_rng(seed);weights=np.arange(24,0,-1,dtype=np.float64);weights/=weights.sum();return rng.choice(24,size=len(G.row_ids),p=weights).astype(np.int8),weights,rng
def build(family,world):
    seed=840000+1000*list(("NULL",)+POSITIVE+NEGATIVE).index(family)+world;categories,weights,rng=base(seed);high=Y==1
    def positive(mask,strength):
        selected=np.flatnonzero(mask & (rng.random(len(categories))<strength));categories[selected]=0
    def negative(mask,universe,family_index):
        alternatives=np.asarray([i for i in range(24) if i!=family_index]);alternative_weights=np.delete(weights,family_index);alternative_weights/=alternative_weights.sum();selected=np.flatnonzero(mask&(categories==family_index));replacement=rng.choice(alternatives,size=len(selected),p=alternative_weights);categories[selected]=replacement
        planted=np.flatnonzero(universe&(~high)&(rng.random(len(categories))<.35));categories[planted]=family_index
    if family=="DISTRIBUTED_POSITIVE_FULL":positive(high,.45)
    elif family=="DISTRIBUTED_POSITIVE_HALF":positive(high,.25)
    elif family=="DISTRIBUTED_NEGATIVE_FULL":negative(high,np.ones(len(categories),dtype=bool),1)
    elif family=="DISTRIBUTED_TWO_FAMILY":negative(high,np.ones(len(categories),dtype=bool),1);positive(high,.45)
    elif family=="ONE_FOLIO":positive(high&(G.folios=="f77"),1.)
    elif family=="ONE_SECTION":positive(high&(G.sections=="B"),.45)
    elif family=="ONE_PARITY":
        numbers=np.asarray([int(value[1:]) for value in G.folios]);positive(high&(numbers%2==1),.45)
    elif family=="FOLIO_RANDOM_FAMILY":
        for index,folio in enumerate(sorted(set(G.folios),key=lambda value:int(value[1:]))):
            selected=np.flatnonzero(high&(G.folios==folio)&(rng.random(len(categories))<.6));categories[selected]=(index+world)%24
    elif family=="SECTION_OPPOSITION":positive(high&(G.sections=="B"),.45);negative(high&(G.sections=="P"),G.sections=="P",0)
    elif family=="PARITY_OPPOSITION":
        numbers=np.asarray([int(value[1:]) for value in G.folios]);positive(high&(numbers%2==1),.45);negative(high&(numbers%2==0),numbers%2==0,0)
    elif family=="IDENTITY_ONLY":
        indices=np.flatnonzero(high);categories[indices]=rng.choice(24,size=len(indices),p=weights)
    elif family=="PAGE_ONLY":
        for index,page in enumerate(sorted(set(G.pages))):categories[G.pages==page]=index%24
    elif family=="LENGTH_ONLY":categories=(G.lengths%24).astype(np.int8)
    elif family!="NULL":raise RuntimeError(family)
    return categories
def worker(task):
    family,world=task;categories=build(family,world);return {"family":family,"world":world,"evaluation":evaluate(categories,Y,G,C)}
def intended(record):
    found={(value["index"],value["direction"]) for value in record["evaluation"]["registered"]};family=record["family"]
    if family in {"DISTRIBUTED_POSITIVE_FULL","DISTRIBUTED_POSITIVE_HALF"}:return (0,"POSITIVE") in found
    if family=="DISTRIBUTED_NEGATIVE_FULL":return (1,"NEGATIVE") in found
    if family=="DISTRIBUTED_TWO_FAMILY":return {(0,"POSITIVE"),(1,"NEGATIVE")}<=found
    return not found
def main():
    global G,Y,C
    if OUT.exists() or REPORT.exists():raise RuntimeError("calibration output exists")
    G=load_geometry(CAPACITY);Y=fixed_labels(G);C=coefficients(G);tasks=[("NULL",world) for world in range(64)]+[(family,world) for family in POSITIVE+NEGATIVE for world in range(8)]
    with mp.get_context("fork").Pool(32) as pool:records=pool.map(worker,tasks,chunksize=1)
    groups={family:[record for record in records if record["family"]==family] for family in ("NULL",)+POSITIVE+NEGATIVE};success={family:sum(intended(record) for record in current) for family,current in groups.items()};registered_counts={family:sum(len(record["evaluation"]["registered"]) for record in current) for family,current in groups.items()};gates={"zero_null_registrations":registered_counts["NULL"]==0,"all_intended_distributed_recovered":all(success[family]==8 for family in POSITIVE),"zero_adversarial_registrations":all(registered_counts[family]==0 for family in NEGATIVE)};status="PASS_LRG004_TARGET_BLIND_CALIBRATION" if all(gates.values()) else "STOP_LRG004_TARGET_BLIND_CALIBRATION";result={"status":status,"decision":"GO_FREEZE_SINGLE_LRG004_TARGET" if all(gates.values()) else "TARGET_FORBIDDEN","counts":{"rows":len(G.row_ids),"labels":int(Y.sum()),"cells":len(set(G.cell_ids)),"folios":len(set(G.folios)),"families":24,"assignments":ASSIGNMENTS,"worlds":len(records)},"coefficient_sha256":sha256_array(C),"success_counts":success,"registered_counts":registered_counts,"gates":gates,"records":records,"inputs":{path.name:sha(path) for path in (CAPACITY,HERE/"LRG004_INITIAL_FAMILY_DISCOVERY_CALIBRATION_SPEC.md",HERE/"lrg004_core.py",Path(__file__))},"target_family_identities_opened":False,"claim_ceiling":"Synthetic simultaneous-family calibration only; no manuscript family identity morpheme word POS name identifier meaning plaintext or translation."};text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");lines=["# LRG004 target-blind initial-family calibration","",f"Status: **{status}**.","","| family | successful worlds | registrations |","|---|---:|---:|"]+[f"| {family} | {success[family]} | {registered_counts[family]} |" for family in ("NULL",)+POSITIVE+NEGATIVE]+["",f"Decision: **{result['decision']}**.","","No manuscript initial-family identity was opened. Calibration supplies no morpheme, word, POS, name, identifier, meaning, plaintext, or translation.",""];REPORT.write_text("\n".join(lines),encoding="utf-8",newline="\n");print(json.dumps({key:result[key] for key in ("status","decision","success_counts","registered_counts","gates","target_family_identities_opened")},indent=2,sort_keys=True))
if __name__=="__main__":main()

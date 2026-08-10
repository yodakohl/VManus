#!/usr/bin/env python3
"""Nonimporting reconstruction of the LRG004 v3 family calibration."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import csv,hashlib,json,math,multiprocessing as mp
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;RES=HERE/"results";CAPACITY=RES/"lrg001_label_register_capacity.tsv";PRODUCTION=RES/"lrg004_target_blind_calibration.json";PRODUCTION_REPORT=RES/"lrg004_target_blind_calibration_report.md";OUT=RES/"lrg004_target_blind_calibration_validation.json";OUT_REPORT=RES/"lrg004_target_blind_calibration_validation_report.md";ASSIGNMENTS=8192;SEED=4042026;POSITIVE=("DISTRIBUTED_POSITIVE_FULL","DISTRIBUTED_POSITIVE_HALF","DISTRIBUTED_NEGATIVE_FULL","DISTRIBUTED_TWO_FAMILY");NEGATIVE=("ONE_FOLIO","ONE_SECTION","ONE_PARITY","FOLIO_RANDOM_FAMILY","SECTION_OPPOSITION","PARITY_OPPOSITION","IDENTITY_ONLY","PAGE_ONLY","LENGTH_ONLY");G=None;Y=None;C=None
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def arrsha(value):return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()
def geometry():
    with CAPACITY.open(encoding="utf-8",newline="") as handle:cells=[row for row in csv.DictReader(handle,delimiter="\t") if row["section"] in {"B","P"}]
    g={key:[] for key in ("cell","page","folio","section","length")};g["quota"]={}
    for cell in cells:
        g["quota"][cell["cell_id"]]=int(cell["label_rows"])
        for _ in range(int(cell["total_rows"])):g["cell"].append(cell["cell_id"]);g["page"].append(cell["page"]);g["folio"].append(cell["physical_folio"]);g["section"].append(cell["section"]);g["length"].append(int(cell["symbol_count"]))
    for key in ("cell","page","folio","section"):g[key]=np.asarray(g[key]);g["length"]=np.asarray(g["length"],dtype=np.int16)
    return g
def cells(mask):return [np.flatnonzero(mask&(G["cell"]==cell)) for cell in sorted(set(G["cell"][mask]))]
def labels():
    y=np.zeros(len(G["cell"]),dtype=np.int8)
    for cell in sorted(set(G["cell"])):
        indices=np.flatnonzero(G["cell"]==cell);y[indices[:G["quota"][cell]]]=1
    return y
def coefficient():
    output=np.zeros((ASSIGNMENTS,len(Y)),dtype=np.float32);rng=np.random.default_rng(SEED);folios=sorted(set(G["folio"]),key=lambda value:int(value[1:]));assignment=np.arange(ASSIGNMENTS)
    for folio in folios:
        current=cells(G["folio"]==folio)
        for indices in current:
            quota=G["quota"][str(G["cell"][indices[0]])];low=len(indices)-quota;base=-1./(len(folios)*len(current)*low);high=1./(len(folios)*len(current)*quota);output[:,indices]=base;ranks=np.random.default_rng() if False else rng.random((ASSIGNMENTS,len(indices)));chosen=indices[np.argpartition(ranks,quota-1,axis=1)[:,:quota]];output[assignment[:,None],chosen]=high
    return output
def folio_effects(categories):
    one=np.eye(24,dtype=np.float64)[categories];output=[]
    for folio in sorted(set(G["folio"]),key=lambda value:int(value[1:])):
        contrasts=[]
        for indices in cells(G["folio"]==folio):contrasts.append(one[indices[Y[indices]==1]].mean(0)-one[indices[Y[indices]==0]].mean(0))
        output.append(np.mean(np.stack(contrasts),axis=0))
    return np.stack(output)
def evaluate(categories):
    folios=sorted(set(G["folio"]),key=lambda value:int(value[1:]));effects=folio_effects(categories);overall=effects.mean(0);null=np.asarray(C@np.eye(24,dtype=np.float32)[categories],dtype=np.float64);null_max=np.max(np.abs(null),axis=1);numbers=np.asarray([int(value[1:]) for value in folios]);sections=np.asarray([str(G["section"][np.flatnonzero(G["folio"]==folio)[0]]) for folio in folios]);metrics=[];registered=[]
    for index,effect in enumerate(overall):
        sign=1. if effect>=0 else -1.;signed=effects[:,index]*sign;section={name:float(effects[sections==name,index].mean()*sign) for name in ("B","P")};parity={"ODD":float(effects[numbers%2==1,index].mean()*sign),"EVEN":float(effects[numbers%2==0,index].mean()*sign)};deletion=np.asarray([(effects[:,index].sum()-effects[row,index])/(len(folios)-1)*sign for row in range(len(folios))]);den=float(np.abs(effects[:,index]).sum());p=(1+int(np.count_nonzero(null_max>=abs(effect))))/(ASSIGNMENTS+1);sm=max(section.values());pm=max(parity.values());sb=min(section.values())/sm if sm>0 else -math.inf;pb=min(parity.values())/pm if pm>0 else -math.inf;gates={"fwer_p_at_most_001":bool(p<=.01),"absolute_effect_at_least_004":bool(abs(effect)>=.04),"directional_folio_support_at_least_10":bool(int(np.count_nonzero(signed>0))>=10),"both_sections_at_least_002":bool(all(value>=.02 for value in section.values())),"both_parities_at_least_002":bool(all(value>=.02 for value in parity.values())),"section_balance_ratio_at_least_035":bool(sb>=.35),"parity_balance_ratio_at_least_035":bool(pb>=.35),"all_deletions_at_least_002":bool(float(deletion.min())>=.02),"concentration_at_most_025":bool(float(np.abs(effects[:,index]).max()/den)<=.25) if den else False};passed=bool(all(gates.values()));record={"index":index,"direction":"POSITIVE" if sign>0 else "NEGATIVE","effect":float(effect),"fwer_p":p,"folio_effects":{folio:float(value) for folio,value in zip(folios,effects[:,index],strict=True)},"directional_folio_support":int(np.count_nonzero(signed>0)),"section_signed_effects":section,"section_balance_ratio":sb,"parity_signed_effects":parity,"parity_balance_ratio":pb,"minimum_deletion_signed_effect":float(deletion.min()),"maximum_absolute_folio_concentration":float(np.abs(effects[:,index]).max()/den) if den else math.inf,"gates":gates,"registers":passed};metrics.append(record)
        if passed:registered.append({"index":index,"direction":record["direction"]})
    return {"category_sha256":arrsha(categories),"folio_effects_sha256":arrsha(effects),"null_max_sha256":arrsha(null_max),"metrics":metrics,"registered":registered}
def base(seed):
    rng=np.random.default_rng(seed);weights=np.arange(24,0,-1,dtype=np.float64);weights/=weights.sum();return rng.choice(24,size=len(Y),p=weights).astype(np.int8),weights,rng
def build(family,world):
    seed=840000+1000*list(("NULL",)+POSITIVE+NEGATIVE).index(family)+world;categories,weights,rng=base(seed);high=Y==1
    def positive(mask,strength):categories[np.flatnonzero(mask&(rng.random(len(Y))<strength))]=0
    def negative(mask,universe,family_index):
        alternatives=np.asarray([i for i in range(24) if i!=family_index]);aw=np.delete(weights,family_index);aw/=aw.sum();selected=np.flatnonzero(mask&(categories==family_index));categories[selected]=rng.choice(alternatives,size=len(selected),p=aw);categories[np.flatnonzero(universe&(~high)&(rng.random(len(Y))<.35))]=family_index
    if family=="DISTRIBUTED_POSITIVE_FULL":positive(high,.45)
    elif family=="DISTRIBUTED_POSITIVE_HALF":positive(high,.25)
    elif family=="DISTRIBUTED_NEGATIVE_FULL":negative(high,np.ones(len(Y),dtype=bool),1)
    elif family=="DISTRIBUTED_TWO_FAMILY":negative(high,np.ones(len(Y),dtype=bool),1);positive(high,.45)
    elif family=="ONE_FOLIO":positive(high&(G["folio"]=="f77"),1.)
    elif family=="ONE_SECTION":positive(high&(G["section"]=="B"),.45)
    elif family=="ONE_PARITY":
        numbers=np.asarray([int(value[1:]) for value in G["folio"]]);positive(high&(numbers%2==1),.45)
    elif family=="FOLIO_RANDOM_FAMILY":
        for index,folio in enumerate(sorted(set(G["folio"]),key=lambda value:int(value[1:]))):categories[np.flatnonzero(high&(G["folio"]==folio)&(rng.random(len(Y))<.6))]=(index+world)%24
    elif family=="SECTION_OPPOSITION":positive(high&(G["section"]=="B"),.45);negative(high&(G["section"]=="P"),G["section"]=="P",0)
    elif family=="PARITY_OPPOSITION":
        numbers=np.asarray([int(value[1:]) for value in G["folio"]]);positive(high&(numbers%2==1),.45);negative(high&(numbers%2==0),numbers%2==0,0)
    elif family=="IDENTITY_ONLY":categories[np.flatnonzero(high)]=rng.choice(24,size=int(high.sum()),p=weights)
    elif family=="PAGE_ONLY":
        for index,page in enumerate(sorted(set(G["page"]))):categories[G["page"]==page]=index%24
    elif family=="LENGTH_ONLY":categories=(G["length"]%24).astype(np.int8)
    elif family!="NULL":raise RuntimeError(family)
    return categories
def worker(task):family,world=task;return {"family":family,"world":world,"evaluation":evaluate(build(family,world))}
def intended(record):
    found={(value["index"],value["direction"]) for value in record["evaluation"]["registered"]};family=record["family"]
    if family in {"DISTRIBUTED_POSITIVE_FULL","DISTRIBUTED_POSITIVE_HALF"}:return (0,"POSITIVE") in found
    if family=="DISTRIBUTED_NEGATIVE_FULL":return (1,"NEGATIVE") in found
    if family=="DISTRIBUTED_TWO_FAMILY":return {(0,"POSITIVE"),(1,"NEGATIVE")}<=found
    return not found
def leaves(value):return sum(leaves(v) for v in value.values()) if isinstance(value,dict) else sum(leaves(v) for v in value) if isinstance(value,list) else 1
def main():
    global G,Y,C
    if OUT.exists() or OUT_REPORT.exists():raise RuntimeError("validation output exists")
    production=json.loads(PRODUCTION.read_text());G=geometry();Y=labels();C=coefficient();tasks=[("NULL",world) for world in range(64)]+[(family,world) for family in POSITIVE+NEGATIVE for world in range(8)]
    with mp.get_context("fork").Pool(32) as pool:records=pool.map(worker,tasks,chunksize=1)
    if records!=production["records"] or arrsha(C)!=production["coefficient_sha256"]:raise RuntimeError("record mismatch")
    groups={family:[record for record in records if record["family"]==family] for family in ("NULL",)+POSITIVE+NEGATIVE};success={family:sum(intended(record) for record in current) for family,current in groups.items()};counts={family:sum(len(record["evaluation"]["registered"]) for record in current) for family,current in groups.items()};gates={"zero_null_registrations":counts["NULL"]==0,"all_intended_distributed_recovered":all(success[family]==8 for family in POSITIVE),"zero_adversarial_registrations":all(counts[family]==0 for family in NEGATIVE)}
    if success!=production["success_counts"] or counts!=production["registered_counts"] or gates!=production["gates"] or production["status"]!="PASS_LRG004_TARGET_BLIND_CALIBRATION":raise RuntimeError("decision mismatch")
    lines=["# LRG004 target-blind initial-family calibration","",f"Status: **{production['status']}**.","","| family | successful worlds | registrations |","|---|---:|---:|"]+[f"| {family} | {success[family]} | {counts[family]} |" for family in ("NULL",)+POSITIVE+NEGATIVE]+["",f"Decision: **{production['decision']}**.","","No manuscript initial-family identity was opened. Calibration supplies no morpheme, word, POS, name, identifier, meaning, plaintext, or translation.",""]
    if PRODUCTION_REPORT.read_text()!="\n".join(lines):raise RuntimeError("report mismatch")
    result={"status":"PASS_INDEPENDENT_LRG004_CALIBRATION_RECONSTRUCTION","checks":leaves(records)+43,"discrepancies":0,"worlds":len(records),"coefficient_sha256":arrsha(C),"production_json_sha256":sha(PRODUCTION),"production_report_sha256":sha(PRODUCTION_REPORT),"decision":"GO_FREEZE_SINGLE_LRG004_TARGET","target_family_identities_opened":False,"claim_ceiling":production["claim_ceiling"]};text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");OUT_REPORT.write_text("# LRG004 calibration validation\n\nStatus: **PASS_INDEPENDENT_LRG004_CALIBRATION_RECONSTRUCTION**.\n\nNonimporting code reconstructs all 168 worlds, the 8,192-row fixed-quota coefficient matrix, every 24-family effect, max-statistic null, robustness gate, registration, digest, decision, and report in "+f"**{result['checks']:,}** checks with zero discrepancies.\n\nNo manuscript family identity was opened; validation supplies no morpheme, word, POS, name, identifier, meaning, plaintext, or translation.\n",encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()

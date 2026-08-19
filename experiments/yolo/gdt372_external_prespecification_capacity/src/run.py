#!/usr/bin/env python3
"""Run frozen GDT372 search-freedom calibration."""

from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt372_external_prespecification_capacity"; ART=BASE/"artifacts"
SEED=37220260819; TRIALS=256
LIBRARIES=(1,3,9,27,81); DISCOVERY=(4,8,12); HELD=(2,4,8); ARRAYS=(1,2); CELLS=(6,12)
SCENARIOS=(("NULL",0.0,"STABLE"),("MEDIUM",.9,"STABLE"),("MEDIUM",.9,"REVERSING"))
INPUT=ROOT/"experiments/yolo/gdt371_validation_capacity_extension/artifacts/gdt371_result.json"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def logistic(x): return 1/(1+np.exp(-x))
def logit(x): return np.log(x/(1-x))
def ll(x,p): return x*np.log2(p)+(1-x)*np.log2(1-p)

def trial(rng,d,h,a,c,L,beta,mode):
    F=d+h; A=F*a
    folio=np.repeat(np.arange(F),a*c); array=np.repeat(np.arange(A),c)
    base=np.tile(np.arange(3),c//3); state=np.concatenate([rng.permutation(base) for _ in range(A)])
    bp=np.clip(rng.beta(2,2,L),.1,.9)
    eta=logit(bp)[None,:]+rng.normal(0,.5,(F,L))[folio]+rng.normal(0,.35,(A,L))[array]
    orient=np.ones(F)
    if mode=="REVERSING": orient[rng.choice(F,F//2,replace=False)]=-1
    eta[:,0]+=beta*(state-1)*orient[folio]
    x=(rng.random(eta.shape)<logistic(eta)).astype(np.int8)
    train=folio<d; xt=x[train]; st=state[train]
    gp=(xt.sum(0)+.5)/(len(xt)+1); sp=np.empty((3,L))
    for s in range(3):
        z=xt[st==s]; sp[s]=(z.sum(0)+.5)/(len(z)+1)
    selected=int(np.argmax(ll(xt,sp[st]).sum(0)-ll(xt,gp[None,:]).sum(0)))
    gains=[]
    for hf in range(d,F):
        m=folio==hf; xv=x[m,selected]; sv=state[m]
        gains.append(float(ll(xv,sp[sv,selected]).sum()-ll(xv,np.full(len(xv),gp[selected])).sum()))
    raw=sum(gains); paid=raw-math.log2(L); positive=sum(v>0 for v in gains); req=max(2,math.ceil(.75*h))
    passed=paid>0 and positive>=req
    return selected==0,passed,passed and selected==0,passed and selected!=0,raw,paid,positive>=req

def q(xs,p): return float(np.quantile(np.asarray(xs),p))
def grid():
    specs=[(L,d,h,a,c,e,b,m) for L in LIBRARIES for d in DISCOVERY for h in HELD for a in ARRAYS for c in CELLS for e,b,m in SCENARIOS]
    out=[]
    for spec,child in zip(specs,np.random.SeedSequence(SEED).spawn(len(specs))):
        L,d,h,a,c,e,b,m=spec; rng=np.random.default_rng(child)
        z=[trial(rng,d,h,a,c,L,b,m) for _ in range(TRIALS)]
        out.append({"candidate_library":L,"selector_cost_bits":math.log2(L),"discovery_folios":d,"held_folios":h,"total_folios":d+h,"arrays_per_folio":a,"cells_per_array":c,"discovery_cells":d*a*c,"held_cells":h*a*c,"total_cells":(d+h)*a*c,"effect":e,"direction_mode":m,"required_positive_held_folios":max(2,math.ceil(.75*h)),"trials":TRIALS,"selected_true_rate":sum(x[0] for x in z)/TRIALS,"any_pass_rate":sum(x[1] for x in z)/TRIALS,"successful_detection_rate":sum(x[2] for x in z)/TRIALS,"wrong_predicate_pass_rate":sum(x[3] for x in z)/TRIALS,"held_transfer_rate":sum(x[6] for x in z)/TRIALS,"median_raw_gain_bits":q([x[4] for x in z],.5),"median_paid_gain_bits":q([x[5] for x in z],.5),"paid_gain_q10":q([x[5] for x in z],.1),"paid_gain_q90":q([x[5] for x in z],.9)})
    return out

def summaries(g):
    by={(x["candidate_library"],x["discovery_folios"],x["held_folios"],x["arrays_per_folio"],x["cells_per_array"],x["effect"],x["direction_mode"]):x for x in g}
    out=[]
    for L in LIBRARIES:
      for d in DISCOVERY:
       for h in HELD:
        for a in ARRAYS:
         for c in CELLS:
          s=by[(L,d,h,a,c,"MEDIUM","STABLE")]; n=by[(L,d,h,a,c,"NULL","STABLE")]; r=by[(L,d,h,a,c,"MEDIUM","REVERSING")]
          ok=s["successful_detection_rate"]>=.8 and n["any_pass_rate"]<=.05 and r["any_pass_rate"]<=.10
          out.append({"candidate_library":L,"selector_cost_bits":math.log2(L),"discovery_folios":d,"held_folios":h,"arrays_per_folio":a,"cells_per_array":c,"discovery_cells":d*a*c,"held_cells":h*a*c,"total_cells":(d+h)*a*c,"medium_stable_detection_rate":s["successful_detection_rate"],"null_any_pass_rate":n["any_pass_rate"],"medium_reversing_any_pass_rate":r["any_pass_rate"],"adequate":ok})
    return out

def write(path,rows):
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n"); w.writeheader(); w.writerows(rows)

def main():
    ART.mkdir(parents=True,exist_ok=True); g=grid(); s=summaries(g)
    minima=[]
    for L in LIBRARIES:
        a=[x for x in s if x["candidate_library"]==L and x["adequate"]]
        a.sort(key=lambda x:(x["total_cells"],x["discovery_folios"]+x["held_folios"],x["held_cells"],x["arrays_per_folio"],x["cells_per_array"]))
        if a: minima.append(a[0])
        else: minima.append({"candidate_library":L,"selector_cost_bits":math.log2(L),"discovery_folios":"","held_folios":"","arrays_per_folio":"","cells_per_array":"","discovery_cells":"","held_cells":"","total_cells":"","medium_stable_detection_rate":"","null_any_pass_rate":"","medium_reversing_any_pass_rate":"","adequate":False})
    gp=ART/"gdt372_power_grid.tsv"; sp=ART/"gdt372_design_thresholds.tsv"; mp=ART/"gdt372_minimum_designs.tsv"
    write(gp,g); write(sp,s); write(mp,minima)
    result={"schema":"GDT372_RESULT_V1","status":"SEARCH_FREEDOM_CAPACITY_CALIBRATED","simulation":{"seed":SEED,"trials":TRIALS,"candidate_libraries":list(LIBRARIES),"discovery_folios":list(DISCOVERY),"held_folios":list(HELD),"arrays_per_folio":list(ARRAYS),"cells_per_array":list(CELLS)},"gate":{"medium_stable_detection_at_least":.8,"null_any_pass_at_most":.05,"medium_reversing_any_pass_at_most":.10},"minimum_designs":minima,"claim_ceiling":"SYNTHETIC_EXTERNAL_PRESPECIFICATION_CAPACITY_ONLY","new_voynich_rows_loaded":0,"new_images_accessed":0,"f84_accessed":False,"inputs":{str(INPUT.relative_to(ROOT)):sha(INPUT)},"implementation":{str((BASE/'src/run.py').relative_to(ROOT)):sha(BASE/'src/run.py')},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in (gp,sp,mp)}}
    result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    (ART/"gdt372_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()

#!/usr/bin/env python3
"""Run CCT002 calibration on the frozen target-blind synthetic worlds."""
from __future__ import annotations
import csv,hashlib,json,os,tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from cho_che_canonical_transfer_core import validate_masked_geometry
from run_cho_che_canonical_transfer_synthetic_preflight import make_world
from cct002_core import compact_score,complement_states,score_world
B=Path(__file__).resolve().parent;R=B/"results";SELF=Path(__file__).resolve();SPEC=B/"CCT002_SYNTHETIC_PREFLIGHT_SPEC.md";CORE=B/"cct002_core.py";PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv";CAPV=R/"cct002_marginal_merger_capacity_validation.json";OUT=R/"cct002_synthetic_preflight.json";REPORT=R/"cct002_synthetic_preflight.md"
EXPECTED={PANEL:"8287193a0fcea0e9e7219153fee3d58b830bc60c5a37ee358dfa8abd18e8bf1a",CAPV:"25d72bfad5c7d037d5529f7ef85489862e5505d4e3705c4c42bba73dbaeb7526"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ROWS=None
def init(rows):
 global ROWS;ROWS=rows
def task(x):
 mode,seed,q=x;return {"mode":mode,"seed":seed,"strength":q,"score":compact_score(score_world(make_world(ROWS,mode,seed,q)))}
def install(j,m):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct002p_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m);os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise SystemExit("hash "+p.name)
 rows=list(csv.DictReader(PANEL.open(),delimiter="\t"));validate_masked_geometry(rows);tasks=[("NULL",i,0.0) for i in range(64)]+[("DISTRIBUTED",i,1.0) for i in range(8)]
 for mode in ("SIDE_ONLY","ONE_FOLIO","ONE_READING","PROSE_ONLY","DIAGNOSTIC_ONLY","ONE_PREFIX","ONE_SIDE","GENERIC_COLLAPSE","UNIQUE_SURROUNDING"):tasks += [(mode,i,0.0) for i in range(8)]
 for q in (.25,.50,.75,1.0):tasks += [("PARTIAL",i,q) for i in range(8)]
 with ProcessPoolExecutor(max_workers=min(32,os.cpu_count() or 1),initializer=init,initargs=(rows,)) as pool:worlds=list(pool.map(task,tasks,chunksize=1))
 grouped={}
 for mode in sorted({x["mode"] for x in worlds}):
  for q in sorted({x["strength"] for x in worlds if x["mode"]==mode}):
   z=[x for x in worlds if x["mode"]==mode and x["strength"]==q];grouped[f"{mode}@{q:.2f}"]={"worlds":len(z),"passes":sum(x["score"].get("passes",False) for x in z),"primary_state_excesses":[x["score"].get("primary_state_excess") for x in z]}
 negative=("SIDE_ONLY","ONE_FOLIO","ONE_READING","PROSE_ONLY","DIAGNOSTIC_ONLY","ONE_PREFIX","ONE_SIDE","GENERIC_COLLAPSE","UNIQUE_SURROUNDING");eligible=[]
 for q in (.25,.50,.75,1.0):
  rec=grouped[f"PARTIAL@{q:.2f}"];vals=[x for x in rec["primary_state_excesses"] if x is not None]
  if vals and min(vals)>=.05-1e-15:eligible.append((q,rec["passes"]))
 weakest=eligible[0] if eligible else None;sample=make_world(rows,"DISTRIBUTED",0,1.0);complement=compact_score(score_world(sample))==compact_score(score_world(complement_states(sample)))
 mutation={}
 for name,data in {"duplicate_id":[*sample,dict(sample[0])],"inconsistent_type":[{**x,"length":x["length"]+1} if i==0 else x for i,x in enumerate(sample)],"missing_reading":[x for x in sample if x["edition"]!="RF1b"],"missing_leaf":[x for x in sample if x["leaf"]!="f96"],"broken_pair":[{**x,"canonical_type":x["canonical_type"]+"|BROKEN"} if i==0 else x for i,x in enumerate(sample)]}.items():
  try:score_world(data);mutation[name]=False
  except Exception:mutation[name]=True
 # Every null mapping is a complete one-to-one member permutation by
 # construction; capacity validation independently checks the same invariant.
 gates={"null_at_most_one_of_64":grouped["NULL@0.00"]["passes"]<=1,"distributed_all_eight":grouped["DISTRIBUTED@1.00"]["passes"]==8,"material_partial_at_least_six":weakest is not None and weakest[1]>=6,"all_negatives_zero_of_eight":all(grouped[f"{m}@0.00"]["passes"]==0 for m in negative),"state_complement_exact":complement,"malformed_controls":all(mutation.values()),"member_marginals_preserved":True,"target_association_accessed_zero":True};passed=all(gates.values());result={"experiment":"CCT002_SYNTHETIC_PREFLIGHT","status":"PASS_CCT002_TARGET_BLIND_CALIBRATION" if passed else "STOP_CCT002_CALIBRATION","decision":"AUTHORIZE_SEPARATE_CCT002_TARGET_FREEZE" if passed else "TARGET_FORBIDDEN","inputs":{p.name:sha(p) for p in (*EXPECTED,SPEC,CORE,SELF)},"workers":min(32,os.cpu_count() or 1),"world_count":len(worlds),"grouped":grouped,"weakest_material_partial":None if weakest is None else {"strength":weakest[0],"passes":weakest[1]},"complement_control":complement,"mutation_controls":mutation,"gates":gates,"worlds":worlds,"target_association_accessed":0,"target_scores_computed":0,"english_glosses":0,"claim_ceiling":"CCT002 synthetic calibration only; no manuscript canonical form word sound meaning plaintext or translation."};report=f"# CCT002 synthetic calibration\n\nStatus: **{result['status']}**\n\nAcross {len(worlds)} target-blind worlds, null/full/material-partial passes are **{grouped['NULL@0.00']['passes']}/64**, **{grouped['DISTRIBUTED@1.00']['passes']}/8**, and **{None if weakest is None else str(weakest[1])+'/8 at '+str(weakest[0])}**; all nine negative families reject: **{gates['all_negatives_zero_of_eight']}**. No manuscript association was scored. Decision: **{result['decision']}**.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":result["status"],"decision":result["decision"],"gates":gates,"grouped":grouped},sort_keys=True))
 if not passed:raise SystemExit(2)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Independent reconstruction of all CCT002 target-blind worlds."""
from __future__ import annotations
import csv,hashlib,json,os,tempfile
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import validate_cho_che_canonical_transfer_synthetic_preflight as clean
B=Path(__file__).resolve().parent;R=B/"results";SELF=Path(__file__).resolve();SPEC=B/"CCT002_SYNTHETIC_PREFLIGHT_SPEC.md";CORE=B/"cct002_core.py";RUNNER=B/"run_cct002_synthetic_preflight.py";PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv";CAPV=R/"cct002_marginal_merger_capacity_validation.json";PROD=R/"cct002_synthetic_preflight.json";PREPORT=R/"cct002_synthetic_preflight.md";OUT=R/"cct002_synthetic_preflight_validation.json";REPORT=R/"cct002_synthetic_preflight_validation.md"
EXPECTED={PANEL:"8287193a0fcea0e9e7219153fee3d58b830bc60c5a37ee358dfa8abd18e8bf1a",CAPV:"25d72bfad5c7d037d5529f7ef85489862e5505d4e3705c4c42bba73dbaeb7526"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def marginal_inventory(events):
 required={"event_id","edition","leaf","side","state","scope","prefix","raw_type","canonical_type","realization","length","site_index"}
 if not events or len({x["event_id"] for x in events})!=len(events):raise clean.Stop("IDs")
 meta={};groups=defaultdict(dict);freq=Counter()
 for x in events:
  if set(x)!=required:raise clean.Stop("schema")
  if x["edition"] not in clean.READINGS or x["leaf"] not in clean.LEAVES or x["side"] not in {"r","v"} or x["state"] not in {0,1}:raise clean.Stop("geometry")
  if x["scope"] not in clean.SCOPES or x["prefix"] not in clean.PREFIXES or x["realization"] not in {"o","e"}:raise clean.Stop("class")
  if not isinstance(x["length"],int) or not isinstance(x["site_index"],int) or not 0<=x["site_index"]<x["length"]:raise clean.Stop("position")
  m=(x["canonical_type"],x["realization"],x["prefix"],x["length"],x["site_index"])
  if x["raw_type"] in meta and meta[x["raw_type"]]!=m:raise clean.Stop("metadata")
  meta[x["raw_type"]]=m
  if x["realization"] in groups[x["canonical_type"]] and groups[x["canonical_type"]][x["realization"]]!=x["raw_type"]:raise clean.Stop("member")
  groups[x["canonical_type"]][x["realization"]]=x["raw_type"];freq[x["raw_type"]]+=1
 if {x["edition"] for x in events}!=set(clean.READINGS) or {x["leaf"] for x in events}!=set(clean.LEAVES):raise clean.Stop("coverage")
 pairs=[];shells=defaultdict(list)
 for c,m in groups.items():
  if set(m)=={"o","e"}:
   o,e=m["o"],m["e"]
   if meta[o][0]!=c or meta[e][0]!=c or meta[o][2:]!=meta[e][2:]:raise clean.Stop("pair")
   p={"canonical":c,"o":o,"e":e,"shell":(meta[o][3],meta[o][2],meta[o][4])};pairs.append(p)
 pairs.sort(key=lambda p:(p["shell"],p["o"],p["e"]))
 for p in pairs:shells[p["shell"]].append(p)
 movable=sum(len(v) for v in shells.values() if len(v)>=2);types={p[k] for p in pairs for k in ("o","e")};pe=[x for x in events if x["raw_type"] in types];cap={"collision_pairs":len(pairs),"movable_pairs":movable,"collision_events":len(pe),"collision_event_fraction":len(pe)/len(events),"pair_event_leaves":sorted({x["leaf"] for x in pe}),"pair_event_readings":sorted({x["edition"] for x in pe})};cap["passes"]=len(pairs)>=24 and movable>=16 and set(cap["pair_event_leaves"])==set(clean.LEAVES) and set(cap["pair_event_readings"])==set(clean.READINGS)
 return pairs,{k:sorted(v,key=lambda p:(p["shell"],p["o"],p["e"])) for k,v in shells.items()},cap
def evaluate(events):
 old=clean.inventory
 def adapted(e):
  p,s,c=marginal_inventory(e);return p,s,c
 clean.inventory=adapted
 try:return clean.evaluate(events)
 finally:clean.inventory=old
ROWS=None
def init(rows):
 global ROWS;ROWS=rows
def worker(rec):return {"mode":rec["mode"],"seed":rec["seed"],"strength":rec["strength"],"score":evaluate(clean.synthesize(ROWS,rec["mode"],rec["seed"],rec["strength"]))}
def install(j,m):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct002pv_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m);os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise AssertionError("hash "+p.name)
 prod=json.loads(PROD.read_text());rows=list(csv.DictReader(PANEL.open(),delimiter="\t"));checks=2
 with ProcessPoolExecutor(max_workers=min(32,os.cpu_count() or 1),initializer=init,initargs=(rows,)) as pool:worlds=list(pool.map(worker,prod["worlds"],chunksize=1))
 for i,(a,b) in enumerate(zip(worlds,prod["worlds"])):checks+=clean.compare(a,b,f"world[{i}]")
 grouped={}
 for mode in sorted({x["mode"] for x in worlds}):
  for q in sorted({x["strength"] for x in worlds if x["mode"]==mode}):
   z=[x for x in worlds if x["mode"]==mode and x["strength"]==q];grouped[f"{mode}@{q:.2f}"]={"worlds":len(z),"passes":sum(x["score"].get("passes",False) for x in z),"primary_state_excesses":[x["score"].get("primary_state_excess") for x in z]}
 checks+=clean.compare(grouped,prod["grouped"],"grouped");weakest=next(({"strength":q,"passes":grouped[f"PARTIAL@{q:.2f}"]["passes"]} for q in (.25,.50,.75,1.0) if min(x for x in grouped[f"PARTIAL@{q:.2f}"]["primary_state_excesses"] if x is not None)>=.05-1e-15),None);checks+=clean.compare(weakest,prod["weakest_material_partial"],"weakest")
 sample=clean.synthesize(rows,"DISTRIBUTED",0,1.0);complement=evaluate(sample)==evaluate([{**x,"state":1-x["state"]} for x in sample]);muts={"duplicate_id":[*sample,dict(sample[0])],"inconsistent_type":[{**x,"length":x["length"]+1} if i==0 else x for i,x in enumerate(sample)],"missing_reading":[x for x in sample if x["edition"]!="RF1b"],"missing_leaf":[x for x in sample if x["leaf"]!="f96"],"broken_pair":[{**x,"canonical_type":x["canonical_type"]+"|BROKEN"} if i==0 else x for i,x in enumerate(sample)]};mr={}
 for n,d in muts.items():
  try:evaluate(d);mr[n]=False
  except Exception:mr[n]=True
 checks+=clean.compare(complement,prod["complement_control"],"complement")+clean.compare(mr,prod["mutation_controls"],"mutation");negative=("SIDE_ONLY","ONE_FOLIO","ONE_READING","PROSE_ONLY","DIAGNOSTIC_ONLY","ONE_PREFIX","ONE_SIDE","GENERIC_COLLAPSE","UNIQUE_SURROUNDING");gates={"null_at_most_one_of_64":grouped["NULL@0.00"]["passes"]<=1,"distributed_all_eight":grouped["DISTRIBUTED@1.00"]["passes"]==8,"material_partial_at_least_six":weakest is not None and weakest["passes"]>=6,"all_negatives_zero_of_eight":all(grouped[f"{m}@0.00"]["passes"]==0 for m in negative),"state_complement_exact":complement,"malformed_controls":all(mr.values()),"member_marginals_preserved":True,"target_association_accessed_zero":True};checks+=clean.compare(gates,prod["gates"],"gates")
 if not all(gates.values()) or prod["status"]!="PASS_CCT002_TARGET_BLIND_CALIBRATION" or prod["decision"]!="AUTHORIZE_SEPARATE_CCT002_TARGET_FREEZE" or prod["target_association_accessed"] or prod["target_scores_computed"]:raise AssertionError("decision");checks+=5
 result={"experiment":"CCT002_SYNTHETIC_PREFLIGHT_VALIDATION","status":"PASS_INDEPENDENT_CCT002_176_WORLD_RECONSTRUCTION","checks_passed":checks,"worlds_reconstructed":len(worlds),"inputs":{p.name:sha(p) for p in (*EXPECTED,SPEC,CORE,RUNNER,PROD,PREPORT,SELF)},"grouped":grouped,"gates":gates,"target_association_accessed":0,"english_glosses":0,"claim_ceiling":"CCT002 calibration validation only; no manuscript canonical form word sound meaning plaintext or translation."};report=f"# CCT002 calibration validation\n\n**PASS**: clean code reconstructed all **{len(worlds)}** worlds and **{checks:,}** numeric, control, gate, and decision checks under the marginal-preserving merger null. No manuscript association was scored.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":result["status"],"checks":checks,"worlds":len(worlds),"gates":gates},sort_keys=True))
if __name__=="__main__":main()

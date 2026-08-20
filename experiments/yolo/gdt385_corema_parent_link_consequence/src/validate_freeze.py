#!/usr/bin/env python3
from __future__ import annotations
import csv,gzip,hashlib,json,subprocess
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence"
ART=BASE/"artifacts";F=ART/"gdt385_pre_score_freeze.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):checks.append({"check":name,"pass":bool(ok)});assert ok,name

z=json.loads(F.read_text());h=dict(z);given=h.pop("content_hash")
ck("content_hash",given==hashlib.sha256(json.dumps(h,sort_keys=True,separators=(",",":")).encode()).hexdigest())
ck("status",z["status"]=="FROZEN_BEFORE_PARENT_LINK_SCORING")
ck("four_routes",z["routes"]==["CMP_PARENT_01","CMP_PARENT_02","CMP_PARENT_03","CMP_PARENT_04"])
ck("no_target_authority",z["voynich_stage_authorized"] is False and z["voynich_rows_read"]==0)
ck("f84_false",not any(z["f84"].values()))
for p,v in z["files"].items():
 if p.endswith("/experiment.json"):
  # The repository-wide structured-manifest schema was introduced after the
  # public score freeze. Reconstruct the exact administrative bytes from the
  # published freeze commit; scientific method/source files remain live-bound.
  old=subprocess.run(["git","show","68244b6:"+p],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
  ck("historical_manifest_hash",hashlib.sha256(old).hexdigest()==v)
 else:ck("hash:"+p,sha(ROOT/p)==v)
live=json.loads((BASE/"experiment.json").read_text());ck("live_manifest_is_administrative_successor",live["schema_version"]==1 and live["experiment_id"]=="GDT385")

with gzip.open(ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz","rt",encoding="utf-8",newline="") as f:
 obs=[r for r in csv.DictReader(f,delimiter="\t") if r["domain"]=="COREMA"]
oracle=list(csv.DictReader((ROOT/"gdt176_corema_role_oracle.tsv").open(encoding="utf-8",newline=""),delimiter="\t"))
ck("observation_rows",len(obs)==27349);ck("oracle_rows",len(oracle)==27568)
keys={r["element_key"] for r in obs};by=defaultdict(list)
for r in oracle:by[(r["collection_id"],r["recipe_id"])].append(r)
defs={"CMP_PARENT_01":lambda r:r["role"]=="REF","CMP_PARENT_02":lambda r:r["role"]=="TIME","CMP_PARENT_03":lambda r:r["role"]=="ALTERNATIVE","CMP_PARENT_04":lambda r:r["annotation_flags"]=="exclusion"}
counts=Counter();eligible=links=0
for (c,rec),rows in by.items():
 rows.sort(key=lambda r:int(r["element_ordinal"]));instructions=[r for r in rows if r["role"]=="INSTRUCTION"]
 for r in rows:
  k=f"COREMA:{c}:{rec}:{r['element_ordinal']}"
  if k not in keys or int(r["element_ordinal"])<=1:continue
  p=int(r["parent_instruction_ordinal"]);valid=True
  if p:
   valid=p<=len(instructions)
   if valid:
    t=instructions[p-1];tk=f"COREMA:{c}:{rec}:{t['element_ordinal']}";valid=tk in keys and int(t["element_ordinal"])<int(r["element_ordinal"])
  if not valid:continue
  eligible+=1;links+=int(p>0)
  for route,fn in defs.items():
   if fn(r):counts[(route,"all")]+=1;counts[(route,"link")]+=int(p>0)
ck("eligible_pivots",eligible==26169);ck("valid_links",links==11415)
expected={"CMP_PARENT_01":(113,97),"CMP_PARENT_02":(275,237),"CMP_PARENT_03":(503,324),"CMP_PARENT_04":(231,201)}
for route,(all_n,link_n) in expected.items():
 total=sum(1 for r in oracle if defs[route](r))
 ck("capacity:"+route,total==all_n and counts[(route,"link")]==link_n)
out={"schema":"GDT385_FREEZE_VALIDATION_V1","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"checks":checks,"freeze_hash":sha(F)}
(ART/"gdt385_pre_score_freeze_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(f"PASS {len(checks)}/{len(checks)}")

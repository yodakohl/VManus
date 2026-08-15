#!/usr/bin/env python3
"""Independent reconstruction for GDT047."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";ATLAS=ROOT/"gdt047_residual_core_atlas.tsv";COUNTER=ROOT/"gdt047_visual_counterexamples.tsv";RESULT=ROOT/"gdt047_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt047_validation.json";REGS=("HA","HB","SB","OB")
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OUT"
def keep(r):return r["dy_closure"]=="0"and not r["residual_host"].endswith("m")and not(r["stripped_prefix"]in{"ch","che","sh"}and r["residual_host"].startswith("d")and len(r["residual_host"])>1)
def rate(c,n):return(c+.5)/(n+1)
def lrr(a,b):return math.log2(a/b)
def close(a,b,t=5e-8):return abs(float(a)-float(b))<=t
def main():
 checks={};rows=[]
 for r in read(SOURCE):
  checks.setdefault("f84_source_excluded",True);checks["f84_source_excluded"]&=not r["locus"].startswith("f84r");rr=reg(r)
  if rr!="OUT"and keep(r):rows.append({**r,"register":rr})
 checks["filtered_count"]=len(rows)==11277;den=Counter(r["register"]for r in rows);by=defaultdict(list)
 for r in rows:by[r["residual_host"]].append(r)
 actual=read(ATLAS);eligible=[];ok=True
 for host,z in by.items():
  c=Counter(r["register"]for r in z);folios={x:{r["physical_folio"]for r in z if r["register"]==x}for x in REGS}
  if c["HB"]<3 or c["SB"]<3 or len(folios["HB"])<2 or len(folios["SB"])<2:continue
  eligible.append(host);a=next(r for r in actual if r["core"]==host);rr={x:rate(c[x],den[x])for x in REGS};ea=min(lrr(rr["HB"],rr["HA"]),lrr(rr["SB"],rr["HA"]));eo=min(lrr(rr["HB"],rr["OB"]),lrr(rr["SB"],rr["OB"]));lo_a=[];lo_ob=[]
  for f in sorted(folios["HB"]|folios["SB"]):
   cc=Counter(r["register"]for r in z if r["physical_folio"]!=f);dd=Counter(r["register"]for r in rows if r["physical_folio"]!=f);q={x:rate(cc[x],dd[x])for x in REGS};lo_a.append(min(lrr(q["HB"],q["HA"]),lrr(q["SB"],q["HA"])));lo_ob.append(min(lrr(q["HB"],q["OB"]),lrr(q["SB"],q["OB"])))
  ok&=a["hb_count"]==str(c["HB"])and a["sb_count"]==str(c["SB"])and a["ha_count"]==str(c["HA"])and a["ob_count"]==str(c["OB"])and close(a["min_log2_enrichment_vs_ha"],ea)and close(a["min_log2_specificity_vs_ob"],eo)and close(a["lofo_min_ha"],min(lo_a))and close(a["lofo_min_ob"],min(lo_ob))
 checks["all_core_rates_exact"]=ok and len(eligible)==len(actual)==48
 ann=read(ANN);checks["f84_annotations_excluded"]=not any(r["locus"].startswith("f84r")for r in ann);aby=defaultdict(list)
 for r in ann:aby[r["residual_host"]].append(r)
 top=actual[0];checks["winner_exact"]=top["core"]=="okair"and top["hb_count"]=="3"and top["sb_count"]=="7"and top["ha_count"]=="0"and top["ob_count"]=="2"and not aby["okair"]
 robust=[r for r in actual if r["formal_attribution"]=="UNATTRIBUTED_RESIDUAL"and float(r["lofo_min_ha"])>0 and float(r["lofo_min_ob"])>0];checks["robust_residuals_exact"]=[r["core"]for r in robust]==["okair","kaiin"]and not aby["kaiin"]
 expected=[]
 for a in actual:
  if a["grounding_state"]=="VISUAL_OBJECT_DIVERSE_COUNTEREXAMPLE":
   for r in aby[a["core"]]:expected.append({"core":a["core"],"locus":r["locus"],"physical_folio":r["physical_folio"],"token":r["token"],"object_tags":r["object_tags"],"relation_tags":r["relation_tags"],"certainty":r["annotation_certainty"],"description":r["raw_source_description"]})
 expected.sort(key=lambda r:(r["core"],r["physical_folio"],r["locus"]));checks["counterexamples_exact"]=expected==read(COUNTER)
 result=json.loads(RESULT.read_text());checks["headline_exact"]=result["filtered_groups"]==11277 and result["eligible_cores"]==48 and result["unattributed_robust_cores"]==2 and result["top_residual"]["core"]=="okair"
 body=dict(result);claim=body.pop("result_content_sha256");checks["result_hash"]=csha(body)==claim;checks["status"]=result["status"]=="OKAIR_TOP_POST_ATTRIBUTION_RESIDUAL_HOST_UNGROUNDED";checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT047_POST_ATTRIBUTION_CORE_ATLAS_REPORT.md").read_text();checks["claim_ceiling"]="not grounded"in report and"OKAIR` and the lower-ranked `KAIIN"in report and"does not assign"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT047_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT047_POST_ATTRIBUTION_CORE_ATLAS_VALIDATION_V1","status":"PASS_INDEPENDENT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent mechanism filter, exact core rate/LOFO, annotation-capacity, and hash reconstruction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

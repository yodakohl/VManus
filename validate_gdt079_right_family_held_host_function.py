#!/usr/bin/env python3
"""Independent selected-model and profile checks for GDT079."""
from __future__ import annotations

import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";RESULT=ROOT/"gdt079_result.json";SCORES=ROOT/"gdt079_context_model_scores.tsv";FOLDS=ROOT/"gdt079_held_host_folds.tsv";PROFILES=ROOT/"gdt079_right_family_profiles.tsv";VARIANTS=ROOT/"gdt079_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt079_validation.json"
HOSTS=("d","ok","yk","yt");RIGHTS=("aiin","air","ain","ar","al")
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-8):return abs(float(a)-float(b))<=t
def main():
 source=[r for r in read(SOURCE)if r["page_host"]in HOSTS and r["right_family"]in RIGHTS];result=json.loads(RESULT.read_text());scores=read(SCORES);folds=read(FOLDS);profiles=read(PROFILES);checks={}
 checks["panel"]=len(source)==result["groups"]==1212 and Counter(r["page_host"]for r in source)==Counter({"ok":836,"d":268,"yt":55,"yk":53})and not any(r["locus"].startswith("f84r")for r in source)
 checks["grid"]=len(scores)==25 and set((r["context"],int(r["backoff"]))for r in scores)==set((c,b)for c in result["contexts"]for b in result["grid"])
 best=max(scores,key=lambda r:float(r["selector_paid_gain_bits"]));checks["best"]=best["context"]==result["best_model"]["context"]=="POSITION"and int(best["backoff"])==result["best_model"]["backoff"]==64 and close(best["selector_paid_gain_bits"],result["best_model"]["selector_paid_gain_bits"])
 po=max((r for r in scores if r["context"]=="POSITION_ONLY"),key=lambda r:float(r["selector_paid_gain_bits"]));checks["position_only"]=close(po["raw_gain_bits"],result["position_only_best"]["raw_gain_bits"])
 base_total=held_total=0.;fold_rebuild={}
 for host in HOSTS:
  tr=[r for r in source if r["page_host"]!=host];te=[r for r in source if r["page_host"]==host];bc=defaultdict(Counter);bn=Counter();cc=defaultdict(Counter);cn=Counter()
  for r in tr:
   bc[r["register"]][r["right_family"]]+=1;bn[r["register"]]+=1;k=(r["register"],(r["position_quartile"],r["dy_closure"],r["b3"]));cc[k][r["right_family"]]+=1;cn[k]+=1
  bb=hh=0.
  for r in te:
   pb=(bc[r["register"]][r["right_family"]]+.5)/(bn[r["register"]]+.5*len(RIGHTS));k=(r["register"],(r["position_quartile"],r["dy_closure"],r["b3"]));p=(cc[k][r["right_family"]]+64*pb)/(cn[k]+64);bb-=math.log2(pb);hh-=math.log2(p)
  base_total+=bb;held_total+=hh;fold_rebuild[host]=(bb,hh)
 checks["selected_reconstruction"]=close(base_total,result["baseline_bits"])and close(held_total,result["best_model"]["held_bits"])
 checks["folds"]=all(close(fold_rebuild[r["held_page_host"]][0],r["baseline_bits"])and close(fold_rebuild[r["held_page_host"]][1],r["held_bits"])for r in folds)and sum(float(r["gain_bits"])>0 for r in folds)==result["positive_held_hosts"]==3
 pi={r["right_family"]:r for r in profiles};checks["profiles"]=all(int(pi[f]["occurrences"])==sum(r["right_family"]==f for r in source)and int(pi[f]["hosts"])==4 and int(pi[f]["registers"])==5 for f in RIGHTS)
 checks["headline"]=result["status"]=="RIGHT_FAMILY_POSITION_PROFILE_WEAKLY_TRANSFERS_ACROSS_HELD_HOSTS"and result["best_model"]["selector_paid_gain_bits"]>0
 checks["variants"]={r["variant_id"]:r["status"]for r in read(VARIANTS)}=={"V00":"BASELINE","V01":"PRIMARY","V02":"FIXED_HOSTS","V03":"NOT_RUN"}
 checks["f84_seal"]=not any(result["f84r"].values());body=dict(result);claim=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claim;checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in result[fam].items())
 z=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT079_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==result["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT079_RIGHT_FAMILY_HELD_HOST_FUNCTION_VALIDATION_V1","status":"PASS_INDEPENDENT_SELECTED_MODEL_AND_PROFILE_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs the selected leave-host-out POSITION model and every fold, profile counts, grid/selector, variants, seals, hashes and ledger."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

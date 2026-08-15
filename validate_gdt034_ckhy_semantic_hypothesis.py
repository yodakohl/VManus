#!/usr/bin/env python3
"""Independent validator for the frozen GDT034 query."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt034_result.json";VAL=ROOT/"gdt034_validation.json"
def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def guarded(locus,index):
 out=[];path=ROOT/"experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();cols=header.rstrip("\n").split("\t");li=cols.index("locus");gi=cols.index("source_group_index")
  for line in h:
   raw=line.rstrip("\n").split("\t")
   if raw[li]==locus and int(raw[gi])==index:out.append(next(csv.DictReader([header,line],delimiter="\t")))
 return out
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT034_CKHY_SEMANTIC_HYPOTHESIS_RESULT_V1"),("content",digest==csha(body)),("status",result["status"]=="PASS_SEMANTIC_GLOSS_PROVISIONAL_TRANSFER")]
 for section in ("inputs","implementation","outputs"):
  for name,d in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==d))
 pred=json.loads((ROOT/"gdt034_ckhy_semantic_hypothesis_prediction.json").read_text());checks +=[("frozen_prediction",pred["status"]=="FROZEN_BEFORE_CKHY_QUERY"and pred["target"]["page"]=="f14r"and pred["prediction"]["positive_condition"]=="exact_host_occurrences_greater_than_or_equal_to_1"),("failure_scope","only the parallel/fused"in pred["failure_scope"])]
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==15592),("f84_inventory",not any(r["page"]=="f84r"for r in inv))];a=[r for r in inv if r["section"]=="H"and r["currier"]=="A"];host=[r for r in a if r["residual_host"]=="ckhy"];target=[r for r in host if r["page"]=="f14r"]
 checks +=[("target_exact",len(target)==1 and target[0]["locus"]=="f14r.7"and target[0]["token"]=="chckhy"and target[0]["group_index"]=="3"and target[0]["group_count"]=="3"and target[0]["record_state"]=="CARRIER_STATE"and target[0]["dy_closure"]=="0"),("reference",len({r["page"]for r in a})==95 and len(host)==17 and len({r["page"]for r in host})==17)]
 align=guarded("f14r.7",3);checks.append(("alternate_readings",len(align)==3 and {x["edition"]for x in align}=={"ZL3b","IT2a","RF1b"}and {x["primary_sta_families"]for x in align}=={"KUA"}and {x["nearest_basic_eva_primary"]for x in align}=={"chckhy"}and sum(int(x["alternative_site_count"])for x in align)==0));checks.append(("alignment_hash",result["guarded_source_alignment"]["canonical_sha256"]==csha(align)and result["guarded_source_alignment"]["f84r_rows_retained"]==0))
 stored=read("gdt034_ckhy_target_occurrences.tsv");checks.append(("occurrence_export",len(stored)==3 and {x["edition"]for x in stored}=={"ZL3b","IT2a","RF1b"}and all(x["residual_host"]=="ckhy"and x["claim_state"]=="FROZEN_PAGE_LEVEL_HIT_NOT_COMPONENT_OWNERSHIP"for x in stored)))
 report=" ".join((ROOT/"GDT034_CKHY_SEMANTIC_HYPOTHESIS_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("one-page provisional semantic transfer succeeded","substantial background probability","did not search another target","f84r was not opened"))),("formal_core_unchanged",not result["semantic_gloss"]["formal_core_status_modified"]and not result["semantic_gloss"]["parser_modified"]and not result["semantic_gloss"]["alternative_meaning_search_performed"]),("f84_result",result["f84r"]=={"opened":False,"retained":False,"queried":False,"joined":False,"scored":False}),("ledger",ledger.count("GDT034_CKPT001")==1)]
 failures=[name for name,ok in checks if not ok];validation={"schema":"GDT034_CKHY_SEMANTIC_HYPOTHESIS_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of the frozen f14r exact CKHY query, Herbal-A reference prevalence, three-reading agreement, prediction and implementation hashes, semantic-gloss-only scope, ledger, and f84r exclusion."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()

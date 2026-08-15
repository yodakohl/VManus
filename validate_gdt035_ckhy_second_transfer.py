#!/usr/bin/env python3
"""Independent validator for GDT035."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt035_result.json";VAL=ROOT/"gdt035_validation.json";ALLOWED={"ckhy","chckhy","checkhy","shckhy"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def rows():
 out=defaultdict(list);path=ROOT/"experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();cols=header.rstrip("\n").split("\t");li=cols.index("locus")
  for line in h:
   raw=line.rstrip("\n").split("\t")
   if not raw[li].startswith("f101v."):continue
   r=next(csv.DictReader([header,line],delimiter="\t"));out[(r["locus"],r["source_group_index"])].append(r)
 return out
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT035_CKHY_SECOND_TRANSFER_RESULT_V1"),("content",digest==csha(body)),("status",result["status"]=="FAIL_SECOND_SEMANTIC_GLOSS_REJECTED")]
 for section in("inputs","implementation","outputs"):
  for name,d in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==d))
 v1=json.loads((ROOT/"gdt035_ckhy_second_transfer_prediction.json").read_text());v2=json.loads((ROOT/"gdt035_ckhy_second_transfer_prediction_v2.json").read_text());checks +=[("v1_freeze",v1["status"]=="FROZEN_BEFORE_TARGET_CKHY_QUERY"and v1["target"]["page"]=="f101v"),("v2_freeze",v2["status"]=="FROZEN_AFTER_CAPACITY_CORRECTION_BEFORE_SOURCE_GROUP_QUERY"and set(v2["unchanged"]["allowed_surface_forms"])==ALLOWED),("same_gloss",v1["hypothesis"]["gloss"]==v2["unchanged"]["gloss"]=="PARALLEL_OR_FUSED_LEAF_OR_STALK_CONFIGURATION_DESCRIPTOR")]
 groups=rows();hits=[]
 for key,x in groups.items():
  forms={r["nearest_basic_eva_primary"]for r in x}
  if {r["edition"]for r in x}=={"ZL3b","IT2a","RF1b"}and len(forms)==1 and next(iter(forms))in ALLOWED:hits.append(key)
 flat=[r for k in sorted(groups)for r in sorted(groups[k],key=lambda x:x["edition"])];checks +=[("target_groups",len(groups)==233),("zero_hits",hits==[]),("guarded_hash",result["guarded_target_alignment"]["canonical_sha256"]==csha(flat)and result["guarded_target_alignment"]["f84r_rows_retained"]==0)]
 with (ROOT/"gdt035_ckhy_second_transfer_query.tsv").open()as h:q=list(csv.DictReader(h,delimiter="\t"));checks.append(("query_export",len(q)==1 and q[0]["exact_all_reading_ckhy_groups"]=="0"and q[0]["formal_ckhy_core_status"]=="UNCHANGED"))
 report=" ".join((ROOT/"GDT035_CKHY_SECOND_TRANSFER_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("exact semantic gloss","is rejected","does not weaken ckhy as a recurrent formal residual host","no fuzzy form","f84r was not opened"))),("scope",not result["semantic_gloss"]["alternative_meaning_search_performed"]and not result["semantic_gloss"]["parser_modified"]and not result["semantic_gloss"]["formal_core_status_modified"]),("f84",result["f84r"]=={"opened":False,"retained":False,"queried":False,"joined":False,"scored":False}),("ledger",ledger.count("GDT035_CKPT001")==1)]
 failures=[n for n,ok in checks if not ok];validation={"schema":"GDT035_CKHY_SECOND_TRANSFER_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of both freezes, capacity correction, 233 guarded f101v groups, exact four-form zero-hit decision, semantic-gloss-only failure, ledger, hashes, and f84r exclusion."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()

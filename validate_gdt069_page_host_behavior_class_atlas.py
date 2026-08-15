#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT069."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt069_result.json";ATLAS=ROOT/"gdt069_behavior_class_atlas.tsv";EXAMPLES=ROOT/"gdt069_behavior_class_examples.tsv";VARIANTS=ROOT/"gdt069_variant_log.tsv";SOURCE=ROOT/"gdt062_right_family_inventory.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt069_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());atlas=read(ATLAS);examples=read(EXAMPLES);src=read(SOURCE);checks={}
 checks["source_and_seal"]=len(src)==r["groups"]==15592 and not any(x["locus"].startswith("f84r")for x in src)and not any(r["f84r"].values())
 checks["panel_shape"]=r["eligible_loci"]==332 and r["physical_folios"]==19 and r["eligible_raw_predicates"]==154 and r["candidate_predicates"]==140 and len(atlas)==r["tests"]==1120
 candidates={x["candidate"]for x in atlas};checks["unique_mask_library"]=len(candidates)==140 and all(x["candidate"]in x["candidate_aliases"].split(";")for x in atlas)
 interesting=[x for x in atlas if x["label"]=="INTERESTING_EXPLORATORY"];checks["interesting_count"]=len(interesting)==r["interesting_exploratory"]==9
 checks["interesting_blocks"]=dict(Counter(x["behavior_block"]for x in interesting))==r["interesting_by_block"]=={"DY":4,"F":1,"R":2,"W":2}
 top=min(atlas,key=lambda x:(float(x["local_two_sided_p"]),-abs(float(x["conditional_effect"])),x["candidate"],x["external_axis"]));checks["top_confounded"]=top["candidate"]==r["top_candidate"]["candidate"]=="RATE:NDY=0>=0.25"and top["label"]=="LIKELY_PAGE_CONFOUND"and int(top["informative_strata"])==1
 topi=min(interesting,key=lambda x:(float(x["local_two_sided_p"]),-abs(float(x["conditional_effect"])),x["candidate"],x["external_axis"]));checks["top_interesting"]=topi["candidate"]==r["top_interesting"]["candidate"]=="RATE:R=aiin>=0.25"and topi["external_axis"]=="REL_ENCLOSURE"and close(topi["conditional_effect"],r["top_interesting"]["conditional_effect"])
 checks["multiple_test_disclosure"]=all(close(x["bonferroni_all_p"],1.)for x in interesting)and"Identical locus masks collapsed"in r["selection_disclosure"]
 checks["examples_bound"]=len(examples)==40 and all(x["candidate"]in candidates for x in examples)
 checks["variants"]={x["variant_id"]:x["status"]for x in read(VARIANTS)}=={"V00":"PRIMARY","V01":"RUN_SENSITIVITY","V02":"RUN_ROBUSTNESS","V03":"EXCLUDED_CAPACITY","V04":"NOT_RUN"}
 checks["status_ceiling"]=r["status"]=="BEHAVIOR_CLASS_EXTERNAL_ASSOCIATION_LEADS_POSTSELECTED"and"hypothesis-generation"in r["interpretation"]and"No semantic class"in r["claim_ceiling"]
 body=dict(r);claim=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claim;checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT069_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT069_PAGE_HOST_BEHAVIOR_CLASS_ATLAS_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks source/seal, panel and unique-mask atlas shape, interesting rows/blocks, confounded and exploratory leaders, multiple-test disclosure, examples, variants, hashes, ledger and ceiling; does not independently rebuild every fold profile/effect."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

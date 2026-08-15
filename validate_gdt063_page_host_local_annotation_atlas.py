#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT063."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt063_result.json";ATLAS=ROOT/"gdt063_page_host_annotation_atlas.tsv";EXAMPLES=ROOT/"gdt063_page_host_candidate_examples.tsv";GROUPS=ROOT/"gdt059_hpr2_external_inventory.tsv";FULL=ROOT/"gdt062_right_family_inventory.tsv";VARIANTS=ROOT/"gdt063_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt063_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());atlas=read(ATLAS);examples=read(EXAMPLES);groups=read(GROUPS);full=read(FULL);variants=read(VARIANTS);checks={}
 checks["panel_counts"]=len({x["locus"]for x in groups})==r["loci"]==560 and r["unhedged_loci"]==316 and len({x["physical_folio"]for x in groups})==r["physical_folios"]
 checks["atlas_grid"]=len(atlas)==r["tests"]==2592 and r["candidate_features"]==324 and len({x["candidate"]for x in atlas})==324 and len({x["external_axis"]for x in atlas})==8
 labels=Counter(x["label"]for x in atlas);checks["label_counts"]=labels==Counter({"LIKELY_PAGE_CONFOUND":1770,"UNSTABLE":368,"NO_SIGNAL":366,"WEAK":78,"INTERESTING_EXPLORATORY":10})and r["interesting_exploratory"]==10
 by={(x["candidate"],x["external_axis"]):x for x in atlas};d=by["EXACT:d","REL_ENCLOSURE"];ok=by["EXACT:ok","WATER_OR_APPARATUS"]
 checks["exact_d_lead"]=d["label"]=="INTERESTING_EXPLORATORY"and int(d["physical_folios"])==7 and int(d["informative_strata"])==3 and close(d["conditional_effect"],.404542136003)and close(d["unhedged_conditional_effect"],.7)
 checks["exact_ok_lead"]=ok["label"]=="INTERESTING_EXPLORATORY"and int(ok["physical_folios"])==11 and int(ok["informative_strata"])==4 and close(ok["conditional_effect"],.59375)and close(ok["unhedged_conditional_effect"],.857142857143)
 checks["wrapper_reuse"]=len({x["wrapper"]for x in full if x["page_host"]=="d"})==7 and len({x["wrapper"]for x in full if x["page_host"]=="ok"})==7 and int(d["global_exact_host_wrapper_types"])==int(ok["global_exact_host_wrapper_types"])==7
 checks["multiplicity_disclosed"]=all(close(x["bonferroni_all_p"],1.)for x in(d,ok))and close(r["top_candidate"]["bonferroni_all_p"],1.)
 checks["examples_and_counterexamples"]=len(examples)==30 and all(x["counterexample_loci"]!="NONE"for x in examples if x["candidate"]in{"EXACT:d","EXACT:ok"})
 checks["f84_excluded"]=not any(x["locus"].startswith("f84r")for x in groups)and not any(r["f84r"].values())
 checks["variant_log"]={x["variant_id"]:x["status"]for x in variants}=={"V00":"PRIMARY","V01":"RUN_SENSITIVITY","V02":"RUN_LIBRARY","V03":"NOT_RUN"}
 body=dict(r);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 checks["status_and_ceiling"]=r["status"]=="PAGE_HOST_LOCAL_ANNOTATION_LEADS_POSTSELECTED"and"require independent freezing"in r["interpretation"]and"No role"in r["claim_ceiling"]
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT063_CKPT001"];checks["ledger_exact"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT063_PAGE_HOST_LOCAL_ANNOTATION_ATLAS_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks panel/atlas/label counts, the two exact-host leads and wrapper reuse, multiplicity/counterexample disclosures, f84 exclusion, hashes, variants, ledger, and ceiling. It does not independently reconstruct all 2,592 conditional scores."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

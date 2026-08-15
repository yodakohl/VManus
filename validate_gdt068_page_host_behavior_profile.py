#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT068."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt068_result.json";SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";PROFILES=ROOT/"gdt068_host_behavior_profiles.tsv";SCORES=ROOT/"gdt068_behavior_representation_scores.tsv";SUMMARY=ROOT/"gdt068_behavior_representation_summary.tsv";VARIANTS=ROOT/"gdt068_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt068_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());src=read(SOURCE);ann=read(ANN);parsed=read(PARSED);scores=read(SCORES);summary=read(SUMMARY);checks={}
 checks["source_and_seal"]=len(src)==r["groups"]==15592 and not any(x["locus"].startswith("f84r")for x in src)and not any(r["f84r"].values())
 checks["annotation_count"]=len(ann)==len(parsed)==r["annotated_groups"]==671 and len({x["locus"]for x in parsed})==560
 hf=defaultdict(set)
 for x in src:hf[x["page_host"]].add(x["physical_folio"])
 byloc=defaultdict(list)
 for x in parsed:byloc[x["locus"]].append(x)
 eligible=[z for z in byloc.values()if all(len(hf[x["page_host"]])>=2 for x in z)]
 checks["transferable_panel"]=len(eligible)==r["eligible_loci"]==332 and len({x[0]["physical_folio"]for x in eligible})==r["physical_folios"]==19
 checks["profile_rows"]=len(read(PROFILES))==sum(len(v)>=2 for v in hf.values())
 checks["score_shape"]=len(scores)==len(r["axes"])*len(r["representations"])==48 and {(x["external_axis"],x["representation"])for x in scores}=={(a,p)for a in r["axes"]for p in r["representations"]}
 reconstructed={}
 for rep in r["representations"]:
  z=[x for x in scores if x["representation"]==rep];reconstructed[rep]={"external_axes":len(z),"descriptive_total_gain_bits":sum(float(x["gain_vs_nuisance_bits"])for x in z),"axes_positive":sum(float(x["gain_vs_nuisance_bits"])>0 for x in z),"axes_beating_raw_char3":sum(float(x["gain_vs_nuisance_bits"])>float(next(q for q in scores if q["external_axis"]==x["external_axis"]and q["representation"]=="RAW_CHAR3")["gain_vs_nuisance_bits"])for x in z)}
 checks["summary_reconstruction"]=all(reconstructed[k]["external_axes"]==r["summary"][k]["external_axes"]and reconstructed[k]["axes_positive"]==r["summary"][k]["axes_positive"]and reconstructed[k]["axes_beating_raw_char3"]==r["summary"][k]["axes_beating_raw_char3"]and close(reconstructed[k]["descriptive_total_gain_bits"],r["summary"][k]["descriptive_total_gain_bits"])for k in reconstructed)
 lead=max(reconstructed,key=lambda k:reconstructed[k]["descriptive_total_gain_bits"]);checks["leader"]=lead==r["leader"]["representation"]==r["best_behavior"]["representation"]=="BEHAVIOR_SELF_NEIGHBOR_NOPOS"and close(r["leader"]["descriptive_total_gain_bits"],79.58397310463816)
 expected_axis={x["external_axis"]:x for x in scores if x["representation"]==lead};checks["axis_binding"]=set(expected_axis)==set(r["best_behavior_axis_scores"])and all(close(expected_axis[k]["gain_vs_nuisance_bits"],r["best_behavior_axis_scores"][k]["gain_vs_nuisance_bits"])for k in expected_axis)
 checks["failure_disclosure"]=all(float(expected_axis[x]["gain_vs_nuisance_bits"])<0 for x in("PLANT","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT"))
 checks["variants"]={x["variant_id"]:x["status"]for x in read(VARIANTS)}=={"V00":"PRIMARY","V01":"RUN","V02":"RUN","V03":"RUN_BASELINES","V04":"EXCLUDED_CAPACITY","V05":"NOT_RUN"}
 checks["status_ceiling"]=r["status"]=="BEHAVIORAL_PAGE_HOST_PROFILE_LEAD_POSTSELECTED"and"Best of three"in r["selection_disclosure"]and"hypothesis-generation"in r["interpretation"]and"No role"in r["claim_ceiling"]
 body=dict(r);claim=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claim;checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT068_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT068_PAGE_HOST_BEHAVIOR_PROFILE_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks source/annotation counts, two-folio host capacity, profile/score shape, score summaries, leader and failures, variants, seal, hashes, ledger and ceiling. It does not independently rerun all held-folio nearest-neighbor predictions."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

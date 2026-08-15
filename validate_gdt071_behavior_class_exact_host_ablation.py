#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT071."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt071_result.json";TESTS=ROOT/"gdt071_behavior_class_host_ablation.tsv";MEMBERS=ROOT/"gdt071_behavior_class_host_members.tsv";ATLAS=ROOT/"gdt069_behavior_class_atlas.tsv";VARIANTS=ROOT/"gdt071_variant_log.tsv";SOURCE=ROOT/"gdt062_right_family_inventory.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt071_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());tests=read(TESTS);members=read(MEMBERS);atlas=read(ATLAS);src=read(SOURCE);checks={}
 checks["source_panel_seal"]=len(src)==r["groups"]==15592 and r["eligible_loci"]==332 and not any(x["locus"].startswith("f84r")for x in src)and not any(r["f84r"].values())
 leads={(x["candidate"],x["external_axis"]):x for x in atlas if x["label"]=="INTERESTING_EXPLORATORY"};checks["lead_set"]=len(leads)==len(tests)==r["tested_class_leads"]==9 and {(x["candidate"],x["external_axis"])for x in tests}==set(leads)
 checks["original_effects"]=all(close(x["original_conditional_effect"],leads[x["candidate"],x["external_axis"]]["conditional_effect"])for x in tests)
 by=defaultdict(list)
 for x in members:by[x["candidate"],x["external_axis"]].append(x)
 checks["member_counts"]=all(len(by[x["candidate"],x["external_axis"]])==int(x["distinct_exact_hosts"])and sum(int(q["included_in_repeat_host_robustness"])for q in by[x["candidate"],x["external_axis"]])==int(x["repeat_exact_hosts"])for x in tests)
 checks["member_outcomes"]=all(int(x["candidate_positive_loci"])+int(x["candidate_negative_loci"])==int(x["candidate_loci"])for x in members)
 for x in tests:
  z=[float(q["leave_host_out_effect"])for q in by[x["candidate"],x["external_axis"]]if q["included_in_repeat_host_robustness"]=="1"]
  checks["range:"+x["candidate"]+":"+x["external_axis"]]=close(min(z),x["leave_repeat_host_min_effect"])and close(max(z),x["leave_repeat_host_max_effect"])
 checks["all_sign_stable"]=sum(int(x["leave_repeat_host_sign_stable"])for x in tests)==r["sign_stable_class_leads"]==9 and all(x["robustness_label"]=="CLASS_LEVEL_DIRECTION_SURVIVES_EXACT_HOST_ABLATION"for x in tests)
 ai=next(x for x in tests if x["candidate"]=="RATE:R=aiin>=0.25"and x["external_axis"]=="REL_ENCLOSURE");checks["aiin_headline"]=close(ai["leave_d_out_effect"],r["aiin_enclosure"]["leave_d_out_effect"])and close(ai["leave_ok_out_effect"],r["aiin_enclosure"]["leave_ok_out_effect"])and int(ai["distinct_exact_hosts"])==13
 sh=next(x for x in tests if x["candidate"]=="RATE:W=sh>=0.25");checks["sh_headline"]=int(sh["repeat_exact_hosts"])==9 and close(sh["leave_repeat_host_min_effect"],r["sh_attachment"]["leave_repeat_host_min_effect"])
 checks["variants"]={x["variant_id"]:x["status"]for x in read(VARIANTS)}=={"V00":"PRIMARY","V01":"RUN_DISPLAY","V02":"POSTSELECTED_INPUT","V03":"NOT_RUN"}
 checks["status_ceiling"]=r["status"]=="BEHAVIOR_CLASS_LEADS_SURVIVE_EXACT_HOST_ABLATION_POSTSELECTED"and"postselected"in r["interpretation"].lower()and"No semantic class"in r["claim_ceiling"]
 body=dict(r);claim=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claim;checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT071_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT071_BEHAVIOR_CLASS_EXACT_HOST_ABLATION_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks source/panel/seal, exact GDT069 lead set/effects, member counts/outcomes, every repeated-host range and direction, headline classes, variants, hashes, ledger and ceiling; it does not rerun fold-profile construction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

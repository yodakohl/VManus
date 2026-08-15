#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT061."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt061_result.json";SOURCE=ROOT/"gdt060_dy_transition_inventory.tsv";SCORES=ROOT/"gdt061_dy_renderer_host_scores.tsv";ATTR=ROOT/"gdt061_dy_component_attribution.tsv";VARIANTS=ROOT/"gdt061_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt061_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-8):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());src=read(SOURCE);scores=read(SCORES);attr=read(ATTR);variants=read(VARIANTS);checks={}
 checks["input_counts"]=len(src)==r["boundaries"]==7409 and sum(int(x["dy"])for x in src)==r["dy_boundaries"]==1298
 checks["score_grid"]=len(scores)==60 and len({(x["evaluation"],x["representation"],x["renderer_control"],x["scope"])for x in scores})==60
 checks["attribution_grid"]=[x["renderer_control"]for x in attr]==["WRAPPER","WRAPPER_FRAME","FULL_COMPILER"]
 by={(x["evaluation"],x["representation"],x["renderer_control"],x["scope"]):x for x in scores};p=by["LEAVE_FOLIO_OUT","PAGE_HOST","FULL_COMPILER","ALL"];x=by["LEAVE_REGISTER_OUT","PAGE_HOST","FULL_COMPILER","ALL"]
 checks["primary_lofo"]=close(p["dy_gain_vs_base"],762.1704861968392)and close(p["renderer_gain_vs_base"],15566.382370433712)and close(p["residual_dy_gain_vs_renderer"],-291.6885899780609)
 checks["cross_register"]=close(x["residual_dy_gain_vs_renderer"],-491.273804143937)and float(x["dy_gain_vs_base"])>0
 wrapper=by["LEAVE_FOLIO_OUT","PAGE_HOST","WRAPPER","ALL"]
 checks["wrapper_absorption"]=close(wrapper["residual_dy_gain_vs_renderer"],-417.1769846517054)and all(float(by["LEAVE_FOLIO_OUT","PAGE_HOST","WRAPPER",s]["residual_dy_gain_vs_renderer"])<0 for s in("HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B"))
 checks["all_nested_controls_negative"]=all(float(z["lofo_residual_dy_gain_vs_renderer"])<0 and int(z["lofo_residual_gain_positive_registers"])==0 for z in attr)
 checks["f84_excluded"]=not any(z["locus"].startswith("f84r")for z in src)and not any(r["f84r"].values())
 checks["variant_log"]={z["variant_id"]:z["status"]for z in variants}=={"V00":"PRIMARY","V01":"RUN_ABLATION","V02":"RUN_ABLATION","V03":"RUN_BASELINE","V04":"RUN_SENSITIVITY","V05":"NOT_RUN"}
 body=dict(r);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 checks["status_and_ceiling"]=r["status"]=="DY_POST_BOUNDARY_HOST_SIGNAL_ABSORBED_BY_FOLLOWING_WRAPPER"and"following wrapper alone"in r["generative_update"]and"no role"in r["claim_ceiling"]
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT061_CKPT001"];checks["ledger_exact"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT061_DY_RENDERER_HOST_ATTRIBUTION_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks input counts, exact score grids, nested renderer attribution headlines, register directions, f84 exclusion, hashes, variants, ledger, and ceiling; it does not independently rerun the hierarchical character scorer."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

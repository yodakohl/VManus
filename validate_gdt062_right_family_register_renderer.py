#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT062."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt062_result.json";INVENTORY=ROOT/"gdt062_right_family_inventory.tsv";SCORES=ROOT/"gdt062_right_family_scores.tsv";VARIANTS=ROOT/"gdt062_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt062_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-8):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());inv=read(INVENTORY);scores=read(SCORES);variants=read(VARIANTS);checks={}
 checks["inventory_counts"]=len(inv)==r["groups"]==15592 and len({x["physical_folio"]for x in inv})==r["physical_folios"]==94 and sum(x["right_family"]!="NONE"for x in inv)==r["right_family_present"]==2988
 checks["family_counts"]=Counter(x["right_family"]for x in inv)==Counter({"NONE":12604,"aiin":1054,"ar":673,"ain":594,"al":572,"air":95})
 checks["score_grid"]=len(scores)==24 and len({(x["host_key"],x["hand_control"],x["scope"])for x in scores})==24
 by={(x["host_key"],x["hand_control"],x["scope"]):x for x in scores};p=by["EXACT","HAND","ALL"]
 checks["primary_gain"]=close(p["host_gain_vs_nuisance"],2193.4596875352963)and close(p["register_gain_given_host"],350.0543117628331)and close(p["register_gain_per_group"],.02245089223722634)
 checks["all_registers_positive"]=all(float(by["EXACT","HAND",s]["register_gain_given_host"])>0 for s in("HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B"))
 checks["sensitivities"]=close(by["SHAPE","HAND","ALL"]["register_gain_given_host"],368.387284236)and float(by["EXACT","NO_HAND","ALL"]["register_gain_given_host"])>0
 checks["f84_excluded"]=not any(x["locus"].startswith("f84r")for x in inv)and not any(r["f84r"].values())
 checks["variant_log"]={x["variant_id"]:x["status"]for x in variants}=={"V00":"PRIMARY","V01":"RUN_SENSITIVITY","V02":"RUN_SENSITIVITY","V03":"NOT_RUN"}
 body=dict(r);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 checks["status_and_ceiling"]=r["status"]=="RIGHT_FAMILY_IS_TRANSFERABLE_REGISTER_CONDITIONED_RENDERING"and"content neutrality remains unestablished"in r["interpretation"]and"No right-family meaning"in r["claim_ceiling"]
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT062_CKPT001"];checks["ledger_exact"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT062_RIGHT_FAMILY_REGISTER_RENDERER_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks counts, family distribution, exact held-score grid, primary and sensitivity gains, per-register directions, f84 exclusion, hashes, variants, ledger, and claim ceiling; it does not independently rerun the hierarchical categorical scorer."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

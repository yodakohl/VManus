#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT064."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt064_result.json";CELLS=ROOT/"gdt064_cross_wrapper_context_cells.tsv";PAIRS=ROOT/"gdt064_cross_wrapper_context_pairs.tsv";SOURCE=ROOT/"gdt062_right_family_inventory.tsv";VARIANTS=ROOT/"gdt064_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt064_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());cells=read(CELLS);pairs=read(PAIRS);src=read(SOURCE);variants=read(VARIANTS);checks={}
 checks["source_and_unit_counts"]=len(src)==r["groups"]==15592 and len({(x["page"],x["page_host"],x["wrapper"])for x in src})==r["units"]==10705
 checks["pair_and_cell_counts"]=len(pairs)==r["cross_folio_pairs"]==46082 and len(cells)==r["host_register_cells"]==619
 counts=Counter((x["host"],x["register"],x["pair_type"])for x in pairs);checks["pair_cap"]=r["pair_cap_per_host_register_type"]==200 and max(counts.values())<=200
 md=sum(float(x["different_wrapper_mean_similarity"])for x in cells)/len(cells);mc=sum(float(x["matched_control_mean_similarity"])for x in cells)/len(cells);both=[x for x in cells if x["same_wrapper_available"]=="1"];ms=sum(float(x["same_wrapper_mean_similarity"])for x in both)/len(both)
 checks["mean_reconstruction"]=close(md,r["mean_different_wrapper_similarity"])and close(mc,r["mean_matched_control_similarity"])and close(ms,r["mean_same_wrapper_similarity"])
 checks["positive_cells"]=sum(float(x["different_minus_control"])>0 for x in cells)==r["positive_cells"]==374 and r["same_wrapper_cells"]==len(both)==461
 checks["small_invariance_gain"]=close(r["different_minus_control"],.00451776215656472)and close(r["relative_gain_vs_control"],.021725903020181)and close(r["different_minus_same"],-.00046500636807539)
 checks["postselected_leads"]=r["postselected_lead_positive_cells"]=={"d":4,"ok":5}and len(r["postselected_leads"]["d"])==len(r["postselected_leads"]["ok"])==5
 checks["f84_excluded"]=not any(x["locus"].startswith("f84r")for x in src)and not any(r["f84r"].values())
 checks["variant_log"]={x["variant_id"]:x["status"]for x in variants}=={"V00":"PRIMARY","V01":"RUN_CONTROL","V02":"RUN_SENSITIVITY","V03":"POSTSELECTED_DISPLAY","V04":"NOT_RUN"}
 body=dict(r);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 checks["status_and_ceiling"]=r["status"]=="CROSS_WRAPPER_PAGE_CONTEXT_PRESERVATION_SUPPORTED"and"external semantic preservation remains unconfirmed"in r["interpretation"]and"No role"in r["claim_ceiling"]
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT064_CKPT001"];checks["ledger_exact"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT064_CROSS_WRAPPER_PAGE_CONTEXT_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks source/unit, capped pair/cell counts, aggregate similarities, positive directions, postselected lead disclosure, f84 exclusion, hashes, variants, ledger, and ceiling. It does not independently recompute every weighted-Jaccard pair."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

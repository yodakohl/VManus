#!/usr/bin/env python3
"""Integrity and synthesis validator for GDT083."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt083_result.json";SCORES=ROOT/"gdt083_layer_scores.tsv";PAGES=ROOT/"gdt083_layer_page_contributions.tsv";SYN=ROOT/"gdt083_evidence_synthesis.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt083_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(SCORES);b={x["representation"]:x for x in s};checks={"representations":set(b)=={"RAW_TOKEN","RESIDUAL_HOST","PAGE_HOST","COMPILER_ONLY"}and len(s)==4,"ordering":float(b["PAGE_HOST"]["page_gain_vs_wrapper"])>float(b["RESIDUAL_HOST"]["page_gain_vs_wrapper"])>float(b["RAW_TOKEN"]["page_gain_vs_wrapper"])and float(b["COMPILER_ONLY"]["page_gain_vs_wrapper"])>float(b["PAGE_HOST"]["page_gain_vs_wrapper"]),"result_rows":all(abs(float(b[x["representation"]]["page_gain_vs_wrapper"])-x["page_gain_vs_wrapper"])<1e-8 for x in r["representations"]),"external":r["external_archived"]["page_host_gain_bits"]>r["external_archived"]["raw_gain_bits"]and r["external_archived"]["compiler_gain_bits"]<0 and r["external_archived"]["cross_section_behavior_gain_bits"]<0,"tables":len(read(PAGES))>400 and len(read(SYN))==3,"status":r["status"]=="PAGE_HOST_PAGE_SIGNAL_EXCEEDS_RAW_AND_RESIDUAL_BUT_INTERNAL_COMPILER_SIGNAL_PREVENTS_SEMANTIC_LOCALIZATION","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in r[fam].items());q=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT083_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT083_HPR_LAYER_LOCALIZATION_SYNTHESIS_VALIDATION_V1","status":"PASS_BOUND_LAYER_SYNTHESIS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks representation ordering, exact bound result rows, archived external/cross-section directions, tables, seals, hashes and ledger; does not independently rerun all 256 held-fold model cells."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Bound validator for GDT105."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt105_result.json";OUT=R/"gdt105_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(R/"gdt105_edge_model_scores.tsv");g=read(R/"gdt105_leave_register_scores.tsv");p=read(R/"gdt105_nonpch_to_pch_transfer.tsv");b=dict(r);ch=b.pop("result_content_sha256");by={x["model"]:x for x in s};pb={x["model"]:x for x in p}
 checks={"panel":r["groups"]==15592 and r["physical_folios"]==94,"outcomes":r["renderer_counts"]=={"B3":309,"BARE":9653,"DY":2642,"DY_RIGHT":25,"RIGHT":2963},"models":len(s)==6 and float(by["FINAL_CHAR"]["leave_folio_bits"])<float(by["EXACT_PAGE_HOST"]["leave_folio_bits"]),"pch":r["pch_groups"]==331 and len(p)==6 and int(pb["FINAL_CHAR"]["test_groups"])==331 and float(pb["FINAL_CHAR"]["test_bits"])<float(pb["REGISTER_ONLY"]["test_bits"]),"registers":len(g)==30 and all(float(x["gain_vs_other_register_prevalence_bits"])>0 for x in g if x["model"]=="FINAL_CHAR"),"roles":r["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in s+g+p),"seal":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/k)==v for fam in ("inputs","outputs","documents","implementation") for k,v in r[fam].items())};led=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT105_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT105_UNIVERSAL_HOST_EDGE_GRAMMAR_VALIDATION_V1","status":"PASS_BOUND_EDGE_COMPARISON" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/outcome counts, score order, PCH transfer, register directions, bindings, seal, roles, and ledger; does not independently replay codelength accumulation."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

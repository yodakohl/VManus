#!/usr/bin/env python3
"""Bound validator for GDT096."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt096_result.json";OUT=R/"gdt096_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(R/"gdt096_representation_scores.tsv");p=read(R/"gdt096_predictions.tsv");b=dict(r);ch=b.pop("result_content_sha256");f=r["frozen_host_wrapper_result"]
 checks={"capacity":r["train_unhedged_loci"]==83 and r["test_hedged_loci"]==35 and r["positive_test_loci"]==4,"orbit":r["exact_worlds"]==1872,"grid":len(s)==10 and len(p)==35,"frozen_miss":f["representation"]=="HOST_WRAPPER_JOINT" and f["gain_bits"]<0,"host_lead":r["page_host_result"]["gain_bits"]>r["raw_result"]["gain_bits"]>0 and r["page_host_result"]["positive_gain_folios"]==5,"roles":all(x["semantic_role"]=="UNASSIGNED" for x in p),"f84":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())};z=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT096_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 ok=all(checks.values());o={"schema":"GDT096_LAYOUT_CHANNEL_TRANSFER_VALIDATION_V1","status":"PASS_BOUND_TRANSFER_MISS" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks bound capacity, exact-orbit count, frozen miss, output/hash/seal/ledger invariants; does not independently reimplement probabilities."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

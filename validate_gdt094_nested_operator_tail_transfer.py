#!/usr/bin/env python3
"""Aggregate validator for GDT094."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt094_result.json";SCORES=ROOT/"gdt094_nested_model_scores.tsv";TAILS=ROOT/"gdt094_tail_directions.tsv";BASE=ROOT/"gdt094_baseline_comparison.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt094_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(SCORES);t=read(TAILS);b=read(BASE);sel={(x["wrapper_outcome"],x["feature_model"]):x for x in s if x["selected"]=="1"};checks={"capacity":r["groups"]==4641 and r["matched_tails"]==42 and len(s)==40 and len(t)==84,"gains":float(sel["Q","BASE_OY"]["gain_bits"])>1000 and float(sel["D","BASE_OY"]["gain_bits"])>250,"tails":r["tail_direction_accuracy"]=={"Q":"41/41","D":"10/11"},"baseline":len(b)==2 and all(x["numeric_relationship"]=="IDENTICAL_FEATURE_AND_SCORE" for x in b),"status":r["status"]=="OPERATOR_BASE_RULE_TRANSFERS_TO_UNSEEN_TAILS_AND_FOLIOS_BUT_EQUALS_STRING_BASELINE","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==v for fam in ("inputs","outputs","documents","implementation") for name,v in r[fam].items());z=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT094_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT094_NESTED_OPERATOR_TAIL_TRANSFER_VALIDATION_V1","status":"PASS_BOUND_NESTED_TAIL_TRANSFER_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks nested panel/grid capacity, gains, tail directions, factor/string identity, hashes, seal and ledger; held probability stream is bound but not independently reimplemented."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

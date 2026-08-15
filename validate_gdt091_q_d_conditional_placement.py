#!/usr/bin/env python3
"""Aggregate validator for GDT091."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt091_result.json";EFFECTS=ROOT/"gdt091_operator_effects.tsv";NULL=ROOT/"gdt091_permutation_results.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt091_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());e=read(EFFECTS);n=read(NULL);find=lambda x:next(q for q in e if q["operator_contrast"]==x and q["measure"]=="position")
 q=find("Q_ON_O");d=find("D_ON_Y");checks={"capacity":r["matched_tails"]==42 and len(e)==6 and int(q["groups"])==2956 and int(d["groups"])==476,"directions":float(q["observed_target_minus_control"])<-.3 and float(d["observed_target_minus_control"])>.77,"permutation":float(q["two_sided_p"])<.01 and float(n[0]["combined_one_sided_p"])<.05,"status":r["status"]=="Q_EARLY_D_LATE_PLACEMENT_OPPOSITION_CONDITIONAL_ON_HOST_BASE","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==v for fam in ("inputs","outputs","documents","implementation") for name,v in r[fam].items());z=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT091_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT091_Q_D_CONDITIONAL_PLACEMENT_VALIDATION_V1","status":"PASS_BOUND_CONDITIONAL_PLACEMENT_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/effect capacity, q/d directions, permutation thresholds, hashes, seal and ledger; permutation stream is bound but not independently rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

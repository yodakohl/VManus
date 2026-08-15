#!/usr/bin/env python3
"""Aggregate validator for GDT090."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt090_result.json";PAIRS=ROOT/"gdt090_exact_host_pairs.tsv";NULL=ROOT/"gdt090_matched_null.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt090_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());p=read(PAIRS);n=read(NULL);os=next(x for x in p if x["page_host"]=="os");ch=next(x for x in p if x["page_host"]=="ch")
 checks={"capacity":r["loci"]==85 and r["exact_host_pairs"]==len(p)==8 and r["descriptor_patterns"]==11,"means":abs(float(n[0]["observed_mean_jaccard"])-r["observed_mean_jaccard"])<1e-9 and r["observed_mean_jaccard"]<r["null_mean_jaccard"] and r["one_sided_better_p"]>.9,"leaders":float(os["descriptor_jaccard"])==.75 and float(ch["descriptor_jaccard"])>0.66,"status":r["status"]=="EXACT_HOST_WIDE_VISUAL_DESCRIPTOR_STABILITY_NOT_SUPPORTED","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in ("inputs","outputs","documents","implementation") for name,d in r[fam].items());q=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT090_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT090_EXACT_HOST_VISUAL_STABILITY_VALIDATION_V1","status":"PASS_BOUND_EXACT_HOST_STABILITY_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks pair capacity, observed/null means, os/ch rows, hashes, seal and ledger; matched random stream is bound but not independently rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

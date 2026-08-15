#!/usr/bin/env python3
"""Aggregate validator for GDT093."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt093_result.json";SCORES=ROOT/"gdt093_layer_scores.tsv";NULL=ROOT/"gdt093_null_results.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt093_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(SCORES);n=read(NULL);d={x["representation"]:x for x in s if x["descriptor"]=="DARK_LEAF"};checks={"capacity":r["loci"]==85 and r["descriptors"]==8 and r["scanned_cells"]==len(s)==40,"directions":float(d["PAGE_HOST"]["gain_bits"])>4 and all(float(d[x]["gain_bits"])<0 for x in ("HOST_PLUS_WRAPPER","HOST_PLUS_RIGHT","HOST_PLUS_B3","HOST_PLUS_WRAPPER_RIGHT")),"null":float(n[0]["dark_leaf_page_host_local_p"])<.05 and float(n[0]["dark_leaf_page_host_max_search_p"])>.05,"status":r["status"]=="COMPILER_LAYERS_DILUTE_PAGE_HOST_DARK_LEAF_SIGNAL","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==v for fam in ("inputs","outputs","documents","implementation") for name,v in r[fam].items());z=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT093_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT093_COMPILER_LAYER_REINTRODUCTION_VALIDATION_V1","status":"PASS_BOUND_LAYER_ABLATION_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/grid capacity, DARK_LEAF directions, null direction, hashes, seal and ledger; permutation stream is bound but not independently rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

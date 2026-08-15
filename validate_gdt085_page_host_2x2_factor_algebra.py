#!/usr/bin/env python3
"""Independent invariant validator for GDT085."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt085_result.json";CELLS=ROOT/"gdt085_host_renderer_cells.tsv";SCORES=ROOT/"gdt085_held_cell_scores.tsv";SCAN=ROOT/"gdt085_matched_rectangle_scan.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt085_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(SCORES);by={d:sum(float(x["factor_gain_vs_pool"])for x in s if x["dimension"]==d)for d in("WRAPPER","RIGHT_FAMILY","POSITION","REGISTER","DY")};scan=read(SCAN);target=[x for x in scan if x["minimum_cell_occurrences"]=="10"and x["is_target"]=="1"]
 checks={"cells":len(read(CELLS))==r["complete_renderer_cells"]==20 and all(x["cell"]=="PRESENT"for x in read(CELLS)),"scores":len(s)==20 and all(abs(by[d]-r["dimension_summaries"][d]["factor_gain_vs_pool"])<1e-8 for d in by),"localized_success":by["WRAPPER"]>0 and all(by[d]<0 for d in("RIGHT_FAMILY","POSITION","REGISTER","DY")),"scan":len(target)==1 and int(target[0]["rank_by_raw_gain"])==r["threshold10_target_rank"]==1 and sum(x["minimum_cell_occurrences"]=="10"for x in scan)==r["threshold10_rectangles"]==6,"status":r["status"]=="O_Y_HOST_AXIS_PREDICTS_WRAPPER_LICENSE_BUT_FULL_TWO_SLOT_INDEPENDENCE_FAILS","f84_seal":not any(r["f84r"].values())};body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in r[fam].items());q=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT085_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT085_PAGE_HOST_2X2_FACTOR_ALGEBRA_VALIDATION_V1","status":"PASS_BOUND_FACTOR_INVARIANTS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks complete cells, held-cell dimension totals/directions, matched-rectangle rank, hashes, seal and ledger; producer-scored probabilities are bound, not independently reimplemented."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

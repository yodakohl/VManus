#!/usr/bin/env python3
"""Independent aggregate validator for GDT087."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt087_result.json";CELLS=ROOT/"gdt087_wrapper_base_cells.tsv";SCORES=ROOT/"gdt087_wrapper_model_scores.tsv";REGS=ROOT/"gdt087_wrapper_register_gains.tsv";EXC=ROOT/"gdt087_operator_counterexamples.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt087_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());cells=read(CELLS);scores=read(SCORES);regs=read(REGS);exc=read(EXC)
 get=lambda o,b:next(x for x in cells if x["wrapper_outcome"]==o and x["base_axis"]==b)
 selected={x["wrapper_outcome"]:x for x in scores if x["selected"]=="1"}
 checks={
  "panel":r["groups"]==4641 and r["matched_tails"]==42 and len(cells)==10 and all(int(get(o,"o")["occurrences"])+int(get(o,"y")["occurrences"])==4641 for o in r["classifications"]),
  "q_direction":int(get("Q","o")["event_count"])==1746 and int(get("Q","y")["event_count"])==42 and float(selected["Q"]["gain_bits"])>100,
  "d_direction":int(get("D","y")["event_count"])==106 and int(get("D","o")["event_count"])==14 and float(selected["D"]["gain_bits"])>50,
  "selected":len(selected)==5 and int(selected["Q"]["lambda"])==1 and int(selected["D"]["lambda"])==1,
  "registers":sum(x["direction"]=="POSITIVE" for x in regs if x["wrapper_outcome"]=="Q")==5 and sum(x["direction"]=="POSITIVE" for x in regs if x["wrapper_outcome"]=="D")==5,
  "conditional":sum(x["direction"]=="POSITIVE" for x in regs if x["wrapper_outcome"]=="S")==4 and sum(x["direction"]=="POSITIVE" for x in regs if x["wrapper_outcome"]=="CH_FAMILY")==4,
  "exceptions":Counter(x["exception"] for x in exc)==Counter({"Q_ON_Y_EXCEPTION":r["q_y_exceptions"],"D_ON_O_EXCEPTION":r["d_o_exceptions"]}),
  "status":r["status"]=="Q_AND_D_FORM_COMPLEMENTARY_O_Y_HOST_LICENSING_SYSTEM",
  "f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed
 checks["hashes"]=all(sha(ROOT/name)==d for fam in ("inputs","outputs","documents","implementation") for name,d in r[fam].items())
 q=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT087_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT087_OPERATOR_HOST_COMPATIBILITY_VALIDATION_V1","status":"PASS_BOUND_OPERATOR_HOST_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks frozen panel/cells, selected models, register directions, exception accounting, hashes, seal and ledger; held probability stream is bound but not independently reimplemented."}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

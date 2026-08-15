#!/usr/bin/env python3
"""Independent aggregate validator for GDT086."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt086_result.json";CELLS=ROOT/"gdt086_o_y_terminal_cells.tsv";SCORES=ROOT/"gdt086_model_scores.tsv";SCAN=ROOT/"gdt086_base_pair_scan.tsv";COUNTER=ROOT/"gdt086_counterexamples.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt086_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());cells=read(CELLS);scores=read(SCORES);best=next(x for x in scores if x["selected"]=="1");target=next(x for x in read(SCAN)if x["target_o_y"]=="1");checks={"cells":len(cells)==10 and sum(int(x["occurrences"])for x in cells)==r["groups"]==1543 and all(float(next(y for y in cells if y["terminal_axis"]==t and y["base_axis"]=="o")["q_rate"])>float(next(y for y in cells if y["terminal_axis"]==t and y["base_axis"]=="y")["q_rate"])for t in r["terminals"]),"scores":len(scores)==5 and int(best["lambda"])==r["selected_lambda"]==1 and abs(float(best["gain_bits"])-r["held_gain_bits"])<1e-9,"directions":r["positive_terminals"]==5 and r["positive_registers"]==5,"counterexample":len(read(COUNTER))==r["q_y_counterexamples"]==1 and read(COUNTER)[0]["locus"]=="f77r.39","scan":int(target["rank_by_absolute_z"])==r["target_scan_rank"]==2,"status":r["status"]=="Q_OUTER_WRAPPER_SELECTS_O_BASE_ACROSS_FIVE_TERMINALS_AND_ALL_REGISTERS","f84_seal":not any(r["f84r"].values())};body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in r[fam].items());q=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT086_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT086_Q_WRAPPER_O_BASE_SELECTION_VALIDATION_V1","status":"PASS_BOUND_Q_SELECTION_INVARIANTS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks cell counts/directions, retained model, terminal/register signs, counterexample, scan rank, hashes, seal and ledger; held probability stream is bound but not independently reimplemented."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

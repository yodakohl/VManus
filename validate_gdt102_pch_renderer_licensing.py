#!/usr/bin/env python3
"""Bound validator for GDT102."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt102_result.json";OUT=R/"gdt102_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());c=read(R/"gdt102_pch_tail_renderer_counts.tsv");m=read(R/"gdt102_renderer_model_comparison.tsv");x=read(R/"gdt102_cross_register_transfer.tsv");b=dict(r);ch=b.pop("result_content_sha256");by={z["tail"]:z for z in c}
 checks={"counts":len(c)==6 and sum(int(z["source_groups"]) for z in c)==181,"edge_rules":int(by["e"]["dy"])==68 and int(by["d"]["right"])==10 and int(by["ey"]["dy"])+int(by["ey"]["right"])+int(by["y"]["dy"])+int(by["y"]["right"])==0,"models":len(m)==8 and float(next(z for z in m if z["outcome"]=="COARSE" and z["model"]=="FINAL_SOURCE_CHAR")["leave_folio_bits"])<float(next(z for z in m if z["outcome"]=="COARSE" and z["model"]=="PAGE_HOST_TAIL")["leave_folio_bits"]),"transfer":len(x)==16 and {z["train_register"] for z in x}=={"HERBAL_B","STARS_RECIPE_B"},"roles":r["semantic_role"]=="UNASSIGNED" and all(z["semantic_role"]=="UNASSIGNED" for z in c+m+x),"seal":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())};led=[z for z in read(R/"GDT002_YOLO_LEDGER.tsv") if z["checkpoint_id"]=="GDT102_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT102_PCH_RENDERER_LICENSING_VALIDATION_V1","status":"PASS_BOUND_RENDERER_COMPARISON" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks tail counts, edge rules, model ordering, transfer table, bindings, roles, seal, and ledger; it does not independently replay probability accumulation."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

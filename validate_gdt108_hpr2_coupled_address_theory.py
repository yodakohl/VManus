#!/usr/bin/env python3
"""Bound validator for GDT108 theory artifact."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt108_result.json";OUT=R/"gdt108_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());c=read(R/"gdt108_component_status.tsv");t=read(R/"gdt108_theory_comparison.tsv");p=read(R/"gdt108_novel_predictions.tsv");m=json.loads((R/"gdt108_hpr2_coupled_address_model.json").read_text());b=dict(r);ch=b.pop("result_content_sha256")
 checks={"theory":t[0]["theory"]==r["leading_theory"] and int(t[0]["criteria_score"])>int(t[1]["criteria_score"]),"components":len(c)==14 and any(x["component"]=="FINAL_CHARACTER" and x["status"]=="STRONG_FORMAL_COUPLED" for x in c),"predictions":len(p)==7 and all(x["status"]=="FROZEN_NOT_RUN" for x in p),"model":m["semantic_assignments"]==[] and "EDGE_STATE" in m["grammar"],"seal":not any(r["f84r"].values()) and m["f84r"]=="SEALED_NO_PREDICTION","content_hash":csha(b)==ch,"hashes":all(sha(R/k)==v for fam in ("inputs","outputs","documents","implementation") for k,v in r[fam].items())};led=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT108_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT108_HPR2_COUPLED_ADDRESS_THEORY_VALIDATION_V1","status":"PASS_BOUND_THEORY_ARTIFACT" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks bound theory ordering, components, predictions, empty semantics, seal, hashes, and ledger; abductive theory scores are not empirical probabilities."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

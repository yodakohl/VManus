#!/usr/bin/env python3
"""Validator for the GDT092 HPR2 synthesis."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt092_result.json";COMP=ROOT/"gdt092_component_model.tsv";THEORIES=ROOT/"gdt092_theory_comparison.tsv";PRED=ROOT/"gdt092_novel_predictions.tsv";MODEL=ROOT/"gdt092_generative_model.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt092_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());c=read(COMP);t=read(THEORIES);p=read(PRED);m=json.loads(MODEL.read_text());checks={"leading":r["leading_theory"]==m["leading_theory"]=="HYBRID_CONTENT_LEXICON_PLUS_ABBREVIATION_AND_RECORD_COMPILER" and next(x for x in t if x["rank"]=="1")["theory"]==r["leading_theory"],"capacity":r["components"]==len(c)==11 and r["novel_predictions"]==len(p)==6,"roles":all(x["semantic_role"]=="UNASSIGNED" for x in c) and not m["semantic_assignments"],"predictions":all(x["status"]=="FROZEN_NOT_RUN" for x in p) and all("f84r" not in x["target"].lower() for x in p),"grammar":m["grammar"]["OUTER_WRAPPER_COMPATIBILITY"]["Q"]=="O_BASE; EARLY" and m["grammar"]["OUTER_WRAPPER_COMPATIBILITY"]["D"]=="Y_BASE; LATE","status":r["status"]=="HYBRID_PAGE_HOST_LEXICON_PLUS_RECORD_COMPILER_IS_LEADING_GENERATIVE_THEORY","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==v for fam in ("inputs","outputs","documents","implementation") for name,v in r[fam].items());z=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT092_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT092_HPR2_GENERATIVE_THEORY_VALIDATION_V1","status":"PASS_BOUND_GENERATIVE_THEORY_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks selected theory, component/prediction counts, absence of semantic assignments, q/d grammar, input/output hashes, f84 seal and ledger."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

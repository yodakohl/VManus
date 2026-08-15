#!/usr/bin/env python3
"""Bound validator for GDT100 synthesis."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt100_result.json";OUT=R/"gdt100_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());c=read(R/"gdt100_component_status.tsv");t=read(R/"gdt100_theory_comparison.tsv");p=read(R/"gdt100_novel_predictions.tsv");m=json.loads((R/"gdt100_hpr2_revised_model.json").read_text());b=dict(r);ch=b.pop("result_content_sha256")
 checks={"capacity":len(c)==12 and len(t)==3 and len(p)==6,"leading":t[0]["theory"]==r["leading_theory"]==m["leading_theory"],"revision":r["major_revision"]=="PAGE_HOST_CONTENT_LEXICON_TO_UNGROUNDED_CONTENT_ADDRESS_LAYER","no_roles":r["semantic_assignments"]==0 and m["semantic_assignments"]==[] and all(x["semantic_role"]=="UNASSIGNED" for x in p),"predictions":all(x["status"]=="FROZEN_NOT_RUN" for x in p),"f84":not any(r["f84r"].values()) and m["f84r"]=="SEALED_NO_PREDICTION","content_hash":csha(b)==ch,"hashes":all(sha(R/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())};z=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT100_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 ok=all(checks.values());o={"schema":"GDT100_HPR2_THEORY_REVISION_VALIDATION_V1","status":"PASS_BOUND_THEORY_SYNTHESIS" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks bound evidence hashes, theory/component/prediction inventory, no-role and f84 seals; synthesis judgments remain abductive."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

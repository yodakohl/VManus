#!/usr/bin/env python3
"""Bound validator for GDT098."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt098_result.json";OUT=R/"gdt098_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());a=read(R/"gdt098_cross_register_motif_context.tsv");c=read(R/"gdt098_pch_contexts.tsv");s=read(R/"gdt098_pch_annotation_scope.tsv");b=dict(r);ch=b.pop("result_content_sha256");p=next(x for x in a if x["formal_feature"]=="pch")
 checks={"source":r["source_groups"]==15592 and r["pch_source_groups"]==331 and len(c)==183,"registers":r["pch_register_counts"].get("HERBAL_B")==26 and r["pch_register_counts"].get("STARS_RECIPE_B")==157,"atlas":len(a)==84 and p["rank_by_context_cosine"]=="60","scope":len(s)==11 and sum(x["scope_class"]=="PHARMA_PLANT" and x["mixed_spatial_context_positive"]=="1" for x in s)==6 and sum(x["scope_class"]=="OTHER" and x["mixed_spatial_context_positive"]=="0" for x in s)==5,"roles":all(x["semantic_role"]=="UNASSIGNED" for x in a+c+s),"f84":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())};z=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT098_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 ok=all(checks.values());o={"schema":"GDT098_PCH_CROSS_REGISTER_CONTEXT_VALIDATION_V1","status":"PASS_BOUND_CONTEXT_SCOPE" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks source/register/atlas/scope counts and hashes/seal/ledger; does not independently reconstruct residual vectors."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

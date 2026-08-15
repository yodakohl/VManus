#!/usr/bin/env python3
"""Bound validator for GDT106."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt106_result.json";OUT=R/"gdt106_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());s=read(R/"gdt106_edge_stripping_axis_scores.tsv");m=read(R/"gdt106_edge_stripping_summary.tsv");v=read(R/"gdt106_variant_log.tsv");b=dict(r);ch=b.pop("result_content_sha256");by={x["representation"]:x for x in m}
 checks={"panel":r["eligible_loci"]==332 and r["physical_folios"]==19,"matrix":len(s)==72 and len(m)==9 and len(v)==10,"winner":r["winner"]=="FULL_PAGE_HOST" and float(by["FULL_PAGE_HOST"]["summed_gain_vs_nuisance_bits"])>float(by["STRIP_FINAL1"]["summed_gain_vs_nuisance_bits"]),"separation":float(by["CORE_PLUS_EDGE1_SEPARATE"]["summed_gain_vs_nuisance_bits"])<float(by["FULL_PAGE_HOST"]["summed_gain_vs_nuisance_bits"]),"roles":r["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in s+m),"seal":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/k)==z for fam in ("inputs","outputs","documents","implementation") for k,z in r[fam].items())};led=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT106_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT106_HOST_EDGE_STRIPPING_EXTERNAL_TEST_VALIDATION_V1","status":"PASS_BOUND_REPRESENTATION_ORDER" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/matrix/winner/separation/roles/seal/bindings/ledger; does not independently replay the KNN score."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

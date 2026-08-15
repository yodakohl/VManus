#!/usr/bin/env python3
"""Bound validator for GDT099."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt099_result.json";OUT=R/"gdt099_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());a=read(R/"gdt099_subhost_external_atlas.tsv");c=read(R/"gdt099_top_candidate_cases.tsv");b=dict(r);ch=b.pop("result_content_sha256");top=a[0]
 checks={"capacity":r["loci"]==560 and r["physical_folios"]==21 and r["supported_submotifs"]==150,"library":len(a)==557 and r["permutation_worlds"]==5000,"top":top["page_host_submotif"]=="ry$" and top["external_axis"]=="REL_ENCLOSURE","global_none":r["global_survivors"]==0 and float(top["max_search_p"])>.5,"cases":len(c)>0,"roles":all(x["semantic_role"]=="UNASSIGNED" for x in a+c),"f84":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())};z=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT099_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 ok=all(checks.values());o={"schema":"GDT099_SUBHOST_EXTERNAL_ATLAS_VALIDATION_V1","status":"PASS_BOUND_SUBHOST_ATLAS" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks bound capacity/library/top/global ceiling/cases/hashes/seal/ledger; does not independently regenerate null worlds."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

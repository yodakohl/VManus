#!/usr/bin/env python3
"""Bound validator for GDT097."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt097_result.json";OUT=R/"gdt097_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());a=read(R/"gdt097_motif_atlas.tsv");cases=read(R/"gdt097_pch_cases.tsv");b=dict(r);ch=b.pop("result_content_sha256");top=a[0]
 checks={"capacity":r["loci"]==118 and r["physical_folios"]==5 and r["positive_loci"]==34,"library":len(a)==108 and r["permutation_worlds"]==20000,"top":top["representation"]=="PAGE_HOST_CHAR3" and top["formal_feature"]=="pch","cases":len(cases)==6 and all(x["mixed_spatial_context_positive"]=="1" for x in cases),"strata":r["pch_certainty_counts"]=={"HEDGED":2,"UNHEDGED":4},"max_nonconfirm":float(top["max_search_p"])>.1,"roles":all(x["semantic_role"]=="UNASSIGNED" for x in a+cases),"f84":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/n)==v for fam in ("inputs","outputs","documents","implementation") for n,v in r[fam].items())};z=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT097_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]
 ok=all(checks.values());o={"schema":"GDT097_PCH_SPATIAL_CONTEXT_MOTIF_VALIDATION_V1","status":"PASS_BOUND_MOTIF_ATLAS" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks capacity, library, top motif/cases/certainty, maxT ceiling, hashes, seal and ledger; does not independently regenerate permutations."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

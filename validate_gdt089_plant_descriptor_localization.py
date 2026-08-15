#!/usr/bin/env python3
"""Aggregate validator for GDT089."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt089_result.json";MANIFEST=ROOT/"gdt089_descriptor_manifest.tsv";SCORES=ROOT/"gdt089_representation_scores.tsv";LEADS=ROOT/"gdt089_exact_host_descriptor_leads.tsv";CASES=ROOT/"gdt089_os_cases.tsv";NULL=ROOT/"gdt089_null_results.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt089_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());m=read(MANIFEST);s=read(SCORES);l=read(LEADS);c=read(CASES);n=read(NULL);find=lambda d,x:next(q for q in s if q["descriptor"]==d and q["representation"]==x)
 checks={"capacity":r["loci"]==85 and r["physical_folios"]==6 and len(m)==11 and sum(x["eligible"]=="1" for x in m)==8 and len(s)==24,"dark_leaf":float(find("DARK_LEAF","PAGE_HOST_CHAR3")["gain_bits"])>4 and float(find("DARK_LEAF","RAW_CHAR3")["gain_bits"])<0 and float(find("DARK_LEAF","COMPILER_ONLY")["gain_bits"])<0,"os_cases":len(c)==2 and {x["locus"] for x in c}=={"f88v.13","f100v.13"} and all(x["dark_leaf"]==x["light_root"]=="1" for x in c),"os_leads":any(x["page_host"]=="os" and x["descriptor"]=="DARK_LEAF" and x["positive_loci"]==x["all_host_loci"]=="2" for x in l),"global":float(n[0]["global_max_search_p"])>.05 and int(n[0]["scanned_pairs"])==24,"roles":r["os_visual_association"]["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in l),"status":r["status"]=="PAGE_HOST_DARK_LEAF_DESCRIPTOR_LEAD_WEAK_POSTSELECTED","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in ("inputs","outputs","documents","implementation") for name,d in r[fam].items());q=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT089_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT089_PLANT_DESCRIPTOR_LOCALIZATION_VALIDATION_V1","status":"PASS_BOUND_DESCRIPTOR_LOCALIZATION_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/descriptor capacity, representation directions, exact os cases/leads, max-search control, roles, hashes, seal and ledger; permutation stream is bound but not independently rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

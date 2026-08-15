#!/usr/bin/env python3
"""Aggregate validator for GDT088."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt088_result.json";ATLAS=ROOT/"gdt088_page_host_external_atlas.tsv";NULL=ROOT/"gdt088_null_results.tsv";COUNTER=ROOT/"gdt088_counterexamples.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt088_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());a=read(ATLAS);n=read(NULL);c=read(COUNTER);top=a[0]
 find=lambda h,x:next(z for z in a if z["page_host"]==h and z["external_axis"]==x)
 checks={"capacity":r["units"]==560 and r["hosts"]==43 and r["scanned_pairs"]==len(a)==284,"top":top["page_host"]=="os" and top["external_axis"]=="PLANT" and abs(float(top["cmh_z"])-3.655508930735619)<1e-9,"d_leads":float(find("d","REL_ENCLOSURE")["cmh_z"])>2.9 and float(find("d","REL_EXPLICIT_ATTACHMENT")["cmh_z"])>2.4,"ok_lead":float(find("ok","WATER_OR_APPARATUS")["cmh_z"])>2.1,"global":float(top["max_search_p"])>.05 and int(n[0]["scanned_pairs"])==284,"counterexamples":len(c)>0 and any(x["page_host"]=="ok" for x in c),"roles":all(x["semantic_role"]=="UNASSIGNED" for x in r["frozen_followup_candidates"]),"status":r["status"]=="EXACT_PAGE_HOST_ARCHIVE_ASSOCIATIONS_FOUND_NONE_SURVIVE_GLOBAL_SEARCH","f84_seal":not any(r["f84r"].values())}
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed;checks["hashes"]=all(sha(ROOT/name)==d for fam in ("inputs","outputs","documents","implementation") for name,d in r[fam].items());q=[x for x in read(LEDGER) if x["checkpoint_id"]=="GDT088_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT088_PAGE_HOST_EXTERNAL_ASSOCIATION_VALIDATION_V1","status":"PASS_BOUND_EXPLORATORY_ATLAS_INVARIANTS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks atlas capacity, named lead statistics, global control direction, counterexamples, hashes, seal and ledger; permutation stream is bound but not independently rerun."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

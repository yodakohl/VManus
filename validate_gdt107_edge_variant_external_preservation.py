#!/usr/bin/env python3
"""Bound validator for GDT107."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/"gdt107_result.json";OUT=R/"gdt107_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RESULT.read_text());p=read(R/"gdt107_edge_variant_pairs.tsv");s=read(R/"gdt107_edge_variant_scores.tsv");n=read(R/"gdt107_null_summary.tsv");b=dict(r);ch=b.pop("result_content_sha256");by={x["axis_scope"]:x for x in s}
 checks={"panel":r["units"]==319 and r["pairs"]==124 and r["cores"]==28,"matches":r["match_states"]=={"EDGE_RELAXED":17,"EXACT_EDGE":107},"scores":len(s)==3 and len(n)==3 and float(by["OBJECT_AXIS"]["inclusive_p"])>.5 and float(by["RELATION_AXIS"]["inclusive_p"])>.05,"roles":r["semantic_role"]=="UNASSIGNED" and all(x["semantic_role"]=="UNASSIGNED" for x in p+s),"seal":not any(r["f84r"].values()),"content_hash":csha(b)==ch,"hashes":all(sha(R/k)==v for fam in ("inputs","outputs","documents","implementation") for k,v in r[fam].items())};led=[x for x in read(R/"GDT002_YOLO_LEDGER.tsv") if x["checkpoint_id"]=="GDT107_CKPT001"];checks["ledger"]=len(led)==1 and led[0]["status"]==r["status"];ok=all(checks.values());o={"schema":"GDT107_EDGE_VARIANT_EXTERNAL_PRESERVATION_VALIDATION_V1","status":"PASS_BOUND_MATCHED_SUMMARY" if ok else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks panel/pair/core/match counts, score directions, roles, seal, bindings, and ledger; deterministic null stream is bound, not independently replayed."};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":o["status"],"checks":f"{o['checks_passed']}/{o['checks_total']}"}));raise SystemExit(0 if ok else 1)
if __name__=="__main__":main()

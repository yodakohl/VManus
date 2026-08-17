#!/usr/bin/env python3
"""Retained-artifact and arithmetic validation for GDT187."""
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"gdt187_result.json"; VALID=ROOT/"gdt187_validation.json"
INVENTORY=ROOT/"gdt187_page_inventory.tsv"; SCORES=ROOT/"gdt187_similarity_scores.tsv"
NULLS=ROOT/"gdt187_null_results.tsv"; COUNTER=ROOT/"gdt187_counterexamples.tsv"
METHOD=ROOT/"GDT187_KEYED_OMISSION_TEST_METHOD.md"; REPORT=ROOT/"GDT187_KEYED_OMISSION_TEST_REPORT.md"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding="utf8") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());inv=read(INVENTORY);scores=read(SCORES);nulls=read(NULLS);counter=read(COUNTER);checks=[]
 def ck(n,c):assert c,n;checks.append(n)
 ck("status",r["status"]=="FOXTON_KEYED_OMISSION_NOT_SUPPORTED_REGISTER_LOCAL_WEAK_LEAD")
 ck("page_count",len(inv)==23==r["counts"]["pages"])
 ck("folio_count",len({x["physical_folio"] for x in inv})==11==r["counts"]["physical_folios"])
 ck("sections",{x["section"] for x in inv}=={"P","B"})
 ck("metric_count",len(scores)==10==len(nulls)==r["counts"]["metrics"])
 ck("metric_unique",len({(x["scope"],x["representation"]) for x in scores})==10)
 ck("null_worlds",all(int(x["worlds"])==432 for x in nulls))
 ck("p_bounds",all(0<=float(x["local_exact_p"])<=1 and 0<=float(x["max_ten_p"])<=1 for x in scores))
 ck("top_resolves",any(x["scope"]==r["top_metric"]["scope"] and x["representation"]==r["top_metric"]["representation"] for x in scores))
 ck("gates_fail",not r["decision_gates"]["all_pass"])
 ck("label_groups",sum(int(x["label_groups"]) for x in inv)==r["counts"]["label_groups"])
 ck("label_types",sum(int(x["label_host_types"]) for x in inv)==r["counts"]["label_host_types"])
 ck("prose_groups",sum(int(x["prose_groups"]) for x in inv)==r["counts"]["prose_groups"])
 ck("overlap_groups",sum(int(x["label_group_exact_host_overlap_all"]) for x in inv)==r["exact_overlap"]["label_groups_anywhere_in_prose"])
 ck("overlap_types",sum(int(x["label_type_exact_host_overlap_all"]) for x in inv)==r["exact_overlap"]["label_types_anywhere_in_prose"])
 ck("overlap_opening",sum(int(x["label_group_exact_host_overlap_opening"]) for x in inv)==r["exact_overlap"]["label_groups_on_opening_lines"])
 ck("counterexamples",len(counter)==5)
 ck("no_f84_outputs",all("f84" not in p.read_text().lower() for p in (INVENTORY,SCORES,NULLS,COUNTER)))
 ck("f84_flags",not r["f84r_accessed"] and not r["provenance"]["f84r_formal_payload_retained_parsed_joined_scored"])
 ck("output_hashes",all(r["outputs"][p.name]==sha(p) for p in (INVENTORY,SCORES,NULLS,COUNTER)))
 ck("document_hashes",r["documents"][METHOD.name]==sha(METHOD) and r["documents"][REPORT.name]==sha(REPORT))
 ck("implementation_hash",r["implementation"]==sha(ROOT/"run_gdt187_keyed_omission_test.py"))
 out={"experiment":"GDT187_VALIDATION","status":"PASS_RETAINED_ARITHMETIC","checks":len(checks),"check_names":checks,"result_sha256":sha(RESULT),"scope":"retained outputs/arithmetic; exact-null search is reproduced by the bound producer"}
 VALID.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n");print("PASS",len(checks))
if __name__=="__main__":main()

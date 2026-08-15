#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT058."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt058_result.json";TESTS=ROOT/"gdt058_q2_context_tests.tsv";OCC=ROOT/"gdt058_q2_context_inventory.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt058_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());tests=read(TESTS);occ=read(OCC);checks={}
 checks["test_grid"]=len(tests)==8 and {(x["context"],x["feature"])for x in tests}=={(c,f)for c in("GROUP_INITIAL_Q2","INTERNAL_A1Q2")for f in("normalized_line_position","normalized_field_index","normalized_within_field_position","after_dy")}
 checks["inventory_count"]=len(occ)==r["q2_groups"]==1307 and r["q2_member_occurrences"]==1315 and sum(int(x["group_initial_q2"])for x in occ)==234 and sum(int(x["internal_a1q2"])for x in occ)==873
 checks["f84_excluded"]=not any(x["locus"].startswith("f84r")for x in occ)and not any(r["f84r"].values())
 by={(x["context"],x["feature"]):x for x in tests};il=by["GROUP_INITIAL_Q2","normalized_line_position"];af=by["INTERNAL_A1Q2","normalized_field_index"]
 checks["initial_headline"]=int(il["matched_strata"])==153 and int(il["target_groups"])==172 and close(il["effect_target_minus_control"],-.133995836581)and float(il["bonferroni_8_p"])<.05 and float(il["lofo_max_effect"])<0
 checks["internal_headline"]=int(af["matched_strata"])==362 and int(af["target_groups"])==575 and close(af["effect_target_minus_control"],.0598028475385)and float(af["bonferroni_8_p"])<.05 and float(af["lofo_min_effect"])>0
 checks["opposite_direction"]=float(il["effect_target_minus_control"])<0<float(af["effect_target_minus_control"])
 body=dict(r);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in r[fam].items())and all(sha(ROOT/name)==digest for name,digest in r["implementation"].items())
 checks["claim_ceiling"]=r["status"]=="Q2_HAS_CONTEXT_CONDITIONED_EARLY_INITIAL_VS_LATER_INTERNAL_PLACEMENT"and"do not collapse"in r["generative_update"]and"distinct from the display-q/Q1"in r["generative_update"]and"no operator meaning"in r["claim_ceiling"]
 ledger=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT058_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==r["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT058_Q2_CONTEXT_BIFURCATION_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Artifact grid/counts, frozen headline statistics, opposite-direction decision, hashes, f84 exclusion, ledger, and claim ceiling. Permutation engine is producer-validated rather than independently reimplemented."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

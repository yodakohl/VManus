#!/usr/bin/env python3
"""Validator for GDT056 source-native sensitivity."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt056_result.json";PAIRS=ROOT/"gdt056_source_native_a1q2_pairs.tsv";TESTS=ROOT/"gdt056_source_native_a1q2_tests.tsv";OUT=ROOT/"gdt056_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());p=read(PAIRS);t=read(TESTS);checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("counts",len(p)==r["paired_rows"]==41 and r["stable_source_groups"]==7973);ck("three_tests",len(t)==len(r["tests"])==3);ck("source_operation",all((x["q2_present"]=="1")==("A1 Q2"in x["source_codes"])for x in p));field=r["tests"][0];ck("field_direction",field["effect_q2_minus_base"]>0 and field["permutation_p"]<.05 and field["bonferroni_3_p"]>.05);ck("f84",not any(x["locus"].startswith("f84r")for x in p)and not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="SOURCE_NATIVE_A1Q2_LATER_FIELD_TRANSFER_DIRECTIONAL_LOW_CAPACITY");ck("ceiling","no Q2 meaning"in r["claim_ceiling"]and"translation"in r["claim_ceiling"])
 status="PASS_OUTPUTS_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";o={"schema":"GDT056_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{o["checks_passed"]}/{o["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()

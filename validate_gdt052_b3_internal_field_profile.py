#!/usr/bin/env python3
"""Independent count/hash validator for GDT052."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt052_result.json";LINES=ROOT/"gdt052_b3_line_profiles.tsv";TESTS=ROOT/"gdt052_b3_profile_tests.tsv";OUT=ROOT/"gdt052_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());lines=read(LINES);tests=read(TESTS);checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("line_count",len(lines)==r["lines"]==1164);ck("b3_count",sum(x["b3_close"]=="1"for x in lines)==r["b3_closers"]==145);ck("internal_sum",sum(int(x["internal_dy_count"])for x in lines if x["b3_close"]=="1")==r["tests"][0]["observed_sum"]==197);ck("test_count",len(tests)==len(r["tests"])==4);ck("all_nonconfirming",all(float(x["bonferroni_4_p"])>.05 for x in tests));ck("prediction_failed",r["hpr2_prediction"]=="HPR2_P02"and r["prediction_outcome"]=="FALSIFIED");ck("f84",not any(x["locus"].startswith("f84r")for x in lines)and not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="B3_CLOSE_DOES_NOT_PREDICT_INTERNAL_DY_FIELD_COUNT");ck("ceiling","B3 endpoint status remains"in r["claim_ceiling"]and"meaning"in r["claim_ceiling"])
 status="PASS_COUNTS_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";o={"schema":"GDT052_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{o["checks_passed"]}/{o["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()

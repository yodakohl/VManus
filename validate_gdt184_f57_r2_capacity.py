#!/usr/bin/env python3
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(n):
 with (ROOT/n).open(encoding="utf-8") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads((ROOT/"gdt184_result.json").read_text()); c=rows("gdt184_r2_capacity.tsv");m=rows("gdt184_r2_model_comparison.tsv");x=rows("gdt184_counterexamples.tsv");checks=[]
 d={z["quantity"]:float(z["value"]) for z in c};assert d["periods"]==4 and d["positions_per_period"]==17;checks.append("dimensions")
 assert d["all_reading_stable_changing_columns"]==1 and d["stable_noncontrasting_columns"]==16;checks.append("column_capacity")
 assert d["unique_stable_period_profiles"]==2 and d["stable_profile_capacity_bits"]==1;checks.append("profile_bits")
 assert r["capacity"]=={"available_bits":1.0,"required_unique_sector_bits":2,"deficit_bits":1};checks.append("deficit")
 assert next(z for z in m if z["rank"]=="1")["model"]=="FOURFOLD_REFERENCE_OR_CALIBRATION_SEQUENCE";checks.append("leading_model")
 assert next(z for z in m if z["model"]=="FOUR_ELEMENT_ID_TABLE")["fit"]=="FAILED_CAPACITY";checks.append("failed_id_table")
 assert len(x)==5;checks.append("counterexamples")
 for n,digest in r["inputs"].items():assert sha(ROOT/n)==digest;checks.append("input:"+n)
 for n,digest in r["outputs"].items():assert sha(ROOT/n)==digest;checks.append("output:"+n)
 for n,digest in r["documents"].items():assert sha(ROOT/n)==digest;checks.append("document:"+n)
 assert sha(ROOT/"build_gdt184_f57_r2_capacity.py")==r["implementation"];checks.append("implementation")
 assert not r["f84r_accessed"];checks.append("f84r_seal")
 v={"experiment":r["experiment"],"status":"PASS","checks_passed":len(checks),"checks":checks,"result_sha256":sha(ROOT/"gdt184_result.json")};(ROOT/"gdt184_validation.json").write_text(json.dumps(v,sort_keys=True,indent=2)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Validator for GDT055 output arithmetic and bindings."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt055_result.json";OCC=ROOT/"gdt055_complete_line_o_ot_contexts.tsv";TESTS=ROOT/"gdt055_field_decomposition_tests.tsv";OUT=ROOT/"gdt055_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());o=read(OCC);t=read(TESTS);checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("complete_count",r["complete_groups"]==8774);ck("test_count",len(t)==len(r["tests"])==12);ck("occ_f84",not any(x["locus"].startswith("f84r")for x in o));get=lambda c,f:next(x for x in r["tests"]if x["contrast"]==c and x["feature"]==f);ck("field_transfer",get("BASE_TO_OT","normalized_field_index")["effect_b_minus_a"]>0 and get("BASE_TO_OT","normalized_field_index")["loho_min_effect"]>0);ck("within_null",abs(get("BASE_TO_OT","normalized_within_field_position")["effect_b_minus_a"])<.03);ck("o_early",get("BASE_TO_O","normalized_within_field_position")["effect_b_minus_a"]<0);ck("after_dy",get("BASE_TO_OT","after_dy")["effect_b_minus_a"]>0);ck("f84",not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="OT_IS_LATER_FIELD_POST_DY_RENDERER_O_IS_EARLY_INTRAFIELD_RENDERER");ck("ceiling","no lexical"in r["claim_ceiling"]and"meaning"in r["claim_ceiling"])
 status="PASS_OUTPUTS_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";q={"schema":"GDT055_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(q,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{q["checks_passed"]}/{q["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()

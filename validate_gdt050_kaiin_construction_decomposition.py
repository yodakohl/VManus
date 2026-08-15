#!/usr/bin/env python3
"""Independent table/hash validator for GDT050."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt050_result.json";TABLE=ROOT/"gdt050_kaiin_construction_table.tsv";OCC=ROOT/"gdt050_kaiin_occurrences.tsv";OUT=ROOT/"gdt050_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());table=read(TABLE);occ=read(OCC);checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("five_cells",[x["suffix"]for x in table]==["aiin","air","ain","ar","al"]);ck("kaiin_count",len(occ)==r["kaiin_occurrences"]==48);ck("kaiin_identity",all(x["base"]=="k"and x["suffix"]=="aiin"for x in occ));ck("cell_sum",sum(int(x["target_total"])+int(x["control_total"])for x in table)==140)
 aiin=next(x for x in table if x["suffix"]=="aiin");t=r["tests"]["AIIN_WITHIN_K"];ck("aiin_table",[int(aiin["target_total"]),sum(int(x["target_total"])for x in table if x["suffix"]!="aiin"),int(aiin["control_total"]),sum(int(x["control_total"])for x in table if x["suffix"]!="aiin")]==[t["target_positive"],t["target_negative"],t["control_positive"],t["control_negative"]]);ck("all_nonsignificant",all(x["two_sided_fisher_p"]>.05 for x in r["tests"].values()));ck("f84",not any(x["locus"].startswith("f84r")for x in occ)and not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="KAIIN_RESIDUAL_ATTRIBUTED_TO_COMMON_K_AND_AIIN_FAMILY");ck("ceiling","no function"in r["claim_ceiling"]and"meaning"in r["claim_ceiling"])
 status="PASS_TABLE_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";p={"schema":"GDT050_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{p["checks_passed"]}/{p["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()

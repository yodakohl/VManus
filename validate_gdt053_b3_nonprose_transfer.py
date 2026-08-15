#!/usr/bin/env python3
"""Independent count/hash validator for GDT053."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt053_result.json";GROUPS=ROOT/"gdt053_nonprose_member_groups.tsv";ATLAS=ROOT/"gdt053_nonprose_final_member_atlas.tsv";OUT=ROOT/"gdt053_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
 r=json.loads(RESULT.read_text());g=read(GROUPS);a=read(ATLAS);checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("counts",len(g)==r["groups"]==602 and len({x["locus"]for x in g})==r["complete_loci"]==517);ck("complete",all(len([y for y in g if y["locus"]==x["locus"]])==int(x["group_count"])for x in g));b=[x for x in g if x["final_member"]=="B3"];ck("b3",len(b)==r["b3"]["support"]==36 and sum(x["is_locus_final"]=="1"for x in b)==r["b3"]["observed_final"]==32);ck("atlas",len(a)==r["member_classes"]==6 and a[0]["final_member"]=="B3");ck("prediction",r["prediction_outcome"]=="DIRECTIONAL_LOW_CAPACITY_NOT_CONFIRMING");ck("f84",not any(x["locus"].startswith("f84r")for x in g)and not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="B3_NONPROSE_ENDPOINT_TRANSFER_DIRECTIONAL_LOW_CAPACITY");ck("ceiling","not punctuation"in r["claim_ceiling"]and"meaning"in r["claim_ceiling"])
 status="PASS_COUNTS_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";o={"schema":"GDT053_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{o["checks_passed"]}/{o["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()

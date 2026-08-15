#!/usr/bin/env python3
"""Independent arithmetic/hash validator for GDT054."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";RESULT=ROOT/"gdt054_result.json";HOSTS=ROOT/"gdt054_unseen_host_profiles.tsv";TESTS=ROOT/"gdt054_position_tests.tsv";OUT=ROOT/"gdt054_validation.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def pos(r):
 i=int(r["group_index"]);n=int(r["group_count"]);return(i-1)/(n-1)if n>1 else.5
def effect(rows,bases,a,b):
 z=[]
 for h in bases:
  by=defaultdict(lambda:[[],[]])
  for r in rows:
   if r["residual_host"]==a+h:by[r["page"]][0].append(pos(r))
   elif r["residual_host"]==b+h:by[r["page"]][1].append(pos(r))
  z.extend((h,p,x,y)for p,(x,y)in by.items()if x and y)
 num=den=0.
 for h,p,x,y in z:w=len(x)*len(y)/(len(x)+len(y));num+=w*(sum(y)/len(y)-sum(x)/len(x));den+=w
 return num/den,len(z),len({x[0]for x in z})
def main():
 r=json.loads(RESULT.read_text());rows=read(SOURCE);hosts=read(HOSTS);tests=read(TESTS);bases=[x["base_host"]for x in hosts];checks=[]
 def ck(n,x):checks.append({"name":n,"pass":bool(x)})
 ck("input",len(rows)==r["strict_groups"]==15592 and not any(x["locus"].startswith("f84r")for x in rows));ck("host_count",len(bases)==r["eligible_ladders"]==49 and not set(bases)&{"ar","al","ol"})
 for name,a,b in(("BASE_TO_OT","","ot"),("BASE_TO_O","","o"),("O_TO_OT","o","ot")):
  e,s,h=effect(rows,bases,a,b);stored=next(x for x in r["tests"]if x["contrast"]==name);ck(name,abs(e-stored["position_effect_b_minus_a"])<1e-12 and s==stored["shared_page_host_strata"]and h==stored["held_hosts"])
 ck("directions",r["tests"][0]["loho_min_effect"]>0 and r["tests"][1]["position_effect_b_minus_a"]<0 and r["tests"][2]["position_effect_b_minus_a"]>0);ck("prediction",r["prediction_outcome"]=="SUPPORTED_FORMAL_POSITIONAL_TRANSFER");ck("f84",not any(r["f84r"].values()))
 for bucket in("inputs","outputs","documents","implementation"):
  for name,d in r[bucket].items():ck(bucket+":"+name,sha(ROOT/name)==d)
 ck("decision",r["status"]=="O_EARLY_OT_LATE_POSITIONAL_RENDERER_TRANSFERS_TO_UNSEEN_HOSTS");ck("ceiling","no bounded/interior"in r["claim_ceiling"]and"meaning"in r["claim_ceiling"])
 status="PASS_ARITHMETIC_AND_HASH_BINDINGS"if all(x["pass"]for x in checks)else"FAIL";o={"schema":"GDT054_VALIDATION_V1","status":status,"checks_passed":sum(x["pass"]for x in checks),"checks_total":len(checks),"checks":checks,"result_sha256":sha(RESULT)};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"checks":f'{o["checks_passed"]}/{o["checks_total"]}'},sort_keys=True));raise SystemExit(0 if status.startswith("PASS")else 1)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Independent exact reconstruction for GDT043."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt016_group_state_inventory.tsv";OCC=ROOT/"gdt043_od_ain_occurrences.tsv";TESTS=ROOT/"gdt043_variant_tests.tsv";STACK=ROOT/"gdt043_od_stack_tests.tsv";RESULT=ROOT/"gdt043_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt043_validation.json"
REGS=("HB","SB","HA","OB")
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reg(r):
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["currier"]=="B":return"OB"
 return"OUT"
def parse(r):
 p=r["stripped_prefix"];outer=p if p in{"q","ch","che","sh","s","t"}else"NONE";rem="d"+r["residual_host"]if p=="d"else r["residual_host"]
 if rem.startswith("od")and len(rem)>2:return outer,1,1,rem[2:]
 if rem.startswith("o")and len(rem)>1:return outer,1,0,rem[1:]
 if rem.startswith("d")and len(rem)>1:return outer,0,1,rem[1:]
 return outer,0,0,rem
def fisher(a,b,c,d):
 n=a+b+c+d;K=a+c;k=a+b;den=math.comb(n,k);return sum(math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(a,min(K,k)+1))
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def interaction(rows,regs):
 by=defaultdict(list)
 for r in rows:
  if r["register"]in regs:by[r["physical_folio"],r["outer_wrapper"],r["base_host"]].append(r)
 pm={0:1.};obs=0;exp=0.;strata=0
 for z in by.values():
  n=len(z);O=sum(r["outer_o"]for r in z);D=sum(r["inner_d"]for r in z)
  if not O or not D:continue
  strata+=1;obs+=sum(r["outer_o"]and r["inner_d"]for r in z);exp+=O*D/n;pm=conv(pm,hyper(n,O,D))
 return obs,exp,obs-exp,strata,sum(p for x,p in pm.items()if x>=obs)
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 checks={};parsed=[]
 for r in read(SOURCE):
  checks.setdefault("f84_source_excluded",True);checks["f84_source_excluded"]&=not r["locus"].startswith("f84r")
  outer,o,d,base=parse(r);rr=reg(r)
  if rr=="OUT"or not base or base=="y":continue
  parsed.append({**r,"register":rr,"outer_wrapper":outer,"outer_o":o,"inner_d":d,"base_host":base})
 family=[]
 for r in parsed:
  if r["outer_o"]and r["inner_d"]and r["base_host"]in{"ain","aiin"}:
   family.append({k:str(r[k])for k in("locus","page","physical_folio","section","currier","hand","register","group_index","group_count","token","outer_wrapper","base_host","record_state")}|{"variant":"SHORT_AIN"if r["base_host"]=="ain"else"LONG_AIIN"})
 family.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])))
 checks["occurrences_exact"]=family==read(OCC)and len(family)==115
 c=Counter((r["register"],r["variant"])for r in family);expected={"HB":(3,6),"SB":(15,29),"HA":(4,48),"OB":(2,8)}
 checks["register_counts_exact"]=all((c[rg,"SHORT_AIN"],c[rg,"LONG_AIIN"])==v for rg,v in expected.items())
 actual=read(TESTS);primary=next(r for r in actual if r["comparison"]=="HB+SB_VS_HA+OB")
 checks["primary_exact"]=primary["short"]=="18"and primary["long"]=="35"and primary["comparison_short"]=="6"and primary["comparison_long"]=="56"and close(primary["one_sided_p"],fisher(18,35,6,56))
 checks["directions_exact"]=close(next(r for r in actual if r["comparison"]=="HB_VS_HA")["one_sided_p"],fisher(3,6,4,48))and close(next(r for r in actual if r["comparison"]=="SB_VS_OB")["one_sided_p"],fisher(15,29,2,8))
 ok=True
 for regs in(("HB",),("SB",),("HA",),("OB",),("HB","SB")):
  obs,exp,exc,n,p=interaction(parsed,regs);a=next(r for r in actual if r["test"]=="O_D_COMPATIBILITY"and r["comparison"]=="+".join(regs));ok&=a["eligible_observed"]==str(obs)and close(a["eligible_expected"],exp)and close(a["eligible_excess"],exc)and a["eligible_strata"]==str(n)and close(a["one_sided_p"],p)
 checks["all_od_interactions_exact"]=ok and read(STACK)==actual[3:]
 control_rate=6/62;target_folios=sorted({r["physical_folio"]for r in family if r["register"]in{"HB","SB"}});lo=[]
 for f in target_folios:
  z=[r for r in family if r["register"]in{"HB","SB"}and r["physical_folio"]!=f];cc=Counter(r["variant"]for r in z);lo.append(cc["SHORT_AIN"]/(cc["SHORT_AIN"]+cc["LONG_AIIN"])-control_rate)
 result=json.loads(RESULT.read_text());checks["lofo_exact"]=close(result["lofo_min_rate_difference"],min(lo))and min(lo)>0
 body=dict(result);claim=body.pop("result_content_sha256");checks["result_hash"]=csha(body)==claim;checks["status"]=result["status"]=="ODAIN_IS_BS_ENRICHED_SHORT_VARIANT_OF_OD_AIN_FAMILY";checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT043_OD_AIN_VARIANT_REPORT.md").read_text();checks["claim_ceiling"]="indivisible content stem"in report and"does **not** show"in report and"No meaning"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT043_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT043_OD_AIN_VARIANT_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent OD+AIN/AIIN occurrence, exact contingency, O-D compatibility, and hash reconstruction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()

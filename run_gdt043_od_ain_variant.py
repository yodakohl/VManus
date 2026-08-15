#!/usr/bin/env python3
"""GDT043: attribute ODAIN to an OD + AIN/AIIN formal variant system."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt016_group_state_inventory.tsv"
METHOD=ROOT/"GDT043_OD_AIN_VARIANT_METHOD.md"
REPORT=ROOT/"GDT043_OD_AIN_VARIANT_REPORT.md"
OCC=ROOT/"gdt043_od_ain_occurrences.tsv"
TESTS=ROOT/"gdt043_variant_tests.tsv"
STACK=ROOT/"gdt043_od_stack_tests.tsv"
RESULT=ROOT/"gdt043_result.json"
REGS=("HB","SB","HA","OB")

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def reg(r):
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["currier"]=="B":return"OB"
 return"OUT"
def parse(r):
 p=r["stripped_prefix"]
 outer=p if p in{"q","ch","che","sh","s","t"}else"NONE"
 rem="d"+r["residual_host"]if p=="d"else r["residual_host"]
 if rem.startswith("od")and len(rem)>2:o,d,base=1,1,rem[2:]
 elif rem.startswith("o")and len(rem)>1:o,d,base=1,0,rem[1:]
 elif rem.startswith("d")and len(rem)>1:o,d,base=0,1,rem[1:]
 else:o,d,base=0,0,rem
 return outer,o,d,base
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 out=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():out[i+j]+=p*q
 return dict(out)
def fisher_greater(a,b,c,d):
 n=a+b+c+d;K=a+c;k=a+b;lo=max(0,k-(n-K));hi=min(K,k);den=math.comb(n,k)
 return sum(math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(a,lo),hi+1))
def interaction(rows,regs):
 z=[r for r in rows if r["register"]in regs];by=defaultdict(list)
 for r in z:by[r["physical_folio"],r["outer_wrapper"],r["base_host"]].append(r)
 pmf={0:1.};obs=0;exp=0.;strata=0
 for a in by.values():
  n=len(a);O=sum(r["outer_o"]for r in a);D=sum(r["inner_d"]for r in a)
  if not O or not D:continue
  strata+=1;obs+=sum(r["outer_o"]and r["inner_d"]for r in a);exp+=O*D/n;pmf=conv(pmf,hyper(n,O,D))
 return{"test":"O_D_COMPATIBILITY","comparison":"+".join(regs),"short":sum(r["outer_o"]and r["inner_d"]for r in z),"long":len(z)-sum(r["outer_o"]and r["inner_d"]for r in z),"comparison_short":"NA","comparison_long":"NA","rate_difference":"NA","one_sided_p":sum(p for x,p in pmf.items()if x>=obs),"eligible_observed":obs,"eligible_expected":exp,"eligible_excess":obs-exp,"eligible_strata":strata,"notes":"Exact O-D compatibility with base+outer-wrapper+folio margins fixed"}

def main():
 raw=read(SOURCE);parsed=[]
 for r in raw:
  assert not r["locus"].startswith("f84r")
  outer,o,d,base=parse(r);rr=reg(r)
  if rr=="OUT"or not base or base=="y":continue
  parsed.append({**r,"register":rr,"outer_wrapper":outer,"outer_o":o,"inner_d":d,"base_host":base,"double_od":int(o and d)})
 family=[]
 for r in parsed:
  if r["double_od"]and r["base_host"]in{"ain","aiin"}:
   family.append({k:str(r[k])for k in("locus","page","physical_folio","section","currier","hand","register","group_index","group_count","token","outer_wrapper","base_host","record_state")}|{"variant":"SHORT_AIN"if r["base_host"]=="ain"else"LONG_AIIN"})
 family.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])))
 write(OCC,family,list(family[0]))
 counts=Counter((r["register"],r["variant"])for r in family)
 def row(name,left,right):
  a=counts[left,"SHORT_AIN"];b=counts[left,"LONG_AIIN"];c=counts[right,"SHORT_AIN"];d=counts[right,"LONG_AIIN"]
  return{"test":"OD_AIN_SHORT_VARIANT","comparison":name,"short":a,"long":b,"comparison_short":c,"comparison_long":d,"rate_difference":a/(a+b)-c/(c+d),"one_sided_p":fisher_greater(a,b,c,d),"eligible_observed":"NA","eligible_expected":"NA","eligible_excess":"NA","eligible_strata":"NA","notes":f"{left} short fraction versus {right}"}
 tests=[row("HB_VS_HA","HB","HA"),row("SB_VS_OB","SB","OB")]
 target=Counter({"SHORT_AIN":counts["HB","SHORT_AIN"]+counts["SB","SHORT_AIN"],"LONG_AIIN":counts["HB","LONG_AIIN"]+counts["SB","LONG_AIIN"]})
 control=Counter({"SHORT_AIN":counts["HA","SHORT_AIN"]+counts["OB","SHORT_AIN"],"LONG_AIIN":counts["HA","LONG_AIIN"]+counts["OB","LONG_AIIN"]})
 tests.append({"test":"OD_AIN_SHORT_VARIANT","comparison":"HB+SB_VS_HA+OB","short":target["SHORT_AIN"],"long":target["LONG_AIIN"],"comparison_short":control["SHORT_AIN"],"comparison_long":control["LONG_AIIN"],"rate_difference":target["SHORT_AIN"]/sum(target.values())-control["SHORT_AIN"]/sum(control.values()),"one_sided_p":fisher_greater(target["SHORT_AIN"],target["LONG_AIIN"],control["SHORT_AIN"],control["LONG_AIIN"]),"eligible_observed":"NA","eligible_expected":"NA","eligible_excess":"NA","eligible_strata":"NA","notes":"Pooled exploratory target/control contrast"})
 target_folios=sorted({r["physical_folio"]for r in family if r["register"]in{"HB","SB"}})
 control_rate=control["SHORT_AIN"]/sum(control.values());lofo=[]
 for f in target_folios:
  z=[r for r in family if r["register"]in{"HB","SB"}and r["physical_folio"]!=f];c=Counter(r["variant"]for r in z);lofo.append(c["SHORT_AIN"]/sum(c.values())-control_rate)
 tests += [interaction(parsed,(r,))for r in REGS]+[interaction(parsed,("HB","SB"))]
 fields=list(tests[0]);formatted=[]
 for r in tests:formatted.append({k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in r.items()})
 write(TESTS,formatted,fields)
 write(STACK,formatted[3:],fields)
 wrappers=defaultdict(Counter);hands=defaultdict(Counter)
 for r in family:
  wrappers[r["register"]][(r["outer_wrapper"],r["variant"])]+=1;hands[r["register"]][(r["hand"],r["variant"])]+=1
 pooled=tests[2];directions=tests[0]["rate_difference"]>0 and tests[1]["rate_difference"]>0
 decision="ODAIN_IS_BS_ENRICHED_SHORT_VARIANT_OF_OD_AIN_FAMILY"
 assert directions and min(lofo)>0 and len({r["physical_folio"]for r in family if r["register"]in{"HB","SB"}and r["variant"]=="SHORT_AIN"})>=3
 report=f"""# GDT043 — OD + AIN/AIIN variant attribution

## Outcome

**{decision}**

The apparent `ODAIN` residual host is not isolated. In the exact `OD +
{{AIN, AIIN}}` family, Herbal-B has {counts['HB','SHORT_AIN']} short versus
{counts['HB','LONG_AIIN']} long forms and S/B has {counts['SB','SHORT_AIN']}
versus {counts['SB','LONG_AIIN']}. Herbal-A has {counts['HA','SHORT_AIN']}
versus {counts['HA','LONG_AIIN']}, while other Currier-B has
{counts['OB','SHORT_AIN']} versus {counts['OB','LONG_AIIN']}.

The pooled target short fraction exceeds the pooled control by
{pooled['rate_difference']:+.3f} (one-sided exact Fisher p=
{pooled['one_sided_p']:.4g}). The direction is separately positive for
Herbal-B versus Herbal-A ({tests[0]['rate_difference']:+.3f}) and S/B versus
other Currier-B ({tests[1]['rate_difference']:+.3f}), and remains positive
after deleting every target physical folio (minimum difference
{min(lofo):+.3f}). Short `ODAIN` occurs on
{len({r['physical_folio']for r in family if r['register']in {'HB','SB'}and r['variant']=='SHORT_AIN'})}
target physical folios.

This does **not** show that O and D freely or semantically compose. With exact
base-host, outer-wrapper, and physical-folio margins fixed, pooled HB+S has
{tests[-1]['eligible_observed']} OD cells versus
{tests[-1]['eligible_expected']:.3f} expected (excess
{tests[-1]['eligible_excess']:+.3f}, p={tests[-1]['one_sided_p']:.3g}). Thus
the strong result is a **short-versus-long AIN-family selection inside an
already observed OD construction**, not a general independent O×D algebra.

## Interpretation

GDT038's section-conditioned ODAIN contexts now have a simpler formal account:
HB/S preferentially select the short `AIN` member where Herbal-A and other-B
more often select `AIIN`. This is a reusable register/rendering contrast and a
counterexample to treating exact `ODAIN` as an indivisible content stem. It
does not establish whether the extra `I` is linguistic, scribal, numeric, or
notational.

All occurrences, wrappers, hands, and loci are exported. f84r was not opened,
retained, queried, joined, or scored. No meaning, word, morpheme, POS, sound,
language, plaintext, or translation is assigned.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT043_OD_AIN_VARIANT_RESULT_V1","status":decision,"inventory_groups":len(parsed),"od_ain_family_occurrences":len(family),"counts":{rg:{"short_ain":counts[rg,"SHORT_AIN"],"long_aiin":counts[rg,"LONG_AIIN"]}for rg in REGS},"primary_test":pooled,"directional_tests":tests[:2],"target_short_folios":len({r["physical_folio"]for r in family if r["register"]in{"HB","SB"}and r["variant"]=="SHORT_AIN"}),"lofo_min_rate_difference":min(lofo),"wrapper_breakdown":{rg:{f"{w}|{v}":n for(w,v),n in sorted(wrappers[rg].items())}for rg in REGS},"hand_breakdown":{rg:{f"{h}|{v}":n for(h,v),n in sorted(hands[rg].items())}for rg in REGS},"od_compatibility":{r["comparison"]:r for r in tests[3:]},"claim_ceiling":"OD+AIN/AIIN short-long formal selection only; no word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt037_result.json":sha(ROOT/"gdt037_result.json"),"gdt038_result.json":sha(ROOT/"gdt038_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),TESTS.name:sha(TESTS),STACK.name:sha(STACK)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":decision,"family":len(family),"short_target":target["SHORT_AIN"],"short_control":control["SHORT_AIN"],"p":pooled["one_sided_p"],"od_p":tests[-1]["one_sided_p"]},sort_keys=True))
if __name__=="__main__":main()

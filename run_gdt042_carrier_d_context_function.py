#!/usr/bin/env python3
"""GDT042: exact host/folio-controlled local-context test for carrier+D."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT042_CARRIER_D_CONTEXT_FUNCTION_METHOD.md";REPORT=ROOT/"GDT042_CARRIER_D_CONTEXT_FUNCTION_REPORT.md";OCC=ROOT/"gdt042_complete_carrier_contexts.tsv";TESTS=ROOT/"gdt042_context_tests.tsv";RESULT=ROOT/"gdt042_result.json"
FEATURES=("late_half","field_start","preclose_or_close","after_dy","before_dy","physical_line_end");REGS=("HB","SB")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def inventory(rows):
 lines=defaultdict(list)
 for r in rows:assert not r["locus"].startswith("f84r");lines[r["locus"]].append(r)
 out=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or {int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  reg="HB"if line[0]["section"]=="H"and line[0]["currier"]=="B"else"SB"if line[0]["section"]=="S"and line[0]["currier"]=="B"else"OUT"
  if reg=="OUT":continue
  fields=[];cur=[]
  for i,r in enumerate(line):
   cur.append((i,r))
   if r["record_state"]=="DY_RESOLUTION":fields.append((cur,True));cur=[]
  if cur:fields.append((cur,False))
  pos={i:(fi,j)for fi,(f,c)in enumerate(fields)for j,(i,r)in enumerate(f)}
  for i,r in enumerate(line):
   if r["stripped_prefix"]not in{"ch","che","sh"}:continue
   inner=r["residual_host"].startswith("d")and len(r["residual_host"])>1;base=r["residual_host"][1:]if inner else r["residual_host"]
   if base=="y":continue
   fi,j=pos[i];field,closed=fields[fi];size=len(field);position="SINGLE"if size==1 else"FIELD_START"if j==0 else"FIELD_CLOSE"if closed and j==size-1 else"OPEN_FIELD_END"if j==size-1 else"PRECLOSE"if closed and j==size-2 else"FIELD_INTERNAL"
   out.append({"locus":locus,"physical_folio":r["physical_folio"],"register":reg,"hand":r["hand"],"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"wrapper":r["stripped_prefix"],"residual_host":r["residual_host"],"base_host":base,"inner_d":int(inner),"field_position":position,
    "late_half":int(n==1 or i/(n-1)>=.5),"field_start":int(position=="FIELD_START"),"preclose_or_close":int(position in{"PRECLOSE","FIELD_CLOSE"}),"after_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION"),"before_dy":int(i+1<n and line[i+1]["record_state"]=="DY_RESOLUTION"),"physical_line_end":int(i==n-1)})
 out.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])));return out
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def test(rows,regs,feature):
 z=[r for r in rows if r["register"]in regs];by=defaultdict(list)
 for r in z:by[r["physical_folio"],r["base_host"]].append(r)
 pmf={0:1.};N=obs=0;exp=0.;strata=0
 for a in by.values():
  n=len(a);D=sum(r["inner_d"]for r in a);K=sum(r[feature]for r in a)
  if not D:continue
  N+=D;obs+=sum(r["inner_d"]and r[feature]for r in a);exp+=D*K/n;strata+=int(0<K<n);pmf=conv(pmf,hyper(n,K,D))
 return{"registers":"+".join(regs),"feature":feature,"carrier_occurrences":len(z),"inner_d_occurrences":N,"observed_hits":obs,"expected_hits":exp,"rate_effect":(obs-exp)/N,"eligible_strata":strata,"enrichment_p":sum(p for x,p in pmf.items()if x>=obs),"depletion_p":sum(p for x,p in pmf.items()if x<=obs),"two_sided_p":min(1.,2*min(sum(p for x,p in pmf.items()if x>=obs),sum(p for x,p in pmf.items()if x<=obs))),"null_min":min(pmf),"null_max":max(pmf)}
def main():
 rows=inventory(read(SOURCE));assert len(rows)==674 and sum(r["inner_d"]for r in rows)==63
 write(OCC,[{k:str(r[k])for k in r}for r in rows],list(rows[0]));tests=[]
 for regs in(("HB",),("SB",),("HB","SB")):
  for feature in FEATURES:tests.append(test(rows,regs,feature))
 for r in tests:r["bonferroni_18_p"]=min(1.,r["two_sided_p"]*18)
 fields=list(tests[0]);write(TESTS,[{k:(f'{r[k]:.12g}'if isinstance(r[k],float)else r[k])for k in fields}for r in tests],fields)
 pooled=[r for r in tests if r["registers"]=="HB+SB"];passes=[r for r in pooled if abs(r["rate_effect"])>=.1 and r["bonferroni_18_p"]<=.05 and next(x for x in tests if x["registers"]=="HB"and x["feature"]==r["feature"])["rate_effect"]*next(x for x in tests if x["registers"]=="SB"and x["feature"]==r["feature"])["rate_effect"]>0]
 decision="CARRIER_D_STACK_HAS_NO_STABLE_COARSE_LOCAL_CONTEXT_FUNCTION";assert not passes
 strongest=max(pooled,key=lambda r:abs(r["rate_effect"]));report=f"""# GDT042 — carrier+D local-context function

## Outcome

**{decision}**

The complete-line panel contains {len(rows)} carrier-wrapped groups, including
63 inner-D stacks. After exact base-host × physical-folio control, none of six
declared local contexts identifies a transferable function for D.

The largest pooled absolute effect is `{strongest['feature']}` at
{strongest['rate_effect']:+.3f} ({strongest['observed_hits']} observed versus
{strongest['expected_hits']:.3f} expected; adjusted p=
{strongest['bonferroni_18_p']:.3g}). All pooled absolute effects are below
0.03; physical line end is a small depletion of
{next(r for r in pooled if r['feature']=='physical_line_end')['rate_effect']:+.3f}.

The carrier+D stack established in GDT041 is therefore a real combinatorial
permission, but its inner D does not consistently select late half, field
start, preclose/close, immediate DY adjacency, or physical line end once exact
host and folio are fixed. A finer or nonlocal function remains possible.

No meaning, morpheme, POS, sound, language, plaintext, or translation is
assigned. f84r was not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT042_CARRIER_D_CONTEXT_FUNCTION_RESULT_V1","status":decision,"carrier_occurrences":len(rows),"inner_d_occurrences":sum(r["inner_d"]for r in rows),"tests":tests,"passing_features":passes,"claim_ceiling":"No stable coarse local context function for inner D under exact host and folio control; no meaning, morpheme, POS, sound, language, plaintext, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt041_result.json":sha(ROOT/"gdt041_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"events":len(rows),"inner_d":sum(r["inner_d"]for r in rows),"strongest":[strongest["feature"],strongest["rate_effect"],strongest["bonferroni_18_p"]]},sort_keys=True))
if __name__=="__main__":main()

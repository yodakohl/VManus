#!/usr/bin/env python3
"""GDT049: exact base/folio/wrapper-controlled AIR local-context test."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt016_group_state_inventory.tsv"
METHOD=ROOT/"GDT049_AIR_LOCAL_CONTEXT_METHOD.md"
REPORT=ROOT/"GDT049_AIR_LOCAL_CONTEXT_REPORT.md"
OCC=ROOT/"gdt049_air_family_contexts.tsv"
TESTS=ROOT/"gdt049_air_context_tests.tsv"
RESULT=ROOT/"gdt049_result.json"
SUFFIXES=("aiin","air","ain","ar","al")
FEATURES=("late_half","field_start","preclose_or_close","after_dy","before_dy","physical_line_end")

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def split_host(host):
 for s in SUFFIXES:
  if host.endswith(s) and len(host)>len(s):return host[:-len(s)],s
 return None
def inventory(source):
 lines=defaultdict(list)
 for r in source:
  if r["locus"].startswith("f84r"):continue
  lines[r["locus"]].append(r)
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
  pos={i:(fi,j)for fi,(field,closed)in enumerate(fields)for j,(i,r)in enumerate(field)}
  for i,r in enumerate(line):
   if r["dy_closure"]!="0"or r["residual_host"].endswith("m")or r["stripped_prefix"]not in{"NONE","q"}:continue
   parsed=split_host(r["residual_host"])
   if not parsed:continue
   base,suffix=parsed;fi,j=pos[i];field,closed=fields[fi];size=len(field)
   position="SINGLE"if size==1 else"FIELD_START"if j==0 else"FIELD_CLOSE"if closed and j==size-1 else"OPEN_FIELD_END"if j==size-1 else"PRECLOSE"if closed and j==size-2 else"FIELD_INTERNAL"
   out.append({"locus":locus,"physical_folio":r["physical_folio"],"register":reg,"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"wrapper":r["stripped_prefix"],"residual_host":r["residual_host"],"base":base,"suffix":suffix,"is_air":int(suffix=="air"),"field_position":position,
    "late_half":int(n==1 or i/(n-1)>=.5),"field_start":int(position=="FIELD_START"),"preclose_or_close":int(position in{"PRECLOSE","FIELD_CLOSE"}),"after_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION"),"before_dy":int(i+1<n and line[i+1]["record_state"]=="DY_RESOLUTION"),"physical_line_end":int(i==n-1)})
 out.sort(key=lambda r:(r["register"],r["physical_folio"],r["locus"],int(r["group_index"])));return out
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def test(rows,regs,feature):
 z=[r for r in rows if r["register"]in regs];by=defaultdict(list)
 for r in z:by[r["physical_folio"],r["base"],r["wrapper"]].append(r)
 pmf={0:1.};N=obs=0;exp=0.;strata=0
 for a in by.values():
  n=len(a);A=sum(r["is_air"]for r in a);K=sum(r[feature]for r in a)
  if not A:continue
  N+=A;obs+=sum(r["is_air"]and r[feature]for r in a);exp+=A*K/n;strata+=int(0<K<n);pmf=conv(pmf,hyper(n,K,A))
 upper=sum(p for x,p in pmf.items()if x>=obs);lower=sum(p for x,p in pmf.items()if x<=obs)
 return{"registers":"+".join(regs),"feature":feature,"family_groups":len(z),"air_occurrences":N,"observed_hits":obs,"expected_hits":exp,"rate_effect":(obs-exp)/N,"eligible_strata":strata,"two_sided_p":min(1.,2*min(upper,lower)),"null_min":min(pmf),"null_max":max(pmf)}
def main():
 rows=inventory(read(SOURCE));assert len(rows)==614 and sum(r["is_air"]for r in rows)==22
 write(OCC,[{k:str(v)for k,v in r.items()}for r in rows],list(rows[0]))
 tests=[]
 for regs in (("HB",),("SB",),("HB","SB")):
  for feature in FEATURES:tests.append(test(rows,regs,feature))
 for r in tests:r["bonferroni_18_p"]=min(1.,18*r["two_sided_p"])
 fields=list(tests[0]);write(TESTS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in r.items()}for r in tests],fields)
 pooled=[r for r in tests if r["registers"]=="HB+SB"]
 passing=[]
 for r in pooled:
  hb=next(x for x in tests if x["registers"]=="HB"and x["feature"]==r["feature"]);sb=next(x for x in tests if x["registers"]=="SB"and x["feature"]==r["feature"])
  if abs(r["rate_effect"])>=.1 and r["bonferroni_18_p"]<=.05 and hb["rate_effect"]*sb["rate_effect"]>0:passing.append(r)
 strongest=max(pooled,key=lambda r:abs(r["rate_effect"]));decision="AIR_HAS_REGISTER_SELECTION_BUT_NO_STABLE_COARSE_LOCAL_FUNCTION";assert not passing
 report=f"""# GDT049 — AIR local-context function

## Outcome

**{decision}**

Only 22 AIR instances occur on the 614 complete-line members of the matched
right-family panel (3 Herbal B, 19 Stars/Recipe B). After exact left-base,
physical-folio, and outer-wrapper control, none of the six declared positions
identifies a stable AIR function.

The largest pooled effect is `{strongest['feature']}` at
{strongest['rate_effect']:+.3f} ({strongest['observed_hits']} hits versus
{strongest['expected_hits']:.3f} expected; 18-test adjusted p
{strongest['bonferroni_18_p']:.3g}). AIR never occupies physical line end in
this complete panel, but the matched expectation is only
{next(r for r in pooled if r['feature']=='physical_line_end')['expected_hits']:.3f}
and the exact adjusted p is 1. This is a weak descriptive exclusion, not a
record function.

GDT048's reusable AIR register selection survives, but it should not be called
an opener, closer, field boundary, or DY-adjacency marker. No morpheme,
function, word, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r was skipped before line assembly and not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT049_AIR_LOCAL_CONTEXT_RESULT_V1","status":decision,"family_groups":len(rows),"air_occurrences":sum(r["is_air"]for r in rows),"tests":tests,"passing_features":passing,"claim_ceiling":"AIR register selection without a stable tested coarse local function; no morpheme, function, word, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt048_result.json":sha(ROOT/"gdt048_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"groups":len(rows),"air":sum(r["is_air"]for r in rows),"strongest":[strongest["feature"],strongest["rate_effect"],strongest["bonferroni_18_p"]]},sort_keys=True))
if __name__=="__main__":main()

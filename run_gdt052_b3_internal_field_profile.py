#!/usr/bin/env python3
"""GDT052: exact conditional test of B3 close versus internal DY profile."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";FRAMES=ROOT/"gdt046_line_frames.tsv";METHOD=ROOT/"GDT052_B3_INTERNAL_FIELD_PROFILE_METHOD.md";REPORT=ROOT/"GDT052_B3_INTERNAL_FIELD_PROFILE_REPORT.md";LINES=ROOT/"gdt052_b3_line_profiles.tsv";TESTS=ROOT/"gdt052_b3_profile_tests.tsv";RESULT=ROOT/"gdt052_result.json"
FEATURES=("internal_dy_count","any_internal_dy","two_plus_internal_dy","three_plus_internal_dy")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def subset_sum_pmf(values,k):
 dp={(0,0):1}
 for v in values:
  nxt=dict(dp)
  for (used,total),ways in dp.items():
   if used<k:nxt[used+1,total+v]=nxt.get((used+1,total+v),0)+ways
  dp=nxt
 den=math.comb(len(values),k);return{total:ways/den for (used,total),ways in dp.items()if used==k}
def conv(a,b):
 out=defaultdict(float)
 for x,p in a.items():
  for y,q in b.items():out[x+y]+=p*q
 return dict(out)
def exact_test(rows,feature):
 by=defaultdict(list)
 for r in rows:by[r["physical_folio"],r["register"],r["length_bucket"],r["paragraph_start"]].append(r)
 pmf={0:1.};obs=0;exp=0.;closers=0;informative=0
 for z in by.values():
  k=sum(r["b3_close"]for r in z);vals=[r[feature]for r in z]
  if not k:continue
  obs+=sum(r[feature]for r in z if r["b3_close"]);closers+=k;exp+=k*sum(vals)/len(vals);informative+=int(len(set(vals))>1 and k<len(z));pmf=conv(pmf,subset_sum_pmf(vals,k))
 po=pmf[obs];p=sum(v for v in pmf.values()if v<=po+1e-15)
 return{"feature":feature,"b3_closers":closers,"observed_sum":obs,"expected_sum":exp,"effect_per_b3_line":(obs-exp)/closers,"informative_strata":informative,"exact_two_sided_p":p,"null_min":min(pmf),"null_max":max(pmf)}
def main():
 inv=defaultdict(list)
 for r in read(SOURCE):
  if r["locus"].startswith("f84r"):continue
  inv[r["locus"]].append(r)
 rows=[]
 for f in read(FRAMES):
  assert not f["locus"].startswith("f84r");line=sorted(inv[f["locus"]],key=lambda r:int(r["group_index"]));assert len(line)==int(f["group_count"])
  count=sum(r["record_state"]=="DY_RESOLUTION"for r in line[:-1]);rows.append({"locus":f["locus"],"physical_folio":f["physical_folio"],"register":f["register"],"length_bucket":f["length_bucket"],"paragraph_start":int(f["paragraph_start"]),"group_count":int(f["group_count"]),"b3_close":int(f["b3_close"]),"opening_member":f["opening_member"],"closing_member":f["closing_member"],"internal_dy_count":count,"any_internal_dy":int(count>=1),"two_plus_internal_dy":int(count>=2),"three_plus_internal_dy":int(count>=3)})
 assert len(rows)==1164 and sum(r["b3_close"]for r in rows)==145;rows.sort(key=lambda r:(r["register"],r["physical_folio"],r["locus"]));write(LINES,rows,list(rows[0]))
 tests=[exact_test(rows,f)for f in FEATURES]
 for t in tests:t["bonferroni_4_p"]=min(1.,4*t["exact_two_sided_p"])
 write(TESTS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in t.items()}for t in tests],list(tests[0]))
 primary=tests[0];decision="B3_CLOSE_DOES_NOT_PREDICT_INTERNAL_DY_FIELD_COUNT";assert primary["effect_per_b3_line"]<0 and primary["bonferroni_4_p"]>.05 and all(t["bonferroni_4_p"]>.05 for t in tests)
 report=f"""# GDT052 — B3 close and internal DY profile

## Outcome

**{decision}**

The frozen HPR-2 P02 prediction fails. The 145 B3-ended records contain
{primary['observed_sum']} internal DY checkpoints, versus
{primary['expected_sum']:.3f} under exact physical-folio × register × length ×
paragraph-start matching. The effect is {primary['effect_per_b3_line']:+.3f}
DY per B3 line, not an enrichment (exact p {primary['exact_two_sided_p']:.3g},
four-test adjusted p {primary['bonferroni_4_p']:.3g}). Any-DY, two-plus-DY,
and three-plus-DY tests are also nonconfirming.

The raw B3 mean is larger only because B3 prevalence and DY density both vary
by register. Once those margins are fixed, B3 does not preferentially close a
more segmented record. This narrows HPR-2: B3 is a transferable probabilistic
physical-line closer, but its use is independent of the tested internal field
count. DY and B3 can remain different hierarchical boundary classes without a
positive count relation.

No function beyond those formal boundary distributions, and no word,
morpheme, POS, sound, language, plaintext, meaning, or translation is
established. f84r was excluded before assembly and not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT052_B3_INTERNAL_FIELD_PROFILE_RESULT_V1","status":decision,"lines":len(rows),"b3_closers":sum(r["b3_close"]for r in rows),"tests":tests,"hpr2_prediction":"HPR2_P02","prediction_outcome":"FALSIFIED","claim_ceiling":"B3 endpoint status remains; no association with tested internal DY field count and no word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),FRAMES.name:sha(FRAMES),"gdt045_result.json":sha(ROOT/"gdt045_result.json"),"gdt051_result.json":sha(ROOT/"gdt051_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{LINES.name:sha(LINES),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"lines":len(rows),"b3":sum(r["b3_close"]for r in rows),"primary":primary},sort_keys=True))
if __name__=="__main__":main()

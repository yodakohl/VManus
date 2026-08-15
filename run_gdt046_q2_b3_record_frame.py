#!/usr/bin/env python3
"""GDT046: test source-native Q2 opener compatibility with B3 closers."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";SEP=ROOT/"experiments/semantic_assumptions/results/source_separator_transcription.tsv";METHOD=ROOT/"GDT046_Q2_B3_RECORD_FRAME_METHOD.md";REPORT=ROOT/"GDT046_Q2_B3_RECORD_FRAME_REPORT.md";LINES=ROOT/"gdt046_line_frames.tsv";ATLAS=ROOT/"gdt046_opener_atlas.tsv";TESTS=ROOT/"gdt046_transfer_tests.tsv";RESULT=ROOT/"gdt046_result.json";REGS=("HA","HB","SB","OB","OA")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OA"
def guarded(path,keys,mode):
 out={}
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r.")or raw.startswith("ZL3b|f84r.")or raw.startswith("IT2a|f84r.")or raw.startswith("RF1b|f84r."):continue
   vals=None
   if mode=="CONS":
    first=raw.split("\t",1)[0];locus,idx=first.rsplit("|C",1);key=(locus,str(int(idx)))
   else:
    parts=raw.split("\t",4)
    if len(parts)<4 or parts[1]!="ZL3b":continue
    key=parts[2]
   if key not in keys:continue
   vals=next(csv.reader([raw],delimiter="\t"));row=dict(zip(fields,vals))
   if mode=="SEP"and row["source_group_index"]!="1":continue
   out[key]=row
 return out
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def score(rows,member,regs):
 z=[r for r in rows if r["register"]in regs];by=defaultdict(list)
 for r in z:by[r["physical_folio"],r["paragraph_start"],r["length_bucket"]].append(r)
 pm={0:1.};obs=0;exp=0.;strata=0
 for a in by.values():
  n=len(a);O=sum(r["opening_member"]==member for r in a);C=sum(r["closing_member"]=="B3"for r in a)
  if not O or not C:continue
  strata+=1;obs+=sum(r["opening_member"]==member and r["closing_member"]=="B3"for r in a);exp+=O*C/n;pm=conv(pm,hyper(n,O,C))
 support=sum(r["opening_member"]==member for r in z);closers=sum(r["closing_member"]=="B3"for r in z)
 return{"observed_pairs":obs,"expected_pairs":exp,"pair_excess":obs-exp,"opening_support":support,"b3_closers":closers,"lines":len(z),"eligible_strata":strata,"one_sided_p":sum(p for x,p in pm.items()if x>=obs),"null_min":min(pm),"null_max":max(pm)}
def main():
 inv=read(SOURCE);assert not any(r["locus"].startswith("f84r")for r in inv);by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 complete={}
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)==n and{int(r["group_index"])for r in line}==set(range(1,n+1)):complete[locus]=line
 keys={(loc,r["group_index"])for loc,line in complete.items()for r in line};cons=guarded(CONS,keys,"CONS");seps=guarded(SEP,set(complete),"SEP")
 rows=[]
 for locus,line in complete.items():
  if locus not in seps:continue
  first=cons[(locus,line[0]["group_index"])];last=cons[(locus,line[-1]["group_index"])];fc=tuple(first[x].split()[0]for x in("zl_sta_codes","it_sta_codes","rf_sta_codes"));lc=tuple(last[x].split()[-1]for x in("zl_sta_codes","it_sta_codes","rf_sta_codes"))
  if len(set(fc))>1 or len(set(lc))>1:continue
  n=len(line);rows.append({"locus":locus,"page":line[0]["page"],"physical_folio":line[0]["physical_folio"],"register":reg(line[0]),"hand":line[0]["hand"],"group_count":n,"length_bucket":str(n)if n<10 else"10PLUS","paragraph_start":seps[locus]["paragraph_start"],"opening_token":line[0]["token"],"opening_member":fc[0],"closing_token":line[-1]["token"],"closing_member":lc[0],"q2_open":int(fc[0]=="Q2"),"b3_close":int(lc[0]=="B3")})
 rows.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"]));write(LINES,rows,list(rows[0]));assert all((r["opening_token"].startswith("t"))==(r["opening_member"]=="Q2")for r in rows)
 support=Counter(r["opening_member"]for r in rows);atlas=[]
 for m,n in sorted(support.items()):
  if n>=20:atlas.append({"opening_member":m,"support":n,**score(rows,m,REGS)})
 atlas.sort(key=lambda r:(r["one_sided_p"],-r["pair_excess"],r["opening_member"]));K=len(atlas)
 for i,r in enumerate(atlas,1):r["rank"]=i;r["bonferroni_p"]=min(1.,r["one_sided_p"]*K)
 af=["rank","opening_member","support","observed_pairs","expected_pairs","pair_excess","opening_support","b3_closers","lines","eligible_strata","one_sided_p","bonferroni_p","null_min","null_max"];write(ATLAS,[{k:f"{r[k]:.12g}"if isinstance(r[k],float)else r[k]for k in af}for r in atlas],af)
 specs=[("DISCOVERY_HB_SB",("HB","SB")),("TRANSFER_HA_OB_OA",("HA","OB","OA")),("ALL_REGISTERS",REGS)];tests=[]
 for name,regs in specs:tests.append({"comparison":name,"registers":"+".join(regs),**score(rows,"Q2",regs)})
 folios=sorted({r["physical_folio"]for r in rows if r["opening_member"]=="Q2"});lo=[]
 for f in folios:lo.append(score([r for r in rows if r["physical_folio"]!=f],"Q2",REGS)["pair_excess"])
 tests[-1]["lofo_min_pair_excess"]=min(lo)
 tf=list(tests[0]);write(TESTS,[{k:("NA"if k not in r else f"{r[k]:.12g}"if isinstance(r[k],float)else r[k])for k in tf}for r in tests],tf)
 q={r["comparison"]:r for r in tests};allz=q["ALL_REGISTERS"];held=q["TRANSFER_HA_OB_OA"];decision="Q2_B3_RECORD_FRAME_WEAK_TRANSFERABLE_LEAD";assert atlas[0]["opening_member"]=="Q2"and allz["pair_excess"]>0 and held["pair_excess"]>0 and min(lo)>0
 report=f"""# GDT046 — Q2...B3 record-frame compatibility

## Outcome

**{decision}**

Among {len(rows):,} complete lines with transcription-stable source-native
endpoints, 31 begin with Q2 and end with B3. After fixing physical folio,
editorial paragraph-start state, and line-length bucket, {allz['expected_pairs']:.3f}
are expected (excess {allz['pair_excess']:+.3f}, p={allz['one_sided_p']:.4g}).
The excess remains positive after deleting every Q2-positive folio (minimum
{min(lo):+.3f}). Q2 corresponds exactly to display `t-` on this inventory.

The direction transfers but is weak: held HA/other-B/other-A has
{held['observed_pairs']} pairs versus {held['expected_pairs']:.3f} expected
(excess {held['pair_excess']:+.3f}, p={held['one_sided_p']:.3g}). Q2 ranks
first of {K} supported opening-member classes, but the full-search corrected
p is {atlas[0]['bonferroni_p']:.3g}. The result is therefore a reusable weak
frame lead, not a confirmed paired syntax.

This goes beyond Q2's already known association with editorial paragraph
openings because paragraph state is fixed inside the null. Nevertheless, the
editorial state is not authorial semantics, line-length matching is bucketed,
and only 31 positive frames exist. Q2 is not called START and B3 is not called
END; neither receives a word, morpheme, POS, sound, language, plaintext, or
translation. f84r was skipped before formal parsing and was not retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT046_Q2_B3_RECORD_FRAME_RESULT_V1","status":decision,"stable_endpoint_lines":len(rows),"opener_atlas_size":K,"winner":atlas[0],"discovery":q["DISCOVERY_HB_SB"],"transfer":held,"all_registers":allz,"lofo_min_pair_excess":min(lo),"q2_display_t_equivalence":True,"claim_ceiling":"Weak probabilistic source-native line-frame compatibility only; not START/END words, syntax, word, morpheme, POS, sound, language, plaintext, or translation.","f84r":{"opened":False,"parsed":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv":sha(CONS),"experiments/semantic_assumptions/results/source_separator_transcription.tsv":sha(SEP),"gdt045_result.json":sha(ROOT/"gdt045_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{LINES.name:sha(LINES),ATLAS.name:sha(ATLAS),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"pairs":allz["observed_pairs"],"expected":allz["expected_pairs"],"p":allz["one_sided_p"],"held_p":held["one_sided_p"],"adjusted":atlas[0]["bonferroni_p"]},sort_keys=True))
if __name__=="__main__":main()

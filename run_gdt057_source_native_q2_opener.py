#!/usr/bin/env python3
"""GDT057: exact source-native Q2 physical-line opener test."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt016_group_state_inventory.tsv"
CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
METHOD=ROOT/"GDT057_SOURCE_NATIVE_Q2_OPENER_METHOD.md"
REPORT=ROOT/"GDT057_SOURCE_NATIVE_Q2_OPENER_REPORT.md"
OCC=ROOT/"gdt057_q2_occurrences.tsv"
ATLAS=ROOT/"gdt057_first_member_atlas.tsv"
TRANSFER=ROOT/"gdt057_register_transfer.tsv"
RESULT=ROOT/"gdt057_result.json"
REGS=("HA","HB","SB","OB","OA")

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def reg(r):
 if r["section"]=="H" and r["currier"]=="A":return "HA"
 if r["section"]=="H" and r["currier"]=="B":return "HB"
 if r["section"]=="S" and r["currier"]=="B":return "SB"
 if r["currier"]=="B":return "OB"
 return "OA"
def hyper(n,K,k):
 den=math.comb(n,k)
 return {x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 out=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():out[i+j]+=p*q
 return dict(out)
def basic(lines,member,regs):
 pm={0:1.};obs=N=0;exp=0.;nlines=0
 for line in lines:
  if line[0]["register"] not in regs:continue
  nlines+=1;draw=sum(r["first_member"]==member for r in line)
  if not draw:continue
  actual=sum(r["first_member"]==member and r["physical_line_start"] for r in line)
  obs+=actual;N+=draw;exp+=draw/len(line);pm=conv(pm,hyper(len(line),1,draw))
 return {"observed":obs,"member_n":N,"observed_rate":obs/N if N else 0.,"expected_hits":exp,
  "expected_rate":exp/N if N else 0.,"rate_effect":(obs-exp)/N if N else 0.,
  "local_p":sum(p for x,p in pm.items() if x>=obs),"null_min":min(pm),"null_max":max(pm),
  "line_count":nlines,"opener_recall":obs/nlines if nlines else 0.}
def score(lines,member,regs):
 z=basic(lines,member,regs)
 folios=sorted({r["physical_folio"] for line in lines for r in line if line[0]["register"] in regs and r["first_member"]==member})
 effects=[]
 for folio in folios:
  reduced=[line for line in lines if line[0]["physical_folio"]!=folio]
  effects.append(basic(reduced,member,regs)["rate_effect"])
 z["physical_folios"]=len(folios);z["lofo_min_effect"]=min(effects) if effects else 0.
 return z
def guarded_consensus(keys):
 out={}
 with CONS.open(encoding="utf-8",newline="") as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r."):continue
   first=raw.split("\t",1)[0];locus,idx=first.rsplit("|C",1);key=(locus,str(int(idx)))
   if key not in keys:continue
   out[key]=dict(zip(fields,next(csv.reader([raw],delimiter="\t"))))
 return out
def main():
 inv=read(SOURCE);assert not any(r["locus"].startswith("f84r") for r in inv)
 by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 complete=[];keys=set()
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or {int(r["group_index"]) for r in line}!=set(range(1,n+1)):continue
  complete.append(line);keys|={(locus,r["group_index"]) for r in line}
 cons=guarded_consensus(keys);assert len(cons)==sum(map(len,complete))
 lines=[];unstable_lines=0;unstable_groups=0
 for line in complete:
  built=[];stable=True
  for i,r in enumerate(line):
   c=cons[(r["locus"],r["group_index"])]
   starts=tuple(c[k].split()[0] for k in ("zl_sta_codes","it_sta_codes","rf_sta_codes"))
   same=len(set(starts))==1;unstable_groups+=not same;stable&=same
   built.append({**r,"register":reg(r),"physical_line_start":int(i==0),"first_member":starts[0],
    "zl_first_member":starts[0],"it_first_member":starts[1],"rf_first_member":starts[2]})
  if stable:lines.append(built)
  else:unstable_lines+=1
 assert len(lines)==1036 and sum(map(len,lines))==7492
 q2=[r for line in lines for r in line if r["first_member"]=="Q2"]
 occ=[{k:str(r[k]) for k in ("locus","page","physical_folio","register","hand","group_index","group_count","token","first_member","physical_line_start")} for r in q2]
 occ.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])))
 write(OCC,occ,list(occ[0]))
 specs=[(x,(x,)) for x in REGS]+[("CURRIER_B",("HB","SB","OB")),("CURRIER_A",("HA","OA")),("ALL_REGISTERS",REGS)]
 trans=[]
 for name,regs in specs:trans.append({"comparison":name,"registers":"+".join(regs),**score(lines,"Q2",regs)})
 tf=list(trans[0]);tn=set(tf)-{"comparison","registers"}
 write(TRANSFER,[{k:f"{v:.12g}" if k in tn and isinstance(v,float) else v for k,v in r.items()} for r in trans],tf)
 counts=Counter(r["first_member"] for line in lines for r in line);atlas=[]
 for member,n in sorted(counts.items()):
  if n<20:continue
  z=basic(lines,member,REGS);atlas.append({"first_member":member,"support":n,**z})
 atlas.sort(key=lambda r:(-r["rate_effect"],r["local_p"],r["first_member"]));K=len(atlas)
 for i,r in enumerate(atlas,1):r["rank_by_effect"]=i;r["bonferroni_p"]=min(1.,r["local_p"]*K)
 af=["rank_by_effect","first_member","support","observed","member_n","observed_rate","expected_hits","expected_rate","rate_effect","local_p","bonferroni_p","null_min","null_max","line_count","opener_recall"]
 write(ATLAS,[{k:f"{r[k]:.12g}" if isinstance(r[k],float) else r[k] for k in af} for r in atlas],af)
 tr={r["comparison"]:r for r in trans};allz=tr["ALL_REGISTERS"];qrow=next(r for r in atlas if r["first_member"]=="Q2")
 assert qrow["rank_by_effect"]==2 and qrow["bonferroni_p"]<1e-12 and all(tr[x]["rate_effect"]>0 for x in REGS) and allz["lofo_min_effect"]>0
 decision="Q2_IS_STRONG_TRANSFERABLE_PROBABILISTIC_LINE_OPENER_CLASS"
 report=f"""# GDT057 — source-native Q2 probabilistic line opener

## Outcome

**{decision}**

The strict panel contains {len(lines):,} complete physical lines and
{sum(map(len,lines)):,} groups. Every retained group has the same first
source-native STA member in ZL3b, IT2a, and RF1b; the editions are alternate
readings of one manuscript.

Q2 occurs in {allz['member_n']} groups and begins the physical line in
{allz['observed']} cases (precision {allz['observed_rate']:.3f}, line-opener
recall {allz['opener_recall']:.3f}). Exact within-line permutation expects
{allz['expected_hits']:.3f}, an effect of {allz['rate_effect']:+.3f} per Q2
occurrence (p={allz['local_p']:.3g}). Among {K} supported stable first-member
classes, Q2 ranks second by opening effect, behind P1; its Bonferroni-corrected
p is {qrow['bonferroni_p']:.3g}.

The effect is positive separately in Herbal A ({tr['HA']['rate_effect']:+.3f}),
Herbal B ({tr['HB']['rate_effect']:+.3f}), Stars/Recipe B
({tr['SB']['rate_effect']:+.3f}), other Currier B
({tr['OB']['rate_effect']:+.3f}), and other Currier A
({tr['OA']['rate_effect']:+.3f}). Q2 appears on {allz['physical_folios']}
physical folios and the minimum leave-one-folio-out effect is
{allz['lofo_min_effect']:+.3f}. This is therefore not a Currier-B-only effect.

## Correction to the current record compiler

GDT046 showed only that the *pairing* of Q2-open with B3-closed lines was weak
after opener-class search correction. It did not test Q2's marginal line-entry
effect. Q2 itself is a strong, transferable probabilistic line-opener class;
Q2+B3 remains a weak optional pairing, not a mandatory frame.

`Opener` names a physical-coordinate tendency. It does not assert a word
boundary, punctuation, syntax, operator meaning, sound, language, plaintext,
or translation. f84r was skipped before formal parsing and was not opened,
retained, queried, joined, or scored.
"""
 REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT057_SOURCE_NATIVE_Q2_OPENER_RESULT_V1","status":decision,
  "complete_lines":len(lines),"complete_groups":sum(map(len,lines)),"excluded_unstable_lines":unstable_lines,
  "unstable_first_member_groups_in_complete_inventory":unstable_groups,"all_registers":allz,
  "per_register":{x:tr[x] for x in REGS},"currier_b":tr["CURRIER_B"],"currier_a":tr["CURRIER_A"],
  "member_atlas_size":K,"q2_atlas_row":qrow,"atlas_winner":atlas[0],
  "relationship_to_gdt046":"Q2 marginal opening is strong; Q2+B3 paired-frame evidence remains weak and optional.",
  "claim_ceiling":"Probabilistic source-native physical-line opener class only; not word boundary, punctuation, syntax, morpheme, POS, sound, language, plaintext, meaning, or translation.",
  "f84r":{"opened":False,"parsed":False,"retained":False,"queried":False,"joined":False,"scored":False},
  "inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),
   "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv":sha(CONS),
   "gdt045_result.json":sha(ROOT/"gdt045_result.json"),"gdt046_result.json":sha(ROOT/"gdt046_result.json"),
   "gdt051_result.json":sha(ROOT/"gdt051_result.json"),"gdt056_result.json":sha(ROOT/"gdt056_result.json")},
  "implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),ATLAS.name:sha(ATLAS),TRANSFER.name:sha(TRANSFER)},
  "documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":decision,"lines":len(lines),"q2":allz,"rank":qrow["rank_by_effect"]},sort_keys=True))
if __name__=="__main__":main()

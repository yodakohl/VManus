#!/usr/bin/env python3
"""GDT045: transfer the terminal-M effect as source-native final member B3."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";METHOD=ROOT/"GDT045_TERMINAL_B3_RECORD_CLOSER_METHOD.md";REPORT=ROOT/"GDT045_TERMINAL_B3_RECORD_CLOSER_REPORT.md";OCC=ROOT/"gdt045_b3_occurrences.tsv";ATLAS=ROOT/"gdt045_final_member_atlas.tsv";TRANSFER=ROOT/"gdt045_register_transfer.tsv";RESULT=ROOT/"gdt045_result.json"
REGS=("HA","HB","SB","OB","OA")
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
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def basic(lines,member,regs):
 pm={0:1.};obs=N=0;exp=0.
 for line in lines:
  if line[0]["register"]not in regs:continue
  draw=sum(r["final_member"]==member for r in line)
  if not draw:continue
  hit=sum(r["physical_line_end"] for r in line);actual=sum(r["final_member"]==member and r["physical_line_end"]for r in line);obs+=actual;N+=draw;exp+=draw*hit/len(line);pm=conv(pm,hyper(len(line),hit,draw))
 return{"observed":obs,"member_n":N,"observed_rate":obs/N if N else 0.,"expected_hits":exp,"expected_rate":exp/N if N else 0.,"rate_effect":(obs-exp)/N if N else 0.,"local_p":sum(p for x,p in pm.items()if x>=obs),"null_min":min(pm),"null_max":max(pm)}
def score(lines,member,regs):
 z=basic(lines,member,regs);folios=sorted({r["physical_folio"]for line in lines for r in line if line[0]["register"]in regs and r["final_member"]==member});effects=[]
 for f in folios:
  reduced=[[r for r in line if r["physical_folio"]!=f]for line in lines];reduced=[x for x in reduced if x];effects.append(basic(reduced,member,regs)["rate_effect"])
 z["physical_folios"]=len(folios);z["lofo_min_effect"]=min(effects)if effects else 0.;z["line_count"]=sum(line[0]["register"]in regs for line in lines);z["endpoint_recall"]=z["observed"]/z["line_count"] if z["line_count"]else 0.;return z
def guarded_consensus(keys):
 out={}
 with CONS.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r."):continue
   first=raw.split("\t",1)[0];locus,idx=first.rsplit("|C",1);key=(locus,str(int(idx)))
   if key not in keys:continue
   vals=next(csv.reader([raw],delimiter="\t"));out[key]=dict(zip(fields,vals))
 return out
def main():
 inv=read(SOURCE);assert not any(r["locus"].startswith("f84r")for r in inv);by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 complete=[];keys=set()
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or{int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  complete.append(line);keys|={(locus,r["group_index"])for r in line}
 cons=guarded_consensus(keys);assert len(cons)==sum(map(len,complete))
 lines=[];unstable=0
 for line in complete:
  z=[]
  for i,r in enumerate(line):
   c=cons[(r["locus"],r["group_index"])];ends=tuple(c[k].split()[-1]for k in("zl_sta_codes","it_sta_codes","rf_sta_codes"));stable=len(set(ends))==1;unstable+=not stable
   z.append({**r,"register":reg(r),"physical_line_end":int(i==len(line)-1),"final_member":ends[0]if stable else"TRANSCRIPTION_UNSTABLE","zl_final_member":ends[0],"it_final_member":ends[1],"rf_final_member":ends[2]})
  lines.append(z)
 b3=[r for line in lines for r in line if r["final_member"]=="B3"];m=[r for line in lines for r in line if r["residual_host"].endswith("m")];assert {(r["locus"],r["group_index"])for r in b3}=={(r["locus"],r["group_index"])for r in m}and len(b3)==213
 occ=[{k:str(r[k])for k in("locus","page","physical_folio","register","hand","group_index","group_count","token","residual_host","final_member","physical_line_end") }for r in b3];occ.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])));write(OCC,occ,list(occ[0]))
 specs=[("DISCOVERY_HB_SB",("HB","SB")),("TRANSFER_HA_OB_OA",("HA","OB","OA"))]+[(x,(x,))for x in REGS]+[("ALL_REGISTERS",REGS)]
 trans=[]
 for name,regs in specs:trans.append({"comparison":name,"registers":"+".join(regs),**score(lines,"B3",regs)})
 fields=list(trans[0]);nums=set(fields)-{"comparison","registers"};write(TRANSFER,[{k:f"{v:.12g}"if k in nums and isinstance(v,float)else v for k,v in r.items()}for r in trans],fields)
 mc=Counter(r["final_member"]for line in lines for r in line);atlas=[]
 for member,n in sorted(mc.items()):
  if member=="TRANSCRIPTION_UNSTABLE"or n<20:continue
  z=basic(lines,member,REGS);atlas.append({"final_member":member,"support":n,**z})
 atlas.sort(key=lambda r:(r["local_p"],-r["rate_effect"],r["final_member"]));K=len(atlas)
 for i,r in enumerate(atlas,1):r["rank"]=i;r["bonferroni_p"]=min(1.,r["local_p"]*K)
 af=["rank","final_member","support","observed","member_n","observed_rate","expected_hits","expected_rate","rate_effect","local_p","bonferroni_p","null_min","null_max"];write(ATLAS,[{k:f"{r[k]:.12g}"if isinstance(r[k],float)else r[k]for k in af}for r in atlas],af)
 tr={r["comparison"]:r for r in trans};allz=tr["ALL_REGISTERS"];held=tr["TRANSFER_HA_OB_OA"];decision="TERMINAL_B3_IS_TRANSFERABLE_RECORD_CLOSING_MARKER_CLASS";assert atlas[0]["final_member"]=="B3"and held["rate_effect"]>.45 and all(tr[x]["lofo_min_effect"]>0 for x in REGS)
 report=f"""# GDT045 — source-native B3 record-closing marker

## Outcome

**{decision}**

On {len(lines):,} complete physical lines ({sum(map(len,lines)):,} groups),
source-native final member `B3` occurs {allz['member_n']} times and closes the
line {allz['observed']} times: precision {allz['observed_rate']:.3f}, endpoint
recall {allz['endpoint_recall']:.3f}. Exact within-line expectation is
{allz['expected_hits']:.3f}, giving effect {allz['rate_effect']:+.3f} and
p={allz['local_p']:.3g}. Every one of these 213 groups is exactly the residual
display-M class in all three readings; none carries an outer DY closure on the
complete-line inventory.

The transfer set excludes the HB/S discovery registers. Across Herbal-A,
other Currier-B, and other Currier-A, B3 remains line-final
{held['observed']}/{held['member_n']} times versus {held['expected_hits']:.3f}
expected (effect {held['rate_effect']:+.3f}, p={held['local_p']:.3g}, minimum
leave-folio effect {held['lofo_min_effect']:+.3f}). Direction is positive with
positive leave-folio minima separately in HA, HB, S/B, other-B, and other-A.

The supported final-member max-search contains {K} classes. B3 ranks first;
its corrected p is {atlas[0]['bonferroni_p']:.3g}. It is not merely the best
common final glyph by chance: its +{allz['rate_effect']:.3f} effect is far
larger than the remaining supported members.

## Functional reading and limits

The strongest defensible function recovered here is **record-closing marker
class**. It is probabilistic, not mandatory: B3 has high endpoint precision
but only {allz['endpoint_recall']:.3f} recall, so most lines close without it
and 65 B3 groups are internal. `Marker` does not assert punctuation, syntax,
speech, or a specific administrative/medical function. The stronger effect in
Currier B is compatible with its denser record architecture, while transfer to
Currier A shows the convention is manuscript-wide rather than B-only.

No word, morpheme, POS, sound, language, plaintext, concrete meaning, or
translation is assigned. f84r was skipped before source-native formal parsing
and was not retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT045_TERMINAL_B3_RECORD_CLOSER_RESULT_V1","status":decision,"complete_lines":len(lines),"complete_groups":sum(map(len,lines)),"unstable_final_member_groups":unstable,"b3_display_m_equivalence":True,"all_registers":allz,"transfer":held,"per_register":{x:tr[x]for x in REGS},"member_atlas_size":K,"member_atlas_winner":atlas[0],"claim_ceiling":"Probabilistic source-native record-closing marker class only; not punctuation, word, morpheme, POS, sound, language, plaintext, concrete meaning, or translation.","f84r":{"opened":False,"parsed":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv":sha(CONS),"gdt039_result.json":sha(ROOT/"gdt039_result.json"),"gdt044_result.json":sha(ROOT/"gdt044_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),ATLAS.name:sha(ATLAS),TRANSFER.name:sha(TRANSFER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"B3":len(b3),"precision":allz["observed_rate"],"recall":allz["endpoint_recall"],"held_p":held["local_p"],"winner":atlas[0]["final_member"]},sort_keys=True))
if __name__=="__main__":main()

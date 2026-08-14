#!/usr/bin/env python3
"""Test Q/L previous-DY direction outside the DY-ending state."""
from __future__ import annotations
import csv,json,math
from collections import defaultdict
from pathlib import Path
from run_gdt022_full_census_visual_phase import csha,sha,statistic,write
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def branch(r):
 f=r["family_surface"]
 if"QJB"in f or"QKB"in f:return"Q"
 if"LJB"in f or"LKB"in f:return"L"
 return"OTHER"
def fisher(a,b,c,d):
 n=a+b+c+d;r=a+b;k=a+c;lo=max(0,r-(n-k));hi=min(r,k)
 def lp(x):return math.lgamma(k+1)-math.lgamma(x+1)-math.lgamma(k-x+1)+math.lgamma(n-k+1)-math.lgamma(r-x+1)-math.lgamma(n-k-r+x+1)-math.lgamma(n+1)+math.lgamma(r+1)+math.lgamma(n-r+1)
 z=lp(a);xs=[lp(x)for x in range(lo,hi+1)if lp(x)<=z+1e-12];m=max(xs);return min(1.,math.exp(m)*sum(math.exp(x-m)for x in xs))
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 lookup={};base_ctx={};previous={};allkeys=set();qkeys=set()
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(line):
   b=branch(r)
   if r["currier"]!="B"or b=="OTHER":continue
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;k=(locus,int(r["group_index"]));allkeys.add(k);lookup[k]=r;previous[k]=line[i-1]if i else None
   if b=="Q":qkeys.add(k)
   base_ctx[k]={"physical_folio":r["physical_folio"],"state":r["record_state"],"position_bin":min(3,int(z*4)),"PREVIOUS_DY":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")}
 partitions=[("ALL",lambda r:True),("DY",lambda r:r["record_state"]=="DY_RESOLUTION"),("NON_DY",lambda r:r["record_state"]!="DY_RESOLUTION")]
 for state in sorted({lookup[k]["record_state"]for k in allkeys}):partitions.append((state,lambda r,s=state:r["record_state"]==s))
 rows=[]
 for name,pred in partitions:
  keys={k for k in allkeys if pred(lookup[k])};pos=qkeys&keys
  if not keys:continue
  qp=sum(base_ctx[k]["PREVIOUS_DY"]for k in pos);qn=len(pos)-qp;l=keys-pos;lp=sum(base_ctx[k]["PREVIOUS_DY"]for k in l);ln=len(l)-lp;rawp=fisher(qp,qn,lp,ln)if qp+qn and lp+ln else 1.;odds=qp*ln/(qn*lp)if qn and lp else float("inf")if qp and ln else 0.
  rec={"partition":name,"groups":len(keys),"q_groups":len(pos),"l_groups":len(l),"q_postdy":qp,"q_not_postdy":qn,"l_postdy":lp,"l_not_postdy":ln,"raw_odds_ratio":f"{odds:.12g}","raw_fisher_p":f"{rawp:.12g}"}
  for level in("PAGE","FOLIO","SECTION"):
   ctx={k:{**base_ctx[k],"page":lookup[k]["page"]if level=="PAGE"else lookup[k]["physical_folio"]if level=="FOLIO"else lookup[k]["section"]}for k in keys};s=statistic(keys,pos,ctx,"PREVIOUS_DY");rec.update({f"{level.lower()}_effect":f"{s['effect']:.12f}",f"{level.lower()}_exact_p":f"{s['p']:.12g}",f"{level.lower()}_informative_strata":s["informative_strata"]})
  rec["claim_state"]="RIGHT_EDGE_PORTABILITY_CAPACITY_NOT_MEANING";rows.append(rec)
 write("gdt027_right_edge_portability_tests.tsv",rows)
 examples=[]
 for k in sorted(allkeys):
  r=lookup[k]
  if r["record_state"]=="DY_RESOLUTION"or not base_ctx[k]["PREVIOUS_DY"]:continue
  examples.append({"locus":k[0],"page":r["page"],"physical_folio":r["physical_folio"],"group_index":k[1],"branch":branch(r),"current_state":r["record_state"],"previous_dy_token":previous[k]["token"],"current_token":r["token"],"current_family":r["family_surface"],"claim_state":"NON_DY_POST_CHECKPOINT_EXAMPLE_NOT_MEANING"})
 write("gdt027_non_dy_postcheckpoint_examples.tsv",examples)
 by={r["partition"]:r for r in rows};n=by["NON_DY"];status="Q_L_HISTORY_BIT_RIGHT_EDGE_PORTABILITY_PROVISIONAL_LOW_CAPACITY"
 report=f"""# GDT027 Q/L right-edge portability report

Status: **{status.replace('_',' ')}**

The Q/L backward direction extends suggestively beyond DY endings. Among 212
non-DY groups, Q-family is post-checkpoint in 50/144 cases and L-family in
13/68, raw odds {float(n['raw_odds_ratio']):.3f} and Fisher
p={float(n['raw_fisher_p']):.4f}. Section+state+position matching retains effect
{float(n['section_effect']):+.4f} (p={float(n['section_exact_p']):.4f}).

However, the primary page-matched test has only
{n['page_informative_strata']} informative strata and
p={float(n['page_exact_p']):.3f}; folio matching has
{n['folio_informative_strata']} strata and p={float(n['folio_exact_p']):.3f}.
The evidence is concentrated in ED_MEDIUM (27 Q versus 8 L post-checkpoint
examples) and AR_REFERENCE (15 versus 2). AL_STATE and OL_STATE are too small
and do not establish the direction.

Concrete adjacent checkpoint transitions include `qokedy -> qokedal`, `okeedy -> lkeedar`,
`qokedy -> qokedain`, `qotedy -> otedar`, and `okedy -> tedyol`. These support
a candidate factorization:

```
history realization (Q/L family) + host + right-edge state (DY/DAL/DAR/DAIN/...)
```

The factorization remains provisional because page-level exchangeability is
sparse. It is useful theory, not a confirmed independent slot.

Only the frozen GDT016 inventory is used and it contains no f84r row. f84r was
not opened, retained, joined, or scored. No role, referent, morpheme, word,
sound, language, plaintext, meaning, or translation is assigned.
""";(ROOT/"GDT027_Q_L_RIGHT_EDGE_PORTABILITY_REPORT.md").write_text(report)
 outputs=("gdt027_right_edge_portability_tests.tsv","gdt027_non_dy_postcheckpoint_examples.tsv","GDT027_Q_L_RIGHT_EDGE_PORTABILITY_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt026_result.json","GDT027_Q_L_RIGHT_EDGE_PORTABILITY_METHOD.md")
 result={"schema":"GDT027_Q_L_RIGHT_EDGE_PORTABILITY_RESULT_V1","status":status,"inventory_groups":len(inv),"ql_groups":len(allkeys),"partitions":len(rows),"non_dy":n,"examples":len(examples),"candidate_factorization":"Q/L history realization plus host plus independently varying right-edge state","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Provisional low-capacity portability of a formal history contrast across right-edge states only; no role, referent, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{x:sha(ROOT/x)for x in inputs},"implementation":{"run_gdt027_q_l_right_edge_portability.py":sha(Path(__file__)),"run_gdt022_full_census_visual_phase.py":sha(ROOT/"run_gdt022_full_census_visual_phase.py")},"outputs":{x:sha(ROOT/x)for x in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt027_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"non_dy":n,"examples":len(examples)},sort_keys=True))
if __name__=="__main__":main()

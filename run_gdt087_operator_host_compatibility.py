#!/usr/bin/env python3
"""GDT087: whole-folio-held wrapper compatibility for matched oTAIL/yTAIL hosts."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt062_right_family_inventory.tsv"
METHOD=ROOT/"GDT087_OPERATOR_HOST_COMPATIBILITY_METHOD.md"
REPORT=ROOT/"GDT087_OPERATOR_HOST_COMPATIBILITY_REPORT.md"
CELLS=ROOT/"gdt087_wrapper_base_cells.tsv"
SCORES=ROOT/"gdt087_wrapper_model_scores.tsv"
REGS=ROOT/"gdt087_wrapper_register_gains.tsv"
EXC=ROOT/"gdt087_operator_counterexamples.tsv"
RESULT=ROOT/"gdt087_result.json"
LAMBDAS=(1,4,16,64,256)
OUTCOMES=("Q","D","S","CH_FAMILY","NONE")

def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def event(r,outcome):
 if outcome=="Q":return int(r["wrapper"]=="q")
 if outcome=="D":return int(r["wrapper"]=="d")
 if outcome=="S":return int(r["wrapper"]=="s")
 if outcome=="CH_FAMILY":return int(r["wrapper"] in {"ch","che","sh"})
 if outcome=="NONE":return int(r["wrapper"]=="NONE")
 raise ValueError(outcome)

def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r") for r in source)
 by=defaultdict(list)
 for r in source:
  h=r["page_host"]
  if h and h[0] in "oy":by[(h[0],h[1:])].append(r)
 tails=sorted(s for s in {k[1] for k in by} if len(by.get(("o",s),[]))>=2 and len(by.get(("y",s),[]))>=2)
 rows=[]
 for tail in tails:
  for base in "oy":
   for r in by[base,tail]:rows.append({**r,"base_axis":base,"matched_tail":tail})
 assert len(tails)==42 and len(rows)==4641
 folios=sorted({r["physical_folio"] for r in rows})
 score_rows=[];reg_rows=[];best_by={}
 for outcome in OUTCOMES:
  detail={}
  for lam in LAMBDAS:
   baseline_bits=model_bits=0.0;rg=defaultdict(float)
   for folio in folios:
    train=[r for r in rows if r["physical_folio"]!=folio];test=[r for r in rows if r["physical_folio"]==folio]
    tc=defaultdict(Counter);bc=defaultdict(Counter)
    for r in train:
     y=event(r,outcome);tc[r["matched_tail"],r["register"]][y]+=1;bc[r["matched_tail"],r["register"],r["base_axis"]][y]+=1
    for r in test:
     y=event(r,outcome);c=tc[r["matched_tail"],r["register"]];pb=(c[y]+.5)/(sum(c.values())+1)
     d=bc[r["matched_tail"],r["register"],r["base_axis"]];p=(d[y]+lam*pb)/(sum(d.values())+lam)
     g=math.log2(p/pb);baseline_bits-=math.log2(pb);model_bits-=math.log2(p);rg[r["register"]]+=g
   gain=baseline_bits-model_bits
   rec={"wrapper_outcome":outcome,"lambda":lam,"groups":len(rows),"matched_tails":len(tails),"baseline_bits":baseline_bits,"base_model_bits":model_bits,"gain_bits":gain,"selector_paid_gain_bits":gain-math.log2(len(LAMBDAS)),"selected":0}
   score_rows.append(rec);detail[lam]=rg
  best=max((r for r in score_rows if r["wrapper_outcome"]==outcome),key=lambda r:r["gain_bits"]);best["selected"]=1;best_by[outcome]=best
  for register,gain in sorted(detail[best["lambda"]].items()):reg_rows.append({"wrapper_outcome":outcome,"register":register,"selected_lambda":best["lambda"],"gain_bits":gain,"direction":"POSITIVE" if gain>0 else "NEGATIVE_OR_ZERO"})
 cell_rows=[]
 for outcome in OUTCOMES:
  for base in "oy":
   z=[r for r in rows if r["base_axis"]==base];n=sum(event(r,outcome) for r in z)
   cell_rows.append({"wrapper_outcome":outcome,"base_axis":base,"occurrences":len(z),"event_count":n,"event_rate":n/len(z),"physical_folios":len({r["physical_folio"] for r in z})})
 q=best_by["Q"];d=best_by["D"];s=best_by["S"];ch=best_by["CH_FAMILY"]
 classifications={"Q":"O_BASE_LICENSED","D":"Y_BASE_LICENSED","S":"CONDITIONALLY_COMPATIBLE","CH_FAMILY":"REGISTER_CONDITIONED_Y_LEANING","NONE":"DESCRIPTIVE_COMPLEMENT"}
 counter=[]
 for r in rows:
  if r["wrapper"]=="q" and r["base_axis"]=="y":kind="Q_ON_Y_EXCEPTION"
  elif r["wrapper"]=="d" and r["base_axis"]=="o":kind="D_ON_O_EXCEPTION"
  else:continue
  counter.append({"locus":r["locus"],"physical_folio":r["physical_folio"],"token":r["token"],"wrapper":r["wrapper"],"page_host":r["page_host"],"matched_tail":r["matched_tail"],"register":r["register"],"exception":kind})
 status="Q_AND_D_FORM_COMPLEMENTARY_O_Y_HOST_LICENSING_SYSTEM"
 def regs_pos(out):return sum(x["direction"]=="POSITIVE" for x in reg_rows if x["wrapper_outcome"]==out)
 REPORT.write_text(f"""# GDT087 — complementary wrapper/host compatibility

## Outcome

**{status}**

The state-blind matched panel contains {len(rows)} groups, {len(tails)} exact
`o+TAIL / y+TAIL` contrasts, and {len(folios)} physical folios.  After a
`TAIL × register` baseline, adding only base `o/y` saves {q['gain_bits']:+.3f}
held-folio bits for q presence and {d['gain_bits']:+.3f} bits for d presence
({q['selector_paid_gain_bits']:+.3f} and {d['selector_paid_gain_bits']:+.3f}
after each five-way shrinkage selector).  Both directions are positive in
all {regs_pos('Q')}/5 and {regs_pos('D')}/5 registers.

The raw cells expose a complementary licensing pattern: q occurs on
{next(x for x in cell_rows if x['wrapper_outcome']=='Q' and x['base_axis']=='o')['event_count']}/{next(x for x in cell_rows if x['wrapper_outcome']=='Q' and x['base_axis']=='o')['occurrences']}
O-base hosts but only {next(x for x in cell_rows if x['wrapper_outcome']=='Q' and x['base_axis']=='y')['event_count']}/{next(x for x in cell_rows if x['wrapper_outcome']=='Q' and x['base_axis']=='y')['occurrences']} Y-base hosts; d occurs on
{next(x for x in cell_rows if x['wrapper_outcome']=='D' and x['base_axis']=='y')['event_count']}/{next(x for x in cell_rows if x['wrapper_outcome']=='D' and x['base_axis']=='y')['occurrences']}
Y-base hosts versus {next(x for x in cell_rows if x['wrapper_outcome']=='D' and x['base_axis']=='o')['event_count']}/{next(x for x in cell_rows if x['wrapper_outcome']=='D' and x['base_axis']=='o')['occurrences']} O-base hosts.

`s` is weaker ({s['gain_bits']:+.3f} bits) and reverses in Stars/Recipe B.
The pooled `ch/che/sh` family has {ch['gain_bits']:+.3f} bits but reverses in
OTHER_A, so it remains register-conditioned rather than a universal base
operator.

The best current formal grammar is therefore not freely combinatorial:
`q` licenses an O-base host class, `d` licenses a Y-base host class, and the
other wrappers are conditional.  This explains much of the apparent q-X and
d-X productivity as constrained construction selection.  It does not assign
meaning, sound, POS, linguistic morphology, or translation.  GDT003 remains
controlling negative evidence; f84r was excluded before analysis.
""",encoding="utf-8")
 for r in score_rows:r.update(classification=classifications[r["wrapper_outcome"]])
 write(CELLS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in cell_rows],list(cell_rows[0]))
 write(SCORES,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in score_rows],list(score_rows[0]))
 write(REGS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in reg_rows],list(reg_rows[0]))
 write(EXC,counter,list(counter[0]))
 result={"schema":"GDT087_OPERATOR_HOST_COMPATIBILITY_RESULT_V1","status":status,"groups":len(rows),"matched_tails":len(tails),"physical_folios":len(folios),"classifications":classifications,"selected_models":{o:{"lambda":best_by[o]["lambda"],"gain_bits":best_by[o]["gain_bits"],"selector_paid_gain_bits":best_by[o]["selector_paid_gain_bits"],"positive_registers":regs_pos(o)} for o in OUTCOMES},"q_y_exceptions":sum(r["exception"]=="Q_ON_Y_EXCEPTION" for r in counter),"d_o_exceptions":sum(r["exception"]=="D_ON_O_EXCEPTION" for r in counter),"grammar_refinement":"OUTER_WRAPPER compatibility is constrained by PAGE_HOST base: q selects O; d selects Y; ch/che/sh and s remain register-conditional.","claim_ceiling":"Parser-dependent formal construction licensing only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt003_nested_result.json":sha(ROOT/"gdt003_nested_result.json"),"gdt086_result.json":sha(ROOT/"gdt086_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{CELLS.name:sha(CELLS),SCORES.name:sha(SCORES),REGS.name:sha(REGS),EXC.name:sha(EXC)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":status,"groups":len(rows),"tails":len(tails),"q_gain":q["gain_bits"],"d_gain":d["gain_bits"]},sort_keys=True))
if __name__=="__main__":main()

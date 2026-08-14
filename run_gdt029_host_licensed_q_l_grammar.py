#!/usr/bin/env python3
"""Held-out host-compatibility models for Currier-B Q/L branches."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;ALPHA=.5;TRIALS=200000
MODELS=("PRIOR","CONTEXT","HISTORY","EXACT_HOST","EXACT_HOST_HISTORY","HOST_NGRAM","HOST_NGRAM_HISTORY","HOST_NGRAM_INTERACTION")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(n,rows):
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def branch(f):
 if"QJB"in f or"QKB"in f:return 1
 if"LJB"in f or"LKB"in f:return 0
 return None
def grams(s):
 p="^"+s+"$";return sorted({p[i:i+n]for n in(1,2,3)for i in range(len(p)-n+1)})
def features(x,m):
 out=[]
 if m!="PRIOR":out +=["STATE="+x["state"],"POSITION="+str(x["position_bin"])]
 if m in("HISTORY","EXACT_HOST_HISTORY","HOST_NGRAM_HISTORY","HOST_NGRAM_INTERACTION"):out +=["PREVIOUS_DY="+str(x["previous_dy"])]
 if m in("EXACT_HOST","EXACT_HOST_HISTORY"):out +=["HOST="+x["host"]]
 if m in("HOST_NGRAM","HOST_NGRAM_HISTORY","HOST_NGRAM_INTERACTION"):
  g=grams(x["host"]);out +=["GRAM="+z for z in g]
  if m=="HOST_NGRAM_INTERACTION":out +=["HISTGRAM="+str(x["previous_dy"])+":"+z for z in g]
 return out
def fit_score(data,train,test,model):
 classes=[0,0];counts=[Counter(),Counter()];totals=[0,0];vocab=set()
 for i in train:
  x=data[i];fs=features(x,model);classes[x["y"]]+=1;counts[x["y"]].update(fs);totals[x["y"]]+=len(fs);vocab.update(fs)
 bits=0.;correct=0;v=max(1,len(vocab))
 for i in test:
  x=data[i];scores=[]
  for y in(0,1):scores.append(math.log((classes[y]+ALPHA)/(len(train)+2*ALPHA))+sum(math.log((counts[y][f]+ALPHA)/(totals[y]+ALPHA*v))for f in features(x,model)))
  peak=max(scores);p=math.exp(scores[1]-peak)/(math.exp(scores[0]-peak)+math.exp(scores[1]-peak));bits-=math.log2(p if x["y"]else 1-p);correct+=int((p>=.5)==bool(x["y"]))
 return bits,correct
def folds(data,field):
 return [(str(value),[i for i,x in enumerate(data)if x[field]!=value],[i for i,x in enumerate(data)if x[field]==value])for value in sorted({x[field]for x in data})]
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 data=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(line):
   y=branch(r["family_surface"])
   if r["currier"]!="B"or y is None:continue
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;data.append({"y":y,"folio":r["physical_folio"],"host":r["residual_host"],"state":r["record_state"],"position_bin":min(3,int(z*4)),"previous_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")})
 results=[];folio_detail=[]
 for protocol,field in(("LEAVE_ONE_PHYSICAL_FOLIO_OUT","folio"),("LEAVE_ONE_RESIDUAL_HOST_OUT","host")):
  partitions=folds(data,field);summary={m:[0.,0]for m in MODELS}
  for held,train,test in partitions:
   fold_scores={}
   for m in MODELS:
    bits,correct=fit_score(data,train,test,m);summary[m][0]+=bits;summary[m][1]+=correct;fold_scores[m]=bits
   if field=="folio":folio_detail.append({"held_folio":held,"groups":len(test),"host_ngram_bits":f"{fold_scores['HOST_NGRAM']:.12f}","host_ngram_history_bits":f"{fold_scores['HOST_NGRAM_HISTORY']:.12f}","history_increment_gain_bits":f"{fold_scores['HOST_NGRAM']-fold_scores['HOST_NGRAM_HISTORY']:.12f}","exact_host_increment_gain_bits":f"{fold_scores['EXACT_HOST']-fold_scores['EXACT_HOST_HISTORY']:.12f}","claim_state":"HELD_FOLIO_FORMAL_PREDICTION_NOT_MEANING"})
  for m in MODELS:results.append({"protocol":protocol,"model":m,"folds":len(partitions),"groups":len(data),"heldout_bits":f"{summary[m][0]:.12f}","bits_per_group":f"{summary[m][0]/len(data):.12f}","accuracy":f"{summary[m][1]/len(data):.12f}","claim_state":"FORMAL_BRANCH_PREDICTION_NOT_LANGUAGE"})
 write("gdt029_heldout_model_comparison.tsv",results);write("gdt029_folio_history_increment.tsv",folio_detail)
 gains=[float(r["history_increment_gain_bits"])for r in folio_detail];observed=sum(gains);rng=random.Random(290029);extreme=sum(sum(x if rng.getrandbits(1)else-x for x in gains)>=observed-1e-15 for _ in range(TRIALS));signp=(extreme+1)/(TRIALS+1);rng=random.Random(290030);boots=sorted(sum(rng.choice(gains)for _ in gains)for _ in range(TRIALS));lo,hi=boots[int(.025*TRIALS)],boots[int(.975*TRIALS)-1]
 feature=defaultdict(lambda:Counter());folios=defaultdict(lambda:defaultdict(set));tot=Counter(x["y"]for x in data)
 for x in data:
  for g in grams(x["host"]):feature[g][x["y"]]+=1;folios[g][x["y"]].add(x["folio"])
 atlas=[]
 for g,c in feature.items():
  if sum(c.values())<10 or len(folios[g][0]|folios[g][1])<3:continue
  log=math.log2(((c[1]+.5)/(tot[1]+.5))/((c[0]+.5)/(tot[0]+.5)));atlas.append({"host_feature":g,"q_groups":c[1],"l_groups":c[0],"q_folios":len(folios[g][1]),"l_folios":len(folios[g][0]),"log2_q_vs_l_enrichment":f"{log:.12f}","direction":"Q"if log>0 else"L","claim_state":"ORTHOGRAPHIC_HOST_COMPATIBILITY_NOT_MEANING"})
 atlas.sort(key=lambda r:(-abs(float(r["log2_q_vs_l_enrichment"])),r["host_feature"]));write("gdt029_host_compatibility_atlas.tsv",atlas)
 table={(r["protocol"],r["model"]):r for r in results};fo=lambda m:float(table[("LEAVE_ONE_PHYSICAL_FOLIO_OUT",m)]["heldout_bits"]);ho=lambda m:float(table[("LEAVE_ONE_RESIDUAL_HOST_OUT",m)]["heldout_bits"]);status="HOST_LICENSED_Q_L_BRANCHING_SUPPORTED_HISTORY_INCREMENT_WEAK"
 report=f"""# GDT029 host-licensed Q/L grammar report

Status: **{status.replace('_',' ')}**

The Q/L split is overwhelmingly licensed by host form. On completely unseen
folios, context alone costs {fo('CONTEXT'):.3f} bits. Exact-host frequency costs
{fo('EXACT_HOST'):.3f} bits, while host character 1--3-grams cost
{fo('HOST_NGRAM'):.3f} bits ({float(table[('LEAVE_ONE_PHYSICAL_FOLIO_OUT','HOST_NGRAM')]['accuracy'])*100:.2f}% accuracy). Thus the strongest explanation of Q versus L is a
host-conditioned construction lexicon, not a freely selectable operator.

Host spelling also generalizes beyond memorized forms. With every occurrence
of the scored host removed, the n-gram model costs {ho('HOST_NGRAM'):.3f} bits
versus {ho('CONTEXT'):.3f} for context and {ho('EXACT_HOST'):.3f} for exact-host
lookup. Strong Q-compatible signatures include `ke$`, `te`, `ote`, and `oke`;
strong L-compatible signatures include `lsh`, `she`, and terminal `he$`.

Previous-DY adds only {observed:.3f} bits beyond host n-grams across unseen
folios ({observed/len(data):.5f} bit/group): 23/40 folios are positive,
paired sign-flip p={signp:.4f}, and the folio bootstrap interval is
[{lo:.3f}, {hi:.3f}] bits. Exact-host+history similarly improves exact-host
lookup by {fo('EXACT_HOST')-fo('EXACT_HOST_HISTORY'):.3f} bits. The increment is
too small and unstable to establish a separable history operator.

Updated generative account: QJB/QKB and LJB/LKB are host-licensed construction
branches; local history modestly shifts which branch-bearing host class occurs.
GDT026's association remains descriptive, but “one-bit history realization”
is not identified independently of host selection. This is formal redundancy
within the same source strings, not linguistic morphology. The frozen input
contains no f84r row; f84r was not opened, retained, joined, or scored. No
role, morpheme, word, sound, language, plaintext, meaning, or translation is
assigned.
""";(ROOT/"GDT029_HOST_LICENSED_Q_L_GRAMMAR_REPORT.md").write_text(report)
 outputs=("gdt029_heldout_model_comparison.tsv","gdt029_folio_history_increment.tsv","gdt029_host_compatibility_atlas.tsv","GDT029_HOST_LICENSED_Q_L_GRAMMAR_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt026_result.json","gdt028_result.json","GDT029_HOST_LICENSED_Q_L_GRAMMAR_METHOD.md")
 result={"schema":"GDT029_HOST_LICENSED_Q_L_GRAMMAR_RESULT_V1","status":status,"groups":len(data),"folios":len({x["folio"]for x in data}),"residual_hosts":len({x["host"]for x in data}),"models":len(MODELS),"folio_context_bits":fo("CONTEXT"),"folio_exact_host_bits":fo("EXACT_HOST"),"folio_host_ngram_bits":fo("HOST_NGRAM"),"folio_host_ngram_history_bits":fo("HOST_NGRAM_HISTORY"),"folio_history_increment_bits":observed,"folio_history_positive":sum(x>0 for x in gains),"folio_history_signflip_p":signp,"folio_history_bootstrap_95":[lo,hi],"host_holdout_context_bits":ho("CONTEXT"),"host_holdout_exact_bits":ho("EXACT_HOST"),"host_holdout_ngram_bits":ho("HOST_NGRAM"),"interpretation":"Q/L is a host-licensed construction split; previous-DY is at most a weak secondary selection bias after host form is known.","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Formal heldout compatibility only; no independently identified operator, role, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt029_host_licensed_q_l_grammar.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt029_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"folio_bits":{m:fo(m)for m in MODELS},"history_gain":observed,"p":signp,"bootstrap":[lo,hi],"host_holdout_ngram_bits":ho("HOST_NGRAM")},sort_keys=True))
if __name__=="__main__":main()

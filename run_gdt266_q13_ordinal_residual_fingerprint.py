#!/usr/bin/env python3
"""GDT266: held-page ordinal-residual q13 mate retrieval."""
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt227_q13_abstract_interlinear.tsv";ACCESS="gdt257_result.json";METHOD="GDT266_Q13_ORDINAL_RESIDUAL_FINGERPRINT_METHOD.md"
MODES=["STRUCTURE_ONLY","WRAPPER","RIGHT","COMPILER","RAW_EXACT","PAGE_HOST_EXACT","RAW_CHAR3","PAGE_HOST_CHAR3"]
SEEDS=["GDT264-S0","GDT264-S1","GDT264-S2","GDT264-S3"];NW=4096
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,r):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(r)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tri(s):
 z="^"+s+"$";return [z[i:i+3] for i in range(max(0,len(z)-2))]
def feat(rr,m):
 o=Counter()
 for x in rr:
  ts=x["source_tokens"].split("|");hs=x["page_hosts"].split("|");cs=x["compiler_cells"].split("|")
  if m=="STRUCTURE_ONLY":
   n=int(x["field_group_count"]);o["SIZE:"+(str(n) if n<=4 else "5+")]+=1;o["END:"+x["line_field_end"]]+=1;o["CLASS:"+x["abstract_role_like"]]+=1
  elif m=="WRAPPER":
   for c in cs:o["W:"+c.split(":")[0]]+=1
  elif m=="RIGHT":
   for c in cs:o["R:"+c.split(":")[3]]+=1
  elif m=="COMPILER":
   for c in cs:
    for k,v in zip("WFDRYB",c.split(":")):o[k+":"+v]+=1
    o["C:"+c]+=1
  elif m=="RAW_EXACT":
   for t in ts:o["T:"+t]+=1
  elif m=="PAGE_HOST_EXACT":
   for h in hs:o["H:"+h]+=1
  elif m=="RAW_CHAR3":
   for t in ts:
    for q in tri(t):o["R3:"+q]+=1
  elif m=="PAGE_HOST_CHAR3":
   for h in hs:
    for q in tri(h):o["H3:"+q]+=1
  else:raise AssertionError(m)
 return o
def norm(v):
 n=math.sqrt(sum(x*x for x in v.values())) or 1.0;return Counter({k:x/n for k,x in v.items()})
def centroid(vs):
 o=Counter()
 for v in vs:
  for k,x in v.items():o[k]+=x/len(vs)
 return o
def residual(v,c):return Counter({k:v.get(k,0)-c.get(k,0) for k in set(v)|set(c)})
def cos(a,b):
 dot=sum(x*b.get(k,0) for k,x in a.items());aa=sum(x*x for x in a.values());bb=sum(x*x for x in b.values());return dot/math.sqrt(aa*bb) if aa and bb else 0.0
def main():
 src=read(SRC);assert src and all(not x["page"].startswith("f84") for x in src)
 a=json.loads((R/ACCESS).read_text());assert a["access"]["pristine_access_seal"] is False
 rec=defaultdict(list);loc=defaultdict(set)
 for x in src:rec[(x["page"],x["record_id"])].append(x);loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2};assert len(pages)==9
 full={};half={}
 for p,rs in pages.items():
  for rid in rs:
   for m in MODES:full[(m,p,rid)]=feat(rec[(p,rid)],m)
   for si,seed in enumerate(SEEDS):
    ls=sorted(loc[(p,rid)],key=lambda z:hashlib.sha256((seed+"|"+z).encode()).hexdigest());cut=len(ls)//2
    for vn,keep in [("A",set(ls[:cut])),("B",set(ls[cut:]))]:
     rr=[x for x in rec[(p,rid)] if x["locus"] in keep]
     for m in MODES:half[(m,p,rid,si,vn)]=feat(rr,m)
 preds=[];blocks={m:defaultdict(int) for m in MODES}
 for m in MODES:
  for hp,hrs in sorted(pages.items()):
   train=[p for p in pages if p!=hp];docs=[full[(m,p,r)] for p in train for r in pages[p]];df=Counter();n=len(docs)
   for d in docs:
    for k in d:df[k]+=1
   idf={k:math.log((1+n)/(1+v))+1 for k,v in df.items()}
   tvec={(p,r):norm(Counter({k:x*idf.get(k,0) for k,x in full[(m,p,r)].items()})) for p in train for r in pages[p]}
   cen={lab:centroid([tvec[(p,pages[p][0 if lab=="EARLIER" else 1])] for p in train]) for lab in ["EARLIER","LATER"]}
   hvec={}
   for rid in hrs:
    lab="EARLIER" if rid==hrs[0] else "LATER"
    for si in range(4):
     for vn in ["A","B"]:
      v=norm(Counter({k:x*idf.get(k,0) for k,x in half[(m,hp,rid,si,vn)].items()}));hvec[(rid,si,vn)]=residual(v,cen[lab])
   for si in range(4):
    for sv,dv in [("A","B"),("B","A")]:
     for rid in hrs:
      sc={cand:cos(hvec[(rid,si,sv)],hvec[(cand,si,dv)]) for cand in hrs};ranked=sorted(hrs,key=lambda x:(-sc[x],x));other=[x for x in hrs if x!=rid][0];good=int(ranked[0]==rid);blocks[m][(hp,si)]+=good
      preds.append({"representation":m,"held_page":hp,"record_id":rid,"record_ordinal_class":"EARLIER" if rid==hrs[0] else "LATER","split_index":si,"split_seed":SEEDS[si],"direction":sv+"_TO_"+dv,"train_pages":";".join(train),"true_residual_cosine":f"{sc[rid]:.12f}","competitor_residual_cosine":f"{sc[other]:.12f}","rank":1 if good else 2,"top1":good})
 obs={m:sum(blocks[m].values()) for m in MODES};rng=random.Random(26620260817);vals={m:[] for m in MODES};worlds=[]
 for w in range(NW):
  flips={(p,si):rng.randrange(2) for p in pages for si in range(4)};z={m:sum((4-blocks[m][k]) if flips[k] else blocks[m][k] for k in blocks[m]) for m in MODES}
  for m in MODES:vals[m].append(z[m])
  if w<128:worlds.append({"world":w,**z,"max_correct":max(z.values())})
 maxv=[max(vals[m][i] for m in MODES) for i in range(NW)];scores=[]
 for m in MODES:
  o=obs[m];pp=sum(sum(int(x["top1"]) for x in preds if x["representation"]==m and x["held_page"]==p)>8 for p in pages)
  scores.append({"representation":m,"predictions":144,"correct":o,"accuracy":f"{o/144:.12f}","positive_held_pages":pp,"eligible_pages":9,"chance_accuracy":"0.500000000000","local_inclusive_p":f"{(1+sum(v>=o for v in vals[m]))/(NW+1):.12f}","max_eight_inclusive_p":f"{(1+sum(v>=o for v in maxv))/(NW+1):.12f}","null_mean_correct":f"{sum(vals[m])/NW:.12f}"})
 write("gdt266_residual_predictions.tsv",preds);write("gdt266_residual_scores.tsv",scores);write("gdt266_residual_null.tsv",worlds)
 best=max(scores,key=lambda x:int(x["correct"]));host=next(x for x in scores if x["representation"]=="PAGE_HOST_CHAR3");he=next(x for x in scores if x["representation"]=="PAGE_HOST_EXACT");wrap=next(x for x in scores if x["representation"]=="WRAPPER")
 status="ORDINAL_RESIDUAL_MATE_TEST_UNIDENTIFIABLE_NO_SAME_ORDINAL_CONTROL"
 counter=[{"counterexample":"FATAL_ORDINAL_EXCHANGEABILITY","value":"true mate always same ordinal; decoy always opposite ordinal","consequence":"centroid subtraction leaves class-specific residual geometry and the candidate-swap null cannot identify content"},{"counterexample":"NO_SAME_ORDINAL_WITHIN_PAGE_DECOY","value":"0 eligible decoys in all nine binary pages","consequence":"primary residual score is invalid as a payload test"},{"counterexample":"DIAGNOSTIC_SCORE_ONLY","value":f"raw exact {best['correct']}/144; host char3 {host['correct']}/144","consequence":"large numbers are retained to expose the failure mode, not as evidence"},{"counterexample":"EXPLORATORY_SUCCESSOR","value":"designed after exposed GDT264-265","consequence":"no semantic or content claim may be rescued post hoc"}]
 write("gdt266_counterexamples.tsv",counter)
 report=["# GDT266 — q13 ordinal-residual record fingerprint","",f"Status: **{status}**.","","## Result","","Every held-page vector was centered by the corresponding earlier/later centroid learned only from the other eight pages before mate retrieval.","","| representation | correct / 144 | accuracy | positive pages | local p | max-eight p |","|---|---:|---:|---:|---:|---:|"]
 for x in sorted(scores,key=lambda z:-int(z["correct"])):report.append(f"| {x['representation']} | {x['correct']} | {float(x['accuracy']):.3f} | {x['positive_held_pages']}/9 | {float(x['local_inclusive_p']):.4f} | {float(x['max_eight_inclusive_p']):.4f} |")
 report += ["",f"The diagnostic best is **{best['representation']}** at {best['correct']}/144. PAGE_HOST character texture scores {host['correct']}/144 and exact PAGE_HOST identity {he['correct']}/144. These values are **not valid payload evidence**.","","## Fatal identifiability failure","","Every true mate shares the query's earlier/later ordinal, while every competing record has the opposite ordinal. Mean subtraction does not erase class-specific covariance or the shared negative coordinates induced by sparse centering. The candidate-swap null is applied after that geometry exists, so it cannot distinguish page-record content from residual ordinal structure. There are zero same-page same-ordinal decoys in the frozen panel.","","GDT266 therefore stops as unidentifiable. It neither confirms nor rejects a PAGE_HOST payload channel. The next valid use of these data is a direct wrapper/ordinal analysis, not another mate-retrieval residual.","","No topic, object, procedure, word, language, plaintext, or translation is assigned. No f84r material was opened, retained, queried, or scored; the prior process-level breach remains disclosed.",""]
 (R/"GDT266_Q13_ORDINAL_RESIDUAL_FINGERPRINT_REPORT.md").write_text("\n".join(report))
 result={"experiment":"GDT266_Q13_ORDINAL_RESIDUAL_FINGERPRINT","status":status,"valid_primary_score":False,"identifiability_failure":"TRUE_MATE_SAME_ORDINAL_DECOY_OPPOSITE_ORDINAL_ZERO_SAME_ORDINAL_DECOYS","pages":9,"records":18,"predictions_per_representation":144,"diagnostic_best_representation":best["representation"],"diagnostic_best_correct":int(best["correct"]),"diagnostic_page_host_char3_correct":int(host["correct"]),"diagnostic_page_host_exact_correct":int(he["correct"]),"semantic_assignments":0,"interpretation":"The residual candidate geometry is not ordinal-exchangeable; no payload inference is licensed.","claim_ceiling":"Identifiability stop for this binary mate panel only; no record topic host meaning or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),ACCESS:sha(ACCESS)},"documents":{METHOD:sha(METHOD)},"outputs":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 result["outputs"]={p:sha(p) for p in ["gdt266_residual_predictions.tsv","gdt266_residual_scores.tsv","gdt266_residual_null.tsv","gdt266_counterexamples.tsv","GDT266_Q13_ORDINAL_RESIDUAL_FINGERPRINT_REPORT.md"]};result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt266_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"best":best["representation"],"best_correct":best["correct"],"host":host["correct"],"host_p":host["max_eight_inclusive_p"]},sort_keys=True))
if __name__=="__main__":main()

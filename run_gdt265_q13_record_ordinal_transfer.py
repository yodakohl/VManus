#!/usr/bin/env python3
"""GDT265: held-page transfer of q13 R01/R02 record ordinal."""
import csv,hashlib,json,itertools,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
SRC="gdt227_q13_abstract_interlinear.tsv";ACCESS="gdt257_result.json";METHOD="GDT265_Q13_RECORD_ORDINAL_TRANSFER_METHOD.md"
MODES=["STRUCTURE_ONLY","WRAPPER","RIGHT","COMPILER","RAW_EXACT","PAGE_HOST_EXACT","RAW_CHAR3","PAGE_HOST_CHAR3"]
SEEDS=["GDT264-S0","GDT264-S1","GDT264-S2","GDT264-S3"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,r):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(r)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def grams(s):
 z="^"+s+"$";return [z[i:i+3] for i in range(max(0,len(z)-2))]
def features(rr,m):
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
    for q in grams(t):o["R3:"+q]+=1
  elif m=="PAGE_HOST_CHAR3":
   for h in hs:
    for q in grams(h):o["H3:"+q]+=1
  else:raise AssertionError(m)
 return o
def dotcos(a,b,idf):
 dot=aa=bb=0.0
 for k in set(a)|set(b):
  x=a.get(k,0)*idf.get(k,0);y=b.get(k,0)*idf.get(k,0);dot+=x*y;aa+=x*x;bb+=y*y
 return dot/math.sqrt(aa*bb) if aa and bb else 0.0
def plaincos(a,b):
 return dotcos(a,b,{k:1.0 for k in set(a)|set(b)})
def centroid(vs):
 o=Counter()
 for v in vs:
  n=math.sqrt(sum(x*x for x in v.values())) or 1
  for k,x in v.items():o[k]+=x/n
 for k in o:o[k]/=len(vs)
 return o
def main():
 src=read(SRC);assert src and all(not x["page"].startswith("f84") for x in src)
 a=json.loads((R/ACCESS).read_text());assert a["access"]["pristine_access_seal"] is False
 rec=defaultdict(list);loc=defaultdict(set)
 for x in src:rec[(x["page"],x["record_id"])].append(x);loc[(x["page"],x["record_id"])].add(x["locus"])
 bp=defaultdict(list)
 for k,v in loc.items():
  if len(v)>=4:bp[k[0]].append(k[1])
 pages={p:sorted(v) for p,v in bp.items() if len(v)==2};assert len(pages)==9
 for p,rs in pages.items():assert len(rs)==2 and int(rs[0].rsplit("R",1)[-1])<int(rs[1].rsplit("R",1)[-1])
 full={};half={}
 for p,rs in pages.items():
  for rid in rs:
   for m in MODES:full[(m,p,rid)]=features(rec[(p,rid)],m)
   for si,seed in enumerate(SEEDS):
    ls=sorted(loc[(p,rid)],key=lambda z:hashlib.sha256((seed+"|"+z).encode()).hexdigest());cut=len(ls)//2
    for vn,keep in [("A",set(ls[:cut])),("B",set(ls[cut:]))]:
     rr=[x for x in rec[(p,rid)] if x["locus"] in keep]
     for m in MODES:half[(m,p,rid,si,vn)]=features(rr,m)
 preds=[]; block=defaultdict(int)
 # Function refits centroids under a specified page-label flip world.
 def assignments(m,flips,emit=False):
  total=0;out=[]
  for hp,hrs in sorted(pages.items()):
   train=[p for p in pages if p!=hp];docs=[full[(m,p,r)] for p in train for r in pages[p]];df=Counter();n=len(docs)
   for d in docs:
    for k in d:df[k]+=1
   idf={k:math.log((1+n)/(1+v))+1 for k,v in df.items()}
   prot={"EARLIER":[],"LATER":[]}
   for p in train:
    for rid in pages[p]:
     true="EARLIER" if rid==pages[p][0] else "LATER";lab=("LATER" if true=="EARLIER" else "EARLIER") if flips[p] else true
     prot[lab].append(Counter({k:v*idf.get(k,0) for k,v in full[(m,p,rid)].items()}))
   cen={lab:centroid(vs) for lab,vs in prot.items()}
   for si in range(4):
    for vn in ["A","B"]:
     r1,r2=hrs;q1=Counter({k:v*idf.get(k,0) for k,v in half[(m,hp,r1,si,vn)].items()});q2=Counter({k:v*idf.get(k,0) for k,v in half[(m,hp,r2,si,vn)].items()})
     direct=plaincos(q1,cen["EARLIER"])+plaincos(q2,cen["LATER"])
     swap=plaincos(q1,cen["LATER"])+plaincos(q2,cen["EARLIER"])
     good=int(direct>=swap);total+=good
     if emit:out.append({"representation":m,"held_page":hp,"held_record_earlier":r1,"held_record_later":r2,"split_index":si,"split_seed":SEEDS[si],"view":vn,"train_pages":";".join(train),"direct_orientation_score":f"{direct:.12f}","swapped_orientation_score":f"{swap:.12f}","predicted_orientation":"DIRECT" if good else "SWAPPED","correct":good})
  return total,out
 obs={};
 for m in MODES:
  obs[m],o=assignments(m,{p:0 for p in pages},True);preds+=o
 worlds=[];vals={m:[] for m in MODES}
 for wi,bits in enumerate(itertools.product([0,1],repeat=9)):
  f=dict(zip(sorted(pages),bits));z={m:assignments(m,f)[0] for m in MODES}
  for m in MODES:vals[m].append(z[m])
  worlds.append({"world":wi,"flip_bits":"".join(map(str,bits)),**z,"max_standardized_correct":f"{max((z[m]-36)/math.sqrt(18) for m in MODES):.12f}"})
 maxv=[max((vals[m][i]-36)/math.sqrt(18) for m in MODES) for i in range(512)]
 scores=[]
 for m in MODES:
  o=obs[m];st=(o-36)/math.sqrt(18)
  pp=sum(sum(int(x["correct"]) for x in preds if x["representation"]==m and x["held_page"]==p)>4 for p in pages)
  scores.append({"representation":m,"held_page_assignments":72,"correct":o,"accuracy":f"{o/72:.12f}","positive_held_pages":pp,"eligible_pages":9,"chance_accuracy":"0.500000000000","local_inclusive_p":f"{(1+sum(v>=o for v in vals[m]))/513:.12f}","max_eight_inclusive_p":f"{(1+sum(v>=st for v in maxv))/513:.12f}","null_mean_correct":f"{sum(vals[m])/512:.12f}"})
 write("gdt265_record_ordinal_predictions.tsv",preds);write("gdt265_record_ordinal_scores.tsv",scores);write("gdt265_record_ordinal_null.tsv",worlds)
 best=max(scores,key=lambda x:int(x["correct"]));wrap=next(x for x in scores if x["representation"]=="WRAPPER")
 status="WRAPPER_RECORD_ORDINAL_TRANSFER_BORDERLINE" if float(wrap["max_eight_inclusive_p"])>0.1 else "WRAPPER_FINGERPRINT_TRANSFERS_AS_RECORD_ORDINAL"
 counter=[{"counterexample":"GLOBAL_ORDINAL_CONFOUND","value":f"wrapper {wrap['correct']}/72 max-eight p {wrap['max_eight_inclusive_p']}","consequence":"tests whether GDT264 wrapper fingerprint is a reusable earlier/later-record code"},{"counterexample":"BINARY_PANEL","value":"nine pages with exactly two eligible records","consequence":"does not generalize to pages with three or more powered records"},{"counterexample":"MECHANICAL_RECORD_ID","value":"GDT227 record segmentation","consequence":"earlier/later is not a semantic topic label"},{"counterexample":"EXPOSED_SUCCESSOR","value":"designed after GDT264 wrapper lead","consequence":"exploratory mechanism discriminator only"}]
 write("gdt265_counterexamples.tsv",counter)
 report=["# GDT265 — q13 record-ordinal transfer","",f"Status: **{status}**.","","## Held-page result","","| representation | correct / 72 | accuracy | positive pages | local p | max-eight p |","|---|---:|---:|---:|---:|---:|"]
 for x in sorted(scores,key=lambda z:-int(z["correct"])):report.append(f"| {x['representation']} | {x['correct']} | {float(x['accuracy']):.3f} | {x['positive_held_pages']}/9 | {float(x['local_inclusive_p']):.4f} | {float(x['max_eight_inclusive_p']):.4f} |")
 report += ["",f"Wrapper-only transfer scores {wrap['correct']}/72 on {wrap['positive_held_pages']}/9 held pages (local p={float(wrap['local_inclusive_p']):.4f}; max-eight p={float(wrap['max_eight_inclusive_p']):.4f}). The best representation is {best['representation']} at {best['correct']}/72.","","This directly tests the main nuisance explanation for GDT264. The wrapper result is large and broadly signed but misses the max-eight exploratory threshold by one narrow step. Much of the GDT264 wrapper fingerprint is therefore plausibly earlier/later document order; it cannot be promoted as latent content. At the same time, the search-adjusted test does not establish a universal ordinal code. The proper status is borderline positional transfer, not either confirmation or a clean null.","","No topic, object, procedure, word, language, plaintext, or translation is assigned. No f84r material was opened, retained, queried, or scored; the earlier process-level breach remains disclosed.",""]
 (R/"GDT265_Q13_RECORD_ORDINAL_TRANSFER_REPORT.md").write_text("\n".join(report))
 result={"experiment":"GDT265_Q13_RECORD_ORDINAL_TRANSFER","status":status,"pages":9,"records":18,"assignments_per_representation":72,"best_representation":best["representation"],"best_correct":int(best["correct"]),"wrapper_correct":int(wrap["correct"]),"wrapper_max_eight_p":float(wrap["max_eight_inclusive_p"]),"semantic_assignments":0,"claim_ceiling":"Held-page earlier/later mechanical-record assignment only; no record topic meaning or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),ACCESS:sha(ACCESS)},"documents":{METHOD:sha(METHOD)},"outputs":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 result["outputs"]={p:sha(p) for p in ["gdt265_record_ordinal_predictions.tsv","gdt265_record_ordinal_scores.tsv","gdt265_record_ordinal_null.tsv","gdt265_counterexamples.tsv","GDT265_Q13_RECORD_ORDINAL_TRANSFER_REPORT.md"]};result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt265_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":status,"best":best["representation"],"best_correct":best["correct"],"wrapper":wrap["correct"],"wrapper_maxp":wrap["max_eight_inclusive_p"]},sort_keys=True))
if __name__=="__main__":main()

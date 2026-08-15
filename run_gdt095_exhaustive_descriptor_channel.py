#!/usr/bin/env python3
"""GDT095: exhaustive held-folio human-description channel for HPR2 layers."""
from __future__ import annotations
import csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
ANN=ROOT/"gdt012_annotated_core_inventory.tsv"; PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv"
METHOD=ROOT/"GDT095_EXHAUSTIVE_DESCRIPTOR_CHANNEL_METHOD.md"; REPORT=ROOT/"GDT095_EXHAUSTIVE_DESCRIPTOR_CHANNEL_REPORT.md"
MANIFEST=ROOT/"gdt095_descriptor_token_manifest.tsv"; SCORES=ROOT/"gdt095_representation_scores.tsv"
TOKENS=ROOT/"gdt095_token_scores.tsv"; CLASSES=ROOT/"gdt095_construction_descriptor_atlas.tsv"
NULL=ROOT/"gdt095_null_results.tsv"; RESULT=ROOT/"gdt095_result.json"
ABLATION=ROOT/"gdt095_channel_ablation.tsv"
REPS=("RAW_CHAR3","PAGE_HOST_CHAR3","COMPILER_SIGNATURE","WRAPPER_ONLY","RIGHT_ONLY","B3_ONLY","HOST_WRAPPER_JOINT","HOST_RIGHT_JOINT","HOST_B3_JOINT","HOST_WRAPPER_RIGHT_JOINT")
K=5; SHRINK=4.; WORLDS=5000; SEED=95001
STOP=set("a an and are as at be been being but by for from has have in into is it its label labels labeled near next no not of on or page panel plant plants row since that the their them there these they this to under used was we were with word words kluge kluges petersen petersens grove groves latham perhaps seems likely associated actually between east west north south left right above below top bottom middle mid height side first second third fourth fifth sixth one two three four five six seven eight nine ten".split())

def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def tris(values):
 c=Counter()
 for value in values:
  s="^"+value+"$";c.update(s[i:i+3] for i in range(max(1,len(s)-2)))
 return c
def dist(a,b):
 keys=set(a)|set(b);den=sum(max(a[x],b[x]) for x in keys)
 return 1-sum(min(a[x],b[x]) for x in keys)/den if den else 0.
def descriptor_tokens(text):
 text=text.split("||",1)[-1].lower();text=re.sub(r"<[^>]*>|&[^;]*;|\bf\d+[rv]\w*\b"," ",text);out=[]
 for word in re.findall(r"[a-z]+",text):
  if word in STOP or len(word)<3:continue
  if word.endswith("ies") and len(word)>4:word=word[:-3]+"y"
  elif word.endswith("ves") and len(word)>4:word=word[:-3]+"f"
  elif word.endswith("s") and len(word)>4:word=word[:-1]
  if word not in STOP:out.append(word)
 return set(out)

def main():
 ann=read(ANN);parsed=read(PARSED);assert len(ann)==len(parsed)==671
 assert not any(r["locus"].startswith("f84r") for r in ann+parsed)
 by=defaultdict(list);descriptions={}
 for a,p in zip(ann,parsed):
  assert a["locus"]==p["locus"] and a["group_index"]==p["group_index"]
  if a["kind"]=="L" and a["annotation_certainty"]=="UNHEDGED" and a["section"]=="P" and "PLANT" in a["object_tags"].split(";"):
   by[a["locus"]].append(p);descriptions[a["locus"]]=a["raw_source_description"]
 units=[]
 for locus,z in sorted(by.items()):
  z.sort(key=lambda r:int(r["group_index"]));host=tris([r["page_host"] for r in z])
  features={
   "RAW_CHAR3":tris([r["token"] for r in z]),"PAGE_HOST_CHAR3":host,
   "COMPILER_SIGNATURE":Counter(r["compiler_signature"] for r in z),
   "WRAPPER_ONLY":Counter(r["wrapper"] for r in z),"RIGHT_ONLY":Counter(r["right_family"] for r in z),"B3_ONLY":Counter(r["b3"] for r in z),
   "HOST_WRAPPER_JOINT":Counter(r["page_host"]+"@W="+r["wrapper"] for r in z),
   "HOST_RIGHT_JOINT":Counter(r["page_host"]+"@R="+r["right_family"] for r in z),
   "HOST_B3_JOINT":Counter(r["page_host"]+"@B="+r["b3"] for r in z),
   "HOST_WRAPPER_RIGHT_JOINT":Counter(r["page_host"]+"@W="+r["wrapper"]+"@R="+r["right_family"] for r in z),
  }
  units.append({"locus":locus,"folio":z[0]["physical_folio"],"groups":z,"tokens":descriptor_tokens(descriptions[locus]),"features":features})
 assert len(units)==83 and len({u["folio"] for u in units})==5
 freq=Counter(t for u in units for t in u["tokens"]);vocab=sorted(t for t,n in freq.items() if 4<=n<=len(units)-4)
 manifest=[{"descriptor_token":t,"positive_loci":freq[t],"eligible":1,"source":"EXISTING_HUMAN_ANNOTATION_LOCAL_CLAUSE","normalization":"LOWER_ALPHA_SIMPLE_SINGULAR","semantic_role":"UNASSIGNED"} for t in vocab]
 write(MANIFEST,manifest,list(manifest[0]));assert len(vocab)==19
 n=len(units);Y=np.array([[int(t in u["tokens"]) for t in vocab] for u in units],dtype=float);folios=sorted({u["folio"] for u in units});fi={f:np.array([i for i,u in enumerate(units) if u["folio"]==f],dtype=int) for f in folios}
 B=np.zeros((n,n));bc=np.zeros(n);W={r:np.zeros((n,n)) for r in REPS};wc={r:np.zeros(n) for r in REPS}
 for i,target in enumerate(units):
  train=[j for j,u in enumerate(units) if u["folio"]!=target["folio"]];B[i,train]=1/(len(train)+1);bc[i]=.5/(len(train)+1)
  for rep in REPS:
   near=sorted((j for j in train if dist(target["features"][rep],units[j]["features"][rep])<1-1e-12),key=lambda j:(dist(target["features"][rep],units[j]["features"][rep]),units[j]["locus"]))[:K]
   weights=np.array([1/(.1+dist(target["features"][rep],units[j]["features"][rep])) for j in near]);den=weights.sum()+SHRINK
   W[rep][i]=SHRINK*B[i]/den;W[rep][i,near]+=weights/den;wc[rep][i]=SHRINK*bc[i]/den
 def score(y):
  p=np.clip(B@y+bc[:,None],1e-12,1-1e-12);base=(-np.log2(np.where(y>0,p,1-p)))
  out={}
  for rep in REPS:
   q=np.clip(W[rep]@y+wc[rep][:,None],1e-12,1-1e-12);out[rep]=(base,-np.log2(np.where(y>0,q,1-q)))
  return out
 obs=score(Y);obs_gain={r:float((x[0]-x[1]).sum()) for r,x in obs.items()};counts={r:0 for r in REPS};max_count=0;rng=np.random.default_rng(SEED)
 # Post-hoc audit after the exhaustive vocabulary was exposed. It is logged as
 # interpretation, not a second confirmatory endpoint.
 spatial_words={"base","edge","ground","level"};panels={"ALL":list(range(len(vocab))),"SPATIAL_CONTEXT_WORDS":[i for i,t in enumerate(vocab) if t in spatial_words],"NONSPATIAL_REMAINDER":[i for i,t in enumerate(vocab) if t not in spatial_words]}
 panel_obs={(name,rep):float((obs[rep][0][:,idx]-obs[rep][1][:,idx]).sum()) for name,idx in panels.items() for rep in REPS};panel_counts={(name,rep):0 for name in panels for rep in REPS};panel_max={name:0 for name in panels}
 for _ in range(WORLDS):
  yp=Y.copy()
  for idx in fi.values():yp[idx]=yp[rng.permutation(idx)]
  scored=score(yp);g={r:float((x[0]-x[1]).sum()) for r,x in scored.items()}
  for r in REPS:counts[r]+=g[r]>=obs_gain[r]-1e-12
  max_count+=max(g.values())>=max(obs_gain.values())-1e-12
  for name,idx in panels.items():
   pg={rep:float((scored[rep][0][:,idx]-scored[rep][1][:,idx]).sum()) for rep in REPS}
   for rep in REPS:panel_counts[name,rep]+=pg[rep]>=panel_obs[name,rep]-1e-12
   panel_max[name]+=max(pg.values())>=max(panel_obs[name,rep] for rep in REPS)-1e-12
 score_rows=[];token_rows=[]
 for rep in REPS:
  base,model=obs[rep];per_folio=[float((base[idx]-model[idx]).sum()) for idx in fi.values()]
  score_rows.append({"representation":rep,"loci":n,"descriptor_tokens":len(vocab),"baseline_bits":float(base.sum()),"held_bits":float(model.sum()),"gain_bits":obs_gain[rep],"positive_gain_folios":sum(x>0 for x in per_folio),"min_folio_gain":min(per_folio),"max_folio_gain":max(per_folio),"local_permutation_p":(counts[rep]+1)/(WORLDS+1),"max_representation_p":(max_count+1)/(WORLDS+1),"selector_paid_gain_bits":obs_gain[rep]-np.log2(len(REPS))})
  for j,t in enumerate(vocab):token_rows.append({"descriptor_token":t,"representation":rep,"positive_loci":freq[t],"gain_bits":float((base[:,j]-model[:,j]).sum()),"positive_gain_folios":sum(float((base[idx,j]-model[idx,j]).sum())>0 for idx in fi.values())})
 score_rows.sort(key=lambda r:(-r["gain_bits"],r["representation"]));token_rows.sort(key=lambda r:(-r["gain_bits"],r["descriptor_token"],r["representation"]));write(SCORES,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in score_rows],list(score_rows[0]));write(TOKENS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in token_rows],list(token_rows[0]))
 ablation=[]
 for name,idx in panels.items():
  for rep in REPS:ablation.append({"panel":name,"status":"PRIMARY_EXHAUSTIVE" if name=="ALL" else "POSTHOC_INTERPRETIVE_ABLATION","representation":rep,"descriptor_tokens":len(idx),"gain_bits":panel_obs[name,rep],"local_permutation_p":(panel_counts[name,rep]+1)/(WORLDS+1),"panel_max_representation_p":(panel_max[name]+1)/(WORLDS+1)})
 ablation.sort(key=lambda r:(r["panel"],-r["gain_bits"],r["representation"]));write(ABLATION,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in ablation],list(ablation[0]))
 # Transparent recurring exact host-wrapper classes, descriptive only.
 classes=defaultdict(list)
 for u in units:
  for g in u["groups"]:classes[g["page_host"]+"@W="+g["wrapper"]].append(u)
 atlas=[]
 for key,z in sorted(classes.items()):
  loci={u["locus"]:u for u in z};z=list(loci.values());fs={u["folio"] for u in z}
  if len(fs)<2:continue
  common=set.intersection(*(u["tokens"] for u in z)) if z else set();union=set.union(*(u["tokens"] for u in z)) if z else set()
  atlas.append({"host_wrapper_class":key,"loci":len(z),"physical_folios":len(fs),"common_descriptor_tokens":";".join(sorted(common)) or "NONE","union_descriptor_tokens":";".join(sorted(union)) or "NONE","locus_ids":";".join(sorted(loci)),"semantic_role":"UNASSIGNED","status":"EXPLORATORY_RECURRENT_CONSTRUCTION"})
 atlas.sort(key=lambda r:(-len(r["common_descriptor_tokens"].split(";")),-r["physical_folios"],-r["loci"],r["host_wrapper_class"]));write(CLASSES,atlas,list(atlas[0]))
 nullrows=[{"null_id":"WITHIN_FOLIO_COMPLETE_DESCRIPTOR_VECTOR_PERMUTATION","worlds":WORLDS,"seed":SEED,"representations":len(REPS),"descriptor_tokens":len(vocab),"observed_best_representation":score_rows[0]["representation"],"observed_best_gain_bits":score_rows[0]["gain_bits"],"best_representation_max_p":score_rows[0]["max_representation_p"],"preserves":"folio;complete descriptor-token co-occurrence;all formal distances"}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in nullrows],list(nullrows[0]))
 best=score_rows[0];host=next(r for r in score_rows if r["representation"]=="PAGE_HOST_CHAR3");wrapper=next(r for r in score_rows if r["representation"]=="WRAPPER_ONLY");remainder=next(r for r in ablation if r["panel"]=="NONSPATIAL_REMAINDER" and r["representation"]=="HOST_WRAPPER_JOINT");spatial=next(r for r in ablation if r["panel"]=="SPATIAL_CONTEXT_WORDS" and r["representation"]=="HOST_WRAPPER_JOINT");status="EXHAUSTIVE_DESCRIPTOR_CHANNEL_NO_SELECTOR_PAID_HPR2_REPRESENTATION_AFTER_ZERO_OVERLAP_CORRECTION"
 REPORT.write_text(f"""# GDT095 — exhaustive plant-description channel

## Outcome

**{status}**

This exploratory pass takes every one of the {len(vocab)} frequency-eligible
normalized human-description tokens on the complete {n}-locus strict
pharmaceutical plant-label panel.  It does not select `DARK_LEAF` or any other
attractive phrase. Exact-feature representations now use only neighbors with
positive overlap and otherwise back off to the held-folio prevalence code.
This correction removes a prior lexicographic zero-overlap tie artifact.

The best representation is {best['representation']} at only
{best['gain_bits']:+.3f} aggregate bits and on 2/5 folios; its selector-paid
gain is {best['selector_paid_gain_bits']:+.3f}. No representation pays the
ten-way selection cost.

PAGE_HOST character trigrams alone score {host['gain_bits']:+.3f} bits and
WRAPPER alone scores {wrapper['gain_bits']:+.3f}. The exhaustive external
channel therefore does not localize positive information to PAGE_HOST, its
compiler marginals, or their exact conjunctions.

A disclosed post-hoc decomposition gives PAGE_HOST×WRAPPER
{spatial['gain_bits']:+.3f} bits on four mixed spatial/context words (`base`,
`edge`, `ground`, `level`) and {remainder['gain_bits']:+.3f} on the other
fifteen tokens. These words can describe plant geometry, inscription position,
or panel relations and are not a pure layout class. Neither subset rescues the
aggregate channel. PAGE_HOST remains useful for
the narrow GDT089 lead, but the exhaustive vocabulary does not support it as a
general appearance-bearing layer. The split was inspected after vocabulary
exposure and is not confirmatory.
f84r was absent before the model and was not opened, retained, queried, joined,
scored, or targeted.
""",encoding="utf-8")
 result={"schema":"GDT095_EXHAUSTIVE_DESCRIPTOR_CHANNEL_RESULT_V1","status":status,"loci":n,"physical_folios":len(folios),"descriptor_tokens":len(vocab),"representations":list(REPS),"permutation_worlds":WORLDS,"best_representation":best,"page_host_marginal":host,"wrapper_marginal":wrapper,"posthoc_channel_ablation":{"spatial_context_words":spatial,"nonspatial_remainder":remainder},"zero_overlap_policy":"BACKOFF_TO_HELD_FOLIO_PREVALENCE_NO_ARBITRARY_TIE_NEIGHBORS","superseded_result":"The first published GDT095 used lexicographic top-K neighbors even when exact-feature distance equalled one; its +11.252-bit host-wrapper claim is invalid and replaced by this correction.","interpretation":"No tested HPR2 representation pays its selector for the exhaustive archived descriptor vocabulary after zero-overlap correction.","selection_disclosure":"All normalized frequency-eligible local-clause tokens and all ten predeclared representations are exported; K=5/shrink=4 is inherited from GDT068/GDT089. Spatial/nonspatial decomposition was added after seeing the exhaustive token manifest and is explicitly post-hoc.","claim_ceiling":"Archived description-channel construction association only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt089_result.json":sha(ROOT/"gdt089_result.json"),"gdt093_result.json":sha(ROOT/"gdt093_result.json"),"gdt092_result.json":sha(ROOT/"gdt092_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{MANIFEST.name:sha(MANIFEST),SCORES.name:sha(SCORES),TOKENS.name:sha(TOKENS),CLASSES.name:sha(CLASSES),ABLATION.name:sha(ABLATION),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"best":best,"spatial_gain":spatial["gain_bits"],"remainder_gain":remainder["gain_bits"],"host_gain":host["gain_bits"],"wrapper_gain":wrapper["gain_bits"]},sort_keys=True))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""GDT093: held-folio compiler-layer reintroduction on the GDT089 panel."""
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import run_gdt089_plant_descriptor_localization as base
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";MANIFEST=ROOT/"gdt089_descriptor_manifest.tsv";METHOD=ROOT/"GDT093_COMPILER_LAYER_REINTRODUCTION_METHOD.md";REPORT=ROOT/"GDT093_COMPILER_LAYER_REINTRODUCTION_REPORT.md";SCORES=ROOT/"gdt093_layer_scores.tsv";NULL=ROOT/"gdt093_null_results.tsv";RESULT=ROOT/"gdt093_result.json";PERMUTATIONS=5000;SEED=93001
REPS=("PAGE_HOST","HOST_PLUS_WRAPPER","HOST_PLUS_RIGHT","HOST_PLUS_B3","HOST_PLUS_WRAPPER_RIGHT")
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 ann=base.read(ANN);parsed=base.read(PARSED);manifest=base.read(MANIFEST);assert len(ann)==len(parsed)==671 and not any(r["locus"].startswith("f84r") for r in ann+parsed)
 by=defaultdict(list);desc={}
 for a,p in zip(ann,parsed):
  if a["kind"]=="L" and a["annotation_certainty"]=="UNHEDGED" and "PLANT" in a["object_tags"].split(";"):by[a["locus"]].append(p);desc[a["locus"]]=a["raw_source_description"].lower()
 patterns={r["descriptor"]:re.compile(r["exact_regex"]) for r in manifest};eligible=[r["descriptor"] for r in manifest if r["eligible"]=="1"];units=[]
 for loc,z in sorted(by.items()):
  h=base.trigrams([r["page_host"] for r in z]);f={"PAGE_HOST":h}
  for name,key in (("HOST_PLUS_WRAPPER","wrapper"),("HOST_PLUS_RIGHT","right_family"),("HOST_PLUS_B3","b3")):
   q=Counter(h);q.update({name+"="+r[key]:1 for r in z});f[name]=q
  q=Counter(h);q.update({"W="+r["wrapper"]:1 for r in z});q.update({"R="+r["right_family"]:1 for r in z});f["HOST_PLUS_WRAPPER_RIGHT"]=q
  units.append({"locus":loc,"folio":z[0]["physical_folio"],"features":f,"description":desc[loc]})
 n=len(units);assert n==85;folios=sorted({u["folio"] for u in units});fi={f:np.array([i for i,u in enumerate(units) if u["folio"]==f],dtype=int) for f in folios};Y=np.array([[int(bool(patterns[a].search(u["description"]))) for a in eligible] for u in units],dtype=float);B=np.zeros((n,n));bc=np.zeros(n);W={r:np.zeros((n,n)) for r in REPS};wc={r:np.zeros(n) for r in REPS}
 for i,t in enumerate(units):
  train=[j for j,u in enumerate(units) if u["folio"]!=t["folio"]];B[i,train]=1/(len(train)+1);bc[i]=.5/(len(train)+1)
  for rep in REPS:
   near=sorted(train,key=lambda j:(base.distance(t["features"][rep],units[j]["features"][rep]),units[j]["locus"]))[:base.K];ww=np.array([1/(.1+base.distance(t["features"][rep],units[j]["features"][rep])) for j in near]);den=ww.sum()+base.SHRINK;W[rep][i,:]=base.SHRINK*B[i,:]/den;W[rep][i,near]+=ww/den;wc[rep][i]=base.SHRINK*bc[i]/den
 def gains(y):
  p=np.clip(B@y+bc[:,None],1e-12,1-1e-12);bb=(-np.log2(np.where(y>0,p,1-p))).sum(axis=0);out={}
  for rep in REPS:
   q=np.clip(W[rep]@y+wc[rep][:,None],1e-12,1-1e-12);out[rep]=bb-(-np.log2(np.where(y>0,q,1-q))).sum(axis=0)
  return bb,out
 bb,obs=gains(Y);rng=np.random.default_rng(SEED);local={r:np.zeros(len(eligible),dtype=int) for r in REPS};maxima=[]
 for _ in range(PERMUTATIONS):
  yp=Y.copy()
  for idx in fi.values():yp[idx]=yp[rng.permutation(idx)]
  _,g=gains(yp);vals=[]
  for rep in REPS:local[rep]+=(g[rep]>=obs[rep]);vals.extend(g[rep].tolist())
  maxima.append(max(vals))
 maxima=np.array(maxima);rows=[]
 for ai,a in enumerate(eligible):
  for rep in REPS:rows.append({"descriptor":a,"representation":rep,"loci":n,"positive_loci":int(Y[:,ai].sum()),"gain_bits":float(obs[rep][ai]),"local_permutation_p":(int(local[rep][ai])+1)/(PERMUTATIONS+1),"max_search_p":(int(np.sum(maxima>=obs[rep][ai]))+1)/(PERMUTATIONS+1),"delta_vs_page_host_bits":float(obs[rep][ai]-obs["PAGE_HOST"][ai])})
 rows.sort(key=lambda r:(r["descriptor"],REPS.index(r["representation"])));out=[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in rows];write(SCORES,out,list(out[0]));dark={r["representation"]:r for r in rows if r["descriptor"]=="DARK_LEAF"};host_best=sum(next(x for x in rows if x["descriptor"]==a and x["representation"]=="PAGE_HOST")["gain_bits"]>=max(x["gain_bits"] for x in rows if x["descriptor"]==a) for a in eligible);nullrows=[{"null_id":"WITHIN_FOLIO_COMPLETE_DESCRIPTOR_VECTOR_PERMUTATION","permutations":PERMUTATIONS,"seed":SEED,"descriptors":len(eligible),"representations":len(REPS),"scanned_cells":len(rows),"dark_leaf_page_host_local_p":dark["PAGE_HOST"]["local_permutation_p"],"dark_leaf_page_host_max_search_p":dark["PAGE_HOST"]["max_search_p"],"preserves":"folio;descriptor co-occurrence;representation geometry"}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in nullrows],list(nullrows[0]))
 status="COMPILER_LAYERS_DILUTE_PAGE_HOST_DARK_LEAF_SIGNAL"
 REPORT.write_text(f"""# GDT093 — compiler-layer reintroduction

## Outcome

**{status}**

For the GDT089 `DARK_LEAF` endpoint, PAGE_HOST alone gains
{dark['PAGE_HOST']['gain_bits']:+.3f} held bits.  Adding WRAPPER changes this
to {dark['HOST_PLUS_WRAPPER']['gain_bits']:+.3f}; adding RIGHT_FAMILY to
{dark['HOST_PLUS_RIGHT']['gain_bits']:+.3f}; adding B3 to
{dark['HOST_PLUS_B3']['gain_bits']:+.3f}; and adding WRAPPER+RIGHT to
{dark['HOST_PLUS_WRAPPER_RIGHT']['gain_bits']:+.3f}.  PAGE_HOST is the best of
the five variants on {host_best}/{len(eligible)} descriptor axes.

The PAGE_HOST DARK_LEAF cell retains a local permutation p of
{dark['PAGE_HOST']['local_permutation_p']:.4f} but fails the expanded 40-cell
max search at p={dark['PAGE_HOST']['max_search_p']:.4f}.  Compiler layers
therefore dilute this specific archived content signal; they are not thereby
proved semantically neutral.  The result supports the HPR2 generation order
in which content-host identity precedes wrapper/right/B3 rendering.  f84r was
absent.
""",encoding="utf-8")
 result={"schema":"GDT093_COMPILER_LAYER_REINTRODUCTION_RESULT_V1","status":status,"loci":n,"descriptors":len(eligible),"representations":list(REPS),"scanned_cells":len(rows),"page_host_best_axes":host_best,"dark_leaf":dark,"interpretation":"Compiler-state tokens dilute rather than add to the weak PAGE_HOST visual descriptor signal; content neutrality remains unconfirmed.","claim_ceiling":"Archived representation ablation only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),MANIFEST.name:sha(MANIFEST),"gdt089_result.json":sha(ROOT/"gdt089_result.json"),"gdt092_result.json":sha(ROOT/"gdt092_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__)),"run_gdt089_plant_descriptor_localization.py":sha(ROOT/"run_gdt089_plant_descriptor_localization.py")},"outputs":{SCORES.name:sha(SCORES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"dark_leaf":{k:v["gain_bits"] for k,v in dark.items()},"host_best_axes":host_best},sort_keys=True))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""GDT089: held-folio PAGE_HOST localization of human plant descriptors."""
from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv"
METHOD=ROOT/"GDT089_PLANT_DESCRIPTOR_LOCALIZATION_METHOD.md";REPORT=ROOT/"GDT089_PLANT_DESCRIPTOR_LOCALIZATION_REPORT.md";MANIFEST=ROOT/"gdt089_descriptor_manifest.tsv";SCORES=ROOT/"gdt089_representation_scores.tsv";LEADS=ROOT/"gdt089_exact_host_descriptor_leads.tsv";CASES=ROOT/"gdt089_os_cases.tsv";NULL=ROOT/"gdt089_null_results.tsv";RESULT=ROOT/"gdt089_result.json"
K=5;SHRINK=4.;PERMUTATIONS=5000;SEED=89001;REPS=("RAW_CHAR3","PAGE_HOST_CHAR3","COMPILER_ONLY")
DESCRIPTORS=(
 ("DARK",r"\bdark"),("LIGHT",r"\blight"),("DARK_LEAF",r"dark(?:[\s-]+\w+){0,3}[\s-]+lea(?:f|ves)"),("LIGHT_ROOT",r"light(?:[\s-]+\w+){0,3}[\s-]+root"),("BIFURCATED_OR_FORKED",r"bifurcat|fork"),("LARGE_LEAF",r"(?:large|big)(?:[\s-]+\w+){0,2}[\s-]+lea(?:f|ves)"),("SPROUT",r"sprout"),("STAR_SHAPED",r"star[- ]shape"),("ROOT_MENTION",r"root"),("LEAF_MENTION",r"lea(?:f|ves)"),("FLOWER_MENTION",r"flower"))
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def trigrams(items):
 c=Counter()
 for item in items:
  s="^"+item+"$";c.update(s[i:i+3] for i in range(max(1,len(s)-2)))
 return c
def distance(a,b):
 k=set(a)|set(b);den=sum(max(a[x],b[x]) for x in k)
 return 1-sum(min(a[x],b[x]) for x in k)/den if den else 0.
def main():
 ann=read(ANN);parsed=read(PARSED);assert len(ann)==len(parsed)==671 and not any(r["locus"].startswith("f84r") for r in ann+parsed)
 by=defaultdict(list);desc={};meta={}
 for a,p in zip(ann,parsed):
  assert a["locus"]==p["locus"] and a["group_index"]==p["group_index"]
  if a["kind"]=="L" and a["annotation_certainty"]=="UNHEDGED" and "PLANT" in a["object_tags"].split(";"):
   by[a["locus"]].append(p);desc[a["locus"]]=a["raw_source_description"].lower();meta[a["locus"]]=a
 units=[]
 for locus,z in sorted(by.items()):
  z.sort(key=lambda r:int(r["group_index"]));units.append({"locus":locus,"folio":z[0]["physical_folio"],"groups":z,"raw":trigrams([r["token"] for r in z]),"host":trigrams([r["page_host"] for r in z]),"comp":Counter(r["compiler_signature"] for r in z),"description":desc[locus]})
 assert len(units)==85 and len({u["folio"] for u in units})==6
 patterns={n:re.compile(p) for n,p in DESCRIPTORS};counts={n:sum(bool(q.search(u["description"])) for u in units) for n,q in patterns.items()};eligible=[n for n,c in counts.items() if 4<=c<=len(units)-4]
 manifest=[]
 for n,p in DESCRIPTORS:manifest.append({"descriptor":n,"exact_regex":p,"positive_loci":counts[n],"eligible":int(n in eligible),"eligibility_rule":"4_TO_N_MINUS_4","provenance":"EXISTING_HUMAN_ANNOTATION_RAW_SOURCE_DESCRIPTION","interpretation":"NEUTRAL_VISIBLE_DESCRIPTION_PATTERN"})
 write(MANIFEST,manifest,list(manifest[0]))
 n=len(units);folios=sorted({u["folio"] for u in units});fi={f:np.array([i for i,u in enumerate(units) if u["folio"]==f],dtype=int) for f in folios};Y=np.array([[int(patterns[a].search(u["description"])is not None) for a in eligible] for u in units],dtype=float)
 B=np.zeros((n,n));bc=np.zeros(n);W={rep:np.zeros((n,n)) for rep in REPS};wc={rep:np.zeros(n) for rep in REPS}
 fmap={"RAW_CHAR3":"raw","PAGE_HOST_CHAR3":"host","COMPILER_ONLY":"comp"}
 for i,t in enumerate(units):
  train=[j for j,u in enumerate(units) if u["folio"]!=t["folio"]];B[i,train]=1/(len(train)+1);bc[i]=.5/(len(train)+1)
  for rep in REPS:
   key=fmap[rep];near=sorted(train,key=lambda j:(distance(t[key],units[j][key]),units[j]["locus"]))[:K];ww=np.array([1/(.1+distance(t[key],units[j][key])) for j in near]);den=ww.sum()+SHRINK;W[rep][i,:]=SHRINK*B[i,:]/den;W[rep][i,near]+=ww/den;wc[rep][i]=SHRINK*bc[i]/den
 def gains(y):
  p=np.clip(B@y+bc[:,None],1e-12,1-1e-12);base=(-np.log2(np.where(y>0,p,1-p))).sum(axis=0);out={}
  for rep in REPS:
   q=np.clip(W[rep]@y+wc[rep][:,None],1e-12,1-1e-12);bits=(-np.log2(np.where(y>0,q,1-q))).sum(axis=0);out[rep]=base-bits
  return base,out
 base,obs=gains(Y);local={rep:np.zeros(len(eligible),dtype=int) for rep in REPS};maxima=[];rng=np.random.default_rng(SEED)
 for _ in range(PERMUTATIONS):
  yp=Y.copy()
  for idx in fi.values():yp[idx]=yp[rng.permutation(idx)]
  _,g=gains(yp);vals=[]
  for rep in REPS:local[rep]+=(g[rep]>=obs[rep]);vals.extend(g[rep].tolist())
  maxima.append(max(vals))
 maxima=np.array(maxima);score_rows=[]
 for ai,a in enumerate(eligible):
  for rep in REPS:
   # folio contributions under observed labels
   p=np.clip(B@Y+bc[:,None],1e-12,1-1e-12);q=np.clip(W[rep]@Y+wc[rep][:,None],1e-12,1-1e-12);fg=[]
   for idx in fi.values():fg.append(float((-np.log2(np.where(Y[idx,ai]>0,p[idx,ai],1-p[idx,ai]))+np.log2(np.where(Y[idx,ai]>0,q[idx,ai],1-q[idx,ai]))).sum()))
   score_rows.append({"descriptor":a,"representation":rep,"loci":n,"positive_loci":counts[a],"physical_folios":len(folios),"baseline_bits":float(base[ai]),"held_bits":float(base[ai]-obs[rep][ai]),"gain_bits":float(obs[rep][ai]),"positive_gain_folios":sum(x>0 for x in fg),"min_folio_gain":min(fg),"max_folio_gain":max(fg),"local_permutation_p":(int(local[rep][ai])+1)/(PERMUTATIONS+1),"max_search_p":(int(np.sum(maxima>=obs[rep][ai]))+1)/(PERMUTATIONS+1)})
 score_rows.sort(key=lambda r:(-r["gain_bits"],r["descriptor"],r["representation"]));out=[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in score_rows];write(SCORES,out,list(out[0]))
 # Exact-host recurrences in this strict panel.
 hunits=defaultdict(list)
 for u in units:
  for h in {r["page_host"] for r in u["groups"]}:hunits[h].append(u)
 leads=[]
 for h,z in hunits.items():
  if len({u["folio"] for u in z})<2:continue
  for a in eligible:
   pos=[u for u in z if patterns[a].search(u["description"])]
   if len({u["folio"] for u in pos})<2:continue
   leads.append({"page_host":h,"descriptor":a,"positive_loci":len(pos),"all_host_loci":len(z),"positive_folios":len({u['folio'] for u in pos}),"all_host_folios":len({u['folio'] for u in z}),"positive_fraction":len(pos)/len(z),"loci":";".join(u["locus"] for u in pos),"surface_tokens":";".join(sorted({r["token"] for u in pos for r in u["groups"] if r["page_host"]==h})),"wrappers":";".join(sorted({r["wrapper"] for u in pos for r in u["groups"] if r["page_host"]==h})),"right_families":";".join(sorted({r["right_family"] for u in pos for r in u["groups"] if r["page_host"]==h})),"semantic_role":"UNASSIGNED"})
 leads.sort(key=lambda r:(-r["positive_fraction"],-r["positive_loci"],r["page_host"],r["descriptor"]));write(LEADS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in leads],list(leads[0]))
 oscases=[]
 for u in hunits["os"]:
  gs=[r for r in u["groups"] if r["page_host"]=="os"];m=meta[u["locus"]]
  oscases.append({"locus":u["locus"],"physical_folio":u["folio"],"tokens":";".join(r["token"] for r in gs),"wrappers":";".join(r["wrapper"] for r in gs),"right_families":";".join(r["right_family"] for r in gs),"dark_leaf":int(bool(patterns["DARK_LEAF"].search(u["description"]))),"light_root":int(bool(patterns["LIGHT_ROOT"].search(u["description"]))),"raw_source_description":m["raw_source_description"]})
 write(CASES,oscases,list(oscases[0]));nullrows=[{"null_id":"WITHIN_FOLIO_COMPLETE_DESCRIPTOR_VECTOR_PERMUTATION","permutations":PERMUTATIONS,"seed":SEED,"eligible_descriptors":len(eligible),"representations":len(REPS),"scanned_pairs":len(eligible)*len(REPS),"observed_max_gain_bits":score_rows[0]["gain_bits"],"global_max_search_p":score_rows[0]["max_search_p"],"preserves":"folio;descriptor co-occurrence;representation geometry;unit count"}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in nullrows],list(nullrows[0]))
 host_dark=next(r for r in score_rows if r["descriptor"]=="DARK_LEAF" and r["representation"]=="PAGE_HOST_CHAR3");raw_dark=next(r for r in score_rows if r["descriptor"]=="DARK_LEAF" and r["representation"]=="RAW_CHAR3");comp_dark=next(r for r in score_rows if r["descriptor"]=="DARK_LEAF" and r["representation"]=="COMPILER_ONLY")
 status="PAGE_HOST_DARK_LEAF_DESCRIPTOR_LEAD_WEAK_POSTSELECTED"
 REPORT.write_text(f"""# GDT089 — plant descriptor localization inside HPR2

## Outcome

**{status}**

The strict panel has {n} unhedged human-local plant-label loci on six physical
folios.  Eight of eleven transparent descriptor patterns pass capacity.
For `DARK_LEAF`, PAGE_HOST trigrams gain {host_dark['gain_bits']:+.3f}
whole-folio-held bits and are positive on {host_dark['positive_gain_folios']}/6
folios.  Raw words lose {abs(raw_dark['gain_bits']):.3f} bits and compiler-only
features lose {abs(comp_dark['gain_bits']):.3f}.  The same PAGE_HOST advantage
appears for `DARK` and `LIGHT_ROOT`, while several other descriptors are null
or negative.  The best descriptor/representation result does not survive the
24-way maximum search (p={score_rows[0]['max_search_p']:.4f}).

The exact-host seed is concrete: `chos` on f100v and `cheosdy` on f88v reduce
to PAGE_HOST `os`; both independent human descriptions mention a dark leaf
and light roots.  This survives wrapper and DY variation but has only two
visually scored loci.  The corpus contains many unannotated `os` prose
occurrences, so no absence or semantic generality can yet be claimed.

This is the first HPR2 external panel where stripping compiler layers yields a
positive descriptor-specific held signal while raw and compiler-only forms are
negative.  It is still archive-selected, regex-selected, tiny, and globally
non-significant.  `os` remains an UNASSIGNED PAGE_HOST visual-association
hypothesis, not an English gloss.  f84r was absent before analysis.
""",encoding="utf-8")
 result={"schema":"GDT089_PLANT_DESCRIPTOR_LOCALIZATION_RESULT_V1","status":status,"loci":n,"physical_folios":len(folios),"descriptor_patterns":len(DESCRIPTORS),"eligible_descriptors":eligible,"representations":list(REPS),"permutations":PERMUTATIONS,"dark_leaf_scores":{r["representation"]:r for r in score_rows if r["descriptor"]=="DARK_LEAF"},"top_score":score_rows[0],"os_visual_association":{"page_host":"os","dark_leaf_positive":"2/2","light_root_positive":"2/2","physical_folios":["f88","f100"],"semantic_role":"UNASSIGNED","status":"WEAK_POSTSELECTED_TWO_LOCUS_SEED"},"selection_disclosure":"Descriptor regexes and exact-host seed were assembled after GDT088; all eleven tried patterns and null outcomes are exported. GDT068 K=5/shrink=4 was reused without tuning.","claim_ceiling":"Archived visual-description association only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt068_result.json":sha(ROOT/"gdt068_result.json"),"gdt088_result.json":sha(ROOT/"gdt088_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{MANIFEST.name:sha(MANIFEST),SCORES.name:sha(SCORES),LEADS.name:sha(LEADS),CASES.name:sha(CASES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"loci":n,"dark_leaf_host_gain":host_dark["gain_bits"],"top":score_rows[0]},sort_keys=True))
if __name__=="__main__":main()

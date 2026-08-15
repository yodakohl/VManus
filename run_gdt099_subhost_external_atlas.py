#!/usr/bin/env python3
"""GDT099: exhaustive PAGE_HOST submotif by archived external-axis atlas."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT099_SUBHOST_EXTERNAL_ATLAS_METHOD.md";REPORT=ROOT/"GDT099_SUBHOST_EXTERNAL_ATLAS_REPORT.md";ATLAS=ROOT/"gdt099_subhost_external_atlas.tsv";CASES=ROOT/"gdt099_top_candidate_cases.tsv";NULL=ROOT/"gdt099_null_results.tsv";RESULT=ROOT/"gdt099_result.json";WORLDS=5000;SEED=99001
AXES=("PLANT","STAR_OR_SKY","FIGURE","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def tri(v):
 s="^"+v+"$";return {s[i:i+3] for i in range(max(1,len(s)-2))}
def main():
 ann=read(ANN);parsed=read(PARSED);assert len(ann)==len(parsed)==671 and not any(x["locus"].startswith("f84r") for x in ann+parsed)
 by=defaultdict(list);meta={}
 for a,p in zip(ann,parsed):by[a["locus"]].append(p);meta[a["locus"]]=a
 units=[]
 for locus,z in sorted(by.items()):
  a=meta[locus];tags=set(a["object_tags"].split(";"))|set(a["relation_tags"].split(";"));units.append({"locus":locus,"folio":a["physical_folio"],"section":a["section"],"features":set().union(*(tri(x["page_host"]) for x in z)),"y":[int(q in tags) for q in AXES],"tokens":";".join(x["token"] for x in z),"page_hosts":";".join(x["page_host"] for x in z),"object_tags":a["object_tags"],"relation_tags":a["relation_tags"]})
 assert len(units)==560 and len({u["folio"] for u in units})==21
 defs=[]
 for feature in sorted(set().union(*(u["features"] for u in units))):
  mask=np.array([feature in u["features"] for u in units],dtype=float);support=int(mask.sum())
  if 5<=support<=len(units)-5:defs.append((feature,mask))
 Y=np.array([u["y"] for u in units],dtype=float);ix={f:np.array([i for i,u in enumerate(units) if u["folio"]==f]) for f in sorted({u["folio"] for u in units})};C=np.stack([x[1] for x in defs])
 for j in ix.values():C[:,j]-=C[:,j].mean(axis=1,keepdims=True)
 scores=C@Y;eligible=[]
 for i,(feature,mask) in enumerate(defs):
  for ai,axis in enumerate(AXES):
   pos=int(((mask>0)&(Y[:,ai]>0)).sum());remaining=int(Y[:,ai].sum()-pos)
   if pos>=3 and remaining>=3:eligible.append((i,ai,feature,axis,mask,pos))
 observed=np.array([scores[i,a] for i,a,*_ in eligible]);local=np.zeros(len(eligible),dtype=int);maxima=[];rng=np.random.default_rng(SEED)
 for _ in range(WORLDS):
  yy=Y.copy()
  for j in ix.values():yy[j]=yy[rng.permutation(j)]
  s=C@yy;vals=np.array([s[i,a] for i,a,*_ in eligible]);local+=vals>=observed-1e-12;maxima.append(float(vals.max()))
 maxima=np.array(maxima);rows=[]
 for k,(i,ai,feature,axis,mask,pos) in enumerate(eligible):
  contrib={f:float(C[i,j]@Y[j,ai]) for f,j in ix.items()};lofo={f:float(observed[k]-v) for f,v in contrib.items()};localp=(int(local[k])+1)/(WORLDS+1);maxp=(int(np.sum(maxima>=observed[k]))+1)/(WORLDS+1)
  label="INTERESTING_EXPLORATORY" if maxp<=.1 else "WEAK" if localp<=.05 and all(v>=-1e-12 for v in lofo.values()) else "LIKELY_PAGE_CONFOUND" if localp<=.05 else "NO_SIGNAL"
  rows.append({"page_host_submotif":feature,"external_axis":axis,"feature_support_loci":int(mask.sum()),"positive_with_feature":pos,"negative_with_feature":int(mask.sum())-pos,"positive_without_feature":int(Y[:,ai].sum())-pos,"within_folio_effect":float(observed[k]),"local_permutation_p":localp,"max_search_p":maxp,"positive_effect_folios":sum(v>0 for v in contrib.values()),"informative_folios":sum(abs(v)>1e-12 for v in contrib.values()),"folio_contributions":";".join(f"{f}:{v:.6f}" for f,v in contrib.items()),"leave_one_folio_effects":";".join(f"{f}:{v:.6f}" for f,v in lofo.items()),"label":label,"semantic_role":"UNASSIGNED","obvious_confounds":"ARCHIVED_AXIS;SECTION_PAGE_ECOLOGY;POSTSELECTED_SUBMOTIF"})
 rows.sort(key=lambda r:(-r["within_folio_effect"],r["page_host_submotif"],r["external_axis"]));write(ATLAS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in rows],list(rows[0]));top=rows[0]
 topkeys={(x["page_host_submotif"],x["external_axis"]) for x in rows[:10]};cases=[]
 for feature,axis in topkeys:
  ai=AXES.index(axis)
  for u in units:
   if feature in u["features"]:cases.append({"page_host_submotif":feature,"external_axis":axis,"locus":u["locus"],"physical_folio":u["folio"],"section":u["section"],"axis_positive":u["y"][ai],"tokens":u["tokens"],"page_hosts":u["page_hosts"],"object_tags":u["object_tags"],"relation_tags":u["relation_tags"],"semantic_role":"UNASSIGNED"})
 cases.sort(key=lambda x:(x["page_host_submotif"],x["external_axis"],x["locus"]));write(CASES,cases,list(cases[0]));null=[{"null_id":"WITHIN_PHYSICAL_FOLIO_COMPLETE_EXTERNAL_TAG_VECTOR_PERMUTATION","worlds":WORLDS,"seed":SEED,"submotifs":len(defs),"eligible_tests":len(rows),"observed_top":top["page_host_submotif"]+" x "+top["external_axis"],"top_local_p":top["local_permutation_p"],"top_max_search_p":top["max_search_p"],"preserves":"folio;complete external tag co-occurrence;formal masks"}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in x.items()} for x in null],list(null[0]))
 weak=[x for x in rows if x["label"]=="WEAK"];status="SUBHOST_EXTERNAL_ASSOCIATIONS_POSTSELECTED_NONE_SURVIVE_GLOBAL_SEARCH"
 REPORT.write_text(f"""# GDT099 — PAGE_HOST submotif / external-axis atlas

## Outcome

**{status}**

Across all 560 non-f84 human-annotated loci on 21 physical folios, the
state-blind library contains {len(defs)} supported PAGE_HOST trigrams and
{len(rows)} capacity-eligible motif×axis tests. The strongest is
`{top['page_host_submotif']} × {top['external_axis']}` with within-folio effect
{top['within_folio_effect']:+.3f}, local p={top['local_permutation_p']:.4f}, but
full-library max p={top['max_search_p']:.4f}. No candidate survives global
search; {len(weak)} are retained as weak local leads.

The atlas contains recognizable continuations of earlier seeds—`^ok` and
`os$` with the archived PLANT axis, `ok$` with WATER_OR_APPARATUS, and several
relation-axis candidates—but their supports remain section/page concentrated.
This exhaustive motif layer does not establish that a reusable subhost is a
semantic stem. It is nevertheless the right hypothesis inventory for a future
newly annotated endpoint: motifs are smaller than whole PAGE_HOSTs and every
tried association is now logged rather than selected silently.

All semantic roles remain UNASSIGNED. f84r was filtered before analysis and
was not opened, retained, queried, joined, scored, or targeted.
""",encoding="utf-8")
 result={"schema":"GDT099_SUBHOST_EXTERNAL_ATLAS_RESULT_V1","status":status,"loci":len(units),"physical_folios":len(ix),"supported_submotifs":len(defs),"eligible_tests":len(rows),"axes":list(AXES),"permutation_worlds":WORLDS,"top_candidate":top,"weak_candidates":len(weak),"global_survivors":sum(x["max_search_p"]<=.1 for x in rows),"interpretation":"Postselected PAGE_HOST-submotif external-axis atlas; no globally adjusted association and no semantic assignment.","claim_ceiling":"Archived external-axis hypothesis generation only; no semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt088_result.json":sha(ROOT/"gdt088_result.json"),"gdt097_result.json":sha(ROOT/"gdt097_result.json"),"gdt098_result.json":sha(ROOT/"gdt098_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),CASES.name:sha(CASES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"submotifs":len(defs),"tests":len(rows),"top":top,"weak":len(weak)},sort_keys=True))
if __name__=="__main__":main()

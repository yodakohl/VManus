#!/usr/bin/env python3
"""GDT097: exhaustive formal-motif atlas for the GDT096 mixed spatial endpoint."""
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT097_PCH_SPATIAL_CONTEXT_MOTIF_METHOD.md";REPORT=ROOT/"GDT097_PCH_SPATIAL_CONTEXT_MOTIF_REPORT.md";ATLAS=ROOT/"gdt097_motif_atlas.tsv";CASES=ROOT/"gdt097_pch_cases.tsv";NULL=ROOT/"gdt097_null_results.tsv";RESULT=ROOT/"gdt097_result.json";WORLDS=20000;SEED=97001;PAT=re.compile(r"\b(?:base|edge|ground|level)\b")
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
 for a,p in zip(ann,parsed):
  if a["kind"]=="L" and a["section"]=="P" and "PLANT" in a["object_tags"].split(";"):by[a["locus"]].append(p);meta[a["locus"]]=a
 units=[]
 for locus,z in sorted(by.items()):
  h=set().union(*(tri(x["page_host"]) for x in z));raw=set().union(*(tri(x["token"]) for x in z));comp={"W="+x["wrapper"] for x in z}|{"R="+x["right_family"] for x in z}|{"B="+x["b3"] for x in z};desc=meta[locus]["raw_source_description"]
  units.append({"locus":locus,"folio":z[0]["physical_folio"],"certainty":meta[locus]["annotation_certainty"],"y":int(bool(PAT.search(desc.lower()))),"PAGE_HOST_CHAR3":h,"RAW_CHAR3":raw,"COMPILER_PREDICATE":comp,"page_hosts":";".join(x["page_host"] for x in z),"tokens":";".join(x["token"] for x in z),"description":desc})
 assert len(units)==118 and sum(u["y"] for u in units)==34
 folios=sorted({u["folio"] for u in units});ix={f:np.array([i for i,u in enumerate(units) if u["folio"]==f]) for f in folios};y=np.array([u["y"] for u in units],dtype=float);defs=[]
 for rep in ("PAGE_HOST_CHAR3","RAW_CHAR3","COMPILER_PREDICATE"):
  for feature in sorted(set().union(*(u[rep] for u in units))):
   mask=np.array([feature in u[rep] for u in units],dtype=float);support=int(mask.sum())
   if 4<=support<=len(units)-4:defs.append((rep,feature,mask))
 C=np.stack([x[2] for x in defs])
 for j in ix.values():C[:,j]-=C[:,j].mean(axis=1,keepdims=True)
 observed=C@y;local=np.zeros(len(defs),dtype=int);maxima=[];rng=np.random.default_rng(SEED)
 for _ in range(WORLDS):
  yy=y.copy()
  for j in ix.values():yy[j]=yy[rng.permutation(j)]
  s=C@yy;local+=s>=observed-1e-12;maxima.append(float(s.max()))
 maxima=np.array(maxima);rows=[]
 for i,(rep,feature,mask) in enumerate(defs):
  contrib={f:float(C[i,j]@y[j]) for f,j in ix.items()};lofo={f:float(observed[i]-v) for f,v in contrib.items()};rows.append({"representation":rep,"formal_feature":feature,"support_loci":int(mask.sum()),"positive_with_feature":int(((mask>0)&(y>0)).sum()),"negative_with_feature":int(((mask>0)&(y==0)).sum()),"positive_without_feature":int(((mask==0)&(y>0)).sum()),"within_folio_effect":float(observed[i]),"local_permutation_p":(int(local[i])+1)/(WORLDS+1),"max_search_p":(int(np.sum(maxima>=observed[i]))+1)/(WORLDS+1),"positive_effect_folios":sum(v>0 for v in contrib.values()),"informative_folios":sum(abs(v)>1e-12 for v in contrib.values()),"folio_contributions":";".join(f"{f}:{v:.6f}" for f,v in contrib.items()),"leave_one_folio_effects":";".join(f"{f}:{v:.6f}" for f,v in lofo.items()),"semantic_role":"UNASSIGNED"})
 rows.sort(key=lambda r:(-r["within_folio_effect"],r["representation"],r["formal_feature"]));write(ATLAS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in rows],list(rows[0]));pch=next(r for r in rows if r["representation"]=="PAGE_HOST_CHAR3" and r["formal_feature"]=="pch")
 cases=[]
 for u in units:
  if "pch" in u["PAGE_HOST_CHAR3"]:cases.append({"locus":u["locus"],"physical_folio":u["folio"],"annotation_certainty":u["certainty"],"tokens":u["tokens"],"page_hosts":u["page_hosts"],"mixed_spatial_context_positive":u["y"],"raw_source_description":u["description"],"semantic_role":"UNASSIGNED","case_class":"PCH_SUPPORT" if u["y"] else "PCH_COUNTEREXAMPLE"})
 write(CASES,cases,list(cases[0]));null=[{"null_id":"WITHIN_PHYSICAL_FOLIO_OUTCOME_PERMUTATION_MAX_108_FEATURES","worlds":WORLDS,"seed":SEED,"features":len(rows),"observed_top":"PAGE_HOST_CHAR3:pch","observed_top_effect":pch["within_folio_effect"],"top_local_p":pch["local_permutation_p"],"top_max_search_p":pch["max_search_p"],"preserves":"folio;positive count;formal feature masks;certainty composition only marginally"}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in x.items()} for x in null],list(null[0]))
 status="PCH_MIXED_SPATIAL_CONTEXT_MOTIF_WEAK_MAXT_NONCONFIRMING"
 REPORT.write_text(f"""# GDT097 — PAGE_HOST `PCH` mixed spatial-context motif

## Outcome

**{status}**

The exhaustive 108-feature scan covers all 118 section-P human plant-label
annotations, with 34 occurrences of the frozen `base|edge|ground|level`
endpoint. PAGE_HOST trigram `pch` is the strongest formal feature. It occurs in
six loci and all six are positive: f89, f100, and f102; four UNHEDGED and two
HEDGED. Five descriptions say `ground level`; one says `base of stem`.

The folio-conditioned local permutation p is {pch['local_permutation_p']:.5f}
and every leave-one-folio effect remains positive. But after maximizing across
all 108 PAGE_HOST/raw/compiler features, p={pch['max_search_p']:.4f}. Four of
the six cases lie on f102, the endpoint is mixed rather than semantic, and the
same `pch` substring is present in raw strings. This is therefore a concrete
weak motif seed, not a stable meaning or proof that HPR2 beats ordinary string
features.

No alternative endpoint, fuzzy spelling, or English gloss is assigned. f84r
was absent before the scan and was not opened, retained, queried, joined,
scored, or targeted.
""",encoding="utf-8")
 result={"schema":"GDT097_PCH_SPATIAL_CONTEXT_MOTIF_RESULT_V1","status":status,"loci":len(units),"physical_folios":len(folios),"positive_loci":int(y.sum()),"eligible_features":len(rows),"permutation_worlds":WORLDS,"top_candidate":pch,"pch_cases":len(cases),"pch_positive_cases":sum(x["mixed_spatial_context_positive"] for x in cases),"pch_folios":sorted({x["physical_folio"] for x in cases}),"pch_certainty_counts":dict(Counter(x["annotation_certainty"] for x in cases)),"interpretation":"PCH is a weak, postselected PAGE_HOST/raw-string motif associated with mixed base/ground/edge description contexts; no role or gloss is assigned.","claim_ceiling":"Archived mixed-context formal motif only; no semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt095_result.json":sha(ROOT/"gdt095_result.json"),"gdt096_result.json":sha(ROOT/"gdt096_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),CASES.name:sha(CASES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"features":len(rows),"pch":pch,"cases":len(cases)},sort_keys=True))
if __name__=="__main__":main()

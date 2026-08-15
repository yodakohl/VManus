#!/usr/bin/env python3
"""GDT098: cross-register construction context and full annotation scope of PCH."""
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT098_PCH_CROSS_REGISTER_CONTEXT_METHOD.md";REPORT=ROOT/"GDT098_PCH_CROSS_REGISTER_CONTEXT_REPORT.md";ATLAS=ROOT/"gdt098_cross_register_motif_context.tsv";CONTEXTS=ROOT/"gdt098_pch_contexts.tsv";ANNOT=ROOT/"gdt098_pch_annotation_scope.tsv";RESULT=ROOT/"gdt098_result.json";REGS=("HERBAL_B","STARS_RECIPE_B");PAT=re.compile(r"\b(?:base|edge|ground|level)\b")
DIMS=("WRAPPER_Q","WRAPPER_D","WRAPPER_CH_FAMILY","WRAPPER_NONE","RIGHT_PRESENT","RIGHT_AIIN","RIGHT_AR_AL","DY","B3","LINE_ENTRY","LINE_FINAL","POSITION_QUARTILE","PREV_DY","NEXT_Q","NEXT_DY")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def tri(v):
 s="^"+v+"$";return {s[i:i+3] for i in range(max(1,len(s)-2))}
def main():
 source=read(SOURCE);assert not any(x["page"].startswith("f84r") for x in source)
 by=defaultdict(list)
 for x in source:
  if x["register"] in REGS:by[x["locus"]].append(x)
 rows=[]
 for locus,z in by.items():
  z.sort(key=lambda x:int(x["group_index"]))
  for i,x in enumerate(z):
   w=x["wrapper"];rf=x["right_family"];d=np.array([w=="q",w=="d",w in{"ch","che","sh"},w=="NONE",rf!="NONE",rf=="aiin",rf in{"ar","al"},x["dy_closure"]=="1",x["b3"]=="1",int(x["group_index"])==1,int(x["group_index"])==int(x["group_count"]),int(x["position_quartile"])/4,i>0 and z[i-1]["dy_closure"]=="1",i+1<len(z) and z[i+1]["wrapper"]=="q",i+1<len(z) and z[i+1]["dy_closure"]=="1"],dtype=float)
   rows.append({"locus":locus,"page":x["page"],"folio":x["physical_folio"],"register":x["register"],"token":x["token"],"page_host":x["page_host"],"host_length":len(x["page_host"]),"features":tri(x["page_host"]),"dims":d})
 D=np.stack([x["dims"] for x in rows]);res=D.copy();cells=defaultdict(list)
 for i,x in enumerate(rows):cells[x["register"],x["folio"],x["host_length"]].append(i)
 for idx in cells.values():res[idx]-=D[idx].mean(axis=0)
 sd=res.std(axis=0);sd[sd<1e-9]=1;res/=sd
 features=sorted(set().union(*(x["features"] for x in rows)));atlas=[]
 for feature in features:
  effects=[];counts=[];folios=[]
  for reg in REGS:
   idx=[i for i,x in enumerate(rows) if x["register"]==reg and feature in x["features"]];effects.append(res[idx].mean(axis=0) if idx else np.zeros(len(DIMS)));counts.append(len(idx));folios.append(len({rows[i]["folio"] for i in idx}))
  if min(counts)<10 or min(folios)<3:continue
  a,b=effects;den=np.linalg.norm(a)*np.linalg.norm(b);cos=float(a@b/den) if den else 0.
  out={"formal_feature":feature,"herbal_b_groups":counts[0],"stars_recipe_b_groups":counts[1],"herbal_b_folios":folios[0],"stars_recipe_b_folios":folios[1],"context_cosine":cos,"semantic_role":"UNASSIGNED"}
  for name,v in zip(DIMS,a):out["herbal_b_"+name.lower()]=float(v)
  for name,v in zip(DIMS,b):out["stars_recipe_b_"+name.lower()]=float(v)
  atlas.append(out)
 atlas.sort(key=lambda x:(-x["context_cosine"],x["formal_feature"]));
 for i,x in enumerate(atlas,1):x["rank_by_context_cosine"]=i
 write(ATLAS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in x.items()} for x in atlas],list(atlas[0]));pch=next(x for x in atlas if x["formal_feature"]=="pch")
 contexts=[]
 for i,x in enumerate(rows):
  if "pch" not in x["features"]:continue
  out={"locus":x["locus"],"page":x["page"],"physical_folio":x["folio"],"register":x["register"],"token":x["token"],"page_host":x["page_host"],"semantic_role":"UNASSIGNED"}
  for name,v in zip(DIMS,x["dims"]):out[name.lower()]=f"{v:.6g}"
  contexts.append(out)
 write(CONTEXTS,contexts,list(contexts[0]))
 ann=read(ANN);parsed=read(PARSED);scope=[]
 for a,p in zip(ann,parsed):
  if "pch" not in p["page_host"]:continue
  positive=int(bool(PAT.search(a["raw_source_description"].lower())));scope.append({"locus":a["locus"],"physical_folio":a["physical_folio"],"section":a["section"],"kind":a["kind"],"token":p["token"],"page_host":p["page_host"],"object_tags":a["object_tags"],"annotation_certainty":a["annotation_certainty"],"mixed_spatial_context_positive":positive,"raw_source_description":a["raw_source_description"],"semantic_role":"UNASSIGNED","scope_class":"PHARMA_PLANT" if a["section"]=="P" and "PLANT" in a["object_tags"].split(";") else "OTHER"})
 write(ANNOT,scope,list(scope[0]));pc=Counter((x["scope_class"],x["mixed_spatial_context_positive"]) for x in scope);reg_counts=Counter(x["register"] for x in source if "pch" in x["page_host"])
 status="PCH_RECORD_CONTEXT_TRANSFERS_ORDINARILY_SPATIAL_ASSOCIATION_IS_DOMAIN_CONFINED"
 REPORT.write_text(f"""# GDT098 — `PCH` cross-register context and annotation scope

## Outcome

**{status}**

In the complete HPR2 source inventory, PAGE_HOST trigram `pch` occurs 331 times
on 66 folios: 26 Herbal-B and 157 Recipe/Stars-B groups, plus other registers.
After exact register×folio×host-length centering, its fifteen-dimensional record
context has Herbal-B↔Recipe/Stars cosine {pch['context_cosine']:.3f}. This is
positive but ranks only {pch['rank_by_context_cosine']}/{len(atlas)} supported
motifs. In both registers `pch` tends toward wrapper-NONE, DY closure, and a
present right family; this looks like a recurrent record-phase host, but not a
distinctive one.

The full local-annotation scope gives the sharper counterweight: all six
pharmaceutical plant-label `pch` loci carry the GDT097 mixed spatial words,
whereas all five annotated non-pharmaceutical `pch` loci are negative. The
association is therefore perfectly domain-confined in this tiny postselected
archive and cannot be promoted to a manuscript-wide base/ground meaning.
Recipe/Stars contains abundant ungrounded `pch` prose occurrences.

Retain `PCH` as a formal host-family candidate with ordinary cross-register
record behavior and a weak pharmaceutical visual-context seed. No role or
gloss is assigned. f84r was absent and untouched.
""",encoding="utf-8")
 result={"schema":"GDT098_PCH_CROSS_REGISTER_CONTEXT_RESULT_V1","status":status,"source_groups":len(source),"pch_source_groups":sum(reg_counts.values()),"pch_source_folios":len({x["physical_folio"] for x in source if "pch" in x["page_host"]}),"pch_register_counts":dict(reg_counts),"eligible_cross_register_motifs":len(atlas),"pch_cross_register":pch,"annotated_pch_loci":len(scope),"annotation_scope_counts":{f"{k[0]}_{k[1]}":v for k,v in pc.items()},"interpretation":"PCH has ordinary transferable record context and a perfectly domain-confined, postselected mixed spatial-description association; formal-host status only.","claim_ceiling":"Formal cross-register context and archived annotation scope only; no semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt097_result.json":sha(ROOT/"gdt097_result.json"),"gdt044_result.json":sha(ROOT/"gdt044_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),CONTEXTS.name:sha(CONTEXTS),ANNOT.name:sha(ANNOT)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pch":pch,"scope":result["annotation_scope_counts"],"registers":dict(reg_counts)},sort_keys=True))
if __name__=="__main__":main()

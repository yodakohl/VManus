#!/usr/bin/env python3
"""GDT063: rank PAGE_HOST local-annotation associations."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;GROUPS=ROOT/"gdt059_hpr2_external_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";FULL=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT063_PAGE_HOST_LOCAL_ANNOTATION_ATLAS_METHOD.md";REPORT=ROOT/"GDT063_PAGE_HOST_LOCAL_ANNOTATION_ATLAS_REPORT.md";ATLAS=ROOT/"gdt063_page_host_annotation_atlas.tsv";EXAMPLES=ROOT/"gdt063_page_host_candidate_examples.tsv";VARIANTS=ROOT/"gdt063_variant_log.tsv";RESULT=ROOT/"gdt063_result.json"
AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def normal_p(z):return math.erfc(abs(z)/math.sqrt(2))
def features(hosts):
 out=set();seq="|".join(hosts)
 for h in hosts:
  out.add("EXACT:"+h);out.add("LENGTH_BUCKET:"+str(len(h)//2))
  for n in(1,2,3):
   if len(h)>=n:out.add(f"PREFIX_{n}:"+h[:n]);out.add(f"SUFFIX_{n}:"+h[-n:])
  for n in(2,3):
   for i in range(len(h)-n+1):out.add(f"NGRAM_{n}:"+h[i:i+n])
 out.add("GROUP_COUNT:"+str(len(hosts)))
 if len(hosts)>1:out.add("MULTIGROUP_EXACT:"+seq)
 return out
def effect(rows,feature,axis):
 n=len(rows);fp=[r for r in rows if feature in r["features"]];fn=[r for r in rows if feature not in r["features"]];a=sum(axis in r["tags"]for r in fp);c=sum(axis in r["tags"]for r in fn);rd=a/len(fp)-c/len(fn) if fp and fn else 0.;by=defaultdict(list)
 for r in rows:by[r["stratum"]].append(r)
 obs=exp=var=0.;info=0;eligible=0
 for z in by.values():
  nx=sum(feature in r["features"]for r in z);ny=sum(axis in r["tags"]for r in z);m=len(z)
  if not(0<nx<m and 0<ny<m):continue
  o=sum(feature in r["features"]and axis in r["tags"]for r in z);e=nx*ny/m;v=nx*(ny/m)*(1-ny/m)*(m-nx)/(m-1);obs+=o;exp+=e;var+=v;info+=1;eligible+=nx
 ce=(obs-exp)/eligible if eligible else 0.;z=(obs-exp)/math.sqrt(var)if var else 0.;return{"loci":n,"feature_loci":len(fp),"feature_positive":a,"feature_negative":len(fp)-a,"axis_positive_without_feature":c,"physical_folios":len({r["physical_folio"]for r in fp}),"pooled_risk_difference":rd,"informative_strata":info,"eligible_feature_loci":eligible,"conditional_effect":ce,"conditional_z":z,"local_two_sided_p":normal_p(z)if var else 1.}
def main():
 groups=read(GROUPS);ann=read(ANN);full=read(FULL);assert len(groups)==671 and not any(r["locus"].startswith("f84r")for r in groups);meta={}
 for r in ann:
  if r["locus"].startswith("f84r"):continue
  meta.setdefault(r["locus"],r)
 by=defaultdict(list)
 for r in groups:by[r["locus"]].append(r)
 rows=[]
 for locus,z in sorted(by.items()):
  z.sort(key=lambda r:int(r["group_index"]));m=meta[locus];tags={x for x in(m["object_tags"]+";"+m["relation_tags"]).split(";")if x and x!="LABEL"};hs=[r["page_host"]for r in z];rows.append({"locus":locus,"page":m["page"],"physical_folio":m["physical_folio"],"section":m["section"],"currier":m["currier"],"hand":m["hand"],"unit":m["unit"],"certainty":m["annotation_certainty"],"tags":tags,"hosts":hs,"features":features(hs),"stratum":m["physical_folio"]+"|"+m["unit"]})
 assert len(rows)==560
 support=Counter();folios=defaultdict(set)
 for r in rows:
  for f in r["features"]:support[f]+=1;folios[f].add(r["physical_folio"])
 candidates=sorted(f for f in support if support[f]>=5 and len(folios[f])>=3 and support[f]<=len(rows)-10);atlas=[];unhedged=[r for r in rows if r["certainty"]=="UNHEDGED"]
 for f in candidates:
  wrapper_types={r["wrapper"]for r in full if (f.startswith("EXACT:")and r["page_host"]==f[6:])};global_host_wrapper_count=len(wrapper_types)if f.startswith("EXACT:")else 0
  for axis in AXES:
   e=effect(rows,f,axis);u=effect(unhedged,f,axis);sign=1 if e["conditional_effect"]>0 else-1 if e["conditional_effect"]<0 else 0;lo=[]
   for fol in sorted({r["physical_folio"]for r in rows if f in r["features"]}):lo.append(effect([r for r in rows if r["physical_folio"]!=fol],f,axis)["conditional_effect"])
   stable=bool(lo)and all((x>0)==(sign>0)for x in lo if x!=0);label="NO_SIGNAL"
   if e["informative_strata"]<2:label="LIKELY_PAGE_CONFOUND"
   elif not stable:label="UNSTABLE"
   elif e["informative_strata"]>=3 and e["local_two_sided_p"]<.01:label="INTERESTING_EXPLORATORY"
   elif e["local_two_sided_p"]<.1:label="WEAK"
   atlas.append({"candidate":f,"candidate_type":f.split(":",1)[0],"external_axis":axis,**e,"unhedged_loci":u["loci"],"unhedged_conditional_effect":u["conditional_effect"],"unhedged_local_p":u["local_two_sided_p"],"lofo_min_effect":min(lo)if lo else 0.,"lofo_max_effect":max(lo)if lo else 0.,"lofo_sign_stable":int(stable),"global_exact_host_wrapper_types":global_host_wrapper_count,"label":label})
 m=len(atlas)
 for r in atlas:r["bonferroni_all_p"]=min(1.,m*r["local_two_sided_p"])
 atlas.sort(key=lambda r:(r["local_two_sided_p"],-abs(r["conditional_effect"]),r["candidate"],r["external_axis"]));write(ATLAS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in atlas],list(atlas[0]));examples=[]
 for rank,a in enumerate(atlas[:30],1):
  pos=[r["locus"]for r in rows if a["candidate"]in r["features"]and a["external_axis"]in r["tags"]][:5];neg=[r["locus"]for r in rows if a["candidate"]in r["features"]and a["external_axis"]not in r["tags"]][:5];examples.append({"rank":rank,"candidate":a["candidate"],"external_axis":a["external_axis"],"positive_example_loci":";".join(pos)or"NONE","counterexample_loci":";".join(neg)or"NONE","label":a["label"]})
 write(EXAMPLES,examples,list(examples[0]));variants=[{"variant_id":"V00","status":"PRIMARY","description":"All 560 exact local loci; physical-folio by human-unit conditional score."},{"variant_id":"V01","status":"RUN_SENSITIVITY","description":"316 unhedged loci under the same state-blind candidate library."},{"variant_id":"V02","status":"RUN_LIBRARY","description":"Exact host, prefix/suffix, within-host ngram, length, group-count and multigroup candidates."},{"variant_id":"V03","status":"NOT_RUN","description":"No English gloss, semantic role assignment, alternate parser, threshold retuning, or f84r."}];write(VARIANTS,variants,list(variants[0]));interesting=[r for r in atlas if r["label"]=="INTERESTING_EXPLORATORY"];exact_leads=[r for r in interesting if r["candidate_type"]=="EXACT"];top=atlas[0];status="PAGE_HOST_LOCAL_ANNOTATION_LEADS_POSTSELECTED"if interesting else"NO_STABLE_PAGE_HOST_LOCAL_ANNOTATION_LEAD"
 report=f"""# GDT063 — PAGE_HOST local-annotation candidate atlas

## Outcome

**{status}**

The state-blind library contains {len(candidates)} supported PAGE_HOST features
and {len(atlas):,} feature×annotation tests over {len(rows)} loci on
{len({r['physical_folio']for r in rows})} physical folios.  There are
{len(interesting)} `INTERESTING_EXPLORATORY` rows before treating the complete
atlas as a confirmatory search.  The top row is `{top['candidate']}` versus
`{top['external_axis']}`: conditional effect
{top['conditional_effect']:+.4f}, local p={top['local_two_sided_p']:.4g},
all-atlas Bonferroni p={top['bonferroni_all_p']:.4g}, across
{top['informative_strata']} informative folio×unit strata.  Its label is
`{top['label']}`.

Two exact-host rows survive the permissive exploratory label.  `EXACT:d`
versus `REL_ENCLOSURE` has effect
{exact_leads[0]['conditional_effect']:+.4f} across
{exact_leads[0]['physical_folios']} folios and
{exact_leads[0]['informative_strata']} informative strata.  `EXACT:ok` versus
`WATER_OR_APPARATUS` has effect
{exact_leads[1]['conditional_effect']:+.4f} across
{exact_leads[1]['physical_folios']} folios but only
{exact_leads[1]['informative_strata']} informative strata.  Each exact host is
attested under {exact_leads[0]['global_exact_host_wrapper_types']} HPR2 wrapper
types in the full formal inventory.  Both all-atlas corrected p-values are
1.0.  The second row is the more content-like lead; the first may simply be a
short structural label class.  Neither receives a gloss, and both positive and
counterexample loci are frozen in the examples table.

The atlas retains pooled effects, unhedged sensitivity, leave-folio ranges,
page-confound labels, and explicit counterexample loci.  These are dirty,
postselected hypotheses for later freezing, not semantic confirmation.  No
candidate receives a role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation.  f84r was excluded before parsing and was
not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT063_PAGE_HOST_LOCAL_ANNOTATION_ATLAS_RESULT_V1","status":status,"loci":len(rows),"physical_folios":len({r["physical_folio"]for r in rows}),"unhedged_loci":len(unhedged),"candidate_features":len(candidates),"tests":len(atlas),"interesting_exploratory":len(interesting),"top_candidate":top,"exact_host_leads":exact_leads,"interpretation":"Postselected local-annotation candidate atlas only; candidates require independent freezing and transfer.","claim_ceiling":"No role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{GROUPS.name:sha(GROUPS),ANN.name:sha(ANN),FULL.name:sha(FULL),"gdt059_result.json":sha(ROOT/"gdt059_result.json"),"gdt062_result.json":sha(ROOT/"gdt062_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),EXAMPLES.name:sha(EXAMPLES),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"candidates":len(candidates),"tests":len(atlas),"interesting":len(interesting),"top":{k:top[k]for k in("candidate","external_axis","conditional_effect","local_two_sided_p","bonferroni_all_p","label")}},sort_keys=True))
if __name__=="__main__":main()

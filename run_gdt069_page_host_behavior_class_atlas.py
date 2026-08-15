#!/usr/bin/env python3
"""GDT069: explicit fold-safe PAGE_HOST behavior-class candidates."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT069_PAGE_HOST_BEHAVIOR_CLASS_ATLAS_METHOD.md";REPORT=ROOT/"GDT069_PAGE_HOST_BEHAVIOR_CLASS_ATLAS_REPORT.md";ATLAS=ROOT/"gdt069_behavior_class_atlas.tsv";EXAMPLES=ROOT/"gdt069_behavior_class_examples.tsv";VARIANTS=ROOT/"gdt069_variant_log.tsv";RESULT=ROOT/"gdt069_result.json"
AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP");THRESH=(.10,.25,.50,.75)
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def normal_p(z):return math.erfc(abs(z)/math.sqrt(2))
def effect(rows,feature,axis):
 fp=[r for r in rows if feature in r["features"]];fn=[r for r in rows if feature not in r["features"]];a=sum(axis in r["tags"]for r in fp);c=sum(axis in r["tags"]for r in fn);rd=a/len(fp)-c/len(fn)if fp and fn else 0.;by=defaultdict(list)
 for r in rows:by[r["stratum"]].append(r)
 obs=exp=var=0.;info=eligible=0
 for z in by.values():
  nx=sum(feature in r["features"]for r in z);ny=sum(axis in r["tags"]for r in z);m=len(z)
  if not(0<nx<m and 0<ny<m):continue
  o=sum(feature in r["features"]and axis in r["tags"]for r in z);e=nx*ny/m;v=nx*(ny/m)*(1-ny/m)*(m-nx)/(m-1);obs+=o;exp+=e;var+=v;info+=1;eligible+=nx
 ce=(obs-exp)/eligible if eligible else 0.;zz=(obs-exp)/math.sqrt(var)if var else 0.;return{"loci":len(rows),"feature_loci":len(fp),"feature_positive":a,"feature_negative":len(fp)-a,"axis_positive_without_feature":c,"physical_folios":len({r["physical_folio"]for r in fp}),"pooled_risk_difference":rd,"informative_strata":info,"eligible_feature_loci":eligible,"conditional_effect":ce,"conditional_z":zz,"local_two_sided_p":normal_p(zz)if var else 1.}
def main():
 src=read(SOURCE);ann=read(ANN);parsed=read(PARSED);assert len(src)==15592 and len(ann)==len(parsed)==671 and not any(r["locus"].startswith("f84r")for r in src+parsed)
 byline=defaultdict(list)
 for r in src:byline[r["locus"]].append(r)
 events=[];hf=defaultdict(set)
 for locus,z in byline.items():
  z.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(z):
   hf[r["page_host"]].add(r["physical_folio"]);prev=z[i-1]if i else None;nxt=z[i+1]if i+1<len(z)else None;tokens=["W="+r["wrapper"],"D="+r["inner_d"],"F="+r["local_frame"],"R="+r["right_family"],"DY="+r["dy_closure"],"B3="+r["b3"],"P="+r["position_quartile"],"PW="+(prev["wrapper"]if prev else"BOS"),"PF="+(prev["local_frame"]if prev else"BOS"),"PDY="+(prev["dy_closure"]if prev else"BOS"),"NW="+(nxt["wrapper"]if nxt else"EOS"),"NF="+(nxt["local_frame"]if nxt else"EOS"),"NDY="+(nxt["dy_closure"]if nxt else"EOS")];events.append((r["physical_folio"],r["page_host"],tokens))
 amap={(r["locus"],r["group_index"]):r for r in ann};byloc=defaultdict(list)
 for r in parsed:byloc[r["locus"]].append(r)
 base=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda r:int(r["group_index"]));a=amap[locus,z[0]["group_index"]]
  if all(len(hf[r["page_host"]])>=2 for r in z):
   base.append({"locus":locus,"physical_folio":z[0]["physical_folio"],"section":z[0]["section"],"currier":z[0]["currier"],"unit":a["unit"],"certainty":a["annotation_certainty"],"hosts":[r["page_host"]for r in z],"tags":{x for x in(a["object_tags"]+";"+a["relation_tags"]).split(";")if x and x!="LABEL"}})
 assert len(base)==332;fold_profiles={}
 for folio in sorted({r["physical_folio"]for r in base}):
  counts=defaultdict(Counter);n=Counter()
  for f,h,tokens in events:
   if f==folio:continue
   counts[h].update(tokens);n[h]+=1
  fold_profiles[folio]={h:{k:v/n[h]for k,v in q.items()}for h,q in counts.items()}
 rows=[]
 for r in base:
  rates=Counter()
  for host in r["hosts"]:rates.update(fold_profiles[r["physical_folio"]][host])
  rates={k:v/len(r["hosts"])for k,v in rates.items()};features={f"RATE:{k}>={t:.2f}"for k,v in rates.items()for t in THRESH if v>=t};rows.append({**r,"features":features,"rates":rates,"stratum":r["physical_folio"]+"|"+r["unit"]})
 support=Counter();folios=defaultdict(set)
 for r in rows:
  for f in r["features"]:support[f]+=1;folios[f].add(r["physical_folio"])
 eligible=sorted(f for f in support if 5<=support[f]<=len(rows)-10 and len(folios[f])>=3);mask_groups=defaultdict(list)
 for f in eligible:mask_groups[tuple(f in r["features"]for r in rows)].append(f)
 aliases={sorted(v)[0]:sorted(v)for v in mask_groups.values()};candidates=sorted(aliases);unhedged=[r for r in rows if r["certainty"]=="UNHEDGED"];atlas=[]
 for feature in candidates:
  for axis in AXES:
   e=effect(rows,feature,axis);u=effect(unhedged,feature,axis);sign=1 if e["conditional_effect"]>0 else-1 if e["conditional_effect"]<0 else 0;lo=[effect([r for r in rows if r["physical_folio"]!=fol],feature,axis)["conditional_effect"]for fol in sorted({r["physical_folio"]for r in rows if feature in r["features"]})];stable=bool(lo)and all((x>0)==(sign>0)for x in lo if x!=0);label="NO_SIGNAL"
   if e["informative_strata"]<2:label="LIKELY_PAGE_CONFOUND"
   elif not stable:label="UNSTABLE"
   elif e["informative_strata"]>=3 and e["local_two_sided_p"]<.01:label="INTERESTING_EXPLORATORY"
   elif e["local_two_sided_p"]<.1:label="WEAK"
   atlas.append({"candidate":feature,"candidate_aliases":";".join(aliases[feature]),"behavior_block":feature.split(":",1)[1].split("=",1)[0],"external_axis":axis,**e,"unhedged_loci":len(unhedged),"unhedged_conditional_effect":u["conditional_effect"],"unhedged_local_p":u["local_two_sided_p"],"lofo_min_effect":min(lo)if lo else 0.,"lofo_max_effect":max(lo)if lo else 0.,"lofo_sign_stable":int(stable),"label":label})
 m=len(atlas)
 for r in atlas:r["bonferroni_all_p"]=min(1.,m*r["local_two_sided_p"])
 atlas.sort(key=lambda r:(r["local_two_sided_p"],-abs(r["conditional_effect"]),r["candidate"],r["external_axis"]));write(ATLAS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in atlas],list(atlas[0]));examples=[]
 for rank,a in enumerate(atlas[:40],1):
  pos=[r for r in rows if a["candidate"]in r["features"]and a["external_axis"]in r["tags"]];neg=[r for r in rows if a["candidate"]in r["features"]and a["external_axis"]not in r["tags"]];examples.append({"rank":rank,"candidate":a["candidate"],"external_axis":a["external_axis"],"positive_example_loci":";".join(r["locus"]for r in pos[:6])or"NONE","counterexample_loci":";".join(r["locus"]for r in neg[:6])or"NONE","positive_hosts":";".join(sorted({h for r in pos for h in r["hosts"]}))[:500]or"NONE","counterexample_hosts":";".join(sorted({h for r in neg for h in r["hosts"]}))[:500]or"NONE","label":a["label"]})
 write(EXAMPLES,examples,list(examples[0]));interesting=[r for r in atlas if r["label"]=="INTERESTING_EXPLORATORY"];top=atlas[0];top_interesting=interesting[0]if interesting else None;byblock=Counter(r["behavior_block"]for r in interesting);status="BEHAVIOR_CLASS_EXTERNAL_ASSOCIATION_LEADS_POSTSELECTED"if interesting else"NO_STABLE_BEHAVIOR_CLASS_ASSOCIATION_LEAD"
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"Target-folio-excluded behavior rates with fixed thresholds .10/.25/.50/.75."},{"variant_id":"V01","status":"RUN_SENSITIVITY","description":"Unhedged archived annotation subset."},{"variant_id":"V02","status":"RUN_ROBUSTNESS","description":"Leave-one-positive-folio conditional-effect direction."},{"variant_id":"V03","status":"EXCLUDED_CAPACITY","description":"Host must occur on at least two prose folios; predicate support >=5 loci and >=3 folios."},{"variant_id":"V04","status":"NOT_RUN","description":"No supervised semantic class, gloss, alternate parser, retuned threshold, or f84r."}];write(VARIANTS,variants,list(variants[0]))
 report=f"""# GDT069 — PAGE_HOST behavior-class annotation atlas

## Outcome

**{status}**

The state-blind threshold library contains {len(candidates)} supported formal
behavior predicates and {len(atlas):,} predicate×axis tests over {len(rows)}
transferable loci.  {len(interesting)} rows receive the permissive
`INTERESTING_EXPLORATORY` label; every complete-atlas Bonferroni value remains
in the atlas.  The top row is `{top['candidate']}` versus
`{top['external_axis']}`: conditional effect {top['conditional_effect']:+.4f},
local p={top['local_two_sided_p']:.4g}, all-atlas adjusted p
{top['bonferroni_all_p']:.4g}, {top['informative_strata']} informative
folio×unit strata, label `{top['label']}`.  The strongest row passing the
permissive multi-stratum label is
`{top_interesting['candidate'] if top_interesting else 'NONE'}` versus
`{top_interesting['external_axis'] if top_interesting else 'NONE'}` with
effect {top_interesting['conditional_effect'] if top_interesting else 0:+.4f}
and local p={top_interesting['local_two_sided_p'] if top_interesting else 1:.4g}.
Interesting rows by source-native
block are {json.dumps(dict(byblock),sort_keys=True)}.

This decomposes the already postselected GDT068 lead and cannot confirm a
semantic class.  Positive and counterexample loci/hosts are both exported;
weak, unstable, and page-confounded rows are retained.  No role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
f84r was excluded and not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT069_PAGE_HOST_BEHAVIOR_CLASS_ATLAS_RESULT_V1","status":status,"groups":len(src),"eligible_loci":len(rows),"physical_folios":len({r["physical_folio"]for r in rows}),"eligible_raw_predicates":len(eligible),"candidate_predicates":len(candidates),"tests":len(atlas),"interesting_exploratory":len(interesting),"interesting_by_block":dict(byblock),"top_candidate":top,"top_interesting":top_interesting,"selection_disclosure":"Identical locus masks collapsed; remaining complete atlas is still postselected and all adjusted p-values include every unique-mask test.","interpretation":"Postselected decomposition of GDT068's fold-safe behavior-profile lead; archived axes remain hypothesis-generation outcomes.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt068_result.json":sha(ROOT/"gdt068_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),EXAMPLES.name:sha(EXAMPLES),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"candidates":len(candidates),"tests":len(atlas),"interesting":len(interesting),"top":{k:top[k]for k in("candidate","external_axis","conditional_effect","local_two_sided_p","bonferroni_all_p","label")}},sort_keys=True))
if __name__=="__main__":main()

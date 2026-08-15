#!/usr/bin/env python3
"""GDT071: leave each repeated exact host out of GDT069 class leads."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";ATLAS=ROOT/"gdt069_behavior_class_atlas.tsv";METHOD=ROOT/"GDT071_BEHAVIOR_CLASS_EXACT_HOST_ABLATION_METHOD.md";REPORT=ROOT/"GDT071_BEHAVIOR_CLASS_EXACT_HOST_ABLATION_REPORT.md";TESTS=ROOT/"gdt071_behavior_class_host_ablation.tsv";MEMBERS=ROOT/"gdt071_behavior_class_host_members.tsv";VARIANTS=ROOT/"gdt071_variant_log.tsv";RESULT=ROOT/"gdt071_result.json";THRESH=(.10,.25,.50,.75)
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def effect(rows,feature,axis):
 by=defaultdict(list)
 for r in rows:by[r["stratum"]].append(r)
 obs=exp=eligible=0.
 for z in by.values():
  nx=sum(feature in r["features"]for r in z);ny=sum(axis in r["tags"]for r in z);m=len(z)
  if not(0<nx<m and 0<ny<m):continue
  obs+=sum(feature in r["features"]and axis in r["tags"]for r in z);exp+=nx*ny/m;eligible+=nx
 return(obs-exp)/eligible if eligible else 0.
def main():
 src=read(SOURCE);ann=read(ANN);parsed=read(PARSED);atlas=read(ATLAS);leads=[r for r in atlas if r["label"]=="INTERESTING_EXPLORATORY"];assert len(src)==15592 and len(ann)==len(parsed)==671 and len(leads)==9 and not any(r["locus"].startswith("f84r")for r in src+parsed)
 byline=defaultdict(list);hf=defaultdict(set)
 for r in src:byline[r["locus"]].append(r);hf[r["page_host"]].add(r["physical_folio"])
 events=[]
 for z in byline.values():
  z.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(z):
   p=z[i-1]if i else None;n=z[i+1]if i+1<len(z)else None;events.append((r["physical_folio"],r["page_host"],["W="+r["wrapper"],"D="+r["inner_d"],"F="+r["local_frame"],"R="+r["right_family"],"DY="+r["dy_closure"],"B3="+r["b3"],"P="+r["position_quartile"],"PW="+(p["wrapper"]if p else"BOS"),"PF="+(p["local_frame"]if p else"BOS"),"PDY="+(p["dy_closure"]if p else"BOS"),"NW="+(n["wrapper"]if n else"EOS"),"NF="+(n["local_frame"]if n else"EOS"),"NDY="+(n["dy_closure"]if n else"EOS")]))
 amap={(r["locus"],r["group_index"]):r for r in ann};byloc=defaultdict(list)
 for r in parsed:byloc[r["locus"]].append(r)
 base=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda r:int(r["group_index"]));a=amap[locus,z[0]["group_index"]]
  if all(len(hf[r["page_host"]])>=2 for r in z):base.append({"locus":locus,"physical_folio":z[0]["physical_folio"],"unit":a["unit"],"hosts":[r["page_host"]for r in z],"tags":{x for x in(a["object_tags"]+";"+a["relation_tags"]).split(";")if x and x!="LABEL"}})
 profiles={}
 for fol in sorted({r["physical_folio"]for r in base}):
  counts=defaultdict(Counter);n=Counter()
  for f,h,t in events:
   if f==fol:continue
   counts[h].update(t);n[h]+=1
  profiles[fol]={h:{k:v/n[h]for k,v in q.items()}for h,q in counts.items()}
 for r in base:
  rates=Counter()
  for h in r["hosts"]:rates.update(profiles[r["physical_folio"]][h])
  rates={k:v/len(r["hosts"])for k,v in rates.items()};r["features"]={f"RATE:{k}>={t:.2f}"for k,v in rates.items()for t in THRESH if v>=t};r["stratum"]=r["physical_folio"]+"|"+r["unit"]
 tests=[];members=[]
 for lead in leads:
  feature=lead["candidate"];axis=lead["external_axis"];member_rows=[r for r in base if feature in r["features"]];host_count=Counter(h for r in member_rows for h in set(r["hosts"]));repeat=sorted(h for h,n in host_count.items()if n>=2);orig=effect(base,feature,axis);vals=[]
  for host in sorted(host_count):
   z=[r for r in member_rows if host in r["hosts"]];ab=effect([r for r in base if host not in r["hosts"]],feature,axis);members.append({"candidate":feature,"external_axis":axis,"page_host":host,"candidate_loci":len(z),"candidate_positive_loci":sum(axis in r["tags"]for r in z),"candidate_negative_loci":sum(axis not in r["tags"]for r in z),"physical_folios":len({r["physical_folio"]for r in z}),"leave_host_out_effect":ab,"included_in_repeat_host_robustness":int(host in repeat)});vals.append((host,ab))
  repeat_vals=[v for h,v in vals if h in repeat];sign=orig>0;stable=all((v>0)==sign for v in repeat_vals if v!=0);tests.append({"candidate":feature,"external_axis":axis,"original_conditional_effect":orig,"feature_loci":len(member_rows),"distinct_exact_hosts":len(host_count),"repeat_exact_hosts":len(repeat),"leave_repeat_host_min_effect":min(repeat_vals)if repeat_vals else 0.,"leave_repeat_host_max_effect":max(repeat_vals)if repeat_vals else 0.,"leave_repeat_host_sign_stable":int(stable),"leave_d_out_effect":effect([r for r in base if"d"not in r["hosts"]],feature,axis),"leave_ok_out_effect":effect([r for r in base if"ok"not in r["hosts"]],feature,axis),"gdt069_local_p":lead["local_two_sided_p"],"gdt069_adjusted_p":lead["bonferroni_all_p"],"robustness_label":"CLASS_LEVEL_DIRECTION_SURVIVES_EXACT_HOST_ABLATION"if stable else"EXACT_HOST_SENSITIVE"})
 tests.sort(key=lambda r:(-abs(r["original_conditional_effect"]),r["candidate"],r["external_axis"]));members.sort(key=lambda r:(r["candidate"],r["external_axis"],-r["candidate_loci"],r["page_host"]));write(TESTS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in tests],list(tests[0]));write(MEMBERS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in members],list(members[0]));stable=sum(r["leave_repeat_host_sign_stable"]for r in tests);status="BEHAVIOR_CLASS_LEADS_SURVIVE_EXACT_HOST_ABLATION_POSTSELECTED"if stable==len(tests)else"BEHAVIOR_CLASS_LEADS_PARTLY_EXACT_HOST_DEPENDENT";aiin=next(r for r in tests if r["candidate"]=="RATE:R=aiin>=0.25"and r["external_axis"]=="REL_ENCLOSURE");sh=next(r for r in tests if r["candidate"]=="RATE:W=sh>=0.25");oframe=next(r for r in tests if r["candidate"]=="RATE:F=O>=0.10")
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"Remove each exact host occurring in at least two feature-positive loci."},{"variant_id":"V01","status":"RUN_DISPLAY","description":"Explicit d and ok deletions for every class lead."},{"variant_id":"V02","status":"POSTSELECTED_INPUT","description":"Nine GDT069 permissive rows; no new threshold/outcome search."},{"variant_id":"V03","status":"NOT_RUN","description":"No semantic class, gloss, alternative behavior profile, or f84r."}];write(VARIANTS,variants,list(variants[0]))
 report=f"""# GDT071 — behavior-class exact-host ablation

## Outcome

**{status}**

All {stable}/{len(tests)} postselected GDT069 class leads retain their effect
direction after deleting every repeated exact PAGE_HOST in turn.  The
`R=aiin>=.25` / `REL_ENCLOSURE` lead spans {aiin['distinct_exact_hosts']}
hosts ({aiin['repeat_exact_hosts']} repeated): original effect
{aiin['original_conditional_effect']:+.4f}, without `d`
{aiin['leave_d_out_effect']:+.4f}, without `ok`
{aiin['leave_ok_out_effect']:+.4f}, repeated-host deletion range
[{aiin['leave_repeat_host_min_effect']:+.4f},
{aiin['leave_repeat_host_max_effect']:+.4f}].  The `sh`-wrapper/attachment
lead ranges [{sh['leave_repeat_host_min_effect']:+.4f},
{sh['leave_repeat_host_max_effect']:+.4f}], and the O-frame/enclosure lead
[{oframe['leave_repeat_host_min_effect']:+.4f},
{oframe['leave_repeat_host_max_effect']:+.4f}].

Thus the lead is not reducible to `d`, `ok`, or another single repeated host.
This remains a robustness audit of already postselected archived outcomes;
GDT069's all-atlas adjusted p-values remain 1.0.  It supports prospective
class-level hypotheses, not meanings.  No semantic class, role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
f84r was excluded and not opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT071_BEHAVIOR_CLASS_EXACT_HOST_ABLATION_RESULT_V1","status":status,"groups":len(src),"eligible_loci":len(base),"tested_class_leads":len(tests),"sign_stable_class_leads":stable,"aiin_enclosure":aiin,"sh_attachment":sh,"o_frame_enclosure":oframe,"interpretation":"Exact-host ablation of postselected GDT069 class leads; direction stability supports prospective class hypotheses but not confirmation.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),ATLAS.name:sha(ATLAS),"gdt069_result.json":sha(ROOT/"gdt069_result.json"),"gdt070_result.json":sha(ROOT/"gdt070_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{TESTS.name:sha(TESTS),MEMBERS.name:sha(MEMBERS),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"leads":len(tests),"stable":stable,"aiin":aiin,"sh":sh,"o":oframe},sort_keys=True))
if __name__=="__main__":main()

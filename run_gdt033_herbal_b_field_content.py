#!/usr/bin/env python3
"""Explore reusable content hosts inside Herbal-B additional fields."""
from __future__ import annotations
import csv,hashlib,json,random,re
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;N_PERM=10000;SEED=330033

def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (ROOT/name).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def guarded(path,pages):
 out={}
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();idx=header.rstrip("\n").split("\t").index("page")
  for line in h:
   if line.split("\t")[idx]not in pages:continue
   row=next(csv.DictReader([header,line],delimiter="\t"));out[row["page"]]=row
 return out
def guarded_rows(path,pages):
 out=[]
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();idx=header.rstrip("\n").split("\t").index("page")
  for line in h:
   if line.split("\t")[idx]not in pages:continue
   out.append(next(csv.DictReader([header,line],delimiter="\t")))
 return out
def feature_rules():
 return {
 "DAISY_CUP":("VISIBLE_PLANT_FEATURE","illustrations","EXACT: beta daisy-in-a-cup tag",lambda a:"β: 'daisy in a cup'"in a["illustrations"]),
 "BROAD_CALYX":("VISIBLE_PLANT_FEATURE","illustrations","EXACT: beta broad-many-fingered-calyx tag",lambda a:"β: broad many-fingered calyx"in a["illustrations"]),
 "FLOWER_HEAD_ARCHITECTURE":("POSTHOC_COMPOSITE_VISIBLE_FEATURE","illustrations","UNION: DAISY_CUP or BROAD_CALYX",lambda a:"β: 'daisy in a cup'"in a["illustrations"]or"β: broad many-fingered calyx"in a["illustrations"]),
 "GRASS":("VISIBLE_PLANT_FEATURE","illustrations","EXACT: beta grass tag",lambda a:"β: 'grass'"in a["illustrations"]),
 "ROOT_PLATFORM":("VISIBLE_PLANT_FEATURE","illustrations","EXACT: beta root-platform tag",lambda a:"β: root platform"in a["illustrations"]),
 "LEAVES_ONE_SIDE":("VISIBLE_PLANT_FEATURE","illustrations","EXACT: beta all-leaves-one-side tag",lambda a:"β: all leaves point to one side"in a["illustrations"]),
 "FUSED_PARALLEL_LEAVES":("VISIBLE_PLANT_FEATURE","illustrations","EXACT: beta leaves-parallel-and-fused tag",lambda a:"β: leaves parallel and fused together on one stalk"in a["illustrations"]),
 "BULB_OR_TUBER_ROOT":("VISIBLE_PLANT_FEATURE","illustrations","REGEX: bulb or tuber",lambda a:bool(re.search(r"\bbulb|\btuber",a["illustrations"],re.I))),
 "LARGE_OR_EXTENSIVE_ROOT":("VISIBLE_PLANT_FEATURE","illustrations","REGEX: large/extensive/huge root",lambda a:bool(re.search(r"large root|large roots|extensive roots|huge[^.]{0,40}root",a["illustrations"],re.I))),
 "MULTIPLE_PLANTS":("VISIBLE_PLANT_FEATURE","illustrations","REGEX: explicitly multiple plants",lambda a:bool(re.search(r"two plants|two different plants|two of the same plants|row of plants|many plants",a["illustrations"],re.I))),
 "BLUE_FLOWERS_OR_BUDS":("VISIBLE_PLANT_FEATURE","illustrations","RULE: blue and flower/bud",lambda a:"blue"in a["illustrations"].lower()and bool(re.search(r"flower|bud",a["illustrations"],re.I))),
 "FINGERED_OR_FRILLED_LEAVES":("VISIBLE_PLANT_FEATURE","illustrations","STRICT REGEX: fingered/frilled leaves",lambda a:bool(re.search(r"fingered leaves|frilled fingered leaves|leaves (?:ending in|with)[^.]{0,20}(?:finger|figer)|leaves are similar, with many fingers",a["illustrations"],re.I))),
 "MULTIPLE_STEMS_OR_STALKS":("VISIBLE_PLANT_FEATURE","illustrations","REGEX: numbered/several stems or stalks",lambda a:bool(re.search(r"(two|three|four|several) (stems|stalks)",a["illustrations"],re.I))),
 "TEXT_SPLIT_OR_INTERRUPTED":("PAGE_LAYOUT_RELATION","text_description","REGEX: split/interrupted/broken by plant",lambda a:bool(re.search(r"split by the plant|interrupted by the top of the plant|broken up by the plant",a["text_description"],re.I))),
 "TEXT_AVOIDS_DRAWING":("PAGE_LAYOUT_RELATION","text_description","LITERAL: avoid",lambda a:"avoid"in a["text_description"].lower()),
 "TEXT_ABOVE_PLANT":("PAGE_LAYOUT_RELATION","text_description","REGEX: above plant/drawing",lambda a:bool(re.search(r"above the plant|above the drawing|above the dawing",a["text_description"],re.I)))}
def diffmean(rate,feat,pages):
 a=[rate[p]for p in pages if feat[p]];b=[rate[p]for p in pages if not feat[p]]
 return sum(a)/len(a)-sum(b)/len(b)if a and b else None
def scan(hosts,features,rates,feat,pages,arch):
 keys=[(h,f)for h in hosts for f in features];obs={k:diffmean(rates[k[0]],{p:feat[p][k[1]]for p in pages},pages)for k in keys};strata=defaultdict(list)
 for p in pages:strata[(arch[p]["hand"],arch[p]["illustration_profile"])].append(p)
 for ps in strata.values():ps.sort()
 rng=random.Random(SEED+len(pages));null={k:[]for k in keys}
 for _ in range(N_PERM):
  pf={}
  for sk in sorted(strata):
   ps=strata[sk];permuted=ps[:];rng.shuffle(permuted)
   for p,q in zip(ps,permuted):pf[p]=feat[q]
  for h,f in keys:null[h,f].append(diffmean(rates[h],{p:pf[p][f]for p in pages},pages))
 stats={}
 for key in keys:
  values=null[key];mu=sum(values)/N_PERM;sd=(sum((x-mu)**2 for x in values)/N_PERM)**.5;z=(obs[key]-mu)/sd if sd else 0.;local=(1+sum(abs(x-mu)>=abs(obs[key]-mu)-1e-15 for x in values))/(N_PERM+1);stats[key]={"effect":obs[key],"null_mean":mu,"z":z,"local_p":local,"sd":sd}
 maxz=[max(abs((null[key][i]-stats[key]["null_mean"])/stats[key]["sd"])if stats[key]["sd"]else 0 for key in keys)for i in range(N_PERM)]
 folios=sorted({arch[p]["physical_folio"]for p in pages})
 for key in keys:
  s=stats[key];s["maxT_p"]=(1+sum(x>=abs(s["z"])-1e-15 for x in maxz))/(N_PERM+1);loo=[]
  for folio in folios:
   subset=[p for p in pages if arch[p]["physical_folio"]!=folio];value=diffmean(rates[key[0]],{p:feat[p][key[1]]for p in pages},subset)
   if value is not None:loo.append(value)
  s["lofo_min"]=min(loo);s["lofo_max"]=max(loo)
 return stats

def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);B=[r for r in inv if r["section"]=="H"and r["currier"]=="B"];pages=sorted({r["page"]for r in B});assert len(pages)==32
 arch={r["page"]:r for r in read("gdt031_herbal_page_architecture.tsv")if r["currier"]=="B"};assert set(arch)==set(pages)
 annotation_pages=set(pages)|{"f52r"}
 ann=guarded(ROOT/"experiments/semantic_assumptions/results/existing_human_page_annotations.tsv",annotation_pages);assert set(ann)==annotation_pages and"f84r"not in ann
 exact_human=guarded_rows(ROOT/"experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv",set(pages));assert len(exact_human)==4 and not any("LABEL"in r["object_tags"].split(";")for r in exact_human)
 lines=defaultdict(list)
 for r in B:lines[r["locus"]].append(r)
 fields=[]
 for locus,rows in lines.items():
  rows.sort(key=lambda r:int(r["group_index"]));start=ordinal=0
  for i,r in enumerate(rows):
   if r["record_state"]!="DY_RESOLUTION":continue
   segment=rows[start:i+1]
   if ordinal>=1:fields.append((locus,ordinal,segment))
   start=i+1;ordinal+=1
 assert len(fields)==160;field_rows=[];cluster=defaultdict(lambda:{"occ":0,"fields":set(),"closing":0,"pages":set(),"folios":set(),"tokens":set(),"prefixes":set(),"states":set(),"templates":set()});page_total=Counter();page_host_fields=Counter()
 for field_id,(locus,ordinal,segment)in enumerate(fields,1):
  p=segment[-1]["page"];page_total[p]+=1;seen=set()
  template=">".join(r["record_state"]for r in segment)
  for i,r in enumerate(segment):
   h=r["residual_host"];x=cluster[h];x["occ"]+=1;x["fields"].add(field_id);x["closing"]+=int(i==len(segment)-1);x["pages"].add(p);x["folios"].add(r["physical_folio"]);x["tokens"].add(r["token"]);x["prefixes"].add(r["stripped_prefix"]);x["states"].add(r["record_state"]);x["templates"].add(template);seen.add(h)
  for h in seen:page_host_fields[p,h]+=1
  field_rows.append({"field_id":f"HBF{field_id:03d}","page":p,"physical_folio":segment[-1]["physical_folio"],"locus":locus,"additional_field_index":ordinal,"groups":len(segment),"tokens":"|".join(r["token"]for r in segment),"residual_hosts":"|".join(r["residual_host"]for r in segment),"record_states":"|".join(r["record_state"]for r in segment),"closer_host":segment[-1]["residual_host"],"singleton":int(len(segment)==1),"claim_state":"FORMAL_ADDITIONAL_FIELD_NOT_SEMANTICS"})
 write("gdt033_herbal_b_additional_fields.tsv",field_rows)
 label_rows=read("gdt012_annotated_core_inventory.tsv");assert not any(r["page"].startswith("f84r")for r in label_rows);label_by=defaultdict(list)
 for r in label_rows:
  if r["kind"]=="L":label_by[r["residual_host"]].append(r)
 clusters=[];eligible=[]
 for host,x in cluster.items():
  labels=label_by[host];is_eligible=len(x["fields"])>=5 and len(x["pages"])>=4 and(len(x["tokens"])>=2 or len(x["prefixes"])>=2)
  if is_eligible:eligible.append(host)
  clusters.append({"residual_host":host,"additional_field_occurrences":len(x["fields"]),"raw_group_occurrences":x["occ"],"closing_occurrences":x["closing"],"closing_fraction":f"{x['closing']/x['occ']:.12f}","pages":len(x["pages"]),"physical_folios":len(x["folios"]),"token_variants":len(x["tokens"]),"tokens":"|".join(sorted(x["tokens"])),"prefix_variants":len(x["prefixes"]),"prefixes":"|".join(sorted(x["prefixes"])),"record_states":"|".join(sorted(x["states"])),"field_template_count":len(x["templates"]),"exact_label_rows":len(labels),"unhedged_label_rows":sum(r["annotation_certainty"]=="UNHEDGED"for r in labels),"label_object_tags":"|".join(sorted({t for r in labels for t in r["object_tags"].split(";")if t})),"eligible_candidate":int(is_eligible),"claim_state":"HOST_CLUSTER_NOT_WORD_OR_MEANING"})
 clusters.sort(key=lambda r:(-r["eligible_candidate"],-r["additional_field_occurrences"],r["residual_host"]));write("gdt033_field_host_clusters.tsv",clusters);eligible=sorted(eligible);assert len(eligible)==16
 rules=feature_rules();feat={p:{name:int(rule[3](ann[p]))for name,rule in rules.items()}for p in pages};manifest=[]
 for p in pages:
  for name,(kind,source_field,rule,fn)in rules.items():
   if not feat[p][name]:continue
   manifest.append({"page":p,"physical_folio":arch[p]["physical_folio"],"feature":name,"feature_class":kind,"source_field":source_field,"matched_rule":rule,"source_field_sha256":hashlib.sha256(ann[p][source_field].encode()).hexdigest(),"source_url":ann[p]["source_url"],"raw_human_description":ann[p][source_field],"provenance":"EXISTING_HUMAN_ANNOTATION","claim_state":"VISIBLE_OR_LAYOUT_FEATURE_NOT_INTERPRETATION"})
 write("gdt033_visual_feature_manifest.tsv",manifest);features=sorted(rules);add_pages=sorted(page_total);add_rates={h:{p:page_host_fields[p,h]/page_total[p]for p in add_pages}for h in eligible};full_total=Counter(r["page"]for r in B);full_count=Counter((r["page"],r["residual_host"])for r in B);full_rates={h:{p:full_count[p,h]/full_total[p]for p in pages}for h in eligible}
 add_stats=scan(eligible,features,add_rates,feat,add_pages,arch);full_stats=scan(eligible,features,full_rates,feat,pages,arch);cluster_by={r["residual_host"]:r for r in clusters};assoc=[]
 for host in eligible:
  for feature in features:
   a=add_stats[host,feature];f=full_stats[host,feature];host_pages={p for p in pages if full_count[p,host]};feature_pages={p for p in pages if feat[p][feature]};hits=host_pages&feature_pages;counter=host_pages-feature_pages;precision=len(hits)/len(host_pages);hit_folios=len({arch[p]["physical_folio"]for p in hits});local_label="WEAK_POSTSELECTED"if f["local_p"]<=.05 else"WEAK"if abs(f["z"])>=1 else"NO_SIGNAL"
   assoc.append({"host":host,"visual_feature":feature,"feature_class":rules[feature][0],"additional_feature_pages":sum(feat[p][feature]for p in add_pages),"additional_effect":f"{a['effect']:.12f}","additional_z":f"{a['z']:.12f}","additional_local_p":f"{a['local_p']:.12f}","additional_maxT_p":f"{a['maxT_p']:.12f}","additional_lofo_min":f"{a['lofo_min']:.12f}","additional_lofo_max":f"{a['lofo_max']:.12f}","full_b_feature_pages":len(feature_pages),"full_b_host_pages":len(host_pages),"full_b_hit_pages":len(hits),"full_b_counterexample_pages":len(counter),"full_b_feature_precision":f"{precision:.12f}","full_b_hit_folios":hit_folios,"full_b_effect":f"{f['effect']:.12f}","full_b_z":f"{f['z']:.12f}","full_b_local_p":f"{f['local_p']:.12f}","full_b_maxT_p":f"{f['maxT_p']:.12f}","full_b_lofo_min":f"{f['lofo_min']:.12f}","full_b_lofo_max":f"{f['lofo_max']:.12f}","token_variants":cluster_by[host]["token_variants"],"prefix_variants":cluster_by[host]["prefix_variants"],"closing_fraction":cluster_by[host]["closing_fraction"],"label_rows":cluster_by[host]["exact_label_rows"],"label":local_label,"claim_state":"POSTSELECTED_HOST_VISUAL_ASSOCIATION_NOT_CONFIRMED_MEANING"})
 assoc.sort(key=lambda r:(-abs(float(r["full_b_z"])),r["host"],r["visual_feature"]));write("gdt033_core_visual_associations.tsv",assoc)
 lead=next(r for r in assoc if r["host"]=="ckhy"and r["visual_feature"]=="FUSED_PARALLEL_LEAVES");assert float(lead["closing_fraction"])==0 and int(lead["prefix_variants"])>=4 and int(lead["full_b_hit_folios"])>=4 and float(lead["full_b_lofo_min"])>0
 lead_host_pages={p for p in pages if full_count[p,"ckhy"]};lead_feature_pages={p for p in pages if feat[p]["FUSED_PARALLEL_LEAVES"]};counter=[]
 for p in sorted(lead_host_pages|lead_feature_pages):
  state="HOST_AND_FEATURE"if p in lead_host_pages&lead_feature_pages else"HOST_WITHOUT_FEATURE"if p in lead_host_pages else"FEATURE_WITHOUT_HOST";tokens=sorted({r["token"]for r in B if r["page"]==p and r["residual_host"]=="ckhy"})
  counter.append({"evidence_type":state,"page":p,"physical_folio":arch[p]["physical_folio"],"tokens":"|".join(tokens),"human_feature":int(p in lead_feature_pages),"source_url":ann[p]["source_url"],"note":"Existing human beta tag; page-level association only.","claim_state":"SUPPORT_OR_COUNTEREXAMPLE_NOT_TRANSLATION"})
 assert rules["FUSED_PARALLEL_LEAVES"][3](ann["f52r"]);a52=[r for r in inv if r["page"]=="f52r"];assert a52 and not any(r["residual_host"]=="ckhy"for r in a52)
 counter.append({"evidence_type":"CROSS_CURRIER_A_CAPACITY_COUNTEREXAMPLE","page":"f52r","physical_folio":"f52","tokens":"","human_feature":1,"source_url":ann["f52r"]["source_url"],"note":"Only Currier-A Herbal page with the same human tag; CKHY absent. One page is insufficient transfer capacity.","claim_state":"SUPPORT_OR_COUNTEREXAMPLE_NOT_TRANSLATION"});counter.append({"evidence_type":"HERBAL_B_EXACT_LABEL_CAPACITY","page":"NONE","physical_folio":"NONE","tokens":"","human_feature":0,"source_url":"","note":"Four exact-local Herbal-B plant rows exist, but none is a label or authorially owned inscription; CKHY has zero exact label rows in the non-f84 atlas.","claim_state":"SUPPORT_OR_COUNTEREXAMPLE_NOT_TRANSLATION"});write("gdt033_core_counterexamples.tsv",counter)
 status="CKHY_FUSED_LEAF_CONFIGURATION_CORE_PROVISIONAL_POSTSELECTED";singleton=sum(int(r["singleton"])for r in field_rows)
 report=f"""# GDT033 Herbal-B additional-field content

Status: **{status.replace('_',' ')}**

Herbal B supplies 160 additional DY-closed fields on 26 pages. {singleton}/160 ({100*singleton/160:.1f}%) are singleton closure fields, so most of the excess is still compact formal closure material. The largest closer clusters are OKE (21 fields/15 pages), O (11/8), OTE (10/7), and E (9 closers/7 pages). This is not a hidden list of 160 plant nouns.

| additional-field host | fields | closing uses | pages | reading |
| --- | ---: | ---: | ---: | --- |
| OKE | 21 | 21 | 15 | recurrent closure template |
| DY | 15 | 0 | 12 | renderer-stripped host inside fields, not another closer |
| O | 11 | 11 | 8 | recurrent closure template |
| OTE | 10 | 10 | 7 | recurrent closure template |
| E | 10 | 9 | 8 | near-closure template |
| AIIN | 8 | 0 | 7 | reusable content host |
| OL | 7 | 1 | 7 | mostly content host |
| AR | 6 | 0 | 6 | reusable content host |
| OKAR | 6 | 0 | 6 | reusable content host |
| CKHY | 5 | 0 | 5 | reusable content host and selected visual lead |

The first plausible content-stem lead is **CKHY**, provisionally a descriptor of the human-tagged `leaves parallel and fused together on one stalk` configuration. It is not a DY closer in the additional-field sample. It occurs as `ckhy`, `chckhy`, `checkhy`, and `shckhy`; the full Herbal-B census has 23 occurrences on 13 pages. Eight host pages on seven physical folios carry the feature and five do not; four feature pages lack the host. The full-census rate effect is {float(lead['full_b_effect']):+.5f}, hand/profile-restricted local p={float(lead['full_b_local_p']):.5f}, and remains positive under every folio deletion ({float(lead['full_b_lofo_min']):+.5f} to {float(lead['full_b_lofo_max']):+.5f}). The complete postselected-library maxT p={float(lead['full_b_maxT_p']):.5f}, so this is a hypothesis lead, not confirmation.

Two more surprising but more closure-like leads are OKCH with blue flowers/buds and OKAL with root-platform layout. They receive small local p-values in parts of the scan but no search-adjusted support. OKCH is predominantly a DY closer; OKAL mixes AL-state and closer uses and has many non-platform pages. Neither is promoted over CKHY.

| ranked host/feature lead | hit/host pages | local p | maxT p | verdict |
| --- | ---: | ---: | ---: | --- |
| CKHY / fused-parallel leaf-stalk tag | 8/13 | 0.0110 | 0.9069 | PROVISIONAL, best non-closure core |
| OKCH / blue flower-or-bud | 4/6 | 0.0988 full; 0.0148 additional | 1.0000 full | WEAK closure ecology |
| OKAL / root platform | 4/14 | 0.0116 | 0.9992 | WEAK, many counterexamples |
| O / multiple plants | 5/19 | 0.0020 | 0.2571 | LIKELY_GENERIC_CLOSURE/PAGE_CONFOUND |

Counterevidence is material. CKHY appears on f33v, f46v, f50r, f50v, and f94v without the fused/parallel tag; the sole Currier-A page carrying that tag, f52r, lacks CKHY. There is no exact owned Herbal-B plant-label anchor, and CKHY has no exact label occurrence elsewhere in the current non-f84 annotation atlas. The visual feature is itself heavily enriched in Currier B, so a register/style explanation remains strong.

Conclusion: **CKHY is the first concrete provisional semantic-core candidate worth targeted prediction**, with risky gloss `parallel/fused leaf-or-stalk configuration descriptor`. Its renderer variants preserve the same page-level tendency often enough to be useful, but not categorically. Freeze the next prediction on untouched Herbal-B pages or a genuinely comparable visual feature before inspecting their CKHY status. No word, morpheme, POS, sound, language, plaintext, or translation is established. f84r was not opened, retained, joined, or scored.
""";(ROOT/"GDT033_HERBAL_B_FIELD_CONTENT_REPORT.md").write_text(report)
 outputs=("gdt033_herbal_b_additional_fields.tsv","gdt033_field_host_clusters.tsv","gdt033_visual_feature_manifest.tsv","gdt033_core_visual_associations.tsv","gdt033_core_counterexamples.tsv","GDT033_HERBAL_B_FIELD_CONTENT_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt031_herbal_page_architecture.tsv","gdt032_result.json","gdt012_annotated_core_inventory.tsv","GDT033_HERBAL_B_FIELD_CONTENT_METHOD.md")
 result={"schema":"GDT033_HERBAL_B_FIELD_CONTENT_RESULT_V1","status":status,"additional_fields":160,"additional_pages":26,"singleton_fields":singleton,"eligible_hosts":len(eligible),"visual_features":len(features),"association_tests":len(assoc),"permutations":N_PERM,"selected_core":{"host":"ckhy","surface_constructions":["ckhy","chckhy","checkhy","shckhy"],"provisional_role":"PARALLEL_OR_FUSED_LEAF_OR_STALK_CONFIGURATION_DESCRIPTOR","full_b_occurrences":sum(full_count[p,"ckhy"]for p in pages),"full_b_pages":sum(full_count[p,"ckhy"]>0 for p in pages),"feature_hit_pages":int(lead["full_b_hit_pages"]),"feature_hit_folios":int(lead["full_b_hit_folios"]),"counterexample_pages":int(lead["full_b_counterexample_pages"]),"full_b_effect":lead["full_b_effect"],"full_b_local_p":lead["full_b_local_p"],"full_b_maxT_p":lead["full_b_maxT_p"],"full_b_lofo_min":lead["full_b_lofo_min"],"full_b_lofo_max":lead["full_b_lofo_max"],"claim_state":"PROVISIONAL_POSTSELECTED_SEMANTIC_CORE_NOT_CONFIRMED_MEANING"},"capacity":{"exact_local_herbal_b_plant_rows":len(exact_human),"exact_owned_herbal_b_plant_labels":0,"currier_a_fused_parallel_feature_pages":1,"currier_a_feature_pages_with_ckhy":0},"interpretation":"CKHY is a concrete postselected configuration-descriptor hypothesis; field closure, register, hand, page style, and multiple-search alternatives remain viable.","f84r":{"formal_input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Postselected page-level semantic-core hypothesis only; no word, morpheme, POS, sound, language, plaintext, translation, authorship, or origin follows.","guarded_human_subsets":{"page_annotations":{"rows":len(ann),"canonical_sha256":csha([ann[p]for p in sorted(ann)])},"exact_locus_annotations":{"rows":len(exact_human),"canonical_sha256":csha(exact_human)}},"inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt033_herbal_b_field_content.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt033_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"additional_fields":160,"eligible_hosts":len(eligible),"lead":result["selected_core"]},sort_keys=True))
if __name__=="__main__":main()

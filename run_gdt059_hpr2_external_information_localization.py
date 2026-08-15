#!/usr/bin/env python3
"""GDT059: exploratory external-information localization across HPR2 layers."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PAGES=ROOT/"experiments/semantic_assumptions/results/existing_human_page_role_matrix.tsv";METHOD=ROOT/"GDT059_HPR2_EXTERNAL_INFORMATION_LOCALIZATION_METHOD.md";REPORT=ROOT/"GDT059_HPR2_EXTERNAL_INFORMATION_LOCALIZATION_REPORT.md";INVENTORY=ROOT/"gdt059_hpr2_external_inventory.tsv";SCORES=ROOT/"gdt059_representation_scores.tsv";SUMMARY=ROOT/"gdt059_representation_summary.tsv";INVAR=ROOT/"gdt059_renderer_preservation.tsv";VARIANTS=ROOT/"gdt059_variant_log.tsv";RESULT=ROOT/"gdt059_result.json"
RIGHT=("aiin","air","ain","ar","al");K=5;SHRINK=4.;REPS=("RAW_EXACT_BAG","RAW_CHAR3","ROOT_EXACT_BAG","ROOT_CHAR3","PAGE_HOST_EXACT_BAG","PAGE_HOST_CHAR3","PAGE_HOST_PLUS_COMPILER_BAG","COMPILER_ONLY_BAG","RIGHT_FAMILY_ONLY","B3_ONLY")
LOCAL_AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP","REL_OVERLAP_OR_CONTACT")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def state(r):
 h=r["residual_host"]
 if int(r["dy_closure"]):return"DY_RESOLUTION"
 for p,z in(("otar","OT_AR_LOCAL"),("oar","O_AR_LOCAL"),("otal","OT_AL_LOCAL"),("oal","O_AL_LOCAL"),("otol","OT_OL_LOCAL"),("ool","O_OL_LOCAL")):
  if h.startswith(p):return z
 if"ar"in h:return"AR_REFERENCE"
 if"al"in h:return"AL_STATE"
 if"ol"in h:return"OL_STATE"
 if"ed"in h:return"ED_MEDIUM"
 if"kal"in h:return"KAL_INDEX"
 p=r["stripped_prefix"]
 if p in("d","s","t"):return"ENTRY_STATE"
 if p=="q":return"Q_OUTER_STATE"
 if p in("ch","sh","che"):return"CARRIER_STATE"
 return"OTHER"
def preparse(r):
 h=r["residual_host"];b3=int(h.endswith("m")and len(h)>1);h=h[:-1]if b3 else h;right="NONE"
 for s in RIGHT:
  if h.endswith(s)and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(r["stripped_prefix"]in{"ch","che","sh"}and h.startswith("d")and len(h)>1);h=h[1:]if inner else h
 return h,b3,right,inner
def parser(source):
 counts=Counter(preparse(r)[0]for r in source);licensed={h for h in counts if counts[h]and counts["o"+h]and counts["ot"+h]}|{"ar","al","ol"}
 def parse(r):
  h,b3,right,inner=preparse(r);frame="NONE"
  if h.startswith("ot")and h[2:]in licensed:h=h[2:];frame="OT"
  elif h.startswith("o")and h[1:]in licensed:h=h[1:];frame="O"
  host=h or"EMPTY";compiler=f'{r["stripped_prefix"]}|D{inner}|{frame}|{right}|DY{r["dy_closure"]}|B3{b3}|{state(r)}'
  return{"page_host":host,"wrapper":r["stripped_prefix"],"inner_d":inner,"local_frame":frame,"right_family":right,"b3":b3,"record_state":state(r),"compiler_signature":compiler}
 return parse,licensed
def trigrams(items):
 out=[]
 for item in items:
  s="^"+item+"$";out.extend(s[i:i+3]for i in range(max(1,len(s)-2)))
 return out
def features(groups,parsed):
 raw=[r["token"]for r in groups];root=[r["residual_host"]for r in groups];host=[p["page_host"]for p in parsed];comp=[p["compiler_signature"]for p in parsed];right=[p["right_family"]for p in parsed];b3=["B3"if p["b3"]else"NO_B3"for p in parsed]
 return{"RAW_EXACT_BAG":Counter(raw),"RAW_CHAR3":Counter(trigrams(raw)),"ROOT_EXACT_BAG":Counter(root),"ROOT_CHAR3":Counter(trigrams(root)),"PAGE_HOST_EXACT_BAG":Counter(host),"PAGE_HOST_CHAR3":Counter(trigrams(host)),"PAGE_HOST_PLUS_COMPILER_BAG":Counter(h+"@"+c for h,c in zip(host,comp)),"COMPILER_ONLY_BAG":Counter(comp),"RIGHT_FAMILY_ONLY":Counter(right),"B3_ONLY":Counter(b3)}
def wjdist(a,b):
 keys=set(a)|set(b);den=sum(max(a[k],b[k])for k in keys);return 1-sum(min(a[k],b[k])for k in keys)/den if den else 0.
def meta_pool(rows,target):
 train=[r for r in rows if r["physical_folio"]!=target["physical_folio"]]
 z=[r for r in train if r["section"]==target["section"]and r["currier"]==target["currier"]]
 if len(z)>=K:return z
 z=[r for r in train if r["section"]==target["section"]]
 if len(z)>=K:return z
 return train
def eligible_axes(rows,candidates):
 out=[]
 for axis in candidates:
  pos=sum(axis in r["tags"]for r in rows);pf=len({r["physical_folio"]for r in rows if axis in r["tags"]});nf=len({r["physical_folio"]for r in rows if axis not in r["tags"]})
  if 10<=pos<=len(rows)-10 and pf>=2 and nf>=2:out.append(axis)
 return out
def score_panel(panel,rows,axes):
 distance={rep:{}for rep in("NUISANCE",)+REPS}
 for i,a in enumerate(rows):
  for b in rows[i+1:]:
   distance["NUISANCE"][a["unit_id"],b["unit_id"]]=distance["NUISANCE"][b["unit_id"],a["unit_id"]]=wjdist(a["nuisance"],b["nuisance"])
   for rep in REPS:distance[rep][a["unit_id"],b["unit_id"]]=distance[rep][b["unit_id"],a["unit_id"]]=wjdist(a["features"][rep],b["features"][rep])
 output=[]
 for axis in axes:
  base_bits=0.;model_bits={x:0. for x in REPS};fold=defaultdict(lambda:{"base":0.,**{x:0. for x in REPS}})
  for t in rows:
   pool=meta_pool(rows,t);y=int(axis in t["tags"]);bn=sorted(pool,key=lambda x:(distance["NUISANCE"][t["unit_id"],x["unit_id"]],x["unit_id"]))[:K];bw=[1/(.1+distance["NUISANCE"][t["unit_id"],x["unit_id"]])for x in bn];p=(sum(w*int(axis in x["tags"])for w,x in zip(bw,bn))+.5)/(sum(bw)+1);loss=-math.log2(p if y else 1-p);base_bits+=loss;fold[t["physical_folio"]]["base"]+=loss
   for rep in REPS:
    near=sorted(pool,key=lambda x:(distance["NUISANCE"][t["unit_id"],x["unit_id"]]+distance[rep][t["unit_id"],x["unit_id"]],x["unit_id"]))[:K];weights=[1/(.1+distance["NUISANCE"][t["unit_id"],x["unit_id"]]+distance[rep][t["unit_id"],x["unit_id"]])for x in near];pp=(sum(w*int(axis in x["tags"])for w,x in zip(weights,near))+SHRINK*p)/(sum(weights)+SHRINK);ll=-math.log2(pp if y else 1-pp);model_bits[rep]+=ll;fold[t["physical_folio"]][rep]+=ll
  for rep in REPS:
   fg=[v["base"]-v[rep]for v in fold.values()];output.append({"panel":panel,"external_axis":axis,"units":len(rows),"positive_units":sum(axis in r["tags"]for r in rows),"physical_folios":len(fold),"representation":rep,"nuisance_bits":base_bits,"held_bits":model_bits[rep],"gain_vs_nuisance_bits":base_bits-model_bits[rep],"gain_per_unit":(base_bits-model_bits[rep])/len(rows),"positive_gain_folios":sum(x>0 for x in fg),"min_folio_gain":min(fg),"max_folio_gain":max(fg)})
 return output
def page_annotations(allowed):
 out={}
 with PAGES.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r\t"):continue
   page=raw.split("\t",2)[1]
   if page not in allowed:continue
   out[page]=dict(zip(fields,next(csv.reader([raw],delimiter="\t"))))
 return out
def renderer_transfer(groups,axes,kind):
 rows=[]
 for axis in axes:
  base=model=0.;n=0;folios=set();hosts=set()
  for t in groups:
   if kind=="O_VS_OT":valid=lambda x:{t["local_frame"],x["local_frame"]}=={"O","OT"}
   elif kind=="WRAPPER":valid=lambda x:t["wrapper"]!=x["wrapper"]
   else:valid=lambda x:t["right_family"]!="NONE"and x["right_family"]!="NONE"and t["right_family"]!=x["right_family"]
   z=[x for x in groups if x["physical_folio"]!=t["physical_folio"]and x["section"]==t["section"]and x["page_host"]==t["page_host"]and valid(x)]
   if not z:continue
   pool=[x for x in groups if x["physical_folio"]!=t["physical_folio"]and x["section"]==t["section"]];p=(sum(axis in x["tags_set"]for x in pool)+.5)/(len(pool)+1);q=(sum(axis in x["tags_set"]for x in z)+SHRINK*p)/(len(z)+SHRINK);y=int(axis in t["tags_set"]);base-=math.log2(p if y else 1-p);model-=math.log2(q if y else 1-q);n+=1;folios.add(t["physical_folio"]);hosts.add(t["page_host"])
  rows.append({"renderer_contrast":kind,"external_axis":axis,"eligible_predictions":n,"physical_folios":len(folios),"page_hosts":len(hosts),"nuisance_bits":base,"same_host_cross_renderer_bits":model,"gain_vs_nuisance_bits":base-model,"capacity_state":"SCORED"if n else"UNSCORED_ZERO_EXACT_CROSS_FOLIO_CAPACITY"})
 return rows
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);parse,licensed=parser(source)
 ann=[]
 with ANN.open(encoding="utf-8",newline="")as h:
  for r in csv.DictReader(h,delimiter="\t"):
   if r["locus"].startswith("f84r"):continue
   ann.append(r)
 assert len(ann)==671
 byloc=defaultdict(list)
 for r in ann:byloc[r["locus"]].append(r)
 local=[];group_inventory=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda r:int(r["group_index"]));pp=[parse(r)for r in z];first=z[0];tags={x for x in(first["object_tags"]+";"+first["relation_tags"]).split(";")if x and x!="LABEL"};feat=features(z,pp);nuisance=Counter(("HAND_"+first["hand"],"KIND_"+first["kind"],"UNIT_"+first["unit"],"GROUPS_"+str(len(z)),"CERTAINTY_"+first["annotation_certainty"]));row={"unit_id":"L:"+locus,"panel":"EXACT_LOCAL","locus":locus,"page":first["page"],"physical_folio":first["physical_folio"],"section":first["section"],"currier":first["currier"],"hand":first["hand"],"certainty":first["annotation_certainty"],"tags":tags,"nuisance":nuisance,"features":feat};local.append(row)
  for r,p in zip(z,pp):group_inventory.append({"locus":locus,"page":r["page"],"physical_folio":r["physical_folio"],"section":r["section"],"currier":r["currier"],"hand":r["hand"],"group_index":r["group_index"],"token":r["token"],"residual_host":r["residual_host"],**p,"annotation_certainty":r["annotation_certainty"],"tags":";".join(sorted(tags))or"NONE"})
 bypage=defaultdict(list)
 for r in source:bypage[r["page"]].append(r)
 pa=page_annotations(set(bypage));page_rows=[]
 for page,z in sorted(bypage.items()):
  if page not in pa:continue
  p=pa[page];pp=[parse(r)for r in z];tags={x for x in p["source_tags"].split(";")if x and x!="TEXT_PARAGRAPHS"};feat=features(z,pp);line_n=len({r["locus"]for r in z});gpl=len(z)/line_n;nuisance=Counter(("HAND_"+z[0]["hand"],"LAYOUT_"+p["layout_template_id"],"P_"+p["P_count"],"L_"+p["L_count"],"C_"+p["C_count"],"R_"+p["R_count"],"PARA_"+p["paragraph_start_count"],"GROUP_BUCKET_"+str(len(z)//25),"LINE_BUCKET_"+str(line_n//5),"GPL_BUCKET_"+str(int(gpl*2))));page_rows.append({"unit_id":"P:"+page,"panel":"PAGE_CATALOGUE","locus":page,"page":page,"physical_folio":z[0]["physical_folio"],"section":z[0]["section"],"currier":z[0]["currier"],"hand":z[0]["hand"],"certainty":"SOURCE_CATALOGUE","tags":tags,"nuisance":nuisance,"features":feat})
 local_axes=eligible_axes(local,LOCAL_AXES);page_candidates=sorted({x for r in page_rows for x in r["tags"]});page_axes=eligible_axes(page_rows,page_candidates);panels=(("EXACT_LOCAL_ALL",local,local_axes),("EXACT_LOCAL_UNHEDGED",[r for r in local if r["certainty"]=="UNHEDGED"],None),("PAGE_CATALOGUE",page_rows,page_axes));scores=[]
 for name,rows,axes in panels:scores+=score_panel(name,rows,axes or eligible_axes(rows,LOCAL_AXES))
 sf=list(scores[0]);write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in scores],sf)
 summary=[]
 for panel in sorted({r["panel"]for r in scores}):
  z=[r for r in scores if r["panel"]==panel]
  for rep in REPS:
   q=[r for r in z if r["representation"]==rep];summary.append({"panel":panel,"representation":rep,"external_axes":len(q),"descriptive_total_gain_bits":sum(r["gain_vs_nuisance_bits"]for r in q),"mean_gain_per_unit":sum(r["gain_per_unit"]for r in q)/len(q),"axes_positive":sum(r["gain_vs_nuisance_bits"]>0 for r in q),"axes_beating_raw_char3":sum(r["gain_vs_nuisance_bits"]>next(x["gain_vs_nuisance_bits"]for x in z if x["external_axis"]==r["external_axis"]and x["representation"]=="RAW_CHAR3")for r in q)})
 write(SUMMARY,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in summary],list(summary[0]));group_rows=[]
 for r in group_inventory:group_rows.append({**r,"tags_set":set(r["tags"].split(";"))})
 inv=[]
 for kind in("O_VS_OT","WRAPPER","RIGHT_FAMILY"):inv+=renderer_transfer(group_rows,local_axes,kind)
 write(INVAR,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in inv],list(inv[0]));write(INVENTORY,group_inventory,list(group_inventory[0]))
 variants=[{"variant_id":"V00","panel":"INITIAL_POOL_RATE_BASELINE","status":"SUPERSEDED_LENGTH_LAYOUT_LEAKAGE","description":"Preliminary page total gains PAGE_HOST_CHAR3 +16.897, raw +14.322, compiler +12.599, B3 +4.947; baseline averaged the metadata pool and representation neighbours could reselect page length/layout, so these values are not headline evidence."},{"variant_id":"V01","panel":"EXACT_LOCAL_ALL","status":"RUN","description":"All 560 existing exact annotated loci; hedged states retained."},{"variant_id":"V02","panel":"EXACT_LOCAL_UNHEDGED","status":"RUN","description":"Unhedged sensitivity; no outcome or feature selection."},{"variant_id":"V03","panel":"PAGE_CATALOGUE","status":"RUN","description":"Confirmed-prose page inventories against pre-existing catalogue tags."},{"variant_id":"V04","panel":"HPR2_PRIMARY_PARSE","status":"RUN","description":"B3 then right-family then carrier-D then ladder-licensed O/OT stripping."},{"variant_id":"V05","panel":"GLOBAL_O_OT_STRIP","status":"NOT_RUN_NONPRIMARY_SENSITIVITY","description":"Would strip every initial O/OT and is not licensed by GDT054 ladders."},{"variant_id":"V06","panel":"RENDERER_TRANSFER","status":"RUN","description":"Exact same PAGE_HOST across folios under opposite renderer; zero capacity remains explicit."},{"variant_id":"V07","panel":"F84R","status":"SEALED_NOT_OPENED","description":"Filtered before annotation/formal retention and never scored."},{"variant_id":"V08","panel":"SHARED_NUISANCE_NEIGHBOURS","status":"PRIMARY","description":"All predictors add their distance to the same folio-held section/Currier/hand/layout/length nuisance distance; baseline uses nuisance distance alone."}];write(VARIANTS,variants,list(variants[0]))
 sm={(r["panel"],r["representation"]):r for r in summary};lead={p:max((r for r in summary if r["panel"]==p),key=lambda r:r["descriptive_total_gain_bits"])for p in sorted({r["panel"]for r in summary})};host={p:sm[p,"PAGE_HOST_CHAR3"]for p in lead};raw={p:sm[p,"RAW_CHAR3"]for p in lead};compiler={p:sm[p,"COMPILER_ONLY_BAG"]for p in lead};b3={p:sm[p,"B3_ONLY"]for p in lead};o_cap=sum(r["eligible_predictions"]for r in inv if r["renderer_contrast"]=="O_VS_OT")
 def scoped_page(prefix):
  out={}
  for rep in REPS:
   z=[r for r in scores if r["panel"]=="PAGE_CATALOGUE"and r["representation"]==rep and r["external_axis"].startswith(prefix)]
   out[rep]={"axes":len(z),"descriptive_total_gain_bits":sum(r["gain_vs_nuisance_bits"]for r in z),"axes_positive":sum(r["gain_vs_nuisance_bits"]>0 for r in z)}
  return out
 page_content=scoped_page("SOURCE_");page_layout=scoped_page("TEXT_")
 status="PAGE_HOST_SPECIFIC_EXTERNAL_INFORMATION_LOCALIZATION_NOT_SUPPORTED"
 report=f"""# GDT059 — HPR2 external-information localization

## Outcome

**{status}**

This exploratory pass compares {len(local)} exact human-annotated loci and
{len(page_rows)} catalogue-covered pages under complete physical-folio
holdout. It tests {len(local_axes)} local object/relation codes and
{len(page_axes)} page catalogue codes. Archived annotation classes are noisy,
postselected hypothesis-generation outcomes, not semantic confirmation.

The top held representation in the all-local panel is
`{lead['EXACT_LOCAL_ALL']['representation']}` with descriptive summed gain
{lead['EXACT_LOCAL_ALL']['descriptive_total_gain_bits']:+.3f} bits across its
correlated axes. PAGE_HOST character trigrams score
{host['EXACT_LOCAL_ALL']['descriptive_total_gain_bits']:+.3f}, versus raw
surface character trigrams {raw['EXACT_LOCAL_ALL']['descriptive_total_gain_bits']:+.3f},
compiler-only {compiler['EXACT_LOCAL_ALL']['descriptive_total_gain_bits']:+.3f},
and B3-only {b3['EXACT_LOCAL_ALL']['descriptive_total_gain_bits']:+.3f}.

On the page-catalogue panel the corresponding gains across all five correlated
tags are PAGE_HOST
{host['PAGE_CATALOGUE']['descriptive_total_gain_bits']:+.3f}, raw
{raw['PAGE_CATALOGUE']['descriptive_total_gain_bits']:+.3f}, compiler-only
{compiler['PAGE_CATALOGUE']['descriptive_total_gain_bits']:+.3f}, and B3-only
{b3['PAGE_CATALOGUE']['descriptive_total_gain_bits']:+.3f}. These totals rank
hypotheses only; axes overlap and must not be added as independent evidence.

Restricting that panel to the three source content tags, PAGE_HOST scores
{page_content['PAGE_HOST_CHAR3']['descriptive_total_gain_bits']:+.3f} bits,
but ROOT scores {page_content['ROOT_CHAR3']['descriptive_total_gain_bits']:+.3f},
raw surface {page_content['RAW_CHAR3']['descriptive_total_gain_bits']:+.3f},
compiler-only {page_content['COMPILER_ONLY_BAG']['descriptive_total_gain_bits']:+.3f},
RIGHT-family-only {page_content['RIGHT_FAMILY_ONLY']['descriptive_total_gain_bits']:+.3f},
and the intended B3 negative control
{page_content['B3_ONLY']['descriptive_total_gain_bits']:+.3f}. Because the
compiler and B3 controls preserve at least as much page-content signal as the
PAGE_HOST, this pass does **not** localize source-catalogue content to PAGE_HOST.
The likely explanation is residual page/register ecology not removed by the
available low-capacity nuisance scaffold.

At exact annotated loci the weaker useful lead is narrower: PAGE_HOST
character trigrams are positive on five of eight axes and uniquely lead only
`REL_PROXIMITY` at +5.081 bits; that advantage falls to +0.159 bits in the
unhedged subset. Raw character trigrams remain the aggregate leader. This is a
future feature-engineering lead, not evidence for a semantic host layer.

## Renderer preservation and capacity

Cross-wrapper and cross-right-family same-PAGE_HOST predictions are reported
for every local annotation axis. Exact cross-folio O-versus-OT transfer has
{o_cap} eligible predictions, so the frozen O/OT content-preservation
hypothesis is {"UNSCORED_ZERO_CAPACITY"if not o_cap else"SCORED"}; it was not
rescued with same-folio or different-host examples.

The result fails to localize the weak external signal specifically to
PAGE_HOST. It does not establish that PAGE_HOST is lexical, semantic, or
linguistic. Every
representation, negative control, hedged sensitivity, and capacity failure is
retained in the artifacts. No PAGE_HOST receives an English gloss, semantic
role, word, morpheme, POS, sound, language, plaintext, or translation. f84r
was filtered before retention and was not opened, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT059_HPR2_EXTERNAL_INFORMATION_LOCALIZATION_RESULT_V1","status":status,"panels":{"exact_local_all":len(local),"exact_local_unhedged":sum(r["certainty"]=="UNHEDGED"for r in local),"page_catalogue":len(page_rows)},"axes":{"local":local_axes,"page":page_axes},"representations":list(REPS),"licensed_o_ot_hosts":len(licensed),"nuisance_control":"Shared folio-held five-neighbour section/Currier plus hand, kind/layout, group/line count, groups-per-line, and P/L/C/R profile distance; every representation adds to the same nuisance distance.","panel_leaders":lead,"page_host_summary":host,"raw_char_summary":raw,"compiler_only_summary":compiler,"b3_summary":b3,"page_content_summary":page_content,"page_layout_summary":page_layout,"o_ot_cross_folio_capacity":o_cap,"localization_decision":"PAGE_HOST does not outperform raw/root aggregately and compiler-only/RIGHT-family/B3 controls retain equal or greater page-content signal.","interpretation":"Exploratory relative information localization only. Archived annotations are hypothesis-generation outcomes and correlated axes are not independent evidence.","claim_ceiling":"No PAGE_HOST gloss, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),ANN.name:sha(ANN),"gdt012_result.json":sha(ROOT/"gdt012_result.json"),str(PAGES.relative_to(ROOT)):sha(PAGES),"gdt051_result.json":sha(ROOT/"gdt051_result.json"),"gdt055_result.json":sha(ROOT/"gdt055_result.json"),"gdt056_result.json":sha(ROOT/"gdt056_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{INVENTORY.name:sha(INVENTORY),SCORES.name:sha(SCORES),SUMMARY.name:sha(SUMMARY),INVAR.name:sha(INVAR),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"panels":result["panels"],"leaders":lead,"o_ot_capacity":o_cap},sort_keys=True))
if __name__=="__main__":main()

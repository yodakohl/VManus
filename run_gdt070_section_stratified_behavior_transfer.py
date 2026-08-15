#!/usr/bin/env python3
"""GDT070: GDT068 behavior profile inside mixed section/Currier cells."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT070_SECTION_STRATIFIED_BEHAVIOR_TRANSFER_METHOD.md";REPORT=ROOT/"GDT070_SECTION_STRATIFIED_BEHAVIOR_TRANSFER_REPORT.md";SCORES=ROOT/"gdt070_section_stratified_scores.tsv";FOLDS=ROOT/"gdt070_section_stratified_folds.tsv";VARIANTS=ROOT/"gdt070_variant_log.tsv";RESULT=ROOT/"gdt070_result.json"
AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP");REPS=("RAW_CHAR3","PAGE_HOST_CHAR3","BEHAVIOR_SELF_NEIGHBOR_NOPOS");K=5;SHRINK=4.
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def tri(items):
 out=[]
 for x in items:
  s="^"+x+"$";out.extend(s[i:i+3]for i in range(max(1,len(s)-2)))
 return Counter(out)
def dist(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k);return 1-sum(min(a[x],b[x])for x in k)/d if d else 0.
def main():
 src=read(SOURCE);ann=read(ANN);parsed=read(PARSED);assert len(src)==15592 and len(ann)==len(parsed)==671 and not any(r["locus"].startswith("f84r")for r in src+parsed)
 byline=defaultdict(list);hf=defaultdict(set)
 for r in src:byline[r["locus"]].append(r);hf[r["page_host"]].add(r["physical_folio"])
 events=[]
 for z in byline.values():
  z.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(z):
   p=z[i-1]if i else None;n=z[i+1]if i+1<len(z)else None;tokens=["W="+r["wrapper"],"D="+r["inner_d"],"F="+r["local_frame"],"R="+r["right_family"],"DY="+r["dy_closure"],"B3="+r["b3"],"PW="+(p["wrapper"]if p else"BOS"),"PF="+(p["local_frame"]if p else"BOS"),"PDY="+(p["dy_closure"]if p else"BOS"),"NW="+(n["wrapper"]if n else"EOS"),"NF="+(n["local_frame"]if n else"EOS"),"NDY="+(n["dy_closure"]if n else"EOS")];events.append((r["physical_folio"],r["page_host"],tokens))
 amap={(r["locus"],r["group_index"]):r for r in ann};byloc=defaultdict(list)
 for r in parsed:byloc[r["locus"]].append(r)
 rows=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda r:int(r["group_index"]));a=amap[locus,z[0]["group_index"]]
  if all(len(hf[r["page_host"]])>=2 for r in z):
   rows.append({"unit_id":locus,"physical_folio":z[0]["physical_folio"],"section":z[0]["section"],"currier":z[0]["currier"],"tags":{x for x in(a["object_tags"]+";"+a["relation_tags"]).split(";")if x and x!="LABEL"},"groups":z,"nuisance":Counter(("HAND="+a["hand"],"KIND="+a["kind"],"UNIT="+a["unit"],"N="+str(len(z)),"CERT="+a["annotation_certainty"]))})
 assert len(rows)==332;profiles={}
 for fol in sorted({r["physical_folio"]for r in rows}):
  counts=defaultdict(Counter);n=Counter()
  for f,h,t in events:
   if f==fol:continue
   counts[h].update(t);n[h]+=1
  profiles[fol]={h:Counter({k:v/n[h]for k,v in q.items()})for h,q in counts.items()}
 raw={r["unit_id"]:tri([g["token"]for g in r["groups"]])for r in rows};host={r["unit_id"]:tri([g["page_host"]for g in r["groups"]])for r in rows}
 def behavior(r,fold):
  out=Counter()
  for g in r["groups"]:out.update(profiles[fold][g["page_host"]])
  return out
 cells=[]
 for axis in AXES:
  by=defaultdict(list)
  for r in rows:by[r["section"],r["currier"]].append(r)
  for (section,currier),z in sorted(by.items()):
   pos=sum(axis in r["tags"]for r in z);pf=len({r["physical_folio"]for r in z if axis in r["tags"]});nf=len({r["physical_folio"]for r in z if axis not in r["tags"]})
   if len(z)<10 or not(3<=pos<=len(z)-3)or pf<2 or nf<2:continue
   cells.append((axis,section,currier,z))
 score_rows=[];fold_rows=[]
 for axis,section,currier,z in cells:
  totals={rep:0. for rep in REPS};base=0.;fold=defaultdict(lambda:{"base":0.,**{rep:0. for rep in REPS},"predictions":0})
  positive=sum(axis in r["tags"]for r in z)
  for t in z:
   pool=[x for x in z if x["physical_folio"]!=t["physical_folio"]]
   if len(pool)<K:continue
   nd={x["unit_id"]:dist(t["nuisance"],x["nuisance"])for x in pool};near=sorted(pool,key=lambda x:(nd[x["unit_id"]],x["unit_id"]))[:K];ww=[1/(.1+nd[x["unit_id"]])for x in near];p=(sum(w*int(axis in x["tags"])for w,x in zip(ww,near))+.5)/(sum(ww)+1);y=int(axis in t["tags"]);ll=-math.log2(p if y else 1-p);base+=ll;fold[t["physical_folio"]]["base"]+=ll;fold[t["physical_folio"]]["predictions"]+=1
   tf={"RAW_CHAR3":raw[t["unit_id"]],"PAGE_HOST_CHAR3":host[t["unit_id"]],"BEHAVIOR_SELF_NEIGHBOR_NOPOS":behavior(t,t["physical_folio"])}
   for rep in REPS:
    def feat(x):return raw[x["unit_id"]]if rep=="RAW_CHAR3"else host[x["unit_id"]]if rep=="PAGE_HOST_CHAR3"else behavior(x,t["physical_folio"])
    q=sorted(pool,key=lambda x:(nd[x["unit_id"]]+dist(tf[rep],feat(x)),x["unit_id"]))[:K];wq=[1/(.1+nd[x["unit_id"]]+dist(tf[rep],feat(x)))for x in q];pp=(sum(w*int(axis in x["tags"])for w,x in zip(wq,q))+SHRINK*p)/(sum(wq)+SHRINK);loss=-math.log2(pp if y else 1-pp);totals[rep]+=loss;fold[t["physical_folio"]][rep]+=loss
  predictions=sum(v["predictions"]for v in fold.values())
  for rep in REPS:
   gains=[v["base"]-v[rep]for v in fold.values()];score_rows.append({"external_axis":axis,"section":section,"currier":currier or"NONE","eligible_loci":len(z),"predictions":predictions,"positive_loci":positive,"physical_folios":len(fold),"representation":rep,"nuisance_bits":base,"held_bits":totals[rep],"gain_bits":base-totals[rep],"gain_per_prediction":(base-totals[rep])/predictions,"positive_gain_folios":sum(x>0 for x in gains),"min_folio_gain":min(gains),"max_folio_gain":max(gains)})
  for fol,v in sorted(fold.items()):
   for rep in REPS:fold_rows.append({"external_axis":axis,"section":section,"currier":currier or"NONE","physical_folio":fol,"predictions":v["predictions"],"representation":rep,"gain_bits":v["base"]-v[rep]})
 write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));write(FOLDS,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in fold_rows],list(fold_rows[0]));summary={}
 for rep in REPS:
  q=[r for r in score_rows if r["representation"]==rep];summary[rep]={"cells":len(q),"positive_cells":sum(r["gain_bits"]>0 for r in q),"cell_mean_gain_per_prediction":sum(r["gain_per_prediction"]for r in q)/len(q),"total_gain_bits":sum(r["gain_bits"]for r in q),"cells_beating_raw":sum(r["gain_bits"]>next(x["gain_bits"]for x in score_rows if x["external_axis"]==r["external_axis"]and x["section"]==r["section"]and x["currier"]==r["currier"]and x["representation"]=="RAW_CHAR3")for r in q)}
 best=summary["BEHAVIOR_SELF_NEIGHBOR_NOPOS"];rawsum=summary["RAW_CHAR3"];behavior_rows=[r for r in score_rows if r["representation"]=="BEHAVIOR_SELF_NEIGHBOR_NOPOS"];multi={}
 for axis in sorted({r["external_axis"]for r in behavior_rows}):
  q=[r for r in behavior_rows if r["external_axis"]==axis]
  if len(q)>=2:multi[axis]={"cells":len(q),"positive_cells":sum(r["gain_bits"]>0 for r in q),"sections":";".join(sorted(r["section"]for r in q)),"mean_gain_per_prediction":sum(r["gain_per_prediction"]for r in q)/len(q)}
 status="BEHAVIOR_PROFILE_LEAD_PARTLY_SURVIVES_SECTION_STRATIFICATION"if best["cell_mean_gain_per_prediction"]>rawsum["cell_mean_gain_per_prediction"]and best["positive_cells"]>len(cells)/2 else"BEHAVIOR_PROFILE_LEAD_COLLAPSES_UNDER_SECTION_STRATIFICATION"
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"GDT068 selected no-position behavior profile inside mixed section/Currier cells."},{"variant_id":"V01","status":"RUN_BASELINES","description":"Raw and PAGE_HOST char3 on identical targets/pools."},{"variant_id":"V02","status":"CAPACITY_RULE","description":"At least 10 loci, 3 positives/negatives, and 2 positive/negative folios; targets with fewer than five training loci skipped."},{"variant_id":"V03","status":"POSTSELECTED_AUDIT","description":"Representation inherited from GDT068, not an independent validation."},{"variant_id":"V04","status":"NOT_RUN","description":"No semantic class, gloss, alternate parser, cross-section borrowing, or f84r."}];write(VARIANTS,variants,list(variants[0]));top=max((r for r in score_rows if r["representation"]=="BEHAVIOR_SELF_NEIGHBOR_NOPOS"),key=lambda r:r["gain_per_prediction"]);bottom=min((r for r in score_rows if r["representation"]=="BEHAVIOR_SELF_NEIGHBOR_NOPOS"),key=lambda r:r["gain_per_prediction"])
 report=f"""# GDT070 — section-stratified PAGE_HOST behavior transfer

## Outcome

**{status}**

Twelve mixed external-axis×section×Currier cells satisfy the frozen capacity
rule.  The selected behavior profile is positive in {best['positive_cells']}/12
cells, with cell-balanced gain {best['cell_mean_gain_per_prediction']:+.4f}
bit/prediction and total {best['total_gain_bits']:+.3f} bits.  Raw char3 is
positive in {rawsum['positive_cells']}/12 cells at
{rawsum['cell_mean_gain_per_prediction']:+.4f} bit/prediction.  Behavior beats
raw in {best['cells_beating_raw']}/12 cells.  Its strongest cell is
`{top['external_axis']}` in section `{top['section']}` at
{top['gain_per_prediction']:+.4f} bit/prediction; its weakest is
`{bottom['external_axis']}` in section `{bottom['section']}` at
{bottom['gain_per_prediction']:+.4f}.

Among axes with multiple eligible sections, `REL_ENCLOSURE` is positive in
{multi['REL_ENCLOSURE']['positive_cells']}/{multi['REL_ENCLOSURE']['cells']},
`REL_ARRAY_OR_GROUP` in
{multi['REL_ARRAY_OR_GROUP']['positive_cells']}/{multi['REL_ARRAY_OR_GROUP']['cells']},
and `REL_EXPLICIT_ATTACHMENT` in only
{multi['REL_EXPLICIT_ATTACHMENT']['positive_cells']}/{multi['REL_EXPLICIT_ATTACHMENT']['cells']}.

This removes broad section identity but remains a postselected audit on noisy,
correlated archived axes.  The complete cell and folio failures are exported.
No semantic class, role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned.  f84r was excluded and not
opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT070_SECTION_STRATIFIED_BEHAVIOR_TRANSFER_RESULT_V1","status":status,"groups":len(src),"eligible_loci":len(rows),"mixed_cells":len(cells),"summary":summary,"multi_section_axes":multi,"strongest_behavior_cell":top,"weakest_behavior_cell":bottom,"selection_disclosure":"The behavior representation was selected in GDT068; this is a confound audit, not independent validation.","interpretation":"Postselected section-stratified audit of GDT068; cell and folio failures retained, no independent validation.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt068_result.json":sha(ROOT/"gdt068_result.json"),"gdt069_result.json":sha(ROOT/"gdt069_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),FOLDS.name:sha(FOLDS),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"cells":len(cells),"behavior":best,"raw":rawsum,"top":(top["external_axis"],top["section"],top["gain_per_prediction"]),"bottom":(bottom["external_axis"],bottom["section"],bottom["gain_per_prediction"])},sort_keys=True))
if __name__=="__main__":main()

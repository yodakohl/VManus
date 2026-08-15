#!/usr/bin/env python3
"""GDT068: folio-held PAGE_HOST behavior profiles versus external axes."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT068_PAGE_HOST_BEHAVIOR_PROFILE_METHOD.md";REPORT=ROOT/"GDT068_PAGE_HOST_BEHAVIOR_PROFILE_REPORT.md";PROFILES=ROOT/"gdt068_host_behavior_profiles.tsv";SCORES=ROOT/"gdt068_behavior_representation_scores.tsv";SUMMARY=ROOT/"gdt068_behavior_representation_summary.tsv";VARIANTS=ROOT/"gdt068_variant_log.tsv";RESULT=ROOT/"gdt068_result.json"
K=5;SHRINK=4.;REPS=("RAW_CHAR3","PAGE_HOST_CHAR3","COMPILER_ONLY","BEHAVIOR_SELF","BEHAVIOR_SELF_NEIGHBOR","BEHAVIOR_SELF_NEIGHBOR_NOPOS");AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP")
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def trigrams(items):
 out=[]
 for item in items:
  s="^"+item+"$";out.extend(s[i:i+3]for i in range(max(1,len(s)-2)))
 return out
def wjdist(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k);return 1-sum(min(a[x],b[x])for x in k)/d if d else 0.
def eligible_axes(rows):
 return[a for a in AXES if 10<=sum(a in r["tags"]for r in rows)<=len(rows)-10 and len({r["physical_folio"]for r in rows if a in r["tags"]})>=2 and len({r["physical_folio"]for r in rows if a not in r["tags"]})>=2]
def main():
 src=read(SOURCE);assert len(src)==15592 and not any(r["locus"].startswith("f84r")for r in src)
 byline=defaultdict(list)
 for r in src:byline[r["locus"]].append(r)
 events=[];host_folios=defaultdict(set)
 for locus,z in byline.items():
  z.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(z):
   host_folios[r["page_host"]].add(r["physical_folio"]);prev=z[i-1]if i else None;nxt=z[i+1]if i+1<len(z)else None
   self_tokens=["W="+r["wrapper"],"D="+r["inner_d"],"F="+r["local_frame"],"R="+r["right_family"],"DY="+r["dy_closure"],"B3="+r["b3"],"P="+r["position_quartile"]]
   neighbor=["PW="+(prev["wrapper"]if prev else"BOS"),"PF="+(prev["local_frame"]if prev else"BOS"),"PDY="+(prev["dy_closure"]if prev else"BOS"),"NW="+(nxt["wrapper"]if nxt else"EOS"),"NF="+(nxt["local_frame"]if nxt else"EOS"),"NDY="+(nxt["dy_closure"]if nxt else"EOS")]
   events.append({"folio":r["physical_folio"],"host":r["page_host"],"self":self_tokens,"neighbor":neighbor})
 ann=read(ANN);parsed=read(PARSED);assert len(ann)==len(parsed)==671
 amap={(r["locus"],r["group_index"]):r for r in ann};assert all((r["locus"],r["group_index"])in amap for r in parsed)
 byloc=defaultdict(list)
 for r in parsed:byloc[r["locus"]].append(r)
 rows=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda r:int(r["group_index"]));a=amap[locus,z[0]["group_index"]];tags={x for x in(a["object_tags"]+";"+a["relation_tags"]).split(";")if x and x!="LABEL"}
  if all(len(host_folios[r["page_host"]])>=2 for r in z):
   rows.append({"unit_id":locus,"physical_folio":z[0]["physical_folio"],"section":z[0]["section"],"currier":z[0]["currier"],"tags":tags,"groups":z,"nuisance":Counter(("HAND="+a["hand"],"KIND="+a["kind"],"UNIT="+a["unit"],"N="+str(len(z)),"CERT="+a["annotation_certainty"]))})
 assert len(rows)==332;axes=eligible_axes(rows);folds=sorted({r["physical_folio"]for r in rows});fold_profiles={};profile_rows=[]
 for folio in folds:
  counts=defaultdict(lambda:{"self":Counter(),"neighbor":Counter(),"n":0})
  for e in events:
   if e["folio"]==folio:continue
   counts[e["host"]]["self"].update(e["self"]);counts[e["host"]]["neighbor"].update(e["neighbor"]);counts[e["host"]]["n"]+=1
  fold_profiles[folio]={}
  for host,v in counts.items():
   n=v["n"];selfp=Counter({k:q/n for k,q in v["self"].items()});neigh=Counter({k:q/n for k,q in v["neighbor"].items()});nopos=Counter({k:q for k,q in selfp.items()if not k.startswith("P=")});nopos.update(neigh);both=Counter(selfp);both.update(neigh);fold_profiles[folio][host]=(selfp,both,nopos)
 global_counts=Counter(e["host"]for e in events)
 for host in sorted(host_folios):
  if len(host_folios[host])>=2:
   z=[e for e in events if e["host"]==host];selfc=Counter(x for e in z for x in e["self"]);profile_rows.append({"page_host":host,"occurrences":global_counts[host],"physical_folios":len(host_folios[host]),"dominant_wrapper":max((k for k in selfc if k.startswith("W=")),key=selfc.get).split("=",1)[1],"dominant_frame":max((k for k in selfc if k.startswith("F=")),key=selfc.get).split("=",1)[1],"dominant_right_family":max((k for k in selfc if k.startswith("R=")),key=selfc.get).split("=",1)[1],"mean_position_quartile":sum(int(x.split("=")[1])*q for x,q in selfc.items()if x.startswith("P="))/global_counts[host]})
 write(PROFILES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in profile_rows],list(profile_rows[0]))
 rawfeat={};hostfeat={};compfeat={}
 for r in rows:
  rawfeat[r["unit_id"]]=Counter(trigrams([x["token"]for x in r["groups"]]));hostfeat[r["unit_id"]]=Counter(trigrams([x["page_host"]for x in r["groups"]]));compfeat[r["unit_id"]]=Counter(x["compiler_signature"]for x in r["groups"])
 def behavior(row,fold,index):
  out=Counter()
  for g in row["groups"]:out.update(fold_profiles[fold][g["page_host"]][index])
  return out
 score_rows=[]
 for axis in axes:
  base=0.;bits={rep:0. for rep in REPS};fg=defaultdict(lambda:{"base":0.,**{rep:0. for rep in REPS}})
  for t in rows:
   fold=t["physical_folio"];pool=[x for x in rows if x["physical_folio"]!=fold and x["section"]==t["section"]and x["currier"]==t["currier"]]
   if len(pool)<K:pool=[x for x in rows if x["physical_folio"]!=fold and x["section"]==t["section"]]
   if len(pool)<K:pool=[x for x in rows if x["physical_folio"]!=fold]
   nd={x["unit_id"]:wjdist(t["nuisance"],x["nuisance"])for x in pool};near=sorted(pool,key=lambda x:(nd[x["unit_id"]],x["unit_id"]))[:K];weights=[1/(.1+nd[x["unit_id"]])for x in near];p=(sum(w*int(axis in x["tags"])for w,x in zip(weights,near))+.5)/(sum(weights)+1);y=int(axis in t["tags"]);loss=-math.log2(p if y else 1-p);base+=loss;fg[fold]["base"]+=loss
   target_features={"RAW_CHAR3":rawfeat[t["unit_id"]],"PAGE_HOST_CHAR3":hostfeat[t["unit_id"]],"COMPILER_ONLY":compfeat[t["unit_id"]],"BEHAVIOR_SELF":behavior(t,fold,0),"BEHAVIOR_SELF_NEIGHBOR":behavior(t,fold,1),"BEHAVIOR_SELF_NEIGHBOR_NOPOS":behavior(t,fold,2)}
   for rep in REPS:
    def feat(x):
     if rep=="RAW_CHAR3":return rawfeat[x["unit_id"]]
     if rep=="PAGE_HOST_CHAR3":return hostfeat[x["unit_id"]]
     if rep=="COMPILER_ONLY":return compfeat[x["unit_id"]]
     return behavior(x,fold,{"BEHAVIOR_SELF":0,"BEHAVIOR_SELF_NEIGHBOR":1,"BEHAVIOR_SELF_NEIGHBOR_NOPOS":2}[rep])
    ranked=sorted(pool,key=lambda x:(nd[x["unit_id"]]+wjdist(target_features[rep],feat(x)),x["unit_id"]))[:K];ww=[1/(.1+nd[x["unit_id"]]+wjdist(target_features[rep],feat(x)))for x in ranked];q=(sum(w*int(axis in x["tags"])for w,x in zip(ww,ranked))+SHRINK*p)/(sum(ww)+SHRINK);ll=-math.log2(q if y else 1-q);bits[rep]+=ll;fg[fold][rep]+=ll
  for rep in REPS:
   gains=[z["base"]-z[rep]for z in fg.values()];score_rows.append({"external_axis":axis,"representation":rep,"units":len(rows),"positive_units":sum(axis in r["tags"]for r in rows),"physical_folios":len(fg),"nuisance_bits":base,"held_bits":bits[rep],"gain_vs_nuisance_bits":base-bits[rep],"gain_per_unit":(base-bits[rep])/len(rows),"positive_gain_folios":sum(x>0 for x in gains),"min_folio_gain":min(gains),"max_folio_gain":max(gains)})
 write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in score_rows],list(score_rows[0]));summary=[]
 for rep in REPS:
  z=[r for r in score_rows if r["representation"]==rep];summary.append({"representation":rep,"external_axes":len(z),"descriptive_total_gain_bits":sum(r["gain_vs_nuisance_bits"]for r in z),"axes_positive":sum(r["gain_vs_nuisance_bits"]>0 for r in z),"axes_beating_raw_char3":sum(r["gain_vs_nuisance_bits"]>next(x["gain_vs_nuisance_bits"]for x in score_rows if x["external_axis"]==r["external_axis"]and x["representation"]=="RAW_CHAR3")for r in z)})
 write(SUMMARY,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in summary],list(summary[0]));lead=max(summary,key=lambda r:r["descriptive_total_gain_bits"]);best_behavior=max((r for r in summary if r["representation"].startswith("BEHAVIOR")),key=lambda r:r["descriptive_total_gain_bits"]);raw=next(r for r in summary if r["representation"]=="RAW_CHAR3");host=next(r for r in summary if r["representation"]=="PAGE_HOST_CHAR3");status="BEHAVIORAL_PAGE_HOST_PROFILE_LEAD_POSTSELECTED"if best_behavior["descriptive_total_gain_bits"]>max(raw["descriptive_total_gain_bits"],host["descriptive_total_gain_bits"])else"BEHAVIORAL_PAGE_HOST_CLASSES_DO_NOT_OUTPERFORM_STRING_BASELINES";axis_scores={r["external_axis"]:r for r in score_rows if r["representation"]==best_behavior["representation"]}
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"SELF formal host profile rebuilt without target folio."},{"variant_id":"V01","status":"RUN","description":"SELF plus preceding/following compiler-state profile."},{"variant_id":"V02","status":"RUN","description":"SELF plus neighbor profile without position."},{"variant_id":"V03","status":"RUN_BASELINES","description":"Raw char3, PAGE_HOST char3, and compiler-only on identical 332-locus panel."},{"variant_id":"V04","status":"EXCLUDED_CAPACITY","description":"Loci containing a host on fewer than two prose folios excluded."},{"variant_id":"V05","status":"NOT_RUN","description":"No supervised semantic clustering, gloss, alternate parser, or f84r."}];write(VARIANTS,variants,list(variants[0]))
 report=f"""# GDT068 — PAGE_HOST behavior-profile external-information test

## Outcome

**{status}**

The transferable panel contains {len(rows)} exact annotated loci on
{len(folds)} physical folios and {len(axes)} archived visual/content axes.
Every target-folio host behavior profile is rebuilt without that folio.
The overall descriptive leader is `{lead['representation']}` at
{lead['descriptive_total_gain_bits']:+.3f} summed held bits.  The best formal
behavior profile is `{best_behavior['representation']}` at
{best_behavior['descriptive_total_gain_bits']:+.3f}, versus raw char3
{raw['descriptive_total_gain_bits']:+.3f} and PAGE_HOST char3
{host['descriptive_total_gain_bits']:+.3f}.  Behavior profiles therefore beat
raw strings on {best_behavior['axes_beating_raw_char3']}/{len(axes)} axes.

The selected profile gains most on `STAR_OR_SKY`
{axis_scores['STAR_OR_SKY']['gain_vs_nuisance_bits']:+.3f} bits,
`REL_ENCLOSURE` {axis_scores['REL_ENCLOSURE']['gain_vs_nuisance_bits']:+.3f},
and `WATER_OR_APPARATUS`
{axis_scores['WATER_OR_APPARATUS']['gain_vs_nuisance_bits']:+.3f}.  It loses on
`PLANT` {axis_scores['PLANT']['gain_vs_nuisance_bits']:+.3f}, `REL_PROXIMITY`
{axis_scores['REL_PROXIMITY']['gain_vs_nuisance_bits']:+.3f}, and
`REL_EXPLICIT_ATTACHMENT`
{axis_scores['REL_EXPLICIT_ATTACHMENT']['gain_vs_nuisance_bits']:+.3f}.

This is a fold-safe test of unsupervised formal behavior, but the archived axes
remain postselected, correlated hypothesis-generation outcomes.  A positive
profile would localize a reusable structural class, not a lexical meaning; a
negative result says the tested compiler/neighbor distributions do not improve
on string shape.  No role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned.  f84r was excluded and not
opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT068_PAGE_HOST_BEHAVIOR_PROFILE_RESULT_V1","status":status,"groups":len(src),"annotated_groups":len(parsed),"eligible_loci":len(rows),"physical_folios":len(folds),"axes":axes,"representations":list(REPS),"summary":{r["representation"]:r for r in summary},"leader":lead,"best_behavior":best_behavior,"best_behavior_axis_scores":axis_scores,"selection_disclosure":"Best of three predeclared behavior-profile variants on eight correlated archived axes; no selector penalty or confirmation claim.","interpretation":"Folio-held unsupervised formal PAGE_HOST behavior profiles versus archived hypothesis-generation axes; no supervised semantic clustering.","claim_ceiling":"No role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt059_result.json":sha(ROOT/"gdt059_result.json"),"gdt062_result.json":sha(ROOT/"gdt062_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PROFILES.name:sha(PROFILES),SCORES.name:sha(SCORES),SUMMARY.name:sha(SUMMARY),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"loci":len(rows),"folios":len(folds),"leader":lead,"best_behavior":best_behavior},sort_keys=True))
if __name__=="__main__":main()

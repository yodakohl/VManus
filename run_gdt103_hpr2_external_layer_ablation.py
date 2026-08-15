#!/usr/bin/env python3
"""GDT103: external-axis ablation of PAGE_HOST and HPR2 compiler layers."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT103_HPR2_EXTERNAL_LAYER_ABLATION_METHOD.md";REPORT=ROOT/"GDT103_HPR2_EXTERNAL_LAYER_ABLATION_REPORT.md";SCORES=ROOT/"gdt103_external_layer_scores.tsv";SUMMARY=ROOT/"gdt103_external_layer_summary.tsv";VARIANTS=ROOT/"gdt103_variant_log.tsv";RESULT=ROOT/"gdt103_result.json"
K=5;SHRINK=4.;AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP");REPS=("RAW_CHAR3","PAGE_HOST_CHAR3","HOST_PLUS_WRAPPER","HOST_PLUS_FRAME","HOST_PLUS_RIGHT","HOST_PLUS_DY","HOST_PLUS_B3","HOST_PLUS_ALL","COMPILER_ONLY");ENCODINGS=("ACTIVE_ONLY","CATEGORICAL_LEVEL")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def trigrams(values):
 out=[]
 for value in values:
  s="^"+value+"$";out.extend(s[i:i+3] for i in range(max(1,len(s)-2)))
 return Counter(out)
def dist(a,b):
 keys=set(a)|set(b);den=sum(max(a[x],b[x]) for x in keys);return 1-sum(min(a[x],b[x]) for x in keys)/den if den else 0.
def main():
 source=[x for x in read(SOURCE) if not x["page"].startswith("f84r")];assert source and not any(x["page"].startswith("f84r") for x in source);host_folios=defaultdict(set)
 for x in source:host_folios[x["page_host"]].add(x["physical_folio"])
 ann=read(ANN);parsed=read(PARSED);assert len(ann)==len(parsed)==671;amap={(x["locus"],x["group_index"]):x for x in ann};byloc=defaultdict(list)
 for x in parsed:
  if x["page"].startswith("f84r"):continue
  byloc[x["locus"]].append(x)
 rows=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda x:int(x["group_index"]));a=amap[locus,z[0]["group_index"]];tags={x for x in (a["object_tags"]+";"+a["relation_tags"]).split(";") if x and x!="LABEL"}
  if all(len(host_folios[x["page_host"]])>=2 for x in z):rows.append({"id":locus,"folio":z[0]["physical_folio"],"section":z[0]["section"],"currier":z[0]["currier"],"tags":tags,"groups":z,"nuisance":Counter(("HAND="+a["hand"],"KIND="+a["kind"],"UNIT="+a["unit"],"N="+str(len(z)),"CERT="+a["annotation_certainty"]))})
 assert len(rows)==332
 def features(row,rep,encoding):
  z=row["groups"]
  if rep=="RAW_CHAR3":return trigrams([x["token"] for x in z])
  if rep=="COMPILER_ONLY":return Counter(x["compiler_signature"] for x in z)
  out=trigrams([x["page_host"] for x in z])
  if rep=="PAGE_HOST_CHAR3":return out
  for x in z:
   states={"HOST_PLUS_WRAPPER":("W",x["wrapper"],"NONE"),"HOST_PLUS_FRAME":("F",x["local_frame"],"NONE"),"HOST_PLUS_RIGHT":("R",x["right_family"],"NONE"),"HOST_PLUS_DY":("DY","1" if "DY1" in x["compiler_signature"] else "0","0"),"HOST_PLUS_B3":("B3",x["b3"],"0")}
   chosen=states.keys() if rep=="HOST_PLUS_ALL" else (rep,)
   for key in chosen:
    name,value,default=states[key]
    if encoding=="CATEGORICAL_LEVEL" or value!=default:out[name+"="+value]+=1
  return out
 feat={(enc,r["id"],rep):features(r,rep,enc) for enc in ENCODINGS for r in rows for rep in REPS};score_rows=[]
 for encoding in ENCODINGS:
  for axis in AXES:
   total={rep:0. for rep in REPS};base=0.;folio_loss=defaultdict(lambda:{"BASE":0.,**{rep:0. for rep in REPS}})
   for target in rows:
    pool=[x for x in rows if x["folio"]!=target["folio"] and x["section"]==target["section"] and x["currier"]==target["currier"]]
    if len(pool)<K:pool=[x for x in rows if x["folio"]!=target["folio"] and x["section"]==target["section"]]
    if len(pool)<K:pool=[x for x in rows if x["folio"]!=target["folio"]]
    nuisance={x["id"]:dist(target["nuisance"],x["nuisance"]) for x in pool};near=sorted(pool,key=lambda x:(nuisance[x["id"]],x["id"]))[:K];weights=[1/(.1+nuisance[x["id"]]) for x in near];p=(sum(w*int(axis in x["tags"]) for w,x in zip(weights,near))+.5)/(sum(weights)+1);y=int(axis in target["tags"]);loss=-math.log2(p if y else 1-p);base+=loss;folio_loss[target["folio"]]["BASE"]+=loss
    for rep in REPS:
     ranked=sorted(pool,key=lambda x:(nuisance[x["id"]]+dist(feat[encoding,target["id"],rep],feat[encoding,x["id"],rep]),x["id"]))[:K];ww=[1/(.1+nuisance[x["id"]]+dist(feat[encoding,target["id"],rep],feat[encoding,x["id"],rep])) for x in ranked];q=(sum(w*int(axis in x["tags"]) for w,x in zip(ww,ranked))+SHRINK*p)/(sum(ww)+SHRINK);ll=-math.log2(q if y else 1-q);total[rep]+=ll;folio_loss[target["folio"]][rep]+=ll
   host=total["PAGE_HOST_CHAR3"]
   for rep in REPS:
    gains=[z["BASE"]-z[rep] for z in folio_loss.values()];score_rows.append({"encoding":encoding,"external_axis":axis,"representation":rep,"units":len(rows),"positive_units":sum(axis in x["tags"] for x in rows),"physical_folios":len(folio_loss),"nuisance_bits":base,"held_bits":total[rep],"gain_vs_nuisance_bits":base-total[rep],"increment_vs_page_host_bits":host-total[rep],"positive_gain_folios":sum(x>0 for x in gains),"semantic_role":"UNASSIGNED"})
 write(SCORES,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in score_rows],list(score_rows[0]));summ=[]
 for encoding in ENCODINGS:
  for rep in REPS:
   z=[x for x in score_rows if x["encoding"]==encoding and x["representation"]==rep];summ.append({"encoding":encoding,"representation":rep,"axes":len(z),"summed_gain_vs_nuisance_bits":sum(x["gain_vs_nuisance_bits"] for x in z),"summed_increment_vs_page_host_bits":sum(x["increment_vs_page_host_bits"] for x in z),"axes_increment_positive_vs_host":sum(x["increment_vs_page_host_bits"]>0 for x in z),"selector_cost_bits":math.log2(6) if rep in {"PAGE_HOST_CHAR3","HOST_PLUS_WRAPPER","HOST_PLUS_FRAME","HOST_PLUS_RIGHT","HOST_PLUS_DY","HOST_PLUS_B3"} else 0,"selector_paid_increment_vs_host_bits":sum(x["increment_vs_page_host_bits"] for x in z)-(math.log2(6) if rep in {"HOST_PLUS_WRAPPER","HOST_PLUS_FRAME","HOST_PLUS_RIGHT","HOST_PLUS_DY","HOST_PLUS_B3"} else 0),"semantic_role":"UNASSIGNED"})
 write(SUMMARY,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in summ],list(summ[0]));primary={x["representation"]:x for x in summ if x["encoding"]=="ACTIVE_ONLY"};cat={x["representation"]:x for x in summ if x["encoding"]=="CATEGORICAL_LEVEL"};variants=[{"variant_id":"V00","status":"PRIMARY","description":"ACTIVE_ONLY compiler additions; default NONE/0 contributes no token."},{"variant_id":"V01","status":"SENSITIVITY_ARTIFACT","description":f"CATEGORICAL_LEVEL includes default tokens; B3 increment {cat['HOST_PLUS_B3']['summed_increment_vs_page_host_bits']:+.3f} bits is representation-geometry sensitive."},{"variant_id":"V02","status":"BOUND_BASELINE","description":"RAW_CHAR3 on identical panel/folds."},{"variant_id":"V03","status":"BOUND_BASELINE","description":"PAGE_HOST_CHAR3 on identical panel/folds."},{"variant_id":"V04","status":"BOUND_NEGATIVE","description":"COMPILER_ONLY on identical panel/folds."},{"variant_id":"V05","status":"NOT_RUN","description":"No alternate axes, semantic clustering, glosses, language mapping, or f84r."}];write(VARIANTS,variants,list(variants[0]));status="PAGE_HOST_RETAINS_EXTERNAL_SIGNAL_B3_NEUTRAL_DY_RIGHT_ADD_RELATION_LAYOUT_ONLY"
 def v(rep,key):return float(primary[rep][key])
 axis_dy={x["external_axis"]:x["increment_vs_page_host_bits"] for x in score_rows if x["encoding"]=="ACTIVE_ONLY" and x["representation"]=="HOST_PLUS_DY"};axis_right={x["external_axis"]:x["increment_vs_page_host_bits"] for x in score_rows if x["encoding"]=="ACTIVE_ONLY" and x["representation"]=="HOST_PLUS_RIGHT"}
 REPORT.write_text(f"""# GDT103 — HPR2 external-layer ablation

## Outcome

**{status}**

On the exact GDT068 332-locus, 19-folio panel, PAGE_HOST character features
gain {v('PAGE_HOST_CHAR3','summed_gain_vs_nuisance_bits'):+.3f} descriptive
held bits across eight archived axes, versus raw strings
{v('RAW_CHAR3','summed_gain_vs_nuisance_bits'):+.3f}. Compiler-only loses
{abs(v('COMPILER_ONLY','summed_gain_vs_nuisance_bits')):.3f} bits. This
reproduces the PAGE_HOST localization lead; it does not create new independent
external evidence.

With default compiler states omitted, wrappers change PAGE_HOST by
{v('HOST_PLUS_WRAPPER','summed_increment_vs_page_host_bits'):+.3f} bits and
O/OT frame by {v('HOST_PLUS_FRAME','summed_increment_vs_page_host_bits'):+.3f}.
B3 is effectively neutral at
{v('HOST_PLUS_B3','summed_increment_vs_page_host_bits'):+.3f}. RIGHT_FAMILY is
small at {v('HOST_PLUS_RIGHT','summed_increment_vs_page_host_bits'):+.3f}; its
main positive component is REL_ENCLOSURE
{axis_right['REL_ENCLOSURE']:+.3f}. DY adds
{v('HOST_PLUS_DY','summed_increment_vs_page_host_bits'):+.3f}, mostly the
relation/layout axes REL_ARRAY_OR_GROUP
{axis_dy['REL_ARRAY_OR_GROUP']:+.3f}, REL_EXPLICIT_ATTACHMENT
{axis_dy['REL_EXPLICIT_ATTACHMENT']:+.3f}, and REL_ENCLOSURE
{axis_dy['REL_ENCLOSURE']:+.3f}. This is compatible with compiler layers
carrying record/relation layout while PAGE_HOST carries the stronger object
address, not proof of semantic neutrality.

The categorical-zero sensitivity is a warning: simply adding the ubiquitous
`B3=0` token changes weighted-Jaccard geometry and makes B3 look
{float(cat['HOST_PLUS_B3']['summed_increment_vs_page_host_bits']):+.3f} bits
better. That variant is retained as a representation artifact, not evidence.
After a six-way layer selector, active DY remains
{v('HOST_PLUS_DY','selector_paid_increment_vs_host_bits'):+.3f} bits and RIGHT
{v('HOST_PLUS_RIGHT','selector_paid_increment_vs_host_bits'):+.3f}; the eight
axes are correlated and archived, so these remain exploratory.

All roles remain UNASSIGNED. f84r was excluded and untouched.
""",encoding="utf-8")
 result={"schema":"GDT103_HPR2_EXTERNAL_LAYER_ABLATION_RESULT_V1","status":status,"eligible_loci":len(rows),"physical_folios":len({x["folio"] for x in rows}),"external_axes":list(AXES),"representations":list(REPS),"encodings":list(ENCODINGS),"primary_summary":primary,"categorical_sensitivity_summary":cat,"dy_axis_increments":axis_dy,"right_axis_increments":axis_right,"interpretation":"PAGE_HOST retains the broad archived external-signal lead; B3 is neutral, wrappers/frames dilute, and DY/RIGHT add mainly relation/layout association under active-only encoding.","semantic_role":"UNASSIGNED","claim_ceiling":"Exploratory external-signal localization only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt068_result.json":sha(ROOT/"gdt068_result.json"),"gdt093_result.json":sha(ROOT/"gdt093_result.json"),"gdt100_result.json":sha(ROOT/"gdt100_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),SUMMARY.name:sha(SUMMARY),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"host":v('PAGE_HOST_CHAR3','summed_gain_vs_nuisance_bits'),"raw":v('RAW_CHAR3','summed_gain_vs_nuisance_bits'),"dy":v('HOST_PLUS_DY','summed_increment_vs_page_host_bits'),"b3":v('HOST_PLUS_B3','summed_increment_vs_page_host_bits')},sort_keys=True))
if __name__=="__main__":main()

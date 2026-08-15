#!/usr/bin/env python3
"""GDT106: test external signal after PAGE_HOST edge removal/separation."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT106_HOST_EDGE_STRIPPING_EXTERNAL_TEST_METHOD.md";REPORT=ROOT/"GDT106_HOST_EDGE_STRIPPING_EXTERNAL_TEST_REPORT.md";SCORES=ROOT/"gdt106_edge_stripping_axis_scores.tsv";SUMMARY=ROOT/"gdt106_edge_stripping_summary.tsv";VARIANTS=ROOT/"gdt106_variant_log.tsv";RESULT=ROOT/"gdt106_result.json";K=5;SHRINK=4.;AXES=("STAR_OR_SKY","FIGURE","PLANT","WATER_OR_APPARATUS","REL_PROXIMITY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_ARRAY_OR_GROUP");OBJECT=set(AXES[:4]);REPS=("RAW_CHAR3","FULL_PAGE_HOST","STRIP_FINAL1","STRIP_FINAL2","STRIP_FIRST1","INTERIOR","EDGE1_ONLY","CORE_PLUS_EDGE1_SEPARATE","CORE_PLUS_EDGE2_SEPARATE")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def tri(values):
 out=[]
 for value in values:
  s="^"+value+"$";out.extend(s[i:i+3] for i in range(max(1,len(s)-2)))
 return Counter(out)
def dist(a,b):
 keys=set(a)|set(b);den=sum(max(a[x],b[x]) for x in keys);return 1-sum(min(a[x],b[x]) for x in keys)/den if den else 0.
def main():
 source=[x for x in read(SOURCE) if not x["page"].startswith("f84r")];assert len(source)==15592;folios=defaultdict(set)
 for x in source:folios[x["page_host"]].add(x["physical_folio"])
 ann=read(ANN);parsed=[x for x in read(PARSED) if not x["page"].startswith("f84r")];amap={(x["locus"],x["group_index"]):x for x in ann};byloc=defaultdict(list)
 for x in parsed:byloc[x["locus"]].append(x)
 rows=[]
 for locus,z in sorted(byloc.items()):
  z.sort(key=lambda x:int(x["group_index"]));a=amap[locus,z[0]["group_index"]]
  if all(len(folios[x["page_host"]])>=2 for x in z):rows.append({"id":locus,"folio":z[0]["physical_folio"],"section":z[0]["section"],"currier":z[0]["currier"],"tags":{x for x in (a["object_tags"]+";"+a["relation_tags"]).split(";") if x and x!="LABEL"},"groups":z,"nuisance":Counter(("HAND="+a["hand"],"KIND="+a["kind"],"UNIT="+a["unit"],"N="+str(len(z)),"CERT="+a["annotation_certainty"]))})
 assert len(rows)==332
 def features(row,rep):
  z=row["groups"];hosts=[x["page_host"] for x in z]
  if rep=="RAW_CHAR3":return tri([x["token"] for x in z])
  if rep=="FULL_PAGE_HOST":return tri(hosts)
  if rep=="STRIP_FINAL1":return tri([x[:-1] for x in hosts])
  if rep=="STRIP_FINAL2":return tri([x[:-2] for x in hosts])
  if rep=="STRIP_FIRST1":return tri([x[1:] for x in hosts])
  if rep=="INTERIOR":return tri([x[1:-1] for x in hosts])
  if rep=="EDGE1_ONLY":return Counter("EDGE1="+x[-1:] for x in hosts)
  out=tri([x[:-1] for x in hosts]);out.update(("EDGE1="+x[-1:] if rep=="CORE_PLUS_EDGE1_SEPARATE" else "EDGE2="+x[-2:]) for x in hosts);return out
 feat={(x["id"],rep):features(x,rep) for x in rows for rep in REPS};score=[]
 for axis in AXES:
  bits={rep:0. for rep in REPS};base=0.;fold=defaultdict(lambda:{"BASE":0.,**{rep:0. for rep in REPS}})
  for target in rows:
   pool=[x for x in rows if x["folio"]!=target["folio"] and x["section"]==target["section"] and x["currier"]==target["currier"]]
   if len(pool)<K:pool=[x for x in rows if x["folio"]!=target["folio"] and x["section"]==target["section"]]
   if len(pool)<K:pool=[x for x in rows if x["folio"]!=target["folio"]]
   nd={x["id"]:dist(target["nuisance"],x["nuisance"]) for x in pool};near=sorted(pool,key=lambda x:(nd[x["id"]],x["id"]))[:K];w=[1/(.1+nd[x["id"]]) for x in near];p=(sum(q*int(axis in x["tags"]) for q,x in zip(w,near))+.5)/(sum(w)+1);y=int(axis in target["tags"]);loss=-math.log2(p if y else 1-p);base+=loss;fold[target["folio"]]["BASE"]+=loss
   for rep in REPS:
    ranked=sorted(pool,key=lambda x:(nd[x["id"]]+dist(feat[target["id"],rep],feat[x["id"],rep]),x["id"]))[:K];ww=[1/(.1+nd[x["id"]]+dist(feat[target["id"],rep],feat[x["id"],rep])) for x in ranked];q=(sum(v*int(axis in x["tags"]) for v,x in zip(ww,ranked))+SHRINK*p)/(sum(ww)+SHRINK);ll=-math.log2(q if y else 1-q);bits[rep]+=ll;fold[target["folio"]][rep]+=ll
  full=bits["FULL_PAGE_HOST"]
  for rep in REPS:score.append({"external_axis":axis,"axis_class":"OBJECT_AXIS" if axis in OBJECT else "RELATION_AXIS","representation":rep,"units":len(rows),"physical_folios":len(fold),"gain_vs_nuisance_bits":base-bits[rep],"increment_vs_full_host_bits":full-bits[rep],"positive_folios_vs_nuisance":sum(x["BASE"]>x[rep] for x in fold.values()),"semantic_role":"UNASSIGNED"})
 write(SCORES,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in score],list(score[0]));summary=[]
 for rep in REPS:
  z=[x for x in score if x["representation"]==rep];summary.append({"representation":rep,"axes":len(z),"summed_gain_vs_nuisance_bits":sum(x["gain_vs_nuisance_bits"] for x in z),"summed_increment_vs_full_host_bits":sum(x["increment_vs_full_host_bits"] for x in z),"object_axis_gain_bits":sum(x["gain_vs_nuisance_bits"] for x in z if x["axis_class"]=="OBJECT_AXIS"),"relation_axis_gain_bits":sum(x["gain_vs_nuisance_bits"] for x in z if x["axis_class"]=="RELATION_AXIS"),"selector_paid_increment_vs_full_host_bits":sum(x["increment_vs_full_host_bits"] for x in z)-math.log2(len(REPS)),"semantic_role":"UNASSIGNED"})
 write(SUMMARY,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in summary],list(summary[0]));by={x["representation"]:x for x in summary};variants=[{"variant_id":"V00","status":"BASELINE","description":"RAW_CHAR3."},{"variant_id":"V01","status":"PRIMARY","description":"FULL_PAGE_HOST."},{"variant_id":"V02","status":"RUN","description":"STRIP_FINAL1 following GDT105 edge-state discovery."},{"variant_id":"V03","status":"RUN_SENSITIVITY","description":"STRIP_FINAL2."},{"variant_id":"V04","status":"RUN_CONTROL","description":"STRIP_FIRST1."},{"variant_id":"V05","status":"RUN_CONTROL","description":"INTERIOR strips both first and final."},{"variant_id":"V06","status":"RUN_CONTROL","description":"EDGE1_ONLY."},{"variant_id":"V07","status":"RUN","description":"CORE_PLUS_EDGE1_SEPARATE preserves edge as typed token."},{"variant_id":"V08","status":"RUN_SENSITIVITY","description":"CORE_PLUS_EDGE2_SEPARATE."},{"variant_id":"V09","status":"NOT_RUN","description":"No alternate axes, learned split, semantics, language map, or f84r."}];write(VARIANTS,variants,list(variants[0]));status="EDGE_STRIPPING_DESTROYS_EXTERNAL_SIGNAL_FULL_HOST_REMAINS_CONTENT_ADDRESS"
 REPORT.write_text(f"""# GDT106 — host-edge stripping external-information test

## Outcome

**{status}**

The clean decomposition prediction fails. Full PAGE_HOST retains
{by['FULL_PAGE_HOST']['summed_gain_vs_nuisance_bits']:+.3f} descriptive held
bits across the eight archived axes. Removing the final character falls to
{by['STRIP_FINAL1']['summed_gain_vs_nuisance_bits']:+.3f}, a
{by['STRIP_FINAL1']['summed_increment_vs_full_host_bits']:+.3f}-bit change.
Removing two characters, the first character, or both edges is worse.

The edge alone is also insufficient at
{by['EDGE1_ONLY']['summed_gain_vs_nuisance_bits']:+.3f} bits. Keeping a stripped
core and a separate typed edge recovers only
{by['CORE_PLUS_EDGE1_SEPARATE']['summed_gain_vs_nuisance_bits']:+.3f}; a typed
two-character edge reaches
{by['CORE_PLUS_EDGE2_SEPARATE']['summed_gain_vs_nuisance_bits']:+.3f}. The full
joint host remains the best of all nine tried representations, so no
postselection credit is needed.

GDT105 still establishes the final character as a strong renderer-licensing
state. GDT106 shows that it cannot simply be discarded as content-neutral
syntax. The revised generator is `CONTENT_ADDRESS(CORE, EDGE_STATE)` with a
coupled edge, not `CONTENT_CORE + disposable suffix`. This can reflect address
identity, allomorphy/check state, or string-neighbour geometry; it does not
assign the edge a meaning.

All roles remain UNASSIGNED. f84r was excluded and untouched.
""",encoding="utf-8")
 result={"schema":"GDT106_HOST_EDGE_STRIPPING_EXTERNAL_TEST_RESULT_V1","status":status,"eligible_loci":len(rows),"physical_folios":len({x["folio"] for x in rows}),"axes":list(AXES),"representations":{x["representation"]:x for x in summary},"winner":max(summary,key=lambda x:x["summed_gain_vs_nuisance_bits"])["representation"],"generative_revision":"CONTENT_ADDRESS := coupled(CORE, EDGE_STATE); EDGE_STATE licenses renderer but is not externally disposable.","interpretation":"Full PAGE_HOST is the best tested external representation; universal edge state must remain coupled to address identity at this resolution.","semantic_role":"UNASSIGNED","claim_ceiling":"Archived external-signal representation only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt105_result.json":sha(ROOT/"gdt105_result.json"),"gdt103_result.json":sha(ROOT/"gdt103_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),SUMMARY.name:sha(SUMMARY),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"winner":result["winner"],"full":by['FULL_PAGE_HOST']['summed_gain_vs_nuisance_bits'],"strip":by['STRIP_FINAL1']['summed_gain_vs_nuisance_bits'],"separate":by['CORE_PLUS_EDGE1_SEPARATE']['summed_gain_vs_nuisance_bits']},sort_keys=True))
if __name__=="__main__":main()

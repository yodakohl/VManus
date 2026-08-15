#!/usr/bin/env python3
"""Independent core-score and artifact validation for GDT136."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt062_right_family_inventory.tsv";PROSE=ROOT/"gdt016_group_state_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";TARGETS=ROOT/"gdt109_target_inventory.tsv";MANIFEST=ROOT/"gdt095_descriptor_token_manifest.tsv";SCORES=ROOT/"gdt136_representation_scores.tsv";FOLDS=ROOT/"gdt136_folio_scores.tsv";NULL=ROOT/"gdt136_null_results.tsv";RESULT=ROOT/"gdt136_result.json";OUT=ROOT/"gdt136_validation.json"
PFX=("che","ch","sh","t","s","d","q");RIGHT=("aiin","air","ain","ar","al");REPS=("BEHAVIOR_SELF_NEIGHBOR_NOPOS","PAGE_HOST_CHAR3","RAW_CHAR3");STOP=set("a an and are as at be been being but by for from has have in into is it its label labels labeled near next no not of on or page panel plant plants row since that the their them there these they this to under used was we were with word words kluge kluges petersen petersens grove groves latham perhaps seems likely associated actually between east west north south left right above below top bottom middle mid height side first second third fourth fifth sixth one two three four five six seven eight nine ten".split())

def read(p):
 with Path(p).open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def dtoken(text):
 text=text.split("||",1)[-1].lower();text=re.sub(r"<[^>]*>|&[^;]*;|\bf\d+[rv]\w*\b"," ",text);out=[]
 for word in re.findall(r"[a-z]+",text):
  if word in STOP or len(word)<3:continue
  if word.endswith("ies")and len(word)>4:word=word[:-3]+"y"
  elif word.endswith("ves")and len(word)>4:word=word[:-3]+"f"
  elif word.endswith("s")and len(word)>4:word=word[:-1]
  if word not in STOP:out.append(word)
 return set(out)
def strip(token):
 w="NONE";h=token
 for p in PFX:
  if h.startswith(p)and len(h)>len(p):w=p;h=h[len(p):];break
 dy=int(h.endswith("dy")and len(h)>2)
 if dy:h=h[:-2]
 return w,h,dy
def prep(w,h):
 b=int(h.endswith("m")and len(h)>1)
 if b:h=h[:-1]
 right="NONE"
 for s in RIGHT:
  if h.endswith(s)and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(w in {"ch","che","sh"}and h.startswith("d")and len(h)>1)
 if inner:h=h[1:]
 return h,b,right,inner
def parse(token,licensed):
 w,h,dy=strip(token);h,b,right,inner=prep(w,h);frame="NONE"
 if h.startswith("ot")and h[2:]in licensed:h=h[2:];frame="OT"
 elif h.startswith("o")and h[1:]in licensed:h=h[1:];frame="O"
 return {"token":token,"host":h or"EMPTY","w":w,"dy":dy,"b":b,"right":right,"inner":inner,"frame":frame}
def char3(counter,value):
 s="^"+value+"$"
 for i in range(max(1,len(s)-2)):counter[s[i:i+3]]+=1
def avg(items):
 out=Counter()
 for item in items:
  for k,v in item.items():out[k]+=v/len(items)
 return out
def dist(a,b):
 keys=set(a)|set(b);den=sum(max(a[k],b[k])for k in keys)
 return 1-sum(min(a[k],b[k])for k in keys)/den if den else 1
def losses(y,p):
 p=np.clip(p,1e-12,1-1e-12);return-np.log2(np.where(y>0,p,1-p))

checks=[]
def check(name,value):checks.append({"check":name,"pass":bool(value)});assert value,name
result=json.loads(RESULT.read_text());check("status",result["status"]=="BEHAVIOR_PROFILE_LEGACY_TRANSFER_NOT_SUPPORTED")
prose=[r for r in read(PROSE)if not r["page"].startswith("f84")];cc=Counter()
for r in prose:h,*_=prep(r["stripped_prefix"],r["residual_host"]);cc[h]+=1
licensed={h for h in cc if cc[h]and cc["o"+h]and cc["ot"+h]}|{"ar","al","ol"}
source=[r for r in read(SOURCE)if not r["page"].startswith("f84")];check("source_no_f84",len(source)==15364 and not any(r["page"].startswith("f84")for r in source))
byline=defaultdict(list);hostfolios=defaultdict(set)
for r in source:byline[r["locus"]].append(r);hostfolios[r["page_host"]].add(r["physical_folio"])
events=[]
for line in byline.values():
 line.sort(key=lambda r:int(r["group_index"]))
 for i,r in enumerate(line):
  a=line[i-1]if i else None;b=line[i+1]if i+1<len(line)else None
  tokens=["W="+r["wrapper"],"D="+r["inner_d"],"F="+r["local_frame"],"R="+r["right_family"],"DY="+r["dy_closure"],"B3="+r["b3"],"PW="+(a["wrapper"]if a else"BOS"),"PF="+(a["local_frame"]if a else"BOS"),"PDY="+(a["dy_closure"]if a else"BOS"),"NW="+(b["wrapper"]if b else"EOS"),"NF="+(b["local_frame"]if b else"EOS"),"NDY="+(b["dy_closure"]if b else"EOS")]
  events.append((r["physical_folio"],r["page_host"],tokens))
profile_cache={}
def profiles(folio):
 if folio not in profile_cache:
  z=defaultdict(lambda:[Counter(),0])
  for f,h,t in events:
   if f==folio:continue
   z[h][0].update(t);z[h][1]+=1
  profile_cache[folio]={h:Counter({k:v/n for k,v in c.items()})for h,(c,n)in z.items()}
 return profile_cache[folio]

targets=read(TARGETS);vocab=[r["descriptor_token"]for r in read(MANIFEST)];check("target_and_vocab",len(targets)==44 and len(vocab)==19 and not any(r["page"].startswith("f84")for r in targets))
y=np.array([[int(t in set(r["descriptor_tokens"].split(";")))for t in vocab]for r in targets],float);folios=sorted({r["physical_folio"]for r in targets});findex={f:np.array([i for i,r in enumerate(targets)if r["physical_folio"]==f],int)for f in folios}
annotations=read(ANN);parsed=read(PARSED);grouped=defaultdict(list)
for a,p in zip(annotations,parsed):
 check("join_"+a["locus"]+"_"+a["group_index"],a["locus"]==p["locus"]and a["group_index"]==p["group_index"])
 if a["kind"]=="L"and a["annotation_certainty"]=="UNHEDGED"and a["section"]=="P"and"PLANT"in a["object_tags"].split(";"):grouped[a["locus"]].append((a,p))
check("training_loci",len(grouped)==83)
training={}
for folio in folios:
 pf=profiles(folio);z=[]
 for locus,pairs in sorted(grouped.items()):
  pairs.sort(key=lambda q:int(q[0]["group_index"]))
  if not all(p["page_host"]in pf and len(hostfolios[p["page_host"]]-{folio})>=1 for _,p in pairs):continue
  feat={r:Counter()for r in REPS}
  for a,p in pairs:feat[REPS[0]].update(pf[p["page_host"]]);char3(feat[REPS[1]],p["page_host"]);char3(feat[REPS[2]],a["token"])
  z.append((locus,dtoken(pairs[0][0]["raw_source_description"]),feat))
 training[folio]=z
check("training_fold_counts",{f:len(z)for f,z in training.items()}==result["training_loci_by_target_fold"])

edition_features=[]
for row in targets:
 pf=profiles(row["physical_folio"]);ed=[]
 for col in("zl3b_forms","it2a_forms","rf1b_forms"):
  items=[parse(t,licensed)for t in row[col].split("|")];feat={r:Counter()for r in REPS}
  for item in items:feat[REPS[0]].update(pf.get(item["host"],Counter()));char3(feat[REPS[1]],item["host"]);char3(feat[REPS[2]],item["token"])
  ed.append((all(len(hostfolios[x["host"]]-{row["physical_folio"]})>=1 for x in items),all(len(hostfolios[x["host"]]-{row["physical_folio"]})>=2 for x in items),feat))
 edition_features.append(ed)
primary_idx=np.array([i for i,z in enumerate(edition_features)if any(x[0]for x in z)],int);strong_idx=np.array([i for i,z in enumerate(edition_features)if any(x[1]for x in z)],int);all3_idx=np.array([i for i,z in enumerate(edition_features)if all(x[0]for x in z)],int)
check("scope_counts",(len(primary_idx),len(strong_idx),len(all3_idx))==(31,27,15))
base=np.zeros_like(y);features={};strong_features={};all3_features={}
for i,row in enumerate(targets):
 tr=training[row["physical_folio"]]
 for j,t in enumerate(vocab):base[i,j]=(sum(t in z[1]for z in tr)+.5)/(len(tr)+1)
 z=edition_features[i];chosen=[x[2]for x in z if x[0]];chosen2=[x[2]for x in z if x[1]]
 if chosen:features[i]={rep:avg([q[rep]for q in chosen])for rep in REPS}
 if chosen2:strong_features[i]={rep:avg([q[rep]for q in chosen2])for rep in REPS}
 if all(x[0]for x in z):all3_features[i]={rep:avg([x[2][rep]for x in z])for rep in REPS}
def predict(indexes,target_features):
 out={rep:base.copy()for rep in REPS}
 for rep in REPS:
  for i in indexes:
   train=training[targets[i]["physical_folio"]];cand=[]
   for locus,toks,feat in train:
    d=dist(target_features[i][rep],feat[rep])
    if d<1-1e-12:cand.append((d,locus,toks))
   cand.sort();near=cand[:5];weights=np.array([1/(.1+x[0])for x in near]);den=weights.sum()+4;pred=4*base[i]/den
   for w,(_,_,toks)in zip(weights,near):pred+=w*np.array([int(t in toks)for t in vocab])/den
   out[rep][i]=pred
 return out
pred=predict(primary_idx,features);strong_pred=predict(strong_idx,strong_features);all3_pred=predict(all3_idx,all3_features);bl=losses(y,base)
rebuild={}
for rep in REPS:
 ml=losses(y,pred[rep]);gain=float((bl[primary_idx]-ml[primary_idx]).sum());fg=[]
 for f in folios:
  idx=np.intersect1d(primary_idx,findex[f]);fg.append(float((bl[idx]-ml[idx]).sum()))
 rebuild[rep]=(gain,sum(v>0 for v in fg),fg)
 stored=result["primary"][rep];check("gain_"+rep,abs(gain-float(stored["gain_bits"]))<1e-9 and sum(v>0 for v in fg)==int(stored["positive_gain_folios"]))
sg=float((bl[strong_idx]-losses(y,strong_pred[REPS[0]])[strong_idx]).sum());check("stronger_gain",abs(sg-float(result["two_outside_folio_behavior"]["gain_bits"]))<1e-9)
ag=float((bl[all3_idx]-losses(y,all3_pred[REPS[2]])[all3_idx]).sum());check("all3_raw",abs(ag-float(result["all_readings_raw"]["gain_bits"]))<1e-9)

# Reproduce the primary all-19 exact shared permutation diagnostic.
observed={rep:rebuild[rep][0]for rep in REPS};local=Counter();maximum=0;rng=np.random.default_rng(136001)
for _ in range(10000):
 perm=y.copy()
 for idx in findex.values():perm[idx]=perm[rng.permutation(idx)]
 pb=losses(perm,base);g={}
 for rep in REPS:g[rep]=float((pb[primary_idx]-losses(perm,pred[rep])[primary_idx]).sum());local[rep]+=g[rep]>=observed[rep]-1e-12
 maximum+=max(g.values())>=max(observed.values())-1e-12
for rep in REPS:
 stored=result["primary"][rep];check("null_"+rep,abs((local[rep]+1)/10001-float(stored["local_permutation_p"]))<1e-12 and abs((maximum+1)/10001-float(stored["max_three_p"]))<1e-12)

score_rows=read(SCORES);fold_rows=read(FOLDS);null_rows=read(NULL);check("row_counts",len(score_rows)==36 and len(null_rows)==36)
for row in score_rows:
 check("arithmetic_"+row["scope"]+row["endpoint_panel"]+row["representation"],abs(float(row["baseline_bits"])-float(row["held_bits"])-float(row["gain_bits"]))<2e-9)
 matching=[x for x in fold_rows if x["scope"]==row["scope"]and x["endpoint_panel"]==row["endpoint_panel"]and x["representation"]==row["representation"]]
 check("fold_sum_"+row["scope"]+row["endpoint_panel"]+row["representation"],abs(sum(float(x["gain_bits"])for x in matching)-float(row["gain_bits"]))<2e-9)
check("gates",result["gates"]=={"beats_page_host":False,"beats_raw":False,"max_three_p_le_005":True,"positive_at_least_4_of_6_folios":False,"selector_paid_positive":False,"two_outside_folio_sensitivity_positive":False})
check("input_hashes",all(sha(ROOT/name)==digest for name,digest in result["inputs"].items()))
check("implementation_hashes",all(sha(ROOT/name)==digest for name,digest in result["implementation"].items()))
check("output_hashes",all(sha(ROOT/name)==digest for name,digest in result["outputs"].items()))
check("document_hashes",all(sha(ROOT/name)==digest for name,digest in result["documents"].items()))
content=dict(result);digest=content.pop("result_content_sha256");check("content_hash",csha(content)==digest)
validation={"schema":"GDT136_VALIDATION_V1","status":"PASS_INDEPENDENT_CORE_REFIT_AND_NULL","checks":len(checks),"passed":sum(x["pass"]for x in checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"check_rows":checks}
OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":validation["status"],"checks":validation["checks"]},sort_keys=True))

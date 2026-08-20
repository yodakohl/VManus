#!/usr/bin/env python3
"""Run the frozen comparator-only GDT385 parent-link calibration."""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence";ART=BASE/"artifacts"
ENC=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz"
ORACLE=ROOT/"gdt176_corema_role_oracle.tsv";FREEZE=ART/"gdt385_pre_score_freeze.json"
ROUTES={
 "CMP_PARENT_01":lambda r:r["role"]=="REF",
 "CMP_PARENT_02":lambda r:r["role"]=="TIME",
 "CMP_PARENT_03":lambda r:r["role"]=="ALTERNATIVE",
 "CMP_PARENT_04":lambda r:r["annotation_flags"]=="exclusion",
}
REPS=["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN"]
FORBIDDEN=("semantic","oracle","concept","role","parent","english","label","instruction")
K=14

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def readgz(p):
 with gzip.open(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def writegz(p,rows):
 raw=p.open("wb");gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0);f=io.TextIOWrapper(gz,encoding="utf-8",newline="")
 with f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sigmoid(x):x=np.clip(np.asarray(x,float),-30,30);return 1/(1+np.exp(-x))
def logit(x):x=np.clip(np.asarray(x,float),1e-7,1-1e-7);return np.log(x/(1-x))
def rankdata(x):
 a=np.asarray(x,float);o=np.argsort(a,kind="stable");z=np.empty(len(a),float);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[o[j]]==a[o[i]]:j+=1
  z[o[i:j]]=(i+j+1)/2;i=j
 return z
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1
 if not n1 or not n0:return float("nan")
 q=rankdata(s);return float((q[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bits_binary(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-12,1-1e-12);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def bits_multi(y,p):
 y=np.asarray(y,int);return float(-np.log2(np.clip(p[np.arange(len(y)),y],1e-15,1)).sum())
def binint(v,cuts):
 v=int(v)
 for i,c in enumerate(cuts):
  if v<=c:return str(i)
 return str(len(cuts))
def combine(ps):return sigmoid(np.median(np.vstack([logit(p) for p in ps]),axis=0))
def combine2(a,b):return sigmoid((logit(a)+logit(b))/2)

def prepare(rows):
 byrec=defaultdict(list)
 for i,r in enumerate(rows):byrec[r["record_id"]].append(i)
 rep={k:[None]*len(rows) for k in REPS};channels=[None]*len(rows);strata=[None]*len(rows)
 for ids in byrec.values():
  ids.sort(key=lambda i:int(rows[i]["element_ordinal"]))
  for j,i in enumerate(ids):
   r=rows[i];span=[rows[x] for x in ids[max(0,j-2):j]]+[r];g=r["rendered_group"]
   rep["HOST_IDENTITY"][i]=("H="+r["host_id"],"HL="+str(len(r["host_id"])))
   rep["COMPLETE_RENDERED_GROUP"][i]=("G="+g,"GP="+g[:2],"GS="+g[-2:],"GL="+str(len(g)))
   rep["CONSTRUCTION_STATE"][i]=("W="+r["wrapper_state"],"P="+r["positional_state"],"B="+r["boundary_state"],"R="+r["record_state"],"V="+r["renderer_variant"],"WF="+r["within_field_index"])
   rep["COMPOSITE_JOINT_STATE"][i]=("J="+r["composite_joint_id"],)
   rep["SHORT_CONSTRUCTION_SPAN"][i]=("SS="+"|".join(x["wrapper_state"]+x["boundary_state"]+x["renderer_variant"] for x in span),"SH="+"|".join(x["host_id"] for x in span))
   rb=binint(r["within_record_frequency"],[1,2,4]);rl=binint(r["record_element_count"],[8,16,32,64]);fi=binint(r["field_index"],[0,1,2,4,8]);wi=binint(r["within_field_index"],[0,1,2,4,8])
   channels[i]=("C="+rb,"FI="+r["field_index"],"WF="+r["within_field_index"],"P="+r["positional_state"],"B="+r["boundary_state"],"PREV="+r["previous_host"],"RL="+rl)
   strata[i]=(r["positional_state"],r["boundary_state"],fi,wi,rl,rb)
 return rep,channels,strata

def nb_crossfit(y,features,folds):
 y=np.asarray(y,int);pred=np.zeros(len(y));tc=Counter(y);hc=Counter();tot=Counter();held=Counter();tv=Counter();hv=Counter();voc=defaultdict(set);groups=defaultdict(list)
 for i,f in enumerate(folds):
  groups[f].append(i);hc[(f,y[i])]+=1
  for k,v in enumerate(features[i]):tot[(y[i],k,v)]+=1;held[(f,y[i],k,v)]+=1;tv[(k,v)]+=1;hv[(f,k,v)]+=1;voc[k].add(v)
 for f,test in groups.items():
  n1=tc[1]-hc[(f,1)];n0=tc[0]-hc[(f,0)];prior=math.log((n1+1)/(n0+1));vs=[len(voc[k])-sum(hv[(f,k,v)]==tv[(k,v)] for v in voc[k] if hv[(f,k,v)])+1 for k in range(len(features[0]))]
  for i in test:
   z=prior
   for k,v in enumerate(features[i]):z+=math.log((tot[(1,k,v)]-held[(f,1,k,v)]+1)/(n1+vs[k]))-math.log((tot[(0,k,v)]-held[(f,0,k,v)]+1)/(n0+vs[k]))
   pred[i]=float(sigmoid(z))
 return pred

def nb_crossfit_frequency(y,features,folds,tokens):
 """Collection-held NB with opaque frequency bins learned on training only."""
 y=np.asarray(y,int);pred=np.zeros(len(y));groups=defaultdict(list)
 for i,f in enumerate(folds):groups[f].append(i)
 for held,test in groups.items():
  train=[i for i,f in enumerate(folds) if f!=held];gf=Counter(tokens[i] for i in train)
  def feat(i):return ("F="+binint(gf[tokens[i]],[1,2,4,8,16,32,64]),)+tuple(features[i])
  ff={i:feat(i) for i in train+test};tc=Counter(y[i] for i in train);tot=Counter();voc=defaultdict(set)
  for i in train:
   for k,v in enumerate(ff[i]):tot[(y[i],k,v)]+=1;voc[k].add(v)
  n1=tc[1];n0=tc[0];prior=math.log((n1+1)/(n0+1));vs=[len(voc[k])+1 for k in range(len(ff[train[0]]))]
  for i in test:
   z=prior
   for k,v in enumerate(ff[i]):z+=math.log((tot[(1,k,v)]+1)/(n1+vs[k]))-math.log((tot[(0,k,v)]+1)/(n0+vs[k]))
   pred[i]=float(sigmoid(z))
 return pred

def build_outcome(rows,oracle):
 keys={r["element_key"] for r in rows};by=defaultdict(list)
 for r in oracle:by[(r["collection_id"],r["recipe_id"])].append(r)
 out={};target={};invalid=[]
 for (c,rec),rr in by.items():
  rr.sort(key=lambda r:int(r["element_ordinal"]));ins=[r for r in rr if r["role"]=="INSTRUCTION"]
  for r in rr:
   k=f"COREMA:{c}:{rec}:{r['element_ordinal']}"
   if k not in keys or int(r["element_ordinal"])<=1:continue
   p=int(r["parent_instruction_ordinal"])
   if not p:out[k]=0;target[k]="NONE";continue
   if p>len(ins):invalid.append(k);continue
   t=ins[p-1];tk=f"COREMA:{c}:{rec}:{t['element_ordinal']}"
   d=int(r["element_ordinal"])-int(t["element_ordinal"])
   if tk not in keys or d<=0 or d>=K:invalid.append(k);continue
   out[k]=d;target[k]=tk
 return out,target,invalid

def outcome_crossfit(y,role,strata,folds,tokens):
 n=len(y);p0=np.zeros((n,K));q0=np.zeros((n,K));q1=np.zeros((n,K));lookup=np.full(n,-1,int);eval_strata=[None]*n
 for held in sorted(set(folds)):
  tr=[i for i,f in enumerate(folds) if f!=held];te=[i for i,f in enumerate(folds) if f==held];gf=Counter(tokens[i] for i in tr);ss={i:tuple(strata[i])+(binint(gf[tokens[i]],[1,2,4,8,16,32,64]),) for i in tr+te};gy=np.bincount(y[tr],minlength=K);gp=(gy+1)/(len(tr)+K)
  sc=Counter();src=Counter();rc={0:Counter(),1:Counter()};rn={0:Counter(),1:Counter()};rgy={0:np.zeros(K,int),1:np.zeros(K,int)};rgn={0:0,1:0}
  for i in tr:
   s=ss[i];v=int(y[i]);rr=int(role[i]);sc[s]+=1;src[(s,v)]+=1;rn[rr][s]+=1;rc[rr][(s,v)]+=1;rgy[rr][v]+=1;rgn[rr]+=1
  rp={rr:(rgy[rr]+1)/(rgn[rr]+K) if rgn[rr] else gp for rr in [0,1]}
  for i in te:
   s=ss[i];eval_strata[i]=s;p0[i]=(np.array([src[(s,k)] for k in range(K)])+8*gp)/(sc[s]+8)
   for rr,dest in [(0,q0),(1,q1)]:dest[i]=(np.array([rc[rr][(s,k)] for k in range(K)])+8*rp[rr])/(rn[rr][s]+8)
   if sc[s]:lookup[i]=min([k for k in range(K) if src[(s,k)]==max(src[(s,j)] for j in range(K))])
 p=role[:,None]*q1+(1-role[:,None])*q0
 return p0,p,q0,q1,lookup,eval_strata

def target_metrics(y,p):
 ids=np.where(y>0)[0]
 if not len(ids):return (float("nan"),float("nan"))
 vals=p[ids,1:];truth=y[ids]-1;top=float(np.mean(np.argmax(vals,axis=1)==truth));rr=[]
 for a,t in zip(vals,truth):
  order=np.argsort(-a,kind="stable");rr.append(1/(int(np.where(order==t)[0][0])+1))
 return top,float(np.mean(rr))

def main():
 freeze=json.loads(FREEZE.read_text());assert freeze["status"]=="FROZEN_BEFORE_PARENT_LINK_SCORING" and not freeze["voynich_stage_authorized"] and not any(freeze["f84"].values())
 rows=[r for r in readgz(ENC) if r["domain"]=="COREMA"]
 assert all(not any(x in c.lower() for x in FORBIDDEN) for c in ["host_id","rendered_group","wrapper_state","positional_state","boundary_state","record_state","renderer_variant","composite_joint_id","field_index","within_field_index","record_element_count","relative_position","surface_length","within_record_frequency","previous_host","source_token_equality"])
 oracle=list(csv.DictReader(ORACLE.open(encoding="utf-8",newline=""),delimiter="\t"));om={f"COREMA:{r['collection_id']}:{r['recipe_id']}:{r['element_ordinal']}":r for r in oracle};assert len(rows)==27349 and all(r["element_key"] in om for r in rows)
 out,target,invalid=build_outcome(rows,oracle);rep,ch,strata_all=prepare(rows);eligible=[i for i,r in enumerate(rows) if r["element_key"] in out];assert len(eligible)==26169 and sum(out[rows[i]["element_key"]]>0 for i in eligible)==11415 and len(invalid)==87
 erows=[rows[i] for i in eligible];folds_all=[r["collection_id"] for r in rows];folds=[folds_all[i] for i in eligible];y=np.array([out[r["element_key"]] for r in erows],int);estrata=[strata_all[i] for i in eligible]
 const=[("CONST",)]*len(rows);route_cache={};score_rows=[];fold_rows=[];pred_rows=[];counter=[]
 for route,fn in ROUTES.items():
  yr=np.array([int(fn(om[r["element_key"]])) for r in rows]);pr0=nb_crossfit(yr,const,folds_all);local=[nb_crossfit(yr,rep[x],folds_all) for x in REPS];pc=nb_crossfit_frequency(yr,ch,folds_all,[r["source_token_equality"] for r in rows]);pr=combine2(combine(local),pc);pj=local[REPS.index("COMPOSITE_JOINT_STATE")]
  yre=yr[eligible];pre=pr[eligible];pje=pj[eligible];pbase,pfull,q0,q1,lookup,eval_strata=outcome_crossfit(y,yre,estrata,folds,[r["source_token_equality"] for r in erows]);sb=bits_multi(y,pbase);fb=bits_multi(y,pfull);gain=sb-fb;source_top=float(np.mean(np.argmax(pbase,axis=1)==y));full_top=float(np.mean(np.argmax(pfull,axis=1)==y));s_t1,s_mrr=target_metrics(y,pbase);f_t1,f_mrr=target_metrics(y,pfull);edge=(y>0).astype(int);source_edge=auc(edge,1-pbase[:,0]);full_edge=auc(edge,1-pfull[:,0]);covered=lookup>=0;lookup_acc=float(np.mean(lookup[covered]==y[covered])) if covered.any() else float("nan")
  posfold=0
  for f in sorted(set(folds)):
   ids=np.array([i for i,x in enumerate(folds) if x==f]);g=bits_multi(y[ids],pbase[ids])-bits_multi(y[ids],pfull[ids]);posfold+=g>0;st1,sm=target_metrics(y[ids],pbase[ids]);ft1,fm=target_metrics(y[ids],pfull[ids]);fold_rows.append({"route_id":route,"held_collection":f,"n":len(ids),"links":int((y[ids]>0).sum()),"role_rows":int(yre[ids].sum()),"source_bits":bits_multi(y[ids],pbase[ids]),"role_bits":bits_multi(y[ids],pfull[ids]),"gain_bits":g,"source_target_top1":st1,"role_target_top1":ft1,"source_target_mrr":sm,"role_target_mrr":fm})
  # Conditional mobility is defined on the exact frozen source stratum.
  groups=defaultdict(list)
  for i,(f,s) in enumerate(zip(folds,eval_strata)):groups[(f,s)].append(i)
  mobile=np.zeros(len(y),bool)
  for ids in groups.values():
   if len(ids)>1 and len({round(float(pre[i]),12) for i in ids})>1:mobile[ids]=True
  route_links=sum(int(fn(r)) and int(r["parent_instruction_ordinal"])>0 for r in oracle)
  linkcols=len({r["collection_id"] for r in oracle if fn(r) and int(r["parent_instruction_ordinal"])>0})
  row={"route_id":route,"n":len(y),"role_rows":int(yre.sum()),"visible_role_links":sum(int(y[i]>0 and yre[i]) for i in range(len(y))),"link_collections":linkcols,"role_auc":auc(yre,pre),"role_gain_bits":bits_binary(yre,pr0[eligible])-bits_binary(yre,pre),"exact_joint_role_auc":auc(yre,pje),"source_relation_bits":sb,"role_relation_bits":fb,"relation_gain_bits":gain,"positive_gain_collections":int(posfold),"source_relation_top1":source_top,"role_relation_top1":full_top,"source_edge_auc":source_edge,"role_edge_auc":full_edge,"source_target_top1":s_t1,"role_target_top1":f_t1,"source_target_mrr":s_mrr,"role_target_mrr":f_mrr,"target_mrr_delta":f_mrr-s_mrr,"exact_signature_coverage":int(covered.sum()),"exact_signature_accuracy":lookup_acc,"exact_signature_perfect":int(covered.any() and lookup_acc==1),"mobile_rows":int(mobile.sum()),"mobile_fraction":float(mobile.mean()),"joint_max4_p":"PENDING","gate_pass":0};score_rows.append(row)
  route_cache[route]={"pre":pre,"pbase":pbase,"q0":q0,"q1":q1,"source_bits":sb,"obs_gain":gain,"mobile":mobile,"eval_strata":eval_strata}
  for i,r in enumerate(erows):
   pred_rows.append({"route_id":route,"element_key":r["element_key"],"held_collection":folds[i],"role_y":int(yre[i]),"relation_class":"NONE" if y[i]==0 else "D"+str(y[i]),"target_element_key":target[r["element_key"]],"p_role_baseline":pr0[eligible[i]],"p_role":pre[i],"p_exact_joint_role":pje[i],"source_true_probability":pbase[i,y[i]],"role_true_probability":pfull[i,y[i]],"source_prediction":"NONE" if np.argmax(pbase[i])==0 else "D"+str(np.argmax(pbase[i])),"role_prediction":"NONE" if np.argmax(pfull[i])==0 else "D"+str(np.argmax(pfull[i])),"exact_source_lookup_prediction":"UNSEEN" if lookup[i]<0 else ("NONE" if lookup[i]==0 else "D"+str(lookup[i]))})
   if route=="CMP_PARENT_01" and yre[i] and y[i]>0:
    delta=math.log2(max(pfull[i,y[i]],1e-15)/max(pbase[i,y[i]],1e-15));counter.append({"element_key":r["element_key"],"held_collection":folds[i],"true_relation":"D"+str(y[i]),"source_prediction":"NONE" if np.argmax(pbase[i])==0 else "D"+str(np.argmax(pbase[i])),"role_prediction":"NONE" if np.argmax(pfull[i])==0 else "D"+str(np.argmax(pfull[i])),"role_probability":pre[i],"role_added_log2_true_probability":delta})
 # One shared conditional permutation per world, jointly charging four routes.
 gids={};ga=[]
 for f,s in zip(folds,route_cache["CMP_PARENT_01"]["eval_strata"]):
  k=(f,s)
  if k not in gids:gids[k]=len(gids)
  ga.append(gids[k])
 ga=np.array(ga);base_order=np.argsort(ga,kind="stable");rng=np.random.default_rng(3852048);nullrows=[];worldmax=[]
 for world in range(2048):
  donor=np.lexsort((rng.random(len(y)),ga));perm=np.empty(len(y),int);perm[base_order]=donor;gains=[]
  for route in ROUTES:
   z=route_cache[route];pp=z["pre"][perm];true0=z["q0"][np.arange(len(y)),y];true1=z["q1"][np.arange(len(y)),y];b=-np.log2(np.clip((1-pp)*true0+pp*true1,1e-15,1)).sum();gains.append(z["source_bits"]-b)
  m=float(max(gains));worldmax.append(m);nullrows.append({"world":world,"max4_gain_bits":m})
 for row in score_rows:
  row["joint_max4_p"]=(1+sum(x>=float(row["relation_gain_bits"]) for x in worldmax))/2049
  row["gate_pass"]=int(float(row["role_auc"])>=.60 and float(row["role_gain_bits"])>0 and int(row["visible_role_links"])>=50 and int(row["link_collections"])>=5 and not int(row["exact_signature_perfect"]) and float(row["relation_gain_bits"])>0 and int(row["positive_gain_collections"])>=4 and float(row["target_mrr_delta"])>=0 and float(row["mobile_fraction"])>=.20 and float(row["joint_max4_p"])<=.05)
 passed=sum(int(r["gate_pass"]) for r in score_rows);priority=next(r for r in score_rows if r["route_id"]=="CMP_PARENT_01");instrument=bool(priority["gate_pass"] and passed>=3)
 write(ART/"gdt385_route_scores.tsv",score_rows);write(ART/"gdt385_collection_folds.tsv",fold_rows);write(ART/"gdt385_null_worlds.tsv",nullrows);writegz(ART/"gdt385_predictions.tsv.gz",pred_rows);counter.sort(key=lambda x:float(x["role_added_log2_true_probability"]));write(ART/"gdt385_counterexamples.tsv",counter[:30])
 outs=[ART/x for x in ["gdt385_route_scores.tsv","gdt385_collection_folds.tsv","gdt385_null_worlds.tsv","gdt385_predictions.tsv.gz","gdt385_counterexamples.tsv"]]
 impl=[BASE/"src/run.py",BASE/"src/run_gdt385.py",BASE/"src/validate.py",BASE/"src/freeze_gdt385.py",BASE/"src/validate_freeze.py"]
 result={"schema":"GDT385_RESULT_V1","status":"COMPARATOR_PARENT_LINK_INSTRUMENT_VALIDATED_TARGET_FREEZE_REQUIRED" if instrument else "COMPARATOR_PARENT_LINK_INSTRUMENT_FAILED_STOP_BEFORE_VOYNICH","eligible_pivots":len(y),"valid_links":int((y>0).sum()),"invalid_or_unobservable_positive_links":len(invalid),"routes_passing":passed,"priority_route_pass":bool(priority["gate_pass"]),"instrument_pass":instrument,"voynich_stage_authorized":False,"voynich_rows_read":0,"semantic_state":"UNASSIGNED","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"route_summary":{r["route_id"]:{k:r[k] for k in ["role_auc","role_gain_bits","relation_gain_bits","positive_gain_collections","target_mrr_delta","mobile_fraction","joint_max4_p","gate_pass"]} for r in score_rows},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [ENC,ORACLE,FREEZE]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outs},"implementation":{str(p.relative_to(ROOT)):sha(p) for p in impl},"claim_ceiling":"COMPARATOR_EXTERNAL_PARENT_LINK_INSTRUMENT_ONLY"};result["content_hash"]=content(result);(ART/"gdt385_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"passing":passed,"routes":result["route_summary"]},sort_keys=True))

if __name__=="__main__":main()

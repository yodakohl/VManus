#!/usr/bin/env python3
"""Run the frozen GDT381 anonymous topology target; never inspect realizations."""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt381_relational_topology_transfer";ART=BASE/"artifacts";SOURCE=ROOT/"gdt327_joint_tuple_interlinear.tsv";FREEZE=ART/"gdt381_voynich_target_freeze.json";RUNNER=BASE/"src/run_comparator.py"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(o):q=dict(o);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write_json(p,o):o["content_hash"]=content(o);p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def write_tsv(p,rows):
 if p.suffix==".gz":raw=p.open("wb");gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0);h=io.TextIOWrapper(gz,encoding="utf-8",newline="")
 else:h=p.open("w",encoding="utf-8",newline="")
 with h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def read_source():
 with SOURCE.open(encoding="utf-8",newline="") as h:raw=list(csv.DictReader(h,delimiter="\t"))
 for r in raw:
  if any(r[k].startswith("f84") for k in ["page","physical_folio","locus"]):raise ValueError("f84 row")
 byrec=defaultdict(list)
 for i,r in enumerate(raw):byrec[(r["page"],r["record_ordinal"])].append(i)
 obs=[None]*len(raw)
 for key,ids in byrec.items():
  cnt=Counter(raw[i]["joint_tuple_id"] for i in ids);m=len(ids)
  for j,i in enumerate(ids):
   r=raw[i];before=int(r["line_first"]=="1" or r["prev_dy"]=="1");after=int(r["dy_closure"]=="1" or r["b3"]=="1" or r["group_index"]==r["group_count"])
   obs[i]={"element_key":r["event_id_sha256"],"domain":r["register"],"collection_id":r["physical_folio"],"record_id":r["page"]+":R"+r["record_ordinal"],"element_ordinal":str(j+1),"opaque_form_id":r["joint_tuple_id"],"relative_position":str((j+.5)/m),"record_element_count":str(m),"surface_length":"0","direct_token_count":"1","boundary_before":str(before),"boundary_after":str(after),"within_record_frequency":str(cnt[r["joint_tuple_id"]]),"physical_line_count":r["group_count"]}
 return raw,obs,byrec
def sigmoid(x):z=np.clip(x,-40,40);return np.where(z>=0,1/(1+np.exp(-z)),np.exp(z)/(1+np.exp(z)))
def entropy(vals):
 if not vals:return 0.
 c=Counter(vals);n=len(vals);return -sum((v/n)*math.log2(v/n) for v in c.values())
def rankdata(v):
 v=np.asarray(v);o=np.argsort(v,kind="stable");r=np.empty(len(v));i=0
 while i<len(v):
  j=i+1
  while j<len(v) and v[o[j]]==v[o[i]]:j+=1
  r[o[i:j]]=(i+j+1)/2;i=j
 return r
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1
 if not n1 or not n0:return float("nan")
 r=rankdata(s);return float((r[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bits(y,p):p=np.clip(np.asarray(p),1e-9,1-1e-9);y=np.asarray(y);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))


def source_features(raw,obs,event_class,held):
 train=[i for i,r in enumerate(raw) if r["physical_folio"]!=held];trainset=set(train);records=defaultdict(list)
 for i,r in enumerate(raw):records[(r["page"],r["record_ordinal"])].append(i)
 edge=Counter();cc=Counter();out=defaultdict(set);inn=defaultdict(set)
 for ids in records.values():
  seq=[(raw[i]["register"],int(event_class[i])) for i in ids if i in trainset]
  cc.update(seq)
  for a,b in zip(seq,seq[1:]):edge[a,b]+=1;out[a].add(b);inn[b].add(a)
 sections=sorted({r["section"] for r in raw});registers=sorted({r["register"] for r in raw});curriers=sorted({r["currier"] for r in raw});hands=sorted({r["hand"] for r in raw})
 nn=["INTERCEPT","LOG_RECORD_LENGTH","RELATIVE_POSITION","RELATIVE_POSITION_SQ","FIELD_ORDINAL_RATE","LINE_FIRST","PREV_DY","DY_CLOSURE","B3","LINE_END","LOG_RECORD_TUPLE_RECURRENCE","LOG_TRAIN_CLASS_SIZE"]+["SECTION_"+x for x in sections]+["REGISTER_"+x for x in registers]+["CURRIER_"+x for x in curriers]+["HAND_"+x for x in hands]+["WITHIN_FIELD_"+x for x in ["FIRST","MIDDLE","LAST","SINGLE"]]
 tn=["PREV_CLASS_CHANGE","CURRENT_SEEN_LEFT4","LOG_PREV_OUTDEGREE","LOG_PREV_CURRENT_EDGE","CURRENT_CLASS_SIZE_RANK","LEFT1_UNIQUE","LEFT2_UNIQUE","LEFT4_UNIQUE","LEFT8_UNIQUE"]
 fn=["ALT_PATHS_INTO_CURRENT","SKIP_EDGE_LOG_SUPPORT","PRIOR_ACA_CHAIN"]
 for h in [1,2,4,8]:fn += [f"H{h}_LEFT_ENTROPY",f"H{h}_CURRENT_RETURN",f"H{h}_DOMINANT_PERSISTENCE",f"H{h}_LEFT_DIVERSITY",f"H{h}_PREV_BRANCH_DEGREE"]
 Xn=np.zeros((len(raw),len(nn)));Xt=np.zeros((len(raw),len(tn)));Xf=np.zeros((len(raw),len(fn)));sizes=np.array(list(cc.values()) or [1])
 for ids in records.values():
  seq=[(raw[i]["register"],int(event_class[i])) for i in ids];tuplecnt=Counter(raw[i]["joint_tuple_id"] for i in ids);m=len(ids);maxfield=max(int(raw[i]["field_ordinal"]) for i in ids)
  for j,i in enumerate(ids):
   r=raw[i];cur=seq[j];prev=seq[j-1] if j else None;prevprev=seq[j-2] if j>=2 else None;left4=seq[max(0,j-4):j];lineend=int(r["group_index"]==r["group_count"]);nvec=[1,math.log1p(m),(j+.5)/m,((j+.5)/m)**2,int(r["field_ordinal"])/max(1,maxfield),int(r["line_first"]=="1"),int(r["prev_dy"]=="1"),int(r["dy_closure"]=="1"),int(r["b3"]=="1"),lineend,math.log1p(tuplecnt[r["joint_tuple_id"]]),math.log1p(cc[cur])]
   nvec += [int(r["section"]==x) for x in sections]+[int(r["register"]==x) for x in registers]+[int(r["currier"]==x) for x in curriers]+[int(r["hand"]==x) for x in hands]+[int(r["within_field_position"]==x) for x in ["FIRST","MIDDLE","LAST","SINGLE"]];Xn[i]=nvec
   rank=sum(v<=cc[cur] for v in sizes)/len(sizes);tvec=[int(prev is not None and prev!=cur),int(cur in left4),math.log1p(len(out[prev])) if prev else 0,math.log1p(edge[prev,cur]) if prev else 0,rank]
   for h in [1,2,4,8]:left=seq[max(0,j-h):j];tvec.append(len(set(left))/max(1,len(left)))
   Xt[i]=tvec;mids=(out[prevprev]&inn[cur]) if prevprev else set();fvec=[max(0,len(mids)-1),math.log1p(edge[prevprev,cur]) if prevprev else 0,int(j>=3 and seq[j-3]==prev and seq[j-2]==cur)]
   for h in [1,2,4,8]:
    left=seq[max(0,j-h):j];dom=Counter(left).most_common(1)[0][0] if left else None;fvec += [entropy(left)/max(1.,math.log2(max(2,len(left)))),int(cur in left),int(dom==cur),len(set(left))/max(1,len(left)),math.log1p(len(out[prev])) if prev else 0]
   Xf[i]=fvec
 return Xn,Xt,Xf,nn,tn,fn


def main():
 freeze=json.loads(FREEZE.read_text());assert freeze["status"]=="FROZEN_BEFORE_VOYNICH_TOPOLOGY_SCORING" and freeze["voynich_events_scored"]==0
 spec=importlib.util.spec_from_file_location("gdt381_runner_target",RUNNER);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 raw,obs,byrec=read_source();domains=np.array([r["domain"] for r in obs]);domain_indices={d:np.where(domains==d)[0].tolist() for d in sorted(set(domains))};design=json.loads((ART/"gdt381_comparator_topology_freeze.json").read_text())
 event_class,class_q,nuisance,trivial,relational,nn,tn,rn,_,_,classrows,meta=mod.build_topology(obs,domain_indices,design);names=nn+tn+rn;assert names==freeze["comparator_model"]["feature_names"]
 X=np.column_stack([nuisance,trivial,relational]);mu=np.array(freeze["comparator_model"]["training_mean"]);sd=np.array(freeze["comparator_model"]["training_sd"]);beta=np.array(freeze["comparator_model"]["coefficients"]);Z=X.copy();Z[:,1:]=(Z[:,1:]-mu)/sd;topology_score=sigmoid(Z@beta);membership=np.zeros(len(raw),int);cuts={}
 for reg in sorted(set(r["register"] for r in raw)):
  ids=[i for i,r in enumerate(raw) if r["register"]==reg];cut=float(np.quantile(topology_score[ids],freeze["comparator_model"]["selected_within_domain_quantile"]));cuts[reg]=cut;membership[ids]=(topology_score[ids]>=cut).astype(int)
 folios=sorted(set(r["physical_folio"] for r in raw));all_pn=np.full(len(raw),np.nan);all_pt=all_pn.copy();all_pf=all_pn.copy();foldrows=[]
 for held in folios:
  train=np.array([i for i,r in enumerate(raw) if r["physical_folio"]!=held]);test=np.array([i for i,r in enumerate(raw) if r["physical_folio"]==held]);Xn,Xt,Xf,snn,stn,sfn=source_features(raw,obs,event_class,held);p0=mod.predict(mod.fit(Xn[train],membership[train],[raw[i]["physical_folio"] for i in train]),Xn[test]);p1=mod.predict(mod.fit(np.column_stack([Xn[train],Xt[train]]),membership[train],[raw[i]["physical_folio"] for i in train]),np.column_stack([Xn[test],Xt[test]]));p2=mod.predict(mod.fit(np.column_stack([Xn[train],Xt[train],Xf[train]]),membership[train],[raw[i]["physical_folio"] for i in train]),np.column_stack([Xn[test],Xt[test],Xf[test]]));all_pn[test],all_pt[test],all_pf[test]=p0,p1,p2;y=membership[test];gn=bits(y,p0)-bits(y,p2);gt=bits(y,p1)-bits(y,p2);powered=len(test)>=20 and y.sum()>=4 and (len(y)-y.sum())>=4
  foldrows.append({"held_folio":held,"n":len(test),"positives":int(y.sum()),"powered":int(powered),"auc_nuisance":f"{auc(y,p0):.9f}","auc_trivial":f"{auc(y,p1):.9f}","auc_full":f"{auc(y,p2):.9f}","gain_full_vs_nuisance_bits":f"{gn:.9f}","gain_full_vs_trivial_bits":f"{gt:.9f}","positive_both":int(gn>0 and gt>0)})
 assert np.all(np.isfinite(all_pf));total_gn=bits(membership,all_pn)-bits(membership,all_pf);total_gt=bits(membership,all_pt)-bits(membership,all_pf);powered=[r for r in foldrows if r["powered"]=="1" or r["powered"]==1];folio_fraction=sum(int(r["positive_both"]) for r in powered)/max(1,len(powered));overall_auc=auc(membership,all_pf)
 regrows=[]
 for reg in sorted(set(r["register"] for r in raw)):
  ids=np.array([i for i,r in enumerate(raw) if r["register"]==reg]);gn=bits(membership[ids],all_pn[ids])-bits(membership[ids],all_pf[ids]);gt=bits(membership[ids],all_pt[ids])-bits(membership[ids],all_pf[ids]);regrows.append({"register":reg,"n":len(ids),"positives":int(membership[ids].sum()),"gain_full_vs_nuisance_bits":f"{gn:.9f}","gain_full_vs_trivial_bits":f"{gt:.9f}","positive_both":int(gn>0 and gt>0)})
 strata=defaultdict(list)
 classcount=Counter((raw[i]["register"],int(event_class[i])) for i in range(len(raw)))
 for i,r in enumerate(raw):
  m=int(obs[i]["record_element_count"]);lb="1-8" if m<=8 else "9-16" if m<=16 else "17-32" if m<=32 else "33+";pb=min(4,int(float(obs[i]["relative_position"])*5));closure=r["dy_closure"]+r["b3"]+str(int(r["group_index"]==r["group_count"]));freq=int(obs[i]["within_record_frequency"]);fb="1" if freq<=1 else "2" if freq==2 else "3+";strata[(r["section"],r["register"],r["currier"],r["hand"],lb,pb,r["within_field_position"],closure,fb,int(class_q[i]))].append(i)
 mixed=[ids for ids in strata.values() if len({int(membership[i]) for i in ids})>1];mobile=sum(len(ids) for ids in mixed);obs_joint=min(total_gn,total_gt);nullrows=[]
 for world in range(freeze["held_test"]["null_worlds"]):
  rng=np.random.default_rng(freeze["held_test"]["seed"]+world);yp=membership.copy()
  for ids in strata.values():yp[ids]=rng.permutation(yp[ids])
  gn=bits(yp,all_pn)-bits(yp,all_pf);gt=bits(yp,all_pt)-bits(yp,all_pf);nullrows.append({"world":world,"gain_vs_nuisance_bits":f"{gn:.9f}","gain_vs_trivial_bits":f"{gt:.9f}","joint_min_gain_bits":f"{min(gn,gt):.9f}"})
 p=(1+sum(float(r["joint_min_gain_bits"])>=obs_joint for r in nullrows))/(1+len(nullrows));positive_regs=sum(int(r["positive_both"]) for r in regrows);passes=total_gn>0 and total_gt>0 and folio_fraction>=.60 and positive_regs>=3 and overall_auc>=.60 and p<=.05 and mobile>=256 and len(powered)>=20
 eventrows=[{"event_id":raw[i]["event_id_sha256"],"page":raw[i]["page"],"physical_folio":raw[i]["physical_folio"],"section":raw[i]["section"],"register":raw[i]["register"],"local_latent_class":int(event_class[i]),"comparator_topology_score":f"{topology_score[i]:.9f}","behavior_class_member":int(membership[i]),"held_probability_nuisance":f"{all_pn[i]:.9f}","held_probability_trivial":f"{all_pt[i]:.9f}","held_probability_full":f"{all_pf[i]:.9f}","exact_formal_identity_exported":0,"semantic_state":"UNASSIGNED"} for i in range(len(raw))]
 classout=[]
 for r in classrows:classout.append({**r,"selected_k":meta[r["domain"]]["k"]})
 write_tsv(ART/"gdt381_voynich_latent_class_summary.tsv",classout);write_tsv(ART/"gdt381_voynich_event_scores.tsv.gz",eventrows);write_tsv(ART/"gdt381_voynich_fold_scores.tsv",foldrows);write_tsv(ART/"gdt381_voynich_register_scores.tsv",regrows);write_tsv(ART/"gdt381_voynich_null.tsv.gz",nullrows)
 outcome={"schema":"GDT381_VOYNICH_TOPOLOGY_RESULT_V1","status":"ANONYMOUS_RELATIONAL_TOPOLOGY_TRANSFER_PASS" if passes else "NO_STABLE_ANONYMOUS_RELATIONAL_TOPOLOGY_TRANSFER","behavior_class_id":"CMP04_BEHAVIOR_CLASS_A","events":len(raw),"folios":len(folios),"registers":len(regrows),"members":int(membership.sum()),"total_gain_vs_nuisance_bits":total_gn,"total_gain_vs_trivial_bits":total_gt,"held_auc":overall_auc,"powered_folios":len(powered),"positive_both_folios":sum(int(r["positive_both"]) for r in powered),"positive_both_folio_fraction":folio_fraction,"positive_both_registers":positive_regs,"mobile_events":mobile,"mobile_strata":len(mixed),"joint_null_p":p,"promotion":passes,"formal_realizations_inspected":False,"exact_formal_identity_exported":False,"semantic_state":"UNASSIGNED","inputs":{str(p.relative_to(ROOT)):sha(p) for p in [SOURCE,FREEZE]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in [ART/"gdt381_voynich_latent_class_summary.tsv",ART/"gdt381_voynich_event_scores.tsv.gz",ART/"gdt381_voynich_fold_scores.tsv",ART/"gdt381_voynich_register_scores.tsv",ART/"gdt381_voynich_null.tsv.gz"]},"implementation":{str((BASE/"src/run_target.py").relative_to(ROOT)):sha(BASE/"src/run_target.py"),str(RUNNER.relative_to(ROOT)):sha(RUNNER)},"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"ANONYMOUS_RELATION_TOPOLOGY_CLASS_ONLY_NO_FUNCTION_LABEL"};write_json(ART/"gdt381_voynich_result.json",outcome);print(json.dumps({k:outcome[k] for k in ["status","members","total_gain_vs_nuisance_bits","total_gain_vs_trivial_bits","held_auc","positive_both_folio_fraction","positive_both_registers","joint_null_p"]}))
if __name__=="__main__":main()

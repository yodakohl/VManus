#!/usr/bin/env python3
"""Run frozen GDT384 priority COORDINATOR relation test only."""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt384_role_specific_relational_consequence";ART=BASE/"artifacts"
ENC=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz"
ORACLE=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_hidden_oracle.tsv.gz"
REL=ART/"gdt384_hidden_relational_oracle.tsv.gz";FREEZE=ART/"gdt384_stage_a_freeze.json"
REPS=["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN"]
CHANNELS=["FREQUENCY","RECURRENCE","LINE_FIELD_POSITION","RECORD_RELATIVE_POSITION","BOUNDARY_CLOSURE","PREVIOUS_STATE","RECORD_LENGTH"]

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
def bits(y,p):y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-9,1-1e-9);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def binint(v,cuts):
 v=int(v)
 for i,c in enumerate(cuts):
  if v<=c:return str(i)
 return str(len(cuts))
def combine(ps):return sigmoid(np.median(np.vstack([logit(p) for p in ps]),axis=0))
def combine2(a,b):return sigmoid((logit(a)+logit(b))/2)

def prepare(rows):
 gf=Counter(r["source_token_equality"] for r in rows);byrec=defaultdict(list)
 for i,r in enumerate(rows):byrec[r["record_id"]].append(i)
 rep={k:[None]*len(rows) for k in REPS};ch={k:[None]*len(rows) for k in CHANNELS};allch=[None]*len(rows)
 for ids in byrec.values():
  ids.sort(key=lambda i:int(rows[i]["element_ordinal"]))
  for j,i in enumerate(ids):
   r=rows[i];span=[rows[x] for x in ids[max(0,j-2):j]]+[r];g=r["rendered_group"]
   rep["HOST_IDENTITY"][i]=("H="+r["host_id"],"HL="+str(len(r["host_id"])))
   rep["COMPLETE_RENDERED_GROUP"][i]=("G="+g,"GP="+g[:2],"GS="+g[-2:],"GL="+str(len(g)))
   rep["CONSTRUCTION_STATE"][i]=("W="+r["wrapper_state"],"P="+r["positional_state"],"B="+r["boundary_state"],"R="+r["record_state"],"V="+r["renderer_variant"],"WF="+r["within_field_index"])
   rep["COMPOSITE_JOINT_STATE"][i]=("J="+r["composite_joint_id"],)
   rep["SHORT_CONSTRUCTION_SPAN"][i]=("SS="+"|".join(x["wrapper_state"]+x["boundary_state"]+x["renderer_variant"] for x in span),"SH="+"|".join(x["host_id"] for x in span))
   ch["FREQUENCY"][i]=("F="+binint(gf[r["source_token_equality"]],[1,2,4,8,16,32,64]),);ch["RECURRENCE"][i]=("C="+binint(r["within_record_frequency"],[1,2,4]),)
   ch["LINE_FIELD_POSITION"][i]=("FI="+r["field_index"],"WF="+r["within_field_index"]);ch["RECORD_RELATIVE_POSITION"][i]=("P="+r["positional_state"],);ch["BOUNDARY_CLOSURE"][i]=("B="+r["boundary_state"],);ch["PREVIOUS_STATE"][i]=("PREV="+r["previous_host"],);ch["RECORD_LENGTH"][i]=("RL="+binint(r["record_element_count"],[8,16,32,64]),)
   allch[i]=tuple(v for name in CHANNELS for v in ch[name][i])
 return rep,allch

def nb_crossfit(y,features,rows,folds):
 n=len(y);pred=np.zeros(n,float);groups=defaultdict(list)
 for i,f in enumerate(folds):groups[f].append(i)
 tc=Counter(y);hc=Counter();tot=Counter();held=Counter();tv=Counter();hv=Counter();voc=defaultdict(set)
 for i,c in enumerate(y):
  f=folds[i];hc[(f,c)]+=1
  for k,v in enumerate(features[i]):tot[(c,k,v)]+=1;held[(f,c,k,v)]+=1;tv[(k,v)]+=1;hv[(f,k,v)]+=1;voc[k].add(v)
 for f,test in groups.items():
  n1=tc[1]-hc[(f,1)];n0=tc[0]-hc[(f,0)];prior=math.log((n1+1)/(n0+1));Vs=[]
  for k in range(len(features[0])):Vs.append(len(voc[k])-sum(hv[(f,k,v)]==tv[(k,v)] for v in voc[k] if hv[(f,k,v)])+1)
  for i in test:
   z=prior
   for k,v in enumerate(features[i]):z+=math.log((tot[(1,k,v)]-held[(f,1,k,v)]+1)/(n1+Vs[k]))-math.log((tot[(0,k,v)]-held[(f,0,k,v)]+1)/(n0+Vs[k]))
   pred[i]=float(sigmoid(z))
 return pred

def exact_lookup_crossfit(y,features,folds):
 total=Counter();pos=Counter();ft=Counter();fp=Counter();out=np.zeros(len(y))
 for i,(v,f) in enumerate(zip(features,folds)):total[v]+=1;pos[v]+=y[i];ft[(f,v)]+=1;fp[(f,v)]+=y[i]
 prior=(sum(y)+1)/(len(y)+2)
 for i,(v,f) in enumerate(zip(features,folds)):
  n=total[v]-ft[(f,v)];k=pos[v]-fp[(f,v)];out[i]=(k+2*prior)/(n+2)
 return out

def fit_logistic(X,y,l2=4.):
 X=np.asarray(X,float);y=np.asarray(y,float);mu=X[:,1:].mean(0);sd=X[:,1:].std(0);sd[sd<1e-8]=1;Z=X.copy();Z[:,1:]=(Z[:,1:]-mu)/sd;b=np.zeros(Z.shape[1]);pen=np.ones(len(b))*l2;pen[0]=0
 for _ in range(40):
  p=sigmoid(Z@b);w=np.maximum(p*(1-p),1e-5);H=(Z.T*w)@Z+np.diag(pen);g=Z.T@(y-p)-pen*b
  try:step=np.linalg.solve(H,g)
  except np.linalg.LinAlgError:step=np.linalg.lstsq(H,g,rcond=None)[0]
  b+=step
  if np.max(np.abs(step))<1e-7:break
 return b,mu,sd
def predict(model,X):b,mu,sd=model;Z=np.asarray(X,float).copy();Z[:,1:]=(Z[:,1:]-mu)/sd;return sigmoid(Z@b)
def relation_crossfit(y,p_source,p_role,folds):
 p=np.zeros(len(y));groups=defaultdict(list)
 for i,f in enumerate(folds):groups[f].append(i)
 X=np.column_stack([np.ones(len(y)),logit(p_source),logit(p_role)])
 for f,test in groups.items():
  train=[i for i in range(len(y)) if folds[i]!=f];p[test]=predict(fit_logistic(X[train],np.asarray(y)[train]),X[test])
 return p

def main():
 freeze=json.loads(FREEZE.read_text());assert freeze["status"]=="FROZEN_BEFORE_RELATION_CONSTRUCTION_OR_SCORING" and not freeze["voynich_stage_b_authorized"]
 enc=[x for x in readgz(ENC) if x["domain"]=="PCEEC2"];om={x["element_key"]:x for x in readgz(ORACLE) if x["domain"]=="PCEEC2"};rm={x["element_key"]:x for x in readgz(REL) if x["domain"]=="PCEEC2"};assert len(enc)==len(om)==len(rm)==27518
 role=np.array([int(om[x["element_key"]]["COORDINATOR"]) for x in enc]);rel=np.array([int(rm[x["element_key"]]["COORDINATOR_relation_y"]) for x in enc]);folds=[x["collection_id"] for x in enc]
 rep,allch=prepare(enc);constant=[("CONST",)]*len(enc);base_role=nb_crossfit(role,constant,enc,folds);local=[nb_crossfit(role,rep[r],enc,folds) for r in REPS];compiler=nb_crossfit(role,allch,enc,folds);p_role=combine2(combine(local),compiler)
 source_features=[tuple(list(rep["CONSTRUCTION_STATE"][i])+list(allch[i])) for i in range(len(enc))];p_source=nb_crossfit(rel,source_features,enc,folds);p_deterministic=exact_lookup_crossfit(rel,source_features,folds);p_relation=relation_crossfit(rel,p_source,p_role,folds)
 role_auc=auc(role,p_role);role_gain=bits(role,base_role)-bits(role,p_role);source_auc=auc(rel,p_source);det_auc=auc(rel,p_deterministic);base_auc=source_auc;full_auc=auc(rel,p_relation);gain=bits(rel,p_source)-bits(rel,p_relation)
 foldrows=[]
 for f in sorted(set(folds)):
  ids=[i for i,x in enumerate(folds) if x==f];g=bits(rel[ids],p_source[ids])-bits(rel[ids],p_relation[ids]);foldrows.append({"held_collection":f,"n":len(ids),"role_positives":int(role[ids].sum()),"relation_positives":int(rel[ids].sum()),"source_auc":auc(rel[ids],p_source[ids]),"role_plus_relation_auc":auc(rel[ids],p_relation[ids]),"gain_bits":g})
 prepass=(int(rel.sum())>=50 and len(rel)-int(rel.sum())>=50 and source_auc<=.65 and det_auc<=.65 and gain>0 and full_auc-base_auc>=.02 and sum(float(x["gain_bits"])>0 for x in foldrows)>=4)
 # Null is deliberately not entered unless every cheaper frozen prerequisite
 # passes; this sequential stop was frozen to prioritize COORDINATOR first.
 outrow={"role":"COORDINATOR","domain":"PCEEC2","n":len(enc),"role_positives":int(role.sum()),"relation_positives":int(rel.sum()),"role_auc":role_auc,"role_gain_bits":role_gain,"source_overlap_auc":source_auc,"deterministic_overlap_auc":det_auc,"source_relation_auc":base_auc,"role_plus_relation_auc":full_auc,"auc_increment":full_auc-base_auc,"relation_gain_bits":gain,"positive_held_collections":sum(float(x["gain_bits"])>0 for x in foldrows),"held_collections":len(foldrows),"pre_null_gate_pass":int(prepass),"joint_max_family_p":"NOT_RUN_PREREQUISITE_FAILURE" if not prepass else "PENDING_NULL"}
 write(ART/"gdt384_priority_coordinator.tsv",[outrow]);write(ART/"gdt384_priority_coordinator_folds.tsv",foldrows)
 predrows=[{"element_key":x["element_key"],"held_collection":folds[i],"role_y":int(role[i]),"relation_y":int(rel[i]),"p_role_baseline":base_role[i],"p_role":p_role[i],"p_source_relation":p_source[i],"p_deterministic_overlap":p_deterministic[i],"p_role_plus_relation":p_relation[i]} for i,x in enumerate(enc)]
 writegz(ART/"gdt384_priority_predictions.tsv.gz",predrows)
 status="PRIORITY_RELATION_FAILED_STOP_BEFORE_OTHER_ROLES" if not prepass else "PRIORITY_PRE_NULL_PASS_NULL_REQUIRED"
 result={"schema":"GDT384_PRIORITY_RESULT_V1","status":status,"priority":outrow,"other_roles_scored":False,"null_run":False,"stage_a_pass":False,"voynich_stage_b_authorized":False,"voynich_rows_read":0,"gdt381_target_artifacts_read":False,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [FREEZE,ENC,ORACLE,REL]},"outputs":{str((ART/n).relative_to(ROOT)):sha(ART/n) for n in ["gdt384_priority_coordinator.tsv","gdt384_priority_coordinator_folds.tsv","gdt384_priority_predictions.tsv.gz"]},"implementation":{str((BASE/"src/run_priority_coordinator.py").relative_to(ROOT)):sha(BASE/"src/run_priority_coordinator.py")},"claim_ceiling":"COMPARATOR_PRIORITY_ROLE_RELATION_ONLY"};result["content_hash"]=content(result);(ART/"gdt384_priority_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,**outrow},sort_keys=True))
if __name__=="__main__":main()

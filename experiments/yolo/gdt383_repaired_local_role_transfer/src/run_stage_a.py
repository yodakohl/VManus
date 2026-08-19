#!/usr/bin/env python3
"""Run frozen GDT383 Stage A. No Voynich source is permitted."""
from __future__ import annotations
import csv,gzip,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer";ART=BASE/"artifacts";G382=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts";G378=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
ENC=G382/"gdt382_voynichified_observation_layer.tsv.gz";ORACLE=G378/"gdt378_hidden_oracle.tsv.gz";FREEZE=ART/"gdt383_stage_a_freeze.json"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
REPS=["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN"]
OUTCOMES=["POST_RETURN_ABC_A","POST_PERSIST_THEN_EXIT","POST_HOMOGENEOUS_3","POST_LOW_DIVERSITY_3","POST_ANY_BOUNDARY_3","POST_WRAPPER_CHANGE_3","POST_RENDERER_STABLE_3","POST_TERMINUS_3"]
CHANNELS=["FREQUENCY","RECURRENCE","LINE_FIELD_POSITION","RECORD_RELATIVE_POSITION","BOUNDARY_CLOSURE","PREVIOUS_STATE","RECORD_LENGTH"]
MODES=["FREE_TOKEN","PREFIX","SUFFIX","WRAPPER_ALTERNATION","BOUNDARY_CHOICE","POSITIONAL_ALTERNATION","ZERO_SUPPLETIVE"]
DEV={"COREMA","PCEEC2","CURIOUS_CURES"};CONF={"HARLEIAN_COOKERY","QUINTE_ESSENCE"}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hx(*x,n=10):return hashlib.sha256("\x1f".join(map(str,x)).encode()).hexdigest()[:n]
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def readgz(p):
 with gzip.open(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sigmoid(x):
 x=np.clip(np.asarray(x,float),-30,30);return 1/(1+np.exp(-x))
def logit(x):
 x=np.clip(np.asarray(x,float),1e-7,1-1e-7);return np.log(x/(1-x))
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
def bits(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-9,1-1e-9);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def binint(v,cuts):
 v=int(v)
 for i,c in enumerate(cuts):
  if v<=c:return str(i)
 return str(len(cuts))

def folds_for(rows):
 cols=defaultdict(set);mx=Counter()
 for r in rows:cols[r["domain"]].add(r["collection_id"]);mx[r["domain"]]=max(mx[r["domain"]],int(r["record_ordinal"])+1)
 out=[]
 for r in rows:
  d=r["domain"];sub=r["collection_id"] if len(cols[d])>1 else "BLOCK"+str(min(4,int(r["record_ordinal"])*5//max(1,mx[d])));out.append(d+"::"+sub)
 return out

def prepare(rows):
 gf=Counter((r["domain"],r["source_token_equality"]) for r in rows);byrec=defaultdict(list)
 for i,r in enumerate(rows):byrec[(r["domain"],r["collection_id"],r["record_id"])].append(i)
 rep={k:[None]*len(rows) for k in REPS};ch={k:[None]*len(rows) for k in CHANNELS};allch=[None]*len(rows);source_stratum=[None]*len(rows);pivots=[];ys={k:{} for k in OUTCOMES}
 for key,ids in byrec.items():
  ids.sort(key=lambda i:int(rows[i]["element_ordinal"]));m=len(ids)
  for j,i in enumerate(ids):
   r=rows[i];prev=[rows[x] for x in ids[max(0,j-2):j]];span=prev+[r]
   rep["HOST_IDENTITY"][i]=("H="+r["host_id"],"HL="+str(len(r["host_id"])))
   g=r["rendered_group"];rep["COMPLETE_RENDERED_GROUP"][i]=("G="+g,"GP="+g[:2],"GS="+g[-2:],"GL="+str(len(g)))
   rep["CONSTRUCTION_STATE"][i]=("W="+r["wrapper_state"],"P="+r["positional_state"],"B="+r["boundary_state"],"R="+r["record_state"],"V="+r["renderer_variant"],"WF="+r["within_field_index"])
   rep["COMPOSITE_JOINT_STATE"][i]=("J="+r["composite_joint_id"],)
   rep["SHORT_CONSTRUCTION_SPAN"][i]=("SS="+"|".join(x["wrapper_state"]+x["boundary_state"]+x["renderer_variant"] for x in span),"SH="+"|".join(x["host_id"] for x in span))
   ch["FREQUENCY"][i]=("F="+binint(gf[(r["domain"],r["source_token_equality"])],[1,2,4,8,16,32,64]),)
   ch["RECURRENCE"][i]=("C="+binint(r["within_record_frequency"],[1,2,4]),)
   ch["LINE_FIELD_POSITION"][i]=("FI="+r["field_index"],"WF="+r["within_field_index"])
   ch["RECORD_RELATIVE_POSITION"][i]=("P="+r["positional_state"],)
   ch["BOUNDARY_CLOSURE"][i]=("B="+r["boundary_state"],)
   ch["PREVIOUS_STATE"][i]=("PREV="+r["previous_host"],)
   ch["RECORD_LENGTH"][i]=("RL="+binint(r["record_element_count"],[8,16,32,64]),)
   allch[i]=tuple(v for name in CHANNELS for v in ch[name][i]);source_stratum[i]=(r["positional_state"],r["boundary_state"],binint(r["record_element_count"],[8,16,32,64]),binint(gf[(r["domain"],r["source_token_equality"])],[1,2,4,8,16,32,64]),binint(r["within_record_frequency"],[1,2,4]),binint(r["field_index"],[0,1,2,4,8]))
   if j+3<m:
    a,b,c=(rows[ids[j+k]] for k in [1,2,3]);pivots.append(i);hs=[a["host_id"],b["host_id"],c["host_id"]]
    vals={"POST_RETURN_ABC_A":int(hs[0]==hs[2] and hs[0]!=hs[1]),"POST_PERSIST_THEN_EXIT":int(hs[0]==hs[1] and hs[1]!=hs[2]),"POST_HOMOGENEOUS_3":int(len(set(hs))==1),"POST_LOW_DIVERSITY_3":int(len(set(hs))<=2),"POST_ANY_BOUNDARY_3":int(any(x["boundary_state"]!="B00" for x in [a,b,c])),"POST_WRAPPER_CHANGE_3":int(len({x["wrapper_state"] for x in [a,b,c]})>1),"POST_RENDERER_STABLE_3":int(len({x["renderer_variant"] for x in [a,b,c]})==1),"POST_TERMINUS_3":int(any(x["positional_state"]=="END" for x in [a,b,c]))}
    for name,v in vals.items():ys[name][i]=v
 return rep,ch,allch,source_stratum,pivots,ys

def nb_crossfit(y,features,rows,folds,regime="LOCAL"):
 n=len(y);pred=np.zeros(n,float);excls=folds if regime=="LOCAL" else [r["domain"] for r in rows];groups=defaultdict(list)
 for i,f in enumerate(excls):groups[f].append(i)
 tc=Counter();hc=Counter();tot=Counter();held=Counter();tv=Counter();hv=Counter();voc=defaultdict(set)
 for i,r in enumerate(rows):
  base=r["domain"] if regime=="LOCAL" else "ALL";ex=folds[i] if regime=="LOCAL" else r["domain"];c=y[i];tc[(base,c)]+=1;hc[(ex,c)]+=1
  for k,v in enumerate(features[i]):tot[(base,c,k,v)]+=1;held[(ex,c,k,v)]+=1;tv[(base,k,v)]+=1;hv[(ex,k,v)]+=1;voc[(base,k)].add(v)
 for ex,test in groups.items():
  d=rows[test[0]]["domain"];base=d if regime=="LOCAL" else "ALL";n1=tc[(base,1)]-hc[(ex,1)];n0=tc[(base,0)]-hc[(ex,0)];prior=math.log((n1+1)/(n0+1));Vs=[]
  for k in range(len(features[0])):Vs.append(len(voc[(base,k)])-sum(hv[(ex,k,v)]==tv[(base,k,v)] for v in voc[(base,k)] if hv[(ex,k,v)])+1)
  for i in test:
   z=prior
   for k,v in enumerate(features[i]):z+=math.log((tot[(base,1,k,v)]-held[(ex,1,k,v)]+1)/(n1+Vs[k]))-math.log((tot[(base,0,k,v)]-held[(ex,0,k,v)]+1)/(n0+Vs[k]))
   pred[i]=float(sigmoid(z))
 return pred

def combine(ps):return sigmoid(np.median(np.vstack([logit(p) for p in ps]),axis=0))
def combine2(a,b):return sigmoid((logit(a)+logit(b))/2)
def role_metrics(y,p,p0,rows):
 by=defaultdict(list)
 for i,r in enumerate(rows):by[r["domain"]].append(i)
 aucs={};gains={}
 for d,ids in by.items():
  yy=[y[i] for i in ids]
  if 0<sum(yy)<len(yy):aucs[d]=auc(yy,[p[i] for i in ids]);gains[d]=bits(yy,[p0[i] for i in ids])-bits(yy,[p[i] for i in ids])
 return {"macro_auc":float(np.mean(list(aucs.values()))),"gain_bits":sum(gains.values()),"positive_domains":sum(v>0 for v in gains.values()),"aucs":aucs,"gains":gains}

OUTCOME_COMPONENT_CACHE={}
def outcome_predict(yout,yrole,prole,rows,folds,strata,pivotset,cache_key):
 """Fold-local source baseline and role-conditioned mixture; test roles inferred."""
 if cache_key in OUTCOME_COMPONENT_CACHE:
  p0,q0,q1=OUTCOME_COMPONENT_CACHE[cache_key];return p0,{i:(1-prole[i])*q0[i]+prole[i]*q1[i] for i in pivotset}
 p0={};q0={};q1={};groups=defaultdict(list);dn=Counter();dy=Counter();fn=Counter();fy=Counter();bn=Counter();by=Counter();fbn=Counter();fby=Counter();rn=Counter();ry=Counter();frn=Counter();fry=Counter();brn=Counter();bry=Counter();fbrn=Counter();fbry=Counter();keys=defaultdict(set)
 for i in pivotset:
  d=rows[i]["domain"];f=folds[i];k=strata[i];rv=yrole[i];groups[f].append(i);dn[d]+=1;dy[d]+=yout[i];fn[f]+=1;fy[f]+=yout[i];bn[(d,k)]+=1;by[(d,k)]+=yout[i];fbn[(f,k)]+=1;fby[(f,k)]+=yout[i];rn[(d,rv)]+=1;ry[(d,rv)]+=yout[i];frn[(f,rv)]+=1;fry[(f,rv)]+=yout[i];brn[(d,k,rv)]+=1;bry[(d,k,rv)]+=yout[i];fbrn[(f,k,rv)]+=1;fbry[(f,k,rv)]+=yout[i];keys[d].add(k)
 for fold,test in groups.items():
  d=rows[test[0]]["domain"];train_n=dn[d]-fn[fold];train_y=dy[d]-fy[fold];glob=(train_y+1)/(train_n+2);gb={};gr={}
  for key in keys[d]:
   base_n=bn[(d,key)]-fbn[(fold,key)];base_y=by[(d,key)]-fby[(fold,key)]
   if base_n:gb[key]=(base_y+2*glob)/(base_n+2)
   for rv in [0,1]:
    global_n=rn[(d,rv)]-frn[(fold,rv)];global_y=ry[(d,rv)]-fry[(fold,rv)];pr=(global_y+1)/(global_n+2);role_n=brn[(d,key,rv)]-fbrn[(fold,key,rv)];role_y=bry[(d,key,rv)]-fbry[(fold,key,rv)];gr[(key,rv)]=(role_y+4*pr)/(role_n+4)
  for i in test:
   base=gb.get(strata[i],glob);p0[i]=base;q0[i]=gr.get((strata[i],0),base);q1[i]=gr.get((strata[i],1),base)
 OUTCOME_COMPONENT_CACHE[cache_key]=(p0,q0,q1);return p0,{i:(1-prole[i])*q0[i]+prole[i]*q1[i] for i in pivotset}

def main():
 freeze=json.loads(FREEZE.read_text());assert freeze["status"]=="FROZEN_BEFORE_POSITIVE_CONTROL_EVALUATION" and not freeze["voynich_stage_b_authorized"] and not freeze["gdt381_target_artifacts_allowed"]
 rows=readgz(ENC);om={x["element_key"]:x for x in readgz(ORACLE)};oracle=[om[x["element_key"]] for x in rows];assert all("f84" not in (x["domain"]+x["collection_id"]+x["record_id"]+x["element_key"]).lower() for x in rows)
 folds=folds_for(rows);rep,ch,allch,strata,pivots,outs=prepare(rows);constant=[("CONST",)]*len(rows);domains=np.array([r["domain"] for r in rows]);role_rows=[];weight_rows=[];channel_rows=[];control_rows=[];scores={};pred_cache={}
 for endpoint in ENDPOINTS:
  y=[int(x[endpoint]) for x in oracle];p0=nb_crossfit(y,constant,rows,folds,"LOCAL");pc=nb_crossfit(y,allch,rows,folds,"LOCAL");local=[];univ=[]
  for rn in REPS:
   pl=nb_crossfit(y,rep[rn],rows,folds,"LOCAL");pu=nb_crossfit(y,rep[rn],rows,folds,"UNIVERSAL");local.append(pl);univ.append(pu);m=role_metrics(y,pl,p0,rows);weight_rows.append({"endpoint":endpoint,"resolution":rn,"local_macro_auc":m["macro_auc"],"local_gain_bits":m["gain_bits"],"combination_weight":"FIXED_MEDIAN_LOG_ODDS"})
  ph=combine(local);pe=combine2(ph,pc);pu=combine(univ);pr=sigmoid(logit(ph)-logit(pc)+logit(p0));scores[(endpoint,"EVIDENCE")]=pe;scores[(endpoint,"OMITTED")]=ph;scores[(endpoint,"CONDITIONED_NUISANCE")]=pr;scores[(endpoint,"EXACT_JOINT")]=local[REPS.index("COMPOSITE_JOINT_STATE")];scores[(endpoint,"UNIVERSAL")]=pu;pred_cache[(endpoint,"CONST")]=p0
  for name,p in [("HIERARCHICAL_EVIDENCE",pe),("HIERARCHICAL_OMITTED",ph),("HIERARCHICAL_CONDITIONED_NUISANCE",pr),("EXACT_JOINT_ONLY",scores[(endpoint,"EXACT_JOINT")]),("STRICT_UNIVERSAL",pu)]:
   m=role_metrics(y,p,p0,rows);role_rows.append({"endpoint":endpoint,"model":name,"macro_auc":m["macro_auc"],"gain_bits":m["gain_bits"],"positive_domains":m["positive_domains"],"domain_aucs_json":json.dumps(m["aucs"],sort_keys=True,separators=(",",":")),"domain_gains_json":json.dumps(m["gains"],sort_keys=True,separators=(",",":"))})
  for cn in CHANNELS:
   px=nb_crossfit(y,ch[cn],rows,folds,"LOCAL");ev=combine2(ph,px);res=sigmoid(logit(ph)-logit(px)+logit(p0))
   for tr,p in [("EVIDENCE",ev),("CONDITIONED_NUISANCE",res),("OMITTED",ph)]:
    m=role_metrics(y,p,p0,rows);channel_rows.append({"endpoint":endpoint,"channel":cn,"treatment":tr,"macro_auc":m["macro_auc"],"gain_bits":m["gain_bits"],"positive_domains":m["positive_domains"]})
  for mode in MODES:
   mark=[("MARK="+(mode if y[i] else "UNMARKED"),"DOMAIN_MARK="+(hx(rows[i]["domain"],endpoint,mode,n=6) if y[i] else "NONE")) for i in range(len(rows))];pm=nb_crossfit(y,mark,rows,folds,"LOCAL");pp=combine2(pe,pm);m=role_metrics(y,pp,p0,rows);control_rows.append({"endpoint":endpoint,"realization_mode":mode,"macro_auc":m["macro_auc"],"gain_bits":m["gain_bits"],"positive_domains":m["positive_domains"]})
 # Role max-family null over fixed cross-fitted evidence scores.
 rcache={};obs_auc={}
 for e in ENDPOINTS:
  for d in sorted(set(domains)):
   ids=np.where(domains==d)[0];yy=np.array([int(oracle[i][e]) for i in ids]);
   if 0<yy.sum()<len(yy):rcache[(e,d)]=(ids,rankdata(scores[(e,"EVIDENCE")][ids]));obs_auc[(e,d)]=auc(yy,scores[(e,"EVIDENCE")][ids])
 permstr=defaultdict(list)
 for i,r in enumerate(rows):permstr[(r["domain"],folds[i],binint(r["record_element_count"],[8,16,32,64]),r["positional_state"],r["boundary_state"])].append(i)
 rolemax=[]
 for world in range(512):
  rng=np.random.default_rng(383000+world);wm=[]
  for e in ENDPOINTS:
   yp=np.array([int(x[e]) for x in oracle])
   for ids in permstr.values():yp[ids]=rng.permutation(yp[ids])
   av=[]
   for d in sorted(set(domains)):
    if (e,d) not in rcache:continue
    ids,rk=rcache[(e,d)];yy=yp[ids];n1=int(yy.sum());n0=len(yy)-n1
    if n1 and n0:av.append(float((rk[yy==1].sum()-n1*(n1+1)/2)/(n1*n0)))
   if av:wm.append(float(np.mean(av)))
  rolemax.append(max(wm) if wm else .5)
 for row in role_rows:
  if row["model"]=="HIERARCHICAL_EVIDENCE":row["max_family_p"]=(1+sum(x>=float(row["macro_auc"]) for x in rolemax))/513
  else:row["max_family_p"]="NA"
 # Strict post-pivot outcomes and source-overlap audit.
 pivotset=set(pivots);outcome_rows=[];down=[];selection={}
 source_feats=[tuple(list(rep["CONSTRUCTION_STATE"][i])+list(allch[i])) for i in range(len(rows))]
 for on in OUTCOMES:
  yo=[outs[on].get(i,0) for i in range(len(rows))];subrows=[rows[i] for i in pivots];subfolds=[folds[i] for i in pivots];suby=[yo[i] for i in pivots];subfeat=[source_feats[i] for i in pivots];subp=nb_crossfit(suby,subfeat,subrows,subfolds,"LOCAL");ps=np.zeros(len(rows),float)
  for i,v in zip(pivots,subp):ps[i]=v
  pred_cache[(on,"SOURCE")]=ps
  for d in sorted(set(domains)):
   ids=[i for i in pivots if rows[i]["domain"]==d];yy=[yo[i] for i in ids];a=auc(yy,[ps[i] for i in ids]) if 0<sum(yy)<len(yy) else float("nan");outcome_rows.append({"outcome":on,"domain":d,"n":len(ids),"positives":sum(yy),"source_only_auc":a if math.isfinite(a) else "NA"})
 # Compute every endpoint/outcome/treatment fold-local latent-role mixture.
 for e in ENDPOINTS:
  yr=[int(x[e]) for x in oracle];cands=[]
  for on in OUTCOMES:
   yo=[outs[on].get(i,0) for i in range(len(rows))];devauc=[float(x["source_only_auc"]) for x in outcome_rows if x["outcome"]==on and x["domain"] in DEV and x["source_only_auc"]!="NA"];
   eligible=bool(devauc) and float(np.mean(devauc))<=.65
   for tr in ["EVIDENCE","CONDITIONED_NUISANCE","OMITTED"]:
    p0,p1=outcome_predict(yo,yr,scores[(e,tr)],rows,folds,strata,pivotset,(e,on));gains={};aucs={}
    for d in sorted(set(domains)):
     ids=[i for i in pivots if rows[i]["domain"]==d];yy=[yo[i] for i in ids]
     if not ids:continue
     gains[d]=bits(yy,[p0[i] for i in ids])-bits(yy,[p1[i] for i in ids]);aucs[d]=auc(yy,[p1[i] for i in ids]) if 0<sum(yy)<len(yy) else float("nan")
    devgain=sum(gains.get(d,0) for d in DEV);row={"endpoint":e,"outcome":on,"treatment":tr,"development_eligible":int(eligible),"development_gain_bits":devgain,"confirmation_harleian_gain_bits":gains.get("HARLEIAN_COOKERY",0),"confirmation_quinte_gain_bits":gains.get("QUINTE_ESSENCE",0),"confirmation_total_gain_bits":sum(gains.get(d,0) for d in CONF),"domain_gains_json":json.dumps(gains,sort_keys=True,separators=(",",":")),"domain_aucs_json":json.dumps(aucs,sort_keys=True,separators=(",",":")),"selected_on_development":0,"confirmation_max_family_p":"NA"};down.append(row)
    if eligible:cands.append((devgain,-OUTCOMES.index(on),-["EVIDENCE","CONDITIONED_NUISANCE","OMITTED"].index(tr),on,tr,p0,p1))
  if cands:
   best=max(cands,key=lambda x:x[:3]);selection[e]=(best[3],best[4],best[5],best[6]);next(x for x in down if x["endpoint"]==e and x["outcome"]==best[3] and x["treatment"]==best[4])["selected_on_development"]=1
 # Confirmation max-family null across the six dev-selected tests.
 confids=[i for i in pivots if rows[i]["domain"] in CONF];downmax=[];observed={}
 for e,(on,tr,p0,p1) in selection.items():
  yy=[outs[on][i] for i in confids];observed[e]=bits(yy,[p0[i] for i in confids])-bits(yy,[p1[i] for i in confids])
 for world in range(512):
  rng=np.random.default_rng(383800+world);wm=[]
  for e,(on,tr,p0,p1) in selection.items():
   yp={i:outs[on][i] for i in confids};ng=defaultdict(list)
   for i in confids:ng[(rows[i]["domain"],folds[i],strata[i])].append(i)
   for ids in ng.values():
    vals=rng.permutation([yp[i] for i in ids])
    for i,v in zip(ids,vals):yp[i]=int(v)
   yy=[yp[i] for i in confids];wm.append(bits(yy,[p0[i] for i in confids])-bits(yy,[p1[i] for i in confids]))
  downmax.append(max(wm) if wm else 0)
 for e,val in observed.items():
  row=next(x for x in down if x["endpoint"]==e and x["selected_on_development"]==1);row["confirmation_max_family_p"]=(1+sum(x>=val for x in downmax))/513
 # Gates.
 role_gate={}
 for e in ENDPOINTS:
  q=next(x for x in role_rows if x["endpoint"]==e and x["model"]=="HIERARCHICAL_EVIDENCE");j=next(x for x in role_rows if x["endpoint"]==e and x["model"]=="EXACT_JOINT_ONLY");u=next(x for x in role_rows if x["endpoint"]==e and x["model"]=="STRICT_UNIVERSAL");role_gate[e]=float(q["macro_auc"])>=.80 and float(q["gain_bits"])>0 and int(q["positive_domains"])>=3 and float(q["macro_auc"])-float(j["macro_auc"])>=.02 and float(q["macro_auc"])-float(u["macro_auc"])>=.10 and float(q["max_family_p"])<=.05
 controls_pass=all(float(x["macro_auc"])>=.90 and float(x["gain_bits"])>0 for x in control_rows) and len(control_rows)==42
 downstream_gate={}
 for e in ENDPOINTS:
  if e not in selection:downstream_gate[e]=False;continue
  on,tr,_,_=selection[e];row=next(x for x in down if x["endpoint"]==e and x["selected_on_development"]==1);confauc=[float(x["source_only_auc"]) for x in outcome_rows if x["outcome"]==on and x["domain"] in CONF and x["source_only_auc"]!="NA"]
  downstream_gate[e]=len(confauc)==2 and float(np.mean(confauc))<=.65 and float(row["confirmation_harleian_gain_bits"])>0 and float(row["confirmation_quinte_gain_bits"])>0 and float(row["confirmation_max_family_p"])<=.05
 stage_a_pass=all(role_gate.values()) and controls_pass and sum(downstream_gate.values())>=4 and downstream_gate.get("COORDINATOR",False)
 nullrows=[{"family":"ROLE_MEMBERSHIP","world":i,"world_max":v} for i,v in enumerate(rolemax)]+[{"family":"SELECTED_DOWNSTREAM","world":i,"world_max":v} for i,v in enumerate(downmax)]
 write(ART/"gdt383_role_recovery.tsv",role_rows);write(ART/"gdt383_resolution_diagnostics.tsv",weight_rows);write(ART/"gdt383_channel_treatments.tsv",channel_rows);write(ART/"gdt383_realization_controls.tsv",control_rows);write(ART/"gdt383_outcome_overlap.tsv",outcome_rows);write(ART/"gdt383_downstream_transfer.tsv",down);write(ART/"gdt383_null_worlds.tsv",nullrows)
 outsfiles=[ART/x for x in ["gdt383_role_recovery.tsv","gdt383_resolution_diagnostics.tsv","gdt383_channel_treatments.tsv","gdt383_realization_controls.tsv","gdt383_outcome_overlap.tsv","gdt383_downstream_transfer.tsv","gdt383_null_worlds.tsv"]]
 result={"schema":"GDT383_STAGE_A_RESULT_V1","status":"STAGE_A_PASS_TARGET_FREEZE_AUTHORIZED" if stage_a_pass else "STAGE_A_FAILED_STOP_BEFORE_VOYNICH","rows":len(rows),"records":len({(r['domain'],r['collection_id'],r['record_id']) for r in rows}),"pivots":len(pivots),"role_gates":role_gate,"realization_gate_pass":controls_pass,"downstream_gates":downstream_gate,"downstream_roles_passing":sum(downstream_gate.values()),"priority_coordinator_pass":downstream_gate.get("COORDINATOR",False),"stage_a_pass":stage_a_pass,"voynich_stage_b_authorized":stage_a_pass,"voynich_rows_read":0,"gdt381_target_artifacts_read":False,"semantic_state":"UNASSIGNED","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [ENC,ORACLE,FREEZE]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outsfiles},"implementation":{str((BASE/'src/run_stage_a.py').relative_to(ROOT)):sha(BASE/'src/run_stage_a.py')},"claim_ceiling":"COMPARATOR_POSITIVE_CONTROL_REPAIRED_INSTRUMENT_ONLY"};result["content_hash"]=content(result);(ART/"gdt383_stage_a_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"role_gates":role_gate,"realizations":controls_pass,"downstream":downstream_gate,"pivots":len(pivots)},sort_keys=True))
if __name__=="__main__":main()

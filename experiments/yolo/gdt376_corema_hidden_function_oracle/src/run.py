#!/usr/bin/env python3
"""Evaluate frozen form-blind detectors against held CoReMA oracle labels."""
from __future__ import annotations
import csv, hashlib, json, math, random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'experiments/yolo/gdt376_corema_hidden_function_oracle';ART=BASE/'artifacts'
OBS=ART/'gdt376_observation_layer.tsv';ORACLE=ROOT/'gdt176_corema_role_oracle.tsv';DESIGN=ART/'gdt376_design_freeze.json'
CONTRACT=ROOT/'experiments/yolo/gdt375_comparator_derived_functional_roadmap/artifacts/gdt375_detector_contract.tsv'
TARGETS=['ALTERNATIVE','TIME','REF','CLOSER','EXCLUSION','ANALOGY','COMPARISON','PREDICATE_HEAD_WITH_DEPENDENTS','HIGH_VALENCY_HEAD','PARENTED_DEPENDENT','ANY_FUNCTIONAL_CLASS']

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def read_tsv(p:Path):
    with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write_tsv(p:Path,rows):
    with p.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sigmoid(x):return np.where(x>=0,1/(1+np.exp(-np.clip(x,-40,40))),np.exp(np.clip(x,-40,40))/(1+np.exp(np.clip(x,-40,40))))
def fit_logistic(X,y,l2=4.0):
    X=np.asarray(X,float);y=np.asarray(y,float);mu=X[:,1:].mean(0);sd=X[:,1:].std(0);sd[sd<1e-8]=1
    Z=X.copy();Z[:,1:]=(Z[:,1:]-mu)/sd
    b=np.zeros(Z.shape[1]);pen=np.ones(len(b))*l2;pen[0]=0
    for _ in range(45):
        p=sigmoid(Z@b);w=np.maximum(p*(1-p),1e-5)
        H=(Z.T*w)@Z+np.diag(pen);g=Z.T@(y-p)-pen*b
        try:step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError:step=np.linalg.lstsq(H,g,rcond=None)[0]
        b+=step
        if np.max(np.abs(step))<1e-7:break
    return b,mu,sd
def predict(model,X):
    b,mu,sd=model;Z=np.asarray(X,float).copy();Z[:,1:]=(Z[:,1:]-mu)/sd;return np.clip(sigmoid(Z@b),1e-6,1-1e-6)
def bits(y,p):
    y=np.asarray(y);p=np.clip(np.asarray(p),1e-9,1-1e-9);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def auc(y,p):
    y=np.asarray(y);p=np.asarray(p);pos=np.where(y==1)[0];neg=np.where(y==0)[0]
    if not len(pos) or not len(neg):return float('nan')
    order=np.argsort(p,kind='stable');ranks=np.empty(len(p),float);i=0
    while i<len(order):
        j=i+1
        while j<len(order) and p[order[j]]==p[order[i]]:j+=1
        ranks[order[i:j]]=(i+j+1)/2;i=j
    return float((ranks[pos].sum()-len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg)))
def ap(y,p):
    y=np.asarray(y);order=np.argsort(-np.asarray(p),kind='stable');total=int(y.sum())
    if not total:return float('nan')
    hit=0;s=0
    for rank,i in enumerate(order,1):
        if y[i]:hit+=1;s+=hit/rank
    return s/total
def bucket_len(n):return 'A' if n<=8 else 'B' if n<=16 else 'C' if n<=32 else 'D'
def bucket_tok(n):return '0' if n==0 else '1' if n==1 else '2' if n<=3 else '4+'

def labels(oracle):
    byrec=defaultdict(list)
    for i,r in enumerate(oracle):byrec[(r['collection_id'],r['recipe_id'])].append((i,r))
    out={t:np.zeros(len(oracle),dtype=int) for t in TARGETS}
    for rec,values in byrec.items():
        values.sort(key=lambda z:int(z[1]['element_ordinal']));child=Counter(int(r['parent_instruction_ordinal']) for _,r in values if int(r['parent_instruction_ordinal'])>0);instruction_no=0
        for i,r in values:
            role=r['role'];flag=r['annotation_flags']
            for t in ['ALTERNATIVE','TIME','REF','CLOSER']:out[t][i]=role==t
            for t in ['EXCLUSION','ANALOGY','COMPARISON']:out[t][i]=flag==t.lower()
            if role=='INSTRUCTION':
                instruction_no+=1;out['PREDICATE_HEAD_WITH_DEPENDENTS'][i]=child[instruction_no]>0;out['HIGH_VALENCY_HEAD'][i]=child[instruction_no]>=2
            out['PARENTED_DEPENDENT'][i]=int(r['parent_instruction_ordinal'])>0
            out['ANY_FUNCTIONAL_CLASS'][i]=role in {'ALTERNATIVE','TIME','REF','CLOSER'} or flag in {'exclusion','analogy','comparison'}
    return out

def static_features(obs):
    byrec=defaultdict(list);bycol=defaultdict(list)
    for i,r in enumerate(obs):byrec[(r['collection_id'],r['recipe_id'])].append(i);bycol[r['collection_id']].append(i)
    record_order={}
    for c,idxs in bycol.items():
        recs=sorted({(int(obs[i]['recipe_ordinal']),obs[i]['recipe_id']) for i in idxs});record_order[c]=[x[1] for x in recs]
    F=[None]*len(obs)
    for (c,rec),idxs in byrec.items():
        idxs.sort(key=lambda i:int(obs[i]['element_ordinal']));forms=[obs[i]['opaque_form_id'] for i in idxs];n=len(idxs);cnt=Counter(forms);positions=defaultdict(list)
        for j,f in enumerate(forms):positions[f].append(j)
        ro=record_order[c];rp=ro.index(rec);prevset=set(obs[i]['opaque_form_id'] for i in byrec[(c,ro[rp-1])]) if rp else set();nextset=set(obs[i]['opaque_form_id'] for i in byrec[(c,ro[rp+1])]) if rp+1<len(ro) else set();curset=set(forms)
        prevjac=len(curset&prevset)/max(1,len(curset|prevset));nextjac=len(curset&nextset)/max(1,len(curset|nextset))
        for j,i in enumerate(idxs):
            f=forms[j];ps=positions[f];before=[x for x in ps if x<j];after=[x for x in ps if x>j]
            nuisance=[1.,math.log1p(n),j/max(1,n-1),(j/max(1,n-1))**2,math.log1p(int(obs[i]['direct_token_count'])),float(j==0),float(j==n-1),math.log1p(int(obs[i]['recipe_ordinal']))]
            structure=[
              float(j>0 and forms[j-1]==f),float(j+1<n and forms[j+1]==f),float(bool(before)),float(bool(after)),math.log1p(len(before)),math.log1p(len(after)),
              (j-before[-1])/max(1,n) if before else 1.,(after[0]-j)/max(1,n) if after else 1.,math.log1p(cnt[f]),len(curset)/max(1,n),
              float(f in prevset),float(f in nextset),prevjac,nextjac,len(set(forms[:j]))/max(1,n),len(set(forms[j+1:]))/max(1,n),
              float(j>0 and j+1<n and forms[j-1]==forms[j+1]),float(j>=2 and forms[j-2]==f),float(j+2<n and forms[j+2]==f),
              float(j>0 and forms[j-1] not in set(forms[:j-1])),float(j+1<n and forms[j+1] not in set(forms[:j+1])),
            ]
            F[i]=(nuisance,structure)
    return F,byrec

def learned_form_features(obs,train,test):
    stats=defaultdict(lambda:{'n':0,'pos':[],'prev':set(),'next':set(),'records':set()})
    byrec=defaultdict(list)
    for i in train:byrec[(obs[i]['collection_id'],obs[i]['recipe_id'])].append(i)
    for key,idxs in byrec.items():
        idxs.sort(key=lambda i:int(obs[i]['element_ordinal']));forms=[obs[i]['opaque_form_id'] for i in idxs];n=len(idxs)
        for j,i in enumerate(idxs):
            s=stats[forms[j]];s['n']+=1;s['pos'].append(j/max(1,n-1));s['records'].add(key)
            if j:s['prev'].add(forms[j-1])
            if j+1<n:s['next'].add(forms[j+1])
    out={}
    for i in test:
        s=stats.get(obs[i]['opaque_form_id']);
        if not s:out[i]=[0.,0.,0.,0.,0.5,0.]
        else:
            pos=s['pos'];out[i]=[math.log1p(s['n']),math.log1p(len(s['records'])),math.log1p(len(s['prev'])),math.log1p(len(s['next'])),sum(pos)/len(pos),float(np.std(pos))]
    return out,stats

def main():
    design=json.loads(DESIGN.read_text());assert design['status']=='FROZEN_BEFORE_HELD_ORACLE_EVALUATION';assert sha(OBS)==design['observation_sha256'] and sha(ORACLE)==design['oracle_commitment_sha256']
    obs=read_tsv(OBS);oracle=read_tsv(ORACLE);assert len(obs)==len(oracle);Y=labels(oracle);static,byrec=static_features(obs);collections=design['collections'];valid=np.array([r['observable_surface']=='1' for r in obs])
    foldrows=[];predrows=[];allpred={t:{} for t in TARGETS}
    for target in TARGETS:
      yall=Y[target]
      for held in collections:
        train=[i for i,r in enumerate(obs) if valid[i] and r['collection_id']!=held];test=[i for i,r in enumerate(obs) if valid[i] and r['collection_id']==held]
        learned_train,stats=learned_form_features(obs,train,train);learned_test,_=learned_form_features(obs,train,test)
        Xn_tr=[static[i][0] for i in train];Xn_te=[static[i][0] for i in test]
        Xs_tr=[static[i][0]+static[i][1]+learned_train[i] for i in train];Xs_te=[static[i][0]+static[i][1]+learned_test[i] for i in test]
        prior=(int(yall[train].sum())+0.5)/(len(train)+1);formpos=Counter();formn=Counter()
        for i in train:formpos[obs[i]['opaque_form_id']]+=int(yall[i]);formn[obs[i]['opaque_form_id']]+=1
        pid_tr=[(formpos[obs[i]['opaque_form_id']]+2*prior)/(formn[obs[i]['opaque_form_id']]+2) for i in train]
        pid_te=[(formpos[obs[i]['opaque_form_id']]+2*prior)/(formn[obs[i]['opaque_form_id']]+2) for i in test]
        Xi_tr=[x+[math.log(max(1e-6,p)/max(1e-6,1-p))] for x,p in zip(Xs_tr,pid_tr)];Xi_te=[x+[math.log(max(1e-6,p)/max(1e-6,1-p))] for x,p in zip(Xs_te,pid_te)]
        models={'PREVALENCE':np.full(len(test),prior),'NUISANCE':predict(fit_logistic(Xn_tr,yall[train]),Xn_te),'OPAQUE_ID':np.asarray(pid_te),'STRUCTURE':predict(fit_logistic(Xs_tr,yall[train]),Xs_te),'STRUCTURE_PLUS_ID':predict(fit_logistic(Xi_tr,yall[train]),Xi_te)}
        for name,p in models.items():
            foldrows.append({'target':target,'held_collection':held,'model':name,'n':len(test),'positives':int(yall[test].sum()),'bits':f'{bits(yall[test],p):.9f}','auc':f'{auc(yall[test],p):.9f}','average_precision':f'{ap(yall[test],p):.9f}','prevalence':f'{np.mean(yall[test]):.9f}'})
        for loc,i in enumerate(test):
            allpred[target][i]={k:float(v[loc]) for k,v in models.items()}
            predrows.append({'target':target,'held_collection':held,'collection_id':obs[i]['collection_id'],'recipe_id':obs[i]['recipe_id'],'element_ordinal':obs[i]['element_ordinal'],'oracle_label':int(yall[i]),**{f'p_{k.lower()}':f'{v[loc]:.9f}' for k,v in models.items()}})
    summary=[]
    observed={}
    for target in TARGETS:
        inds=sorted(allpred[target]);y=Y[target][inds];P={m:np.array([allpred[target][i][m] for i in inds]) for m in ['PREVALENCE','NUISANCE','OPAQUE_ID','STRUCTURE','STRUCTURE_PLUS_ID']};B={m:bits(y,p) for m,p in P.items()};gain_best=float(min(B['NUISANCE'],B['OPAQUE_ID'])-B['STRUCTURE_PLUS_ID']);observed[target]=gain_best
        folds=[r for r in foldrows if r['target']==target];by={(r['held_collection'],r['model']):float(r['bits']) for r in folds};posfold=sum(by[(c,'STRUCTURE_PLUS_ID')]<min(by[(c,'NUISANCE')],by[(c,'OPAQUE_ID')]) for c in collections);positive_cols=sum(any(r['target']==target and r['held_collection']==c and int(r['positives'])>0 for r in folds) for c in collections);prev=float(y.mean());a=auc(y,P['STRUCTURE_PLUS_ID']);a_p=ap(y,P['STRUCTURE_PLUS_ID'])
        summary.append({'target':target,'n':len(inds),'positives':int(y.sum()),'positive_collections':positive_cols,'structure_gain_vs_nuisance_bits':f'{B["NUISANCE"]-B["STRUCTURE"]:.9f}','combined_gain_vs_identity_bits':f'{B["OPAQUE_ID"]-B["STRUCTURE_PLUS_ID"]:.9f}','combined_gain_vs_best_aggregate_baseline_bits':f'{gain_best:.9f}','positive_gain_folds':posfold,'pooled_auc':f'{a:.9f}','pooled_average_precision':f'{a_p:.9f}','prevalence':f'{prev:.9f}','ap_over_prevalence':f'{a_p/max(prev,1e-12):.9f}'})
    # Fixed-prediction, nuisance-stratified held-label null; max across all endpoints.
    indices={t:sorted(allpred[t]) for t in TARGETS};strata=defaultdict(list)
    for i in indices[TARGETS[0]]:
        r=obs[i];strata[(r['collection_id'],bucket_len(int(r['record_element_count'])),str(min(9,int(float(r['relative_position'])*10))),bucket_tok(int(r['direct_token_count'])))].append(i)
    nullvals={t:[] for t in TARGETS};maxima=[]
    for world in range(1024):
        rng=random.Random(376000+world);permuted={}
        for t in TARGETS:
            yy=Y[t].copy()
            for ids in strata.values():
                vals=[int(yy[i]) for i in ids];rng.shuffle(vals)
                for i,v in zip(ids,vals):yy[i]=v
            ids=indices[t];y=yy[ids];p=allpred[t];bn=bits(y,[p[i]['NUISANCE'] for i in ids]);bi=bits(y,[p[i]['OPAQUE_ID'] for i in ids]);bc=bits(y,[p[i]['STRUCTURE_PLUS_ID'] for i in ids]);g=min(bn,bi)-bc;nullvals[t].append(g)
        maxima.append(max(nullvals[t][-1] for t in TARGETS))
    for row in summary:
        t=row['target'];obsval=observed[t];row['local_p']=f'{(1+sum(v>=obsval for v in nullvals[t]))/1025:.9f}';row['max_family_p']=f'{(1+sum(v>=obsval for v in maxima))/1025:.9f}'
        row['promoted']='YES' if int(row['positive_collections'])>=4 and int(row['positive_gain_folds'])>=4 and float(row['pooled_auc'])>=.65 and float(row['ap_over_prevalence'])>=1.5 and float(row['structure_gain_vs_nuisance_bits'])>0 and float(row['combined_gain_vs_identity_bits'])>0 and float(row['max_family_p'])<=.05 else 'NO'
    contracts=read_tsv(CONTRACT);promoted_targets={r['target'] for r in summary if r['promoted']=='YES'};transfer=[]
    for c in contracts:
        eps=[x.strip() for x in c['hidden_oracle_endpoints'].split(';')];matched=sorted(set(eps)&promoted_targets)
        transfer.append({'hypothesis_family':c['hypothesis_family'],'oracle_endpoints':c['hidden_oracle_endpoints'],'promoted_endpoints':';'.join(matched),'transfer_to_voynich':'YES' if matched else 'NO','frozen_signature':c['form_blind_signature'],'semantic_gloss':'UNASSIGNED'})
    write_tsv(ART/'gdt376_fold_scores.tsv',foldrows);write_tsv(ART/'gdt376_oracle_endpoint_summary.tsv',summary);write_tsv(ART/'gdt376_transfer_gate.tsv',transfer)
    nullrows=[{'target':t,'observed_gain_bits':f'{observed[t]:.9f}','local_p':next(r['local_p'] for r in summary if r['target']==t),'max_family_p':next(r['max_family_p'] for r in summary if r['target']==t),'null_worlds':1024} for t in TARGETS];write_tsv(ART/'gdt376_null.tsv',nullrows)
    promoted=[r['target'] for r in summary if r['promoted']=='YES'];families=[r['hypothesis_family'] for r in transfer if r['transfer_to_voynich']=='YES']
    promoted_predictions=[row for row in predrows if row['target'] in promoted]
    write_tsv(ART/'gdt376_promoted_endpoint_predictions.tsv',promoted_predictions)
    legacy_predictions=ART/'gdt376_held_predictions.tsv'
    if legacy_predictions.exists():legacy_predictions.unlink()
    outputs=[ART/x for x in ['gdt376_fold_scores.tsv','gdt376_promoted_endpoint_predictions.tsv','gdt376_oracle_endpoint_summary.tsv','gdt376_transfer_gate.tsv','gdt376_null.tsv']]
    result={'schema':'GDT376_RESULT_V1','status':'FORM_BLIND_FUNCTIONAL_SIGNATURES_CALIBRATED' if promoted else 'NO_FORM_BLIND_FUNCTIONAL_SIGNATURE_GENERALIZED','rows_scored':int(sum(valid)),'collections':collections,'targets':len(TARGETS),'promoted_endpoints':promoted,'transferable_families':families,'voynich_scored':False,'f84_accessed':False,'design_sha256':sha(DESIGN),'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [OBS,ORACLE,CONTRACT]},'outputs':{str(p.relative_to(ROOT)):sha(p) for p in outputs},'implementation':{str((BASE/'src/run.py').relative_to(ROOT)):sha(BASE/'src/run.py')},'claim_ceiling':'COMPARATOR_HELD_FUNCTIONAL_DETECTOR_CALIBRATION_ONLY'}
    result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ART/'gdt376_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'promoted':promoted,'families':families},sort_keys=True))
if __name__=='__main__':main()

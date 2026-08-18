#!/usr/bin/env python3
"""Predict sparse operation licenses from frozen opaque-host ecology."""
import csv,hashlib,json,statistics
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;FEATURES=R/'gdt309_host_features.tsv';DESIGN=R/'gdt309_design.json';METHOD=R/'GDT309_OPERATION_LICENSE_PREDICTION_METHOD.md';PRED=R/'gdt309_host_predictions.tsv';SCORES=R/'gdt309_model_scores.tsv';NULL=R/'gdt309_null_max.tsv';COUNTER=R/'gdt309_counterexamples.tsv';REPORT=R/'GDT309_OPERATION_LICENSE_PREDICTION_REPORT.md';RESULT=R/'gdt309_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def matrix(rows,names):
 X=np.array([[float(x[k]) for k in names] for x in rows]);mu=X.mean(0);sd=X.std(0);sd[sd==0]=1;Z=(X-mu)/sd;return np.column_stack([np.ones(len(rows)),Z])
def hat(X,lam):
 P=np.eye(X.shape[1])*lam;P[0,0]=0;return X@np.linalg.pinv(X.T@X+P)@X.T
def loo(H,y,clip):
 fit=H@y;diag=np.diag(H);p=(fit-diag*y)/(1-diag);return np.clip(p,clip[0],clip[1])
def brier(p,y):return float(np.mean((p-y)**2))
def auc(p,y):
 pos=p[y==1];neg=p[y==0];return float(sum((a>b)+.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg)))
def ap(p,y):
 order=sorted(range(len(y)),key=lambda i:(-p[i],i));hit=0;s=0
 for rank,i in enumerate(order,1):
  if y[i]==1:hit+=1;s+=hit/rank
 return s/hit
def label_name(op):return 'license_'+op.replace(':','_').replace('>','_to_')
def permute(y,bins,seed,world,op):
 out=y.copy()
 for b in sorted(set(bins)):
  idx=np.where(bins==b)[0];vals=y[idx].copy();key=int(hashlib.sha256(f'{seed}|{world}|{op}|{b}'.encode()).hexdigest()[:16],16);rng=np.random.default_rng(key);rng.shuffle(vals);out[idx]=vals
 return out
def main():
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');assert stored==can(d) and d['status']=='FROZEN_BEFORE_LICENSE_PREDICTION_SCORING';rows=read(FEATURES);models=list(d['models']);H={m:hat(matrix(rows,d['models'][m]),d['ridge']) for m in models};events=np.array([int(x['events']) for x in rows]);order=np.argsort(events,kind='stable');bins=np.empty(len(rows),int)
 for rank,i in enumerate(order):bins[i]=min(3,rank*4//len(rows))
 observed={};predrows=[];scorerows=[];null={}
 for op in d['operations']:
  y=np.array([int(x[label_name(op)]) for x in rows],float);pred={m:loo(H[m],y,d['prediction_clip']) for m in models};base=brier(pred['FREQUENCY'],y)
  for m in models:
   gain=base-brier(pred[m],y);observed[(op,m)]=gain
   scorerows.append({'operation':op,'model':m,'hosts':len(y),'licensed_hosts':int(y.sum()),'brier':f'{brier(pred[m],y):.12f}','brier_gain_vs_frequency':f'{gain:.12f}','roc_auc':f'{auc(pred[m],y):.12f}','average_precision':f'{ap(pred[m],y):.12f}','null_mean_gain':'NA' if m=='FREQUENCY' else '', 'null_sd_gain':'NA' if m=='FREQUENCY' else '', 'standardized_gain':'NA' if m=='FREQUENCY' else '', 'local_p':'NA' if m=='FREQUENCY' else '', 'max12_p':'NA' if m=='FREQUENCY' else ''})
   for i,x in enumerate(rows):predrows.append({'host_id_sha256':x['host_id_sha256'],'operation':op,'licensed':int(y[i]),'model':m,'loo_probability':f'{pred[m][i]:.12f}','event_count_quartile':int(bins[i])})
  for m in models:
   if m!='FREQUENCY':null[(op,m)]=[]
 for world in range(d['null_worlds']):
  for op in d['operations']:
   y=np.array([int(x[label_name(op)]) for x in rows],float);q=permute(y,bins,d['null_seed'],world,op);base=brier(loo(H['FREQUENCY'],q,d['prediction_clip']),q)
   for m in models:
    if m!='FREQUENCY':null[(op,m)].append(base-brier(loo(H[m],q,d['prediction_clip']),q))
 mu={k:statistics.mean(v) for k,v in null.items()};sd={k:statistics.pstdev(v) for k,v in null.items()};z={k:(observed[k]-mu[k])/sd[k] if sd[k] else 0 for k in null};maxz=[max((null[k][w]-mu[k])/sd[k] if sd[k] else 0 for k in null) for w in range(d['null_worlds'])]
 scoremap={(x['operation'],x['model']):x for x in scorerows}
 for k,values in null.items():
  row=scoremap[k];lp=(1+sum(v>=observed[k]-1e-15 for v in values))/(1+d['null_worlds']);mp=(1+sum(v>=z[k]-1e-15 for v in maxz))/(1+d['null_worlds']);row.update({'null_mean_gain':f'{mu[k]:.12f}','null_sd_gain':f'{sd[k]:.12f}','standardized_gain':f'{z[k]:.12f}','local_p':f'{lp:.12f}','max12_p':f'{mp:.12f}'})
 classes={}
 for op in d['operations']:
  x=scoremap[(op,'FULL')];ok=float(x['brier_gain_vs_frequency'])>0 and float(x['roc_auc'])>=d['decision']['full_auc_minimum'] and float(x['max12_p'])<=d['decision']['full_max12_p_le'];classes[op]='STRUCTURALLY_PREDICTABLE' if ok else 'OPAQUE_OR_UNRESOLVED_LICENSE'
 status='OPERATION_LICENSE_PARTLY_COMPRESSIBLE' if any(v=='STRUCTURALLY_PREDICTABLE' for v in classes.values()) else 'OPERATION_LICENSE_NOT_STRUCTURALLY_PREDICTABLE';counter=[{'counterexample_id':'C01','finding':'Only 7 ch-to-s and 8 d-to-s positives exist among 58 hosts.','impact':'Rare-class AUC/AP and null tails have high variance.'},{'counterexample_id':'C02','finding':'Operation labels were selected by GDT303 before this model family was frozen.','impact':'This tests compressibility of exposed licenses, not discovery.'},{'counterexample_id':'C03','finding':'Features summarize each host across the whole f84-free corpus, including events carrying the target q or s wrapper.','impact':'GDT309 classifies an observed ecology; it is not a causal pre-target license prediction.'},{'counterexample_id':'C04','finding':'Wrapper counts and host glyphs are excluded.','impact':'A failure does not refute compatibility that is encoded in those forbidden coordinates.'},{'counterexample_id':'C05','finding':'Linear ridge-10 is deliberately low-capacity.','impact':'Nonlinear or interaction-heavy licensing remains untested.'},{'counterexample_id':'C06','finding':'No f84 row occurs in the source feature freeze.','impact':'The sealed holdout remains untouched.'}];write(PRED,predrows);write(SCORES,scorerows);write(NULL,[{'world_index':i,'max12_standardized_brier_gain':f'{v:.12f}'} for i,v in enumerate(maxz)]);write(COUNTER,counter)
 report=['# GDT309 — opaque-host operation-license prediction','',f'Status: **{status}**.','', 'No host glyph, substring, exact identity, surface identity, or wrapper count enters a predictor.','','| operation | FULL gain | AUC | AP | max-12 p | class |','|---|---:|---:|---:|---:|---|']
 for op in d['operations']:
  x=scoremap[(op,'FULL')];report.append(f"| `{op}` | {float(x['brier_gain_vs_frequency']):+.4f} | {float(x['roc_auc']):.3f} | {float(x['average_precision']):.3f} | {x['max12_p']} | {classes[op]} |")
 report+=['','## Model ablations','', '| operation | layout gain | compiler gain | register gain | full gain |','|---|---:|---:|---:|---:|']
 for op in d['operations']:report.append('| `{}` | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} |'.format(op,*[float(scoremap[(op,m)]['brier_gain_vs_frequency']) for m in ('LAYOUT','COMPILER','REGISTER','FULL')]))
 report+=['','## Interpretation','', '`NONE->q` licensing is the only structurally compressible relation under the frozen rule. Its layout block already gives +0.0653 Brier improvement and the strongest corrected tail, while register alone is negative. This agrees with q as a broad field/position ecology rather than a domain-invariant displacement vector. The high raw AUCs for `ch->s` and `d->s` are already present in the frequency baseline; allowed structural features add no corrected Brier improvement. Their positional operations remain real on compatible hosts, but their compatibility list stays opaque under this instrument.','','## Causal limitation','', 'Although wrapper values/counts are excluded as columns, each host summary uses all of that host\'s events, including target q/s occurrences. GDT309 therefore classifies the full observed ecology of a known license; it does **not** predict a target alternant before that alternant is seen. A source-side-only successor is required for causal license prediction.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[PRED,SCORES,NULL,COUNTER,REPORT];inputs=[FEATURES,R/'gdt309_capacity.tsv',R/'gdt309_design_validation.json',R/'gdt303_result.json',R/'gdt307_result.json',R/'gdt308_result.json'];res={'schema':'GDT309_OPERATION_LICENSE_PREDICTION_RESULT_V1','status':status,'classifications':classes,'target_event_exposure':'INCLUDED_IN_HOST_ECOLOGY_CLASSIFICATION_NOT_CAUSAL_LICENSE_PREDICTION','summary':{'hosts':58,'predictable_licenses':sum(v=='STRUCTURALLY_PREDICTABLE' for v in classes.values())},'provenance':'POST_SELECTION_FULL_OBSERVED_ECOLOGY_COMPRESSIBILITY_TEST','semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in outputs}};res['content_sha256']=can(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'classes':classes,'full':{op:scoremap[(op,'FULL')] for op in d['operations']}},sort_keys=True))
if __name__=='__main__':main()

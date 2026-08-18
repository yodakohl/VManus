#!/usr/bin/env python3
"""Validate GDT309 scores, null, decision and artifact bindings."""
import csv,hashlib,json,statistics
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;FEATURES=R/'gdt309_host_features.tsv';DESIGN=R/'gdt309_design.json';SCORES=R/'gdt309_model_scores.tsv';RESULT=R/'gdt309_result.json';OUT=R/'gdt309_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def matrix(rows,names):
 X=np.array([[float(x[k]) for k in names] for x in rows]);sd=X.std(0);sd[sd==0]=1;return np.column_stack([np.ones(len(rows)),(X-X.mean(0))/sd])
def hat(X,lam):
 P=np.eye(X.shape[1])*lam;P[0,0]=0;return X@np.linalg.pinv(X.T@X+P)@X.T
def loo(H,y,c):
 f=H@y;h=np.diag(H);return np.clip((f-h*y)/(1-h),c[0],c[1])
def brier(p,y):return float(np.mean((p-y)**2))
def auc(p,y):
 a=p[y==1];b=p[y==0];return float(sum((x>z)+.5*(x==z) for x in a for z in b)/(len(a)*len(b)))
def label(op):return 'license_'+op.replace(':','_').replace('>','_to_')
def permute(y,bins,seed,world,op):
 out=y.copy()
 for b in sorted(set(bins)):
  idx=np.where(bins==b)[0];vals=y[idx].copy();key=int(hashlib.sha256(f'{seed}|{world}|{op}|{b}'.encode()).hexdigest()[:16],16);rng=np.random.default_rng(key);rng.shuffle(vals);out[idx]=vals
 return out
checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def close(a,b):return abs(float(a)-float(b))<5e-12
def main():
 d=json.loads(DESIGN.read_text());rows=read(FEATURES);scores={(x['operation'],x['model']):x for x in read(SCORES)};H={m:hat(matrix(rows,n),d['ridge']) for m,n in d['models'].items()}
 observed={};events=np.array([int(x['events']) for x in rows]);order=np.argsort(events,kind='stable');bins=np.empty(len(rows),int)
 for rank,i in enumerate(order):bins[i]=min(3,rank*4//len(rows))
 for op in d['operations']:
  y=np.array([int(x[label(op)]) for x in rows],float);pred={m:loo(H[m],y,d['prediction_clip']) for m in H};base=brier(pred['FREQUENCY'],y)
  for m,p in pred.items():observed[(op,m)]=base-brier(p,y);ck('observed_scores',close(scores[(op,m)]['brier'],brier(p,y)) and close(scores[(op,m)]['brier_gain_vs_frequency'],observed[(op,m)]) and close(scores[(op,m)]['roc_auc'],auc(p,y)))
 tests=[(op,m) for op in d['operations'] for m in d['models'] if m!='FREQUENCY'];null={key:[] for key in tests}
 for world in range(d['null_worlds']):
  for op in d['operations']:
   y=np.array([int(x[label(op)]) for x in rows],float);q=permute(y,bins,d['null_seed'],world,op);base=brier(loo(H['FREQUENCY'],q,d['prediction_clip']),q)
   for m in d['models']:
    if m!='FREQUENCY':null[(op,m)].append(base-brier(loo(H[m],q,d['prediction_clip']),q))
 mu={key:statistics.mean(values) for key,values in null.items()};sd={key:statistics.pstdev(values) for key,values in null.items()};z={key:(observed[key]-mu[key])/sd[key] if sd[key] else 0 for key in tests};maxz=[max((null[key][world]-mu[key])/sd[key] if sd[key] else 0 for key in tests) for world in range(d['null_worlds'])]
 for key in tests:
  local=(1+sum(value>=observed[key]-1e-15 for value in null[key]))/(1+d['null_worlds']);maximum=(1+sum(value>=z[key]-1e-15 for value in maxz))/(1+d['null_worlds']);row=scores[key];ck('null_scores',close(row['null_mean_gain'],mu[key]) and close(row['null_sd_gain'],sd[key]) and close(row['local_p'],local) and close(row['max12_p'],maximum))
 classes={}
 for op in d['operations']:
  x=scores[(op,'FULL')];ok=float(x['brier_gain_vs_frequency'])>0 and float(x['roc_auc'])>=d['decision']['full_auc_minimum'] and float(x['max12_p'])<=d['decision']['full_max12_p_le'];classes[op]='STRUCTURALLY_PREDICTABLE' if ok else 'OPAQUE_OR_UNRESOLVED_LICENSE'
 status='OPERATION_LICENSE_PARTLY_COMPRESSIBLE' if any(v=='STRUCTURALLY_PREDICTABLE' for v in classes.values()) else 'OPERATION_LICENSE_NOT_STRUCTURALLY_PREDICTABLE';res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('content_hash',stored==can(res));ck('status_classes',res['status']==status and res['classifications']==classes);ck('input_hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));ck('output_hashes',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));ck('document_hashes',all(res['documents'][n]==sha(R/n) for n in res['documents']));ck('implementation_hash',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84_flags',not any(res['f84'].values()));v={'schema':'GDT309_OPERATION_LICENSE_PREDICTION_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'reconstructed_status':status,'f84_rows':0,'scope':'INDEPENDENT_OBSERVED_SCORE_EXACT_NULL_DECISION_AND_BINDING_RECONSTRUCTION'};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'reconstructed_status':status},sort_keys=True))
if __name__=='__main__':main()

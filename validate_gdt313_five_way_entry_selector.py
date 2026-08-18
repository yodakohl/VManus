#!/usr/bin/env python3
"""Independently rebuild GDT313 five-way fit, null, and decision."""
import csv,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIRS=R/'gdt303_pair_deltas.tsv';PANEL=R/'gdt313_frozen_panel.tsv';DESIGN=R/'gdt313_design.json';SCORES=R/'gdt313_model_scores.tsv';ATLAS=R/'gdt313_context_atlas.tsv';RESULT=R/'gdt313_result.json';OUT=R/'gdt313_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b):return abs(float(a)-float(b))<5e-12
def truth():
 ev=[x for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'];rep={}
 for x in ev:rep.setdefault(x['source_surface_sha256'],x)
 ops={}
 for name in ('wrapper:ch>s','wrapper:d>s','wrapper:NONE>q'):
  z={}
  for p in read(PAIRS):
   if p['operation']==name:
    e=rep[p['source_surface_sha256']];z[(p['page_host'],e['local_frame'],e['inner_d'],e['right_family'],e['dy_closure'],e['b3'])]=p
  ops[name]=z
 sur={}
 for key in set(ops['wrapper:ch>s'])&set(ops['wrapper:d>s'])&set(ops['wrapper:NONE>q']):
  a,d,q=ops['wrapper:ch>s'][key],ops['wrapper:d>s'][key],ops['wrapper:NONE>q'][key];cid=hashlib.sha256(('CELL|'+'|'.join(key)).encode()).hexdigest()[:20]
  for choice,s in [('NONE',q['source_surface_sha256']),('q',q['target_surface_sha256']),('ch',a['source_surface_sha256']),('d',d['source_surface_sha256']),('s',a['target_surface_sha256'])]:sur[s]=(cid,choice)
 return {hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:sur[x['source_surface_sha256']] for x in ev if x['source_surface_sha256'] in sur}
def matrix(tr,te,names):
 ids=sorted({x['cell_id'] for x in tr})
 def enc(rr):return np.array([[1.]+[float(x['cell_id']==v) for v in ids]+[float(x[n]) for n in names] for x in rr])
 return enc(tr),enc(te),['INTERCEPT']+['CELL:'+x for x in ids]+names
def fit(x,y,z,classes,ridge):
 k=len(classes)-1;p=x.shape[1];B=np.zeros((p,k));PEN=np.eye(p)*ridge;PEN[0,0]=0;Y=np.column_stack([y==i for i in range(1,len(classes))]).astype(float)
 for _ in range(100):
  ex=np.exp(np.clip(x@B,-30,30));pr=ex/(1+ex.sum(1,keepdims=True));g=x.T@(Y-pr)-PEN@B;H=np.zeros((p*k,p*k))
  for a in range(k):
   for b in range(k):
    w=pr[:,a]*((1. if a==b else 0.)-pr[:,b]);H[a*p:(a+1)*p,b*p:(b+1)*p]=x.T@(x*w[:,None])+(PEN if a==b else 0)
  step=np.linalg.pinv(H)@g.T.reshape(-1);B+=step.reshape(k,p).T
  if abs(step).max()<1e-10:break
 ex=np.exp(np.clip(z@B,-30,30));den=1+ex.sum(1,keepdims=True);return np.column_stack([1/den[:,0],ex/den]),B
def bits(p,y):return float(-np.mean(np.log2(np.maximum(p[np.arange(len(y)),y],1e-15))))
def perm(y,rows,seed,w):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{seed}|{w}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def matched(rows,y,feature,target):
 g=defaultdict(lambda:[[],[]])
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])][int(x[feature])].append(int(y[i]==target))
 num=den=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());rows=read(PANEL);t=truth();classes=d['choices'];idx={v:i for i,v in enumerate(classes)};tr=[x for x in rows if x['split']=='TRAIN'];te=[x for x in rows if x['split']=='TEST'];yt=np.array([idx[t[x['event_id_sha256']][1]] for x in tr]);ye=np.array([idx[t[x['event_id_sha256']][1]] for x in te]);pred={};coef={};cols={}
 for m,n in d['models'].items():x,z,cols[m]=matrix(tr,te,n);pred[m],coef[m]=fit(x,yt,z,classes,d['ridge'])
 base=bits(pred['CELL'],ye);obs={m:base-bits(v,ye) for m,v in pred.items()};scores={x['model']:x for x in read(SCORES)}
 for m,v in pred.items():ck('score',close(scores[m]['held_bits_per_event'],bits(v,ye)) and close(scores[m]['gain_vs_cell_bits_per_event'],obs[m]) and close(scores[m]['top1_accuracy'],np.mean(np.argmax(v,1)==ye)))
 null={m:[] for m in d['models'] if m!='CELL'}
 for w in range(d['null']['worlds']):
  y=perm(ye,te,d['null']['seed'],w);bb=bits(pred['CELL'],y)
  for m in null:null[m].append(bb-bits(pred[m],y))
 mu={m:statistics.mean(v) for m,v in null.items()};sd={m:statistics.pstdev(v) for m,v in null.items()};z={m:(obs[m]-mu[m])/sd[m] if sd[m] else 0 for m in null};mx=[max((null[m][w]-mu[m])/sd[m] if sd[m] else 0 for m in null) for w in range(d['null']['worlds'])]
 for m,v in null.items():local=(1+sum(x>=obs[m]-1e-15 for x in v))/(1+d['null']['worlds']);maximum=(1+sum(x>=z[m]-1e-15 for x in mx))/(1+d['null']['worlds']);ck('null',close(scores[m]['null_mean_gain'],mu[m]) and close(scores[m]['null_centered_gain'],obs[m]-mu[m]) and close(scores[m]['local_p'],local) and close(scores[m]['max3_p'],maximum))
 entry=scores['ENTRY_STATE'];scoef=coef['ENTRY_STATE'][cols['ENTRY_STATE'].index('line_first'),classes[1:].index('s')];qcoef=coef['ENTRY_STATE'][cols['ENTRY_STATE'].index('prev_dy'),classes[1:].index('q')];sdelta=matched(te,ye,'line_first',idx['s']);qdelta=matched(te,ye,'prev_dy',idx['q']);ck('directions',close(entry['s_line_start_coefficient'],scoef) and close(entry['q_prev_dy_coefficient'],qcoef) and scoef>0 and qcoef>0 and sdelta>0 and qdelta>0);atlas={(x['split'],x['target_choice']):x for x in read(ATLAS)};ck('atlas',close(atlas[('TEST','s')]['cell_register_matched_delta'],sdelta) and close(atlas[('TEST','q')]['cell_register_matched_delta'],qdelta));res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('content',stored==can(res));ck('status',res['status']=='FIVE_WAY_ENTRY_STATE_SELECTOR_TRANSFERS');ck('hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']) and all(res['outputs'][n]==sha(R/n) for n in res['outputs']) and all(res['documents'][n]==sha(R/n) for n in res['documents']) and all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84',not any(res['f84'].values()));v={'schema':'GDT313_FIVE_WAY_ENTRY_SELECTOR_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'f84_rows':0,'scope':'INDEPENDENT_TRUTH_MULTINOMIAL_SCORE_NULL_DIRECTION_AND_BINDING_RECONSTRUCTION'};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

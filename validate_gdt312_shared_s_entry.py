#!/usr/bin/env python3
"""Independently reconstruct GDT312 triads, held scores, and null."""
import csv,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIRS=R/'gdt303_pair_deltas.tsv';SCORES=R/'gdt312_model_scores.tsv';RESULT=R/'gdt312_result.json';OUT=R/'gdt312_validation.json';MODELS={'TRIAD':[],'LINE_START':['line_first'],'PREV_DY':['prev_dy'],'SHARED_ENTRY':['line_first','prev_dy']};RIDGE=10.;WORLDS=8192;SEED=31220260818
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b):return abs(float(a)-float(b))<5e-12
def split(f):return int(hashlib.sha256(f'GDT311_SPLIT_V1|{f}'.encode()).hexdigest()[:8],16)%3==0
def build():
 p=read(PAIRS);a={x['target_surface_sha256']:x for x in p if x['operation']=='wrapper:ch>s'};b={x['target_surface_sha256']:x for x in p if x['operation']=='wrapper:d>s'};sur={}
 for target in a.keys()&b.keys():
  t=hashlib.sha256(f'TRIAD|{target}'.encode()).hexdigest()[:20];sur[a[target]['source_surface_sha256']]=(t,0);sur[b[target]['source_surface_sha256']]=(t,0);sur[target]=(t,1)
 ev=[x for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'];assert not any(x['page'].startswith('f84') for x in ev);pos={(x['locus'],int(x['group_index'])):x for x in ev};rows=[]
 for x in ev:
  if x['source_surface_sha256'] in sur:
   t,y=sur[x['source_surface_sha256']];pr=pos.get((x['locus'],int(x['group_index'])-1));rows.append({'triad_id':t,'y':y,'test':split(x['physical_folio']),'register':x['register'],'line_first':int(x['group_index']=='1'),'prev_dy':int(pr is not None and pr['dy_closure']=='1'),'physical_folio':x['physical_folio'],'locus':x['locus'],'event_id':hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]})
 return sorted(rows,key=lambda x:(x['triad_id'],x['physical_folio'],x['locus'],x['event_id']))
def matrix(tr,te,names):
 ids=sorted({x['triad_id'] for x in tr})
 def enc(rr):return np.array([[1.]+[float(x['triad_id']==v) for v in ids]+[float(x[n]) for n in names] for x in rr])
 return enc(tr),enc(te)
def fit(x,y,z):
 b=np.zeros(x.shape[1]);P=np.eye(len(b))*RIDGE;P[0,0]=0
 for _ in range(100):
  p=1/(1+np.exp(-np.clip(x@b,-30,30)));w=np.maximum(p*(1-p),1e-8);step=np.linalg.pinv(x.T@(x*w[:,None])+P)@(x.T@(y-p)-P@b);b+=step
  if abs(step).max()<1e-10:break
 return np.clip(1/(1+np.exp(-np.clip(z@b,-30,30))),.01,.99)
def bits(p,y):return float(-np.mean(y*np.log2(p)+(1-y)*np.log2(1-p)))
def perm(y,rows,world):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['triad_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{SEED}|{world}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 rows=build();tr=[x for x in rows if not x['test']];te=[x for x in rows if x['test']];yt=np.array([x['y'] for x in tr],float);ye=np.array([x['y'] for x in te],float);pred={}
 for m,n in MODELS.items():x,z=matrix(tr,te,n);pred[m]=fit(x,yt,z)
 base=bits(pred['TRIAD'],ye);obs={m:base-bits(p,ye) for m,p in pred.items()};scores={x['model']:x for x in read(SCORES)}
 for m,p in pred.items():ck('score',close(scores[m]['held_bits_per_event'],bits(p,ye)) and close(scores[m]['gain_vs_triad_bits_per_event'],obs[m]))
 null={m:[] for m in MODELS if m!='TRIAD'}
 for w in range(WORLDS):
  y=perm(ye,te,w);bb=bits(pred['TRIAD'],y)
  for m in null:null[m].append(bb-bits(pred[m],y))
 mu={m:statistics.mean(v) for m,v in null.items()};sd={m:statistics.pstdev(v) for m,v in null.items()};z={m:(obs[m]-mu[m])/sd[m] if sd[m] else 0 for m in null};mx=[max((null[m][w]-mu[m])/sd[m] if sd[m] else 0 for m in null) for w in range(WORLDS)]
 for m,v in null.items():local=(1+sum(x>=obs[m]-1e-15 for x in v))/(1+WORLDS);maximum=(1+sum(x>=z[m]-1e-15 for x in mx))/(1+WORLDS);ck('null',close(scores[m]['null_mean_gain'],mu[m]) and close(scores[m]['null_centered_gain'],obs[m]-mu[m]) and close(scores[m]['local_p'],local) and close(scores[m]['max3_p'],maximum))
 ck('capacity',len(rows)==879 and len(tr)==529 and len(te)==350 and int(ye.sum())==48 and len({x['triad_id'] for x in rows})==7);res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('content_hash',stored==can(res));ck('status',res['status']=='SHARED_S_LINE_ENTRY_RULE_POSTHOC');ck('input_hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));ck('output_hashes',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));ck('documents',all(res['documents'][n]==sha(R/n) for n in res['documents']));ck('implementation',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84',not any(res['f84'].values()));v={'schema':'GDT312_SHARED_S_ENTRY_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'f84_rows':0,'scope':'INDEPENDENT_TRIAD_FIT_SCORE_NULL_AND_BINDING_RECONSTRUCTION'};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

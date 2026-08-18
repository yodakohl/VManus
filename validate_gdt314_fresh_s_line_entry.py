#!/usr/bin/env python3
"""Independently rebuild GDT314 crossfit result and alignment diagnostic."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt314_frozen_panel.tsv';DESIGN=R/'gdt314_design.json';FOLDS=R/'gdt314_folio_scores.tsv';SECTIONS=R/'gdt314_section_scores.tsv';RESULT=R/'gdt314_result.json';OUT=R/'gdt314_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b):return abs(float(a)-float(b))<5e-12
def matrix(tr,te,full):
 cells=sorted({x['cell_id'] for x in tr})
 def enc(rr):return np.array([[1.]+[float(x['cell_id']==v) for v in cells]+([float(x['line_first'])] if full else []) for x in rr])
 return enc(tr),enc(te)
def fit(x,y,z,ridge):
 b=np.zeros(x.shape[1]);P=np.eye(len(b))*ridge;P[0,0]=0
 for _ in range(100):
  p=1/(1+np.exp(-np.clip(x@b,-30,30)));w=np.maximum(p*(1-p),1e-8);step=np.linalg.pinv(x.T@(x*w[:,None])+P)@(x.T@(y-p)-P@b);b+=step
  if abs(step).max()<1e-10:break
 return np.clip(1/(1+np.exp(-np.clip(z@b,-30,30))),.01,.99),b
def eb(p,y):return -(y*np.log2(p)+(1-y)*np.log2(1-p))
def perm(y,rows,seed,w):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{seed}|{w}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def matched(rows,y):
 g=defaultdict(lambda:[[],[]])
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])][int(x['line_first'])].append(int(y[i]))
 num=den=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());rows=read(PANEL);truth={hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:int(x['wrapper']=='s') for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'};y=np.array([truth[x['event_id_sha256']] for x in rows],float);base=np.zeros(len(rows));cand=np.zeros(len(rows));coefs={};fg={x['physical_folio']:x for x in read(FOLDS)}
 for f in sorted({x['physical_folio'] for x in rows}):
  tr=[x for x in rows if x['physical_folio']!=f];te=[x for x in rows if x['physical_folio']==f];yt=np.array([truth[x['event_id_sha256']] for x in tr],float);idx=[i for i,x in enumerate(rows) if x['physical_folio']==f];x,z=matrix(tr,te,False);base[idx],_=fit(x,yt,z,d['ridge']);x,z=matrix(tr,te,True);cand[idx],b=fit(x,yt,z,d['ridge']);coefs[f]=b[-1];gain=float(np.sum(eb(base[idx],y[idx])-eb(cand[idx],y[idx])));ck('fold',close(fg[f]['line_start_coefficient'],b[-1]) and close(fg[f]['gain_bits'],gain))
 ge=eb(base,y)-eb(cand,y);gain=float(ge.mean());delta=matched(rows,y);null=[]
 for w in range(d['null']['worlds']):
  q=perm(y,rows,d['null']['seed'],w);null.append(float(np.mean(eb(base,q)-eb(cand,q))))
 p=(1+sum(v>=gain-1e-15 for v in null))/(1+d['null']['worlds']);sections={x['section']:x for x in read(SECTIONS)}
 for s in sections:
  idx=[i for i,x in enumerate(rows) if x['section']==s];ck('section',close(sections[s]['gain_bits'],ge[idx].sum()))
 summary={'cells':15,'events':344,'s_events':35,'folios':78,'gain_bits_per_event':gain,'matched_line_start_delta':delta,'positive_coefficients':int(sum(v>0 for v in coefs.values())),'positive_folios':int(sum(float(x['gain_bits'])>0 for x in fg.values())),'positive_powered_sections':int(sum(float(sections[s]['gain_bits'])>0 for s in ('B','H','S'))),'alignment_diagnostic_p':p};res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('summary',all(close(res['summary'][k],v) if isinstance(v,float) else res['summary'][k]==v for k,v in summary.items()));ck('content',stored==can(res));ck('status',res['status']=='S_LINE_ENTRY_EXTENDS_TO_FRESH_SURFACES');ck('hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']) and all(res['outputs'][n]==sha(R/n) for n in res['outputs']) and all(res['documents'][n]==sha(R/n) for n in res['documents']) and all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84',not any(res['f84'].values()) and not any(x['page'].startswith('f84') for x in rows));v={'schema':'GDT314_FRESH_S_LINE_ENTRY_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'f84_rows':0,'scope':'INDEPENDENT_LABEL_CROSSFIT_SCORE_ALIGNMENT_AND_BINDING_RECONSTRUCTION'};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

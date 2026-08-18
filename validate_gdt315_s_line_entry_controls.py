#!/usr/bin/env python3
"""Independently reconstruct GDT315 panel scores, ranks, and bindings."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt315_frozen_panel.tsv';DESIGN=R/'gdt315_design.json';SCORES=R/'gdt315_panel_scores.tsv';RESULT=R/'gdt315_result.json';OUT=R/'gdt315_validation.json'
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
  p=1/(1+np.exp(-np.clip(x@b,-30,30)));w=np.maximum(p*(1-p),1e-8);st=np.linalg.pinv(x.T@(x*w[:,None])+P)@(x.T@(y-p)-P@b);b+=st
  if abs(st).max()<1e-10:break
 return np.clip(1/(1+np.exp(-np.clip(z@b,-30,30))),.01,.99),b
def eb(p,y):return -(y*np.log2(p)+(1-y)*np.log2(1-p))
def perm(y,rows,seed,w,panel):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{seed}|{w}|{panel}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def matched(rows,y):
 g=defaultdict(lambda:[[],[]])
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])][int(x['line_first'])].append(int(y[i]))
 num=den=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den if den else 0
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());allrows=read(PANEL);truth={hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:int(x['wrapper']=='s') for x in read(SOURCE)};stored={x['panel']:x for x in read(SCORES)};calc=[]
 for panel in d['powered_panels']:
  rows=[x for x in allrows if x['panel']==panel];y=np.array([truth[x['event_id_sha256']] for x in rows],float);base=np.zeros(len(rows));cand=np.zeros(len(rows));co=[]
  for f in sorted({x['physical_folio'] for x in rows}):
   tr=[x for x in rows if x['physical_folio']!=f];te=[x for x in rows if x['physical_folio']==f];yt=np.array([truth[x['event_id_sha256']] for x in tr],float);idx=[i for i,x in enumerate(rows) if x['physical_folio']==f];x,z=matrix(tr,te,False);base[idx],_=fit(x,yt,z,d['instrument']['ridge']);x,z=matrix(tr,te,True);cand[idx],b=fit(x,yt,z,d['instrument']['ridge']);co.append(b[-1])
  gain=float(np.mean(eb(base,y)-eb(cand,y)));delta=matched(rows,y);null=[]
  for w in range(d['instrument']['null_worlds']):
   q=perm(y,rows,d['instrument']['null_seed'],w,panel);null.append(float(np.mean(eb(base,q)-eb(cand,q))))
  p=(1+sum(v>=gain-1e-15 for v in null))/(1+d['instrument']['null_worlds']);row=stored[panel];ck('panel_score',close(row['gain_bits_per_event'],gain) and close(row['matched_line_start_delta'],delta) and int(row['positive_coefficients'])==sum(v>0 for v in co) and close(row['alignment_diagnostic_p'],p));calc.append((panel,gain,delta))
 go=sorted(calc,key=lambda x:(-x[1],x[0]));do=sorted(calc,key=lambda x:(-x[2],x[0]));ck('ranks',all(int(stored[x[0]]['gain_rank'])==i for i,x in enumerate(go,1)) and all(int(stored[x[0]]['delta_rank'])==i for i,x in enumerate(do,1)));v=stored['VOYNICH_REFERENCE'];controls=sum(float(x['gain_bits_per_event'])>=float(v['gain_bits_per_event'])-1e-15 for k,x in stored.items() if k!='VOYNICH_REFERENCE');status='S_LINE_ENTRY_VOYNICH_ENRICHED' if int(v['gain_rank'])==1 and int(v['delta_rank'])==1 else 'S_LINE_ENTRY_NOT_VOYNICH_SPECIFIC' if controls>=2 else 'S_LINE_ENTRY_CONTROL_MIXED';res=json.loads(RESULT.read_text());content=res.pop('content_sha256');ck('content',content==can(res));ck('status',res['status']==status and res['summary']['controls_gain_ge_voynich']==controls);ck('hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']) and all(res['outputs'][n]==sha(R/n) for n in res['outputs']) and all(res['documents'][n]==sha(R/n) for n in res['documents']) and all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84',not any(res['f84'].values()) and not any(x['page'].startswith('f84') for x in allrows));out={'schema':'GDT315_S_LINE_ENTRY_CONTROL_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'f84_rows':0,'scope':'INDEPENDENT_PANEL_CROSSFIT_NULL_RANK_DECISION_AND_BINDING_RECONSTRUCTION'};out['content_sha256']=can(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'reconstructed_status':status},sort_keys=True))
if __name__=='__main__':main()

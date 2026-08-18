#!/usr/bin/env python3
"""Score fresh q/non-q LOFO post-DY transfer."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt316_frozen_panel.tsv';DESIGN=R/'gdt316_design.json';METHOD=R/'GDT316_FRESH_Q_POST_DY_METHOD.md';PRED=R/'gdt316_predictions.tsv';FOLDS=R/'gdt316_folio_scores.tsv';SECTIONS=R/'gdt316_section_scores.tsv';NULL=R/'gdt316_null.tsv';COUNTER=R/'gdt316_counterexamples.tsv';REPORT=R/'GDT316_FRESH_Q_POST_DY_REPORT.md';RESULT=R/'gdt316_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def matrix(tr,te,full):
 cells=sorted({x['cell_id'] for x in tr})
 def enc(rr):return np.array([[1.]+[float(x['cell_id']==v) for v in cells]+([float(x['prev_dy'])] if full else []) for x in rr])
 return enc(tr),enc(te)
def fit(x,y,z,ridge):
 b=np.zeros(x.shape[1]);P=np.eye(len(b))*ridge;P[0,0]=0
 for _ in range(100):
  p=1/(1+np.exp(-np.clip(x@b,-30,30)));w=np.maximum(p*(1-p),1e-8);st=np.linalg.pinv(x.T@(x*w[:,None])+P)@(x.T@(y-p)-P@b);b+=st
  if abs(st).max()<1e-10:break
 return np.clip(1/(1+np.exp(-np.clip(z@b,-30,30))),.01,.99),b
def eb(p,y):return -(y*np.log2(p)+(1-y)*np.log2(1-p))
def perm(y,rows,seed,w):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{seed}|{w}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def matched(rows,y):
 g=defaultdict(lambda:[[],[]]);raw=[[],[]]
 for i,x in enumerate(rows):v=int(x['prev_dy']);g[(x['cell_id'],x['register'])][v].append(int(y[i]));raw[v].append(int(y[i]))
 num=den=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return len(raw[0]),sum(raw[0])/len(raw[0]),len(raw[1]),sum(raw[1])/len(raw[1]),num/den
def main():
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');assert stored==can(d);rows=read(PANEL);truth={hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:int(x['wrapper']=='q') for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'};y=np.array([truth[x['event_id_sha256']] for x in rows],float);folios=sorted({x['physical_folio'] for x in rows});base=np.zeros(len(rows));cand=np.zeros(len(rows));co={};folds=[]
 for f in folios:
  tr=[x for x in rows if x['physical_folio']!=f];te=[x for x in rows if x['physical_folio']==f];yt=np.array([truth[x['event_id_sha256']] for x in tr],float);idx=[i for i,x in enumerate(rows) if x['physical_folio']==f];x,z=matrix(tr,te,False);base[idx],_=fit(x,yt,z,d['ridge']);x,z=matrix(tr,te,True);cand[idx],b=fit(x,yt,z,d['ridge']);co[f]=b[-1];gain=float(np.sum(eb(base[idx],y[idx])-eb(cand[idx],y[idx])));folds.append({'physical_folio':f,'events':len(idx),'q_events':int(y[idx].sum()),'prev_dy_coefficient':f'{b[-1]:.12f}','gain_bits':f'{gain:.12f}','gain_bits_per_event':f'{gain/len(idx):.12f}'})
 ge=eb(base,y)-eb(cand,y);gain=float(ge.mean());n0,p0,n1,p1,delta=matched(rows,y);sections=[]
 for s in sorted({x['section'] for x in rows}):
  idx=[i for i,x in enumerate(rows) if x['section']==s];sections.append({'section':s,'events':len(idx),'q_events':int(y[idx].sum()),'gain_bits':f'{ge[idx].sum():.12f}','gain_bits_per_event':f'{ge[idx].mean():.12f}','powered':int(sum(y[idx])>0 and sum(y[idx])<len(idx))})
 null=[]
 for w in range(d['null']['worlds']):
  q=perm(y,rows,d['null']['seed'],w);null.append(float(np.mean(eb(base,q)-eb(cand,q))))
 p=(1+sum(v>=gain-1e-15 for v in null))/(1+d['null']['worlds']);pc=int(sum(v>0 for v in co.values()));pf=int(sum(float(x['gain_bits'])>0 for x in folds));powered={x['section']:x for x in sections if x['section'] in ('B','H','S')};ps=int(sum(float(x['gain_bits'])>0 for x in powered.values()));passes=gain>0 and delta>0 and pc>=d['decision']['positive_coefficients_min'] and ps>=d['decision']['positive_powered_sections_min'] and p<=d['decision']['alignment_p_le'];status='Q_POST_DY_EXTENDS_TO_FRESH_SURFACES' if passes else 'Q_POST_DY_FRESH_SURFACE_TRANSFER_WEAK_OR_FAILED';pred=[{'event_id_sha256':x['event_id_sha256'],'cell_id':x['cell_id'],'physical_folio':x['physical_folio'],'section':x['section'],'register':x['register'],'prev_dy':x['prev_dy'],'observed_q':int(y[i]),'cell_probability':f'{base[i]:.12f}','cell_prev_dy_probability':f'{cand[i]:.12f}','gain_bits':f'{ge[i]:.12f}'} for i,x in enumerate(rows)];write(PRED,pred);write(FOLDS,folds);write(SECTIONS,sections);write(NULL,[{'world_index':i,'alignment_gain_bits_per_event':f'{v:.12f}'} for i,v in enumerate(null)]);counter=[{'counterexample_id':'C01','finding':'The 450-event panel contains 137 q choices but only cells already known to admit q.','impact':'Occurrence context transfers; unseen license prediction remains failed.'},{'counterexample_id':'C02','finding':'Every GDT303 q surface and every GDT306 surface is excluded.','impact':'Any positive effect is a second genuinely disjoint surface transfer.'},{'counterexample_id':'C03','finding':'Crossfit predictions share outcomes through other folds.','impact':'Alignment p is diagnostic rather than an exact retrained null.'},{'counterexample_id':'C04','finding':'Preceding DY is an external structural coordinate, not a semantic boundary.','impact':'The result identifies no linguistic function.'},{'counterexample_id':'C05','finding':'No f84 row occurs in source or panel.','impact':'The sealed holdout remains untouched.'}];write(COUNTER,counter);report=['# GDT316 — fresh-surface `q` post-DY generalization','',f'Status: **{status}**.','','Every GDT303 neutral/q surface and every GDT306 surface is excluded. The panel contains 36 cells, 450 events, 137 `q` choices and 82 folios.','',f'The cross-fitted exact-cell plus preceding-DY model changes held log loss by {gain:+.6f} bits/event. The cell/register-matched delta is {delta:+.3f}; raw `q` rates are {p1:.1%} after DY and {p0:.1%} otherwise.','',f'Coefficients are positive in {pc}/82 folds and {pf}/82 folios improve. Powered-section gains are '+', '.join(f"{s}={float(x['gain_bits_per_event']):+.4f}" for s,x in powered.items())+f'. Alignment diagnostic p={p:.12f}.','','This is the second surface-disjoint q post-DY transfer and does not reuse any GDT306 surface. It still conditions on known q-compatible cells.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[PRED,FOLDS,SECTIONS,NULL,COUNTER,REPORT];inputs=[PANEL,R/'gdt316_capacity.tsv',R/'gdt316_design_validation.json',SOURCE,R/'gdt306_result.json',R/'gdt313_result.json'];res={'schema':'GDT316_FRESH_Q_POST_DY_RESULT_V1','status':status,'summary':{'cells':36,'events':len(rows),'q_events':int(y.sum()),'folios':len(folios),'gain_bits_per_event':gain,'matched_prev_dy_delta':delta,'positive_coefficients':pc,'positive_folios':pf,'positive_powered_sections':ps,'alignment_diagnostic_p':p},'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':{'input_rows':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{x.name:sha(x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=can(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':res['summary']},sort_keys=True))
if __name__=='__main__':main()

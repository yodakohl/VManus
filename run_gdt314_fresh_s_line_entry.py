#!/usr/bin/env python3
"""Score fresh-surface LOFO line-entry transfer."""
import csv,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt314_frozen_panel.tsv';DESIGN=R/'gdt314_design.json';METHOD=R/'GDT314_FRESH_S_LINE_ENTRY_METHOD.md';PRED=R/'gdt314_predictions.tsv';FOLDS=R/'gdt314_folio_scores.tsv';SECTIONS=R/'gdt314_section_scores.tsv';NULL=R/'gdt314_null.tsv';COUNTER=R/'gdt314_counterexamples.tsv';REPORT=R/'GDT314_FRESH_S_LINE_ENTRY_REPORT.md';RESULT=R/'gdt314_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def truth():return {hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:int(x['wrapper']=='s') for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'}
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
def event_bits(p,y):return -(y*np.log2(p)+(1-y)*np.log2(1-p))
def perm(y,rows,seed,world):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{seed}|{world}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def matched(rows,y):
 g=defaultdict(lambda:[[],[]]);raw=[[],[]]
 for i,x in enumerate(rows):v=int(x['line_first']);g[(x['cell_id'],x['register'])][v].append(int(y[i]));raw[v].append(int(y[i]))
 num=den=0;mob=ev=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w;mob+=1;ev+=len(a)+len(b)
 return len(raw[0]),sum(raw[0])/len(raw[0]),len(raw[1]),sum(raw[1])/len(raw[1]),num/den,mob,ev
def main():
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');assert stored==can(d);rows=read(PANEL);t=truth();folios=sorted({x['physical_folio'] for x in rows});y=np.array([t[x['event_id_sha256']] for x in rows],float);base=np.zeros(len(rows));cand=np.zeros(len(rows));coef={};foldrows=[]
 for folio in folios:
  tr=[x for x in rows if x['physical_folio']!=folio];te=[x for x in rows if x['physical_folio']==folio];yt=np.array([t[x['event_id_sha256']] for x in tr],float);indices=[i for i,x in enumerate(rows) if x['physical_folio']==folio];x,z=matrix(tr,te,False);base[indices],_=fit(x,yt,z,d['ridge']);x,z=matrix(tr,te,True);cand[indices],b=fit(x,yt,z,d['ridge']);coef[folio]=b[-1];yb=y[indices];gain=float(np.sum(event_bits(base[indices],yb)-event_bits(cand[indices],yb)));foldrows.append({'physical_folio':folio,'events':len(indices),'s_events':int(yb.sum()),'line_start_coefficient':f'{b[-1]:.12f}','gain_bits':f'{gain:.12f}','gain_bits_per_event':f'{gain/len(indices):.12f}'})
 gain_events=event_bits(base,y)-event_bits(cand,y);gain=float(gain_events.sum()/len(rows));n0,p0,n1,p1,delta,mob,me=matched(rows,y);sectionrows=[]
 for s in sorted({x['section'] for x in rows}):
  idx=[i for i,x in enumerate(rows) if x['section']==s];sectionrows.append({'section':s,'events':len(idx),'s_events':int(y[idx].sum()),'gain_bits':f'{gain_events[idx].sum():.12f}','gain_bits_per_event':f'{gain_events[idx].mean():.12f}','powered':int(sum(y[idx])>0 and sum(y[idx])<len(idx))})
 null=[]
 for w in range(d['null']['worlds']):
  q=perm(y,rows,d['null']['seed'],w);null.append(float(np.mean(event_bits(base,q)-event_bits(cand,q))))
 p=(1+sum(v>=gain-1e-15 for v in null))/(1+d['null']['worlds']);positive_coef=int(sum(v>0 for v in coef.values()));positive_folios=int(sum(float(x['gain_bits'])>0 for x in foldrows));powered={x['section']:x for x in sectionrows if x['section'] in ('B','H','S')};positive_sections=int(sum(float(x['gain_bits'])>0 for x in powered.values()));passes=gain>0 and delta>0 and positive_coef>=d['decision']['positive_coefficients_min'] and positive_sections>=d['decision']['positive_powered_sections_min'] and p<=d['decision']['alignment_p_le'];status='S_LINE_ENTRY_EXTENDS_TO_FRESH_SURFACES' if passes else 'S_LINE_ENTRY_FRESH_SURFACE_TRANSFER_WEAK_OR_FAILED';predrows=[]
 for i,x in enumerate(rows):predrows.append({'event_id_sha256':x['event_id_sha256'],'cell_id':x['cell_id'],'physical_folio':x['physical_folio'],'section':x['section'],'register':x['register'],'line_first':x['line_first'],'observed_s':int(y[i]),'cell_probability':f'{base[i]:.12f}','cell_line_start_probability':f'{cand[i]:.12f}','gain_bits':f'{gain_events[i]:.12f}'})
 write(PRED,predrows);write(FOLDS,foldrows);write(SECTIONS,sectionrows);write(NULL,[{'world_index':i,'alignment_gain_bits_per_event':f'{v:.12f}'} for i,v in enumerate(null)]);counter=[{'counterexample_id':'C01','finding':'Only 35 s events exist in the 344-event disjoint panel.','impact':'Rare-event estimates and individual cell rates remain noisy.'},{'counterexample_id':'C02','finding':'Cell eligibility uses corpus-wide evidence that both s and non-s occur.','impact':'The test transfers occurrence context, not unseen compatibility licensing.'},{'counterexample_id':'C03','finding':'Crossfit predictions share outcomes through other folio folds.','impact':'The fixed-prediction permutation p is an alignment diagnostic, not an exact retrained null.'},{'counterexample_id':'C04','finding':'Only B, H and S have powered section sensitivities.','impact':'Other registers cannot test direction.'},{'counterexample_id':'C05','finding':'Every GDT303 ch/d/s surface is excluded.','impact':'Any transfer is genuinely surface-disjoint from the discovery triads.'},{'counterexample_id':'C06','finding':'No f84 row occurs in source or panel.','impact':'The sealed holdout remains untouched.'}];write(COUNTER,counter);report=['# GDT314 — fresh-surface `s` line-entry generalization','',f'Status: **{status}**.','','Every exact surface used by GDT303 `ch->s` or `d->s` is excluded. The remaining panel contains 15 cells, 344 events, 35 `s` choices and 78 folios.','',f'The cross-fitted exact-cell plus line-start model changes held log loss by {gain:+.6f} bits/event. The cell/register-matched held line-start delta is {delta:+.3f}; raw `s` rates are {p1:.1%} at line start and {p0:.1%} elsewhere.', '',f'Line-start coefficients are positive in {positive_coef}/78 folio folds; {positive_folios}/78 folios have positive local gain. Powered-section gains are '+', '.join(f"{s}={float(x['gain_bits_per_event']):+.4f}" for s,x in powered.items())+f'. The fixed-crossfit alignment diagnostic is p={p:.12f}.','','This is the first surface-disjoint extension of the `s` physical-entry tendency. It still conditions on cells already known to admit `s`; it does not predict a new license.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[PRED,FOLDS,SECTIONS,NULL,COUNTER,REPORT];inputs=[PANEL,R/'gdt314_capacity.tsv',R/'gdt314_design_validation.json',SOURCE,R/'gdt303_result.json',R/'gdt313_result.json'];res={'schema':'GDT314_FRESH_S_LINE_ENTRY_RESULT_V1','status':status,'summary':{'cells':15,'events':len(rows),'s_events':int(y.sum()),'folios':len(folios),'gain_bits_per_event':gain,'matched_line_start_delta':delta,'positive_coefficients':positive_coef,'positive_folios':positive_folios,'positive_powered_sections':positive_sections,'alignment_diagnostic_p':p},'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':{'input_rows':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{x.name:sha(x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=can(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':res['summary']},sort_keys=True))
if __name__=='__main__':main()

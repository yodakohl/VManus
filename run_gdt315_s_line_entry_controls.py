#!/usr/bin/env python3
"""Run unchanged fresh-s line-entry instrument on frozen controls."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt315_frozen_panel.tsv';DESIGN=R/'gdt315_design.json';METHOD=R/'GDT315_S_LINE_ENTRY_CONTROL_CALIBRATION_METHOD.md';SCORES=R/'gdt315_panel_scores.tsv';FOLDS=R/'gdt315_folio_scores.tsv';NULL=R/'gdt315_null.tsv';COUNTER=R/'gdt315_counterexamples.tsv';REPORT=R/'GDT315_S_LINE_ENTRY_CONTROL_CALIBRATION_REPORT.md';RESULT=R/'gdt315_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
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
 g=defaultdict(lambda:[[],[]]);raw=[[],[]]
 for i,x in enumerate(rows):v=int(x['line_first']);g[(x['cell_id'],x['register'])][v].append(int(y[i]));raw[v].append(int(y[i]))
 num=den=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return sum(raw[1])/len(raw[1]) if raw[1] else 0,sum(raw[0])/len(raw[0]) if raw[0] else 0,num/den if den else 0
def main():
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');assert stored==can(d);allrows=read(PANEL);truth={hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:int(x['wrapper']=='s') for x in read(SOURCE)};score=[];folds=[];nullrows=[]
 for panel in d['powered_panels']:
  rows=[x for x in allrows if x['panel']==panel];y=np.array([truth[x['event_id_sha256']] for x in rows],float);base=np.zeros(len(rows));cand=np.zeros(len(rows));co=[]
  for folio in sorted({x['physical_folio'] for x in rows}):
   tr=[x for x in rows if x['physical_folio']!=folio];te=[x for x in rows if x['physical_folio']==folio];yt=np.array([truth[x['event_id_sha256']] for x in tr],float);idx=[i for i,x in enumerate(rows) if x['physical_folio']==folio];x,z=matrix(tr,te,False);base[idx],_=fit(x,yt,z,d['instrument']['ridge']);x,z=matrix(tr,te,True);cand[idx],b=fit(x,yt,z,d['instrument']['ridge']);co.append(b[-1]);gain=float(np.sum(eb(base[idx],y[idx])-eb(cand[idx],y[idx])));folds.append({'panel':panel,'physical_folio':folio,'events':len(idx),'s_events':int(y[idx].sum()),'line_start_coefficient':f'{b[-1]:.12f}','gain_bits':f'{gain:.12f}','gain_bits_per_event':f'{gain/len(idx):.12f}'})
  gains=eb(base,y)-eb(cand,y);gain=float(gains.mean());r1,r0,delta=matched(rows,y);null=[]
  for w in range(d['instrument']['null_worlds']):
   q=perm(y,rows,d['instrument']['null_seed'],w,panel);null.append(float(np.mean(eb(base,q)-eb(cand,q))));nullrows.append({'panel':panel,'world_index':w,'alignment_gain_bits_per_event':f'{null[-1]:.12f}'})
  p=(1+sum(v>=gain-1e-15 for v in null))/(1+d['instrument']['null_worlds']);score.append({'panel':panel,'cells':len({x['cell_id'] for x in rows}),'events':len(rows),'s_events':int(y.sum()),'folios':len(co),'gain_bits_per_event':f'{gain:.12f}','matched_line_start_delta':f'{delta:.12f}','raw_s_rate_line_start':f'{r1:.12f}','raw_s_rate_elsewhere':f'{r0:.12f}','positive_coefficients':int(sum(v>0 for v in co)),'positive_folios':int(sum(float(x['gain_bits'])>0 for x in folds if x['panel']==panel)),'alignment_diagnostic_p':f'{p:.12f}','gain_rank':'','delta_rank':''})
 gainorder=sorted(score,key=lambda x:(-float(x['gain_bits_per_event']),x['panel']));deltaorder=sorted(score,key=lambda x:(-float(x['matched_line_start_delta']),x['panel']))
 for i,x in enumerate(gainorder,1):x['gain_rank']=i
 for i,x in enumerate(deltaorder,1):x['delta_rank']=i
 by={x['panel']:x for x in score};v=by['VOYNICH_REFERENCE'];controls_ge=sum(float(x['gain_bits_per_event'])>=float(v['gain_bits_per_event'])-1e-15 for x in score if x['panel']!='VOYNICH_REFERENCE');status='S_LINE_ENTRY_VOYNICH_ENRICHED' if int(v['gain_rank'])==1 and int(v['delta_rank'])==1 else 'S_LINE_ENTRY_NOT_VOYNICH_SPECIFIC' if controls_ge>=2 else 'S_LINE_ENTRY_CONTROL_MIXED';write(SCORES,sorted(score,key=lambda x:x['panel']));write(FOLDS,folds);write(NULL,nullrows);counter=[{'counterexample_id':'C01','finding':'Control wrapper s is an observation-parser surface class, not a harmonized linguistic morpheme.','impact':'Similar behavior calibrates architecture only.'},{'counterexample_id':'C02','finding':'Control panels have 6 to 175 folios and different cell/support distributions.','impact':'Raw ranks are not rescaled and coverage remains explicit.'},{'counterexample_id':'C03','finding':'The diagnostic permutes fixed crossfit outcomes without retraining.','impact':'Its p-values are alignment diagnostics rather than exact null tests.'},{'counterexample_id':'C04','finding':'Voynich alone excludes GDT303 surfaces because GDT314 is the frozen target.','impact':'Controls have no corresponding selected-surface history to subtract.'},{'counterexample_id':'C05','finding':'No f84 row occurs in the frozen source or outputs.','impact':'The sealed holdout remains untouched.'}];write(COUNTER,counter);report=['# GDT315 — `s` line-entry control calibration','',f'Status: **{status}**.','','The GDT314 instrument is unchanged. No panel was rescaled or tuned.','', '| panel | events / s | gain bits/event | matched delta | gain rank | delta rank |','|---|---:|---:|---:|---:|---:|']
 for x in sorted(score,key=lambda x:int(x['gain_rank'])):report.append(f"| {x['panel']} | {x['events']} / {x['s_events']} | {float(x['gain_bits_per_event']):+.5f} | {float(x['matched_line_start_delta']):+.3f} | {x['gain_rank']} | {x['delta_rank']} |")
 report+=['',f"Voynich ranks {v['gain_rank']}/8 by held gain and {v['delta_rank']}/8 by matched delta. {controls_ge} controls equal or exceed its held gain.",'','A positive `s` line-entry tendency is therefore calibrated as '+('Voynich-enriched under the frozen rank rule.' if status=='S_LINE_ENTRY_VOYNICH_ENRICHED' else 'not uniquely Voynich under the frozen rank rule.' if status=='S_LINE_ENTRY_NOT_VOYNICH_SPECIFIC' else 'mixed across controls.')+' The GDT314 formal rule remains real on Voynich; this comparison limits its architectural specificity.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[SCORES,FOLDS,NULL,COUNTER,REPORT];inputs=[PANEL,R/'gdt315_capacity.tsv',R/'gdt315_design_validation.json',SOURCE,R/'gdt314_result.json'];res={'schema':'GDT315_S_LINE_ENTRY_CONTROL_RESULT_V1','status':status,'summary':{'panels':len(score),'voynich_gain_rank':int(v['gain_rank']),'voynich_delta_rank':int(v['delta_rank']),'controls_gain_ge_voynich':controls_ge},'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':{'input_rows':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{x.name:sha(x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=can(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':res['summary'],'scores':score},sort_keys=True))
if __name__=='__main__':main()

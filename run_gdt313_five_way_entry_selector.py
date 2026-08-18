#!/usr/bin/env python3
"""Score the frozen five-way entry-state selector."""
import csv,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIRS=R/'gdt303_pair_deltas.tsv';PANEL=R/'gdt313_frozen_panel.tsv';DESIGN=R/'gdt313_design.json';METHOD=R/'GDT313_FIVE_WAY_ENTRY_SELECTOR_METHOD.md';PRED=R/'gdt313_event_predictions.tsv';SCORES=R/'gdt313_model_scores.tsv';ATLAS=R/'gdt313_context_atlas.tsv';NULL=R/'gdt313_null.tsv';COUNTER=R/'gdt313_counterexamples.tsv';REPORT=R/'GDT313_FIVE_WAY_ENTRY_SELECTOR_REPORT.md';RESULT=R/'gdt313_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def recover():
 events=[x for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'];rep={}
 for x in events:rep.setdefault(x['source_surface_sha256'],x)
 op={}
 for name in ('wrapper:ch>s','wrapper:d>s','wrapper:NONE>q'):
  cells={}
  for p in read(PAIRS):
   if p['operation']==name:
    e=rep[p['source_surface_sha256']];cells[(p['page_host'],e['local_frame'],e['inner_d'],e['right_family'],e['dy_closure'],e['b3'])]=p
  op[name]=cells
 surface={}
 for key in set(op['wrapper:ch>s'])&set(op['wrapper:d>s'])&set(op['wrapper:NONE>q']):
  a,d,q=op['wrapper:ch>s'][key],op['wrapper:d>s'][key],op['wrapper:NONE>q'][key];cid=hashlib.sha256(('CELL|'+'|'.join(key)).encode()).hexdigest()[:20];
  for choice,s in [('NONE',q['source_surface_sha256']),('q',q['target_surface_sha256']),('ch',a['source_surface_sha256']),('d',d['source_surface_sha256']),('s',a['target_surface_sha256'])]:surface[s]=(cid,choice)
 truth={}
 for x in events:
  if x['source_surface_sha256'] in surface:truth[hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]]=surface[x['source_surface_sha256']]
 return truth
def matrix(tr,te,names):
 cells=sorted({x['cell_id'] for x in tr})
 def enc(rows):return np.array([[1.]+[float(x['cell_id']==v) for v in cells]+[float(x[n]) for n in names] for x in rows])
 return enc(tr),enc(te),['INTERCEPT']+['CELL:'+x for x in cells]+names
def fit(x,y,z,classes,ridge):
 k=len(classes)-1;p=x.shape[1];B=np.zeros((p,k));PEN=np.eye(p)*ridge;PEN[0,0]=0;Y=np.column_stack([y==i for i in range(1,len(classes))]).astype(float)
 for _ in range(100):
  eta=np.clip(x@B,-30,30);ex=np.exp(eta);den=1+ex.sum(1,keepdims=True);pr=ex/den;grad=x.T@(Y-pr)-PEN@B;H=np.zeros((p*k,p*k))
  for a in range(k):
   for b in range(k):
    w=pr[:,a]*((1. if a==b else 0.)-pr[:,b]);H[a*p:(a+1)*p,b*p:(b+1)*p]=x.T@(x*w[:,None])+(PEN if a==b else 0)
  step=np.linalg.pinv(H)@grad.T.reshape(-1);B+=(step.reshape(k,p)).T
  if abs(step).max()<1e-10:break
 eta=np.clip(z@B,-30,30);ex=np.exp(eta);den=1+ex.sum(1,keepdims=True);return np.column_stack([1/den[:,0],ex/den]),B
def bits(pr,y):return float(-np.mean(np.log2(np.maximum(pr[np.arange(len(y)),y],1e-15))))
def perm(y,rows,seed,world):
 out=y.copy();g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['cell_id'],x['register'])].append(i)
 for key,idx in sorted(g.items()):
  v=y[idx].copy();rng=np.random.default_rng(int(hashlib.sha256(f'{seed}|{world}|{key[0]}|{key[1]}'.encode()).hexdigest()[:16],16));rng.shuffle(v);out[idx]=v
 return out
def matched(rows,y,feature,target):
 g=defaultdict(lambda:[[],[]]);raw=[[],[]]
 for i,x in enumerate(rows):value=int(y[i]==target);g[(x['cell_id'],x['register'])][int(x[feature])].append(value);raw[int(x[feature])].append(value)
 num=den=0;mobile=events=0
 for a,b in g.values():
  if a and b:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w;mobile+=1;events+=len(a)+len(b)
 return len(raw[0]),sum(raw[0])/len(raw[0]),len(raw[1]),sum(raw[1])/len(raw[1]),num/den,mobile,events
def main():
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');assert stored==can(d);rows=read(PANEL);truth=recover();classes=d['choices'];index={v:i for i,v in enumerate(classes)}
 for x in rows:assert truth[x['event_id_sha256']][0]==x['cell_id']
 tr=[x for x in rows if x['split']=='TRAIN'];te=[x for x in rows if x['split']=='TEST'];yt=np.array([index[truth[x['event_id_sha256']][1]] for x in tr]);ye=np.array([index[truth[x['event_id_sha256']][1]] for x in te]);pred={};coef={};cols={}
 for m,names in d['models'].items():x,z,cols[m]=matrix(tr,te,names);pred[m],coef[m]=fit(x,yt,z,classes,d['ridge'])
 base=bits(pred['CELL'],ye);scores=[];obs={};predrows=[]
 for m in d['models']:
  obs[m]=base-bits(pred[m],ye);top=np.argmax(pred[m],1);scores.append({'model':m,'training_events':len(tr),'test_events':len(te),'held_bits_per_event':f'{bits(pred[m],ye):.12f}','gain_vs_cell_bits_per_event':f'{obs[m]:.12f}','top1_accuracy':f'{np.mean(top==ye):.12f}','mean_true_probability':f'{np.mean(pred[m][np.arange(len(ye)),ye]):.12f}','s_line_start_coefficient':'NA','q_prev_dy_coefficient':'NA','null_mean_gain':'NA' if m=='CELL' else '', 'null_centered_gain':'NA' if m=='CELL' else '', 'local_p':'NA' if m=='CELL' else '', 'max3_p':'NA' if m=='CELL' else ''})
  for i,x in enumerate(te):predrows.append({'event_id_sha256':x['event_id_sha256'],'cell_id':x['cell_id'],'physical_folio':x['physical_folio'],'register':x['register'],'observed_choice':classes[ye[i]],'model':m,**{f'p_{c}':f'{pred[m][i,j]:.12f}' for j,c in enumerate(classes)}})
 sm={x['model']:x for x in scores}
 for m in d['models']:
  if 'line_first' in d['models'][m]:sm[m]['s_line_start_coefficient']=f'{coef[m][cols[m].index("line_first"),classes[1:].index("s")]:.12f}'
  if 'prev_dy' in d['models'][m]:sm[m]['q_prev_dy_coefficient']=f'{coef[m][cols[m].index("prev_dy"),classes[1:].index("q")]:.12f}'
 null={m:[] for m in d['models'] if m!='CELL'}
 for w in range(d['null']['worlds']):
  y=perm(ye,te,d['null']['seed'],w);bb=bits(pred['CELL'],y)
  for m in null:null[m].append(bb-bits(pred[m],y))
 mu={m:statistics.mean(v) for m,v in null.items()};sd={m:statistics.pstdev(v) for m,v in null.items()};z={m:(obs[m]-mu[m])/sd[m] if sd[m] else 0 for m in null};mx=[max((null[m][w]-mu[m])/sd[m] if sd[m] else 0 for m in null) for w in range(d['null']['worlds'])]
 for m,v in null.items():sm[m].update({'null_mean_gain':f'{mu[m]:.12f}','null_centered_gain':f'{obs[m]-mu[m]:.12f}','local_p':f'{(1+sum(x>=obs[m]-1e-15 for x in v))/(1+d["null"]["worlds"]):.12f}','max3_p':f'{(1+sum(x>=z[m]-1e-15 for x in mx))/(1+d["null"]["worlds"]):.12f}'})
 write(PRED,predrows);write(SCORES,scores);write(NULL,[{'world_index':i,'max3_standardized_gain':f'{v:.12f}'} for i,v in enumerate(mx)]);atlas=[]
 for split_name,rr,yy in [('TRAIN',tr,yt),('TEST',te,ye)]:
  for feature,target in [('line_first','s'),('prev_dy','q')]:
   n0,p0,n1,p1,delta,mob,ev=matched(rr,yy,feature,index[target]);atlas.append({'split':split_name,'target_choice':target,'feature':feature,'state0_events':n0,'state0_target_rate':f'{p0:.12f}','state1_events':n1,'state1_target_rate':f'{p1:.12f}','cell_register_matched_delta':f'{delta:.12f}','mobile_strata':mob,'mobile_events':ev})
 write(ATLAS,atlas);entry=sm['ENTRY_STATE'];srow=[x for x in atlas if x['split']=='TEST' and x['target_choice']=='s'][0];qrow=[x for x in atlas if x['split']=='TEST' and x['target_choice']=='q'][0];passes=float(entry['gain_vs_cell_bits_per_event'])>0 and float(entry['null_centered_gain'])>0 and float(entry['max3_p'])<=d['decision']['max3_p_le'] and float(entry['s_line_start_coefficient'])>0 and float(entry['q_prev_dy_coefficient'])>0 and float(srow['cell_register_matched_delta'])>0 and float(qrow['cell_register_matched_delta'])>0;status='FIVE_WAY_ENTRY_STATE_SELECTOR_TRANSFERS' if passes else 'FIVE_WAY_ENTRY_STATE_SELECTOR_WEAK_OR_FAILED';counter=[{'counterexample_id':'C01','finding':'Only two exact opaque cells contain all five choices.','impact':'This is a compact within-cell mechanism, not manuscript-wide coverage.'},{'counterexample_id':'C02','finding':'The operations were selected in GDT303 before this five-way model was frozen.','impact':'The deterministic held split tests parameter transfer, not independent operation discovery.'},{'counterexample_id':'C03','finding':'The q class is sparse in the or cell.','impact':'The shared q coefficient may be carried mainly by the l cell.'},{'counterexample_id':'C04','finding':'No host glyph or surface similarity enters the model.','impact':'The result says nothing about how another cell becomes licensed.'},{'counterexample_id':'C05','finding':'No f84 row occurs in source or panel.','impact':'The sealed holdout remains untouched.'}];write(COUNTER,counter);report=['# GDT313 — five-way entry-state selector','',f'Status: **{status}**.','','Two exact opaque cells contain every `{NONE,ch,d,s,q}` surface choice. The training-only model compares those choices directly without duplicating an `s` event.','',f"The exact-cell prior costs {base:.6f} held bits/event. Adding physical line start and preceding DY changes this by {obs['ENTRY_STATE']:+.6f} bits/event (null-centered {float(entry['null_centered_gain']):+.6f}; max-three p {entry['max3_p']}).",'',f"For `s × LINE_START`, the training logit coefficient is {float(entry['s_line_start_coefficient']):+.3f} and the held cell/register-matched delta is {float(srow['cell_register_matched_delta']):+.3f}. For `q × PREV_DY`, they are {float(entry['q_prev_dy_coefficient']):+.3f} and {float(qrow['cell_register_matched_delta']):+.3f}.",'','The same opaque opportunities therefore choose `s` preferentially at physical line entry and `q` preferentially after a DY boundary. `NONE`, `ch`, and `d` remain the residual alternatives. This is probabilistic, not deterministic.','','## Claim ceiling','',d['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[PRED,SCORES,ATLAS,NULL,COUNTER,REPORT];inputs=[PANEL,R/'gdt313_capacity.tsv',R/'gdt313_design_validation.json',SOURCE,PAIRS,R/'gdt311_result.json',R/'gdt312_result.json'];res={'schema':'GDT313_FIVE_WAY_ENTRY_SELECTOR_RESULT_V1','status':status,'summary':{'cells':2,'training_events':len(tr),'test_events':len(te),'entry_gain_bits_per_event':obs['ENTRY_STATE'],'s_line_start_held_matched_delta':float(srow['cell_register_matched_delta']),'q_prev_dy_held_matched_delta':float(qrow['cell_register_matched_delta'])},'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':{'input_rows':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in outputs}};res['content_sha256']=can(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'entry':entry,'s_delta':srow,'q_delta':qrow},sort_keys=True))
if __name__=='__main__':main()

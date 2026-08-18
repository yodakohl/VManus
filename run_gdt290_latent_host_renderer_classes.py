#!/usr/bin/env python3
"""Run frozen GDT290 latent opaque host renderer classes."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;DESIGN=R/'gdt290_design.json';METHOD=R/'GDT290_LATENT_HOST_RENDERER_CLASSES_METHOD.md';REPORT=R/'GDT290_LATENT_HOST_RENDERER_CLASSES_REPORT.md';RESULT=R/'gdt290_result.json'
OUT_PANEL=R/'gdt290_panel_scores.tsv';OUT_FOLD=R/'gdt290_folio_scores.tsv';OUT_DETAIL=R/'gdt290_class_breakdown.tsv';OUT_NULL=R/'gdt290_null_results.tsv';OUT_SENS=R/'gdt290_voynich_sensitivities.tsv';OUT_COUNTER=R/'gdt290_counterexamples.tsv';MODELS=('POSITION_CONTEXT','OTHER_POSITION_HOST_BAG','LATENT_HOST_CLASS');PRIOR=11.;ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rcsha(v):q=dict(v);q.pop('content_sha256',None);return csha(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 ff=[]
 for r in rr:
  for k in r:
   if k not in ff:ff.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'NA') for k in ff} for r in rr])
def bucket(panel,h):return int(hashlib.sha256(f'GDT289_HOST_BUCKET|{panel}|{h}'.encode()).hexdigest()[:16],16)%8
def bkey(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def nkey(r):return (r['physical_folio'],)+bkey(r)
def feature(pm,target,positions,wr):
 z=[]
 for s in positions:
  if s==target:continue
  c=pm.get(s,{});n=sum(c.values());z.extend([c.get(w,0)/n if n else 0. for w in wr]);z.append(0. if n else 1.)
 return np.asarray(z,dtype=float)
def cluster_model(profiles,panel,b,target,positions,wr,k):
 hosts=sorted(h for h,pm in profiles.items() if bucket(panel,h)!=b and target in pm and any(s!=target and sum(c.values()) for s,c in pm.items()))
 if len(hosts)<3*k:return None
 X=np.vstack([feature(profiles[h],target,positions,wr) for h in hosts]);first=min(range(len(hosts)),key=lambda i:(hashlib.sha256(f'GDT290_KMEANS_INIT|{panel}|{target}|{hosts[i]}'.encode()).hexdigest(),hosts[i]));chosen=[first]
 while len(chosen)<k:
  dist=np.min(np.sum((X[:,None,:]-X[np.asarray(chosen)][None,:,:])**2,axis=2),axis=1);dist[np.asarray(chosen)]=-1.;chosen.append(sorted((i for i in range(len(hosts)) if i not in chosen),key=lambda i:(-dist[i],hosts[i]))[0])
 cen=X[np.asarray(chosen)].copy();lab=np.full(len(hosts),-1,dtype=int)
 for _ in range(30):
  nl=np.argmin(np.sum((X[:,None,:]-cen[None,:,:])**2,axis=2),axis=1)
  if np.array_equal(nl,lab):break
  lab=nl
  for j in range(k):
   if np.any(lab==j):cen[j]=X[lab==j].mean(axis=0)
 acc=np.zeros((k,len(wr)),float);nh=np.zeros(k,int)
 for i,h in enumerate(hosts):
  c=profiles[h][target];n=sum(c.values());nh[lab[i]]+=1
  for j,w in enumerate(wr):acc[lab[i],j]+=c[w]/n
 probs=(acc+ALPHA)/(nh[:,None]+ALPHA*len(wr));return cen,probs,nh,len(hosts)
def score(events,panel,k=4,split='physical_folio'):
 wr=sorted({r['wrapper'] for r in events});K=len(wr);positions=sorted({r['within_field_position'] for r in events});folds=defaultdict(list)
 for i,r in enumerate(events):folds[r[split]].append(i)
 bits=Counter();top=Counter();scored=[];foldrows=[];detail=defaultdict(lambda:[0,0.]);capacity=[]
 for held,tests in sorted(folds.items()):
  train=[i for i,r in enumerate(events) if r[split]!=held];g=Counter(events[i]['wrapper'] for i in train);base=defaultdict(Counter);profiles=defaultdict(lambda:defaultdict(Counter))
  for i in train:r=events[i];base[bkey(r)][r['wrapper']]+=1;profiles[r['page_host']][r['within_field_position']][r['wrapper']]+=1
  models={(b,t):cluster_model(profiles,panel,b,t,positions,wr,k) for b in range(8) for t in positions};fb=Counter();ft=Counter();fn=0
  for i in tests:
   r=events[i];h=r['page_host'];t=r['within_field_position'];b=bucket(panel,h);pm=profiles.get(h,{});other={s:c for s,c in pm.items() if s!=t and sum(c.values())};nn=sum(sum(c.values()) for c in other.values());model=models[b,t]
   if not nn or model is None:continue
   bc=base[bkey(r)];nb=sum(bc.values());p0={w:(g[w]+ALPHA)/(len(train)+ALPHA*K) for w in wr};pb={w:(bc[w]+PRIOR*p0[w])/(nb+PRIOR) for w in wr};cc=Counter()
   for c in other.values():cc.update(c)
   bag={w:(cc[w]+PRIOR*pb[w])/(nn+PRIOR) for w in wr};cen,cp,nh,ntrainhosts=model;x=feature(pm,t,positions,wr);cl=int(np.argmin(np.sum((cen-x[None,:])**2,axis=1)));cls={w:(nn*cp[cl,j]+PRIOR*pb[w])/(nn+PRIOR) for j,w in enumerate(wr)};actual=r['wrapper'];pp={'POSITION_CONTEXT':pb,'OTHER_POSITION_HOST_BAG':bag,'LATENT_HOST_CLASS':cls}
   for m in MODELS:
    z=-math.log2(pp[m][actual]);bits[m]+=z;fb[m]+=z;ok=int(max(wr,key=lambda w:(pp[m][w],-wr.index(w)))==actual);top[m]+=ok;ft[m]+=ok
   gain=math.log2(cls[actual]/bag[actual]);detail['BUCKET',str(b)][0]+=1;detail['BUCKET',str(b)][1]+=gain;detail['POSITION',t][0]+=1;detail['POSITION',t][1]+=gain;detail['FOLD',held][0]+=1;detail['FOLD',held][1]+=gain;detail['CLASS',str(cl)][0]+=1;detail['CLASS',str(cl)][1]+=gain;capacity.append((held,b,t,ntrainhosts,int(sum(nh>0))));scored.append({'actual':actual,'bag':bag,'class':cls,'null_key':nkey(r)});fn+=1
  for m in MODELS:foldrows.append({'control_id':panel,'k':k,'split':'HELD_'+split.upper(),'held_value':held,'model':m,'scored_events':fn,'bits':fb[m],'top1':ft[m]})
 return {'bits':dict(bits),'top':dict(top),'n':len(scored),'scored':scored,'foldrows':foldrows,'detail':{q:list(z) for q,z in detail.items()},'capacity':capacity}
def nulls(q,panel,k):
 if q['n']==0:return [],0
 st=defaultdict(list)
 for i,r in enumerate(q['scored']):st[r['null_key']].append(i)
 out=[];mob=0
 for world in range(64):
  yy=[r['actual'] for r in q['scored']]
  for key,ids in sorted(st.items(),key=lambda z:repr(z[0])):
   seed=f"GDT290_HELD_WRAPPER_ALIGNMENT|{panel}|{k}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[yy[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=yy[i]:mob+=1
    yy[i]=x
  out.append(sum(math.log2(r['class'][y]/r['bag'][y]) for r,y in zip(q['scored'],yy))/q['n'])
 return out,mob
def job(item):
 p,e=item;q=score(e,p,4);ng,mob=nulls(q,p,4);return p,q,ng,mob
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='CAPACITY_CORRECTED_FROZEN_BEFORE_GDT290_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt290_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(x)==8448 for x in panels.values());rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,x):x[0] for x in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z;print(json.dumps({'panel':z[0],'scored':z[1]['n']},sort_keys=True),flush=True)
 panelrows=[];foldrows=[];detailrows=[];nullrows=[];obs={};ngs={};mobile={}
 for p in d['panels']:
  _,q,ng,mob=rr[p];mobile[p]=mob;ngs[p]=ng;obs[p]=(q['bits']['OTHER_POSITION_HOST_BAG']-q['bits']['LATENT_HOST_CLASS'])/q['n'] if q['n'] else None
  for m in MODELS:panelrows.append({'control_id':p,'k':4,'capacity_status':'SCORED' if q['n'] else 'UNSCORED_NO_LATENT_CLASS_CAPACITY','model':m,'scored_events':q['n'],'bits':f"{q['bits'].get(m,0):.12f}" if q['n'] else 'NA','bits_per_event':f"{q['bits'].get(m,0)/q['n']:.12f}" if q['n'] else 'NA','top1':q['top'].get(m,0) if q['n'] else 'NA','top1_rate':f"{q['top'].get(m,0)/q['n']:.12f}" if q['n'] else 'NA'})
  for x in q['foldrows']:foldrows.append({**x,'bits':f"{x['bits']:.12f}"})
  for (kind,val),z in sorted(q['detail'].items()):detailrows.append({'control_id':p,'k':4,'breakdown':kind,'value':val,'scored_events':z[0],'gain_bits':f'{z[1]:.12f}','gain_bits_per_event':f'{z[1]/z[0]:.12f}'})
  for w,v in enumerate(ng):nullrows.append({'control_id':p,'k':4,'world_index':w,'class_gain_bits_per_event':f'{v:.12f}'})
 sens=[]
 for k in d['voynich_sensitivity_k']:
  q=score(panels['VOYNICH_REFERENCE'],'VOYNICH_REFERENCE',k);sens.append({'split':'HELD_PHYSICAL_FOLIO','k':k,'scored_events':q['n'],'gain_bits_per_event':(q['bits']['OTHER_POSITION_HOST_BAG']-q['bits']['LATENT_HOST_CLASS'])/q['n'],'positive_buckets':sum(z[1]>0 for a,z in q['detail'].items() if a[0]=='BUCKET'),'positive_positions':sum(z[1]>0 for a,z in q['detail'].items() if a[0]=='POSITION')})
 for split in ('section','hand'):
  q=score(panels['VOYNICH_REFERENCE'],'VOYNICH_REFERENCE',4,split);sens.append({'split':'HELD_'+split.upper(),'k':4,'scored_events':q['n'],'gain_bits_per_event':(q['bits']['OTHER_POSITION_HOST_BAG']-q['bits']['LATENT_HOST_CLASS'])/q['n'],'positive_buckets':sum(z[1]>0 for a,z in q['detail'].items() if a[0]=='BUCKET'),'positive_positions':sum(z[1]>0 for a,z in q['detail'].items() if a[0]=='POSITION')})
 sensrows=[{**x,'gain_bits_per_event':f"{x['gain_bits_per_event']:.12f}"} for x in sens];write(OUT_PANEL,panelrows);write(OUT_FOLD,foldrows);write(OUT_DETAIL,detailrows);write(OUT_NULL,nullrows);write(OUT_SENS,sensrows)
 means={p:statistics.mean(ngs[p]) if ngs[p] else None for p in d['panels']};sds={p:statistics.pstdev(ngs[p]) if ngs[p] else None for p in d['panels']};var=[p for p in d['panels'] if sds[p] is not None and sds[p]>0];zs={p:(obs[p]-means[p])/sds[p] for p in var};wm=[max((ngs[p][i]-means[p])/sds[p] for p in var) for i in range(64)];summary=[]
 for p in d['panels']:
  q=rr[p][1];cap=q['n']>0;vv=p in var;local=(1+sum(x>=obs[p]-1e-15 for x in ngs[p]))/65 if vv else None;mp=(1+sum(x>=zs[p]-1e-15 for x in wm))/65 if vv else None;na='NA_ZERO_NULL_VARIANCE' if cap else 'NA_NO_LATENT_CLASS_CAPACITY';summary.append({'control_id':p,'capacity_status':'SCORED' if cap else 'UNSCORED_NO_LATENT_CLASS_CAPACITY','scored_events':q['n'],'folios':len({x['physical_folio'] for x in panels[p]}),'k4_gain_bits_per_event':f'{obs[p]:.12f}' if cap else 'NA','null_mean':f'{means[p]:.12f}' if cap else 'NA','null_sd':f'{sds[p]:.12f}' if cap else 'NA','observed_z':f'{zs[p]:.12f}' if vv else na,'local_p':f'{local:.12f}' if vv else na,'max_variable_family_p':f'{mp:.12f}' if vv else na,'null_variable_panels':len(var),'null_mobile_world0':mobile[p],'positive_host_buckets':sum(z[1]>0 for a,z in q['detail'].items() if a[0]=='BUCKET'),'positive_positions':sum(z[1]>0 for a,z in q['detail'].items() if a[0]=='POSITION')})
 v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');ss={x['split']:x for x in sens};g={'minimum_capacity':int(v['scored_events'])>=d['minimum_voynich_scored_events'],'primary_gain_positive':float(v['k4_gain_bits_per_event'])>0,'at_least_six_positive_host_buckets':int(v['positive_host_buckets'])>=6,'at_least_three_positive_positions':int(v['positive_positions'])>=3,'maxT_p_le_0_05':not v['max_variable_family_p'].startswith('NA') and float(v['max_variable_family_p'])<=.05,'held_section_gain_positive':ss['HELD_SECTION']['gain_bits_per_event']>0,'held_hand_gain_positive':ss['HELD_HAND']['gain_bits_per_event']>0};status=d['decision']['capacity'] if not g['minimum_capacity'] else d['decision']['support'] if all(g.values()) else d['decision']['fail']
 counters=[{'counterexample':'K4_DOES_NOT_BEAT_OTHER_POSITION_BAG','evidence':f"Voynich gain {float(v['k4_gain_bits_per_event']):+.6f} bits/event",'impact':'nonpositive gain rejects compact classes'}, {'counterexample':'K4_GAIN_CONCENTRATED','evidence':f"positive buckets {v['positive_host_buckets']}/8; positions {v['positive_positions']}/4",'impact':'fails reuse if below frozen floors'}, {'counterexample':'K_SCALE_RESCUE_ONLY','evidence':'; '.join(f"K{x['k']} {x['gain_bits_per_event']:+.6f}" for x in sens if x['split']=='HELD_PHYSICAL_FOLIO'),'impact':'K2/K8 cannot replace primary'}, {'counterexample':'REGISTER_TRANSFER_FAILS','evidence':f"section {ss['HELD_SECTION']['gain_bits_per_event']:+.6f}; hand {ss['HELD_HAND']['gain_bits_per_event']:+.6f}",'impact':'either nonpositive fails compact transfer'}, {'counterexample':'F84_USED','evidence':'only f84-free native event inventory read','impact':'no f84 access'}];write(OUT_COUNTER,counters)
 report=['# GDT290 — latent opaque host renderer classes','',f'Status: **{status}**.','','## K=4 primary','', '| panel | scored | gain (bits/event) | buckets + | positions + | local p | max-family p |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summary:
  lp=x['local_p'] if x['local_p'].startswith('NA') else f"{float(x['local_p']):.4f}";mp=x['max_variable_family_p'] if x['max_variable_family_p'].startswith('NA') else f"{float(x['max_variable_family_p']):.4f}";gain='NA' if x['k4_gain_bits_per_event']=='NA' else f"{float(x['k4_gain_bits_per_event']):+.4f}";report.append(f"| {x['control_id']} | {x['scored_events']} | {gain} | {x['positive_host_buckets']}/8 | {x['positive_positions']}/4 | {lp} | {mp} |")
 report +=['','## Voynich sensitivities','']+[f"- {x['split']} K={x['k']}: {x['gain_bits_per_event']:+.4f} bits/event on {x['scored_events']} events; buckets {x['positive_buckets']}/8, positions {x['positive_positions']}/4." for x in sens]+['','## Frozen gates','']+[f"- `{k}`: **{'PASS' if z else 'FAIL'}**" for k,z in g.items()]+['','The target host-position cell is absent from both its feature vector and its class target estimate. Hosts in its immutable bucket never train that class model.','','## Claim ceiling','','This can identify only compact opaque renderer classes. It cannot establish lexical classes, morphology, grammar functions, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_PANEL,OUT_FOLD,OUT_DETAIL,OUT_NULL,OUT_SENS,OUT_COUNTER,REPORT];inputs=['gdt290_design.json','gdt290_design_validation.json','gdt290_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt289_result.json','gdt288_result.json'];res={'schema':'GDT290_LATENT_HOST_RENDERER_CLASSES_RESULT_V1','status':status,'summary':summary,'voynich_summary':v,'voynich_sensitivities':sens,'frozen_gates':g,'null_variable_panels':var,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich':v,'sensitivities':sens,'gates':g},sort_keys=True))
if __name__=='__main__':main()

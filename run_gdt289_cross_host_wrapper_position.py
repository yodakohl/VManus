#!/usr/bin/env python3
"""Run frozen GDT289 cross-host wrapper-position transfer."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;DESIGN=R/'gdt289_design.json';METHOD=R/'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_METHOD.md';REPORT=R/'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_REPORT.md';RESULT=R/'gdt289_result.json'
OUT_PANEL=R/'gdt289_panel_scores.tsv';OUT_FOLD=R/'gdt289_folio_scores.tsv';OUT_DETAIL=R/'gdt289_transfer_breakdown.tsv';OUT_NULL=R/'gdt289_null_results.tsv';OUT_SENS=R/'gdt289_voynich_sensitivities.tsv';OUT_COUNTER=R/'gdt289_counterexamples.tsv'
MODELS=('POSITION_CONTEXT','OTHER_POSITION_HOST_BAG','CROSS_HOST_POSITION_TRANSFER');PRIOR=11.;ALPHA=.5
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
def transition_tables(profiles,panel,target_bucket,positions,wr):
 joint=defaultdict(float);den=defaultdict(float)
 for h,pmap in profiles.items():
  if bucket(panel,h)==target_bucket:continue
  for s in positions:
   if s not in pmap:continue
   ns=sum(pmap[s].values());ps={u:c/ns for u,c in pmap[s].items()}
   for t in positions:
    if t==s or t not in pmap:continue
    nt=sum(pmap[t].values());pt={v:c/nt for v,c in pmap[t].items()}
    for u,pu in ps.items():
     den[s,t,u]+=pu
     for v,pv in pt.items():joint[s,t,u,v]+=pu*pv
 return joint,den
def score(events,panel,split='physical_folio'):
 wr=sorted({r['wrapper'] for r in events});K=len(wr);positions=sorted({r['within_field_position'] for r in events});wi={w:i for i,w in enumerate(wr)};folds=defaultdict(list)
 for i,r in enumerate(events):folds[r[split]].append(i)
 scored=[];foldrows=[];total_bits=Counter();total_top=Counter();detail=defaultdict(lambda:[0,0.,0.])
 for held,test_ids in sorted(folds.items()):
  train=[i for i,r in enumerate(events) if r[split]!=held];g=Counter(events[i]['wrapper'] for i in train);base=defaultdict(Counter);profiles=defaultdict(lambda:defaultdict(Counter))
  for i in train:
   r=events[i];base[bkey(r)][r['wrapper']]+=1;profiles[r['page_host']][r['within_field_position']][r['wrapper']]+=1
  tables={b:transition_tables(profiles,panel,b,positions,wr) for b in range(8)};fb=Counter();ft=Counter();fn=0
  for i in test_ids:
   r=events[i];t=r['within_field_position'];h=r['page_host'];other={s:c for s,c in profiles.get(h,{}).items() if s!=t and sum(c.values())>0};nother=sum(sum(c.values()) for c in other.values())
   if nother<=0:continue
   bc=base[bkey(r)];nb=sum(bc.values());p0={w:(g[w]+ALPHA)/(len(train)+ALPHA*K) for w in wr};pb={w:(bc[w]+PRIOR*p0[w])/(nb+PRIOR) for w in wr};bagc=Counter()
   for c in other.values():bagc.update(c)
   pbag={w:(bagc[w]+PRIOR*pb[w])/(nother+PRIOR) for w in wr};joint,den=tables[bucket(panel,h)];forecast={w:0. for w in wr}
   for s,c in other.items():
    ns=sum(c.values())
    for u,cu in c.items():
     pu=cu/ns;dd=den[s,t,u]+ALPHA*K
     for v in wr:forecast[v]+=ns*pu*(joint[s,t,u,v]+ALPHA)/dd
   forecast={w:forecast[w]/nother for w in wr};ptr={w:(nother*forecast[w]+PRIOR*pb[w])/(nother+PRIOR) for w in wr};actual=r['wrapper'];probs={'POSITION_CONTEXT':pb,'OTHER_POSITION_HOST_BAG':pbag,'CROSS_HOST_POSITION_TRANSFER':ptr};bits={m:-math.log2(probs[m][actual]) for m in MODELS};tops={m:int(max(wr,key=lambda w:(probs[m][w],-wi[w]))==actual) for m in MODELS}
   for m in MODELS:fb[m]+=bits[m];ft[m]+=tops[m];total_bits[m]+=bits[m];total_top[m]+=tops[m]
   fn+=1;gain=bits['OTHER_POSITION_HOST_BAG']-bits['CROSS_HOST_POSITION_TRANSFER'];detail['BUCKET',str(bucket(panel,h))][0]+=1;detail['BUCKET',str(bucket(panel,h))][1]+=gain;detail['POSITION',t][0]+=1;detail['POSITION',t][1]+=gain;detail['FOLD',held][0]+=1;detail['FOLD',held][1]+=gain
   scored.append({'actual':actual,'bag':pbag,'transfer':ptr,'null_key':nkey(r),'bucket':bucket(panel,h),'position':t,'held':held,'observation_id':r['observation_id']})
  for m in MODELS:foldrows.append({'control_id':panel,'split':'HELD_'+split.upper(),'held_value':held,'model':m,'scored_events':fn,'bits':fb[m],'top1':ft[m]})
 for k,v in detail.items():v[2]=v[1]/v[0] if v[0] else 0.
 return {'wr':wr,'bits':dict(total_bits),'top':dict(total_top),'n':len(scored),'scored':scored,'foldrows':foldrows,'detail':{k:list(v) for k,v in detail.items()}}
def null_gains(q,panel):
 strata=defaultdict(list)
 for i,r in enumerate(q['scored']):strata[r['null_key']].append(i)
 out=[];mobile0=0
 for world in range(64):
  yy=[r['actual'] for r in q['scored']]
  for key,ids in sorted(strata.items(),key=lambda z:repr(z[0])):
   seed=f"GDT289_HELD_WRAPPER_ALIGNMENT|{panel}|{world}|"+'|'.join(map(str,key));rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16));v=[yy[i] for i in ids];rng.shuffle(v)
   for i,x in zip(ids,v):
    if world==0 and x!=yy[i]:mobile0+=1
    yy[i]=x
  gain=sum(math.log2(r['transfer'][y]/r['bag'][y]) for r,y in zip(q['scored'],yy))/q['n']
  out.append(gain)
 return out,mobile0
def job(item):
 panel,events=item;q=score(events,panel);null,mob=null_gains(q,panel);sens=[]
 if panel=='VOYNICH_REFERENCE':
  for s in ('section','hand'):sens.append((s,score(events,panel,s)))
 return panel,q,null,mob,sens
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='CAPACITY_CORRECTED_FROZEN_BEFORE_GDT289_SCORING' and d['content_sha256']==rcsha(d) and d['target_page_outcomes_used'] is False
 for x in read(R/'gdt289_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(x)==8448 for x in panels.values())
 rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,x):x[0] for x in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z;print(json.dumps({'scored':z[0],'events':z[1]['n']},sort_keys=True),flush=True)
 panelrows=[];foldrows=[];detailrows=[];nullrows=[];sensrows=[];obs={};nulls={};mobile={}
 for p in d['panels']:
  _,q,ng,mob,sens=rr[p];mobile[p]=mob;nulls[p]=ng;obs[p]=(q['bits']['OTHER_POSITION_HOST_BAG']-q['bits']['CROSS_HOST_POSITION_TRANSFER'])/q['n']
  for m in MODELS:panelrows.append({'control_id':p,'model':m,'scored_events':q['n'],'bits':f"{q['bits'][m]:.12f}",'bits_per_event':f"{q['bits'][m]/q['n']:.12f}",'top1':q['top'][m],'top1_rate':f"{q['top'][m]/q['n']:.12f}"})
  for x in q['foldrows']:foldrows.append({**x,'bits':f"{x['bits']:.12f}",'gain_bits':f"{next((y['bits'] for y in q['foldrows'] if y['held_value']==x['held_value'] and y['model']=='OTHER_POSITION_HOST_BAG'),0)-next((y['bits'] for y in q['foldrows'] if y['held_value']==x['held_value'] and y['model']=='CROSS_HOST_POSITION_TRANSFER'),0):.12f}" if x['model']=='CROSS_HOST_POSITION_TRANSFER' else 'NA'})
  for (kind,val),z in sorted(q['detail'].items()):detailrows.append({'control_id':p,'breakdown':kind,'value':val,'scored_events':z[0],'gain_bits':f'{z[1]:.12f}','gain_bits_per_event':f'{z[2]:.12f}'})
  for w,v in enumerate(ng):nullrows.append({'control_id':p,'world_index':w,'transfer_gain_bits_per_event':f'{v:.12f}'})
  for split,z in sens:
   gain=(z['bits']['OTHER_POSITION_HOST_BAG']-z['bits']['CROSS_HOST_POSITION_TRANSFER'])/z['n']
   for m in MODELS:sensrows.append({'split':'HELD_'+split.upper(),'model':m,'scored_events':z['n'],'bits':f"{z['bits'][m]:.12f}",'bits_per_event':f"{z['bits'][m]/z['n']:.12f}",'top1':z['top'][m],'transfer_gain_bits_per_event':f'{gain:.12f}'})
 means={p:statistics.mean(nulls[p]) for p in d['panels']};sds={p:statistics.pstdev(nulls[p]) for p in d['panels']};assert all(sds[p]>0 for p in d['maxT_panels']) and all(sds[p]==0 for p in d['zero_null_variance_panels']);zs={p:(obs[p]-means[p])/sds[p] for p in d['maxT_panels']};worldmax=[max((nulls[p][i]-means[p])/sds[p] for p in d['maxT_panels']) for i in range(64)];summary=[]
 for p in d['panels']:
  q=rr[p][1];local=(1+sum(x>=obs[p]-1e-15 for x in nulls[p]))/65;variable=p in d['maxT_panels'];maxp=(1+sum(x>=zs[p]-1e-15 for x in worldmax))/65 if variable else None;summary.append({'control_id':p,'scored_events':q['n'],'folios':len({x['physical_folio'] for x in panels[p]}),'transfer_gain_bits_per_event':f'{obs[p]:.12f}','null_mean':f'{means[p]:.12f}','null_sd':f'{sds[p]:.12f}','observed_z':f'{zs[p]:.12f}' if variable else 'NA_ZERO_NULL_VARIANCE','local_p':f'{local:.12f}','max4_p':f'{maxp:.12f}' if variable else 'NA_ZERO_NULL_VARIANCE','null_mobile_events_world0':mobile[p],'positive_host_buckets':sum(z[1]>0 for k,z in q['detail'].items() if k[0]=='BUCKET'),'positive_positions':sum(z[1]>0 for k,z in q['detail'].items() if k[0]=='POSITION')})
 v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');sg={x['split']:float(x['transfer_gain_bits_per_event']) for x in sensrows if x['model']=='CROSS_HOST_POSITION_TRANSFER'};gates={'minimum_capacity':int(v['scored_events'])>=d['minimum_voynich_scored_events'],'primary_gain_positive':float(v['transfer_gain_bits_per_event'])>0,'at_least_six_positive_host_buckets':int(v['positive_host_buckets'])>=6,'at_least_three_positive_positions':int(v['positive_positions'])>=3,'max4_p_le_0_05':float(v['max4_p'])<=.05,'held_section_gain_positive':sg['HELD_SECTION']>0,'held_hand_gain_positive':sg['HELD_HAND']>0}
 if not gates['minimum_capacity']:status=d['decision']['capacity']
 elif all(gates.values()):status=d['decision']['support']
 else:status=d['decision']['fail']
 write(OUT_PANEL,panelrows);write(OUT_FOLD,foldrows);write(OUT_DETAIL,detailrows);write(OUT_NULL,nullrows);write(OUT_SENS,sensrows)
 counters=[{'counterexample':'TRANSFER_DOES_NOT_BEAT_OTHER_POSITION_BAG','evidence':f"Voynich gain {float(v['transfer_gain_bits_per_event']):+.6f} bits/event",'impact':'nonpositive gain requires host-specific-table status'}, {'counterexample':'GAIN_CONCENTRATED_IN_HOST_BUCKETS','evidence':f"positive buckets {v['positive_host_buckets']}/8",'impact':'fewer than six fails compact reuse'}, {'counterexample':'GAIN_CONCENTRATED_IN_POSITIONS','evidence':f"positive positions {v['positive_positions']}/4",'impact':'fewer than three fails general position transfer'}, {'counterexample':'NO_SECTION_OR_HAND_TRANSFER','evidence':f"held-section {sg['HELD_SECTION']:+.6f}; held-hand {sg['HELD_HAND']:+.6f}",'impact':'either nonpositive fails transfer'}, {'counterexample':'TARGET_CELL_LEAKAGE','evidence':'target host target-position counts are excluded by construction','impact':'none detected'}, {'counterexample':'F84_USED','evidence':'only f84-free native event inventory read','impact':'no f84 access'}];write(OUT_COUNTER,counters)
 report=['# GDT289 — cross-host wrapper-position transfer','',f'Status: **{status}**.','','## Result','', '| panel | scored | transfer gain (bits/event) | positive buckets | positive positions | local p | max8 p |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summary:
  mp=x['max4_p'] if x['max4_p'].startswith('NA') else f"{float(x['max4_p']):.4f}"
  report.append(f"| {x['control_id']} | {x['scored_events']} | {float(x['transfer_gain_bits_per_event']):+.4f} | {x['positive_host_buckets']}/8 | {x['positive_positions']}/4 | {float(x['local_p']):.4f} | {mp} |")
 report +=['',f"Voynich held-section gain is {sg['HELD_SECTION']:+.4f} bits/event and held-hand gain is {sg['HELD_HAND']:+.4f}. World 0 changes {v['null_mobile_events_world0']} held wrapper labels inside exact nuisance strata.",'','## Frozen gates','']+[f"- `{k}`: **{'PASS' if x else 'FAIL'}**" for k,x in gates.items()]+['','The target host is recognized only through occurrences on other folios and other positions. Its own target-position cell is never available, and the cross-position transition is learned from other immutable host buckets. The null permutes unseen wrapper outcomes only after both predictors are fixed.','','## Claim ceiling','','This can establish only a reusable opaque wrapper-position rule. It cannot identify morphology, a lexical class, a grammatical function, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_PANEL,OUT_FOLD,OUT_DETAIL,OUT_NULL,OUT_SENS,OUT_COUNTER,REPORT];inputs=['gdt289_design.json','gdt289_design_validation.json','gdt289_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt286_result.json','gdt288_result.json'];res={'schema':'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_RESULT_V1','status':status,'panels':8,'summary':summary,'voynich_summary':v,'voynich_sensitivity_gains':sg,'frozen_gates':gates,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich':v,'gates':gates},sort_keys=True))
if __name__=='__main__':main()

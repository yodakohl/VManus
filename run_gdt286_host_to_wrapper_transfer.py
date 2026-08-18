#!/usr/bin/env python3
"""Run frozen GDT286 host-to-wrapper transfer."""
from __future__ import annotations
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;DESIGN=R/'gdt286_design.json';METHOD=R/'GDT286_HOST_TO_WRAPPER_TRANSFER_METHOD.md';REPORT=R/'GDT286_HOST_TO_WRAPPER_TRANSFER_REPORT.md';RESULT=R/'gdt286_result.json'
OUT_PANEL=R/'gdt286_panel_scores.tsv';OUT_FOLD=R/'gdt286_folio_scores.tsv';OUT_NULL=R/'gdt286_null_results.tsv';OUT_SENS=R/'gdt286_voynich_transfer_sensitivities.tsv';OUT_COUNTER=R/'gdt286_counterexamples.tsv';MODELS=('SHAPE_CONTEXT','EXACT_HOST','EXACT_HOST_X_POSITION')
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
def basekey(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def nullids(events,panel,world):
 st=defaultdict(list)
 for i,r in enumerate(events):st[(r['physical_folio'],)+basekey(r)].append(i)
 rng=random.Random(int(hashlib.sha256(f'GDT286_WITHIN_FOLIO_SHAPE_HOST_ID|{panel}|{world}'.encode()).hexdigest()[:16],16));out=[r['page_host'] for r in events]
 for k in sorted(st):
  ids=st[k];v=[out[i] for i in ids];rng.shuffle(v)
  for i,x in zip(ids,v):out[i]=x
 return out
def score(events,split,hostids=None):
 prior=11.;hostids=hostids or [r['page_host'] for r in events];wr=sorted({r['wrapper'] for r in events});K=len(wr);folds=defaultdict(list)
 for i,r in enumerate(events):folds[r[split]].append(i)
 g=Counter();fg=defaultdict(Counter);gb=defaultdict(Counter);fb=defaultdict(lambda:defaultdict(Counter));gh=defaultdict(Counter);fh=defaultdict(lambda:defaultdict(Counter));gp=defaultdict(Counter);fp=defaultdict(lambda:defaultdict(Counter))
 for i,r in enumerate(events):
  f=r[split];w=r['wrapper'];b=basekey(r);h=hostids[i];p=(h,r['within_field_position']);g[w]+=1;fg[f][w]+=1;gb[b][w]+=1;fb[f][b][w]+=1;gh[h][w]+=1;fh[f][h][w]+=1;gp[p][w]+=1;fp[f][p][w]+=1
 bits=Counter();top=Counter();foldrows=[];covered=0
 def sub(a,x,w):return a[w]-x[w]
 for held,ids in sorted(folds.items()):
  page=defaultdict(Counter);fbits=Counter();ftop=Counter();fcov=0;ntrain=len(events)-len(ids)
  for i in ids:
   r=events[i];w0=r['wrapper'];b=basekey(r);h=hostids[i];p=(h,r['within_field_position']);past=page[r['page']]
   probs={m:{} for m in MODELS}
   for w in wr:
    p0=(sub(g,fg[held],w)+.5)/(ntrain+.5*K);pp=(past[w]+prior*p0)/(sum(past.values())+prior);nb=sum(gb[b].values())-sum(fb[held][b].values());pb=(sub(gb[b],fb[held][b],w)+prior*pp)/(nb+prior);nh=sum(gh[h].values())-sum(fh[held][h].values());ph=(sub(gh[h],fh[held][h],w)+prior*pb)/(nh+prior);np=sum(gp[p].values())-sum(fp[held][p].values());php=(sub(gp[p],fp[held][p],w)+prior*ph)/(np+prior);probs['SHAPE_CONTEXT'][w]=pb;probs['EXACT_HOST'][w]=ph;probs['EXACT_HOST_X_POSITION'][w]=php
   nh=sum(gh[h].values())-sum(fh[held][h].values());fcov+=int(nh>0)
   for m in MODELS:
    v=-math.log2(probs[m][w0]);bits[m]+=v;fbits[m]+=v;pred=max(wr,key=lambda w:(probs[m][w],-wr.index(w)));ok=int(pred==w0);top[m]+=ok;ftop[m]+=ok
   past[w0]+=1
  covered+=fcov
  for m in MODELS:foldrows.append({'split':split,'held_value':held,'model':m,'events':len(ids),'covered_exact_host_events':fcov,'bits':fbits[m],'top1':ftop[m]})
 return {'bits':dict(bits),'top1':dict(top),'covered':covered,'events':len(events),'foldrows':foldrows}
def job(item):
 panel,events=item;obs=score(events,'physical_folio');null=[]
 for w in range(64):q=score(events,'physical_folio',nullids(events,panel,w));null.append((obs['bits']['SHAPE_CONTEXT']-q['bits']['EXACT_HOST'])/len(events))
 sens=[]
 if panel=='VOYNICH_REFERENCE':
  for split in ('section','hand'):sens.append((split,score(events,split)))
 return panel,obs,null,sens,sum(nullids(events,panel,0)[i]!=events[i]['page_host'] for i in range(len(events)))
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_GDT286_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt286_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(x)==8448 for x in panels.values())
 results={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,x):x[0] for x in panels.items()}
  for f in as_completed(fs):q=f.result();results[q[0]]=q;print(json.dumps({'scored':q[0]},sort_keys=True),flush=True)
 panelrows=[];foldrows=[];nullrows=[];sensrows=[];obs={};ng={};mobile={}
 for panel in d['panels']:
  _,q,n,s,mob=results[panel];mobile[panel]=mob;ng[panel]=n;obs[panel]=(q['bits']['SHAPE_CONTEXT']-q['bits']['EXACT_HOST'])/8448
  for m in MODELS:panelrows.append({'control_id':panel,'split':'HELD_PHYSICAL_FOLIO','model':m,'events':8448,'wrapper_classes':len({x['wrapper'] for x in panels[panel]}),'covered_exact_host_events':q['covered'],'bits':f"{q['bits'][m]:.12f}",'bits_per_event':f"{q['bits'][m]/8448:.12f}",'top1':q['top1'][m],'top1_rate':f"{q['top1'][m]/8448:.12f}"})
  for x in q['foldrows']:foldrows.append({'control_id':panel,**x,'bits':f"{x['bits']:.12f}"})
  for w,v in enumerate(n):nullrows.append({'control_id':panel,'world_index':w,'exact_host_gain_bits_per_event':f'{v:.12f}'})
  for split,z in s:
   for m in MODELS[:2]:sensrows.append({'control_id':panel,'split':'HELD_'+split.upper(),'model':m,'events':8448,'folds':len({x[split] for x in panels[panel]}),'covered_exact_host_events':z['covered'],'bits':f"{z['bits'][m]:.12f}",'bits_per_event':f"{z['bits'][m]/8448:.12f}",'top1':z['top1'][m],'top1_rate':f"{z['top1'][m]/8448:.12f}"})
 means={p:statistics.mean(ng[p]) for p in d['panels']};sds={p:statistics.pstdev(ng[p]) for p in d['panels']};assert all(sds[p]>0 for p in d['panels']);oz={p:(obs[p]-means[p])/sds[p] for p in d['panels']};wm=[max((ng[p][i]-means[p])/sds[p] for p in d['panels']) for i in range(64)]
 summary=[]
 for panel in d['panels']:
  q=results[panel][1];hg=obs[panel];pi=(q['bits']['EXACT_HOST']-q['bits']['EXACT_HOST_X_POSITION'])/8448;local=(1+sum(x>=hg-1e-15 for x in ng[panel]))/65;mp=(1+sum(x>=oz[panel]-1e-15 for x in wm))/65;summary.append({'control_id':panel,'events':8448,'folios':len({x['physical_folio'] for x in panels[panel]}),'wrapper_classes':len({x['wrapper'] for x in panels[panel]}),'null_mobile_events_world0':mobile[panel],'null_mobile_rate_world0':f'{mobile[panel]/8448:.12f}','exact_host_coverage':q['covered'],'exact_host_coverage_rate':f"{q['covered']/8448:.12f}",'exact_host_gain_bits_per_event':f'{hg:.12f}','host_gain_above_null_mean_bits_per_event':f'{hg-means[panel]:.12f}','host_position_increment_bits_per_event':f'{pi:.12f}','shape_top1_rate':f"{q['top1']['SHAPE_CONTEXT']/8448:.12f}",'host_top1_rate':f"{q['top1']['EXACT_HOST']/8448:.12f}",'host_position_top1_rate':f"{q['top1']['EXACT_HOST_X_POSITION']/8448:.12f}",'null_mean':f'{means[panel]:.12f}','null_sd':f'{sds[panel]:.12f}','observed_z':f'{oz[panel]:.12f}','local_p':f'{local:.12f}','max8_p':f'{mp:.12f}'})
 v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');sec={x['model']:x for x in sensrows if x['split']=='HELD_SECTION'};hand={x['model']:x for x in sensrows if x['split']=='HELD_HAND'};sg=(float(sec['SHAPE_CONTEXT']['bits'])-float(sec['EXACT_HOST']['bits']))/8448;hg=(float(hand['SHAPE_CONTEXT']['bits'])-float(hand['EXACT_HOST']['bits']))/8448;hostpass=float(v['exact_host_gain_bits_per_event'])>0 and float(v['max8_p'])<=d['decision']['alpha'];pos=float(v['host_position_increment_bits_per_event']);transfer=sg>0 or hg>0
 if hostpass and pos<=0 and transfer:status=d['decision']['stable']
 elif hostpass and pos>0:status=d['decision']['contextual']
 else:status=d['decision']['fail']
 gates={'held_folio_exact_host_gain_positive':float(v['exact_host_gain_bits_per_event'])>0,'max8_p_le_0_05':float(v['max8_p'])<=.05,'host_position_increment_nonpositive':pos<=0,'held_section_or_hand_gain_positive':transfer};write(OUT_PANEL,panelrows);write(OUT_FOLD,foldrows);write(OUT_NULL,nullrows);write(OUT_SENS,sensrows)
 counters=[{'counterexample':'HOST_IDENTITY_ADDS_NO_HELD_FOLIO_INFORMATION','evidence':f"Voynich gain {float(v['exact_host_gain_bits_per_event']):+.6f} bits/event max8 p {v['max8_p']}",'impact':'a nonpositive or null-compatible gain fails transfer'}, {'counterexample':'STRICT_NULL_DESTROYS_MOST_HOST_ALIGNMENT','evidence':f"world0 changes {v['null_mobile_events_world0']}/8448 IDs; observed-minus-null-mean {float(v['host_gain_above_null_mean_bits_per_event']):+.6f} bits/event",'impact':'p-value calibrates a low-mobility perturbation and raw host gain is not wholly identity-specific'}, {'counterexample':'WRAPPER_IS_POSITION_CONDITIONED_WITHIN_HOST','evidence':f"host×position increment {pos:+.6f} bits/event",'impact':'positive increment selects the contextual status'}, {'counterexample':'HOST_ASSOCIATION_IS_REGISTER_LOCKED','evidence':f'held-section gain {sg:+.6f}; held-hand gain {hg:+.6f}','impact':'both nonpositive fail the stable transfer gate'}, {'counterexample':'HOST_IS_A_LEXEME','evidence':'exact identity is opaque frozen parser output','impact':'wrapper predictability supplies no lexical or semantic interpretation'}, {'counterexample':'F84_USED','evidence':'only f84-free native inventory read','impact':'no f84 access'}];write(OUT_COUNTER,counters)
 report=['# GDT286 — opaque host-to-wrapper transfer','',f'Status: **{status}**.','','## Held-folio scores','', '| panel | coverage | host gain | above null | host×position | null mobile | max8 p |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summary:report.append(f"| {x['control_id']} | {float(x['exact_host_coverage_rate']):.3f} | {float(x['exact_host_gain_bits_per_event']):+.4f} | {float(x['host_gain_above_null_mean_bits_per_event']):+.4f} | {float(x['host_position_increment_bits_per_event']):+.4f} | {int(x['null_mobile_events_world0'])}/8448 | {float(x['max8_p']):.4f} |")
 report +=['','Voynich held-section exact-host gain: '+f'{sg:+.4f}'+' bits/event; held-hand gain: '+f'{hg:+.4f}'+'. The exact null changes only '+str(v['null_mobile_events_world0'])+'/8448 Voynich IDs in world 0; the observed host gain exceeds the high null mean by '+f"{float(v['host_gain_above_null_mean_bits_per_event']):+.4f}"+' bits/event. This is a low-mobility identity-alignment calibration.','','## Frozen gates','']+[f"- `{k}`: **{'PASS' if x else 'FAIL'}**" for k,x in gates.items()]+['','## Claim ceiling','','This distinguishes an opaque host-class association from a position-conditioned association only. It establishes no lexical class, morphology, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_PANEL,OUT_FOLD,OUT_NULL,OUT_SENS,OUT_COUNTER,REPORT];inputs=['gdt286_design.json','gdt286_design_validation.json','gdt286_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt285_result.json'];res={'schema':'GDT286_HOST_TO_WRAPPER_TRANSFER_RESULT_V1','status':status,'panels':8,'events_per_panel':8448,'frozen_gates':gates,'voynich_summary':v,'voynich_held_section_gain_bits_per_event':sg,'voynich_held_hand_gain_bits_per_event':hg,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'gates':gates},sort_keys=True))
if __name__=='__main__':main()

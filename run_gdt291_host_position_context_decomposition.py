#!/usr/bin/env python3
"""Run frozen GDT291 host-position context decomposition."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parent;DESIGN=R/'gdt291_design.json';METHOD=R/'GDT291_HOST_POSITION_CONTEXT_DECOMPOSITION_METHOD.md';REPORT=R/'GDT291_HOST_POSITION_CONTEXT_DECOMPOSITION_REPORT.md';RESULT=R/'gdt291_result.json';OUT_PANEL=R/'gdt291_panel_scores.tsv';OUT_FOLD=R/'gdt291_folio_scores.tsv';OUT_INC=R/'gdt291_nested_increments.tsv';OUT_SENS=R/'gdt291_voynich_sensitivities.tsv';OUT_COUNTER=R/'gdt291_counterexamples.tsv'
MODELS=('SHAPE_CONTEXT','RECORD_CONTEXT','NONWRAPPER_COMPILER','EXACT_HOST_RICH','EXACT_HOST_X_POSITION_RICH','EXACT_HOST_SHAPE','EXACT_HOST_X_POSITION_SHAPE');ALPHA=.5
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
def ob(x):
 n=int(x);return '1' if n==1 else '2' if n==2 else '3_4' if n<=4 else '5_PLUS'
def lp(r):
 i=int(r['group_index']);n=int(r['group_count']);return 'ONLY' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def sk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def rk(r):return sk(r)+(ob(r['record_ordinal']),ob(r['field_ordinal']),lp(r),r['line_close'],r['paragraph_close'],r['known_label_renderer'])
def ck(r):return rk(r)+(r['local_frame'],r['inner_d'],r['right_family'],r['dy_closure'],r['b3'])
def score(events,split='physical_folio',prior=11.):
 wr=sorted({r['wrapper'] for r in events});K=len(wr);folds=defaultdict(list)
 for i,r in enumerate(events):folds[r[split]].append(i)
 totals=Counter();tops=Counter();foldrows=[]
 for held,tests in sorted(folds.items()):
  train=[i for i,r in enumerate(events) if r[split]!=held];g=Counter();cs=defaultdict(Counter);cr=defaultdict(Counter);cc=defaultdict(Counter);ch=defaultdict(Counter);chp=defaultdict(Counter)
  for i in train:
   r=events[i];w=r['wrapper'];h=r['page_host'];p=(h,r['within_field_position']);g[w]+=1;cs[sk(r)][w]+=1;cr[rk(r)][w]+=1;cc[ck(r)][w]+=1;ch[h][w]+=1;chp[p][w]+=1
  fb=Counter();ft=Counter()
  for i in tests:
   r=events[i];actual=r['wrapper'];h=r['page_host'];hp=(h,r['within_field_position']);probs={m:{} for m in MODELS}
   for w in wr:
    p0=(g[w]+ALPHA)/(len(train)+ALPHA*K);a=cs[sk(r)];ps=(a[w]+prior*p0)/(sum(a.values())+prior);a=cr[rk(r)];pr=(a[w]+prior*ps)/(sum(a.values())+prior);a=cc[ck(r)];pc=(a[w]+prior*pr)/(sum(a.values())+prior);a=ch[h];phr=(a[w]+prior*pc)/(sum(a.values())+prior);a=chp[hp];phpr=(a[w]+prior*phr)/(sum(a.values())+prior);a=ch[h];phs=(a[w]+prior*ps)/(sum(a.values())+prior);a=chp[hp];phps=(a[w]+prior*phs)/(sum(a.values())+prior);vals=(ps,pr,pc,phr,phpr,phs,phps)
    for m,v in zip(MODELS,vals):probs[m][w]=v
   for m in MODELS:
    z=-math.log2(probs[m][actual]);totals[m]+=z;fb[m]+=z;ok=int(max(wr,key=lambda w:(probs[m][w],-wr.index(w)))==actual);tops[m]+=ok;ft[m]+=ok
  for m in MODELS:foldrows.append({'split':'HELD_'+split.upper(),'held_value':held,'prior_mass':prior,'model':m,'events':len(tests),'bits':fb[m],'top1':ft[m]})
 return {'bits':dict(totals),'top':dict(tops),'foldrows':foldrows,'events':len(events)}
def increments(q):
 b=q['bits'];n=q['events'];return {'RECORD_GIVEN_SHAPE':(b['SHAPE_CONTEXT']-b['RECORD_CONTEXT'])/n,'COMPILER_GIVEN_RECORD':(b['RECORD_CONTEXT']-b['NONWRAPPER_COMPILER'])/n,'HOST_GIVEN_RICH_CONTEXT':(b['NONWRAPPER_COMPILER']-b['EXACT_HOST_RICH'])/n,'HOST_POSITION_GIVEN_RICH_CONTEXT':(b['EXACT_HOST_RICH']-b['EXACT_HOST_X_POSITION_RICH'])/n,'HOST_GIVEN_SHAPE':(b['SHAPE_CONTEXT']-b['EXACT_HOST_SHAPE'])/n,'HOST_POSITION_GIVEN_SHAPE':(b['EXACT_HOST_SHAPE']-b['EXACT_HOST_X_POSITION_SHAPE'])/n}
def job(item):p,e=item;return p,score(e)
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_GDT291_SCORING' and d['content_sha256']==rcsha(d)
 for x in read(R/'gdt291_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};assert all(len(x)==8448 for x in panels.values());rr={}
 with ProcessPoolExecutor(max_workers=4) as ex:
  fs={ex.submit(job,x):x[0] for x in panels.items()}
  for f in as_completed(fs):z=f.result();rr[z[0]]=z[1];print(json.dumps({'panel':z[0]},sort_keys=True),flush=True)
 panelrows=[];foldrows=[];incrows=[];summary=[]
 for p in d['panels']:
  q=rr[p];inc=increments(q)
  for m in MODELS:panelrows.append({'control_id':p,'split':'HELD_PHYSICAL_FOLIO','prior_mass':11,'model':m,'events':8448,'bits':f"{q['bits'][m]:.12f}",'bits_per_event':f"{q['bits'][m]/8448:.12f}",'top1':q['top'][m],'top1_rate':f"{q['top'][m]/8448:.12f}"})
  for x in q['foldrows']:foldrows.append({'control_id':p,**x,'bits':f"{x['bits']:.12f}"})
  for name,v in inc.items():incrows.append({'control_id':p,'split':'HELD_PHYSICAL_FOLIO','prior_mass':11,'increment':name,'gain_bits_per_event':f'{v:.12f}'})
  summary.append({'control_id':p,**{k:float(f'{v:.12f}') for k,v in inc.items()}})
 sens=[]
 for prior in d['voynich_prior_sensitivities']:
  q=score(panels['VOYNICH_REFERENCE'],prior=prior);z=increments(q);sens.append({'split':'HELD_PHYSICAL_FOLIO','prior_mass':prior,**z})
 for split in ('section','hand'):
  q=score(panels['VOYNICH_REFERENCE'],split,11);z=increments(q);sens.append({'split':'HELD_'+split.upper(),'prior_mass':11,**z})
 sensrows=[]
 for x in sens:
  for name in increments(rr['VOYNICH_REFERENCE']):sensrows.append({'split':x['split'],'prior_mass':x['prior_mass'],'increment':name,'gain_bits_per_event':f"{x[name]:.12f}"})
 write(OUT_PANEL,panelrows);write(OUT_FOLD,foldrows);write(OUT_INC,incrows);write(OUT_SENS,sensrows);v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');A=v['HOST_POSITION_GIVEN_SHAPE'];Rich=v['HOST_POSITION_GIVEN_RICH_CONTEXT']
 if A>0 and Rich<=0:status=d['decision']['reversed']
 elif A>0 and Rich<A:status=d['decision']['reduced']
 elif A>0 and Rich>=A:status=d['decision']['persists']
 else:status=d['decision']['no_anchor']
 counters=[{'counterexample':'NO_TARGET_HISTORY_FREE_ANCHOR','evidence':f'shape-anchor host×position {A:+.6f} bits/event','impact':'nonpositive anchor prevents attribution to richer context'}, {'counterexample':'RICH_CONTEXT_DOES_NOT_REDUCE_INCREMENT','evidence':f'rich host×position {Rich:+.6f} versus anchor {A:+.6f}','impact':'equal or larger increment supports residual exact-host cells'}, {'counterexample':'RESULT_DEPENDS_ON_PRIOR','evidence':'; '.join(f"prior {x['prior_mass']}: {x['HOST_POSITION_GIVEN_RICH_CONTEXT']:+.6f}" for x in sens if x['split']=='HELD_PHYSICAL_FOLIO'),'impact':'sign changes weaken localization'}, {'counterexample':'RESULT_DEPENDS_ON_REGISTER_SPLIT','evidence':'; '.join(f"{x['split']}: {x['HOST_POSITION_GIVEN_RICH_CONTEXT']:+.6f}" for x in sens if x['prior_mass']==11 and x['split']!='HELD_PHYSICAL_FOLIO'),'impact':'negative transfer weakens universality'}, {'counterexample':'WHOLE_REGISTER_CONTEXT_BACKOFF','evidence':'held-section and held-hand record/compiler increments are exactly zero because those identifiers occur in the context keys','impact':'sensitivities test only residual host layers, not transfer of the rich context itself'}, {'counterexample':'F84_USED','evidence':'only f84-free native inventory read','impact':'no f84 access'}];write(OUT_COUNTER,counters)
 report=['# GDT291 — host-position omitted-context decomposition','',f'Status: **{status}**.','','## Held-folio nested increments','', '| panel | record | nonwrapper compiler | exact host rich | host×position rich | exact host shape | host×position shape |','|---|---:|---:|---:|---:|---:|---:|']
 for x in summary:report.append(f"| {x['control_id']} | {x['RECORD_GIVEN_SHAPE']:+.4f} | {x['COMPILER_GIVEN_RECORD']:+.4f} | {x['HOST_GIVEN_RICH_CONTEXT']:+.4f} | {x['HOST_POSITION_GIVEN_RICH_CONTEXT']:+.4f} | {x['HOST_GIVEN_SHAPE']:+.4f} | {x['HOST_POSITION_GIVEN_SHAPE']:+.4f} |")
 report +=['','The target-history-free Voynich shape anchor is '+f'{A:+.4f}'+' bits/event; after record and all frozen non-wrapper compiler coordinates the residual host×position increment is '+f'{Rich:+.4f}'+'.','','## Voynich sensitivities','']+[f"- {x['split']} prior={x['prior_mass']}: rich host×position {x['HOST_POSITION_GIVEN_RICH_CONTEXT']:+.4f}; shape anchor {x['HOST_POSITION_GIVEN_SHAPE']:+.4f}." for x in sens]+['','In the whole-section and whole-hand splits, the richer record/compiler keys contain the held identifier and therefore have no exact training support; their increments are exactly zero by hierarchical backoff. Those sensitivities test the residual host layers only and are not evidence that record/compiler context is neutral across registers.','','## Claim ceiling','','This localizes a formal wrapper interaction only. It cannot establish lexical class, morphology, grammar function, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[OUT_PANEL,OUT_FOLD,OUT_INC,OUT_SENS,OUT_COUNTER,REPORT];inputs=['gdt291_design.json','gdt291_design_validation.json','gdt291_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt290_result.json','gdt289_result.json','gdt286_result.json'];res={'schema':'GDT291_HOST_POSITION_CONTEXT_DECOMPOSITION_RESULT_V1','status':status,'summary':summary,'voynich_summary':v,'voynich_sensitivities':sens,'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'voynich':v,'sensitivities':sens},sort_keys=True))
if __name__=='__main__':main()

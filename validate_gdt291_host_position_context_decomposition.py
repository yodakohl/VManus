#!/usr/bin/env python3
"""Independent reconstruction for GDT291."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt291_result.json';OUT=R/'gdt291_validation.json';MODELS=('SHAPE_CONTEXT','RECORD_CONTEXT','NONWRAPPER_COMPILER','EXACT_HOST_RICH','EXACT_HOST_X_POSITION_RICH','EXACT_HOST_SHAPE','EXACT_HOST_X_POSITION_SHAPE');ALPHA=.5
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=2e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def ob(x):
 n=int(x);return '1' if n==1 else '2' if n==2 else '3_4' if n<=4 else '5_PLUS'
def lp(r):
 i=int(r['group_index']);n=int(r['group_count']);return 'ONLY' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def sk(r):return (r['section'],r['currier'],r['hand'],r['register'],r['within_field_position'],int(r['host_length']),r['page_host'][:1],r['page_host'][-1:])
def rk(r):return sk(r)+(ob(r['record_ordinal']),ob(r['field_ordinal']),lp(r),r['line_close'],r['paragraph_close'],r['known_label_renderer'])
def ck(r):return rk(r)+(r['local_frame'],r['inner_d'],r['right_family'],r['dy_closure'],r['b3'])
def score(ev,split='physical_folio',prior=11.):
 wr=sorted({r['wrapper'] for r in ev});K=len(wr);folds=defaultdict(list)
 for i,r in enumerate(ev):folds[r[split]].append(i)
 bits=Counter();top=Counter();ff=[]
 for held,tests in sorted(folds.items()):
  train=[i for i,r in enumerate(ev) if r[split]!=held];g=Counter();a=defaultdict(Counter);b=defaultdict(Counter);c=defaultdict(Counter);h=defaultdict(Counter);hp=defaultdict(Counter)
  for i in train:r=ev[i];w=r['wrapper'];g[w]+=1;a[sk(r)][w]+=1;b[rk(r)][w]+=1;c[ck(r)][w]+=1;h[r['page_host']][w]+=1;hp[r['page_host'],r['within_field_position']][w]+=1
  fb=Counter();ft=Counter()
  for i in tests:
   r=ev[i];actual=r['wrapper'];probs={m:{} for m in MODELS}
   for w in wr:
    p0=(g[w]+ALPHA)/(len(train)+ALPHA*K);x=a[sk(r)];ps=(x[w]+prior*p0)/(sum(x.values())+prior);x=b[rk(r)];pr=(x[w]+prior*ps)/(sum(x.values())+prior);x=c[ck(r)];pc=(x[w]+prior*pr)/(sum(x.values())+prior);x=h[r['page_host']];phr=(x[w]+prior*pc)/(sum(x.values())+prior);x=hp[r['page_host'],r['within_field_position']];phpr=(x[w]+prior*phr)/(sum(x.values())+prior);x=h[r['page_host']];phs=(x[w]+prior*ps)/(sum(x.values())+prior);x=hp[r['page_host'],r['within_field_position']];phps=(x[w]+prior*phs)/(sum(x.values())+prior)
    for m,v in zip(MODELS,(ps,pr,pc,phr,phpr,phs,phps)):probs[m][w]=v
   for m in MODELS:z=-math.log2(probs[m][actual]);bits[m]+=z;fb[m]+=z;ok=int(max(wr,key=lambda w:(probs[m][w],-wr.index(w)))==actual);top[m]+=ok;ft[m]+=ok
  for m in MODELS:ff.append((held,m,len(tests),fb[m],ft[m]))
 return dict(bits),dict(top),ff
def inc(bits,n):return {'RECORD_GIVEN_SHAPE':(bits['SHAPE_CONTEXT']-bits['RECORD_CONTEXT'])/n,'COMPILER_GIVEN_RECORD':(bits['RECORD_CONTEXT']-bits['NONWRAPPER_COMPILER'])/n,'HOST_GIVEN_RICH_CONTEXT':(bits['NONWRAPPER_COMPILER']-bits['EXACT_HOST_RICH'])/n,'HOST_POSITION_GIVEN_RICH_CONTEXT':(bits['EXACT_HOST_RICH']-bits['EXACT_HOST_X_POSITION_RICH'])/n,'HOST_GIVEN_SHAPE':(bits['SHAPE_CONTEXT']-bits['EXACT_HOST_SHAPE'])/n,'HOST_POSITION_GIVEN_SHAPE':(bits['EXACT_HOST_SHAPE']-bits['EXACT_HOST_X_POSITION_SHAPE'])/n}
def main():
 cc=[]
 def check(n,v):cc.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt291_design.json').read_text());res=json.loads(RESULT.read_text());pr=rows(R/'gdt291_panel_scores.tsv');fr=rows(R/'gdt291_folio_scores.tsv');ir=rows(R/'gdt291_nested_increments.tsv');sr=rows(R/'gdt291_voynich_sensitivities.tsv');check('design',d['content_sha256']==csha(d) and d['status']=='FROZEN_BEFORE_GDT291_SCORING');mf=rows(R/'gdt291_freeze_manifest.tsv');check('freeze',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));check('counts',len(pr)==56 and len(ir)==48 and len(sr)==24 and len(fr)>0);native=rows(R/'gdt278_native_event_inventory.tsv');check('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));panels={p:[x for x in native if x['control_id']==p] for p in d['panels']};check('events',all(len(x)==8448 for x in panels.values()))
 for p in d['panels']:
  q=[x for x in pr if x['control_id']==p];f=[x for x in fr if x['control_id']==p];check('panel:'+p,len(q)==7 and all(int(x['events'])==8448 and close(x['bits_per_event'],float(x['bits'])/8448) and close(x['top1_rate'],int(x['top1'])/8448) for x in q));check('folds:'+p,all(close(next(x for x in q if x['model']==m)['bits'],sum(float(x['bits']) for x in f if x['model']==m)) and int(next(x for x in q if x['model']==m)['top1'])==sum(int(x['top1']) for x in f if x['model']==m) for m in MODELS));b={x['model']:float(x['bits']) for x in q};z=inc(b,8448);check('increments:'+p,all(close(next(x for x in ir if x['control_id']==p and x['increment']==k)['gain_bits_per_event'],v) for k,v in z.items()))
 ev=panels['VOYNICH_REFERENCE'];bits,top,folds=score(ev);z=inc(bits,8448);check('voynich_summary',all(close(res['voynich_summary'][k],v) for k,v in z.items()))
 for m in MODELS:
  x=next(r for r in pr if r['control_id']=='VOYNICH_REFERENCE' and r['model']==m);check('voynich_model:'+m,close(x['bits'],bits[m]) and int(x['top1'])==top[m])
 for held,m,n,b,t in folds:
  x=next(r for r in fr if r['control_id']=='VOYNICH_REFERENCE' and r['held_value']==held and r['model']==m);check('voynich_fold:'+held+':'+m,int(x['events'])==n and close(x['bits'],b) and int(x['top1'])==t)
 for prior in (5.,22.):
  b,t,f=score(ev,prior=prior);z=inc(b,8448);x=next(x for x in res['voynich_sensitivities'] if x['split']=='HELD_PHYSICAL_FOLIO' and float(x['prior_mass'])==prior);check('prior:'+str(prior),all(close(x[k],v) for k,v in z.items()))
 for split in ('section','hand'):
  b,t,f=score(ev,split,11);z=inc(b,8448);x=next(x for x in res['voynich_sensitivities'] if x['split']=='HELD_'+split.upper());check('split:'+split,all(close(x[k],v) for k,v in z.items()))
 A=z0=res['voynich_summary']['HOST_POSITION_GIVEN_SHAPE'];Rich=res['voynich_summary']['HOST_POSITION_GIVEN_RICH_CONTEXT'];status=d['decision']['reversed'] if A>0 and Rich<=0 else d['decision']['reduced'] if A>0 and 0<Rich<A else d['decision']['persists'] if A>0 and Rich>=A else d['decision']['no_anchor'];check('decision',res['status']==status);check('prohibitions',res['new_corpora']==res['new_architectures']==res['semantic_assignments']==res['page_host_substrings_mined']==0);check('hashes',res['content_sha256']==csha(res) and all(sha(R/k)==v for k,v in res['inputs'].items()) and all(sha(R/k)==v for k,v in res['documents'].items()) and all(sha(R/k)==v for k,v in res['implementation'].items()) and all(sha(R/k)==v for k,v in res['outputs'].items()));check('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));out={'schema':'GDT291_HOST_POSITION_CONTEXT_DECOMPOSITION_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_VOYNICH_ALL_FOLDS_PRIORS_SECTION_HAND_PLUS_ALL_PANEL_ACCOUNTING_HASHES_AND_DECISION','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()

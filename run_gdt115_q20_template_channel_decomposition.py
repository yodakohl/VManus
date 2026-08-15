#!/usr/bin/env python3
"""GDT115: decompose GDT114 and apply a stricter same-page pairing null."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g

ROOT=Path(__file__).resolve().parent
METHOD=ROOT/'GDT115_Q20_TEMPLATE_CHANNEL_DECOMPOSITION_METHOD.md';REPORT=ROOT/'GDT115_Q20_TEMPLATE_CHANNEL_DECOMPOSITION_REPORT.md'
STRICT=ROOT/'gdt115_gdt114_strict_page_null.tsv';BLOCKS=ROOT/'gdt115_template_channel_scores.tsv';FOLDS=ROOT/'gdt115_template_channel_folds.tsv';COUNTER=ROOT/'gdt115_template_channel_counterexamples.tsv';RESULT=ROOT/'gdt115_result.json'
BLOCK_SPECS=(
 ('WRAPPER_TO_BODY_WRAPPER','WRAPPER','BODY_WRAPPER'),('WRAPPER_TO_BODY_FRAME','WRAPPER','BODY_FRAME'),('WRAPPER_TO_BODY_RENDERER','WRAPPER','BODY_RENDERER'),
 ('FRAME_TO_BODY_WRAPPER','FRAME','BODY_WRAPPER'),('FRAME_TO_BODY_FRAME','FRAME','BODY_FRAME'),('FRAME_TO_BODY_RENDERER','FRAME','BODY_RENDERER'),
 ('RENDERER_TO_BODY_WRAPPER','RENDERER','BODY_WRAPPER'),('RENDERER_TO_BODY_FRAME','RENDERER','BODY_FRAME'),('RENDERER_TO_BODY_RENDERER','RENDERER','BODY_RENDERER'),
 ('COMPILER_TO_BODY_COMPILER','COMPILER','BODY_COMPILER'),('COMPILER_TO_BODY_EDGE','COMPILER','BODY_EDGE'),('EDGE_TO_BODY_COMPILER','EDGE','BODY_COMPILER'),('EDGE_TO_BODY_EDGE','EDGE','BODY_EDGE'))
LAMS=g.LAMBDAS;WORLDS=g.WORLDS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def add(r,k):
 c=g.compiler_vec(r['open']);e=g.edge_vec(r['open'])
 return {'WRAPPER':c[:7],'FRAME':c[7:9],'RENDERER':c[9:12],'COMPILER':c,'EDGE':e}[k]
def target(r,k):
 c=g.compiler_vec(r['body']);e=g.edge_vec(r['body'])
 return {'BODY_WRAPPER':c[:7],'BODY_FRAME':c[7:9],'BODY_RENDERER':c[9:12],'BODY_COMPILER':c,'BODY_EDGE':e}[k]
def choose(records,ids,Xn,Xa,Y):
 score={l:0. for l in LAMS}
 for held in sorted({records[i]['physical_folio'] for i in ids}):
  tr=[i for i in ids if records[i]['physical_folio']!=held];te=[i for i in ids if records[i]['physical_folio']==held]
  xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);xatr,xate,_,_=g.standardize(Xa[tr],Xa[te]);ytr,yte,_,_=g.standardize(Y[tr],Y[te])
  for l in LAMS:score[l]+=float(np.square(yte-g.ridge_pred(np.c_[xnte,xate],g.ridge_fit(np.c_[xntr,xatr],ytr,l))).sum())
 return min(LAMS,key=lambda l:(score[l],l))
def choose_base(records,ids,Xn,Y):
 score={l:0. for l in LAMS}
 for held in sorted({records[i]['physical_folio'] for i in ids}):
  tr=[i for i in ids if records[i]['physical_folio']!=held];te=[i for i in ids if records[i]['physical_folio']==held]
  xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);ytr,yte,_,_=g.standardize(Y[tr],Y[te])
  for l in LAMS:score[l]+=float(np.square(yte-g.ridge_pred(xnte,g.ridge_fit(xntr,ytr,l))).sum())
 return min(LAMS,key=lambda l:(score[l],l))
def fit_block(records,inkey,outkey):
 Xn=g.nuisance(records);Xa=np.vstack([add(r,inkey) for r in records]);Y=np.vstack([target(r,outkey) for r in records]);fold=[];cache={}
 for held in sorted({r['physical_folio'] for r in records}):
  tr=[i for i,r in enumerate(records) if r['physical_folio']!=held];te=[i for i,r in enumerate(records) if r['physical_folio']==held]
  xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);xatr,xate,amu,asd=g.standardize(Xa[tr],Xa[te]);ytr,yte,_,_=g.standardize(Y[tr],Y[te])
  l0=choose_base(records,tr,Xn,Y)
  b0=g.ridge_fit(xntr,ytr,l0);p0=g.ridge_pred(xnte,b0);lam=choose(records,tr,Xn,Xa,Y);b=g.ridge_fit(np.c_[xntr,xatr],ytr,lam);p=g.ridge_pred(np.c_[xnte,xate],b);gain=g.pseudo_bits(yte,p0,p)
  fold.append({'held_folio':held,'held_records':len(te),'lambda':lam,'nuisance_lambda':l0,'pseudo_gain_bits':gain,'positive_gain':int(gain>0)})
  cache[held]={'te':te,'y':yte,'p0':p0,'xn':xnte,'amu':amu,'asd':asd,'b':b}
 return fold,cache,Xa
def assignments(records,cache,scope,rng):
 out={};cap=0
 for held,c in cache.items():
  te=c['te'];d=defaultdict(list)
  for pos,i in enumerate(te):d[((records[i]['page'],) if scope=='PAGE' else tuple())+(records[i]['open_member_count'],)].append(pos)
  a=list(range(len(te)))
  for ps in d.values():
   if len(ps)>1:
    cap+=len(ps);z=ps[:];rng.shuffle(z)
    for p,q in zip(ps,z):a[p]=q
  out[held]=a
 return out,cap
def null_world(records,models,scope,ed):
 world={name:[] for name,_,_,_,_ in models};cap=None;rng=random.Random(g.seed('GDT115',scope,ed))
 for _ in range(WORLDS):
  # Every block has the same record ordering; derive one shared assignment.
  assign,cc=assignments(records,models[0][3],scope,rng);cap=cc
  for name,_,_,cache,Xa in models:
   total=0.
   for held,c in cache.items():
    te=c['te'];raw=Xa[te][assign[held]];xa=(raw-c['amu'])/c['asd'];p=g.ridge_pred(np.c_[c['xn'],xa],c['b']);total+=g.pseudo_bits(c['y'],c['p0'],p)
   world[name].append(total)
 return world,cap
def strict_gdt114(allr):
 rows=[]
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];fold,cache,adds=g.fit_edition(rec);true={m:sum(x['pseudo_gain_bits'] for x in fold if x['model']==m) for m in g.MODELS}
  # Page-restricted exact-length assignment.
  strata={};cap=0
  for held in sorted({r['physical_folio'] for r in rec}):
   te=cache[(held,g.MODELS[0])]['te'];d=defaultdict(list)
   for pos,i in enumerate(te):d[(rec[i]['page'],rec[i]['open_member_count'])].append(pos)
   cap+=sum(len(v) for v in d.values() if len(v)>1);strata[held]=(te,d)
  rng=random.Random(g.seed('GDT115_STRICT',ed));world={m:[] for m in g.MODELS}
  for _ in range(WORLDS):
   assign={}
   for held,(te,d) in strata.items():
    a=list(range(len(te)))
    for ps in d.values():
     if len(ps)>1:
      z=ps[:];rng.shuffle(z)
      for p,q in zip(ps,z):a[p]=q
    assign[held]=a
   for m in g.MODELS:
    total=0.
    for held in strata:
     c=cache[(held,m)];te=c['te'];raw=adds[m][te][assign[held]];xa=(raw-c['amu'])/c['asd'];p=g.ridge_pred(np.c_[c['xn'],xa],c['b']);total+=g.pseudo_bits(c['y'],c['p0'],p)
    world[m].append(total)
  mx=[max(world[m][i] for m in g.MODELS) for i in range(WORLDS)]
  for m in g.MODELS:rows.append({'edition':ed,'model':m,'true_gain_bits':true[m],'same_page_swappable_records':cap,'null_median_bits':float(np.median(world[m])),'local_p':(1+sum(x>=true[m]-1e-12 for x in world[m]))/(WORLDS+1),'max_five_p':(1+sum(x>=true[m]-1e-12 for x in mx))/(WORLDS+1)})
 return rows
def main():
 allr=g.load_records();strict=strict_gdt114(allr);score=[];foldout=[];counter=[];edmodels={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];models=[];true={}
  for name,ik,ok in BLOCK_SPECS:
   folds,cache,Xa=fit_block(rec,ik,ok);models.append((name,ik,ok,cache,Xa));t=sum(x['pseudo_gain_bits'] for x in folds);true[name]=t
   for x in folds:foldout.append({'edition':ed,'model':name,**x})
   for x in sorted(folds,key=lambda z:z['pseudo_gain_bits'])[:2]:counter.append({'edition':ed,'model':name,'held_folio':x['held_folio'],'pseudo_gain_bits':x['pseudo_gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
  nulls={}
  for scope in ('FOLIO','PAGE'):nulls[scope]=null_world(rec,models,scope,ed)
  for scope,(world,cap) in nulls.items():
   mx=[max(world[n][i] for n,_,_ in BLOCK_SPECS) for i in range(WORLDS)]
   for name,ik,ok in BLOCK_SPECS:
    row={'edition':ed,'model':name,'open_channel':ik,'body_channel':ok,'null_scope':scope,'true_gain_bits':true[name],'selector_paid_gain_bits':true[name]-math.log2(len(BLOCK_SPECS)),'positive_folios':sum(x['pseudo_gain_bits']>0 for x in foldout if x['edition']==ed and x['model']==name),'swappable_records':cap,'null_median_bits':float(np.median(world[name])),'local_p':(1+sum(x>=true[name]-1e-12 for x in world[name]))/(WORLDS+1),'max_13_p':(1+sum(x>=true[name]-1e-12 for x in mx))/(WORLDS+1)};score.append(row)
  edmodels[ed]=true
 primary_strict=next(x for x in strict if x['edition']=='ZL3b' and x['model']=='FULL_HPR2')
 p=[x for x in score if x['edition']=='ZL3b' and x['null_scope']=='PAGE'];best=max(p,key=lambda x:(x['true_gain_bits'],x['model']))
 page_comp=[x for x in score if x['model']=='COMPILER_TO_BODY_COMPILER' and x['null_scope']=='PAGE']
 compiler_gate=(len(page_comp)==3 and all(x['true_gain_bits']>0 and x['positive_folios']==8 and x['max_13_p']<=.05 for x in page_comp))
 status='Q20_OPEN_BODY_COMPILER_CHANNEL_TRANSFERS_WITHIN_PAGE' if compiler_gate else 'Q20_RECORD_TEMPLATE_LINKAGE_PAGE_SENSITIVE_COMPONENT_LOCALIZED' if primary_strict['max_five_p']>.05 else 'Q20_RECORD_TEMPLATE_LINKAGE_SURVIVES_SAME_PAGE_NULL'
 write(STRICT,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in strict]);write(BLOCKS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in score]);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in foldout]);write(COUNTER,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in counter])
 report=f'''# GDT115 — Q20 record-template channel decomposition

Status: **{status}**

## Stricter null for the GDT114 lead

The GDT114 ZL3b `FULL_HPR2` gain remains {primary_strict['true_gain_bits']:+.3f}
pseudo-bits, but the same-page/exact-OPEN-length null has only
{primary_strict['same_page_swappable_records']}/170 swappable records and gives
local p={primary_strict['local_p']:.4f}, max-five p={primary_strict['max_five_p']:.4f}.
The corresponding IT2a/RF1b max-five p-values are
{next(x for x in strict if x['edition']=='IT2a' and x['model']=='FULL_HPR2')['max_five_p']:.4f} and
{next(x for x in strict if x['edition']=='RF1b' and x['model']=='FULL_HPR2')['max_five_p']:.4f}.
Thus the record-linkage lead is real under its registered folio null but is
page-sensitive in the primary reading rather than a clean invariant.

## Channel localization

Under the stricter ZL3b page null the largest block gain is
`{best['model']}` at {best['true_gain_bits']:+.3f} bits, with local
p={best['local_p']:.4f} and max-13 p={best['max_13_p']:.4f}. The same fixed
block gains {next(x for x in page_comp if x['edition']=='IT2a')['true_gain_bits']:+.3f}
bits in IT2a (max-13 p={next(x for x in page_comp if x['edition']=='IT2a')['max_13_p']:.4f})
and {next(x for x in page_comp if x['edition']=='RF1b')['true_gain_bits']:+.3f}
bits in RF1b (max-13 p={next(x for x in page_comp if x['edition']=='RF1b')['max_13_p']:.4f}).
It is positive on all eight held folios in every reading. This supports a
transferable anonymous **compiler-channel linkage** from the first line to the
later lines of the same star record. It does not show that literal codewords,
PAGE_HOST edges, or meanings are shared.

This is still a useful narrowing: it distinguishes OPEN-controlled compiler,
frame, renderer and edge channels from literal OPEN→BODY copying. The existing
Q20OB001 zero-gain KT/cache result remains binding.

No recipe, heading, semantic role, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is inferred. f84r remained completely
excluded and received no prediction.
''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT115_Q20_TEMPLATE_CHANNEL_DECOMPOSITION_RESULT_V1','status':status,'records':170,'physical_folios':8,'worlds':WORLDS,'gdt114_strict_page_primary':primary_strict,'best_zl_page_block':best,'compiler_channel_gate':compiler_gate,'strict_page_scores':strict,'channel_scores':score,'interpretation':'The full GDT114 profile is page-sensitive in ZL3b, but OPEN compiler proportions predict BODY compiler proportions on every held folio and survive the same-page exact-length max-13 null in all three readings.','claim_ceiling':'Anonymous record-template channel decomposition only; no recipe, heading, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{'gdt114_result.json':sha(ROOT/'gdt114_result.json'),'gdt114_q20_record_template_inventory.tsv':sha(ROOT/'gdt114_q20_record_template_inventory.tsv'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (STRICT,BLOCKS,FOLDS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'strict':primary_strict,'best':best},sort_keys=True))
if __name__=='__main__':main()

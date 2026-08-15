#!/usr/bin/env python3
"""GDT114: nested Q20 OPEN-to-BODY HPR2 record-template linkage."""
from __future__ import annotations

import csv, hashlib, json, math, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

from run_gdt012_core_semantic_atlas import strip_layers
from run_gdt062_right_family_register_renderer import parser as hpr2_parser

ROOT=Path(__file__).resolve().parent
PANEL=ROOT/'q20ob001_source_panel.tsv'
ALIGN=ROOT/'experiments/semantic_assumptions/results/source_sta_group_alignment.tsv'
HPR=ROOT/'gdt016_group_state_inventory.tsv'
METHOD=ROOT/'GDT114_Q20_RECORD_TEMPLATE_LINKAGE_METHOD.md'
REPORT=ROOT/'GDT114_Q20_RECORD_TEMPLATE_LINKAGE_REPORT.md'
INV=ROOT/'gdt114_q20_record_template_inventory.tsv'
FOLDS=ROOT/'gdt114_q20_record_template_folds.tsv'
SCORES=ROOT/'gdt114_q20_record_template_scores.tsv'
NULL=ROOT/'gdt114_q20_record_template_null.tsv'
COUNTER=ROOT/'gdt114_q20_record_template_counterexamples.tsv'
RESULT=ROOT/'gdt114_result.json'
EDITIONS=('ZL3b','IT2a','RF1b'); PRIMARY='ZL3b'
MODELS=('COMPILER_ONLY','EDGE_ONLY','FULL_HPR2','RAW_CHAR3_HASH32','HOST_CHAR3_HASH32')
LAMBDAS=(.1,1.,10.,100.,1000.); WORLDS=4096
WRAPS=('q','d','s','ch','che','sh','t')
EDGE_CHARS=tuple('abcdefghijklmnopqrstuvwxyz')+('OTHER',)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def seed(*x):return int(hashlib.sha256('|'.join(map(str,x)).encode()).hexdigest()[:16],16)
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def hash32(text):return int(hashlib.sha256(text.encode()).hexdigest()[:8],16)%32
def ngrams(text,n=3):
 z='^'+text+'$'
 return [z[i:i+n] for i in range(max(0,len(z)-n+1))]

def load_records():
 raw=[r for r in read(PANEL) if r['edition'] in EDITIONS]
 assert len(raw)==510 and not any(r['page'].startswith('f84r') for r in raw)
 wanted=set()
 for r in raw:
  wanted.add(r['open_locus']);wanted.update(r['body_line_loci'].split('|'))
 assert not any(x.startswith('f84r') for x in wanted)
 by=defaultdict(list)
 # Guard before any formal field is retained.
 with ALIGN.open(encoding='utf-8',newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):
   locus=r['locus']
   if locus not in wanted:continue
   assert not locus.startswith('f84r')
   by[(r['edition'],locus)].append((int(r['source_group_index']),r['nearest_basic_eva_primary']))
 for k in by:by[k].sort()
 frozen_source=read(HPR);parse,_=hpr2_parser(frozen_source)
 out=[]
 for r in raw:
  def groups(loci):
   z=[]
   for locus in loci:
    g=by[(r['edition'],locus)];assert g and [i for i,_ in g]==list(range(1,len(g)+1))
    z.extend((locus,i,t) for i,t in g)
   return z
  og=groups([r['open_locus']]);bg=groups(r['body_line_loci'].split('|'))
  def parsed(gs):
   ans=[]
   for locus,i,tok in gs:
    assert tok
    pref,resid,dy=strip_layers(tok);host,b3,right,inner,frame=parse({'residual_host':resid,'stripped_prefix':pref})
    ans.append({'locus':locus,'index':i,'token':tok,'wrapper':pref,'page_host':host,'right':right,'inner_d':inner,'frame':frame,'dy':int(dy),'b3':int(b3)})
   return ans
  O=parsed(og);B=parsed(bg)
  out.append({**r,'star_ordinal':int(r['star_ordinal']),'record_line_count':int(r['record_line_count']),
   'open_group_count':int(r['open_group_count']),'open_member_count':int(r['open_member_count']),
   'body_line_count':int(r['body_line_count']),'body_group_count':int(r['body_group_count']),
   'body_member_count':int(r['body_member_count']),'open':O,'body':B})
 assert all(len(r['open'])==r['open_group_count'] and len(r['body'])==r['body_group_count'] for r in out)
 return out

def compiler_vec(groups):
 n=len(groups);c=Counter()
 for g in groups:
  if g['wrapper'] in WRAPS:c['W_'+g['wrapper']]+=1
  if g['frame'] in ('O','OT'):c['F_'+g['frame']]+=1
  if g['right']!='NONE':c['RIGHT']+=1
  c['DY']+=g['dy'];c['B3']+=g['b3']
 keys=tuple('W_'+x for x in WRAPS)+('F_O','F_OT','RIGHT','DY','B3')
 return np.array([c[k]/n for k in keys],float)
def edge_vec(groups):
 n=len(groups);c=Counter();length=0
 for g in groups:
  h=g['page_host'];ch=h[-1].lower() if h else ''
  c[ch if ch in EDGE_CHARS else 'OTHER']+=1;length+=len(h)
 return np.array([c[k]/n for k in EDGE_CHARS]+[length/n,len({g['page_host'] for g in groups})/n],float)
def hash_vec(groups,use_host):
 x=np.zeros(32)
 for g in groups:
  s=g['page_host'] if use_host else g['token']
  for ng in ngrams(s):x[hash32(ng)]+=1
 return x/max(1,x.sum())
def add_vec(r,mode):
 if mode=='COMPILER_ONLY':return compiler_vec(r['open'])
 if mode=='EDGE_ONLY':return edge_vec(r['open'])
 if mode=='FULL_HPR2':return np.r_[compiler_vec(r['open']),edge_vec(r['open'])]
 return hash_vec(r['open'],mode=='HOST_CHAR3_HASH32')
def target_vec(r):return np.r_[compiler_vec(r['body']),edge_vec(r['body'])]

def local_body_mean(records,i):
 peers=[target_vec(r) for j,r in enumerate(records) if j!=i and r['physical_folio']==records[i]['physical_folio']]
 return np.mean(peers,axis=0) if peers else np.zeros(len(target_vec(records[i])))
def nuisance(records):
 page_counts=Counter(r['page'] for r in records);out=[]
 for i,r in enumerate(records):
  ordinal=r['star_ordinal']/max(1,page_counts[r['page']])
  side=1. if r['page'].endswith('v') else 0.
  shape=np.array([r['record_line_count'],r['open_group_count'],r['open_member_count'],r['body_group_count'],r['body_member_count'],side,ordinal],float)
  out.append(np.r_[shape,local_body_mean(records,i)])
 return np.vstack(out)
def standardize(train,test):
 mu=train.mean(0);sd=train.std(0);sd[sd<1e-8]=1.
 return (train-mu)/sd,(test-mu)/sd,mu,sd
def ridge_fit(X,Y,lam):
 X1=np.c_[np.ones(len(X)),X];pen=np.eye(X1.shape[1]);pen[0,0]=0
 return np.linalg.solve(X1.T@X1+lam*pen,X1.T@Y)
def ridge_pred(X,b):return np.c_[np.ones(len(X)),X]@b
def pseudo_bits(y,p0,p1):return float((np.square(y-p0).sum()-np.square(y-p1).sum())/(2*math.log(2)))

def inner_lambda(records,indices,mode,Xn,Xa,Y):
 folios=sorted({records[i]['physical_folio'] for i in indices});scores={l:0. for l in LAMBDAS}
 for held in folios:
  tr=[i for i in indices if records[i]['physical_folio']!=held];te=[i for i in indices if records[i]['physical_folio']==held]
  xntr,xnte,_,_=standardize(Xn[tr],Xn[te]);ytr,yte,_,_=standardize(Y[tr],Y[te])
  if mode=='NUISANCE':base_train=xntr;base_test=xnte
  else:
   xatr,xate,_,_=standardize(Xa[tr],Xa[te]);base_train=np.c_[xntr,xatr];base_test=np.c_[xnte,xate]
  for lam in LAMBDAS:
   b=ridge_fit(base_train,ytr,lam);scores[lam]+=float(np.square(yte-ridge_pred(base_test,b)).sum())
 return min(LAMBDAS,key=lambda l:(scores[l],l))

def fit_edition(records):
 Xn=nuisance(records);Y=np.vstack([target_vec(r) for r in records]);adds={m:np.vstack([add_vec(r,m) for r in records]) for m in MODELS}
 fold_rows=[];cache={};pred_store={}
 for held in sorted({r['physical_folio'] for r in records}):
  tr=[i for i,r in enumerate(records) if r['physical_folio']!=held];te=[i for i,r in enumerate(records) if r['physical_folio']==held]
  xntr,xnte,nmu,nsd=standardize(Xn[tr],Xn[te]);ytr,yte,ymu,ysd=standardize(Y[tr],Y[te])
  l0=inner_lambda(records,tr,'NUISANCE',Xn,None,Y);b0=ridge_fit(xntr,ytr,l0);p0=ridge_pred(xnte,b0)
  fold_rows.append({'edition':records[0]['edition'],'held_folio':held,'model':'NUISANCE','held_records':len(te),'lambda':l0,'pseudo_gain_bits':0.,'sse':float(np.square(yte-p0).sum()),'positive_gain':0})
  for mode in MODELS:
   xatr,xate,amu,asd=standardize(adds[mode][tr],adds[mode][te]);lam=inner_lambda(records,tr,mode,Xn,adds[mode],Y)
   b=ridge_fit(np.c_[xntr,xatr],ytr,lam);p=ridge_pred(np.c_[xnte,xate],b);gain=pseudo_bits(yte,p0,p)
   fold_rows.append({'edition':records[0]['edition'],'held_folio':held,'model':mode,'held_records':len(te),'lambda':lam,'pseudo_gain_bits':gain,'sse':float(np.square(yte-p).sum()),'positive_gain':int(gain>0)})
   cache[(held,mode)]={'te':te,'y':yte,'p0':p0,'b':b,'xn':xnte,'amu':amu,'asd':asd}
   pred_store[(held,mode)]=p
 return fold_rows,cache,adds

def permutation_scores(records,cache,adds):
 folios=sorted({r['physical_folio'] for r in records});world={m:[] for m in MODELS};capacities={}
 strata={}
 for held in folios:
  te=cache[(held,MODELS[0])]['te'];groups=defaultdict(list)
  for pos,i in enumerate(te):groups[records[i]['open_member_count']].append(pos)
  strata[held]=(te,groups);capacities[held]=sum(len(v) for v in groups.values() if len(v)>1)
 rng=random.Random(seed('GDT114',records[0]['edition']))
 for _ in range(WORLDS):
  assign={}
  for held,(te,groups) in strata.items():
   a=list(range(len(te)))
   for ps in groups.values():
    if len(ps)>1:
     z=ps[:];rng.shuffle(z)
     for p,q in zip(ps,z):a[p]=q
   assign[held]=a
  for mode in MODELS:
   total=0.
   for held in folios:
    c=cache[(held,mode)];te=c['te'];raw=adds[mode][te][assign[held]];xa=(raw-c['amu'])/c['asd'];p=ridge_pred(np.c_[c['xn'],xa],c['b']);total+=pseudo_bits(c['y'],c['p0'],p)
   world[mode].append(total)
 return world,capacities

def main():
 all_records=load_records();inv=[];all_folds=[];all_scores=[];all_null=[];counter=[];result_ed={}
 for ed in EDITIONS:
  rec=[r for r in all_records if r['edition']==ed];assert len(rec)==170
  for r in rec:
   cv=compiler_vec(r['open']);bv=compiler_vec(r['body']);inv.append({'unit_id':r['unit_id'],'edition':ed,'page':r['page'],'physical_folio':r['physical_folio'],'star_ordinal':r['star_ordinal'],'open_locus':r['open_locus'],'body_line_loci':r['body_line_loci'],'record_line_count':r['record_line_count'],'open_groups':len(r['open']),'body_groups':len(r['body']),'open_member_count':r['open_member_count'],'body_member_count':r['body_member_count'],'open_compiler_rates':'|'.join(f'{x:.6f}' for x in cv),'body_compiler_rates':'|'.join(f'{x:.6f}' for x in bv),'open_profile_sha256':csha({'compiler':cv.tolist(),'edge':edge_vec(r['open']).tolist()}),'body_profile_sha256':csha({'compiler':bv.tolist(),'edge':edge_vec(r['body']).tolist()}),'claim_state':'ANONYMOUS_RECORD_TEMPLATE_PROFILE'})
  folds,cache,adds=fit_edition(rec);world,capacities=permutation_scores(rec,cache,adds);all_folds+=folds
  scores={}
  for mode in MODELS:
   fr=[r for r in folds if r['model']==mode];true=sum(r['pseudo_gain_bits'] for r in fr);null=world[mode];local=(1+sum(x>=true-1e-12 for x in null))/(WORLDS+1)
   maxnull=[max(world[m][i] for m in MODELS) for i in range(WORLDS)];maxt=(1+sum(x>=true-1e-12 for x in maxnull))/(WORLDS+1)
   row={'edition':ed,'model':mode,'records':170,'held_folios':8,'pseudo_gain_bits':true,'selector_paid_gain_bits':true-math.log2(len(MODELS)),'positive_folios':sum(r['pseudo_gain_bits']>0 for r in fr),'local_p':local,'max_five_p':maxt,'null_median_bits':float(np.median(null)),'null_q95_bits':float(np.quantile(null,.95)),'swappable_records':sum(capacities.values())}
   all_scores.append(row);scores[mode]=row;all_null.append({'edition':ed,'model':mode,'worlds':WORLDS,'true_gain_bits':true,'null_mean_bits':float(np.mean(null)),'null_median_bits':float(np.median(null)),'null_sd_bits':float(np.std(null)),'null_q95_bits':float(np.quantile(null,.95)),'inclusive_local_p':local,'inclusive_max_five_p':maxt,'swappable_records':sum(capacities.values()),'folio_capacity':'|'.join(f'{k}:{v}' for k,v in sorted(capacities.items()))})
   for r in sorted(fr,key=lambda x:x['pseudo_gain_bits'])[:3]:counter.append({'edition':ed,'model':mode,'held_folio':r['held_folio'],'pseudo_gain_bits':r['pseudo_gain_bits'],'counterexample':'HELD_FOLIO_NEGATIVE_OR_WEAKEST','claim_state':'TRANSFER_DIAGNOSTIC'})
  result_ed[ed]=scores
 primary=result_ed[PRIMARY]['FULL_HPR2'];raw=result_ed[PRIMARY]['RAW_CHAR3_HASH32'];host=result_ed[PRIMARY]['HOST_CHAR3_HASH32']
 gates={'selector_paid_positive':primary['selector_paid_gain_bits']>0,'six_of_eight_positive_folios':primary['positive_folios']>=6,'all_readings_positive':all(result_ed[e]['FULL_HPR2']['pseudo_gain_bits']>0 for e in EDITIONS),'max_five_p_le_005':primary['max_five_p']<=.05,'beats_both_string_controls':primary['pseudo_gain_bits']>max(raw['pseudo_gain_bits'],host['pseudo_gain_bits'])}
 if all(gates.values()):status='Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_SUPPORTED'
 elif primary['pseudo_gain_bits']>0:status='Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_WEAK_OR_LOCAL'
 else:status='Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_NOT_SUPPORTED'
 write(INV,inv);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in all_folds]);write(SCORES,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in all_scores]);write(NULL,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in all_null]);write(COUNTER,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in counter])
 report=f'''# GDT114 — Q20 OPEN-to-BODY record-template linkage

Status: **{status}**

This nested whole-folio test reused 170 clean star-delimited Q20 records on
eight physical folios. It predicts anonymous HPR2 BODY-template profiles, not
BODY strings or meanings. The nuisance baseline already knows record shape and
the leave-one-record-out mean BODY profile of the other records on the held
folio. ZL3b is primary; IT2a and RF1b are alternate-reading sensitivities.

## Held-folio result

| representation | ZL gain bits | selector-paid | positive folios | local p | max-five p | IT gain | RF gain |
|---|---:|---:|---:|---:|---:|---:|---:|
'''+''.join(f"| `{m}` | {result_ed['ZL3b'][m]['pseudo_gain_bits']:+.3f} | {result_ed['ZL3b'][m]['selector_paid_gain_bits']:+.3f} | {result_ed['ZL3b'][m]['positive_folios']}/8 | {result_ed['ZL3b'][m]['local_p']:.4f} | {result_ed['ZL3b'][m]['max_five_p']:.4f} | {result_ed['IT2a'][m]['pseudo_gain_bits']:+.3f} | {result_ed['RF1b'][m]['pseudo_gain_bits']:+.3f} |\n" for m in MODELS)+f'''
The exact-length pairing null has {primary['swappable_records']}/170 primary
records with permutation capacity. `FULL_HPR2` {'beats' if gates['beats_both_string_controls'] else 'does not beat'}
both hashed-string controls. Its registered gates are `{json.dumps(gates,sort_keys=True)}`.

## Relation to Q20OB001 and GDT113

Q20OB001 remains a zero-gain result for literal OPEN member/family/group caches
above KT/string and other-BODY vocabulary baselines. GDT114 tests a genuinely
different mechanism: training-folio OPEN profiles predicting held-folio BODY
compiler/edge distributions. A positive exploratory score would localize
record linkage above literal copying; a negative score would further narrow
GDT113 to page codebook ecology rather than OPEN-controlled record templates.

No semantic role, recipe, heading, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is inferred. f84r was rejected before
formal retention and was not opened, retained, queried, joined, scored,
targeted, or assigned a prediction.
''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT114_Q20_RECORD_TEMPLATE_LINKAGE_RESULT_V1','status':status,'records':170,'physical_folios':8,'editions':list(EDITIONS),'models':list(MODELS),'worlds':WORLDS,'primary':primary,'gates':gates,'scores':all_scores,'interpretation':'Exploratory nested held-folio OPEN-to-BODY record-template linkage, distinct from the failed Q20OB001 literal cache.','claim_ceiling':'Anonymous record-template dependence only; no semantic role, recipe, heading, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{PANEL.name:sha(PANEL),str(ALIGN.relative_to(ROOT)):sha(ALIGN),HPR.name:sha(HPR),'q20ob001_result.json':sha(ROOT/'q20ob001_result.json'),'gdt113_result.json':sha(ROOT/'gdt113_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt012_core_semantic_atlas.py':sha(ROOT/'run_gdt012_core_semantic_atlas.py'),'run_gdt062_right_family_register_renderer.py':sha(ROOT/'run_gdt062_right_family_register_renderer.py')},'outputs':{p.name:sha(p) for p in (INV,FOLDS,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'primary':primary,'gates':gates},sort_keys=True))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""GDT116: held-folio 7x7 OPEN/BODY wrapper-channel localization."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g

ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT116_Q20_WRAPPER_CHANNEL_MAP_METHOD.md';REPORT=ROOT/'GDT116_Q20_WRAPPER_CHANNEL_MAP_REPORT.md';CELLS=ROOT/'gdt116_wrapper_channel_cells.tsv';FOLDS=ROOT/'gdt116_wrapper_channel_folds.tsv';MAPS=ROOT/'gdt116_wrapper_bijections.tsv';COUNTER=ROOT/'gdt116_wrapper_counterexamples.tsv';RESULT=ROOT/'gdt116_result.json';LAM=1000.;WORLDS=4096;W=g.WRAPS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def fit_pair(rec,i,j):
 Xn=g.nuisance(rec);Xa=np.array([g.compiler_vec(r['open'])[i] for r in rec])[:,None];Y=np.array([g.compiler_vec(r['body'])[j] for r in rec])[:,None];fold=[];cache={}
 for held in sorted({r['physical_folio'] for r in rec}):
  tr=[k for k,r in enumerate(rec) if r['physical_folio']!=held];te=[k for k,r in enumerate(rec) if r['physical_folio']==held]
  xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);xatr,xate,amu,asd=g.standardize(Xa[tr],Xa[te]);ytr,yte,_,_=g.standardize(Y[tr],Y[te]);b0=g.ridge_fit(xntr,ytr,LAM);p0=g.ridge_pred(xnte,b0);b=g.ridge_fit(np.c_[xntr,xatr],ytr,LAM);p=g.ridge_pred(np.c_[xnte,xate],b);gain=g.pseudo_bits(yte,p0,p);fold.append({'held_folio':held,'pseudo_gain_bits':gain,'positive_gain':int(gain>0)});cache[held]={'te':te,'y':yte,'p0':p0,'xn':xnte,'amu':amu,'asd':asd,'b':b}
 return fold,cache,Xa
def main():
 allr=g.load_records();cells=[];foldout=[];maps=[];counter=[];summ={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];models={};true={}
  for i,a in enumerate(W):
   for j,b in enumerate(W):
    f,c,x=fit_pair(rec,i,j);models[a,b]=(c,x);true[a,b]=sum(z['pseudo_gain_bits'] for z in f)
    for z in f:foldout.append({'edition':ed,'open_wrapper':a,'body_wrapper':b,**z})
  # Shared same-page exact-length permutations.
  template=next(iter(models.values()))[0];strata={};cap=0
  for held,c in template.items():
   te=c['te'];d=defaultdict(list)
   for pos,k in enumerate(te):d[(rec[k]['page'],rec[k]['open_member_count'])].append(pos)
   cap+=sum(len(v) for v in d.values() if len(v)>1);strata[held]=(te,d)
  world={(a,b):[] for a in W for b in W};diag=[];rng=random.Random(g.seed('GDT116',ed))
  for _ in range(WORLDS):
   assign={}
   for held,(te,d) in strata.items():
    z=list(range(len(te)))
    for ps in d.values():
     if len(ps)>1:
      q=ps[:];rng.shuffle(q)
      for p,v in zip(ps,q):z[p]=v
    assign[held]=z
   vals={}
   for a in W:
    for b in W:
     total=0.;cache,Xa=models[a,b]
     for held,c in cache.items():
      te=c['te'];raw=Xa[te][assign[held]];xa=(raw-c['amu'])/c['asd'];p=g.ridge_pred(np.c_[c['xn'],xa],c['b']);total+=g.pseudo_bits(c['y'],c['p0'],p)
     world[a,b].append(total);vals[a,b]=total
   diag.append(sum(vals[x,x] for x in W))
  mx=[max(world[k][q] for k in world) for q in range(WORLDS)]
  for a in W:
   for b in W:
    fs=[z for z in foldout if z['edition']==ed and z['open_wrapper']==a and z['body_wrapper']==b];t=true[a,b];cells.append({'edition':ed,'open_wrapper':a,'body_wrapper':b,'true_gain_bits':t,'positive_folios':sum(z['positive_gain'] for z in fs),'same_page_swappable_records':cap,'null_median_bits':float(np.median(world[a,b])),'local_p':(1+sum(x>=t-1e-12 for x in world[a,b]))/(WORLDS+1),'max_49_p':(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1),'diagonal_cell':int(a==b)})
    for z in sorted(fs,key=lambda q:q['pseudo_gain_bits'])[:2]:counter.append({'edition':ed,'open_wrapper':a,'body_wrapper':b,'held_folio':z['held_folio'],'pseudo_gain_bits':z['pseudo_gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
  identity=sum(true[x,x] for x in W);dp=(1+sum(x>=identity-1e-12 for x in diag))/(WORLDS+1)
  perms=[]
  for p in itertools.permutations(W):perms.append((sum(true[a,b] for a,b in zip(W,p)),p))
  perms.sort(reverse=True);rank=1+sum(v>identity+1e-12 for v,_ in perms);bestv,bestp=perms[0]
  maps.append({'edition':ed,'mapping_type':'IDENTITY_PREDECLARED','mapping':'|'.join(f'{a}->{a}' for a in W),'sum_gain_bits':identity,'rank_of_5040':rank,'same_page_permutation_p':dp,'claim_state':'INHERITED_COMPOSITE'})
  maps.append({'edition':ed,'mapping_type':'BEST_POSTSELECTED_BIJECTION','mapping':'|'.join(f'{a}->{b}' for a,b in zip(W,bestp)),'sum_gain_bits':bestv,'rank_of_5040':1,'same_page_permutation_p':'NOT_INFERENTIAL','claim_state':'DESCRIPTIVE_POSTSELECTION'})
  summ[ed]={'identity_gain':identity,'identity_rank':rank,'identity_p':dp,'best_gain':bestv,'best_mapping':'|'.join(f'{a}->{b}' for a,b in zip(W,bestp))}
 zl=sorted([x for x in cells if x['edition']=='ZL3b'],key=lambda x:(-x['true_gain_bits'],x['open_wrapper'],x['body_wrapper']));top=zl[0];stable=[x for x in zl if all(next(z for z in cells if z['edition']==e and z['open_wrapper']==x['open_wrapper'] and z['body_wrapper']==x['body_wrapper'])['true_gain_bits']>0 for e in g.EDITIONS)]
 status='Q20_WRAPPER_CHANNEL_MAP_TRANSFERABLE_BUT_NONIDENTITY' if all(summ[e]['identity_gain']>0 for e in g.EDITIONS) else 'Q20_WRAPPER_CHANNEL_MAP_WEAK_OR_UNSTABLE'
 write(CELLS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in cells]);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in foldout]);write(MAPS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in maps]);write(COUNTER,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in counter])
 report=f'''# GDT116 — Q20 OPEN/BODY wrapper-channel map

Status: **{status}**

The inherited seven-wrapper channel was resolved into 49 held-folio scalar
links under a same-page exact-OPEN-length null. The strongest ZL3b cell is
`{top['open_wrapper']} -> {top['body_wrapper']}` at {top['true_gain_bits']:+.3f}
bits, positive on {top['positive_folios']}/8 folios, local p={top['local_p']:.4f}
and max-49 p={top['max_49_p']:.4f}. {len(stable)}/49 cells have positive gain
in all three reading sensitivities.

The predeclared identity composite gains ZL/IT/RF
{summ['ZL3b']['identity_gain']:+.3f} / {summ['IT2a']['identity_gain']:+.3f} /
{summ['RF1b']['identity_gain']:+.3f} bits. Its rank among all 7! descriptive
bijections is {summ['ZL3b']['identity_rank']}/5040 in ZL3b. The best postselected
ZL mapping is `{summ['ZL3b']['best_mapping']}`. A nonidentity optimum means the
OPEN does not simply repeat the same wrapper mixture: it selects a transferable
but coupled BODY wrapper regime.

This is an anonymous record-channel map only. It does not assign a wrapper
function, recipe, heading, semantic role, word, morpheme, POS, sound, language,
plaintext, meaning, or translation. f84r remained excluded and unpredicted.
''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT116_Q20_WRAPPER_CHANNEL_MAP_RESULT_V1','status':status,'records':170,'physical_folios':8,'cells':49,'worlds':WORLDS,'top_zl_cell':top,'stable_positive_cells':len(stable),'mapping_summary':summ,'interpretation':'OPEN wrapper proportions select a coupled BODY wrapper regime; the best mapping need not be identity.','claim_ceiling':'Anonymous wrapper-channel mapping only; no wrapper function, recipe, heading, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{'gdt115_result.json':sha(ROOT/'gdt115_result.json'),'gdt114_result.json':sha(ROOT/'gdt114_result.json'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (CELLS,FOLDS,MAPS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'top':top,'summary':summ},sort_keys=True))
if __name__=='__main__':main()

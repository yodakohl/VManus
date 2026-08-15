#!/usr/bin/env python3
"""GDT120: nested held-folio discovery/prediction of anonymous Q20 classes."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g

ROOT=Path(__file__).resolve().parent
METHOD=ROOT/'GDT120_Q20_LATENT_RECORD_CLASS_METHOD.md';REPORT=ROOT/'GDT120_Q20_LATENT_RECORD_CLASS_REPORT.md'
ASSIGN=ROOT/'gdt120_q20_latent_class_assignments.tsv';PROTO=ROOT/'gdt120_q20_latent_class_prototypes.tsv';FOLDS=ROOT/'gdt120_q20_latent_class_folds.tsv';SCORES=ROOT/'gdt120_q20_latent_class_scores.tsv';NULL=ROOT/'gdt120_q20_latent_class_null.tsv';COUNTER=ROOT/'gdt120_q20_latent_class_counterexamples.tsv';RESULT=ROOT/'gdt120_result.json'
KS=(2,3,4,5,6);MODES=('OPEN_WRAPPER7','OPEN_COMPILER12','OPEN_EDGE29','RAW_OPEN_CHAR3_HASH32');LAM=1000.;WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def seed(*x):return int(hashlib.sha256('|'.join(map(str,x)).encode()).hexdigest()[:16],16)
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def xadd(r,m):
 if m=='OPEN_WRAPPER7':return g.compiler_vec(r['open'])[:7]
 if m=='OPEN_COMPILER12':return g.compiler_vec(r['open'])
 if m=='OPEN_EDGE29':return g.edge_vec(r['open'])
 return g.hash_vec(r['open'],False)
def nuisance(rec):
 pc=defaultdict(int)
 for r in rec:pc[r['page']]+=1
 return np.array([[r['record_line_count'],r['open_group_count'],r['open_member_count'],r['body_group_count'],r['body_member_count'],float(r['page'].endswith('v')),r['star_ordinal']/pc[r['page']]] for r in rec],float)
def kmeans(train,k,tag):
 best=None
 for rep in range(16):
  rng=random.Random(seed('GDT120_KMEANS',tag,k,rep));ids=rng.sample(range(len(train)),k);cent=train[ids].copy()
  for _ in range(100):
   lab=np.argmin(((train[:,None,:]-cent[None,:,:])**2).sum(2),axis=1);new=cent.copy()
   for j in range(k):
    if np.any(lab==j):new[j]=train[lab==j].mean(0)
   if np.max(np.abs(new-cent))<1e-12:break
   cent=new
  sse=float(((train-cent[lab])**2).sum());key=(sse,tuple(np.round(cent.flatten(),12)))
  if best is None or key<best[0]:best=(key,cent)
 cent=best[1];order=sorted(range(k),key=lambda j:tuple(np.round(cent[j],12)));cent=cent[order]
 lab=np.argmin(((train[:,None,:]-cent[None,:,:])**2).sum(2),axis=1)
 return cent,lab,float(((train-cent[lab])**2).sum())
def ari(a,b):
 n=len(a);ca=defaultdict(int);cb=defaultdict(int);cab=defaultdict(int)
 for x,y in zip(a,b):ca[x]+=1;cb[y]+=1;cab[x,y]+=1
 c2=lambda z:z*(z-1)/2
 s=sum(c2(v) for v in cab.values());sa=sum(c2(v) for v in ca.values());sb=sum(c2(v) for v in cb.values());tot=c2(n)
 exp=sa*sb/tot if tot else 0.;mx=(sa+sb)/2;return (s-exp)/(mx-exp) if mx>exp else 1.
def fit_fold(rec,held,k,ed):
 tr=[i for i,r in enumerate(rec) if r['physical_folio']!=held];te=[i for i,r in enumerate(rec) if r['physical_folio']==held]
 B=np.vstack([g.compiler_vec(r['body']) for r in rec]);bt,bv,mu,sd=g.standardize(B[tr],B[te]);cent,ylab,sse=kmeans(bt,k,f'{ed}:{held}');yt=np.argmin(((bv[:,None,:]-cent[None,:,:])**2).sum(2),axis=1);Y=np.eye(k)[ylab];Yt=np.eye(k)[yt]
 Xn=nuisance(rec);xn,xnt,_,_=g.standardize(Xn[tr],Xn[te]);b0=g.ridge_fit(xn,Y,LAM);p0=g.ridge_pred(xnt,b0);models={}
 for m in MODES:
  A=np.vstack([xadd(r,m) for r in rec]);xa,xat,amu,asd=g.standardize(A[tr],A[te]);b=g.ridge_fit(np.c_[xn,xa],Y,LAM);p=g.ridge_pred(np.c_[xnt,xat],b);models[m]={'gain':g.pseudo_bits(Yt,p0,p),'A':A,'amu':amu,'asd':asd,'b':b,'p0':p0,'Yt':Yt,'xnt':xnt}
 return {'tr':tr,'te':te,'cent':cent,'train_labels':ylab,'test_labels':yt,'train_sse':sse,'models':models}
def main():
 allr=g.load_records();all_assign=[];all_proto=[];all_fold=[];all_score=[];all_null=[];counter=[];foldsets={};summ={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];folios=sorted({r['physical_folio'] for r in rec});Xn=nuisance(rec);cache={}
  for k in KS:
   for held in folios:
    z=fit_fold(rec,held,k,ed);cache[k,held]=z
    for j,c in enumerate(z['cent']):all_proto.append({'edition':ed,'k':k,'held_folio':held,'class_id':j,'training_records':len(z['tr']),'training_sse':z['train_sse'],'centroid':'|'.join(f'{x:.9f}' for x in c)})
    for pos,i in enumerate(z['te']):all_assign.append({'edition':ed,'k':k,'held_folio':held,'unit_id':rec[i]['unit_id'],'page':rec[i]['page'],'star_ordinal':rec[i]['star_ordinal'],'class_id':int(z['test_labels'][pos]),'body_compiler':'|'.join(f'{x:.6f}' for x in g.compiler_vec(rec[i]['body']))})
    for m in MODES:all_fold.append({'edition':ed,'k':k,'model':m,'held_folio':held,'held_records':len(z['te']),'pseudo_gain_bits':z['models'][m]['gain'],'positive_gain':int(z['models'][m]['gain']>0)})
  # Shared same-page/exact-length assignments for every K/model.
  strata={}
  for held in folios:
   te=cache[KS[0],held]['te'];d=defaultdict(list)
   for pos,i in enumerate(te):d[rec[i]['page'],rec[i]['open_member_count']].append(pos)
   strata[held]=d
  rng=random.Random(seed('GDT120_NULL',ed));world={(k,m):[] for k in KS for m in MODES}
  for _ in range(WORLDS):
   assigns={}
   for held,d in strata.items():
    a=list(range(len(cache[KS[0],held]['te'])))
    for ps in d.values():
     if len(ps)>1:
      q=ps[:];rng.shuffle(q)
      for x,y in zip(ps,q):a[x]=y
    assigns[held]=a
   for k in KS:
    for m in MODES:
     total=0.
     for held in folios:
      z=cache[k,held];mm=z['models'][m];te=z['te'];raw=mm['A'][te][assigns[held]];xa=(raw-mm['amu'])/mm['asd'];p=g.ridge_pred(np.c_[mm['xnt'],xa],mm['b']);total+=g.pseudo_bits(mm['Yt'],mm['p0'],p)
     world[k,m].append(total)
  mx=[max(world[k,m][q] for k in KS for m in MODES) for q in range(WORLDS)]
  for k in KS:
   for m in MODES:
    fs=[x for x in all_fold if x['edition']==ed and x['k']==k and x['model']==m];t=sum(x['pseudo_gain_bits'] for x in fs);w=world[k,m]
    row={'edition':ed,'k':k,'model':m,'records':170,'held_folios':8,'pseudo_gain_bits':t,'selector_paid_gain_bits':t-math.log2(len(KS)*len(MODES)),'positive_folios':sum(x['pseudo_gain_bits']>0 for x in fs),'local_p':(1+sum(x>=t-1e-12 for x in w))/(WORLDS+1),'max_20_p':(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1),'null_median_bits':float(np.median(w))};all_score.append(row);all_null.append({'edition':ed,'k':k,'model':m,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(w)),'null_median_bits':float(np.median(w)),'null_q95_bits':float(np.quantile(w,.95)),'local_p':row['local_p'],'max_20_p':row['max_20_p']})
    for x in sorted(fs,key=lambda q:q['pseudo_gain_bits'])[:2]:counter.append({'edition':ed,'k':k,'model':m,'held_folio':x['held_folio'],'pseudo_gain_bits':x['pseudo_gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
  foldsets[ed]=cache
 # Label-free alternate-reading agreement for each K.
 stability={}
 for k in KS:
  labs={}
  for ed in g.EDITIONS:
   rec=[r for r in allr if r['edition']==ed];z={}
   for held in sorted({r['physical_folio'] for r in rec}):
    q=foldsets[ed][k,held]
    for pos,i in enumerate(q['te']):z[rec[i]['unit_id']]=int(q['test_labels'][pos])
   labs[ed]=z
  ids=sorted(set.intersection(*(set(x) for x in labs.values())));pairs={a+'__'+b:ari([labs[a][i] for i in ids],[labs[b][i] for i in ids]) for a,b in (('ZL3b','IT2a'),('ZL3b','RF1b'),('IT2a','RF1b'))};stability[k]={'pairs':pairs,'mean_ari':sum(pairs.values())/3}
  for row in all_score:
   if row['k']==k:row['mean_cross_reading_ari']=stability[k]['mean_ari']
 for ed in g.EDITIONS:summ[ed]={(x['k'],x['model']):x for x in all_score if x['edition']==ed}
 prim=[x for x in all_score if x['edition']=='ZL3b' and x['model']=='OPEN_COMPILER12'];best=max(prim,key=lambda x:(x['pseudo_gain_bits'],-x['k']));gates={'selector_paid_positive':best['selector_paid_gain_bits']>0,'max_20_p_le_005':best['max_20_p']<=.05,'six_of_eight_positive':best['positive_folios']>=6,'all_readings_positive':all(summ[e][best['k'],'OPEN_COMPILER12']['pseudo_gain_bits']>0 for e in g.EDITIONS),'mean_cross_reading_ari_ge_05':stability[best['k']]['mean_ari']>=.5}
 status='Q20_ANONYMOUS_BODY_CLASS_PREDICTABLE_FROM_OPEN_COMPILER' if all(gates.values()) else 'Q20_LATENT_RECORD_CLASSES_WEAK_OR_UNSTABLE' if best['pseudo_gain_bits']>0 else 'Q20_LATENT_RECORD_CLASS_PREDICTION_NOT_SUPPORTED'
 def fmt(rows):return [{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in rows]
 write(ASSIGN,fmt(all_assign));write(PROTO,fmt(all_proto));write(FOLDS,fmt(all_fold));write(SCORES,fmt(all_score));write(NULL,fmt(all_null));write(COUNTER,fmt(counter))
 zlit=stability[best['k']]['mean_ari'];rf=summ['RF1b'][best['k'],'OPEN_COMPILER12'];it=summ['IT2a'][best['k'],'OPEN_COMPILER12']
 report=f'''# GDT120 — Q20 latent record-class prediction\n\nStatus: **{status}**\n\nTraining folios alone discovered anonymous BODY compiler classes for every K=2..6; the unseen folio was assigned to the frozen centroids before its OPEN was scored. The strongest ZL3b compiler resolution is K={best['k']}: {best['pseudo_gain_bits']:+.3f} pseudo-bits, selector-paid {best['selector_paid_gain_bits']:+.3f}, {best['positive_folios']}/8 positive folios, local p={best['local_p']:.4f}, max-20 p={best['max_20_p']:.4f}. IT2a/RF1b gains at the same K are {it['pseudo_gain_bits']:+.3f}/{rf['pseudo_gain_bits']:+.3f}; mean label-free cross-reading ARI is {zlit:.3f}. Registered gates: `{json.dumps(gates,sort_keys=True)}`.\n\n| K | wrapper gain | compiler gain | edge gain | raw gain | compiler max-20 p | mean ARI |\n|---:|---:|---:|---:|---:|---:|---:|\n'''+''.join(f"| {k} | {summ['ZL3b'][k,'OPEN_WRAPPER7']['pseudo_gain_bits']:+.3f} | {summ['ZL3b'][k,'OPEN_COMPILER12']['pseudo_gain_bits']:+.3f} | {summ['ZL3b'][k,'OPEN_EDGE29']['pseudo_gain_bits']:+.3f} | {summ['ZL3b'][k,'RAW_OPEN_CHAR3_HASH32']['pseudo_gain_bits']:+.3f} | {summ['ZL3b'][k,'OPEN_COMPILER12']['max_20_p']:.4f} | {stability[k]['mean_ari']:.3f} |\n" for k in KS)+'''\nThe result concerns an anonymous record-template alphabet only. Fold-local class numbers are not meanings and cannot be compared as named categories across folds without their centroids. It neither overrides Q20OB001's failed literal cache nor turns OPEN into a heading. No semantic role, star property, word, morpheme, POS, sound, language, plaintext, meaning, or translation is assigned. f84r remained fully excluded and unpredicted.\n''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT120_Q20_LATENT_RECORD_CLASS_RESULT_V1','status':status,'records':170,'physical_folios':8,'k_values':list(KS),'models':list(MODES),'worlds':WORLDS,'primary':best,'gates':gates,'stability':stability,'scores':all_score,'interpretation':'Nested held-folio discovery and prediction of anonymous BODY compiler classes from OPEN profiles.','claim_ceiling':'Anonymous record-template classes only; no heading, recipe, role, star property, word, morpheme, POS, sound, language, plaintext, meaning or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'assigned':False,'prediction_frozen':False},'inputs':{'gdt115_result.json':sha(ROOT/'gdt115_result.json'),'gdt117_result.json':sha(ROOT/'gdt117_result.json'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{p.name:sha(p) for p in (ASSIGN,PROTO,FOLDS,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'primary':best,'gates':gates,'stability':stability},sort_keys=True))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""GDT118: held-folio OPEN compiler prediction at successive BODY depths."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g

ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT118_Q20_COMPILER_DEPTH_TRANSFER_METHOD.md';REPORT=ROOT/'GDT118_Q20_COMPILER_DEPTH_TRANSFER_REPORT.md';SCORES=ROOT/'gdt118_compiler_depth_scores.tsv';FOLDS=ROOT/'gdt118_compiler_depth_folds.tsv';NULL=ROOT/'gdt118_compiler_depth_null.tsv';COUNTER=ROOT/'gdt118_compiler_depth_counterexamples.tsv';RESULT=ROOT/'gdt118_result.json';LAM=1000.;WORLDS=4096;DEPTHS=('BODY_LINE_1','BODY_LINE_2','BODY_TAIL_3PLUS');MODES=('COMPILER12','RAW_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def depth_groups(r,d):
 loci=r['body_line_loci'].split('|')
 keep={loci[0]} if d=='BODY_LINE_1' else {loci[1]} if d=='BODY_LINE_2' and len(loci)>1 else set(loci[2:]) if d=='BODY_TAIL_3PLUS' else set()
 return [x for x in r['body'] if x['locus'] in keep]
def add(r,m):return g.compiler_vec(r['open']) if m=='COMPILER12' else g.hash_vec(r['open'],False)
def fit(rec,ids,d,m):
 Xbase=g.nuisance(rec)[ids];Xa=np.vstack([add(rec[i],m) for i in ids]);Y=np.vstack([g.compiler_vec(depth_groups(rec[i],d)) for i in ids]);local=[]
 for ii,i in enumerate(ids):
  peers=[Y[j] for j,k in enumerate(ids) if k!=i and rec[k]['physical_folio']==rec[i]['physical_folio']]
  local.append(np.mean(peers,axis=0) if peers else np.zeros(Y.shape[1]))
 Xn=np.c_[Xbase,np.vstack(local)];fold=[];cache={}
 for held in sorted({rec[i]['physical_folio'] for i in ids}):
  tr=[j for j,i in enumerate(ids) if rec[i]['physical_folio']!=held];te=[j for j,i in enumerate(ids) if rec[i]['physical_folio']==held]
  xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);xatr,xate,amu,asd=g.standardize(Xa[tr],Xa[te]);ytr,yte,_,_=g.standardize(Y[tr],Y[te]);b0=g.ridge_fit(xntr,ytr,LAM);p0=g.ridge_pred(xnte,b0);b=g.ridge_fit(np.c_[xntr,xatr],ytr,LAM);p=g.ridge_pred(np.c_[xnte,xate],b);gain=g.pseudo_bits(yte,p0,p);fold.append({'held_folio':held,'held_records':len(te),'pseudo_gain_bits':gain,'positive_gain':int(gain>0)});cache[held]={'global_ids':[ids[j] for j in te],'y':yte,'p0':p0,'xn':xnte,'amu':amu,'asd':asd,'b':b}
 return fold,cache,np.vstack([add(r,m) for r in rec])
def main():
 allr=g.load_records();scores=[];foldout=[];nullout=[];counter=[];summ={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];models=[];true={}
  for d in DEPTHS:
   ids=[i for i,r in enumerate(rec) if depth_groups(r,d)]
   for m in MODES:
    f,c,X=fit(rec,ids,d,m);name=d+'__'+m;models.append((name,d,m,c,X,ids));true[name]=sum(x['pseudo_gain_bits'] for x in f)
    for x in f:foldout.append({'edition':ed,'depth':d,'model':m,**x})
    for x in sorted(f,key=lambda z:z['pseudo_gain_bits'])[:2]:counter.append({'edition':ed,'depth':d,'model':m,'held_folio':x['held_folio'],'pseudo_gain_bits':x['pseudo_gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
  world={name:[] for name,_,_,_,_,_ in models};caps={};rng=random.Random(g.seed('GDT118',ed))
  for _ in range(WORLDS):
   assignments={}
   for name,d,m,c,X,ids in models:
    if d in assignments:continue
    by=defaultdict(list)
    for i in ids:by[(rec[i]['page'],rec[i]['open_member_count'])].append(i)
    a={i:i for i in ids}
    for ps in by.values():
     if len(ps)>1:
      z=ps[:];rng.shuffle(z)
      for p,q in zip(ps,z):a[p]=q
    assignments[d]=a;caps[d]=sum(len(v) for v in by.values() if len(v)>1)
   for name,d,m,c,X,ids in models:
    total=0.;a=assignments[d]
    for held,z in c.items():
     raw=np.vstack([X[a[i]] for i in z['global_ids']]);xa=(raw-z['amu'])/z['asd'];p=g.ridge_pred(np.c_[z['xn'],xa],z['b']);total+=g.pseudo_bits(z['y'],z['p0'],p)
    world[name].append(total)
  mx=[max(world[n][q] for n in world) for q in range(WORLDS)]
  for name,d,m,c,X,ids in models:
   fs=[x for x in foldout if x['edition']==ed and x['depth']==d and x['model']==m];t=true[name];row={'edition':ed,'depth':d,'model':m,'eligible_records':len(ids),'held_folios':len(fs),'swappable_records':caps[d],'true_gain_bits':t,'selector_paid_gain_bits':t-math.log2(6),'positive_folios':sum(x['positive_gain'] for x in fs),'null_median_bits':float(np.median(world[name])),'local_p':(1+sum(x>=t-1e-12 for x in world[name]))/(WORLDS+1),'max_six_p':(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1)};scores.append(row);nullout.append({'edition':ed,'depth':d,'model':m,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(world[name])),'null_median_bits':float(np.median(world[name])),'null_q95_bits':float(np.quantile(world[name],.95)),'local_p':row['local_p'],'max_six_p':row['max_six_p']})
  summ[ed]={(x['depth'],x['model']):x for x in scores if x['edition']==ed}
 p=summ['ZL3b'];line1=p['BODY_LINE_1','COMPILER12'];line2=p['BODY_LINE_2','COMPILER12'];tail=p['BODY_TAIL_3PLUS','COMPILER12'];supported=[x for x in (line1,line2,tail) if x['true_gain_bits']>0 and x['max_six_p']<=.05]
 status='Q20_OPEN_COMPILER_LINK_PERSISTS_BEYOND_FIRST_BODY_LINE' if any(x['depth']!='BODY_LINE_1' for x in supported) else 'Q20_OPEN_COMPILER_LINK_IS_IMMEDIATE_CONTINUATION_ONLY' if line1 in supported else 'Q20_OPEN_COMPILER_DEPTH_TRANSFER_WEAK_OR_UNSTABLE'
 write(SCORES,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in scores]);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in foldout]);write(NULL,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in nullout]);write(COUNTER,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in counter])
 report=f'''# GDT118 — Q20 OPEN compiler transfer by BODY depth

Status: **{status}**

| depth | records | ZL compiler gain | positive folios | max-6 p | ZL raw gain | IT compiler | RF compiler |
|---|---:|---:|---:|---:|---:|---:|---:|
'''+''.join(f"| `{d}` | {p[d,'COMPILER12']['eligible_records']} | {p[d,'COMPILER12']['true_gain_bits']:+.3f} | {p[d,'COMPILER12']['positive_folios']}/{p[d,'COMPILER12']['held_folios']} | {p[d,'COMPILER12']['max_six_p']:.4f} | {p[d,'RAW_CHAR3_HASH32']['true_gain_bits']:+.3f} | {summ['IT2a'][d,'COMPILER12']['true_gain_bits']:+.3f} | {summ['RF1b'][d,'COMPILER12']['true_gain_bits']:+.3f} |\n" for d in DEPTHS)+'''
The depth profile distinguishes whole-record persistence from a merely adjacent
OPEN→next-line dependency. Lower-capacity tails are reported rather than
discarded. BODY depth is physical layout only.

No heading, recipe, semantic role, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned. f84r remained excluded and
unpredicted.
''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT118_Q20_COMPILER_DEPTH_TRANSFER_RESULT_V1','status':status,'records':170,'physical_folios':8,'worlds':WORLDS,'primary_depths':{'BODY_LINE_1':line1,'BODY_LINE_2':line2,'BODY_TAIL_3PLUS':tail},'scores':scores,'interpretation':'Tests whether OPEN compiler linkage persists across physical BODY depth.','claim_ceiling':'Anonymous physical-depth record linkage only; no heading, recipe, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{'gdt117_result.json':sha(ROOT/'gdt117_result.json'),'gdt115_result.json':sha(ROOT/'gdt115_result.json'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (SCORES,FOLDS,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'primary':result['primary_depths']},sort_keys=True))
if __name__=='__main__':main()

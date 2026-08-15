#!/usr/bin/env python3
"""GDT119: exploratory held-folio star-morphology/compiler association."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g

ROOT=Path(__file__).resolve().parent;SME=ROOT/'experiments/semantic_assumptions/star_morphology_entry';BIND=SME/'target_source_binding.tsv';SOURCE=SME/'source_panel.tsv';MANIFEST=SME/'SOURCE_MANIFEST.tsv';METHOD=ROOT/'GDT119_Q20_VISUAL_COMPILER_ASSOCIATION_METHOD.md';REPORT=ROOT/'GDT119_Q20_VISUAL_COMPILER_ASSOCIATION_REPORT.md';INV=ROOT/'gdt119_q20_visual_compiler_inventory.tsv';SCORES=ROOT/'gdt119_q20_visual_compiler_scores.tsv';FOLDS=ROOT/'gdt119_q20_visual_compiler_folds.tsv';NULL=ROOT/'gdt119_q20_visual_compiler_null.tsv';COUNTER=ROOT/'gdt119_q20_visual_compiler_counterexamples.tsv';RESULT=ROOT/'gdt119_result.json';AXES=('RAYS_8_VS_7','TAIL_2_VS_1','COLOR_RED_VS_YEL');MODES=('OPEN_WRAPPER7','OPEN_COMPILER12','BODY_COMPILER12','OPEN_BODY_COMPILER24','RAW_RECORD_CHAR3_HASH32');LAM=10.;WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def yval(v,axis):
 if axis=='RAYS_8_VS_7':return 1 if v['rays']=='8' else 0 if v['rays']=='7' else None
 if axis=='TAIL_2_VS_1':return 1 if v['tail']=='2' else 0 if v['tail']=='1' else None
 return 1 if v['color']=='RED' else 0 if v['color']=='yel' else None
def avec(r,m):
 if m=='OPEN_WRAPPER7':return g.compiler_vec(r['open'])[:7]
 if m=='OPEN_COMPILER12':return g.compiler_vec(r['open'])
 if m=='BODY_COMPILER12':return g.compiler_vec(r['body'])
 if m=='OPEN_BODY_COMPILER24':return np.r_[g.compiler_vec(r['open']),g.compiler_vec(r['body'])]
 x=np.zeros(32)
 for q in r['open']+r['body']:
  for ng in g.ngrams(q['token']):x[g.hash32(ng)]+=1
 return x/max(1,x.sum())
def nuisance(records,ids):
 pc=Counter(records[i]['page'] for i in ids);out=[]
 for i in ids:
  r=records[i];n=pc[r['page']];out.append([r['star_ordinal']%2,r['star_ordinal']/n,n,r['page'].endswith('v'),r['record_line_count'],r['open_group_count'],r['open_member_count'],r['body_group_count'],r['body_member_count']])
 return np.asarray(out,float)
def sigmoid(z):return 1/(1+np.exp(-np.clip(z,-35,35)))
def logfit(X,y,lam=LAM):
 X=np.c_[np.ones(len(X)),X];b=np.zeros(X.shape[1]);pen=np.eye(X.shape[1]);pen[0,0]=0
 for _ in range(60):
  p=sigmoid(X@b);w=np.maximum(p*(1-p),1e-6);grad=X.T@(p-y)+lam*pen@b;H=X.T@(X*w[:,None])+lam*pen;step=np.linalg.solve(H,grad);b-=step
  if np.max(np.abs(step))<1e-9:break
 return b
def pred(X,b):return sigmoid(np.c_[np.ones(len(X)),X]@b)
def bits(y,p):return float(-np.sum(y*np.log2(np.maximum(p,1e-12))+(1-y)*np.log2(np.maximum(1-p,1e-12))))
def ap(y,p):
 order=np.argsort(-p);yy=y[order];tot=yy.sum()
 return float(sum((yy[:i+1].sum()/(i+1)) for i in range(len(yy)) if yy[i])/tot) if tot else 0.
def main():
 allr=g.load_records();bind={r['unit_id']:r for r in read(BIND)};src={(r['page'],r['star_ordinal']):r for r in read(SOURCE)};assert len(bind)==156 and not any(r['page'].startswith('f84r') for r in bind.values());joined={}
 for uid,b in bind.items():
  s=src[b['page'],b['star_ordinal']];assert s['locus']==b['locus'] and s['rays']==b['rays'] and s['tail']==b['tail'];joined[uid]={**b,'color':s['color'],'paint':s['paint'],'core':s['core'],'provenance':'EXISTING_HUMAN_ANNOTATION_STOLFI_STAR_PROPS'}
 inv=[];scores=[];foldout=[];nullout=[];counter=[];summ={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed and r['unit_id'] in joined];assert len(rec)==156;R={r['unit_id']:joined[r['unit_id']] for r in rec}
  for r in rec:
   v=R[r['unit_id']];inv.append({'unit_id':r['unit_id'],'edition':ed,'page':r['page'],'physical_folio':r['physical_folio'],'star_ordinal':r['star_ordinal'],'locus':v['locus'],'rays':v['rays'],'tail':v['tail'],'color':v['color'],'paint':v['paint'],'core':v['core'],'provenance':v['provenance'],'open_compiler_sha256':csha(g.compiler_vec(r['open']).tolist()),'body_compiler_sha256':csha(g.compiler_vec(r['body']).tolist()),'claim_state':'EXPLORATORY_VISUAL_FORMAL_JOIN'})
  models=[];true={}
  for axis in AXES:
   ids=[i for i,r in enumerate(rec) if yval(R[r['unit_id']],axis) is not None];Y=np.array([yval(R[rec[i]['unit_id']],axis) for i in ids],float);Xn=nuisance(rec,ids)
   for m in MODES:
    Xa=np.vstack([avec(rec[i],m) for i in ids]);fold=[];cache={}
    for held in sorted({rec[i]['physical_folio'] for i in ids}):
     tr=[j for j,i in enumerate(ids) if rec[i]['physical_folio']!=held];te=[j for j,i in enumerate(ids) if rec[i]['physical_folio']==held];xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);xatr,xate,amu,asd=g.standardize(Xa[tr],Xa[te]);b0=logfit(xntr,Y[tr]);p0=pred(xnte,b0);b=logfit(np.c_[xntr,xatr],Y[tr]);p=pred(np.c_[xnte,xate],b);gain=bits(Y[te],p0)-bits(Y[te],p);fold.append({'held_folio':held,'held_rows':len(te),'positives':int(Y[te].sum()),'gain_bits':gain,'brier_nuisance':float(np.mean((Y[te]-p0)**2)),'brier_model':float(np.mean((Y[te]-p)**2)),'ap_nuisance':ap(Y[te],p0),'ap_model':ap(Y[te],p)});cache[held]={'global_ids':[ids[j] for j in te],'y':Y[te],'p0':p0,'xn':xnte,'amu':amu,'asd':asd,'b':b}
    name=axis+'__'+m;models.append((name,axis,m,ids,cache,np.vstack([avec(r,m) for r in rec])));true[name]=sum(x['gain_bits'] for x in fold)
    for x in fold:foldout.append({'edition':ed,'axis':axis,'model':m,**x})
    for x in sorted(fold,key=lambda z:z['gain_bits'])[:2]:counter.append({'edition':ed,'axis':axis,'model':m,'held_folio':x['held_folio'],'gain_bits':x['gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
  world={n:[] for n,_,_,_,_,_ in models};rng=random.Random(g.seed('GDT119',ed))
  for _ in range(WORLDS):
   assign={}
   for axis in AXES:
    ids=next(x[3] for x in models if x[1]==axis);by=defaultdict(list)
    for i in ids:by[rec[i]['page']].append(i)
    a={i:i for i in ids}
    for ps in by.values():
     z=ps[:];rng.shuffle(z)
     for p,q in zip(ps,z):a[p]=q
    assign[axis]=a
   for name,axis,m,ids,cache,X in models:
    total=0.;a=assign[axis]
    for held,z in cache.items():
     raw=np.vstack([X[a[i]] for i in z['global_ids']]);xa=(raw-z['amu'])/z['asd'];p=pred(np.c_[z['xn'],xa],z['b']);total+=bits(z['y'],z['p0'])-bits(z['y'],p)
    world[name].append(total)
  mx=[max(world[n][q] for n in world) for q in range(WORLDS)]
  for name,axis,m,ids,cache,X in models:
   fs=[x for x in foldout if x['edition']==ed and x['axis']==axis and x['model']==m];t=true[name];row={'edition':ed,'axis':axis,'model':m,'rows':len(ids),'positives':sum(yval(R[rec[i]['unit_id']],axis) for i in ids),'held_folios':len(fs),'gain_bits':t,'selector_paid_gain_bits':t-math.log2(15),'positive_folios':sum(x['gain_bits']>0 for x in fs),'mean_brier_gain':sum((x['brier_nuisance']-x['brier_model'])*x['held_rows'] for x in fs)/len(ids),'mean_ap_gain':sum((x['ap_model']-x['ap_nuisance'])*x['held_rows'] for x in fs)/len(ids),'null_median_bits':float(np.median(world[name])),'local_p':(1+sum(x>=t-1e-12 for x in world[name]))/(WORLDS+1),'max_15_p':(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1)};scores.append(row);nullout.append({'edition':ed,'axis':axis,'model':m,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(world[name])),'null_median_bits':float(np.median(world[name])),'null_q95_bits':float(np.quantile(world[name],.95)),'local_p':row['local_p'],'max_15_p':row['max_15_p']})
  summ[ed]={(x['axis'],x['model']):x for x in scores if x['edition']==ed}
 zl=sorted([x for x in scores if x['edition']=='ZL3b'],key=lambda x:(-x['gain_bits'],x['axis'],x['model']));top=zl[0];supported=[x for x in zl if x['gain_bits']>0 and x['max_15_p']<=.05 and all(summ[e][x['axis'],x['model']]['gain_bits']>0 for e in g.EDITIONS)]
 status='Q20_VISUAL_STATE_COMPILER_ASSOCIATION_EXPLORATORY' if supported else 'Q20_VISUAL_STATE_NOT_PREDICTED_BY_RECORD_COMPILER'
 write(INV,inv);write(SCORES,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in scores]);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in foldout]);write(NULL,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in nullout]);write(COUNTER,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in counter])
 report=f'''# GDT119 — Q20 star morphology versus record compiler

Status: **{status}**

This is the first exploratory join of the archived SME human star observations
to the independently discovered Q20 compiler profiles. The previous SME
target-free calibration failure remains unchanged.

The strongest ZL3b axis/model is `{top['axis']} / {top['model']}` with
{top['gain_bits']:+.3f} held-folio bits, {top['positive_folios']}/{top['held_folios']}
positive folios, local p={top['local_p']:.4f}, max-15 p={top['max_15_p']:.4f}.
{len(supported)} candidates clear the exploratory corrected/directional gate.
Color is interpreted only as an alternating visible state and is strongly
ordinal-confounded.

No star state receives a meaning and no record class, heading, recipe, role,
word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r remained absent and unpredicted.
''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT119_Q20_VISUAL_COMPILER_ASSOCIATION_RESULT_V1','status':status,'joined_units':156,'physical_folios':7,'axes':list(AXES),'models':list(MODES),'worlds':WORLDS,'top_zl':top,'supported_candidates':supported,'scores':scores,'historical_sme_status':'FAIL_TARGET_FREE_NULL_AND_POWER_CALIBRATION; TARGET_JOIN_NOT_PREVIOUSLY_RUN','interpretation':'Exploratory reuse of archived human star morphology to localize possible external signal in Q20 record compiler profiles.','claim_ceiling':'Hypothesis-generation visual/formal association only; no star meaning, record meaning, heading, recipe, role, word, morpheme, POS, sound, language, plaintext or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{str(BIND.relative_to(ROOT)):sha(BIND),str(SOURCE.relative_to(ROOT)):sha(SOURCE),str(MANIFEST.relative_to(ROOT)):sha(MANIFEST),'gdt118_result.json':sha(ROOT/'gdt118_result.json'),'gdt117_result.json':sha(ROOT/'gdt117_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (INV,SCORES,FOLDS,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'top':top,'supported':supported},sort_keys=True))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""GDT122: held-folio PAGE_HOST association with archived Q20 star states."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g
import run_gdt119_q20_visual_compiler_association as v
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT122_Q20_PAGE_HOST_VISUAL_ASSOCIATION_METHOD.md';REPORT=ROOT/'GDT122_Q20_PAGE_HOST_VISUAL_ASSOCIATION_REPORT.md';INV=ROOT/'gdt122_q20_page_host_visual_inventory.tsv';FOLDS=ROOT/'gdt122_q20_page_host_visual_folds.tsv';SCORES=ROOT/'gdt122_q20_page_host_visual_scores.tsv';NULL=ROOT/'gdt122_q20_page_host_visual_null.tsv';COUNTER=ROOT/'gdt122_q20_page_host_visual_counterexamples.tsv';RESULT=ROOT/'gdt122_result.json';AXES=v.AXES;MODES=('OPEN_HOST_CHAR3_HASH32','BODY_HOST_CHAR3_HASH32','OPEN_BODY_HOST_CHAR3_HASH32','OPEN_COMPILER12','RAW_RECORD_CHAR3_HASH32');WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def hvec(groups,use_host):
 x=np.zeros(32)
 for q in groups:
  z=q['page_host'] if use_host else q['token']
  for ng in g.ngrams(z):x[g.hash32(ng)]+=1
 return x/max(1,x.sum())
def avec(r,m):
 if m=='OPEN_HOST_CHAR3_HASH32':return hvec(r['open'],True)
 if m=='BODY_HOST_CHAR3_HASH32':return hvec(r['body'],True)
 if m=='OPEN_BODY_HOST_CHAR3_HASH32':return hvec(r['open']+r['body'],True)
 if m=='OPEN_COMPILER12':return g.compiler_vec(r['open'])
 return hvec(r['open']+r['body'],False)
def main():
 allr=g.load_records();bind={r['unit_id']:r for r in read(v.BIND)};src={(r['page'],r['star_ordinal']):r for r in read(v.SOURCE)};assert len(bind)==156 and not any(r['page'].startswith('f84r') for r in bind.values());joined={}
 for uid,b in bind.items():
  s=src[b['page'],b['star_ordinal']];assert s['locus']==b['locus'];joined[uid]={**b,'color':s['color'],'paint':s['paint'],'core':s['core'],'provenance':'EXISTING_HUMAN_ANNOTATION_STOLFI_STAR_PROPS'}
 inv=[];foldout=[];scores=[];nullout=[];counter=[];summ={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed and r['unit_id'] in joined];assert len(rec)==156;R={r['unit_id']:joined[r['unit_id']] for r in rec}
  for r in rec:
   q=R[r['unit_id']];inv.append({'unit_id':r['unit_id'],'edition':ed,'page':r['page'],'physical_folio':r['physical_folio'],'star_ordinal':r['star_ordinal'],'locus':q['locus'],'rays':q['rays'],'tail':q['tail'],'color':q['color'],'provenance':q['provenance'],'open_host_sha256':csha([x['page_host'] for x in r['open']]),'body_host_sha256':csha([x['page_host'] for x in r['body']]),'claim_state':'EXPLORATORY_PAGE_HOST_VISUAL_JOIN'})
  models=[];true={}
  for axis in AXES:
   ids=[i for i,r in enumerate(rec) if v.yval(R[r['unit_id']],axis) is not None];Y=np.array([v.yval(R[rec[i]['unit_id']],axis) for i in ids],float);Xn=v.nuisance(rec,ids)
   for m in MODES:
    Xa=np.vstack([avec(rec[i],m) for i in ids]);fold=[];cache={}
    for held in sorted({rec[i]['physical_folio'] for i in ids}):
     tr=[j for j,i in enumerate(ids) if rec[i]['physical_folio']!=held];te=[j for j,i in enumerate(ids) if rec[i]['physical_folio']==held];xn,xnt,_,_=g.standardize(Xn[tr],Xn[te]);xa,xat,amu,asd=g.standardize(Xa[tr],Xa[te]);b0=v.logfit(xn,Y[tr]);p0=v.pred(xnt,b0);b=v.logfit(np.c_[xn,xa],Y[tr]);p=v.pred(np.c_[xnt,xat],b);gain=v.bits(Y[te],p0)-v.bits(Y[te],p);fold.append({'held_folio':held,'held_rows':len(te),'positives':int(Y[te].sum()),'gain_bits':gain,'brier_nuisance':float(np.mean((Y[te]-p0)**2)),'brier_model':float(np.mean((Y[te]-p)**2)),'ap_nuisance':v.ap(Y[te],p0),'ap_model':v.ap(Y[te],p)});cache[held]={'global_ids':[ids[j] for j in te],'y':Y[te],'p0':p0,'xn':xnt,'amu':amu,'asd':asd,'b':b}
    name=axis+'__'+m;models.append((name,axis,m,ids,cache,np.vstack([avec(r,m) for r in rec])));true[name]=sum(x['gain_bits'] for x in fold)
    for x in fold:foldout.append({'edition':ed,'axis':axis,'model':m,**x})
    for x in sorted(fold,key=lambda q:q['gain_bits'])[:2]:counter.append({'edition':ed,'axis':axis,'model':m,'held_folio':x['held_folio'],'gain_bits':x['gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
  world={x[0]:[] for x in models};rng=random.Random(g.seed('GDT122_NULL',ed));capacity={}
  for _ in range(WORLDS):
   assign={}
   for axis in AXES:
    ids=next(x[3] for x in models if x[1]==axis);by=defaultdict(list)
    for i in ids:by[rec[i]['page'],rec[i]['open_member_count']].append(i)
    a={i:i for i in ids};capacity[axis]=sum(len(ps) for ps in by.values() if len(ps)>1)
    for ps in by.values():
     if len(ps)>1:
      z=ps[:];rng.shuffle(z)
      for p,q in zip(ps,z):a[p]=q
    assign[axis]=a
   for name,axis,m,ids,cache,X in models:
    total=0.;a=assign[axis]
    for held,z in cache.items():
     raw=np.vstack([X[a[i]] for i in z['global_ids']]);xa=(raw-z['amu'])/z['asd'];p=v.pred(np.c_[z['xn'],xa],z['b']);total+=v.bits(z['y'],z['p0'])-v.bits(z['y'],p)
    world[name].append(total)
  mx=[max(world[name][q] for name in world) for q in range(WORLDS)]
  for name,axis,m,ids,cache,X in models:
   fs=[x for x in foldout if x['edition']==ed and x['axis']==axis and x['model']==m];t=true[name];w=world[name];row={'edition':ed,'axis':axis,'model':m,'rows':len(ids),'positives':sum(v.yval(R[rec[i]['unit_id']],axis) for i in ids),'held_folios':len(fs),'swappable_rows':capacity[axis],'gain_bits':t,'selector_paid_gain_bits':t-math.log2(15),'positive_folios':sum(x['gain_bits']>0 for x in fs),'mean_brier_gain':sum((x['brier_nuisance']-x['brier_model'])*x['held_rows'] for x in fs)/len(ids),'mean_ap_gain':sum((x['ap_model']-x['ap_nuisance'])*x['held_rows'] for x in fs)/len(ids),'null_median_bits':float(np.median(w)),'local_p':(1+sum(x>=t-1e-12 for x in w))/(WORLDS+1),'max_15_p':(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1)};scores.append(row);summ[ed,axis,m]=row;nullout.append({'edition':ed,'axis':axis,'model':m,'worlds':WORLDS,'true_gain_bits':t,'swappable_rows':capacity[axis],'null_mean_bits':float(np.mean(w)),'null_median_bits':float(np.median(w)),'null_q95_bits':float(np.quantile(w,.95)),'local_p':row['local_p'],'max_15_p':row['max_15_p']})
 zl=sorted([x for x in scores if x['edition']=='ZL3b'],key=lambda x:(-x['gain_bits'],x['axis'],x['model']));top=zl[0];hosts=[x for x in zl if 'HOST_CHAR3' in x['model']];best=max(hosts,key=lambda x:(x['gain_bits'],x['axis'],x['model']));gates={'selector_paid_positive':best['selector_paid_gain_bits']>0,'max_15_p_le_005':best['max_15_p']<=.05,'five_of_seven_positive':best['positive_folios']>=5,'all_readings_positive':all(summ[e,best['axis'],best['model']]['gain_bits']>0 for e in g.EDITIONS),'beats_compiler_and_raw':best['gain_bits']>max(summ['ZL3b',best['axis'],'OPEN_COMPILER12']['gain_bits'],summ['ZL3b',best['axis'],'RAW_RECORD_CHAR3_HASH32']['gain_bits'])};status='Q20_PAGE_HOST_VISUAL_ASSOCIATION_EXPLORATORY' if all(gates.values()) else 'Q20_PAGE_HOST_DOES_NOT_RECOVER_STAR_VISUAL_SIGNAL'
 def fmt(z):return [{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in z]
 write(INV,fmt(inv));write(FOLDS,fmt(foldout));write(SCORES,fmt(scores));write(NULL,fmt(nullout));write(COUNTER,fmt(counter))
 report=f'''# GDT122 — Q20 PAGE_HOST versus archived visual states\n\nStatus: **{status}**\n\nThe strongest PAGE_HOST result is `{best['axis']} / {best['model']}` at {best['gain_bits']:+.3f} held-folio bits, selector-paid {best['selector_paid_gain_bits']:+.3f}, {best['positive_folios']}/7 positive folios, local/max-15 p={best['local_p']:.4f}/{best['max_15_p']:.4f}. The strongest result of any layer is `{top['axis']} / {top['model']}` at {top['gain_bits']:+.3f} bits. Registered gates: `{json.dumps(gates,sort_keys=True)}`.\n\n| axis | best PAGE_HOST model | host gain | max-15 p | compiler gain | raw gain |\n|---|---|---:|---:|---:|---:|\n'''+''.join(f"| `{a}` | `{max([summ['ZL3b',a,m] for m in MODES if 'HOST_CHAR3' in m],key=lambda x:x['gain_bits'])['model']}` | {max([summ['ZL3b',a,m] for m in MODES if 'HOST_CHAR3' in m],key=lambda x:x['gain_bits'])['gain_bits']:+.3f} | {max([summ['ZL3b',a,m] for m in MODES if 'HOST_CHAR3' in m],key=lambda x:x['gain_bits'])['max_15_p']:.4f} | {summ['ZL3b',a,'OPEN_COMPILER12']['gain_bits']:+.3f} | {summ['ZL3b',a,'RAW_RECORD_CHAR3_HASH32']['gain_bits']:+.3f} |\n" for a in AXES)+'''\nStripping HPR2 compiler layers does not by itself license any visual or semantic reading. The SME calibration failure and GDT119 negative remain binding. No star state or PAGE_HOST receives a meaning; no word, morpheme, POS, sound, language, plaintext, meaning, or translation is assigned. f84r remained fully excluded and unpredicted.\n''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT122_Q20_PAGE_HOST_VISUAL_ASSOCIATION_RESULT_V1','status':status,'joined_units':156,'physical_folios':7,'axes':list(AXES),'models':list(MODES),'worlds':WORLDS,'top_any':top,'best_page_host':best,'gates':gates,'scores':scores,'historical_sme_status':'FAIL_TARGET_FREE_NULL_AND_POWER_CALIBRATION','interpretation':'Held-folio localization of archived Q20 star-state association in PAGE_HOST-only versus compiler/raw representations.','claim_ceiling':'Exploratory PAGE_HOST/visual association only; no star or PAGE_HOST meaning, word, morpheme, POS, sound, language, plaintext or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'assigned':False,'predicted':False},'inputs':{'gdt119_result.json':sha(ROOT/'gdt119_result.json'),str(v.BIND.relative_to(ROOT)):sha(v.BIND),str(v.SOURCE.relative_to(ROOT)):sha(v.SOURCE),str(v.MANIFEST.relative_to(ROOT)):sha(v.MANIFEST)},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py'),'run_gdt119_q20_visual_compiler_association.py':sha(ROOT/'run_gdt119_q20_visual_compiler_association.py')},'outputs':{x.name:sha(x) for x in (INV,FOLDS,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'best':best,'top':top,'gates':gates},sort_keys=True))
if __name__=='__main__':main()

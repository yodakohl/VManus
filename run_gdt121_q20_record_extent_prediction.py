#!/usr/bin/env python3
"""GDT121: nested held-folio OPEN prediction of Q20 BODY extent."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT121_Q20_RECORD_EXTENT_PREDICTION_METHOD.md';REPORT=ROOT/'GDT121_Q20_RECORD_EXTENT_PREDICTION_REPORT.md';PRED=ROOT/'gdt121_q20_record_extent_predictions.tsv';FOLDS=ROOT/'gdt121_q20_record_extent_folds.tsv';SCORES=ROOT/'gdt121_q20_record_extent_scores.tsv';NULL=ROOT/'gdt121_q20_record_extent_null.tsv';COUNTER=ROOT/'gdt121_q20_record_extent_counterexamples.tsv';RESULT=ROOT/'gdt121_result.json';MODES=('OPEN_WRAPPER7','OPEN_COMPILER12','OPEN_EDGE29','RAW_OPEN_CHAR3_HASH32','HOST_OPEN_CHAR3_HASH32');LAM=1000.;WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def seed(*x):return int(hashlib.sha256('|'.join(map(str,x)).encode()).hexdigest()[:16],16)
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def target(r):return np.array([r['body_line_count'],r['body_group_count'],r['body_member_count'],r['body_group_count']/r['body_line_count'],r['body_member_count']/r['body_group_count']],float)
def add(r,m):
 if m=='OPEN_WRAPPER7':return g.compiler_vec(r['open'])[:7]
 if m=='OPEN_COMPILER12':return g.compiler_vec(r['open'])
 if m=='OPEN_EDGE29':return g.edge_vec(r['open'])
 return g.hash_vec(r['open'],m=='HOST_OPEN_CHAR3_HASH32')
def nuisance(rec):
 pc=Counter(r['page'] for r in rec);Y=np.vstack([target(r) for r in rec]);out=[]
 for i,r in enumerate(rec):
  ids=[j for j,z in enumerate(rec) if j!=i and z['page']==r['page']];pm=Y[ids].mean(0) if ids else np.zeros(5)
  out.append(np.r_[[float(r['page'].endswith('v')),r['star_ordinal']/pc[r['page']],pc[r['page']],r['open_group_count'],r['open_member_count']],pm])
 return np.vstack(out)
def fit(rec,m,held):
 tr=[i for i,r in enumerate(rec) if r['physical_folio']!=held];te=[i for i,r in enumerate(rec) if r['physical_folio']==held];Xn=nuisance(rec);A=np.vstack([add(r,m) for r in rec]);Y=np.vstack([target(r) for r in rec]);xn,xnt,_,_=g.standardize(Xn[tr],Xn[te]);xa,xat,amu,asd=g.standardize(A[tr],A[te]);y,yt,ymu,ysd=g.standardize(Y[tr],Y[te]);b0=g.ridge_fit(xn,y,LAM);p0=g.ridge_pred(xnt,b0);b=g.ridge_fit(np.c_[xn,xa],y,LAM);p=g.ridge_pred(np.c_[xnt,xat],b)
 return {'tr':tr,'te':te,'A':A,'amu':amu,'asd':asd,'xnt':xnt,'yt':yt,'ymu':ymu,'ysd':ysd,'b':b,'p0':p0,'p':p,'gain':g.pseudo_bits(yt,p0,p)}
def main():
 allr=g.load_records();pred=[];foldout=[];scoreout=[];nullout=[];counter=[];summ={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];folios=sorted({r['physical_folio'] for r in rec});cache={(m,h):fit(rec,m,h) for m in MODES for h in folios}
  for m in MODES:
   for h in folios:
    z=cache[m,h];foldout.append({'edition':ed,'model':m,'held_folio':h,'held_records':len(z['te']),'pseudo_gain_bits':z['gain'],'positive_gain':int(z['gain']>0)})
    for pos,i in enumerate(z['te']):
     actual=target(rec[i]);base=z['p0'][pos]*z['ysd']+z['ymu'];model=z['p'][pos]*z['ysd']+z['ymu'];pred.append({'edition':ed,'model':m,'held_folio':h,'unit_id':rec[i]['unit_id'],'page':rec[i]['page'],'actual_body_lines':actual[0],'pred_body_lines_nuisance':base[0],'pred_body_lines_model':model[0],'actual_body_groups':actual[1],'pred_body_groups_nuisance':base[1],'pred_body_groups_model':model[1],'actual_body_members':actual[2],'pred_body_members_nuisance':base[2],'pred_body_members_model':model[2]})
  strata={}
  for h in folios:
   te=cache[MODES[0],h]['te'];d=defaultdict(list)
   for pos,i in enumerate(te):d[rec[i]['page'],rec[i]['open_member_count']].append(pos)
   strata[h]=d
  rng=random.Random(seed('GDT121_NULL',ed));world={m:[] for m in MODES}
  for _ in range(WORLDS):
   assigns={}
   for h,d in strata.items():
    a=list(range(len(cache[MODES[0],h]['te'])))
    for ps in d.values():
     if len(ps)>1:
      q=ps[:];rng.shuffle(q)
      for x,y in zip(ps,q):a[x]=y
    assigns[h]=a
   for m in MODES:
    total=0.
    for h in folios:
     z=cache[m,h];raw=z['A'][z['te']][assigns[h]];xa=(raw-z['amu'])/z['asd'];p=g.ridge_pred(np.c_[z['xnt'],xa],z['b']);total+=g.pseudo_bits(z['yt'],z['p0'],p)
    world[m].append(total)
  mx=[max(world[m][q] for m in MODES) for q in range(WORLDS)]
  summ[ed]={}
  for m in MODES:
   fs=[x for x in foldout if x['edition']==ed and x['model']==m];t=sum(x['pseudo_gain_bits'] for x in fs);w=world[m];ps=[x for x in pred if x['edition']==ed and x['model']==m];mae0=sum(abs(float(x['actual_body_groups'])-float(x['pred_body_groups_nuisance'])) for x in ps)/170;mae1=sum(abs(float(x['actual_body_groups'])-float(x['pred_body_groups_model'])) for x in ps)/170
   row={'edition':ed,'model':m,'records':170,'held_folios':8,'pseudo_gain_bits':t,'selector_paid_gain_bits':t-math.log2(5),'positive_folios':sum(x['pseudo_gain_bits']>0 for x in fs),'body_group_mae_nuisance':mae0,'body_group_mae_model':mae1,'local_p':(1+sum(x>=t-1e-12 for x in w))/(WORLDS+1),'max_five_p':(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1),'null_median_bits':float(np.median(w))};scoreout.append(row);summ[ed][m]=row;nullout.append({'edition':ed,'model':m,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(w)),'null_median_bits':float(np.median(w)),'null_q95_bits':float(np.quantile(w,.95)),'local_p':row['local_p'],'max_five_p':row['max_five_p']})
   for x in sorted(fs,key=lambda q:q['pseudo_gain_bits'])[:3]:counter.append({'edition':ed,'model':m,'held_folio':x['held_folio'],'pseudo_gain_bits':x['pseudo_gain_bits'],'counterexample':'WEAKEST_HELD_FOLIO'})
 p=summ['ZL3b']['OPEN_COMPILER12'];gates={'selector_paid_positive':p['selector_paid_gain_bits']>0,'max_five_p_le_005':p['max_five_p']<=.05,'six_of_eight_positive':p['positive_folios']>=6,'all_readings_positive':all(summ[e]['OPEN_COMPILER12']['pseudo_gain_bits']>0 for e in g.EDITIONS),'beats_string_controls':p['pseudo_gain_bits']>max(summ['ZL3b']['RAW_OPEN_CHAR3_HASH32']['pseudo_gain_bits'],summ['ZL3b']['HOST_OPEN_CHAR3_HASH32']['pseudo_gain_bits'])};status='Q20_OPEN_COMPILER_PREDICTS_BODY_EXTENT' if all(gates.values()) else 'Q20_BODY_EXTENT_SIGNAL_WEAK_OR_STRING_LIKE' if p['pseudo_gain_bits']>0 else 'Q20_OPEN_COMPILER_DOES_NOT_PREDICT_BODY_EXTENT'
 def fmt(z):return [{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in z]
 write(PRED,fmt(pred));write(FOLDS,fmt(foldout));write(SCORES,fmt(scoreout));write(NULL,fmt(nullout));write(COUNTER,fmt(counter))
 report=f'''# GDT121 — Q20 OPEN prediction of BODY extent\n\nStatus: **{status}**\n\nThe OPEN compiler predicts five held-folio BODY extent measures by {p['pseudo_gain_bits']:+.3f} standardized Gaussian pseudo-bits in ZL3b, selector-paid {p['selector_paid_gain_bits']:+.3f}, on {p['positive_folios']}/8 positive folios; local/max-five p={p['local_p']:.4f}/{p['max_five_p']:.4f}. IT2a/RF1b gains are {summ['IT2a']['OPEN_COMPILER12']['pseudo_gain_bits']:+.3f}/{summ['RF1b']['OPEN_COMPILER12']['pseudo_gain_bits']:+.3f}. BODY-group MAE changes from {p['body_group_mae_nuisance']:.3f} to {p['body_group_mae_model']:.3f}. Gates: `{json.dumps(gates,sort_keys=True)}`.\n\n| model | ZL gain | selector-paid | positive folios | max-five p | BODY-group MAE |\n|---|---:|---:|---:|---:|---:|\n'''+''.join(f"| `{m}` | {summ['ZL3b'][m]['pseudo_gain_bits']:+.3f} | {summ['ZL3b'][m]['selector_paid_gain_bits']:+.3f} | {summ['ZL3b'][m]['positive_folios']}/8 | {summ['ZL3b'][m]['max_five_p']:.4f} | {summ['ZL3b'][m]['body_group_mae_model']:.3f} |\n" for m in MODES)+'''\nThis test concerns aggregate record extent only. It does not assign a count value to any unit or establish that OPEN is a heading. No number value, recipe, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation is inferred. f84r remained fully excluded and unpredicted.\n''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT121_Q20_RECORD_EXTENT_PREDICTION_RESULT_V1','status':status,'records':170,'physical_folios':8,'targets':['BODY_LINES','BODY_GROUPS','BODY_MEMBERS','GROUPS_PER_LINE','MEMBERS_PER_GROUP'],'models':list(MODES),'worlds':WORLDS,'primary':p,'gates':gates,'scores':scoreout,'interpretation':'Nested held-folio test of whether OPEN formal profiles predict BODY structural extent beyond page ecology and OPEN length.','claim_ceiling':'Aggregate record extent only; no number value, heading, recipe, semantic role, word, morpheme, POS, sound, language, plaintext, meaning or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'assigned':False,'predicted':False},'inputs':{'gdt115_result.json':sha(ROOT/'gdt115_result.json'),'gdt117_result.json':sha(ROOT/'gdt117_result.json'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (PRED,FOLDS,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'primary':p,'gates':gates},sort_keys=True))
if __name__=='__main__':main()

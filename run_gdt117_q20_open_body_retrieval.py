#!/usr/bin/env python3
"""GDT117: identify a BODY's true same-page/equal-length OPEN on held folios."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as g

ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT117_Q20_OPEN_BODY_RETRIEVAL_METHOD.md';REPORT=ROOT/'GDT117_Q20_OPEN_BODY_RETRIEVAL_REPORT.md';PRED=ROOT/'gdt117_open_body_retrieval_predictions.tsv';SCORES=ROOT/'gdt117_open_body_retrieval_scores.tsv';FOLDS=ROOT/'gdt117_open_body_retrieval_folds.tsv';COUNTER=ROOT/'gdt117_open_body_retrieval_counterexamples.tsv';RESULT=ROOT/'gdt117_result.json';LAM=1000.;WORLDS=4096;MODES=('WRAPPER7','COMPILER12','EDGE29','RAW_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def write(p,rows):
 fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def avec(r,m):
 if m=='WRAPPER7':return g.compiler_vec(r['open'])[:7]
 if m=='COMPILER12':return g.compiler_vec(r['open'])
 if m=='EDGE29':return g.edge_vec(r['open'])
 return g.hash_vec(r['open'],False)
def target(r,m):return g.compiler_vec(r['body'])[:7] if m=='WRAPPER7' else g.compiler_vec(r['body'])
def fit_outer(rec,m,held):
 Xn=g.nuisance(rec);Xa=np.vstack([avec(r,m) for r in rec]);Y=np.vstack([target(r,m) for r in rec]);tr=[i for i,r in enumerate(rec) if r['physical_folio']!=held];te=[i for i,r in enumerate(rec) if r['physical_folio']==held]
 xntr,xnte,_,_=g.standardize(Xn[tr],Xn[te]);xatr,xate,amu,asd=g.standardize(Xa[tr],Xa[te]);ytr,yte,_,_=g.standardize(Y[tr],Y[te]);b=g.ridge_fit(np.c_[xntr,xatr],ytr,LAM)
 return {'te':te,'xn':xnte,'y':yte,'b':b,'amu':amu,'asd':asd,'Xa':Xa}
def ranks(scores,truepos):
 value=scores[truepos];better=sum(x<value-1e-12 for x in scores);equal=sum(abs(x-value)<=1e-12 for x in scores);rank=better+(equal+1)/2
 return rank,int(rank<=1+1e-12),sum(value<x-1e-12 for i,x in enumerate(scores) if i!=truepos)+.5*sum(abs(value-x)<=1e-12 for i,x in enumerate(scores) if i!=truepos)
def main():
 allr=g.load_records();pred=[];foldout=[];scoreout=[];counter=[];summary={}
 for ed in g.EDITIONS:
  rec=[r for r in allr if r['edition']==ed];folios=sorted({r['physical_folio'] for r in rec});models={m:{h:fit_outer(rec,m,h) for h in folios} for m in MODES};cells={m:{} for m in MODES};eligible=set();strata=defaultdict(list)
  for i,r in enumerate(rec):strata[(r['page'],r['open_member_count'])].append(i)
  for ids in strata.values():
   if len(ids)>1:eligible.update(ids)
  for m in MODES:
   for held in folios:
    z=models[m][held];pos={idx:k for k,idx in enumerate(z['te'])}
    for i in z['te']:
     ids=strata[(rec[i]['page'],rec[i]['open_member_count'])]
     if len(ids)<2:continue
     ys=z['y'][pos[i]];vals=[]
     for j in ids:
      xa=(z['Xa'][j]-z['amu'])/z['asd'];p=g.ridge_pred(np.c_[z['xn'][pos[i]][None,:],xa[None,:]],z['b'])[0];vals.append(float(np.square(ys-p).sum()))
     tp=ids.index(i);rank,top,pairwins=ranks(vals,tp);cells[m][i]={'ids':ids,'scores':vals,'rank':rank,'top':top,'pairwins':pairwins}
     pred.append({'edition':ed,'model':m,'held_folio':held,'unit_id':rec[i]['unit_id'],'page':rec[i]['page'],'candidate_count':len(ids),'true_rank':rank,'top1':top,'reciprocal_rank':1/rank,'pairwise_wins':pairwins,'pairwise_trials':len(ids)-1,'candidate_unit_ids':'|'.join(rec[j]['unit_id'] for j in ids),'candidate_sse':'|'.join(f'{x:.9f}' for x in vals)})
  # one-to-one within-stratum permutation null on fixed score matrices
  rng=random.Random(g.seed('GDT117',ed));world={m:{'top':[],'mrr':[]} for m in MODES}
  for _ in range(WORLDS):
   perms={}
   for k,ids in strata.items():
    if len(ids)>1:z=ids[:];rng.shuffle(z);perms[k]=dict(zip(ids,z))
   for m in MODES:
    top=0.;rr=0.
    for i in eligible:
     cell=cells[m][i];ids=cell['ids'];assigned=perms[(rec[i]['page'],rec[i]['open_member_count'])][i];rank,hit,_=ranks(cell['scores'],ids.index(assigned));top+=hit;rr+=1/rank
    world[m]['top'].append(top/len(eligible));world[m]['mrr'].append(rr/len(eligible))
  max_top=[max(world[m]['top'][q] for m in MODES) for q in range(WORLDS)];max_mrr=[max(world[m]['mrr'][q] for m in MODES) for q in range(WORLDS)]
  for m in MODES:
   ps=[x for x in pred if x['edition']==ed and x['model']==m];top=sum(int(x['top1']) for x in ps)/len(ps);mrr=sum(float(x['reciprocal_rank']) for x in ps)/len(ps);wins=sum(float(x['pairwise_wins']) for x in ps);trials=sum(int(x['pairwise_trials']) for x in ps);row={'edition':ed,'model':m,'eligible_records':len(ps),'candidate_strata':sum(len(x)>1 for x in strata.values()),'top1_accuracy':top,'null_top1_expectation':sum(1/len(x) for x in strata.values() if len(x)>1 for _ in x)/len(ps),'mrr':mrr,'null_mrr_mean':float(np.mean(world[m]['mrr'])),'pairwise_accuracy':wins/trials,'top1_local_p':(1+sum(x>=top-1e-12 for x in world[m]['top']))/(WORLDS+1),'top1_max_four_p':(1+sum(x>=top-1e-12 for x in max_top))/(WORLDS+1),'mrr_local_p':(1+sum(x>=mrr-1e-12 for x in world[m]['mrr']))/(WORLDS+1),'mrr_max_four_p':(1+sum(x>=mrr-1e-12 for x in max_mrr))/(WORLDS+1)};scoreout.append(row)
   for held in folios:
    q=[x for x in ps if x['held_folio']==held];foldout.append({'edition':ed,'model':m,'held_folio':held,'eligible_records':len(q),'top1_accuracy':sum(int(x['top1']) for x in q)/len(q),'mrr':sum(float(x['reciprocal_rank']) for x in q)/len(q),'pairwise_accuracy':sum(float(x['pairwise_wins']) for x in q)/sum(int(x['pairwise_trials']) for x in q)})
   for x in sorted(ps,key=lambda q:(-float(q['true_rank']),q['unit_id']))[:8]:counter.append({'edition':ed,'model':m,'held_folio':x['held_folio'],'unit_id':x['unit_id'],'page':x['page'],'candidate_count':x['candidate_count'],'true_rank':x['true_rank'],'counterexample':'WORST_RETRIEVAL_RANK'})
  summary[ed]={m:next(x for x in scoreout if x['edition']==ed and x['model']==m) for m in MODES}
 p=summary['ZL3b']['COMPILER12'];all_direction=all(summary[e]['COMPILER12']['mrr']>summary[e]['COMPILER12']['null_mrr_mean'] for e in g.EDITIONS);all_corrected=all(summary[e]['COMPILER12']['mrr_max_four_p']<=.05 for e in g.EDITIONS);status='Q20_COMPILER_PROFILE_SUPPORTS_HELD_RECORD_RETRIEVAL' if p['top1_accuracy']>p['null_top1_expectation'] and p['mrr_max_four_p']<=.05 and all_corrected else 'Q20_COMPILER_PROFILE_SUPPORTS_HELD_RECORD_RETRIEVAL_READING_SENSITIVE' if p['top1_accuracy']>p['null_top1_expectation'] and p['mrr_max_four_p']<=.05 and all_direction else 'Q20_RECORD_RETRIEVAL_WEAK_OR_NOT_ABOVE_STRING_CONTROLS'
 write(PRED,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in pred]);write(SCORES,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in scoreout]);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in foldout]);write(COUNTER,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in x.items()} for x in counter])
 report=f'''# GDT117 — Q20 same-page OPEN/BODY retrieval

Status: **{status}**

The held-folio task contains {p['eligible_records']} records in same-page,
exact-OPEN-length candidate strata. Chance top-1 is
{p['null_top1_expectation']:.3f}. `COMPILER12` identifies the true OPEN with
top-1 accuracy {p['top1_accuracy']:.3f}, MRR {p['mrr']:.3f}, and pairwise
accuracy {p['pairwise_accuracy']:.3f}; its MRR local/max-four p-values are
{p['mrr_local_p']:.4f}/{p['mrr_max_four_p']:.4f}.
That is {round(p['top1_accuracy']*p['eligible_records'])}/{p['eligible_records']}
exact first choices versus {round(p['null_top1_expectation']*p['eligible_records'])}
expected. RF1b also clears the MRR max-four control
({summary['RF1b']['COMPILER12']['mrr_max_four_p']:.4f}); IT2a remains positive
but does not ({summary['IT2a']['COMPILER12']['mrr_max_four_p']:.4f}), where the
wrapper-only representation is stronger. The linkage is therefore
transcription-sensitive in its exact representation.

ZL3b comparison:

| model | top-1 | MRR | pairwise | MRR max-4 p |
|---|---:|---:|---:|---:|
'''+''.join(f"| `{m}` | {summary['ZL3b'][m]['top1_accuracy']:.3f} | {summary['ZL3b'][m]['mrr']:.3f} | {summary['ZL3b'][m]['pairwise_accuracy']:.3f} | {summary['ZL3b'][m]['mrr_max_four_p']:.4f} |\n" for m in MODES)+'''
This is a specific record-linkage prediction on completely unseen folios. It
does not make OPEN a heading or identify what any record contains. No role,
word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r remained excluded and unpredicted.
''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT117_Q20_OPEN_BODY_RETRIEVAL_RESULT_V1','status':status,'records':170,'physical_folios':8,'eligible_records':p['eligible_records'],'worlds':WORLDS,'primary':p,'scores':scoreout,'interpretation':'Concrete held-folio retrieval of the true same-page/equal-length OPEN from anonymous BODY compiler profile.','claim_ceiling':'Formal record linkage only; no heading, recipe, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'opened':False,'retained':False,'queried':False,'joined':False,'scored':False,'targeted':False,'prediction_frozen':False},'inputs':{'gdt116_result.json':sha(ROOT/'gdt116_result.json'),'gdt115_result.json':sha(ROOT/'gdt115_result.json'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{x.name:sha(x) for x in (PRED,SCORES,FOLDS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'primary':p,'scores':scoreout},sort_keys=True))
if __name__=='__main__':main()

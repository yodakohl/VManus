#!/usr/bin/env python3
"""Independently refit GDT326 and validate retained-null arithmetic and hashes."""
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;RESULT=R/'gdt326_result.json';OUT=R/'gdt326_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b,t=4e-9):return abs(float(a)-float(b))<=t
def norm(v):
 v=np.array(v,float);return v/v.sum()
def cid(c):return hashlib.sha256(('COORD|'+'|'.join(c)).encode()).hexdigest()[:20]
def main():
 checks=[]
 def check(n,c):
  if not c:raise AssertionError(n)
  checks.append(n)
 res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');check('result_content',stored==can(res));d=json.loads((R/'gdt326_design.json').read_text());ds=d.pop('content_sha256');check('design_content',ds==can(d));C=tuple(d['coordinate_fields']);rows=[x for x in read('gdt278_native_event_inventory.tsv') if x['control_id']=='VOYNICH_REFERENCE'];check('f84_source',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));byid={hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20]:x for x in rows};panel=read('gdt326_frozen_panel.tsv');check('panel',len(panel)==315 and len({x['physical_folio'] for x in panel})==76);pred={x['event_id_sha256']:x for x in read('gdt326_predictions.tsv')};models=d['models'];bits={m:[] for m in models};byfolio=defaultdict(list)
 for i,target in enumerate(panel):
  source=byid[target['event_id_sha256']];training=[x for x in rows if x['physical_folio']!=target['physical_folio']];universe=sorted({tuple(x[k] for k in C) for x in training});ui={v:j for j,v in enumerate(universe)};actual=tuple(source[k] for k in C);global_counts=np.full(len(universe),d['alpha']);register_counts=np.full(len(universe),d['alpha']);host_counts=np.full(len(universe),d['alpha']);hostrows=[]
  for x in training:
   c=tuple(x[k] for k in C);global_counts[ui[c]]+=1
   if x['register']==source['register']:register_counts[ui[c]]+=1
   if x['page_host']==source['page_host']:host_counts[ui[c]]+=1;hostrows.append(x)
  pg=norm(global_counts);pr=norm(register_counts);ph=norm(host_counts);component=[]
  for k in C:
   values=sorted({x[k] for x in training});count=Counter(x[k] for x in hostrows);den=len(hostrows)+d['alpha']*len(values);component.append({v:(count[v]+d['alpha'])/den for v in values})
  pf=norm([np.prod([component[j][c[j]] for j in range(len(C))]) for c in universe]);lp=np.log(pf)+np.log(pr)-np.log(pg);pfr=norm(np.exp(lp-lp.max()));vectors={'REGISTER_TABLE':pr,'HOST_TABLE':ph,'HOST_FACTORIAL':pf,'HOST_FACTORIAL_REGISTER':pfr};storedpred=pred[target['event_id_sha256']];check(f'coord_{i}',storedpred['observed_coordinate_id']==cid(actual))
  for m in models:
   b=-np.log2(max(vectors[m][ui[actual]],1e-15));bits[m].append(b);check(f'bits_{i}_{m}',close(b,storedpred[f'{m}_bits']))
  byfolio[target['physical_folio']].append(i)
 bits={m:np.array(v) for m,v in bits.items()};folds=read('gdt326_folio_scores.tsv');fm={(x['physical_folio'],x['model']):x for x in folds};observed={}
 for m in models:
  gains=[]
  for folio,idx in sorted(byfolio.items()):
   value=float(np.mean(bits[m][idx]));gain=float(np.mean(bits['REGISTER_TABLE'][idx])-value);gains.append(gain);row=fm[(folio,m)];check(f'fold_{folio}_{m}',close(value,row['bits_per_event']) and close(gain,row['gain_vs_register']))
  observed[m]={'folio_bits':float(np.mean([np.mean(bits[m][idx]) for idx in byfolio.values()])),'gain':sum(gains),'event_bits':float(bits[m].mean()),'event_gain':float(np.sum(bits['REGISTER_TABLE']-bits[m])),'positive':sum(x>0 for x in gains)}
 modelrows={x['model']:x for x in read('gdt326_model_scores.tsv')}
 for m in models:check(f'model_{m}',close(observed[m]['folio_bits'],modelrows[m]['folio_balanced_bits_per_event']) and close(observed[m]['gain'],modelrows[m]['folio_equivalent_gain_bits']) and close(observed[m]['event_bits'],modelrows[m]['event_weighted_bits_per_event']) and close(observed[m]['event_gain'],modelrows[m]['event_weighted_gain_bits']) and observed[m]['positive']==int(modelrows[m]['positive_folios']))
 null=read('gdt326_null.tsv');check('null_shape',len(null)==8192 and null[0]['world_index']=='0' and null[-1]['world_index']=='8191');maxima=[]
 for i,row in enumerate(null):
  values=[float(row[m]) for m in models];maximum=max(values);maxima.append(maximum);check(f'null_max_{i}',close(maximum,row['max_four_folio_equivalent_gain_bits']))
 for m in models:check(f'p_{m}',close((1+sum(x>=observed[m]['gain']-1e-15 for x in maxima))/8193,modelrows[m]['max_four_diagnostic_p']))
 check('decision',res['status']=='HOST_COORDINATE_TUPLE_REMAINS_LEXICALIZED');check('inputs',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));check('docs',all(res['documents'][n]==sha(R/n) for n in res['documents']));check('impl',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));check('outputs',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));check('f84_result',res['f84']['input_rows']==0 and not any(v for k,v in res['f84'].items() if k!='input_rows'));v={'schema':'GDT326_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_SOURCE_MODEL_REFIT_ALL_PREDICTIONS_FOLDS_RETAINED_NULL_ARITHMETIC_DECISION_AND_HASHES','checks_passed':len(checks),'result_sha256':sha(RESULT),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

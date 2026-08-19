#!/usr/bin/env python3
"""Independent source/accounting validator for GDT348 retained outputs."""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];EXP=ROOT/'experiments/yolo/gdt348_oracle_coordinate_transport_calibration';ART=EXP/'artifacts'
D=ART/'gdt348_design.json';P=ART/'gdt348_panel_scores.tsv';U=ART/'gdt348_unit_scores.tsv';E=ART/'gdt348_edge_scores.tsv';N=ART/'gdt348_null.tsv';C=ART/'gdt348_counterexamples.tsv';R=ART/'gdt348_result.json';REPORT=EXP/'REPORT.md';OUT=ART/'gdt348_validation.json'
O172=ROOT/'gdt172_sealed_oracle.json.gz';O173=ROOT/'gdt173_b2_sealed_oracle.json.gz';FROZEN=ROOT/'experiments/yolo/gdt347_fixed_graph_control_transport/artifacts/gdt347_frozen_graph.json'
SYSTEMS={'LEXICAL_A':(O172,'SYSTEM_A_V3_UNCHANGED_LITERAL'),'FACTORIAL_B':(O172,'SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3'),'HUMAN_GROWN_B2':(O173,'SYSTEM_B2_HUMAN_GROWN_DISTRIBUTED_CONTROL')}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def chash(x):
 y=dict(x);y.pop('content_sha256',None);return hashlib.sha256((json.dumps(y,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def load(p):
 with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)['rows']
checks=[]
def ck(v,n):checks.append(n);assert v,n
def close(a,b,t=2e-8):return abs(float(a)-float(b))<=t
def main():
 d=json.loads(D.read_text());res=json.loads(R.read_text());pan=read(P);units=read(U);edges=read(E);null=read(N);frozen=json.loads(FROZEN.read_text())
 ck(res['content_sha256']==chash(res),'result content');ck(res['status']=='ORACLE_MANUSCRIPT_SPECIFIC_RETAINED','status');ck(res['weights_unchanged'] and not res['score_optimized_mapping'],'fixed graph/mapping')
 ck([r['system'] for r in pan]==list(SYSTEMS),'panel order');ck(len(units)==15,'unit rows');ck(len(edges)==9,'edge rows');ck(len(null)==3*4096,'null rows');ck(len(read(C))==4,'counterexamples')
 held=set(d['split']['held_units']);train=set(d['split']['training_units']);cache={}
 for system,(path,label) in SYSTEMS.items():
  if path not in cache:cache[path]=load(path)
  rows=[x for x in cache[path] if x['system']==label];ck(len(rows)==15214,system+' rows');ck({x['source_unit_full'] for x in rows}==held|train,system+' units');ck(not any('f84' in x['source_unit_full'].lower() for x in rows),system+' no f84')
  by=defaultdict(list)
  for x in rows:by[x['true_record_id']].append(x)
  train_edges=held_edges=0
  for rr in by.values():
   rr.sort(key=lambda x:int(x['true_record_slot']));ck([int(x['true_record_slot']) for x in rr]==list(range(len(rr))),system+' record slots')
   n=len(rr)-1
   if rr[0]['source_unit_full'] in held:held_edges+=n
   else:train_edges+=n
  pr=next(x for x in pan if x['system']==system);ck(train_edges==int(pr['training_events'])==11263,system+' train edges');ck(held_edges==int(pr['held_events'])==3103,system+' held edges')
  ur=[x for x in units if x['system']==system];ck(sum(int(x['events']) for x in ur)==held_edges,system+' unit events');ck(len(ur)==5,system+' held unit count');ck(sum(int(x['positive']) for x in ur)==int(pr['positive_units'])==0,system+' unit signs')
  ck(close(sum(float(x['independent_bits']) for x in ur),pr['independent_bits']),system+' independent sum');ck(close(sum(float(x['graph_bits']) for x in ur),pr['graph_bits']),system+' graph sum');ck(close(float(pr['independent_bits'])-float(pr['graph_bits']),pr['raw_gain_bits']),system+' gain arithmetic');ck(close(float(pr['raw_gain_bits'])-float(frozen['selector_bits_once']),pr['cost_adjusted_gain_bits']),system+' cost arithmetic');ck(int(pr['comparable'])==1,system+' comparable')
  nr=[x for x in null if x['system']==system];obs=float(pr['raw_gain_bits']);p=(1+sum(float(x['graph_gain_bits'])>=obs for x in nr))/4097;ck(close(p,pr['inclusive_p']),system+' p')
  er=[x for x in edges if x['system']==system];ck({x['pair_id'] for x in er}=={'1-5','3-5','2-3'},system+' topology');ck(all(int(x['events'])==held_edges for x in er),system+' edge events')
 ck(all(float(x['raw_gain_bits'])<0 for x in pan),'all gains negative');ck(all(int(x['graph_exact'])==int(x['independent_exact']) for x in pan),'exact unchanged')
 obsmax=max(float(x['raw_gain_bits']) for x in pan);byworld=defaultdict(list)
 for x in null:byworld[int(x['world'])].append(float(x['graph_gain_bits']))
 maxp=(1+sum(max(v)>=obsmax for v in byworld.values()))/4097;ck(close(maxp,res['max_three_p']),'max3 p');ck(all(close(x['max_three_p'],maxp) for x in pan),'panel max3')
 for p,h in res['inputs'].items():ck(sha(ROOT/p)==h,'input '+p)
 for p,h in res['outputs'].items():ck(sha(ROOT/p)==h,'output '+p)
 ck(sha(Path(__file__).resolve())==sha(Path(__file__).resolve()),'validator readable');ck(all(v is False for v in res['f84'].values()),'f84 flags');text=REPORT.read_text();ck('ORACLE_MANUSCRIPT_SPECIFIC_RETAINED' in text,'report status');ck('No semantics' in text,'claim ceiling')
 out={'schema':'GDT348_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_SOURCE_CENSUS_SPLIT_AND_RETAINED_SCORE_ACCOUNTING_NO_MODEL_REFIT','checks_passed':len(checks),'checks_total':len(checks),'result_sha256':sha(R),'f84_access':False};out['content_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)} {res['status']}")
if __name__=='__main__':main()

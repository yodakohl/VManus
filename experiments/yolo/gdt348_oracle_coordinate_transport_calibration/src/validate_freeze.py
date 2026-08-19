#!/usr/bin/env python3
"""Independent compact validation of the GDT348 design freeze."""
import csv,gzip,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];EXP=ROOT/'experiments/yolo/gdt348_oracle_coordinate_transport_calibration';ART=EXP/'artifacts'
D=ART/'gdt348_design.json';C=ART/'gdt348_oracle_capacity.tsv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def chash(x):
 y=dict(x);y.pop('content_sha256',None);return hashlib.sha256(json.dumps(y,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(p):
 with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)['rows']
checks=[]
def ck(x,n):checks.append((n,bool(x)));assert x,n
def main():
 d=json.loads(D.read_text());ck(d['content_sha256']==chash(d),'content hash');ck(d['status']=='FROZEN_BEFORE_ORACLE_TRANSPORT_SCORING','status')
 o172=load(ROOT/'gdt172_sealed_oracle.json.gz');o173=load(ROOT/'gdt173_b2_sealed_oracle.json.gz')
 units={r['source_unit_full'] for r in o172};ck(len(units)==21,'21 units');ck(set(d['split']['training_units'])|set(d['split']['held_units'])==units,'split exhaustive');ck(not(set(d['split']['training_units'])&set(d['split']['held_units'])),'split disjoint');ck(len(d['split']['held_units'])==5,'held five')
 systems=Counter(r['system'] for r in o172);ck(systems['SYSTEM_A_V3_UNCHANGED_LITERAL']==15214,'A rows');ck(systems['SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3']==15214,'B rows');ck(len(o173)==15214,'B2 rows')
 with C.open(encoding='utf-8',newline='') as f:cap=list(csv.DictReader(f,delimiter='\t'))
 ck([r['system'] for r in cap]==['LEXICAL_A','FACTORIAL_B','HUMAN_GROWN_B2'],'capacity systems');ck(all(int(r['source_units'])==21 for r in cap),'capacity units');ck(all(int(r['inner_d_positive'])>=0 and int(r['dy_positive'])>0 for r in cap),'coordinate capacity')
 ck(d['graph']['weights_unchanged'] and not d['graph']['mapping_score_optimized'],'graph and mapping freeze');ck(all(v is False for v in d['f84'].values()),'f84 flags');ck(all(not str(x).startswith('f84') for x in d['split']['training_units']+d['split']['held_units']),'no f84 identifiers')
 for p,h in d['inputs'].items():ck(sha(ROOT/p)==h,'input '+p)
 for p,h in d['outputs'].items():ck(sha(ROOT/p)==h,'output '+p)
 out={'schema':'GDT348_FREEZE_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'design_sha256':sha(D),'f84_access':False};out['content_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ART/'gdt348_freeze_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")
if __name__=='__main__':main()

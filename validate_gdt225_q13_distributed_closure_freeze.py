#!/usr/bin/env python3
"""Integrity validator for GDT225 freeze."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt225_prediction_freeze.json';OUT=R/'gdt225_freeze_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
r=json.loads(RES.read_text());saved=r.pop('freeze_content_sha256');checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('content',saved==csha(r));r['freeze_content_sha256']=saved
ck('status',r['status']=='FROZEN_BEFORE_B3_AND_FOLLOWING_LABEL_JOIN')
ck('counts',r['target_records']==33 and r['control_records']==22)
ck('mechanisms',r['mechanisms']==['FINAL_LINE_B3','FOLLOWING_LABEL_BLOCK','UNION_DISTRIBUTED_CLOSURE_PROXY'])
ck('predictions',len(r['predictions'])==3 and r['required_lofo_positive']==8)
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
ck('f84',not any(r['f84'].values()))
v={'schema':'GDT225_FREEZE_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'freeze_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

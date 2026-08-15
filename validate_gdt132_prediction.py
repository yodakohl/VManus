#!/usr/bin/env python3
"""Validate the GDT132 pre-target freeze."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;P=ROOT/'gdt132_prediction.json';OUT=ROOT/'gdt132_prediction_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
x=json.loads(P.read_text());checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('schema',x['schema']=='GDT132_CROSS_REGISTER_CONTINUATION_ARITY_PREDICTION_V1');ck('status',x['status']=='FROZEN_BEFORE_EXTERNAL_TARGET_PAIR_ENUMERATION');ck('models',x['models']==['REFERENCE','LAST_HOST_CHAR3_HASH32','LAST_RAW_CHAR3_HASH32']);ck('target',x['target']=='FIRST_NEXT_LINE_FIELD_GROUP_COUNT_BIN_1_2_3_4PLUS');ck('f84',all(v is False for v in x['f84r'].values()));ck('inputs',all(sha(ROOT/n)==h for n,h in x['inputs'].items()));ck('implementation',all(sha(ROOT/n)==h for n,h in x['implementation'].items()));y=dict(x);h=y.pop('prediction_content_sha256');ck('content_hash',csha(y)==h);ck('no_result',not (ROOT/'gdt132_result.json').exists())
z={'schema':'GDT132_PREDICTION_VALIDATION_V1','status':'PASS_PRETARGET_FREEZE','checks':len(checks),'passed':sum(r['pass'] for r in checks),'prediction_sha256':sha(P),'validator_sha256':sha(Path(__file__)),'check_rows':checks};OUT.write_text(json.dumps(z,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':z['status'],'checks':z['checks']},sort_keys=True))

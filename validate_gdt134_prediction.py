#!/usr/bin/env python3
"""Validate the pre-enumeration GDT134 freeze."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;P=ROOT/'gdt134_prediction.json';OUT=ROOT/'gdt134_prediction_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
x=json.loads(P.read_text());checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('schema',x['schema']=='GDT134_GENERAL_ADJACENT_CONTINUATION_TRANSFER_PREDICTION_V1');ck('status',x['status']=='FROZEN_BEFORE_GENERAL_ADJACENT_PAIR_ENUMERATION');ck('models',x['models']==['RAW_CHAR3','HOST_CHAR3','COMPILER12']);ck('worlds',x['worlds']==4096);ck('capacity',x['capacity_gate']==50);ck('f84',x['f84r']=={'new_access':False,'actual_inputs_contain_rows':False,'prior_limited_audit_exposure_inherited':True});ck('inputs',all(sha(ROOT/p)==h for p,h in x['inputs'].items()));ck('implementation',all(sha(ROOT/p)==h for p,h in x['implementation'].items()));y=dict(x);h=y.pop('prediction_content_sha256');ck('content_hash',csha(y)==h);ck('no_result',not (ROOT/'gdt134_result.json').exists());v={'schema':'GDT134_PREDICTION_VALIDATION_V1','status':'PASS_PRE_ENUMERATION_FREEZE','checks':len(checks),'passed':sum(r['pass'] for r in checks),'prediction_sha256':sha(P),'validator_sha256':sha(Path(__file__)),'check_rows':checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))

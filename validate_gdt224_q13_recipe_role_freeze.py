#!/usr/bin/env python3
"""Integrity validator for GDT224 prediction freeze."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt224_prediction_freeze.json';OUT=R/'gdt224_freeze_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
r=json.loads(RES.read_text());saved=r.pop('freeze_content_sha256');checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('content',saved==csha(r));r['freeze_content_sha256']=saved
ck('status',r['status']=='FROZEN_BEFORE_Q13_FIELD_ROLE_PROJECTION')
ck('target',r['target']=={'scope':'Q13_F75_F83_OB_HAND2','lines':240,'pages':18,'physical_folios':9,'records':33})
ck('control',r['control']=={'scope':'HERBAL_B_HAND2','lines':61,'pages':19,'physical_folios':10,'records':22})
ck('predictions',len(r['predictions'])==3)
ck('features',len(r['model_features'])==4)
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
ck('f84',not any(r['f84'].values()))
v={'schema':'GDT224_FREEZE_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'freeze_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

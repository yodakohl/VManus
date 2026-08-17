#!/usr/bin/env python3
"""Validate GDT223 freeze integrity without reading target formal data."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent; RES=R/'gdt223_prediction_freeze.json'; OUT=R/'gdt223_freeze_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
r=json.loads(RES.read_text());saved=r.pop('freeze_content_sha256');checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('content_hash',saved==csha(r));r['freeze_content_sha256']=saved
ck('status',r['status']=='FROZEN_BEFORE_TARGET_MODULE_REVEAL')
ck('page',r['page']=='f82v' and r['physical_folio']=='f82')
ck('counts',r['selected_label_loci']==8 and r['selected_prose_lines']==r['complete_prose_lines']==12)
ck('modules',r['modules']==['ar','ol','dal','dar','sy','te','tee','dy'])
ck('predictions',r['predictions']['positive_correct_assignment_lead'] and r['predictions']['ar_discriminates_exactly_one_matching_assembly_side'] and r['predictions']['ar_side']=='UNPREDICTED')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('document_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('implementation_'+n,sha(R/n)==h)
ck('access',not r['access']['target_tokens_displayed_in_this_pass'] and not r['access']['target_module_presence_displayed_in_this_pass'])
ck('f84',not any(r['f84'].values()))
v={'schema':'GDT223_FREEZE_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'freeze_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

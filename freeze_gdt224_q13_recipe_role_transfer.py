#!/usr/bin/env python3
"""Freeze GDT224 target/control and diagnostics without field-role scoring."""
import csv,hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent;FRAME=R/'gdt046_line_frames.tsv';EXT=R/'gdt176_external_role_units.tsv';OLD=R/'gdt176_result.json'
METHOD=R/'GDT224_Q13_RECIPE_ROLE_TRANSFER_FREEZE_METHOD.md';OUT=R/'gdt224_prediction_freeze.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def pn(p):return int(re.match(r'f(\d+)',p).group(1))
def ln(l):return int(l.split('.')[1])
rows=[]
with FRAME.open() as h:
 for r in csv.DictReader(h,delimiter='\t'):
  if r['page'].startswith('f84'):continue
  rows.append(r)
q=[r for r in rows if 75<=pn(r['page'])<=83 and r['register']=='OB' and r['hand']=='2']
h=[r for r in rows if r['register']=='HB' and r['hand']=='2']
def records(rr):
 n=0
 for p in {r['page'] for r in rr}:
  x=sorted((r for r in rr if r['page']==p),key=lambda z:ln(z['locus']));n+=1+sum(int(z['paragraph_start']) for z in x[1:])
 return n
assert (len(q),len({x['page'] for x in q}),len({x['physical_folio'] for x in q}),records(q))==(240,18,9,33)
assert (len(h),len({x['page'] for x in h}),len({x['physical_folio'] for x in h}),records(h))==(61,19,10,22)
v={'schema':'GDT224_Q13_RECIPE_ROLE_TRANSFER_FREEZE_V1','status':'FROZEN_BEFORE_Q13_FIELD_ROLE_PROJECTION','external_instrument':'GDT176_POSITION_LENGTH','target':{'scope':'Q13_F75_F83_OB_HAND2','lines':240,'pages':18,'physical_folios':9,'records':33},'control':{'scope':'HERBAL_B_HAND2','lines':61,'pages':19,'physical_folios':10,'records':22},'classes':['INSTRUCTION_CLAUSE_LIKE','SHORT_ARGUMENT_LIKE','RECORD_CLOSER_LIKE','UNRESOLVED_EDGE_CLASS'],'predictions':['Q13_HIGHER_MIXED_CLAUSE_ARGUMENT_RECORD_RATE','Q13_HIGHER_FINAL_CLOSER_RATE','Q13_LOWER_JS_DIVERGENCE_TO_EXTERNAL_RECIPE_DISTRIBUTION'],'model_features':['RELATIVE_FIELD_POSITION','SQUARED_POSITION','LOG2_ONE_PLUS_FIELD_GROUP_COUNT','LOG2_ONE_PLUS_RECORD_FIELD_COUNT'],'f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (FRAME,EXT,OLD)},'documents':{METHOD.name:sha(METHOD)},'implementation':{Path(__file__).name:sha(Path(__file__))}}
v['freeze_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(v['status'])

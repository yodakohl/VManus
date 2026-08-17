#!/usr/bin/env python3
"""Validate GDT226 source freeze and non-f84 scope census."""
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt226_prediction_freeze.json';OUT=R/'gdt226_freeze_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def pn(p):return int(re.match(r'f(\d+)',p).group(1))
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('freeze_content_sha256');ck('content',saved==csha(r));r['freeze_content_sha256']=saved
ck('status',r['status']=='FROZEN_BEFORE_SIX_SCOPE_ROLE_PROJECTION')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
def scope(x):
 if x['register']=='HA':return 'HERBAL_A'
 if x['register']=='HB':return 'HERBAL_B'
 if x['register']=='SB':return 'STARS_B'
 if x['register']=='OA':return 'OTHER_A'
 if x['register']=='OB' and 75<=pn(x['page'])<=83:return 'Q13'
 if x['register']=='OB':return 'OTHER_B'
 raise AssertionError(x['register'])
c=Counter();pages={};folios={}
with (R/'gdt046_line_frames.tsv').open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84'):continue
  s=scope(x);c[s]+=1;pages.setdefault(s,set()).add(x['page']);folios.setdefault(s,set()).add(x['physical_folio'])
ck('six_scopes',set(c)=={'HERBAL_A','HERBAL_B','STARS_B','OTHER_A','Q13','OTHER_B'})
ck('lines',dict(sorted(c.items()))==r['line_counts'])
ck('pages',{s:len(v) for s,v in sorted(pages.items())}==r['page_counts'])
ck('folios',{s:len(v) for s,v in sorted(folios.items())}==r['folio_counts'])
ck('q13_folios',r['folio_counts']['Q13']==9)
ck('predictions',[x['id'] for x in r['predictions']]==['P1','P2','P3'])
ck('f84',r['f84']=={'public_metadata_previously_exposed':True,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False})
v={'schema':'GDT226_FREEZE_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'freeze_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

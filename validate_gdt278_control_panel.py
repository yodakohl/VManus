#!/usr/bin/env python3
"""Validate GDT278 control admission independently of score outputs."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def rows(p):
 with (R/p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
c=[]
def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
x=json.loads((R/'gdt278_control_source_freeze.json').read_text());rr=rows('gdt278_control_manifest.tsv')
ck('status',x['status']=='CONTROL_PANEL_FROZEN_BEFORE_GDT278_SCORING');ck('fifteen_controls',len(rr)==x['controls']==15 and len({z['control_id'] for z in rr})==15)
ck('sources_current',all(sha(z['observation_artifact'])==z['observation_sha256'] for z in rr));ck('evidence_current',all(sha(z['architecture_evidence_artifact'])==z['architecture_evidence_sha256'] for z in rr))
ck('oracle_not_scored',all(z['oracle_fields_scored']=='0' for z in rr) and x['oracle_fields_scored']==0)
ck('required_categories',{'REAL_DIPLOMATIC_ABBREVIATION','SYNTHETIC_LEXICAL_CODEBOOK','SYNTHETIC_FACTORIAL_TECHNICAL_NOTATION','SYNTHETIC_HUMAN_GROWN_HYBRID'}.issubset(x['categories']))
ck('gdt156_excluded',any(z['control_id']=='GDT156_IMPOSED_HPR2_ENCODER' for z in x['exclusions']))
ck('no_hpr1_or_substrings',x['voynich_substrings_mined']==x['hpr1_semantics_used']==0);ck('f84_false',not any(x['f84'].values()))
q=dict(x);h=q.pop('content_sha256');ck('content_hash',hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()==h)
o={'schema':'GDT278_CONTROL_SOURCE_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'manifest_sha256':sha('gdt278_control_manifest.tsv'),'freeze_sha256':sha('gdt278_control_source_freeze.json')};o['content_sha256']=hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt278_control_source_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)}))

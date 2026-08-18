#!/usr/bin/env python3
"""Validate the GDT282 pre-score freeze."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):
 q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt282_design.json').read_text());ck('status',d['status']=='FROZEN_BEFORE_GDT282_SCORING');ck('content',d['content_sha256']==csha(d));ck('method',d['method_sha256']==sha(R/'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_METHOD.md'));ck('freezer',d['implementation_sha256']==sha(R/'freeze_gdt282_outer_wrapper_class_transfer.py'))
 rr=list(csv.DictReader(open(R/'gdt282_gdt281_freeze_manifest.tsv'),delimiter='\t'));ck('manifest',len(rr)==15 and d['freeze_manifest_sha256']==sha(R/'gdt282_gdt281_freeze_manifest.tsv'));[ck('frozen:'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256']) for x in rr]
 ck('models',len(d['models'])==5);ck('classes',d['wrapper_classes']==['NONE','q','ch','d','sh','che','t','s']);ck('class_probe',d['class_probe_rule']=='EXHAUSTIVE_ONE_VS_REST_BINARY' and d['superseded_invalid_probe']=='UNIQUE_RENAME_IS_BIJECTIVE_ZERO_INFORMATION');ck('regimes',len(d['transfer_regimes'])==3);ck('sections',len(d['powered_sections'])==6);ck('hands',len(d['powered_hands'])==4);ck('null',d['null_worlds']==64);ck('no_semantics',d['semantic_assignments']==d['hpr1_semantics_used']==d['page_host_substrings_mined']==0);ck('f84',all(v in (0,False) for v in d['f84'].values()))
 out={'schema':'GDT282_DESIGN_VALIDATION_V1','status':'PASS','checks':len(c),'design_sha256':sha(R/'gdt282_design.json'),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);(R/'gdt282_design_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

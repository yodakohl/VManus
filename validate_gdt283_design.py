#!/usr/bin/env python3
"""Validate the GDT283 score freeze."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt283_design.json').read_text());ck('status',d['status']=='FROZEN_BEFORE_GDT283_SCORING');ck('content',d['content_sha256']==csha(d));ck('method',d['method_sha256']==sha(R/'GDT283_WRAPPER_HOST_COUPLING_LOCALIZATION_METHOD.md'));ck('freezer',d['implementation_sha256']==sha(R/'freeze_gdt283_wrapper_host_coupling_localization.py'));rr=list(csv.DictReader(open(R/'gdt283_gdt282_freeze_manifest.tsv'),delimiter='\t'));ck('manifest',len(rr)==15 and d['freeze_manifest_sha256']==sha(R/'gdt283_gdt282_freeze_manifest.tsv'));[ck('frozen:'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256']) for x in rr];ck('panels',len(d['panels'])==4);ck('models',len(d['models'])==2);ck('components',d['components']==['INITIAL','INTERNAL','FINAL','EOS']);ck('host_buckets',d['host_bucket_count']==8);ck('null',d['null_worlds']==64 and d['null_seed_family']=='GDT283_FIRSTCHAR_LENGTH_MATCHED_V1' and len(d['null_strata'])==6);ck('maxT',d['maxT_statistic']=='MAX_PANEL_STANDARDIZED_TOTAL_GAIN');ck('mobile',d['voynich_mobile_events']==7075);ck('no_semantics',d['semantic_assignments']==d['page_host_substrings_mined']==0);ck('f84',all(v in (0,False) for v in d['f84'].values()));out={'schema':'GDT283_DESIGN_VALIDATION_V1','status':'PASS','checks':len(c),'design_sha256':sha(R/'gdt283_design.json'),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);(R/'gdt283_design_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

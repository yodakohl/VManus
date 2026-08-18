#!/usr/bin/env python3
"""Validate the pre-score GDT284 freeze without scoring any panel."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt284_design.json';M=R/'gdt284_freeze_manifest.tsv';OUT=R/'gdt284_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());m=rows(M);native=rows(R/'gdt278_native_event_inventory.tsv')
 ck('status',d['status']=='CORRECTED_FROZEN_BEFORE_AUTHORITATIVE_GDT284_SCORING');ck('content',d['content_sha256']==csha(d));ck('manifest_hash',d['freeze_manifest_sha256']==sha(M));ck('manifest_files',len(m)==11 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in m));ck('panels',len(d['panels'])==12 and len(set(d['panels']))==12);ck('events',all(sum(x['control_id']==p for x in native)==8448 for p in d['panels']));ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('components',d['components']==['INITIAL','INTERNAL','FINAL','EOS']);ck('modes',d['modes']==['STANDARD_HELD_FOLIO','NESTED_UNSEEN_HOST_BUCKET']);ck('null',d['null_worlds']==64 and d['host_bucket_count']==8);ck('capacity_rule',d['capacity_rule']['known_zero_wrapper_capacity_panels']==['LEARNED_ABBREVIATION_MAP','LEARNED_ABBREVIATION_SAMPLED'] and d['capacity_rule']['known_zero_context_reuse_panels']==['ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL'] and d['capacity_rule']['exclude_from_sign_match'] and d['capacity_rule']['exclude_from_standardized_maxT']);ck('no_tuning',d['semantic_assignments']==d['page_host_substrings_mined']==d['new_synthetic_worlds']==d['oracle_fields_scored']==0 and not d['threshold_tuned']);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));ck('method',d['method_sha256']==sha(R/'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_METHOD.md'));ck('implementation',all(sha(R/k)==v for k,v in d['implementation'].items()))
 out={'schema':'GDT284_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

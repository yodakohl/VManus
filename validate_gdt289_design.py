#!/usr/bin/env python3
"""Validate the GDT289 pre-score design."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt289_design.json';OUT=R/'gdt289_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='CORRECTED_FROZEN_BEFORE_GDT289_SCORING');ck('panels',len(d['panels'])==8 and len(set(d['panels']))==8);ck('models',d['models']==['POSITION_CONTEXT','OTHER_POSITION_HOST_BAG','CROSS_HOST_POSITION_TRANSFER']);ck('target_cell_forbidden',d['target_cell_rule']=='FORBID_TARGET_HOST_TARGET_POSITION_PROFILE');ck('transition_exclusions',d['transition_training_rule']=='EXCLUDE_HELD_FOLIO_AND_TARGET_HOST_BUCKET');ck('host_equal',d['transition_estimator'].startswith('HOST_EQUAL_'));ck('buckets',d['host_bucket_count']==8);ck('null',d['null_worlds']==64 and d['null_operation'].startswith('PERMUTE_HELD_WRAPPER_OUTCOMES_'));ck('no_target_history',d['target_page_outcomes_used'] is False);ck('chronology',d['correction_chronology'].endswith('BEFORE_ANY_WRAPPER_OUTCOME_SCORE'));ck('decision',d['decision']['minimum_positive_host_buckets']==6 and d['decision']['minimum_positive_positions']==3 and d['decision']['alpha']==.05);ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==d['page_host_substrings_mined']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));m=rows(R/'gdt289_freeze_manifest.tsv');ck('manifest_count',len(m)==5);ck('manifest_hashes',all(sha(R/x['artifact'])==x['frozen_sha256'] for x in m));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt289_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_METHOD.md'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('native_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('event_counts',all(sum(x['control_id']==p for x in native)==8448 for p in d['panels']))
 out={'schema':'GDT289_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

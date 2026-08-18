#!/usr/bin/env python3
"""Validate GDT290 pre-score design."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt290_design.json';OUT=R/'gdt290_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 cc=[]
 def ck(n,v):cc.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT290_SCORING');ck('panels',len(d['panels'])==8 and len(set(d['panels']))==8);ck('primary_k',d['primary_k']==4 and d['voynich_sensitivity_k']==[2,8]);ck('target_forbidden',d['target_cell_rule']=='FORBID_TARGET_HOST_TARGET_POSITION_PROFILE');ck('training_exclusion',d['training_exclusion']=='HELD_FOLIO_AND_TARGET_HOST_BUCKET');ck('opaque_features',d['features'].startswith('OPAQUE_HOST_'));ck('cluster_rule',d['minimum_training_hosts_per_class']==3 and d['maximum_lloyd_iterations']==30);ck('null',d['null_worlds']==64 and d['null_operation'].startswith('PERMUTE_HELD_WRAPPER_OUTCOMES_'));ck('zero_variance',d['zero_variance_rule'].endswith('EXCLUDE_FROM_MAXT'));ck('decision',d['decision']['minimum_positive_host_buckets']==6 and d['decision']['minimum_positive_positions']==3 and d['decision']['alpha']==.05);ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==d['page_host_substrings_mined']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));m=rows(R/'gdt290_freeze_manifest.tsv');ck('manifest',len(m)==5 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in m));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt290_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT290_LATENT_HOST_RENDERER_CLASSES_METHOD.md'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('native_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('event_counts',all(sum(x['control_id']==p for x in native)==8448 for p in d['panels']));out={'schema':'GDT290_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()

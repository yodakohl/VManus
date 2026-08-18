#!/usr/bin/env python3
"""Validate GDT291 frozen design."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt291_design.json';OUT=R/'gdt291_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT291_SCORING');ck('panels',len(d['panels'])==8);ck('models',len(d['models'])==7 and d['models'][0]=='SHAPE_CONTEXT');ck('q_forbidden','q_flag' in d['forbidden_predictors']);ck('target_history_forbidden','target_page_wrapper_history' in d['forbidden_predictors']);ck('contexts',len(d['shape_context'])==8 and len(d['record_context'])==6 and len(d['nonwrapper_compiler'])==5);ck('priors',d['primary_prior_mass']==11 and d['voynich_prior_sensitivities']==[5,22]);ck('decision',len(d['decision'])==4);ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==d['page_host_substrings_mined']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));m=rows(R/'gdt291_freeze_manifest.tsv');ck('manifest',len(m)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in m));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt291_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT291_HOST_POSITION_CONTEXT_DECOMPOSITION_METHOD.md'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('native_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('event_counts',all(sum(x['control_id']==p for x in native)==8448 for p in d['panels']));out={'schema':'GDT291_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Validate GDT292 frozen design."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt292_design.json';OUT=R/'gdt292_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT292_SCORING');ck('panels',len(d['panels'])==8);ck('models',d['models']==['LAYOUT_CONTEXT','EXACT_HOST','OUTER_LOCAL_CONTEXT','RIGHT_FAMILY']);ck('outcome',d['outcome'].startswith('EXACT_DY_B3_'));ck('contexts',len(d['layout_context'])==9 and len(d['outer_local_context'])==4);ck('priors',d['primary_prior_mass']==11 and d['voynich_prior_sensitivities']==[5,22]);ck('null',d['null_worlds']==64 and d['null_operation'].startswith('PERMUTE_HELD_CLOSURE_'));ck('decision',d['decision']['minimum_positive_right_classes']==4 and d['decision']['minimum_positive_folios']==60 and d['decision']['alpha']==.05);ck('parser_coupling',d['same_group_parser_coupled'] is True);ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));m=rows(R/'gdt292_freeze_manifest.tsv');ck('manifest',len(m)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in m));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt292_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT292_RIGHT_FAMILY_CLOSURE_CHANNEL_METHOD.md'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('native_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('event_counts',all(sum(x['control_id']==p for x in native)==8448 for p in d['panels']));out={'schema':'GDT292_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

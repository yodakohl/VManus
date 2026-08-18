#!/usr/bin/env python3
"""Validate the GDT285 pre-score freeze."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt285_design.json';M=R/'gdt285_freeze_manifest.tsv';OUT=R/'gdt285_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());m=rows(M);native=rows(R/'gdt278_native_event_inventory.tsv');ck('status',d['status']=='FROZEN_BEFORE_GDT285_SCORING');ck('content',d['content_sha256']==csha(d));ck('manifest',len(m)==7 and sha(M)==d['freeze_manifest_sha256'] and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in m));ck('panels',len(d['panels'])==4 and all(sum(x['control_id']==p for x in native)==8448 for p in d['panels']));ck('bins',d['recurrence_bins']=={'ZERO':[0,0],'ONE':[1,1],'TWO_TO_THREE':[2,3],'FOUR_TO_SEVEN':[4,7],'EIGHT_PLUS':[8,None]});ck('modes',d['modes']==['STANDARD','EXACT_HOST_EXCLUDED','MATCHED_NONHOST_EXCLUDED']);ck('tiers',len(d['matched_donor_tiers'])==5);ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==d['page_host_substrings_mined']==0);ck('method',d['method_sha256']==sha(R/'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_METHOD.md'));ck('implementation',all(sha(R/k)==v for k,v in d['implementation'].items()))
 out={'schema':'GDT285_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

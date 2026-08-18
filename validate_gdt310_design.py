#!/usr/bin/env python3
"""Validate target-blind GDT310 source-side feature freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;FEATURES=R/'gdt310_source_side_features.tsv';CAP=R/'gdt310_capacity.tsv';DESIGN=R/'gdt310_design.json';OUT=R/'gdt310_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content_hash',stored==can(d));rows=read(FEATURES);cap={x['operation']:x for x in read(CAP)};ck('status',d['status']=='FROZEN_BEFORE_TARGET_BLIND_LICENSE_SCORING');ck('capacity',{k:(int(v['hosts']),int(v['licensed_hosts'])) for k,v in cap.items()}=={'wrapper:NONE>q':(52,31),'wrapper:ch>s':(25,7),'wrapper:d>s':(16,8)});ck('source_support',all(int(x['source_events'])>=5 and int(x['source_folios'])>=3 for x in rows));ck('unique_operation_hosts',len(rows)==len({(x['operation'],x['host_id_sha256']) for x in rows})==93);ck('forbidden_absent',not any(k in d['models']['FULL'] for k in d['forbidden_predictors']));ck('input_hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']));ck('output_hashes',all(d['outputs'][n]==sha(R/n) for n in d['outputs']));ck('f84_flags',not any(d['f84'].values()));v={'schema':'GDT310_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'rows':len(rows)},sort_keys=True))
if __name__=='__main__':main()

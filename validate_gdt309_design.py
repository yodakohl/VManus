#!/usr/bin/env python3
"""Validate frozen GDT309 feature/label capacity and hashes."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;DESIGN=R/'gdt309_design.json';FEATURES=R/'gdt309_host_features.tsv';CAP=R/'gdt309_capacity.tsv';OUT=R/'gdt309_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content_hash',stored==can(d));rows=read(FEATURES);ck('status',d['status']=='FROZEN_BEFORE_LICENSE_PREDICTION_SCORING');ck('host_count_unique',len(rows)==58==len({x['host_id_sha256'] for x in rows}));ck('labels_exact',[sum(int(x[k]) for x in rows) for k in ('license_wrapper_ch_to_s','license_wrapper_d_to_s','license_wrapper_NONE_to_q')]==[7,8,31]);ck('forbidden_absent',not any(k in d['models']['FULL'] for k in d['forbidden_predictors']));ck('model_nesting',set(d['models']['FREQUENCY'])<set(d['models']['LAYOUT'])<set(d['models']['FULL']) and set(d['models']['FREQUENCY'])<set(d['models']['COMPILER'])<set(d['models']['FULL']) and set(d['models']['FREQUENCY'])<set(d['models']['REGISTER'])<set(d['models']['FULL']));ck('input_hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']));ck('output_hashes',all(d['outputs'][n]==sha(R/n) for n in d['outputs']));ck('f84_flags',not any(d['f84'].values()));v={'schema':'GDT309_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()

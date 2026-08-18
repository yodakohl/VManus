#!/usr/bin/env python3
"""Validate GDT295 design and online capacity."""
from __future__ import annotations
import csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt295_design.json';OUT=R/'gdt295_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT295_SCORING');ck('panels',len(d['panels'])==8 and len(d['powered_panels'])==5 and len(d['unscored_zero_capacity_panels'])==3);ck('models',len(d['models'])==3 and d['models'][-1]=='PAGE_LOCAL_HOST_X_POSITION');ck('line_safe',d['same_line_update_forbidden'] is True);ck('priors',d['primary_prior_mass']==11 and d['voynich_prior_sensitivities']==[5,22]);ck('null',d['null_worlds']==64 and 'AFTER_ALL_ONLINE_PREDICTIONS_FREEZE' in d['null_operation']);ck('decision',d['decision']['minimum_positive_pages']==100 and d['decision']['minimum_positive_sections']==4 and d['decision']['alpha']==.05);ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));cap=rows(R/'gdt295_capacity.tsv');ck('cap_shape',len(cap)==8 and d['capacity_sha256']==sha(R/'gdt295_capacity.tsv'))
 for p in d['panels']:
  ev=[x for x in native if x['control_id']==p];hf=defaultdict(set)
  for x in ev:hf[x['page_host']].add(x['physical_folio'])
  seen=set();e=[]
  for locus,g in itertools.groupby(ev,key=lambda x:x['locus']):
   line=list(g)
   for x in line:
    if len(hf[x['page_host']])>=2 and (x['page'],x['page_host']) in seen:e.append(x)
   for x in line:seen.add((x['page'],x['page_host']))
  q=next(x for x in cap if x['control_id']==p);ck('capacity:'+p,int(q['events'])==len(ev)==8448 and int(q['eligible_events'])==len(e) and int(q['eligible_pages'])==len({x['page'] for x in e}) and int(q['eligible_folios'])==len({x['physical_folio'] for x in e}) and int(q['eligible_hosts'])==len({x['page_host'] for x in e}) and (q['capacity_status']=='POWERED')==(len(e)>0))
 ck('lists',d['powered_panels']==[x['control_id'] for x in cap if int(x['eligible_events'])>0] and d['unscored_zero_capacity_panels']==[x['control_id'] for x in cap if int(x['eligible_events'])==0]);mf=rows(R/'gdt295_freeze_manifest.tsv');ck('manifest',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt295_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT295_ONLINE_PAGE_LOCAL_RENDERER_METHOD.md'));o={'schema':'GDT295_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};o['content_sha256']=csha(o);OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

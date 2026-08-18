#!/usr/bin/env python3
"""Validate GDT294 frozen design."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt294_design.json';OUT=R/'gdt294_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT294_SCORING');ck('panels',len(d['panels'])==8);ck('models',d['models']==['LAYOUT_CONTEXT','BOUNDARY_CONTEXT','EXACT_HOST','HOST_X_POSITION','HOST_X_RECORD_SLOT']);ck('effects',d['primary_effect'].startswith('EXACT_HOST_MINUS_') and d['secondary_effect'].startswith('HOST_X_POSITION_MINUS_'));ck('contexts',len(d['layout_context'])==9 and len(d['boundary_context'])==3);ck('prior',d['primary_prior_mass']==11 and d['voynich_prior_sensitivities']==[5,22]);ck('null',d['null_worlds']==64 and 'EXCLUDING_WITHIN_FIELD_POSITION' in d['null_operation']);ck('decision',d['decision']['minimum_positive_folios']==60 and d['decision']['alpha']==.05);ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('native_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));cap=rows(R/'gdt294_capacity.tsv');ck('capacity_shape',len(cap)==8 and d['capacity_sha256']==sha(R/'gdt294_capacity.tsv'))
 for p in d['panels']:
  ev=[x for x in native if x['control_id']==p];hf=defaultdict(set)
  for x in ev:hf[x['page_host']].add(x['physical_folio'])
  e=[x for x in ev if len(hf[x['page_host']])>=2];hp=defaultdict(set)
  for x in e:hp[x['page_host'],x['within_field_position']].add(x['physical_folio'])
  q=next(x for x in cap if x['control_id']==p);ck('capacity:'+p,int(q['events'])==len(ev)==8448 and int(q['exact_host_eligible_events'])==len(e) and int(q['cross_folio_host_position_cells'])==sum(len(v)>=2 for v in hp.values()) and int(q['host_position_supported_events'])==sum(len(hp[x['page_host'],x['within_field_position']]-{x['physical_folio']})>0 for x in e))
 mf=rows(R/'gdt294_freeze_manifest.tsv');ck('manifest',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt294_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT294_HOST_POSITION_RENDERER_TUPLE_METHOD.md'));o={'schema':'GDT294_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};o['content_sha256']=csha(o);OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

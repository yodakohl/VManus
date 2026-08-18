#!/usr/bin/env python3
"""Validate GDT296 frozen population."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt296_design.json';OUT=R/'gdt296_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT296_ATLAS_SCORING');ck('population',d['population']=={'minimum_events':20,'minimum_physical_folios':5,'hosts':59,'events':5715});ck('models',d['models']==['HOST_CANONICAL','HOST_X_POSITION']);ck('labels',d['labels']['canonical']['top1_min']==.7 and d['labels']['canonical']['entropy_max_bits']==1 and d['labels']['position_conditioned']['top1_improvement_min']==.1);ck('prohibitions',d['p_values']==d['host_substrings_mined']==d['semantic_assignments']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));r=[x for x in native if x['control_id']=='VOYNICH_REFERENCE'];by=defaultdict(list)
 for x in r:by[x['page_host']].append(x)
 exp=[{'page_host':h,'events':str(len(v)),'folios':str(len({x['physical_folio'] for x in v})),'sections':str(len({x['section'] for x in v})),'hands':str(len({x['hand'] for x in v}))} for h,v in by.items() if len(v)>=20 and len({x['physical_folio'] for x in v})>=5];exp.sort(key=lambda x:(-int(x['events']),x['page_host']));pop=rows(R/'gdt296_population.tsv');ck('population_rows',pop==exp and d['population_sha256']==sha(R/'gdt296_population.tsv'));mf=rows(R/'gdt296_freeze_manifest.tsv');ck('manifest',len(mf)==5 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt296_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT296_OPAQUE_HOST_RENDERER_ATLAS_METHOD.md'));o={'schema':'GDT296_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};o['content_sha256']=csha(o);OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

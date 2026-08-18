#!/usr/bin/env python3
"""Validate frozen GDT299 design and capacity without scoring positions."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt299_design.json';OUT=R/'gdt299_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):c.append((n,bool(v)));assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==rch(d));ck('status',d['status']=='FROZEN_BEFORE_GDT299_SCORING');ck('models',d['models']==['LAYOUT','PAGE_HOST','WHOLE_FORM']);ck('outcome',d['outcome']=='PHYSICAL_GROUP_POSITION_FIRST_MIDDLE_LAST');ck('prohibitions',d['page_host_substrings_mined']==d['source_strings_inspected']==d['semantic_assignments']==0);ck('f84',not any(d['f84'].values()));rows=read(R/'gdt278_native_event_inventory.tsv');ck('source_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));pub={x['control_id']:x for x in read(R/'gdt299_capacity.tsv')};reb={}
 for panel in sorted({x['control_id'] for x in rows}):
  base=[x for x in rows if x['control_id']==panel and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
  for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
  e=[x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2];s=defaultdict(list)
  for x in e:s[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(x)
  mob=sum(len(v) for v in s.values() if len({x['source_surface_sha256'] for x in v})>1);p=pub[panel];ck(f'capacity:{panel}',int(p['multi_group_events'])==len(base) and int(p['eligible_events'])==len(e) and int(p['eligible_folios'])==len({x['physical_folio'] for x in e}) and int(p['null_mobile_events'])==mob and p['score_capacity']==('POWERED' if len(e)>=500 else 'UNSCORED_LT500') and p['null_capacity']==('VARIABLE' if mob>=100 else 'DESCRIPTIVE_LOW_MOBILITY'))
 ck('capacity_hash',sha(R/'gdt299_capacity.tsv')==d['capacity_sha256']);ck('method',sha(R/'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_METHOD.md')==d['method_sha256']);ck('manifest',sha(R/'gdt299_freeze_manifest.tsv')==d['freeze_manifest_sha256']);
 for x in read(R/'gdt299_freeze_manifest.tsv'):ck(f"frozen:{x['artifact']}",sha(R/x['artifact'])==x['frozen_sha256'])
 out={'schema':'GDT299_DESIGN_VALIDATION_V1','status':'PASS','checks_total':len(c),'checks_passed':sum(v for n,v in c),'failed_checks':[n for n,v in c if not v],'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=rch(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()

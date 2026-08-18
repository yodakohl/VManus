#!/usr/bin/env python3
"""Independent GDT301 freeze validator."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
d=json.loads((R/'gdt301_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('content',d['content_sha256']==can(q));ck('status',d['status']=='FROZEN_BEFORE_GDT301_SCORING');ck('axes',d['axes']==['physical_folio','register','section','currier','hand']);ck('flags',d['source_strings_inspected']==d['page_host_substrings_mined']==d['semantic_assignments']==0 and not any(d['f84'].values()));ck('method',sha(R/'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_METHOD.md')==d['method_sha256']);ck('capacity',sha(R/'gdt301_capacity.tsv')==d['capacity_sha256']);ck('manifest',sha(R/'gdt301_freeze_manifest.tsv')==d['freeze_manifest_sha256']);
for n,h in d['implementation'].items():ck('impl_'+n,sha(R/n)==h)
for x in read(R/'gdt301_freeze_manifest.tsv'):ck('manifest_'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256'])
rows=read(R/'gdt278_native_event_inventory.tsv');ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));exp=[]
for p in sorted({x['control_id'] for x in rows}):
 base=[x for x in rows if x['control_id']==p and int(x['group_count'])>=2]
 for ax in d['axes']:
  n=lev=0
  for v in sorted({x[ax] for x in base}):
   tr=[x for x in base if x[ax]!=v];hs={x['page_host'] for x in tr};ss={x['source_surface_sha256'] for x in tr};z=[x for x in base if x[ax]==v and x['page_host'] in hs and x['source_surface_sha256'] in ss];n+=len(z);lev+=bool(z)
  exp.append((p,ax,n,lev))
got=[(x['control_id'],x['held_axis'],int(x['eligible_events']),int(x['held_levels_with_events'])) for x in read(R/'gdt301_capacity.tsv')];ck('capacity_exact',got==exp);v=[x for x in got if x[0]=='VOYNICH_REFERENCE'];ck('voynich',[x[2] for x in v]==[6844,6368,6294,4648,6243]);(R/'gdt301_design_validation.json').write_text(json.dumps({'schema':'GDT301_DESIGN_VALIDATION_V1','status':'PASS','checks':len(checks),'design_sha256':sha(R/'gdt301_design.json')},indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))

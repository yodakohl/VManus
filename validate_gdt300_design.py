#!/usr/bin/env python3
"""Independent integrity/capacity validator for frozen GDT300 design."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
d=json.loads((R/'gdt300_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('content',d['content_sha256']==canonical(q));ck('status',d['status']=='FROZEN_BEFORE_GDT300_SCORING');ck('fields',d['renderer_fields']==['wrapper','local_frame','inner_d','right_family','dy_closure','b3']);ck('models',d['shared_models']==d['renderer_fields']+['renderer_tuple']);ck('no_strings',d['source_strings_inspected']==d['page_host_substrings_mined']==0);ck('no_semantics',d['semantic_assignments']==0);ck('f84_flags',not any(d['f84'].values()));
for n,h in d['implementation'].items():ck('implementation_'+n,sha(R/n)==h)
ck('method_hash',sha(R/'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_METHOD.md')==d['method_sha256']);ck('cap_hash',sha(R/'gdt300_capacity.tsv')==d['capacity_sha256']);ck('manifest_hash',sha(R/'gdt300_freeze_manifest.tsv')==d['freeze_manifest_sha256']);
for x in read(R/'gdt300_freeze_manifest.tsv'):ck('manifest_'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256'])
rows=read(R/'gdt278_native_event_inventory.tsv');ck('source_nonempty',bool(rows));ck('source_f84_free',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));out=[]
for panel in sorted({x['control_id'] for x in rows}):
 base=[x for x in rows if x['control_id']==panel and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 ev=[x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2];groups=defaultdict(list)
 for x in ev:groups[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(x)
 mobile=sum(len(v) for v in groups.values() if len({tuple(x[k] for k in d['renderer_fields']) for x in v})>1);out.append((panel,len(ev),len({x['physical_folio'] for x in ev}),mobile))
got=[(x['control_id'],int(x['eligible_events']),int(x['eligible_folios']),int(x['renderer_mobile_events'])) for x in read(R/'gdt300_capacity.tsv')];ck('capacity_exact',got==out);v=next(x for x in got if x[0]=='VOYNICH_REFERENCE');ck('voynich_capacity',v[1]==6844 and v[2]==91);ck('decision',d['decision']['minimum_shared_fraction']==.5 and d['decision']['max_seven_p_le']==.05);Path(R/'gdt300_design_validation.json').write_text(json.dumps({'schema':'GDT300_DESIGN_VALIDATION_V1','status':'PASS','checks':len(checks),'design_sha256':sha(R/'gdt300_design.json')},indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'voynich_mobile':v[3]},sort_keys=True))

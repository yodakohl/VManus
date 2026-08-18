#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
d=json.loads((R/'gdt303_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('content',d['content_sha256']==can(q));ck('status',d['status']=='FROZEN_BEFORE_GDT303_POSITION_SCORING');ck('fields',d['renderer_fields']==['wrapper','local_frame','inner_d','right_family','dy_closure','b3']);ck('thresholds',(d['form_min_events'],d['form_min_folios'],d['operation_min_pairs'],d['operation_min_hosts'])==(5,3,4,4));ck('semantic',d['semantic_assignments']==0);ck('f84',not any(d['f84'].values()));ck('method',sha(R/'GDT303_RENDERER_OPERATION_POSITION_DELTA_METHOD.md')==d['method_sha256']);ck('capacity',sha(R/'gdt303_capacity.tsv')==d['capacity_sha256']);ck('manifest',sha(R/'gdt303_freeze_manifest.tsv')==d['freeze_manifest_sha256']);
for n,h in d['implementation'].items():ck('impl_'+n,sha(R/n)==h)
for x in read(R/'gdt303_freeze_manifest.tsv'):ck('manifest_'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256'])
rows=read(R/'gdt278_native_event_inventory.tsv');ck('f84source',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));cap=read(R/'gdt303_capacity.tsv');ck('powered',sum(x['capacity']=='POWERED' for x in cap)==29);ck('pairs',sum(int(x['pairs']) for x in cap)==314);(R/'gdt303_design_validation.json').write_text(json.dumps({'schema':'GDT303_DESIGN_VALIDATION_V1','status':'PASS','checks':len(checks),'design_sha256':sha(R/'gdt303_design.json')},indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))

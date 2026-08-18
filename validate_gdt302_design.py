#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
d=json.loads((R/'gdt302_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('content',d['content_sha256']==can(q));ck('status',d['status']=='FROZEN_BEFORE_GDT302_ROLE_SCORING');ck('thresholds',(d['form_min_events'],d['form_min_folios'],d['host_min_events'],d['host_min_scored_forms'])==(8,4,20,2));ck('no_substrings',d['substrings_mined']==0);ck('no_semantics',d['semantic_assignments']==0);ck('f84',not any(d['f84'].values()));ck('method',sha(R/'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_METHOD.md')==d['method_sha256']);ck('capacity',sha(R/'gdt302_capacity.tsv')==d['capacity_sha256']);ck('manifest',sha(R/'gdt302_freeze_manifest.tsv')==d['freeze_manifest_sha256']);
for n,h in d['implementation'].items():ck('impl_'+n,sha(R/n)==h)
for x in read(R/'gdt302_freeze_manifest.tsv'):ck('manifest_'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256'])
for f in ('gdt278_native_event_inventory.tsv','gdt276_event_inventory.tsv'):
 r=read(R/f);ck('f84_'+f,not any(x.get('page','').startswith('f84') or x.get('locus','').startswith('f84') for x in r))
(R/'gdt302_design_validation.json').write_text(json.dumps({'schema':'GDT302_DESIGN_VALIDATION_V1','status':'PASS','checks':len(checks),'design_sha256':sha(R/'gdt302_design.json')},indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))

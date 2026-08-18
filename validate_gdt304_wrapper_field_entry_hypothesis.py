#!/usr/bin/env python3
"""Independent arithmetic/provenance validation of post-hoc GDT304."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def close(a,b):return abs(float(a)-float(b))<2e-10
r=json.loads((R/'gdt304_result.json').read_text());q=dict(r);q.pop('content_sha256');ck('content',r['content_sha256']==can(q));
for g in ('inputs','documents','implementation','outputs'):
 for n,h in r[g].items():ck(g+'_'+n,sha(R/n)==h)
rows=read(R/'gdt278_native_event_inventory.tsv');ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));D=defaultdict(list)
for x in rows:
 if x['control_id']=='VOYNICH_REFERENCE':D[(x['page_host'],x['source_surface_sha256'])].append(x)
P=[x for x in read(R/'gdt303_pair_deltas.tsv') if x['operation'] in ('wrapper:ch>s','wrapper:d>s','wrapper:NONE>q')];F={'LINE_FIRST':lambda x:int(x['group_index'])==1,'LINE_LAST':lambda x:int(x['group_index'])==int(x['group_count']),'FIELD_FIRST':lambda x:x['within_field_position']=='FIRST','FIELD_LAST':lambda x:x['within_field_position']=='LAST','RECORD_ORDINAL_1':lambda x:int(x['record_ordinal'])==1,'FIELD_ORDINAL_1':lambda x:int(x['field_ordinal'])==1,'LINE_CLOSE':lambda x:x['line_close']=='1','PARAGRAPH_CLOSE':lambda x:x['paragraph_close']=='1'};H=defaultdict(lambda:defaultdict(list))
for p in P:
 a=D[(p['page_host'],p['source_surface_sha256'])];b=D[(p['page_host'],p['target_surface_sha256'])]
 for n,f in F.items():H[(p['operation'],p['page_host'])][n].append(sum(f(x) for x in b)/len(b)-sum(f(x) for x in a)/len(a))
stored={(x['operation'],x['endpoint']):x for x in read(R/'gdt304_endpoint_deltas.tsv')}
for o,n in stored:
 hs=[h for q,h in H if q==o];v=[sum(H[(o,h)][n])/len(H[(o,h)][n]) for h in hs];ck(o+n,close(stored[(o,n)]['mean_delta'],sum(v)/len(v)))
pred=json.loads((R/'gdt304_frozen_future_predictions.json').read_text());ck('predictions',len(pred['predictions'])==4 and not pred['f84_authorized']);ck('posthoc',r['provenance']=='POSTHOC_ENDPOINTS_INSPECTED_BEFORE_METHOD');ck('status',r['status']=='FIELD_ENTRY_WRAPPER_HYPOTHESIS_GENERATED_POSTHOC');ck('report',r['status'] in (R/'GDT304_WRAPPER_FIELD_ENTRY_HYPOTHESIS_REPORT.md').read_text());val={'schema':'GDT304_VALIDATION_V1','status':'PASS','checks':len(checks),'result_sha256':sha(R/'gdt304_result.json'),'result_content_sha256':r['content_sha256'],'scope':'INDEPENDENT_SOURCE_ENDPOINT_ARITHMETIC_PROVENANCE_HASH_RECONSTRUCTION'};(R/'gdt304_validation.json').write_text(json.dumps(val,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))

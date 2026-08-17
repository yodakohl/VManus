#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt249_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
m=list(csv.DictReader((R/'gdt249_cross_scope_layer_correction.tsv').open(),delimiter='\t'));s=list(csv.DictReader((R/'gdt249_corrected_candidate_status.tsv').open(),delimiter='\t'))
ck(len(m)==3);o=next(r for r in m if r['source_group']=='okal');ck((o['parsed_page_host'],o['right_family'])==('ok','al'));ck(o['gdt248_state']=='INVALIDLY_MAPPED_TO_PAGE_HOST_OKAL')
ck([(r['page_host'],int(r['window_occurrences']),int(r['physical_folios'])) for r in s]==[('ok',834,69),('olky',11,9),('okaly',18,15)])
ck(next(r for r in s if r['page_host']=='ok')['sections']=='B:289;C:3;H:139;P:10;S:334;T:59');ck(all(r['semantic_value']=='UNASSIGNED' for r in s));ck(z['gdt247_exact_source_group_reuse_retained']);ck(z['active_semantic_assignments']==0)
ck(z['status']=='GDT248_OKAL_Q13_STARS_LEAD_WITHDRAWN_SOURCE_GROUP_PAGE_HOST_LAYER_CONFLATION');ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt249_result.json')};(R/'gdt249_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

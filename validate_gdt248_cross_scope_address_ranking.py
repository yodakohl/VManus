#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt248_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
r=list(csv.DictReader((R/'gdt248_cross_scope_address_candidates.tsv').open(),delimiter='\t'));c=list(csv.DictReader((R/'gdt248_address_counterexamples.tsv').open(),delimiter='\t'))
ck([x['page_host'] for x in r]==['okal','olky','okaly']);ck([int(x['window_occurrences']) for x in r]==[4,11,18]);ck([int(x['window_physical_folios']) for x in r]==[4,9,15]);ck(sum(int(x['unique_window_contexts']) for x in r)==33);ck(all(int(x['gdt165_stable_directed_relations'])==0 for x in r));ck(all(x['semantic_value']=='UNASSIGNED' for x in r));ck(len(c)==5)
ck(next(x for x in r if x['page_host']=='okal')['sections']=='S:4');ck(next(x for x in r if x['page_host']=='olky')['currier']=='B:11');ck(next(x for x in r if x['page_host']=='okaly')['sections']=='B:7;H:3;S:7;T:1')
ck(z['active_semantic_assignments']==0);ck(z['stable_directed_relations']==0);ck(z['status']=='OKAL_LOW_CAPACITY_Q13_STARS_ADDRESS_LEAD_OTHERS_FORMAL_OR_REGISTER_LIKE');ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt248_result.json')};(R/'gdt248_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

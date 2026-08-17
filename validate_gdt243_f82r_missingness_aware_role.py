#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt243_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
rr=list(csv.DictReader((R/'gdt243_f82r_missingness_role_projection.tsv').open(),delimiter='\t'));pp=list(csv.DictReader((R/'gdt243_f82r_paragraph_uncertainty.tsv').open(),delimiter='\t'));ss=list(csv.DictReader((R/'gdt243_role_summary.tsv').open(),delimiter='\t'))
ck(len(rr)==z['fields']==51);ck(len(pp)==3);ck(sum(int(x['robust_under_missingness']) for x in rr)==z['robust_fields']);ck(sum(x['robust_under_missingness']=='0' for x in rr)==z['unresolved_fields'])
ck(Counter(x['robust_abstract_role_like'] for x in rr)==Counter(z['role_counts']));ck(all(int(x['feasible_coordinates'])>0 for x in rr));ck(all(x['semantic_value']=='UNASSIGNED' for x in rr));ck(all(x['page']=='f82r' for x in rr))
ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt243_result.json')};(R/'gdt243_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

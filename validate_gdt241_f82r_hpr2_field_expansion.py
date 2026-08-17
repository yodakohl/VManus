#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt241_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
ff=list(csv.DictReader((R/'gdt241_f82r_hpr2_fields.tsv').open(),delimiter='\t'));ll=list(csv.DictReader((R/'gdt241_f82r_line_coverage.tsv').open(),delimiter='\t'))
ck(len(ll)==z['hpr2_covered_loci']==17);ck(len(ff)==z['hpr2_fields']);ck(sum(int(x['gdt229_role_available']) for x in ll)==z['prior_role_scaffold_loci']==8);ck(z['new_formal_only_loci']==9)
ck(sum(x['overlap_exact_match']=='1' for x in ll)==z['overlap_exact_loci']==8);ck(all(x['semantic_role']=='UNASSIGNED' for x in ff));ck(all(x['page']=='f82r' for x in ff+ll))
ck(all(not x['locus'].startswith('f84') for x in ff));ck(z['f84']=={'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt241_result.json')};(R/'gdt241_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt242_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
rr=list(csv.DictReader((R/'gdt242_f82r_paragraph_coordinate.tsv').open(),delimiter='\t'));cc=list(csv.DictReader((R/'gdt242_f82r_record_correction.tsv').open(),delimiter='\t'))
ck(len(rr)==32);ck(len(cc)==3);ck(z['paragraph_starts']==['f82r.1','f82r.11','f82r.20']);ck(z['paragraph_line_counts']==[9,9,14])
ck(z['hpr2_covered_by_paragraph']==[6,5,6]);ck(z['hpr2_fields_by_paragraph']==[17,17,17]);ck(z['historical_role_loci_by_paragraph']==[4,1,3]);ck(z['historical_gdt229_record_ids']==['Q13|f82r|R01'])
ck(all(x['correction_state'].startswith('PARAGRAPH_BOUNDARY_MISSING') for x in cc));ck(z['status']=='GDT229_F82R_RECORD_COORDINATE_INVALID_THREE_PARAGRAPHS_COLLAPSED')
ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt242_result.json')};(R/'gdt242_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

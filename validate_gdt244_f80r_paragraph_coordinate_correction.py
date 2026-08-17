#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt244_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
rr=list(csv.DictReader((R/'gdt244_f80r_paragraph_coordinate.tsv').open(),delimiter='\t'));cc=list(csv.DictReader((R/'gdt244_f80r_record_correction.tsv').open(),delimiter='\t'))
ck(len(rr)==43);ck(len(cc)==5);ck(z['paragraph_starts']==['f80r.11','f80r.28','f80r.34','f80r.40','f80r.47']);ck(z['single_reading_disagreement']==['f80r.18'])
ck(z['paragraph_line_counts']==[17,6,6,7,7]);ck(z['historical_role_loci_by_paragraph']==[7,2,1,3,1]);ck(z['historical_records']==['Q13|f80r|R01','Q13|f80r|R02'])
ck(all(x['correction_state']=='PARAGRAPH_COLLAPSED_IN_HISTORICAL_ROLE_COORDINATE' for x in cc));ck(z['status']=='GDT229_F80R_RECORD_COORDINATE_INVALID_FIVE_PARAGRAPHS_COLLAPSED_TO_TWO')
ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt244_result.json')};(R/'gdt244_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt240_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
rr=list(csv.DictReader((R/'gdt240_f82r_complete_locus_inventory.tsv').open(),delimiter='\t'));ss=list(csv.DictReader((R/'gdt240_f82r_coverage_summary.tsv').open(),delimiter='\t'))
ck(len(rr)==45);ck(sum(x['kind']=='P' for x in rr)==32);ck(sum(x['kind']=='L' for x in rr)==13);ck(len({x['locus'] for x in rr})==45)
ck(Counter(x['coverage_state'] for x in rr)==Counter({'STRICT_EXACT_FAMILY':29,'NO_EXACT_FAMILY_CONSENSUS':11,'EXACT_FAMILY_WITH_ALTERNATIVE':5}))
ck(Counter(x['coverage_state'] for x in rr if x['kind']=='P')==Counter({'STRICT_EXACT_FAMILY':19,'NO_EXACT_FAMILY_CONSENSUS':11,'EXACT_FAMILY_WITH_ALTERNATIVE':2}))
ck(sum(int(x['gdt229_semantic_scaffold_coverage']) for x in rr if x['kind']=='P')==8);ck(sum(int(x['gdt239_label_dossier_coverage']) for x in rr)==13)
ck(all(x['semantic_value']=='UNASSIGNED' for x in rr));ck(all(not x['page'].startswith('f84') for x in rr));ck(z['semantic_scaffold_fraction']==.25)
ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt240_result.json')};(R/'gdt240_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

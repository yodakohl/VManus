#!/usr/bin/env python3
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
R = Path(__file__).resolve().parent; checks=[]
def ck(x): checks.append(bool(x)); assert x
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt246_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items(): ck(sha(p)==h)
inv=list(csv.DictReader((R/'gdt246_f80r_complete_locus_inventory.tsv').open(),delimiter='\t'))
par=list(csv.DictReader((R/'gdt246_f80r_paragraph_coverage.tsv').open(),delimiter='\t'))
rec=list(csv.DictReader((R/'gdt246_f80r_label_prose_recurrence.tsv').open(),delimiter='\t'))
ck(len(inv)==53);ck(len({r['locus'] for r in inv})==53);ck(sum(r['kind']=='L' for r in inv)==10);ck(sum(r['kind']=='P' for r in inv)==43)
ck(Counter(r['coverage_state'] for r in inv)==Counter({'STRICT_EXACT_FAMILY':33,'NO_EXACT_FAMILY_CONSENSUS':19,'EXACT_FAMILY_WITH_ALTERNATIVE':1}))
ck(Counter(r['coverage_state'] for r in inv if r['kind']=='P')==Counter({'STRICT_EXACT_FAMILY':25,'NO_EXACT_FAMILY_CONSENSUS':17,'EXACT_FAMILY_WITH_ALTERNATIVE':1}))
ck(Counter(r['coverage_state'] for r in inv if r['kind']=='L')==Counter({'STRICT_EXACT_FAMILY':8,'NO_EXACT_FAMILY_CONSENSUS':2}))
ck([int(r['physical_prose_loci']) for r in par]==[17,6,6,7,7]);ck([int(r['strict_exact_family_loci']) for r in par]==[10,4,2,6,3])
ck(sum(r['transferred_label_prediction']=='1' for r in inv if r['kind']=='L')==7)
ck([r['family_surface'] for r in rec]==['ABQA','AQABA','AQAC']);ck(sum(int(r['label_occurrences']) for r in rec)==4);ck(sum(int(r['prose_group_occurrences']) for r in rec)==5)
ck(all(r['semantic_value']=='UNASSIGNED' for r in inv+rec));ck(all(r['historical_role_state']=='SUSPENDED_COORDINATE_INVALID' for r in inv if r['kind']=='P'))
ck(all('|' not in r['family_expression'] or int(r['consensus_group_count'])>1 for r in inv))
ck(z['active_semantic_assignments']==0);ck(z['status']=='F80R_COMPLETE_FORMAL_CENSUS_THREE_LABEL_FAMILIES_RECUR_IN_PROSE_NO_SEMANTIC_KEY')
ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt246_result.json')}
(R/'gdt246_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

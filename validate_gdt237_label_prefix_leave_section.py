#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent; checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt237_result.json').read_text())
for p,h in z['inputs'].items():ck(sha(p)==h)
for p,h in z['outputs'].items():ck(sha(p)==h)
for p,h in z['documents'].items():ck(sha(p)==h)
for p,h in z['implementation'].items():ck(sha(p)==h)
folds=list(csv.DictReader((R/'gdt237_section_folds.tsv').open(),delimiter='\t'))
pred=list(csv.DictReader((R/'gdt237_predictions.tsv').open(),delimiter='\t'))
stab=list(csv.DictReader((R/'gdt237_prefix_stability.tsv').open(),delimiter='\t'))
ck(len(folds)==8);ck(sum(int(x['test_rows']) for x in folds)==z['rows']==3857)
ck(sum(int(x['test_labels']) for x in folds)==z['labels']==741);ck(len(pred)==z['rows'])
for x in folds:
 rr=[y for y in pred if y['held_section']==x['held_section']]
 ck(len(rr)==int(x['test_rows']));ck(sum(int(y['true_label']) for y in rr)==int(x['test_labels']))
 ck(sum(int(y['predicted_label']) for y in rr)==int(x['predicted_positive']))
ck(sum(int(x['tp']) for x in folds)==z['pooled']['tp']);ck(sum(int(x['fp']) for x in folds)==z['pooled']['fp'])
ck(all(int(x['selected_folds'])<=8 for x in stab));ck(z['f84']=={'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
out={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt237_result.json')}
(R/'gdt237_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

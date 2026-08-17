#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt238_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
inv=list(csv.DictReader((R/'gdt238_relation_inventory.tsv').open(),delimiter='\t'));fold=list(csv.DictReader((R/'gdt238_relation_folds.tsv').open(),delimiter='\t'));summary=list(csv.DictReader((R/'gdt238_relation_summary.tsv').open(),delimiter='\t'))
ck(len(inv)==z['inventory_rows']==310);ck(len({x['physical_folio'] for x in inv})==z['folios'])
ck(Counter(x['relation_class'] for x in inv)==Counter(z['relation_classes']))
ck(len(z['stable_prefixes'])==7);ck(all(not x['page'].startswith('f84') for x in inv))
p=next(x for x in summary if x['model']=='STABLE_PREFIX');ck(int(p['covered'])==68);ck(int(p['feature_correct'])==56);ck(int(p['baseline_correct'])==51);ck(int(p['paired_wins'])==5);ck(int(p['paired_losses'])==0)
r=next(x for x in summary if x['model']=='RAW_FAMILY');ck(int(r['covered'])==112);ck(int(r['feature_correct'])==65);ck(int(r['baseline_correct'])==80)
ck(z['status']=='WEAK_PREFIX_RELATION_MODE_LEAD_LOW_CAPACITY');ck(z['f84']=={'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
out={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt238_result.json')};(R/'gdt238_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

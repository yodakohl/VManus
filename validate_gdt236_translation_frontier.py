#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parent
checks=[]
def ck(x): checks.append(bool(x)); assert x
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
res=json.loads((R/'gdt236_result.json').read_text())
ck(res['status']=='HYBRID_RECORD_COMPILER_LEADS_CONTENT_CHANNEL_UNRESOLVED')
ck(res['f84']=={'input':False,'new_access':False,'prediction_target':False,'retained':False,'scored':False})
for p,h in res['inputs'].items(): ck(sha(p)==h); ck(not p.lower().startswith('f84'))
for p,h in res['outputs'].items(): ck(sha(p)==h)
for p,h in res['documents'].items(): ck(sha(p)==h)
for p,h in res['implementation'].items(): ck(sha(p)==h)
layers=list(csv.DictReader((R/'gdt236_layer_status.tsv').open(),delimiter='\t'))
ck(len(layers)==9); ck(sum(x['status']=='UNIDENTIFIED' for x in layers)==1)
ck(next(x for x in layers if x['layer']=='LOCAL_DIAGRAM_STATE')['status']=='DEMOTED_DESCRIPTIVE')
ck(next(x for x in layers if x['layer']=='LABEL_RESIDUAL')['status']=='REGISTER_BOUND_OPAQUE')
theories=list(csv.DictReader((R/'gdt236_theory_comparison.tsv').open(),delimiter='\t'))
ck(len(theories)==3); ck(sum(x['rank']=='1_LEADING' for x in theories)==1)
preds=list(csv.DictReader((R/'gdt236_prediction_registry.tsv').open(),delimiter='\t'))
ck(len(preds)==6); ck(all('f84' not in json.dumps(x).lower() for x in preds))
core=dict(res); got=core.pop('content_hash')
ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
out={'experiment':res['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt236_result.json')}
(R/'gdt236_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(f"PASS {len(checks)}/{len(checks)}")

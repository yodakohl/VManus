#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt250_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
r=list(csv.DictReader((R/'gdt250_candidate_semantic_roles.tsv').open(),delimiter='\t'));e=list(csv.DictReader((R/'gdt250_candidate_evidence.tsv').open(),delimiter='\t'));c=list(csv.DictReader((R/'gdt250_counterexamples.tsv').open(),delimiter='\t'))
ck(len(r)==2);ck(len(e)==6);ck(len(c)==6);ok=[x for x in e if x['page_host']=='okaly'];ol=[x for x in e if x['page_host']=='olky'];ck(len(ok)==4 and len({x['physical_folio'] for x in ok})==2);ck(all(x['figure_tag']=='1' for x in ok));ck(sum(x['certainty']=='HEDGED' for x in ok)==3);ck(len(ol)==2 and {x['object_class'] for x in ol}=={'FIGURE_ONLY','PLANT'});ck(r[0]['classification']=='PROVISIONAL_LOW_INDEPENDENCE');ck(r[1]['classification']=='FAILED_COUNTEREXAMPLE');ck(z['hypotheses_generated']==1 and z['active_semantic_assignments']==0);ck(z['status']=='OKALY_PROVISIONAL_FIGURE_CLASS_DESCRIPTOR_TWO_FOLIO_HYPOTHESIS_OLKY_OBJECT_GLOSS_FAILED');ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt250_result.json')};(R/'gdt250_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

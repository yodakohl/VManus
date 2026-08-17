#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt252_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
s=list(csv.DictReader((R/'gdt252_ten_slot_slot4_inventory.tsv').open(),delimiter='\t'));e=list(csv.DictReader((R/'gdt252_okal_ab_position_evidence.tsv').open(),delimiter='\t'));c=list(csv.DictReader((R/'gdt252_counterexamples.tsv').open(),delimiter='\t'))
ck(len(s)==8);ck(sum(r['coverage_state']=='FORMAL_COVERED' for r in s)==7);ck(sum(r['okal_plus_ab_candidate']=='1' for r in s)==2);ck(sum(r['catalogue_homolog']=='KLUGE_09A' and r['coverage_state']=='FORMAL_COVERED' for r in s)==4);ck([(r['locus'],r['token']) for r in e]==[('f70v1.5','okalal'),('f72r1.5','okalam')]);ck(all(r['raw_family']=='AQABAB' and r['slot_index']=='4' and r['slot_count']=='10' for r in e));ck(all(r['catalogue_homolog']=='KLUGE_09A' for r in e));ck(len(c)==7);ck(z['kluge_09a_formal_covered']==4 and z['kluge_09a_candidate_positive']==2);ck(z['broader_family_counterexample']=={'locus':'f70v2.25','slot_count':10,'slot_index':3,'token':'otalam'});ck(z['active_semantic_assignments']==0);ck(z['status']=='POSTHOC_OKAL_PLUS_AB_SLOT4_OF_10_POSITION_LEAD_TWO_FOLIOS_NOT_VALIDATED');ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt252_result.json')};(R/'gdt252_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')

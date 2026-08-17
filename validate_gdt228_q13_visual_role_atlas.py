#!/usr/bin/env python3
"""Integrity and arithmetic validation for GDT228 postselected atlas."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt228_result.json';OUT=R/'gdt228_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='MULTI_REGION_SHORT_ARGUMENT_LEAD_POSTSELECTED_LOW_CAPACITY');ck('postselection',r['postselection']=='FULLY_DISCLOSED_TWO_AXES_SIX_ENDPOINTS')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
m=read(R/'gdt228_visual_feature_manifest.tsv');ck('manifest',len(m)==18 and len({x['page'] for x in m})==18 and {x['physical_folio'] for x in m}=={f'f{i}' for i in range(75,84)});ck('no_f84_manifest',not any(x['page'].startswith('f84') for x in m));ck('states',sum(int(x['multiple_bounded_regions']) for x in m)==7 and sum(int(x['explicit_linear_path']) for x in m)==11)
p=read(R/'gdt228_page_role_profiles.tsv');ck('profiles',len(p)==18 and {x['page'] for x in p}=={x['page'] for x in m});ck('fields',sum(int(x['fields']) for x in p)==701==r['fields'])
s=read(R/'gdt228_visual_role_scores.tsv');ck('scores',len(s)==6);top=max(s,key=lambda x:abs(float(x['observed_effect'])));ck('top',top['visual_feature']=='multiple_bounded_regions' and top['abstract_role']=='INSTRUCTION_CLAUSE_LIKE' and abs(float(top['observed_effect'])+0.0940713133157)<1e-11);ck('local',abs(float(top['exact_two_sided_p'])-0.100835847159)<1e-11);ck('within',top['discordant_folios']=='3' and top['within_folio_worlds']=='8' and abs(float(top['within_folio_two_sided_p'])-.125)<1e-12);ck('lofo',top['lofo_same_direction']=='9');ck('max6',abs(float(top['max_six_p'])-.385986328125)<1e-12)
null=read(R/'gdt228_null_results.tsv');ck('null',len(null)==6 and all(x['max_six_worlds']=='4096' for x in null));ck('counterexamples',len(read(R/'gdt228_counterexamples.tsv'))==6)
ck('f84',r['f84']=={'public_metadata_previously_exposed':True,'manifest_rows':0,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False})
v={'schema':'GDT228_VALIDATION_V1','status':'PASS','scope':'RETAINED_MANIFEST_SCORE_AND_NULL_INTEGRITY_NOT_INDEPENDENT_VISUAL_REANNOTATION','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

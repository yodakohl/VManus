#!/usr/bin/env python3
"""Integrity and arithmetic validation of GDT226 retained projections."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt226_result.json';OUT=R/'gdt226_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='Q13_RECIPE_ROLE_SPECIFICITY_PROVISIONAL');ck('secondary',r['secondary_status']=='REGISTER_AND_RECORD_SIZE_CONFOUNDED')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
p=read(R/'gdt226_field_role_projection.tsv');scopes={'HERBAL_A','HERBAL_B','STARS_B','OTHER_A','Q13','OTHER_B'}
ck('scopes',{x['scope'] for x in p}==scopes)
ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in p))
ck('unique_fields',len({(x['record_id'],x['field_ordinal']) for x in p})==len(p))
profiles=read(R/'gdt226_scope_profiles.tsv');ck('six_profiles',len(profiles)==6 and {x['scope'] for x in profiles}==scopes)
for x in profiles:
 s=x['scope'];z=[y for y in p if y['scope']==s];ck('fields_'+s,len(z)==int(x['fields'])==r['scope_profiles'][s]['fields']);ck('records_'+s,len({y['record_id'] for y in z})==int(x['records'])==r['scope_profiles'][s]['records'])
 for role in ('opener','operation','ingredient','tool','closer'):ck(role+'_'+s,sum(y['predicted_role_like']==role.upper() for y in z)==int(x[role+'_fields']))
ranks=sorted(profiles,key=lambda x:int(x['recipe_js_rank']));ck('ranks',[int(x['recipe_js_rank']) for x in ranks]==list(range(1,7)));ck('q13_rank',ranks[0]['scope']=='Q13' and r['q13_recipe_js_rank']==1);ck('stars_rank',ranks[1]['scope']=='STARS_B')
pairs=read(R/'gdt226_pairwise_distances.tsv');ck('pairs',len(pairs)==15);q=[x for x in pairs if x['scope_a']=='Q13' or x['scope_b']=='Q13'];ck('q_pairs',len(q)==5);nearest=min(q,key=lambda x:float(x['js_divergence']));ck('nearest',set((nearest['scope_a'],nearest['scope_b']))=={'Q13','STARS_B'} and r['q13_nearest_other_scope']=='STARS_B')
size=read(R/'gdt226_size_matched.tsv');ck('size_rows',len(size)==44);ck('size_scopes',{x['comparator_scope'] for x in size}==scopes-{'Q13'})
for s in scopes-{'Q13'}:
 z=[x for x in size if x['comparator_scope']==s];m=sum(float(x['q13_advantage']) for x in z)/len(z);ck('size_'+s,len(z)==r['size_matched_sensitivity'][s]['shared_size_strata'] and abs(m-r['size_matched_sensitivity'][s]['mean_q13_advantage'])<1e-11)
lofo=read(R/'gdt226_lofo.tsv');ck('lofo',len(lofo)==9 and sum(int(x['all_three_hit']) for x in lofo)==9==r['lofo_all_three_hits']);ck('lofo_nearest',all(x['nearest_other_scope']=='STARS_B' for x in lofo))
ck('predictions',r['prediction_hits']=={'P1':True,'P2':True,'P3':True});ck('gates',r['gates']=={'P1':True,'P2':True,'P3':True,'at_least_eight_lofo':True})
ck('counterexamples',len(read(R/'gdt226_counterexamples.tsv'))==7);ck('freeze',r['freeze_commit']=='80181f9')
ck('f84',r['f84']=={'public_metadata_previously_exposed':True,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False})
v={'schema':'GDT226_VALIDATION_V1','status':'PASS','scope':'RETAINED_PROJECTION_INTEGRITY_AND_ARITHMETIC_NOT_INDEPENDENT_MODEL_REFIT','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

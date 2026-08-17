#!/usr/bin/env python3
"""Integrity and arithmetic validation for GDT224 retained projections."""
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt224_result.json';OUT=R/'gdt224_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def js(a,b):
 a=[x/sum(a) for x in a];b=[x/sum(b) for x in b];m=[(x+y)/2 for x,y in zip(a,b)]
 def kl(x,y):return sum(v*math.log2(v/w) for v,w in zip(x,y) if v>0)
 return (kl(a,m)+kl(b,m))/2
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='Q13_RECIPE_ROLE_ARCHITECTURE_WEAK_OR_GENERIC')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
p=read(R/'gdt224_field_role_projection.tsv');q=[x for x in p if x['scope']=='Q13'];h=[x for x in p if x['scope']=='HERBAL_B2']
ck('field_counts',len(q)==701 and len(h)==163 and r['target']['fields']==701 and r['control']['fields']==163)
ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in p))
recs=read(R/'gdt224_record_role_summary.tsv');qr=[x for x in recs if x['scope']=='Q13'];hr=[x for x in recs if x['scope']=='HERBAL_B2'];ck('record_counts',len(qr)==33 and len(hr)==22)
def folio_mean(rows,key):
 fs={x['physical_folio'] for x in rows};return sum(sum(int(x[key]) for x in rows if x['physical_folio']==f)/sum(1 for x in rows if x['physical_folio']==f) for f in fs)/len(fs)
mixed=folio_mean(qr,'mixed_clause_argument')-folio_mean(hr,'mixed_clause_argument');closer=folio_mean(qr,'final_closer_like')-folio_mean(hr,'final_closer_like')
ck('mixed_effect',abs(mixed-r['raw_effects']['MIXED_CLAUSE_ARGUMENT'])<1e-12)
ck('closer_effect',abs(closer-r['raw_effects']['FINAL_CLOSER'])<1e-12)
classes=('OPENER','OPERATION','INGREDIENT','TOOL','CLOSER');ext=[r['external_predicted_class_counts'][c] for c in classes]
qc=Counter(x['predicted_role_like'] for x in q);hc=Counter(x['predicted_role_like'] for x in h);adv=js([hc[c] for c in classes],ext)-js([qc[c] for c in classes],ext);ck('js_advantage',abs(adv-r['raw_effects']['RECIPE_JS_ADVANTAGE'])<1e-12)
scores=read(R/'gdt224_scope_comparison.tsv');ck('three_scores',len(scores)==3)
null=read(R/'gdt224_null_results.tsv');ck('null_worlds',len(null)==3 and all(int(x['worlds'])==4096 for x in null))
ck('directions',r['gates']=={'all_three_raw_directions':False,'at_least_eight_lofo_all_three':False,'at_least_two_size_directions':False})
ck('lofo',r['lofo_total']==9 and r['lofo_all_three_positive']==0 and r['lofo_positive_by_endpoint']=={'FINAL_CLOSER':0,'MIXED_CLAUSE_ARGUMENT':9,'RECIPE_JS_ADVANTAGE':9})
ck('freeze_commit',r['freeze_commit']=='f51a140')
ck('claim','translation' not in r['interpretation'].lower() and 'plaintext' not in r['interpretation'].lower())
ck('f84_flags',not any(r['f84'].values()))
v={'schema':'GDT224_VALIDATION_V1','status':'PASS','scope':'RETAINED_PROJECTION_INTEGRITY_AND_ARITHMETIC_NOT_INDEPENDENT_MODEL_REFIT','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

#!/usr/bin/env python3
"""Integrity and arithmetic validation for GDT227 abstract interlinear."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt227_result.json';OUT=R/'gdt227_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='ABSTRACT_Q13_INTERLINEAR_BUILT_IDENTITY_PLACEMENT_DESCRIPTIVE');ck('secondary',r['secondary_status']=='Q13_IDENTITY_SLOT_STABLE_CROSS_REGISTER_PAGE_HOST_TRANSFER_NULL')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
i=read(R/'gdt227_q13_abstract_interlinear.tsv');ck('fields',len(i)==701==r['q13_fields']);ck('unique',len({(x['record_id'],x['field_ordinal']) for x in i})==701);ck('scope',all(x['scope']=='Q13' for x in i));ck('no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in i));ck('groups',sum(int(x['field_group_count']) for x in i)==1896==r['q13_group_occurrences'])
for x in i:ck('pipes_'+x['record_id']+'_'+x['field_ordinal'],len(x['source_tokens'].split('|'))==len(x['page_hosts'].split('|'))==len(x['compiler_cells'].split('|'))==int(x['field_group_count']))
a=read(R/'gdt227_identity_role_atlas.tsv');qh=[x for x in a if x['scope']=='Q13' and x['identity_level']=='PAGE_HOST' and int(x['cross_folio'])];stable=[x for x in qh if int(x['occurrences'])>=5 and float(x['dominant_purity'])>=.8];ck('cross_folio',len(qh)==130==r['q13_cross_folio_page_hosts']);ck('stable',len(stable)==38==r['q13_recurrent_role_stable_page_hosts'])
for x in a:ck('atlas_sum_'+x['scope']+'_'+x['identity_level']+'_'+x['identity'],sum(int(x[k]) for k in ('instruction','argument','closer','unresolved'))==int(x['occurrences']))
t=read(R/'gdt227_cross_register_transfer.tsv');ck('six_transfer',len(t)==6)
for x in t:
 key=(x['identity_level']+'_Q13_LOFO') if x['train_scope']=='Q13_OTHER_FOLIOS' else f"{x['identity_level']}_{x['train_scope']}_TO_{x['test_scope']}";z=r['placement_scores'][key];ck('transfer_'+key,int(x['predictions'])==z['predictions'] and int(x['correct'])==z['correct'] and abs(float(x['accuracy'])-z['accuracy'])<1e-11 and abs(float(x['gain_over_training_prior'])-z['gain_over_training_prior'])<1e-11)
ck('q13_host_gain',abs(r['placement_scores']['PAGE_HOST_Q13_LOFO']['gain_over_training_prior']-0.08058823529411763)<1e-12)
ck('q13_to_stars_null',r['placement_scores']['PAGE_HOST_Q13_TO_STARS_B']['gain_over_training_prior']<0)
ck('counterexamples',len(read(R/'gdt227_counterexamples.tsv'))==5)
ck('f84',r['f84']=={'public_metadata_previously_exposed':True,'raw_rows_rejected_before_parse':True,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False})
v={'schema':'GDT227_VALIDATION_V1','status':'PASS','scope':'RETAINED_INTERLINEAR_INTEGRITY_AND_ARITHMETIC_NOT_INDEPENDENT_HPR2_REPARSE','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

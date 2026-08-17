#!/usr/bin/env python3
"""Integrity and arithmetic validation for the retained GDT225 closure atlas."""
import csv,hashlib,json
from pathlib import Path

R=Path(__file__).resolve().parent
RES=R/'gdt225_result.json';OUT=R/'gdt225_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
def rate(rows,key,cond=lambda x:True):
 z=[x for x in rows if cond(x)];return sum(int(x[key]) for x in z)/len(z)
def balanced(rows,key):
 fs=sorted({x['physical_folio'] for x in rows});return sum(rate([x for x in rows if x['physical_folio']==f],key) for f in fs)/len(fs)

r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='DISTRIBUTED_CLOSURE_PARTIAL_OR_GENERIC')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('doc_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('impl_'+n,sha(R/n)==h)
a=read(R/'gdt225_record_closure_atlas.tsv');q=[x for x in a if x['scope']=='Q13'];h=[x for x in a if x['scope']=='HERBAL_B2']
ck('records',len(a)==55 and len(q)==33 and len(h)==22)
ck('unique_records',len({x['record_id'] for x in a})==55)
ck('no_f84',not any(x['page'].startswith('f84') or x['final_prose_locus'].startswith('f84') for x in a))
for x in a:
 ck('boolean_'+x['record_id'],all(x[k] in ('0','1') for k in ('field_closer_like','missing_field_closer','final_line_b3','following_label_block','distributed_closure_proxy','expanded_closure')))
 ck('complement_'+x['record_id'],int(x['field_closer_like'])+int(x['missing_field_closer'])==1)
 ck('proxy_'+x['record_id'],int(x['distributed_closure_proxy'])==int(bool(int(x['final_line_b3']) or int(x['following_label_block']))))
 ck('expanded_'+x['record_id'],int(x['expanded_closure'])==int(bool(int(x['field_closer_like']) or int(x['distributed_closure_proxy']))))
counts={'q13_records':len(q),'herbal_records':len(h),'q13_field_closers':sum(int(x['field_closer_like']) for x in q),'herbal_field_closers':sum(int(x['field_closer_like']) for x in h),'q13_b3':sum(int(x['final_line_b3']) for x in q),'herbal_b3':sum(int(x['final_line_b3']) for x in h),'q13_following_label_blocks':sum(int(x['following_label_block']) for x in q),'herbal_following_label_blocks':sum(int(x['following_label_block']) for x in h),'q13_proxies':sum(int(x['distributed_closure_proxy']) for x in q),'herbal_proxies':sum(int(x['distributed_closure_proxy']) for x in h),'q13_expanded_closures':sum(int(x['expanded_closure']) for x in q),'herbal_expanded_closures':sum(int(x['expanded_closure']) for x in h)}
ck('counts',counts==r['counts'])
qm=rate(q,'distributed_closure_proxy',lambda x:int(x['missing_field_closer']));hm=rate(h,'distributed_closure_proxy',lambda x:int(x['missing_field_closer']));qc=rate(q,'distributed_closure_proxy',lambda x:int(x['field_closer_like']))
rb=rate(h,'field_closer_like')-rate(q,'field_closer_like');re=rate(h,'expanded_closure')-rate(q,'expanded_closure');rs=(rb-re)/rb
fb=balanced(h,'field_closer_like')-balanced(q,'field_closer_like');fe=balanced(h,'expanded_closure')-balanced(q,'expanded_closure');fs=(fb-fe)/fb
expected={'missing_proxy_q13_minus_herbal':qm-hm,'q13_proxy_missing_minus_field_closer':qm-qc,'record_weighted_baseline_deficit':rb,'record_weighted_expanded_deficit':re,'record_weighted_deficit_shrink':rs,'folio_balanced_baseline_deficit':fb,'folio_balanced_expanded_deficit':fe,'folio_balanced_deficit_shrink':fs}
ck('effects',all(abs(expected[k]-r['effects'][k])<1e-12 for k in expected))
scores=read(R/'gdt225_closure_scores.tsv');ck('scores',len(scores)==4 and sum(int(x['direction_hit']) for x in scores)==3)
lofo=read(R/'gdt225_lofo.tsv');ck('lofo_rows',len(lofo)==9);ck('lofo_hits',sum(int(x['all_three_hit']) for x in lofo)==4==r['lofo_all_three_hits'])
ck('gates',r['gates']=={'q13_missing_proxy_higher':True,'q13_missing_enrichment':True,'record_weighted_half_deficit_reduction':True,'folio_balanced_half_deficit_reduction':False,'at_least_eight_lofo':False})
ck('counterexamples',len(read(R/'gdt225_counterexamples.tsv'))==5)
ck('freeze',r['freeze_commit']=='f9ed5f1')
ck('f84_flags',not any(r['f84'].values()))
v={'schema':'GDT225_VALIDATION_V1','status':'PASS','scope':'RETAINED_ATLAS_INTEGRITY_AND_ARITHMETIC_NOT_INDEPENDENT_SOURCE_RECONSTRUCTION','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")

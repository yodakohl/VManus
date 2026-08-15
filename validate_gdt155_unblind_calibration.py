#!/usr/bin/env python3
"""Independent integrity/arithmetic validator for GDT155 unblind calibration."""
from __future__ import annotations
import csv,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
R=ROOT/'gdt155_unblind_calibration_result.json';S=ROOT/'gdt155_abbreviation_recovery.tsv';E=ROOT/'gdt155_abbreviation_counterexamples.tsv';O=ROOT/'gdt155_operation_correspondence.tsv';D=ROOT/'gdt155_unblind_retrieval.tsv';A=ROOT/'gdt155_unblind_retrieval_summary.tsv';V=ROOT/'gdt155_unblind_calibration_validation.json'

def read(p):
    with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
checks=[]
def ck(name,ok,detail):checks.append({'check':name,'ok':bool(ok),'detail':detail});assert ok,(name,detail)

r=json.loads(R.read_text());s=read(S);e=read(E);o=read(O);d=read(D);a=read(A)
ck('schema',r['schema']=='GDT155_UNBLIND_CALIBRATION_RESULT_V1',r['schema']);ck('status',r['status']=='REAL_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_CALIBRATED',r['status']);ck('chronology',r['chronology']=={'source_freeze_commit':'d62de97','blind_analysis_commit':'99bab66','truth_export_commit':'3374596','unblind_scoring_after_all':True},r['chronology']);ck('external_counts',r['counts']['lines']==48347 and r['counts']['sites']==119064 and r['counts']['records']==3178,r['counts']);ck('line_alignment',r['counts']['aligned_group_lines']+r['counts']['unaligned_group_lines']==48347,r['counts'])
for name,digest in r['inputs'].items():ck('input_hash_'+name,sha(ROOT/name)==digest,digest)
for name,digest in r['outputs'].items():ck('output_hash_'+name,sha(ROOT/name)==digest,digest)
for name,digest in r['documents'].items():ck('document_hash_'+name,sha(ROOT/name)==digest,digest)
for name,digest in r['implementation'].items():ck('implementation_hash_'+name,sha(ROOT/name)==digest,digest)
copy=dict(r);stored=copy.pop('result_content_sha256');ck('content_hash',csha(copy)==stored,stored)
books={'Band2','Band3','Band4','Band5'};reps={x['representation'] for x in s};ck('site_representations',len(reps)==8,sorted(reps));ck('site_books',{x['held_book_or_ms'] for x in s}==books|{'Ste1'},sorted({x['held_book_or_ms'] for x in s}));ck('nuremberg_sites_per_rep',all(sum(int(x['test_sites']) for x in s if x['representation']==rep and x['held_book_or_ms'] in books)==119031 for rep in reps),len(reps));ck('ste_sites_per_rep',all(int(x['test_sites'])==33 for x in s if x['held_book_or_ms']=='Ste1'),33)

def agg_site(rep):
    rows=[x for x in s if x['representation']==rep and x['held_book_or_ms'] in books];n=sum(int(x['predictions_made']) for x in rows);c=sum(int(x['top1_correct']) for x in rows);return {'n':str(n),'correct':str(c),'accuracy':f'{c/max(1,n):.12g}'}
mapping={'raw_identity':'RAW_SITE_IDENTITY','raw_char3_backoff':'RAW_CHAR3_BACKOFF','page_host':'PAGE_HOST_IDENTITY','compiler':'COMPILER_SIGNATURE'}
for key,rep in mapping.items():ck('site_result_'+key,r['site_expansion_recovery'][key]==agg_site(rep),r['site_expansion_recovery'][key])
ck('site_arithmetic',all(int(x['top1_correct'])<=int(x['top3_correct'])<=int(x['predictions_made'])<=int(x['test_sites']) for x in s),len(s));ck('counterexamples_nonempty',len(e)>0,len(e));ck('operation_inventory',len(o)==len(read(ROOT/'gdt155_blind_transformations.tsv')),len(o));ck('operation_partition',all(int(x['exact_aligned_pairs'])==int(x['edge_operation_preserved'])+int(x['same_expanded_form'])+int(x['other_lexical_or_orthographic']) for x in o),len(o))

acc=defaultdict(lambda:{'n':0,'rr':0.,'top1':0,'top10':0,'topdec':0,'nr':[]})
for x in d:
    rank=int(x['model_rank']);pool=int(x['candidate_pool']);ckey=(x['book'],x['truth_dimension'],x['representation'])
    for key in (ckey,('ALL',x['truth_dimension'],x['representation'])):
        z=acc[key];z['n']+=1;z['rr']+=1/rank;z['top1']+=rank==1;z['top10']+=rank<=10;z['topdec']+=rank<=max(1,math.ceil(pool/10));z['nr'].append(rank/pool)
ck('retrieval_row_count',len(d)==r['counts']['retrieval_rows'],len(d));ck('retrieval_dimensions',{x['truth_dimension'] for x in d}=={'CONTENT','ADDRESSEE'},sorted({x['truth_dimension'] for x in d}));ck('retrieval_representations',len({x['representation'] for x in d})==7,sorted({x['representation'] for x in d}))
for x in a:
    z=acc[(x['book'],x['truth_dimension'],x['representation'])];n=z['n']
    expected=(n,f'{z["rr"]/n:.12g}',z['top1'],z['top10'],z['topdec'],f'{statistics.median(z["nr"]):.12g}')
    got=(int(x['queries_with_nonzero_truth_neighbor']),x['mean_reciprocal_rank'],int(x['top1']),int(x['top10']),int(x['top_decile']),x['median_normalized_rank'])
    ck('retrieval_summary_'+x['book']+'_'+x['truth_dimension']+'_'+x['representation'],got==expected,got)
for key,rep in {'raw_char3':'RAW_CHAR3','page_host_char3':'PAGE_HOST_CHAR3','compiler':'COMPILER_SIGNATURE'}.items():
    row=next(x for x in a if x['book']=='ALL' and x['truth_dimension']=='CONTENT' and x['representation']==rep);stored=r['content_retrieval'][key];ck('retrieval_result_'+key,all(str(value)==row[field] for field,value in stored.items()),stored)
ck('f84_flags',r['f84']=={'voynich_inputs':0,'accessed':False},r['f84']);ck('no_f84_text',all('f84' not in (ROOT/name).read_text(encoding='utf-8').lower() for name in r['outputs']),list(r['outputs']));ck('no_voynich_inputs',all('voynich' not in name.lower() for name in r['inputs']),list(r['inputs']));ck('claim_ceiling','no Voynich word' in r['claim_ceiling'] and 'translation' in r['claim_ceiling'],r['claim_ceiling'])
out={'schema':'GDT155_UNBLIND_CALIBRATION_VALIDATION_V1','status':'PASS_'+str(len(checks))+'_CHECK_INDEPENDENT_ARITHMETIC_AND_INTEGRITY','checks':checks,'result_sha256':sha(R),'result_content_sha256':r['result_content_sha256'],'validator_sha256':sha(Path(__file__)),'f84':{'accessed':False,'voynich_inputs':0}}
out['validation_content_sha256']=csha(out);V.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])

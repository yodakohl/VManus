#!/usr/bin/env python3
"""Independent integrity/arithmetic validator for GDT156 synthetic control."""
from __future__ import annotations
import csv,hashlib,json,math,statistics,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;R=ROOT/'gdt156_result.json';G=ROOT/'gdt156_encoded_groups.tsv';A=ROOT/'gdt156_encoded_architecture.tsv';W=ROOT/'gdt156_word_recovery.tsv';X=ROOT/'gdt156_synthetic_rectangles.tsv';P=ROOT/'gdt156_property_attribution.tsv';D=ROOT/'gdt156_retrieval.tsv';S=ROOT/'gdt156_retrieval_summary.tsv';C=ROOT/'gdt156_comparison.tsv';V=ROOT/'gdt156_validation.json';FOLD=str.maketrans({'ſ':'s','ı':'i','ȷ':'j','ẜ':'s'});VOWELS=set('aeiouyäöü')
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def norm(s):return ''.join(ch for ch in unicodedata.normalize('NFC',s).translate(FOLD).lower() if ch.isalnum())
def host(word):
 letters=[ch for ch in norm(word) if ch.isalpha()]
 if not letters:
  digits=norm(word);return (digits[:1]+digits[-1:]) or 'x'
 return letters[0]+''.join(ch for ch in letters[1:] if ch not in VOWELS)[:2]+letters[-1]
checks=[]
def ck(n,o,d):checks.append({'check':n,'ok':bool(o),'detail':d});assert o,(n,d)
r=json.loads(R.read_text());g=read(G);a=read(A);w=read(W);x=read(X);p=read(P);d=read(D);s=read(S);c=read(C)
ck('schema',r['schema']=='GDT156_VMS_HPR2_SYNTHETIC_ABBREVIATION_RESULT_V1',r['schema']);ck('status',r['status']=='SYNTHETIC_HPR2_CONTROL_COMPLETE',r['status']);ck('encoder',r['encoder']=='VMS_HPR2_ABBR_V1',r['encoder']);ck('freeze',r['freeze_provenance']=={'published_in_commit':'d62de97','method_before_gdt155_unblind_scoring':True},r['freeze_provenance'])
for n,h in r['inputs'].items():ck('input_'+n,sha(ROOT/n)==h,h)
for n,h in r['outputs'].items():ck('output_'+n,sha(ROOT/n)==h,h)
for n,h in r['documents'].items():ck('document_'+n,sha(ROOT/n)==h,h)
for n,h in r['implementation'].items():ck('implementation_'+n,sha(ROOT/n)==h,h)
z=dict(r);stored=z.pop('result_content_sha256');ck('content_hash',csha(z)==stored,stored)
records={q['record_id'] for q in g};first={}
for q in g:
 if q['record_id'] not in first or int(q['group_index_in_record'])<int(first[q['record_id']]['group_index_in_record']):first[q['record_id']]=q
ck('group_count',len(g)==r['counts']['groups']==438091,len(g));ck('record_count',len(records)==r['counts']['records']==3178,len(records));ck('corpus_partition',sum(q['corpus']=='NUREMBERG' for q in g)==r['counts']['nuremberg_groups'] and sum(q['corpus']=='STE1' for q in g)==r['counts']['ste1_groups'],r['counts']);ck('host_exact',all(q['page_host']==host(q['normalized_expanded_group']) for q in g),len(g));ck('right_exact',all(q['right_family']==('al' if len(q['normalized_expanded_group'])<=3 else 'ar' if len(q['normalized_expanded_group'])<=5 else 'ain' if len(q['normalized_expanded_group'])<=7 else 'aiin') for q in g),len(g));ck('compiler_recompose',all(q['synthetic_token']==('' if q['outer_wrapper']=='NONE' else q['outer_wrapper'])+('' if q['local_frame']=='NONE' else q['local_frame'])+q['page_host']+q['right_family']+('dy' if q['dy_closure']=='1' else '')+('m' if q['record_closure_m']=='1' else '') for q in g),len(g));ck('record_first_q',all(q['outer_wrapper']=='q' for q in first.values()),3178);ck('one_m_per_record',Counter(q['record_id'] for q in g if q['record_closure_m']=='1')==Counter({record:1 for record in records}),3178)
bybook=defaultdict(list)
for q in g:bybook[q['book_or_ms']].append(q)
for row in a:
 vals=bybook[row['book_or_ms']];src=sum(len(q['normalized_expanded_group']) for q in vals);hosts=sum(len(q['page_host']) for q in vals);code=sum(len(q['synthetic_token']) for q in vals);atoms=sum(len(q['page_host'])+(q['outer_wrapper']!='NONE')+(q['local_frame']!='NONE')+1+int(q['dy_closure'])+int(q['record_closure_m']) for q in vals)
 ck('arch_'+row['book_or_ms'],(int(row['groups']),int(row['source_characters']),int(row['page_host_characters']),int(row['synthetic_codepoints']),int(row['synthetic_abstract_atoms']))==(len(vals),src,hosts,code,atoms),row)
nb=[q for q in g if q['corpus']=='NUREMBERG'];src=sum(len(q['normalized_expanded_group']) for q in nb);hosts=sum(len(q['page_host']) for q in nb);code=sum(len(q['synthetic_token']) for q in nb);atoms=sum(len(q['page_host'])+(q['outer_wrapper']!='NONE')+(q['local_frame']!='NONE')+1+int(q['dy_closure'])+int(q['record_closure_m']) for q in nb);ck('compression',r['compression']=={'nuremberg_source_characters':src,'page_host_ratio':f'{hosts/src:.12g}','literal_codepoint_ratio':f'{code/src:.12g}','abstract_atom_ratio':f'{atoms/src:.12g}','verdict':'PAGE_HOST_COMPRESSES_BUT_FULL_V1_EXPANDS'},r['compression'])
ck('recovery_rows',len(w)==30,len(w));ck('recovery_arithmetic',all(int(q['top1_correct'])<=int(q['top3_correct'])<=int(q['predictions_made'])<=int(q['test_groups']) for q in w),len(w));ck('recovery_books',{q['held_book_or_ms'] for q in w}=={'Ste1','Band2','Band3','Band4','Band5'},sorted({q['held_book_or_ms'] for q in w}));ck('rectangle_family',{q['completion_requirement'] for q in x}=={'4_OF_4','8_OF_8'},len(x));ck('rectangle_attribution',all(q['attribution']=='MIXED_IMPOSED_OPERATOR_PLUS_EMERGENT_HOST_REUSE' for q in x),len(x));ck('property_attribution',{q['attribution'] for q in p}=={'IMPOSED_BY_ENCODER','EMERGENT_AFTER_ENCODING','MIXED_IMPOSED_OPERATOR_PLUS_EMERGENT_HOST_REUSE','EMERGENT_FAILURE_OF_ENCODER_DESIGN'},sorted({q['attribution'] for q in p}))
acc=defaultdict(lambda:{'n':0,'rr':0.,'one':0,'ten':0,'dec':0,'nr':[]})
for q in d:
 rank=int(q['model_rank']);pool=int(q['candidate_pool']);dec=max(1,math.ceil(pool/10))
 for key in ((q['book'],q['truth_dimension'],q['representation']),('ALL',q['truth_dimension'],q['representation'])):
  z=acc[key];z['n']+=1;z['rr']+=1/rank;z['one']+=rank==1;z['ten']+=rank<=10;z['dec']+=rank<=dec;z['nr'].append(rank/pool)
ck('retrieval_count',len(d)==r['counts']['retrieval_rows'],len(d));ck('retrieval_reps',len({q['representation'] for q in d})==8,sorted({q['representation'] for q in d}));ck('retrieval_dims',{q['truth_dimension'] for q in d}=={'CONTENT','ADDRESSEE'},sorted({q['truth_dimension'] for q in d}))
for q in s:
 z=acc[(q['book'],q['truth_dimension'],q['representation'])];n=z['n'];got=(int(q['queries']),q['mean_reciprocal_rank'],int(q['top1']),int(q['top10']),int(q['top_decile']),q['median_normalized_rank']);exp=(n,f'{z["rr"]/n:.12g}',z['one'],z['ten'],z['dec'],f'{statistics.median(z["nr"]):.12g}');ck('summary_'+q['book']+'_'+q['truth_dimension']+'_'+q['representation'],got==exp,got)
for key,rep in {'synthetic_char3':'SYNTHETIC_CHAR3','page_host_char3':'PAGE_HOST_CHAR3','compiler':'COMPILER_SIGNATURE','expanded_reference':'UNBLINDED_EXPANDED_CHAR3_REFERENCE'}.items():
 row=next(q for q in s if q['book']=='ALL' and q['truth_dimension']=='CONTENT' and q['representation']==rep);ck('result_'+key,all(str(v)==row[k] for k,v in r['content_retrieval'][key].items()),r['content_retrieval'][key])
g155=read(ROOT/'gdt155_unblind_retrieval_summary.tsv')
def rr(rows,rep):return next(float(q['mean_reciprocal_rank']) for q in rows if q['book']=='ALL' and q['truth_dimension']=='CONTENT' and q['representation']==rep)
expected={'RAW_OR_COMPLETE_TOKEN':(rr(g155,'RAW_CHAR3'),rr(s,'SYNTHETIC_CHAR3')),'PAGE_HOST':(rr(g155,'PAGE_HOST_CHAR3'),rr(s,'PAGE_HOST_CHAR3')),'COMPILER':(rr(g155,'COMPILER_SIGNATURE'),rr(s,'COMPILER_SIGNATURE'))}
for q in c:
 if q['layer'] in expected:
  old,new=expected[q['layer']];ck('comparison_'+q['layer'],q['diplomatic_control']==f'{old:.12g}' and q['synthetic_encoder']==f'{new:.12g}' and q['synthetic_minus_diplomatic']==f'{new-old:.12g}',q)
ck('external_only',{q['corpus'] for q in g}=={'NUREMBERG','STE1'},sorted({q['corpus'] for q in g}));ck('no_f84_data',all(not any(v.lower().startswith('f84') for v in q.values()) for table in (g,d) for q in table),len(g)+len(d));ck('f84_flags',r['f84']=={'voynich_inputs':0,'accessed':False},r['f84']);ck('claim','no Voynich word' in r['claim_ceiling'] and 'translation' in r['claim_ceiling'],r['claim_ceiling'])
out={'schema':'GDT156_VALIDATION_V1','status':'PASS_'+str(len(checks))+'_CHECK_INDEPENDENT_ARITHMETIC_AND_INTEGRITY','checks':checks,'result_sha256':sha(R),'result_content_sha256':r['result_content_sha256'],'validator_sha256':sha(Path(__file__)),'f84':{'accessed':False,'voynich_inputs':0}};out['validation_content_sha256']=csha(out);V.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])

#!/usr/bin/env python3
"""Validate GDT133 retained decomposition accounting and provenance."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt133_result.json';SCORES=ROOT/'gdt133_transfer_decomposition_scores.tsv';FOLDS=ROOT/'gdt133_transfer_decomposition_folds.tsv';SECTIONS=ROOT/'gdt133_transfer_decomposition_sections.tsv';NULL=ROOT/'gdt133_transfer_decomposition_null.tsv';OUT=ROOT/'gdt133_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b):return abs(float(a)-float(b))<2e-10
def main():
 r=json.loads(RESULT.read_text());checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 ck('schema',r['schema']=='GDT133_RAW_SURFACE_TRANSFER_DECOMPOSITION_RESULT_V1');ck('status',r['status']=='RAW_CONTROL_POSTHOC_RESIDUAL_SURFACE_LEAD_ONLY');ck('panel',r['panel']=='PUBLIC_CORRECTED_GDT132_31_PAIRS')
 base=json.loads((ROOT/'gdt132_result.json').read_text());ck('base_status',base['target_pairs']==31 and base['physical_folios']==24 and base['status']=='Q20_CONTINUATION_ARITY_DOES_NOT_TRANSFER_OUTSIDE_SECTION_S')
 s=read(SCORES);f=read(FOLDS);z=read(SECTIONS);n={x['model']:x for x in read(NULL)};js={x['model']:x for x in r['scores']};ck('models',len(s)==len(js)==6 and set(js)=={x['model'] for x in s});ck('fold_rows',len(f)==144);ck('section_rows',len(z)==48)
 for x in s:
  m=x['model'];ff=[y for y in f if y['model']==m];nn=n[m];j=js[m]
  ck('fold_count_'+m,len(ff)==24);ck('fold_sum_'+m,close(sum(float(y['gain_bits']) for y in ff),j['gain_bits']));ck('positive_'+m,sum(int(y['positive']) for y in ff)==j['positive_folios']);ck('score_'+m,all(close(x[k],j[k]) for k in ('gain_bits','local_p','max_six_p','null_mean_bits')));ck('null_'+m,close(nn['true_gain_bits'],j['gain_bits']) and close(nn['local_p'],j['local_p']) and close(nn['max_six_p'],j['max_six_p']))
 best=max(r['scores'],key=lambda x:x['gain_bits']);ck('best',r['best_model']=='RAW_CHAR3'==best['model']);ck('host_failed',js['HOST_CHAR3']['gain_bits']<0);ck('raw_residual_only',js['RAW_CHAR3']['model_top1']==js['RAW_CHAR3']['reference_top1'] and js['RAW_CHAR3']['positive_folios']==12 and js['FACTORED']['gain_bits']<0 and js['FACTORED_PLUS_RAW']['gain_bits']<0)
 ck('input_hashes',all(sha(ROOT/p)==h for p,h in r['inputs'].items()));ck('implementation_hashes',all(sha(ROOT/p)==h for p,h in r['implementation'].items()));ck('output_hashes',all(sha(ROOT/p)==h for p,h in r['outputs'].items()));ck('document_hashes',all(sha(ROOT/p)==h for p,h in r['documents'].items()));x=dict(r);h=x.pop('result_content_sha256');ck('content_hash',csha(x)==h)
 ck('f84_flags',r['f84r']=={'new_access':False,'actual_inputs_contain_rows':False,'prior_limited_audit_exposure_inherited':True});ck('no_f84_output_rows',not any('f84r\t' in (ROOT/p).read_text(errors='ignore') for p in r['outputs']))
 v={'schema':'GDT133_RAW_SURFACE_TRANSFER_DECOMPOSITION_VALIDATION_V1','status':'PASS_RETAINED_ACCOUNTING_AND_PROVENANCE','checks':len(checks),'passed':sum(x['pass'] for x in checks),'scope':'Retained output arithmetic, hashes, corrected-panel binding, status, and provenance; trained coefficients and 4096 permutation worlds are not independently refit.','result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'check_rows':checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))
if __name__=='__main__':main()

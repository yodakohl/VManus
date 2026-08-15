#!/usr/bin/env python3
"""Integrity/aggregate validator for GDT115; does not import its runner."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt115_result.json';OUT=ROOT/'gdt115_validation.json'
EDS=('ZL3b','IT2a','RF1b');MODELS=('COMPILER_ONLY','EDGE_ONLY','FULL_HPR2','RAW_CHAR3_HASH32','HOST_CHAR3_HASH32')
BLOCKS=('WRAPPER_TO_BODY_WRAPPER','WRAPPER_TO_BODY_FRAME','WRAPPER_TO_BODY_RENDERER','FRAME_TO_BODY_WRAPPER','FRAME_TO_BODY_FRAME','FRAME_TO_BODY_RENDERER','RENDERER_TO_BODY_WRAPPER','RENDERER_TO_BODY_FRAME','RENDERER_TO_BODY_RENDERER','COMPILER_TO_BODY_COMPILER','COMPILER_TO_BODY_EDGE','EDGE_TO_BODY_COMPILER','EDGE_TO_BODY_EDGE')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());strict=rows(ROOT/'gdt115_gdt114_strict_page_null.tsv');score=rows(ROOT/'gdt115_template_channel_scores.tsv');fold=rows(ROOT/'gdt115_template_channel_folds.tsv');counter=rows(ROOT/'gdt115_template_channel_counterexamples.tsv');c={}
 c['schema']=r['schema']=='GDT115_Q20_TEMPLATE_CHANNEL_DECOMPOSITION_RESULT_V1'
 c['strict_rows']=len(strict)==15 and set((x['edition'],x['model']) for x in strict)==set((e,m) for e in EDS for m in MODELS)
 c['score_rows']=len(score)==78 and set((x['edition'],x['model'],x['null_scope']) for x in score)==set((e,m,s) for e in EDS for m in BLOCKS for s in ('FOLIO','PAGE'))
 c['fold_rows']=len(fold)==312 and len({(x['edition'],x['model'],x['held_folio']) for x in fold})==312
 c['counter_rows']=len(counter)==78
 c['eight_folios']=all(len({x['held_folio'] for x in fold if x['edition']==e and x['model']==m})==8 for e in EDS for m in BLOCKS)
 c['lambda_grid']=set(float(x['lambda']) for x in fold)|set(float(x['nuisance_lambda']) for x in fold)<={.1,1.,10.,100.,1000.}
 by={(x['edition'],x['model'],x['null_scope']):x for x in score};agg=True
 for e in EDS:
  for m in BLOCKS:
   fs=[x for x in fold if x['edition']==e and x['model']==m];total=sum(float(x['pseudo_gain_bits']) for x in fs)
   for s in ('FOLIO','PAGE'):
    z=by[e,m,s];agg&=abs(total-float(z['true_gain_bits']))<1e-8;agg&=sum(float(x['pseudo_gain_bits'])>0 for x in fs)==int(z['positive_folios']);agg&=abs(float(z['selector_paid_gain_bits'])-(total-math.log2(13)))<1e-8
 c['aggregates']=agg
 c['p_bounds']=all(0<float(x['local_p'])<=1 and 0<float(x['max_13_p'])<=1 for x in score) and all(0<float(x['local_p'])<=1 and 0<float(x['max_five_p'])<=1 for x in strict)
 c['page_capacity']=set(int(x['swappable_records']) for x in score if x['null_scope']=='PAGE')=={99}
 c['folio_capacities']=set(int(x['swappable_records']) for x in score if x['null_scope']=='FOLIO')=={122,124,126}
 page=[by[e,'COMPILER_TO_BODY_COMPILER','PAGE'] for e in EDS];gate=all(float(x['true_gain_bits'])>0 and int(x['positive_folios'])==8 and float(x['max_13_p'])<=.05 for x in page)
 c['compiler_gate']=gate is True and r['compiler_channel_gate'] is True
 c['status']=r['status']=='Q20_OPEN_BODY_COMPILER_CHANNEL_TRANSFERS_WITHIN_PAGE'
 best=max([x for x in score if x['edition']=='ZL3b' and x['null_scope']=='PAGE'],key=lambda x:(float(x['true_gain_bits']),x['model']))
 c['best_exact']=best['model']==r['best_zl_page_block']['model'] and abs(float(best['true_gain_bits'])-float(r['best_zl_page_block']['true_gain_bits']))<1e-10
 c['strict_primary_exact']=next(x for x in strict if x['edition']=='ZL3b' and x['model']=='FULL_HPR2')['max_five_p']==f"{float(r['gdt114_strict_page_primary']['max_five_p']):.12f}"
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z)
 status='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(c.values()) else 'FAIL';out={'schema':'GDT115_Q20_TEMPLATE_CHANNEL_DECOMPOSITION_VALIDATION_V1','status':status,'scope':'Independent hashes, folds, retained aggregates, gates and decision; ridge fits and permutation worlds are not independently refit.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Integrity and retained-aggregate validator for GDT114; does not import runner."""
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULT=ROOT/'gdt114_result.json';OUT=ROOT/'gdt114_validation.json'
FILES=('gdt114_q20_record_template_inventory.tsv','gdt114_q20_record_template_folds.tsv','gdt114_q20_record_template_scores.tsv','gdt114_q20_record_template_null.tsv','gdt114_q20_record_template_counterexamples.tsv')
EDS=('ZL3b','IT2a','RF1b');MODELS=('COMPILER_ONLY','EDGE_ONLY','FULL_HPR2','RAW_CHAR3_HASH32','HOST_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());checks={}
 inv=rows(ROOT/FILES[0]);fold=rows(ROOT/FILES[1]);scores=rows(ROOT/FILES[2]);null=rows(ROOT/FILES[3]);counter=rows(ROOT/FILES[4])
 checks['schema']=r['schema']=='GDT114_Q20_RECORD_TEMPLATE_LINKAGE_RESULT_V1'
 checks['inventory_510']=len(inv)==510
 checks['inventory_unique_per_edition']=all(len({x['unit_id'] for x in inv if x['edition']==e})==170 for e in EDS)
 checks['inventory_folios']=len({x['physical_folio'] for x in inv})==8
 checks['no_f84_inventory']=not any(x['page'].startswith('f84r') or 'f84r' in x['body_line_loci'] for x in inv)
 checks['positive_counts']=all(int(x['open_groups'])>0 and int(x['body_groups'])>0 for x in inv)
 checks['profile_hashes']=all(len(x['open_profile_sha256'])==64 and len(x['body_profile_sha256'])==64 for x in inv)
 checks['fold_rows']=len(fold)==len(EDS)*8*(len(MODELS)+1)
 checks['fold_key_unique']=len({(x['edition'],x['held_folio'],x['model']) for x in fold})==len(fold)
 checks['fold_models']=set(x['model'] for x in fold)==set(MODELS)|{'NUISANCE'}
 checks['lambda_grid']=set(float(x['lambda']) for x in fold)<={.1,1.,10.,100.,1000.}
 checks['score_rows']=len(scores)==len(EDS)*len(MODELS)
 checks['null_rows']=len(null)==len(scores)
 checks['score_keys']=set((x['edition'],x['model']) for x in scores)==set((e,m) for e in EDS for m in MODELS)
 by={(x['edition'],x['model']):x for x in scores}
 agg=True
 for e in EDS:
  for m in MODELS:
   fs=[x for x in fold if x['edition']==e and x['model']==m]
   s=by[e,m]
   agg&=abs(sum(float(x['pseudo_gain_bits']) for x in fs)-float(s['pseudo_gain_bits']))<1e-8
   agg&=sum(float(x['pseudo_gain_bits'])>0 for x in fs)==int(s['positive_folios'])
   agg&=abs(float(s['selector_paid_gain_bits'])-(float(s['pseudo_gain_bits'])-math.log2(5)))<1e-8
 checks['score_aggregates']=agg
 checks['p_bounds']=all(0<float(x['local_p'])<=1 and 0<float(x['max_five_p'])<=1 for x in scores)
 checks['swappable_capacity']=Counter(int(x['swappable_records']) for x in scores)==Counter({124:5,126:5,122:5})
 p=by['ZL3b','FULL_HPR2'];g=r['gates']
 expected={'selector_paid_positive':float(p['selector_paid_gain_bits'])>0,'six_of_eight_positive_folios':int(p['positive_folios'])>=6,'all_readings_positive':all(float(by[e,'FULL_HPR2']['pseudo_gain_bits'])>0 for e in EDS),'max_five_p_le_005':float(p['max_five_p'])<=.05,'beats_both_string_controls':float(p['pseudo_gain_bits'])>max(float(by['ZL3b','RAW_CHAR3_HASH32']['pseudo_gain_bits']),float(by['ZL3b','HOST_CHAR3_HASH32']['pseudo_gain_bits']))}
 checks['gates_exact']=g==expected
 checks['status_exact']=r['status']==('Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_SUPPORTED' if all(expected.values()) else 'Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_WEAK_OR_LOCAL' if float(p['pseudo_gain_bits'])>0 else 'Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_NOT_SUPPORTED')
 checks['result_primary_exact']=all(abs(float(r['primary'][k])-float(p[k]))<1e-10 for k in ('pseudo_gain_bits','selector_paid_gain_bits','local_p','max_five_p'))
 checks['counterexamples_present']=len(counter)==len(EDS)*len(MODELS)*3
 checks['f84_flags']=all(v is False for v in r['f84r'].values())
 checks['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items())
 checks['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items())
 checks['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items())
 checks['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claimed=z.pop('result_content_sha256');checks['content_hash']=claimed==csha(z)
 status='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(checks.values()) else 'FAIL'
 out={'schema':'GDT114_Q20_RECORD_TEMPLATE_LINKAGE_VALIDATION_V1','status':status,'scope':'Independent file/hash/aggregate/decision validation; retained ridge coefficients and 4,096 permutation worlds are not independently refit.','checks_total':len(checks),'checks_passed':sum(checks.values()),'checks':checks,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(checks.values()),'total':len(checks)},sort_keys=True))
if __name__=='__main__':main()

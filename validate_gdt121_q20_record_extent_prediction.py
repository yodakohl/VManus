#!/usr/bin/env python3
"""Independent integrity/aggregate validator for GDT121."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt121_result.json';OUT=ROOT/'gdt121_validation.json';EDS=('ZL3b','IT2a','RF1b');MODES=('OPEN_WRAPPER7','OPEN_COMPILER12','OPEN_EDGE29','RAW_OPEN_CHAR3_HASH32','HOST_OPEN_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());p=rows(ROOT/'gdt121_q20_record_extent_predictions.tsv');f=rows(ROOT/'gdt121_q20_record_extent_folds.tsv');s=rows(ROOT/'gdt121_q20_record_extent_scores.tsv');n=rows(ROOT/'gdt121_q20_record_extent_null.tsv');x=rows(ROOT/'gdt121_q20_record_extent_counterexamples.tsv');c={};keys={(e,m) for e in EDS for m in MODES};by={(z['edition'],z['model']):z for z in s}
 c['schema']=r['schema']=='GDT121_Q20_RECORD_EXTENT_PREDICTION_RESULT_V1'
 c['prediction_rows']=len(p)==2550 and len({(z['edition'],z['model'],z['unit_id']) for z in p})==2550
 c['prediction_counts']=all(len([z for z in p if z['edition']==e and z['model']==m])==170 for e,m in keys)
 c['actual_invariant']=all(len({(z['actual_body_lines'],z['actual_body_groups'],z['actual_body_members']) for z in p if z['edition']==e and z['unit_id']==u})==1 for e in EDS for u in {q['unit_id'] for q in p if q['edition']==e})
 c['no_f84']=not any(z['page'].startswith('f84r') for z in p)
 c['fold_rows']=len(f)==120 and {(z['edition'],z['model']) for z in f}==keys and len({(z['edition'],z['model'],z['held_folio']) for z in f})==120
 c['score_rows']=len(s)==15 and set(by)==keys
 c['null_rows']=len(n)==15 and {(z['edition'],z['model']) for z in n}==keys
 c['counter_rows']=len(x)==45
 agg=True
 for key in keys:
  fs=[z for z in f if (z['edition'],z['model'])==key];q=by[key];total=sum(float(z['pseudo_gain_bits']) for z in fs);ps=[z for z in p if (z['edition'],z['model'])==key];mae0=sum(abs(float(z['actual_body_groups'])-float(z['pred_body_groups_nuisance'])) for z in ps)/170;mae1=sum(abs(float(z['actual_body_groups'])-float(z['pred_body_groups_model'])) for z in ps)/170
  agg &= len(fs)==8 and abs(total-float(q['pseudo_gain_bits']))<1e-8 and sum(float(z['pseudo_gain_bits'])>0 for z in fs)==int(q['positive_folios']) and abs(float(q['selector_paid_gain_bits'])-(total-math.log2(5)))<1e-8 and abs(mae0-float(q['body_group_mae_nuisance']))<1e-9 and abs(mae1-float(q['body_group_mae_model']))<1e-9
 c['aggregates_and_mae']=agg
 q=by['ZL3b','OPEN_COMPILER12'];gates={'selector_paid_positive':float(q['selector_paid_gain_bits'])>0,'max_five_p_le_005':float(q['max_five_p'])<=.05,'six_of_eight_positive':int(q['positive_folios'])>=6,'all_readings_positive':all(float(by[e,'OPEN_COMPILER12']['pseudo_gain_bits'])>0 for e in EDS),'beats_string_controls':float(q['pseudo_gain_bits'])>max(float(by['ZL3b','RAW_OPEN_CHAR3_HASH32']['pseudo_gain_bits']),float(by['ZL3b','HOST_OPEN_CHAR3_HASH32']['pseudo_gain_bits']))};c['gates']=gates==r['gates']
 c['status']=r['status']=='Q20_BODY_EXTENT_SIGNAL_WEAK_OR_STRING_LIKE'
 c['p_bounds']=all(0<float(z['local_p'])<=1 and 0<float(z['max_five_p'])<=1 for z in s)
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z);status='PASS_INTEGRITY_AGGREGATES_AND_PREDICTIONS' if all(c.values()) else 'FAIL';out={'schema':'GDT121_Q20_RECORD_EXTENT_PREDICTION_VALIDATION_V1','status':status,'scope':'Independent artifact integrity, prediction/MAE/fold aggregates, gates and hashes; ridge and permutation worlds are not independently rerun.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Integrity/aggregate validator for GDT117 retrieval."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt117_result.json';OUT=ROOT/'gdt117_validation.json';EDS=('ZL3b','IT2a','RF1b');MODES=('WRAPPER7','COMPILER12','EDGE29','RAW_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());pred=rows(ROOT/'gdt117_open_body_retrieval_predictions.tsv');score=rows(ROOT/'gdt117_open_body_retrieval_scores.tsv');fold=rows(ROOT/'gdt117_open_body_retrieval_folds.tsv');counter=rows(ROOT/'gdt117_open_body_retrieval_counterexamples.tsv');c={}
 c['schema']=r['schema']=='GDT117_Q20_OPEN_BODY_RETRIEVAL_RESULT_V1'
 c['prediction_rows']=len(pred)==1188 and len({(x['edition'],x['model'],x['unit_id']) for x in pred})==1188
 c['score_rows']=len(score)==12 and set((x['edition'],x['model']) for x in score)==set((e,m) for e in EDS for m in MODES)
 c['fold_rows']=len(fold)==96 and len({(x['edition'],x['model'],x['held_folio']) for x in fold})==96
 c['counter_rows']=len(counter)==96
 c['eligible_99']=all(int(x['eligible_records'])==99 for x in score)
 c['candidate_counts']=all(int(x['candidate_count']) in (2,3,4,5) and len(x['candidate_unit_ids'].split('|'))==int(x['candidate_count']) and len(x['candidate_sse'].split('|'))==int(x['candidate_count']) for x in pred)
 c['rank_bounds']=all(1<=float(x['true_rank'])<=int(x['candidate_count']) and abs(float(x['reciprocal_rank'])-1/float(x['true_rank']))<1e-9 for x in pred)
 by={(x['edition'],x['model']):x for x in score};agg=True
 for e in EDS:
  for m in MODES:
   z=[x for x in pred if x['edition']==e and x['model']==m];s=by[e,m];top=sum(int(x['top1']) for x in z)/len(z);mrr=sum(float(x['reciprocal_rank']) for x in z)/len(z);wins=sum(float(x['pairwise_wins']) for x in z);trials=sum(int(x['pairwise_trials']) for x in z);agg&=abs(top-float(s['top1_accuracy']))<1e-10 and abs(mrr-float(s['mrr']))<1e-10 and abs(wins/trials-float(s['pairwise_accuracy']))<1e-10
 c['score_aggregates']=agg
 c['p_bounds']=all(0<float(x[k])<=1 for x in score for k in ('top1_local_p','top1_max_four_p','mrr_local_p','mrr_max_four_p'))
 p=by['ZL3b','COMPILER12'];direction=all(float(by[e,'COMPILER12']['mrr'])>float(by[e,'COMPILER12']['null_mrr_mean']) for e in EDS);corrected=all(float(by[e,'COMPILER12']['mrr_max_four_p'])<=.05 for e in EDS);status='Q20_COMPILER_PROFILE_SUPPORTS_HELD_RECORD_RETRIEVAL' if float(p['top1_accuracy'])>float(p['null_top1_expectation']) and float(p['mrr_max_four_p'])<=.05 and corrected else 'Q20_COMPILER_PROFILE_SUPPORTS_HELD_RECORD_RETRIEVAL_READING_SENSITIVE' if float(p['top1_accuracy'])>float(p['null_top1_expectation']) and float(p['mrr_max_four_p'])<=.05 and direction else 'Q20_RECORD_RETRIEVAL_WEAK_OR_NOT_ABOVE_STRING_CONTROLS'
 c['status']=r['status']==status
 c['primary_exact']=all(abs(float(r['primary'][k])-float(p[k]))<1e-10 for k in ('top1_accuracy','mrr','pairwise_accuracy','mrr_max_four_p'))
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z);statusv='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(c.values()) else 'FAIL';out={'schema':'GDT117_Q20_OPEN_BODY_RETRIEVAL_VALIDATION_V1','status':statusv,'scope':'Independent hashes and retained ranking/aggregate/decision reconstruction; ridge fits and 4,096 worlds are not independently rerun.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':statusv,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

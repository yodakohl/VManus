#!/usr/bin/env python3
"""Integrity/aggregate validator for GDT118."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt118_result.json';OUT=ROOT/'gdt118_validation.json';EDS=('ZL3b','IT2a','RF1b');DEPTHS=('BODY_LINE_1','BODY_LINE_2','BODY_TAIL_3PLUS');MODES=('COMPILER12','RAW_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());score=rows(ROOT/'gdt118_compiler_depth_scores.tsv');fold=rows(ROOT/'gdt118_compiler_depth_folds.tsv');null=rows(ROOT/'gdt118_compiler_depth_null.tsv');counter=rows(ROOT/'gdt118_compiler_depth_counterexamples.tsv');c={}
 c['schema']=r['schema']=='GDT118_Q20_COMPILER_DEPTH_TRANSFER_RESULT_V1'
 keys=set((e,d,m) for e in EDS for d in DEPTHS for m in MODES)
 c['score_rows']=len(score)==18 and set((x['edition'],x['depth'],x['model']) for x in score)==keys
 c['null_rows']=len(null)==18 and set((x['edition'],x['depth'],x['model']) for x in null)==keys
 c['fold_rows']=len(fold)==144 and len({(x['edition'],x['depth'],x['model'],x['held_folio']) for x in fold})==144
 c['counter_rows']=len(counter)==36
 by={(x['edition'],x['depth'],x['model']):x for x in score};agg=True
 for k in keys:
  fs=[x for x in fold if (x['edition'],x['depth'],x['model'])==k];z=by[k];total=sum(float(x['pseudo_gain_bits']) for x in fs);agg&=abs(total-float(z['true_gain_bits']))<1e-8 and sum(int(x['positive_gain']) for x in fs)==int(z['positive_folios']) and abs(float(z['selector_paid_gain_bits'])-(total-math.log2(6)))<1e-8
 c['aggregates']=agg
 c['counts']=all(int(by[e,'BODY_LINE_1',m]['eligible_records'])==170 and int(by[e,'BODY_LINE_2',m]['eligible_records'])==135 and int(by[e,'BODY_TAIL_3PLUS',m]['eligible_records'])==65 for e in EDS for m in MODES)
 c['p_bounds']=all(0<float(x['local_p'])<=1 and 0<float(x['max_six_p'])<=1 for x in score)
 p=[by['ZL3b',d,'COMPILER12'] for d in DEPTHS];supported=[x for x in p if float(x['true_gain_bits'])>0 and float(x['max_six_p'])<=.05];status='Q20_OPEN_COMPILER_LINK_PERSISTS_BEYOND_FIRST_BODY_LINE' if any(x['depth']!='BODY_LINE_1' for x in supported) else 'Q20_OPEN_COMPILER_LINK_IS_IMMEDIATE_CONTINUATION_ONLY' if any(x['depth']=='BODY_LINE_1' for x in supported) else 'Q20_OPEN_COMPILER_DEPTH_TRANSFER_WEAK_OR_UNSTABLE'
 c['status']=r['status']==status
 c['primary_exact']=all(abs(float(r['primary_depths'][d][k])-float(by['ZL3b',d,'COMPILER12'][k]))<1e-10 for d in DEPTHS for k in ('true_gain_bits','local_p','max_six_p'))
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z);statusv='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(c.values()) else 'FAIL';out={'schema':'GDT118_Q20_COMPILER_DEPTH_TRANSFER_VALIDATION_V1','status':statusv,'scope':'Independent hashes, fold aggregates and decision; ridge fits and permutation worlds are not independently rerun.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':statusv,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Integrity/aggregate validator for GDT119."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt119_result.json';OUT=ROOT/'gdt119_validation.json';EDS=('ZL3b','IT2a','RF1b');AXES=('RAYS_8_VS_7','TAIL_2_VS_1','COLOR_RED_VS_YEL');MODES=('OPEN_WRAPPER7','OPEN_COMPILER12','BODY_COMPILER12','OPEN_BODY_COMPILER24','RAW_RECORD_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());inv=rows(ROOT/'gdt119_q20_visual_compiler_inventory.tsv');score=rows(ROOT/'gdt119_q20_visual_compiler_scores.tsv');fold=rows(ROOT/'gdt119_q20_visual_compiler_folds.tsv');null=rows(ROOT/'gdt119_q20_visual_compiler_null.tsv');counter=rows(ROOT/'gdt119_q20_visual_compiler_counterexamples.tsv');c={};keys=set((e,a,m) for e in EDS for a in AXES for m in MODES)
 c['schema']=r['schema']=='GDT119_Q20_VISUAL_COMPILER_ASSOCIATION_RESULT_V1'
 c['inventory']=len(inv)==468 and all(len({x['unit_id'] for x in inv if x['edition']==e})==156 for e in EDS)
 c['provenance']=all(x['provenance']=='EXISTING_HUMAN_ANNOTATION_STOLFI_STAR_PROPS' for x in inv)
 c['no_f84']=not any(x['page'].startswith('f84r') for x in inv)
 c['score_rows']=len(score)==45 and set((x['edition'],x['axis'],x['model']) for x in score)==keys
 c['null_rows']=len(null)==45 and set((x['edition'],x['axis'],x['model']) for x in null)==keys
 c['fold_rows']=len(fold)==315 and len({(x['edition'],x['axis'],x['model'],x['held_folio']) for x in fold})==315
 c['counter_rows']=len(counter)==90
 by={(x['edition'],x['axis'],x['model']):x for x in score};agg=True
 for k in keys:
  fs=[x for x in fold if (x['edition'],x['axis'],x['model'])==k];z=by[k];total=sum(float(x['gain_bits']) for x in fs);n=sum(int(x['held_rows']) for x in fs);agg&=abs(total-float(z['gain_bits']))<1e-8 and n==int(z['rows']) and sum(float(x['gain_bits'])>0 for x in fs)==int(z['positive_folios']) and abs(float(z['selector_paid_gain_bits'])-(total-math.log2(15)))<1e-8
 c['aggregates']=agg
 # The target binding contains 156 complete-page units.  Seven have ray counts
 # outside the frozen 7/8 contrast, one lacks the frozen 1/2 tail contrast,
 # and six have a white or unknown colour in the source panel.
 c['axis_counts']=all(int(by[e,'RAYS_8_VS_7',m]['rows'])==149 and int(by[e,'TAIL_2_VS_1',m]['rows'])==155 and int(by[e,'COLOR_RED_VS_YEL',m]['rows'])==150 for e in EDS for m in MODES)
 c['p_bounds']=all(0<float(x['local_p'])<=1 and 0<float(x['max_15_p'])<=1 for x in score)
 top=max([x for x in score if x['edition']=='ZL3b'],key=lambda x:(float(x['gain_bits']),x['axis'],x['model']));supported=[x for x in score if x['edition']=='ZL3b' and float(x['gain_bits'])>0 and float(x['max_15_p'])<=.05 and all(float(by[e,x['axis'],x['model']]['gain_bits'])>0 for e in EDS)]
 c['top_exact']=top['axis']==r['top_zl']['axis'] and top['model']==r['top_zl']['model'] and abs(float(top['gain_bits'])-float(r['top_zl']['gain_bits']))<1e-10
 c['supported_empty']=not supported and r['supported_candidates']==[]
 c['status']=r['status']=='Q20_VISUAL_STATE_NOT_PREDICTED_BY_RECORD_COMPILER'
 c['historical_failure_preserved']='FAIL_TARGET_FREE_NULL_AND_POWER_CALIBRATION' in r['historical_sme_status']
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z);status='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(c.values()) else 'FAIL';out={'schema':'GDT119_Q20_VISUAL_COMPILER_ASSOCIATION_VALIDATION_V1','status':status,'scope':'Independent provenance/count/hash/fold aggregate/decision validation; logistic fits and permutation worlds are not independently rerun.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

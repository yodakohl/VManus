#!/usr/bin/env python3
"""Independent integrity/aggregate validator for GDT122."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt122_result.json';OUT=ROOT/'gdt122_validation.json';EDS=('ZL3b','IT2a','RF1b');AXES=('RAYS_8_VS_7','TAIL_2_VS_1','COLOR_RED_VS_YEL');MODES=('OPEN_HOST_CHAR3_HASH32','BODY_HOST_CHAR3_HASH32','OPEN_BODY_HOST_CHAR3_HASH32','OPEN_COMPILER12','RAW_RECORD_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());i=rows(ROOT/'gdt122_q20_page_host_visual_inventory.tsv');f=rows(ROOT/'gdt122_q20_page_host_visual_folds.tsv');s=rows(ROOT/'gdt122_q20_page_host_visual_scores.tsv');n=rows(ROOT/'gdt122_q20_page_host_visual_null.tsv');x=rows(ROOT/'gdt122_q20_page_host_visual_counterexamples.tsv');c={};keys={(e,a,m) for e in EDS for a in AXES for m in MODES};by={(z['edition'],z['axis'],z['model']):z for z in s}
 c['schema']=r['schema']=='GDT122_Q20_PAGE_HOST_VISUAL_ASSOCIATION_RESULT_V1'
 c['inventory']=len(i)==468 and all(len({z['unit_id'] for z in i if z['edition']==e})==156 for e in EDS)
 c['provenance']=all(z['provenance']=='EXISTING_HUMAN_ANNOTATION_STOLFI_STAR_PROPS' for z in i)
 c['no_f84']=not any(z['page'].startswith('f84r') for z in i)
 c['fold_rows']=len(f)==315 and len({(z['edition'],z['axis'],z['model'],z['held_folio']) for z in f})==315
 c['score_rows']=len(s)==45 and set(by)==keys
 c['null_rows']=len(n)==45 and {(z['edition'],z['axis'],z['model']) for z in n}==keys
 c['counter_rows']=len(x)==90
 c['axis_counts']=all(int(by[e,'RAYS_8_VS_7',m]['rows'])==149 and int(by[e,'TAIL_2_VS_1',m]['rows'])==155 and int(by[e,'COLOR_RED_VS_YEL',m]['rows'])==150 for e in EDS for m in MODES)
 agg=True
 for key in keys:
  fs=[z for z in f if (z['edition'],z['axis'],z['model'])==key];q=by[key];total=sum(float(z['gain_bits']) for z in fs)
  agg &= len(fs)==7 and abs(total-float(q['gain_bits']))<1e-8 and sum(float(z['gain_bits'])>0 for z in fs)==int(q['positive_folios']) and abs(float(q['selector_paid_gain_bits'])-(total-math.log2(15)))<1e-8 and int(q['swappable_rows'])>0
 c['aggregates']=agg
 hosts=[z for z in s if z['edition']=='ZL3b' and 'HOST_CHAR3' in z['model']];best=max(hosts,key=lambda z:(float(z['gain_bits']),z['axis'],z['model']));top=max([z for z in s if z['edition']=='ZL3b'],key=lambda z:(float(z['gain_bits']),z['axis'],z['model']));c['best_exact']=best['axis']==r['best_page_host']['axis'] and best['model']==r['best_page_host']['model'] and abs(float(best['gain_bits'])-r['best_page_host']['gain_bits'])<1e-10;c['top_exact']=top['axis']==r['top_any']['axis'] and top['model']==r['top_any']['model']
 gates={'selector_paid_positive':float(best['selector_paid_gain_bits'])>0,'max_15_p_le_005':float(best['max_15_p'])<=.05,'five_of_seven_positive':int(best['positive_folios'])>=5,'all_readings_positive':all(float(by[e,best['axis'],best['model']]['gain_bits'])>0 for e in EDS),'beats_compiler_and_raw':float(best['gain_bits'])>max(float(by['ZL3b',best['axis'],'OPEN_COMPILER12']['gain_bits']),float(by['ZL3b',best['axis'],'RAW_RECORD_CHAR3_HASH32']['gain_bits']))};c['gates']=gates==r['gates']
 c['status']=r['status']=='Q20_PAGE_HOST_DOES_NOT_RECOVER_STAR_VISUAL_SIGNAL'
 c['historical_failure']=r['historical_sme_status']=='FAIL_TARGET_FREE_NULL_AND_POWER_CALIBRATION'
 c['p_bounds']=all(0<float(z['local_p'])<=1 and 0<float(z['max_15_p'])<=1 for z in s)
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z);status='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(c.values()) else 'FAIL';out={'schema':'GDT122_Q20_PAGE_HOST_VISUAL_ASSOCIATION_VALIDATION_V1','status':status,'scope':'Independent provenance/count/hash/fold aggregate/gate validation; logistic fits and permutation worlds are not independently rerun.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

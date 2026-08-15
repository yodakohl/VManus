#!/usr/bin/env python3
"""Integrity and retained-aggregate validator for GDT116."""
import csv,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt116_result.json';OUT=ROOT/'gdt116_validation.json';EDS=('ZL3b','IT2a','RF1b');W=('q','d','s','ch','che','sh','t')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());cells=rows(ROOT/'gdt116_wrapper_channel_cells.tsv');fold=rows(ROOT/'gdt116_wrapper_channel_folds.tsv');maps=rows(ROOT/'gdt116_wrapper_bijections.tsv');counter=rows(ROOT/'gdt116_wrapper_counterexamples.tsv');c={}
 c['schema']=r['schema']=='GDT116_Q20_WRAPPER_CHANNEL_MAP_RESULT_V1'
 c['cell_rows']=len(cells)==147 and set((x['edition'],x['open_wrapper'],x['body_wrapper']) for x in cells)==set((e,a,b) for e in EDS for a in W for b in W)
 c['fold_rows']=len(fold)==1176 and len({(x['edition'],x['open_wrapper'],x['body_wrapper'],x['held_folio']) for x in fold})==1176
 c['map_rows']=len(maps)==6 and set((x['edition'],x['mapping_type']) for x in maps)==set((e,t) for e in EDS for t in ('IDENTITY_PREDECLARED','BEST_POSTSELECTED_BIJECTION'))
 c['counter_rows']=len(counter)==294
 by={(x['edition'],x['open_wrapper'],x['body_wrapper']):x for x in cells};agg=True
 for e in EDS:
  for a in W:
   for b in W:
    fs=[x for x in fold if x['edition']==e and x['open_wrapper']==a and x['body_wrapper']==b];z=by[e,a,b]
    agg&=abs(sum(float(x['pseudo_gain_bits']) for x in fs)-float(z['true_gain_bits']))<1e-8;agg&=sum(int(x['positive_gain']) for x in fs)==int(z['positive_folios'])
 c['cell_aggregates']=agg
 c['p_bounds']=all(0<float(x['local_p'])<=1 and 0<float(x['max_49_p'])<=1 for x in cells)
 c['capacity']=set(int(x['same_page_swappable_records']) for x in cells)=={99}
 mby={(x['edition'],x['mapping_type']):x for x in maps};mapping=True;summary={}
 for e in EDS:
  ident=sum(float(by[e,x,x]['true_gain_bits']) for x in W);vals=[]
  for p in itertools.permutations(W):vals.append((sum(float(by[e,a,b]['true_gain_bits']) for a,b in zip(W,p)),p))
  vals.sort(reverse=True);rank=1+sum(v>ident+1e-10 for v,_ in vals);best,p=vals[0];mapping&=abs(float(mby[e,'IDENTITY_PREDECLARED']['sum_gain_bits'])-ident)<1e-8 and int(mby[e,'IDENTITY_PREDECLARED']['rank_of_5040'])==rank;mapping&=abs(float(mby[e,'BEST_POSTSELECTED_BIJECTION']['sum_gain_bits'])-best)<1e-8;summary[e]=(ident,rank,best,'|'.join(f'{a}->{b}' for a,b in zip(W,p)))
 c['bijections_reconstructed']=mapping
 top=max([x for x in cells if x['edition']=='ZL3b'],key=lambda x:(float(x['true_gain_bits']),x['open_wrapper'],x['body_wrapper']))
 c['top_exact']=top['open_wrapper']==r['top_zl_cell']['open_wrapper'] and top['body_wrapper']==r['top_zl_cell']['body_wrapper'] and abs(float(top['true_gain_bits'])-float(r['top_zl_cell']['true_gain_bits']))<1e-10
 c['summary_exact']=all(abs(summary[e][0]-float(r['mapping_summary'][e]['identity_gain']))<1e-8 and summary[e][1]==int(r['mapping_summary'][e]['identity_rank']) and abs(summary[e][2]-float(r['mapping_summary'][e]['best_gain']))<1e-8 and summary[e][3]==r['mapping_summary'][e]['best_mapping'] for e in EDS)
 c['status']=r['status']=='Q20_WRAPPER_CHANNEL_MAP_TRANSFERABLE_BUT_NONIDENTITY'
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z)
 status='PASS_INTEGRITY_AND_RETAINED_AGGREGATES' if all(c.values()) else 'FAIL';out={'schema':'GDT116_Q20_WRAPPER_CHANNEL_MAP_VALIDATION_V1','status':status,'scope':'Independent hashes, 49-cell fold aggregates, complete 7! bijection reconstruction and decision; ridge fits/permutation worlds are not independently refit.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

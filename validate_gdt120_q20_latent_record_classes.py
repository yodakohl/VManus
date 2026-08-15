#!/usr/bin/env python3
"""Independent integrity/aggregate validator for GDT120."""
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt120_result.json';OUT=ROOT/'gdt120_validation.json';EDS=('ZL3b','IT2a','RF1b');KS=(2,3,4,5,6);MODES=('OPEN_WRAPPER7','OPEN_COMPILER12','OPEN_EDGE29','RAW_OPEN_CHAR3_HASH32')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def ari(a,b):
 ca=defaultdict(int);cb=defaultdict(int);cab=defaultdict(int)
 for x,y in zip(a,b):ca[x]+=1;cb[y]+=1;cab[x,y]+=1
 c2=lambda n:n*(n-1)/2
 n=len(a);tot=c2(n);s=sum(c2(v) for v in cab.values());sa=sum(c2(v) for v in ca.values());sb=sum(c2(v) for v in cb.values());ex=sa*sb/tot if tot else 0.;mx=(sa+sb)/2
 return (s-ex)/(mx-ex) if mx>ex else 1.
def main():
 r=json.loads(RESULT.read_text());a=rows(ROOT/'gdt120_q20_latent_class_assignments.tsv');p=rows(ROOT/'gdt120_q20_latent_class_prototypes.tsv');f=rows(ROOT/'gdt120_q20_latent_class_folds.tsv');s=rows(ROOT/'gdt120_q20_latent_class_scores.tsv');n=rows(ROOT/'gdt120_q20_latent_class_null.tsv');x=rows(ROOT/'gdt120_q20_latent_class_counterexamples.tsv');c={};keys={(e,k,m) for e in EDS for k in KS for m in MODES}
 c['schema']=r['schema']=='GDT120_Q20_LATENT_RECORD_CLASS_RESULT_V1'
 c['assignment_rows']=len(a)==2550 and len({(z['edition'],z['k'],z['unit_id']) for z in a})==2550
 c['assignment_counts']=all(len([z for z in a if z['edition']==e and int(z['k'])==k])==170 for e in EDS for k in KS)
 c['assignment_class_bounds']=all(0<=int(z['class_id'])<int(z['k']) for z in a)
 c['no_f84']=not any(z['page'].startswith('f84r') for z in a)
 c['prototype_rows']=len(p)==480 and all(len(z['centroid'].split('|'))==12 for z in p)
 c['prototype_keys']=len({(z['edition'],z['k'],z['held_folio'],z['class_id']) for z in p})==480
 c['fold_rows']=len(f)==480 and {(z['edition'],int(z['k']),z['model']) for z in f}==keys
 c['fold_keys']=len({(z['edition'],z['k'],z['model'],z['held_folio']) for z in f})==480
 c['score_rows']=len(s)==60 and {(z['edition'],int(z['k']),z['model']) for z in s}==keys
 c['null_rows']=len(n)==60 and {(z['edition'],int(z['k']),z['model']) for z in n}==keys
 c['counter_rows']=len(x)==120
 by={(z['edition'],int(z['k']),z['model']):z for z in s};agg=True
 for key in keys:
  fs=[z for z in f if (z['edition'],int(z['k']),z['model'])==key];q=by[key];total=sum(float(z['pseudo_gain_bits']) for z in fs)
  agg &= len(fs)==8 and abs(total-float(q['pseudo_gain_bits']))<1e-8 and sum(float(z['pseudo_gain_bits'])>0 for z in fs)==int(q['positive_folios']) and abs(float(q['selector_paid_gain_bits'])-(total-math.log2(20)))<1e-8
 c['fold_aggregates']=agg
 # Reconstruct label-free reading agreement from held assignment rows.
 aris={}
 for k in KS:
  lab={e:{z['unit_id']:int(z['class_id']) for z in a if z['edition']==e and int(z['k'])==k} for e in EDS};ids=sorted(set.intersection(*(set(lab[e]) for e in EDS)));vals=[]
  for e1,e2 in (('ZL3b','IT2a'),('ZL3b','RF1b'),('IT2a','RF1b')):vals.append(ari([lab[e1][i] for i in ids],[lab[e2][i] for i in ids]))
  aris[k]=sum(vals)/3
 c['ari_reconstructed']=all(abs(float(by[e,k,m]['mean_cross_reading_ari'])-aris[k])<1e-9 for e in EDS for k in KS for m in MODES)
 best=max([by['ZL3b',k,'OPEN_COMPILER12'] for k in KS],key=lambda z:(float(z['pseudo_gain_bits']),-int(z['k'])));c['primary_exact']=int(best['k'])==r['primary']['k'] and abs(float(best['pseudo_gain_bits'])-r['primary']['pseudo_gain_bits'])<1e-10
 gates={'selector_paid_positive':float(best['selector_paid_gain_bits'])>0,'max_20_p_le_005':float(best['max_20_p'])<=.05,'six_of_eight_positive':int(best['positive_folios'])>=6,'all_readings_positive':all(float(by[e,int(best['k']),'OPEN_COMPILER12']['pseudo_gain_bits'])>0 for e in EDS),'mean_cross_reading_ari_ge_05':aris[int(best['k'])]>=.5};c['gates']=gates==r['gates']
 c['status']=r['status']=='Q20_LATENT_RECORD_CLASSES_WEAK_OR_UNSTABLE'
 c['f84_flags']=all(v is False for v in r['f84r'].values())
 c['p_bounds']=all(0<float(z['local_p'])<=1 and 0<float(z['max_20_p'])<=1 for z in s)
 c['input_hashes']=all(sha(ROOT/k)==v for k,v in r['inputs'].items());c['implementation_hashes']=all(sha(ROOT/k)==v for k,v in r['implementation'].items());c['output_hashes']=all(sha(ROOT/k)==v for k,v in r['outputs'].items());c['document_hashes']=all(sha(ROOT/k)==v for k,v in r['documents'].items())
 z=dict(r);claim=z.pop('result_content_sha256');c['content_hash']=claim==csha(z);status='PASS_INTEGRITY_AGGREGATES_AND_READING_STABILITY' if all(c.values()) else 'FAIL';out={'schema':'GDT120_Q20_LATENT_RECORD_CLASS_VALIDATION_V1','status':status,'scope':'Independent artifact integrity, class/fold accounting, aggregate scores, ARI, gates and hashes; k-means and ridge/permutation fits are not independently rerun.','checks_total':len(c),'checks_passed':sum(c.values()),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'passed':sum(c.values()),'total':len(c)},sort_keys=True))
if __name__=='__main__':main()

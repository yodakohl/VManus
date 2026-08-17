#!/usr/bin/env python3
"""Independent retained-artifact checks for GDT199."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt199_result.json';INV=R/'gdt199_renderer_transfer_inventory.tsv';OUT=R/'gdt199_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 q=json.loads(RESULT.read_text());rows=list(csv.DictReader(INV.open(),delimiter='\t'));checks=[]
 def ck(n,x):checks.append((n,bool(x)))
 ck('schema',q['schema']=='GDT199_F77_RENDERER_SWITCH_TRANSFER_RESULT_V1');ck('status',q['status']=='F77_RENDERER_SWITCH_DOES_NOT_TRANSFER_TO_ARCHIVED_LABELS')
 ck('five_complete_targets',len(rows)==q['complete_target_inventory']==5);eligible=[r for r in rows if r['scored']=='1'];hits=sum(r['exact_prediction_correct']=='1' for r in eligible)
 ck('four_eligible',len(eligible)==q['eligible_predictions']==4);ck('one_hit',hits==q['exact_hits']==1);ck('three_misses',q['exact_misses']==3)
 ck('figure_targets_fail',[(r['locus'],r['exact_prediction_correct']) for r in eligible if r['archived_visual_class']=='FIGURE_ONLY']==[('f73v.23','0'),('f82v.2','0')])
 ck('all_target_loci_exact',set(r['locus'] for r in rows)=={'f73v.23','f75v.54','f75v.56','f82v.2','f100v.8'})
 ck('no_f84_rows',not any(r['page'].startswith('f84') or r['locus'].startswith('f84') for r in rows));ck('f84_flags',not any(q['f84r'].values()))
 for section in ('inputs','implementation','outputs','documents'):
  for n,h in q[section].items():ck(f'hash:{n}',sha(R/n)==h)
 z=dict(q);saved=z.pop('result_content_sha256');ck('content_hash',csha(z)==saved)
 bad=[n for n,x in checks if not x];out={'schema':'GDT199_VALIDATION_V1','status':'PASS' if not bad else 'FAIL','checks_passed':sum(x for _,x in checks),'checks_total':len(checks),'failed':bad,'result_sha256':sha(RESULT),'scope':'Independent inventory, prediction, failure, provenance, and hash validation; no semantic claim.'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True));raise SystemExit(bool(bad))
if __name__=='__main__':main()

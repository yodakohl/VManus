#!/usr/bin/env python3
"""Independent retained-artifact validation for GDT200."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt200_result.json';INV=R/'gdt200_f77_figure_zone_inventory.tsv';NULL=R/'gdt200_zone_assignment_null.tsv';OUT=R/'gdt200_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 q=json.loads(RESULT.read_text());rows=list(csv.DictReader(INV.open(),delimiter='\t'));n=list(csv.DictReader(NULL.open(),delimiter='\t'))[0];checks=[]
 def ck(k,x):checks.append((k,bool(x)))
 ck('schema',q['schema']=='GDT200_F77_FIGURE_ZONE_RENDERER_RESULT_V1');ck('status',q['status']=='PERFECT_LOCAL_ZONE_RENDERER_PATTERN_POSTHOC_ONE_FOLIO');ck('four_rows',len(rows)==4)
 upper=[r for r in rows if r['zone']=='UPPER_TUBE_ENDPOINT'];lower=[r for r in rows if r['zone']!='UPPER_TUBE_ENDPOINT'];ck('two_two',len(upper)==len(lower)==2);ck('upper_d',all(r['all_reading_renderer']=='STARTS_D' for r in upper));ck('lower_ot',all(r['all_reading_renderer']=='STARTS_OT' for r in lower));ck('proximity_only',all(r['ownership_evidence']=='PROXIMITY_ONLY' for r in rows));ck('canvas_hash',all(r['canvas_sha256']=='9ad387ccea37cd8a25ce9602817eb19af5105c545a238203715efe454e5b24ad' for r in rows));ck('null',n['worlds']=='6' and n['directional_worlds_at_least_observed']=='1' and n['orientation_free_worlds_at_least_observed']=='2');ck('p',q['directional_p']==1/6 and q['orientation_free_p']==2/6);ck('no_f84',not any(r['locus'].startswith('f84') for r in rows) and not any(q['f84r'].values()))
 for sec in ('inputs','implementation','outputs','documents'):
  for f,h in q[sec].items():ck('hash:'+f,sha(R/f)==h)
 z=dict(q);s=z.pop('result_content_sha256');ck('content_hash',csha(z)==s);bad=[k for k,x in checks if not x];o={'schema':'GDT200_VALIDATION_V1','status':'PASS' if not bad else 'FAIL','checks_passed':sum(x for _,x in checks),'checks_total':len(checks),'failed':bad,'result_sha256':sha(RESULT),'scope':'Independent four-label partition, exact-null, provenance, and hash validation; direct visual description remains machine-authored.'};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps(o,sort_keys=True));raise SystemExit(bool(bad))
if __name__=='__main__':main()

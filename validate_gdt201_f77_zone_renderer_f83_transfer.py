#!/usr/bin/env python3
"""Validate the exact GDT201 fixed-rule transfer."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt201_result.json';PRED=R/'gdt201_f83r_zone_predictions.tsv';OUT=R/'gdt201_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 q=json.loads(RESULT.read_text());r=list(csv.DictReader(PRED.open(),delimiter='\t'));checks=[]
 def ck(k,x):checks.append((k,bool(x)))
 ck('schema',q['schema']=='GDT201_F77_ZONE_RENDERER_F83_TRANSFER_RESULT_V1');ck('status',q['status']=='F77_ZONE_RENDERER_FAILS_COMPARABLE_F83_PANEL');ck('four',len(r)==4);ck('loci',set(x['locus'] for x in r)=={'f83r.45','f83r.46','f83r.50','f83r.51'});ck('zero_hits',sum(x['all_reading_prediction_correct']=='1' for x in r)==q['exact_hits']==0);ck('four_misses',q['exact_misses']==4);ck('reading_agreement',all(x['reading_agreement_on_renderer']=='1' for x in r));ck('upper_pred',all(x['prediction']=='STARTS_D' for x in r[:2]));ck('lower_pred',all(x['prediction']=='STARTS_OT' for x in r[2:]));ck('no_f84',not any(x['locus'].startswith('f84') for x in r) and not any(q['f84r'].values()))
 for sec in ('inputs','implementation','outputs','documents'):
  for f,h in q[sec].items():ck('hash:'+f,sha(R/f)==h)
 z=dict(q);s=z.pop('result_content_sha256');ck('content_hash',csha(z)==s);bad=[k for k,x in checks if not x];o={'schema':'GDT201_VALIDATION_V1','status':'PASS' if not bad else 'FAIL','checks_passed':sum(x for _,x in checks),'checks_total':len(checks),'failed':bad,'result_sha256':sha(RESULT),'scope':'Independent four-target prediction, alternate-reading, provenance, and hash validation; no semantic claim.'};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps(o,sort_keys=True));raise SystemExit(bool(bad))
if __name__=='__main__':main()

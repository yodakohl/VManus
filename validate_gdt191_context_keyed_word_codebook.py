#!/usr/bin/env python3
"""Accounting and artifact validator for GDT191."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt191_result.json';OUT=ROOT/'gdt191_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding='utf8') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());runs=read('gdt191_context_codebook_runs.tsv');summary=read('gdt191_context_codebook_summary.tsv');strata=read('gdt191_context_codebook_strata.tsv');counter=read('gdt191_counterexamples.tsv');c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)})
 ck('status',r['status']=='CONTEXT_KEYED_WORD_NOMENCLATOR_FALSIFIED');ck('runs_90',len(runs)==90);ck('summary_30',len(summary)==30);ck('partitions',{x['partition'] for x in runs}=={'GLOBAL','CURRIER','SECTION','HAND','PHYSICAL_FOLIO'});ck('languages',len({x['language'] for x in runs})==6);ck('seeds',{int(x['seed']) for x in runs}=={19101,19102,19103});ck('strata_nonempty',len(strata)>100);ck('counterexamples',len(counter)>=5);ck('all_local',all(int(x['all_strata_locally_optimal'])==1 for x in runs));ck('gap_arithmetic',all(abs(float(x['paid_total_bits'])-float(x['matched_null_total_bits'])-float(x['gap_vs_matched_kt_bits']))<2e-6 for x in runs));ck('all_fail',all(float(x['gap_vs_matched_kt_bits'])>0 for x in runs));ck('best_folio',r['best']['partition']=='PHYSICAL_FOLIO');ck('best_gap_positive',float(r['best']['gap_vs_matched_kt_bits'])>0);ck('summary_best',all(float(s['paid_total_bits'])==min(float(x['paid_total_bits']) for x in runs if x['partition']==s['partition'] and x['language']==s['language']) for s in summary));ck('input_hashes',all(sha(ROOT/n)==v for n,v in r['inputs'].items()));ck('output_hashes',all(sha(ROOT/n)==v for n,v in r['outputs'].items()));ck('doc_hashes',all(sha(ROOT/n)==v for n,v in r['documents'].items()));ck('implementation_hashes',all(sha(ROOT/n)==v for n,v in r['implementation'].items()));ck('f84_false',r['f84r_accessed'] is False)
 ok=all(x['pass'] for x in c);payload={'status':'PASS' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in c),'checks_total':len(c),'result_sha256':sha(RESULT),'checks':c};OUT.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n');print(payload['status'],payload['checks_passed']);raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()

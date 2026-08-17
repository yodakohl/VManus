#!/usr/bin/env python3
"""Artifact/accounting validator for GDT193."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt193_result.json';OUT=ROOT/'gdt193_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding='utf8') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());runs=read('gdt193_consonantal_runs.tsv');summary=read('gdt193_consonantal_summary.tsv');counter=read('gdt193_counterexamples.tsv');c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)})
 ck('status',r['status']=='COMPILER_STRIPPED_CONSONANTAL_FALSIFIED');ck('runs_18',len(runs)==18);ck('summary_6',len(summary)==6);ck('languages',len({x['language'] for x in runs})==6);ck('seeds',{int(x['seed']) for x in runs}=={19301,19302,19303});ck('active_20',all(int(x['active_source_signs'])==20 for x in runs));ck('mapping_size',all(len(x['mapping'].split('|'))==20 for x in runs));ck('mapping_hash',all(hashlib.sha256(x['mapping'].encode()).hexdigest()==x['mapping_hash'] for x in runs));ck('local',all(int(x['all_eligible_swaps_locally_optimal'])==1 for x in runs));ck('key',all(abs(float(x['mapping_key_bits'])-math.lgamma(22)/math.log(2))<1e-8 for x in runs));ck('gap_math',all(abs(float(x['paid_total_bits'])-float(x['matched_null_total_bits'])-float(x['gap_vs_matched_kt_bits']))<2e-6 for x in runs));ck('all_fail',all(float(x['gap_vs_matched_kt_bits'])>50000 for x in runs));ck('improves_literal',r['gap_reduction_bits']>30000);ck('counterexamples',len(counter)>=5);ck('input_hashes',all(sha(ROOT/n)==v for n,v in r['inputs'].items()));ck('output_hashes',all(sha(ROOT/n)==v for n,v in r['outputs'].items()));ck('doc_hashes',all(sha(ROOT/n)==v for n,v in r['documents'].items()));ck('implementation_hashes',all(sha(ROOT/n)==v for n,v in r['implementation'].items()));ck('f84_false',r['f84r_accessed'] is False)
 ok=all(x['pass'] for x in c);payload={'status':'PASS' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in c),'checks_total':len(c),'result_sha256':sha(RESULT),'checks':c};OUT.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n');print(payload['status'],payload['checks_passed']);raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()

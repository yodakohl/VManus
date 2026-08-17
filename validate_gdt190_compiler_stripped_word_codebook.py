#!/usr/bin/env python3
"""Integrity/accounting validator for GDT190 retained artifacts."""
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt190_result.json';OUT=ROOT/'gdt190_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):
 with (ROOT/name).open(encoding='utf8') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RESULT.read_text());runs=read('gdt190_word_codebook_runs.tsv');summary=read('gdt190_word_codebook_summary.tsv');nulls=read('gdt190_word_codebook_nulls.tsv');counter=read('gdt190_counterexamples.tsv');checks=[]
 def ck(name,value):checks.append({'check':name,'pass':bool(value)})
 ck('status',r['status']=='COMPILER_STRIPPED_WORD_NOMENCLATOR_FALSIFIED');ck('runs_72',len(runs)==72);ck('summary_24',len(summary)==24);ck('nulls_4',len(nulls)==4);ck('counterexamples',len(counter)>=5)
 ck('k_grid',{int(x['k']) for x in runs}=={8,16,32,64});ck('languages',len({x['language'] for x in runs})==6);ck('seeds',{int(x['seed']) for x in runs}=={19001,19002,19003})
 ck('all_local',all(int(x['all_pair_swaps_locally_optimal'])==1 for x in runs));ck('mapping_sizes',all(len(x['mapping'].split('|'))==int(x['k']) for x in runs));ck('mapping_hashes',all(hashlib.sha256(x['mapping'].encode()).hexdigest()==x['mapping_hash'] for x in runs))
 null={int(x['k']):x for x in nulls};ck('gap_arithmetic',all(abs(float(x['paid_total_bits'])-float(x['matched_null_total_bits'])-float(x['gap_vs_matched_kt_bits']))<2e-6 for x in runs));ck('null_join',all(abs(float(x['matched_null_total_bits'])-float(null[int(x['k'])]['matched_null_total_bits']))<1e-8 for x in runs))
 ck('permutation_keys',all(abs(float(x['mapping_key_bits'])-math.lgamma(int(x['k'])+1)/math.log(2))<1e-8 for x in runs));ck('all_gaps_positive',all(float(x['gap_vs_matched_kt_bits'])>0 for x in runs));ck('best_gap_large',float(r['best']['gap_vs_matched_kt_bits'])>500)
 ck('summary_best',all(float(s['paid_total_bits'])==min(float(x['paid_total_bits']) for x in runs if x['language']==s['language'] and int(x['k'])==int(s['k'])) for s in summary));ck('hash_inputs',all(sha(ROOT/n)==v for n,v in r['inputs'].items()));ck('hash_outputs',all(sha(ROOT/n)==v for n,v in r['outputs'].items()));ck('hash_docs',all(sha(ROOT/n)==v for n,v in r['documents'].items()));ck('hash_implementation',all(sha(ROOT/n)==v for n,v in r['implementation'].items()));ck('f84_false',r['f84r_accessed'] is False)
 ok=all(x['pass'] for x in checks);payload={'status':'PASS' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'checks':checks};OUT.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n');print(payload['status'],payload['checks_passed']);raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()

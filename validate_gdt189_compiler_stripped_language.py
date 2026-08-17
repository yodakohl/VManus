#!/usr/bin/env python3
import csv,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt189_result.json';VAL=R/'gdt189_validation.json';RUN=R/'gdt189_language_runs.tsv';SUM=R/'gdt189_language_summary.tsv';REP=R/'gdt189_representation_summary.tsv';NULL=R/'gdt189_matched_nulls.tsv';CO=R/'gdt189_counterexamples.tsv';M=R/'GDT189_COMPILER_STRIPPED_LANGUAGE_METHOD.md';P=R/'GDT189_COMPILER_STRIPPED_LANGUAGE_REPORT.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 with p.open() as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RES.read_text());runs=rd(RUN);summ=rd(SUM);reps=rd(REP);nulls=rd(NULL);c=rd(CO);z=[]
 def ck(n,x):assert x,n;z.append(n)
 ck('status',r['status']=='COMPILER_STRIPPED_INJECTIVE_LANGUAGE_FALSIFIED')
 ck('runs',len(runs)==54 and r['counts']['runs']==54)
 ck('summary',len(summ)==18 and r['counts']['summary_rows']==18)
 ck('representations',{x['representation'] for x in reps}=={'RAW_VISIBLE','RESIDUAL_HOST','PAGE_HOST'})
 ck('languages',len({x['language'] for x in runs})==6)
 ck('seeds',len({x['seed'] for x in runs})==3)
 ck('local_optima',all(x['all_pair_swaps_locally_optimal']=='1' for x in runs))
 ck('nulls',len(nulls)==3)
 ck('gap_arithmetic',all(abs(float(x['gap_vs_matched_kt_bits'])-(float(x['paid_total_bits'])-float(next(n['matched_null_total_bits'] for n in nulls if n['representation']==x['representation']))))<1e-6 for x in runs))
 page=next(x for x in reps if x['representation']=='PAGE_HOST')
 ck('page_gap_positive',float(page['gap_vs_matched_kt_bits'])>100000)
 ck('page_counts',int(page['physical_lines'])==r['counts']['physical_lines'] and int(page['active_source_signs'])==20)
 ck('gates_fail',not r['gates']['all_pass'] and not r['gates']['page_host_beats_matched_kt'])
 ck('counterexamples',len(c)==5)
 ck('f84',r['f84r_accessed'] is False)
 ck('output_hashes',all(r['outputs'][p.name]==sha(p) for p in (RUN,SUM,REP,NULL,CO)))
 ck('docs',r['documents'][M.name]==sha(M) and r['documents'][P.name]==sha(P))
 ck('impl',r['implementation']['run_gdt189_compiler_stripped_language.py']==sha(R/'run_gdt189_compiler_stripped_language.py'))
 out={'experiment':'GDT189_VALIDATION','status':'PASS_RETAINED_SCORE_ACCOUNTING','checks':len(z),'check_names':z,'result_sha256':sha(RES),'scope':'retained score/accounting validation; C++ scoring implementation hash-bound'};VAL.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS',len(z))
if __name__=='__main__':main()

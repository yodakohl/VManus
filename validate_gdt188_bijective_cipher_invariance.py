#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt188_result.json';VAL=R/'gdt188_validation.json';TAB=R/'gdt188_invariance_comparison.tsv';AX=R/'gdt188_invariant_axes.tsv';CO=R/'gdt188_counterexamples.tsv';M=R/'GDT188_BIJECTIVE_CIPHER_INVARIANCE_METHOD.md';P=R/'GDT188_BIJECTIVE_CIPHER_INVARIANCE_REPORT.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 with p.open() as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=json.loads(RES.read_text());t=rd(TAB);a=rd(AX);c=rd(CO);z=[]
 def ck(n,x):assert x,n;z.append(n)
 ck('status',r['status']=='DIRECT_BIJECTIVE_SCIENTIFIC_CIPHER_INSUFFICIENT_FOR_FROZEN_LATIN_CONTROLS')
 ck('three_comparators',len(t)==3)
 ck('all_fail',all(x['direct_bijective_cipher_gate']=='FAIL' for x in t))
 ck('unchanged',all(x['value_after_any_fixed_symbol_bijection']=='UNCHANGED' for x in t))
 ck('latin15_ratio',abs(float(t[0]['voynich_to_corpus_density_ratio'])-32.1279285)<1e-5)
 ck('medical_ratio',float(t[1]['voynich_to_corpus_density_ratio'])>50)
 ck('excess_ratio',abs(float(t[0]['voynich_to_corpus_excess_ratio'])-31.759511756)<1e-6)
 ck('axes',len(a)==10 and sum(x['invariant'].startswith('YES') for x in a)==9)
 ck('counterexamples',len(c)==5)
 ck('decision',r['decision']=='VISIBLE_TEXT_REQUIRES_NONBIJECTIVE_OR_COMPILER_LAYER_BEFORE_LANGUAGE_DECODING')
 ck('f84',r['f84r_accessed'] is False)
 ck('hashes',all(r['outputs'][p.name]==sha(p) for p in (TAB,AX,CO)))
 ck('docs',r['documents'][M.name]==sha(M) and r['documents'][P.name]==sha(P))
 ck('impl',r['implementation']==sha(R/'run_gdt188_bijective_cipher_invariance.py'))
 out={'experiment':'GDT188_VALIDATION','status':'PASS','checks':len(z),'check_names':z,'result_sha256':sha(RES)};VAL.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS',len(z))
if __name__=='__main__':main()

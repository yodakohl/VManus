#!/usr/bin/env python3
"""Post-count algebraic necessary-key bounds, not a decoder or primary gate."""
import hashlib,itertools,json,math
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def count(n,c,t):return math.perm(c,t)*math.factorial(n-t) if t<=c else 0
def main():
 fixtures=0
 for n in range(1,7):
  ps=list(itertools.permutations(range(n)))
  for c in range(n+1):
   for t in range(n+1):
    direct=sum(all(source<c for source,out in enumerate(p) if out<t) for p in ps)
    assert direct==count(n,c,t);fixtures+=1
 p=B/'artifacts/RESULT.json';r=json.loads(p.read_text());n=len(r['source']['alphabet']);c=r['source']['single_word_types'];allkeys=math.factorial(n);rows={}
 for reader,v in r['readers'].items():
  rows[reader]={}
  for tier,entry in v['tiers'].items():
   k=count(n,c,entry['types']);fraction=Fraction(k,allkeys)
   rows[reader][tier]={'required_native_singletons':entry['types'],'necessary_keys':str(k),'all_bijections':str(allkeys),'remaining_fraction_numerator':str(fraction.numerator),'remaining_fraction_denominator':str(fraction.denominator)}
 out={'status':'POST_COUNT_ANALYTIC_COROLLARY','formula':'P(C,t)*(n-t)! if t<=C else0','alphabet_size':n,'source_singletons':c,'readers':rows,'exhaustive_small_parameter_cases':fixtures,'primary_result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'limits':['Keys satisfy only necessary singleton membership, not full writer, source reading or contraction uniqueness.','Fixed W and22-unit/sourceword premises only; no global Voynich search-space percentage.','This derivation followed source counting and does not alter any preregistered gate or primary result.']}
 (B/'artifacts/KEYSPACE_COROLLARY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'IT_ALL':rows['IT2a']['ALL'],'ZL_ALL':rows['ZL3b']['ALL'],'small_parameter_cases':fixtures},indent=2))
if __name__=='__main__':main()

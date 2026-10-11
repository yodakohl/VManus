from pathlib import Path
from fractions import Fraction
from itertools import product
from math import factorial,prod
from collections import Counter
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
F=Fraction;words=['a','b','bb'];pi=[F(1,4),F(3,4)];selected=['b','b','a','bb']
def sp(c,mode):
 value=pi[c[0]]
 for i in range(1,len(c)):
  value*=pi[c[i]] if mode=='IID' else (F(3,4) if c[i]==c[i-1] else F(1,4))
 return value
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 saved=json.loads((B/'artifacts/ALL_VALUES.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());checked=0;grids={F(j,k) for k in range(1,5) for j in range(k+1)};bagchecks=0
 for mode in ('IID','MARKOV'):
  hist={}
  for c in product((0,1),repeat=4):hist[c.count(0),c.count(1)]=hist.get((c.count(0),c.count(1)),F(0))+sp(c,mode)
  assert sum(hist.values())==1
  for name,mapping in [('K1',{'a':0,'b':1,'bb':0}),('K2',{'a':1,'b':1,'bb':0})]:
   label=mode+'_'+name;classes=[[w for w in words if mapping[w]==c] for c in (0,1)];double=next(pool for pool in classes if len(pool)==2);single=next(pool[0] for pool in classes if len(pool)==1);seenbags={};total=F(0);nmax=0;fixedtotal=F(0)
   fixedcounts=Counter(selected);fixedem={single:F(1),double[0]:F(fixedcounts[double[0]],sum(fixedcounts[w] for w in double)),double[1]:F(fixedcounts[double[1]],sum(fixedcounts[w] for w in double))}
   for row,w in zip(saved[label],product(words,repeat=4)):
    assert row['cipher']==list(w);counts=Counter(w);c=tuple(mapping[v] for v in w);nc=(c.count(0),c.count(1));nw=tuple(counts[v] for v in words);s=sp(c,mode);likelihoods=[]
    # The polynomial p^a(1-p)^b is maximized at a/(a+b), or a boundary.
    # All such rational points for at most4visits occur in this complete grid.
    for p in grids:
     em={single:F(1),double[0]:p,double[1]:1-p};likelihoods.append(s*prod((em[v] for v in w),start=F(1)))
    optimum=max(likelihoods);mult=F(prod(factorial(n) for n in nc),prod(factorial(n) for n in nw));conditional=s/(mult*hist[nc]);assert F(row['source_probability'])==s and F(row['profile_supremum'])==optimum and F(row['bag_conditional_probability'])==conditional;assert row['word_counts']==list(nw) and row['source_counts']==list(nc) and row['decoded']==list(c)
    boundary=(sum(counts[v] for v in double)>0 and any(counts[v]==0 for v in double));assert row['attainment']==('SUPREMUM_ONLY' if boundary else 'MAXIMUM');nmax+=not boundary;seenbags[nw]=seenbags.get(nw,F(0))+conditional;total+=optimum;fixedtotal+=s*prod((fixedem[v] for v in w),start=F(1));checked+=1
    empirical=prod((F(n,4)**n for n in nw if n),start=F(1));emhat=prod((F(counts[v],nc[mapping[v]]) for v in w),start=F(1));assert prod((F(n,4)**n for n in nc if n),start=F(1))*emhat==empirical
    if mode=='IID':
     assert conditional==F(prod(factorial(n) for n in nw),factorial(4));assert optimum==empirical*prod(((pi[i]/F(n,4))**n for i,n in enumerate(nc) if n),start=F(1))
   assert len(seenbags)==15 and all(v==1 for v in seenbags.values());bagchecks+=15;assert fixedtotal==1 and total>1;summary=result['cases'][label];assert F(summary['sum_profile_likelihoods_not_probability'])==total and summary['fixed_fitted_channel_total']=='1' and summary['attained_profiles']==nmax and summary['cipher_tuples']==81 and summary['word_bags']==15 and summary['IID_KL_identity_checks']==(81 if mode=='IID' else 0);assert summary['selected']==next(r for r in saved[label] if r['cipher']==selected)
 assert result['cases']['IID_K1']['selected']['profile_supremum']=='9/1024';assert result['cases']['IID_K2']['selected']['profile_supremum']=='1/64';assert result['cases']['MARKOV_K1']['selected']['bag_conditional_probability']=='27/104';assert result['cases']['MARKOV_K2']['selected']['bag_conditional_probability']=='1/6'
 out={'status':'PASS','exact_tuple_key_law_checks':checked,'conditional_bag_normalizations':bagchecks,'fixed_fitted_channel_normalizations':4,'method':'Direct emission-polynomial maximization over all possible rational count optima; independent binary source-histogram enumeration and factorial multiplicity; exact arithmetic, no runner import.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

import collections,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 s=json.loads((B/'src/SPEC.json').read_text());alphabet=s['alphabet'];alpha=F(s['alpha']);train=s['train'];N=sum(train.values());k=s['cut'];length=s['length'];t=collections.defaultdict(collections.Counter);left=collections.Counter();right=collections.defaultdict(collections.Counter);ends=collections.Counter()
 for w,c in train.items():
  assert len(w)==length and set(w)<=set(alphabet);l,r=w[:k],w[k:];left[l]+=c;right[l[-1]][r]+=c;ends[l[-1]]+=c
  for i,x in enumerate(w):t[i,w[i-1] if i else '^'][x]+=c
 oracle={w:F(p) for w,p in s['oracle_words'].items()};generator={l+r:F(pl)*F(pr) for l,pl in s['oracle_left'].items() for r,pr in s['oracle_right'][l[-1]].items()};assert generator==oracle and sum(oracle.values())==1
 fit={l+r:F(lc,N)*F(rc,ends[l[-1]]) for l,lc in left.items() for r,rc in right[l[-1]].items()};assert fit==oracle
 for counts in t.values():assert sum((F(counts.get(a,0))+alpha)/(sum(counts.values())+len(alphabet)*alpha) for a in alphabet)==1
 records=[];certificate=F(1);den=s['sign_denominator'];unseen_mass=sum(p for w,p in oracle.items() if w not in train);assert unseen_mass>0
 for w,h in sorted(oracle.items()):
  factors=[]
  for i,a in enumerate(w):counts=t.get((i,w[i-1] if i else '^'),{});factors.append((F(counts.get(a,0))+alpha)/(sum(counts.values())+len(alphabet)*alpha))
  p=math.prod(factors);mix=(p+h)/2;ratio=mix/p;weight=h*den;assert weight.denominator==1;certificate*=ratio**weight.numerator
  records.append({'word':w,'train_count':train.get(w,0),'H':str(h),'M1_factors':[str(f) for f in factors],'M1':str(p),'MIX':str(mix),'ratio':str(ratio),'raw_gain':math.log(float(ratio)),'unseen':w not in train})
 allgain=sum(float(F(r['H']))*r['raw_gain'] for r in records);unseengain=sum(float(F(r['H'])/unseen_mass)*r['raw_gain'] for r in records if r['unseen']);ucert=F(1)
 for r in records:
  if r['unseen']:ucert*=F(r['ratio'])**(F(r['H'])*den).numerator
 coefficient=math.factorial(N)//math.prod(math.factorial(c) for c in train.values());train_probability=F(coefficient)*math.prod(oracle[w]**c for w,c in train.items());assert train_probability>0
 passed=certificate>1 and ucert<1
 result={'status':'ORACLE_RAW_UNSEEN_COUNTEREXAMPLE_VERIFIED' if passed else 'COUNTEREXAMPLE_NOT_VERIFIED','train_words':N,'oracle_support':len(oracle),'oracle_equals_fitted_H':True,'training_multiset_probability':str(train_probability),'training_multiset_probability_decimal':float(train_probability),'unseen_oracle_mass':str(unseen_mass),'ALL_expected_raw_gain':allgain,'UNSEEN_expected_raw_gain':unseengain,'all_sign_product':str(certificate),'unseen_sign_product':str(ucert),'sign_denominator':den,'records':records,'ceiling':'Source-free logical counterexample only; no native score change, false-negative-rate estimate, historical construction or meaning.'}
 save('RESULT.json',result);print(json.dumps({k:result[k] for k in ['status','ALL_expected_raw_gain','UNSEEN_expected_raw_gain','unseen_oracle_mass','training_multiset_probability_decimal']}))
if __name__=='__main__':main()

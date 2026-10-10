import collections,decimal,hashlib,json,math
from fractions import Fraction as Q
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def D(q):q=Q(q);return decimal.Decimal(q.numerator)/decimal.Decimal(q.denominator)
def main():
 decimal.getcontext().prec=90
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 s=json.loads((B/'src/SPEC.json').read_text());r=json.loads((B/'artifacts/RESULT.json').read_text());a=s['alphabet'];assert len(a)==len(set(a))==22;train=[w for w,c in s['train'].items() for _ in range(c)];assert len(train)==54;rlen=s['length'];cut=s['cut'];alpha=Q(s['alpha'])
 def distribution(i,prev):
  relevant=[w[i] for w in train if i==0 or w[i-1]==prev];counts=collections.Counter(relevant);den=Q(len(relevant))+alpha*len(a)
  return {x:(Q(counts[x])+alpha)/den for x in a}
 mass={'^':Q(1)}
 for i in range(rlen):
  nxt=collections.defaultdict(Q)
  for prev,v in mass.items():
   row=distribution(i,prev);assert sum(row.values())==1
   for symbol,p in row.items():nxt[symbol]+=v*p
  mass=dict(nxt);assert sum(mass.values())==1
 oracle={}
 for l,p in s['oracle_left'].items():
  assert len(l)==cut
  for tail,q in s['oracle_right'][l[-1]].items():oracle[l+tail]=Q(p)*Q(q)
 assert oracle=={w:Q(p) for w,p in s['oracle_words'].items()} and sum(oracle.values())==1
 prefixes={w[:cut] for w in train};fitted={}
 for l in prefixes:
  lc=sum(w[:cut]==l for w in train);compatible=[w[cut:] for w in train if w[cut-1]==l[-1]]
  for tail in set(compatible):fitted[l+tail]=Q(lc,len(train))*Q(compatible.count(tail),len(compatible))
 assert fitted==oracle;unseen=set(oracle)-set(train);assert unseen=={'BACB'}
 total=decimal.Decimal(0);ugain=decimal.Decimal(0);umass=sum(oracle[w] for w in unseen);product=Q(1);uprod=Q(1);den=s['sign_denominator'];assert {x['word'] for x in r['records']}==set(oracle)
 for row in r['records']:
  w=row['word'];h=oracle[w];factors=[distribution(i,w[i-1] if i else '^')[symbol] for i,symbol in enumerate(w)];p=math.prod(factors);mixed=(p+h)/2;ratio=mixed/p;gain=D(ratio).ln();weight=h*den;assert weight.denominator==1;product*=ratio**int(weight);total+=D(h)*gain
  if w in unseen:uprod*=ratio**int(weight);ugain+=D(h/umass)*gain
  assert row['train_count']==train.count(w) and row['unseen']==(w in unseen);assert list(map(Q,row['M1_factors']))==factors
  for key,value in [('H',h),('M1',p),('MIX',mixed),('ratio',ratio)]:assert Q(row[key])==value
  assert abs(float(gain)-row['raw_gain'])<1e-12
 assert Q(r['all_sign_product'])==product>1 and Q(r['unseen_sign_product'])==uprod<1;assert abs(float(total)-r['ALL_expected_raw_gain'])<1e-12 and abs(float(ugain)-r['UNSEEN_expected_raw_gain'])<1e-12;assert Q(r['unseen_oracle_mass'])==umass==Q(2,81)
 assert abs(total-D(product).ln()/decimal.Decimal(den))<decimal.Decimal('1e-80')
 probability=math.prod(oracle[w] for w in train);coefficient=1;remaining=len(train)
 for count in s['train'].values():coefficient*=math.comb(remaining,count);remaining-=count
 probability*=coefficient;assert Q(r['training_multiset_probability'])==probability>0;assert abs(float(probability)-r['training_multiset_probability_decimal'])<1e-15;assert r['status']=='ORACLE_RAW_UNSEEN_COUNTEREXAMPLE_VERIFIED'
 # The compact witness has the exact factors and ratio announced before count.
 witness=next(x for x in r['records'] if x['word']=='BACB');assert Q(witness['M1'])==Q(75625,2363296) and Q(witness['ratio'])==Q(10852217,12251250)
 out={'status':'PASS','oracle_words_checked':len(oracle),'alphabet_size':len(a),'full_M1_mass':str(sum(mass.values())),'exact_signs':{'ALL':'>0','raw_UNSEEN':'<0'},'decimal_precision':90,'oracle_equals_fitted_H':True,'method':'Expanded toy occurrences, forward probability sum, explicit oracle generation, independent multinomial coefficient, exact rational sign products and90digitlogcheck. No native data or capacity-gate calibration.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

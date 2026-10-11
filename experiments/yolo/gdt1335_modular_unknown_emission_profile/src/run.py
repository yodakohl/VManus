from pathlib import Path
from fractions import Fraction as F
import collections,hashlib,itertools,json,math
B=Path(__file__).resolve().parents[1];R=B.parents[2]
BANK=('a','b','bb');KEYS={'K1':{'a':0,'b':1},'K2':{'a':1,'b':1}};PI=(F(1,4),F(3,4));TRANS={'IID':(PI,PI),'MARKOV':((F(3,4),F(1,4)),(F(1,4),F(3,4)))};OBS=('b','b','a','bb')
def source(c,law):
 p=PI[c[0]]
 for a,b in zip(c,c[1:]):p*=TRANS[law][a][b]
 return p
def counts(w,key):
 dec={word:sum(key[u] for u in word)%2 for word in BANK};nw=[w.count(u) for u in BANK];nc=[sum(n for word,n in zip(BANK,nw) if dec[word]==c) for c in (0,1)];return dec,nw,nc
def factor(nw,nc,dec):return math.prod((F(n,nc[dec[w]])**n for w,n in zip(BANK,nw) if n),start=F(1))
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 result={};allrows={};tuples=list(itertools.product(BANK,repeat=4))
 for law in TRANS:
  for name,key in KEYS.items():
   label=law+'_'+name;rows=[];bags=collections.defaultdict(lambda:F(0));bag_profiles=collections.defaultdict(lambda:F(0));total_profile=F(0);idchecks=0
   for w in tuples:
    dec,nw,nc=counts(w,key);c=tuple(dec[v] for v in w);ps=source(c,law);em=factor(nw,nc,dec);profile=ps*em;bags[tuple(nw)]+=ps;total_profile+=profile
    cipher_emp=math.prod((F(n,4)**n for n in nw if n),start=F(1));source_emp=math.prod((F(n,4)**n for n in nc if n),start=F(1));assert source_emp*em==cipher_emp
    if law=='IID':
     ratio=math.prod(((PI[i]/F(n,4))**n for i,n in enumerate(nc) if n),start=F(1));assert profile==cipher_emp*ratio;idchecks+=1
    attained=all(n>0 or nc[dec[v]]==0 for v,n in zip(BANK,nw));rows.append({'cipher':list(w),'word_counts':nw,'source_counts':nc,'decoded':list(c),'source_probability':str(ps),'profile_supremum':str(profile),'attainment':'MAXIMUM' if attained else 'SUPREMUM_ONLY'})
   for row in rows:
    conditional=F(row['source_probability'])/bags[tuple(row['word_counts'])];row['bag_conditional_probability']=str(conditional);bag_profiles[tuple(row['word_counts'])]+=conditional
   assert len(bags)==15 and all(p==1 for p in bag_profiles.values());selected=next(row for row in rows if tuple(row['cipher'])==OBS);dec,nw,nc=counts(OBS,key);emission={w:F(n,nc[dec[w]]) for w,n in zip(BANK,nw)};normalization=sum((source(tuple(dec[u] for u in w),law)*math.prod((emission[u] for u in w),start=F(1)) for w in tuples),F(0));assert normalization==1;assert total_profile>1
   result[label]={'selected':selected,'sum_profile_likelihoods_not_probability':str(total_profile),'fixed_fitted_channel_total':str(normalization),'word_bags':len(bags),'cipher_tuples':len(rows),'IID_KL_identity_checks':idchecks,'attained_profiles':sum(r['attainment']=='MAXIMUM' for r in rows)};allrows[label]=rows
 assert result['IID_K1']['selected']['profile_supremum']=='9/1024' and result['IID_K2']['selected']['profile_supremum']=='1/64'
 assert result['IID_K1']['selected']['bag_conditional_probability']==result['IID_K2']['selected']['bag_conditional_probability']=='1/12'
 assert result['MARKOV_K1']['selected']['source_probability']==result['MARKOV_K2']['selected']['source_probability']=='27/256'
 assert result['MARKOV_K1']['selected']['bag_conditional_probability']=='27/104' and result['MARKOV_K2']['selected']['bag_conditional_probability']=='1/6'
 out={'status':'PROFILE_AND_BAG_CONDITIONING_DISTINCT','cases':result,'scope':'Source-free analytical calculation with disclosed expected values; no recovery, native key, source language or bank binding.'};(B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');(B/'artifacts/ALL_VALUES.json').write_text(json.dumps(allrows,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

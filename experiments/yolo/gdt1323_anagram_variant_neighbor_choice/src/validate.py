import collections,gzip,hashlib,itertools,json,random,re
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 words=['ab','ab','ba'];arr=list(itertools.permutations(words));total=0
 for w in arr:
  total+=int(w[0][-1]==w[1][0])+int(w[1][-1]==w[2][0]);assert w.count('ab')==2 and w.count('ba')==1
  for a in range(3):
   for b in range(3):
    for t in w:
     v=0
     for g in t:v=(v+(a if g=='a' else b))%3
     assert v==(a+b)%3
 assert Fraction(total,len(arr))==Fraction(4,3)
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');old=read(R/'experiments/yolo/gdt1319_cross_word_endpoint_state/artifacts/PAIRS.json.gz');res=read(B/'artifacts/RESULT.json');npairs=nmob=nnull=0
 for ed,rr in sorted(data.items()):
  rows=sorted(rr,key=lambda r:r['id']);idx={r['id']:i for i,r in enumerate(rows)};panel=read(B/'artifacts'/f'{ed}_PANEL.json.gz');assert panel['ids']==[r['id'] for r in rows];pairs=[]
  for p in old[ed]:
   for side in ['left','right']:assert rows[idx[p[side]['id']]]==p[side]
   pairs.append([p['left']['id'],p['right']['id']])
  assert pairs==panel['pairs'];npairs+=len(pairs)
  cells=collections.defaultdict(list)
  for i,r in enumerate(rows):cells[(r['page'],tuple(sorted(r['units'])))].append(i)
  pools=[v for k,v in sorted(cells.items())];assert pools==panel['pools'];owner={i:j for j,p in enumerate(pools) for i in p};types=[collections.Counter(tuple(rows[i]['units']) for i in p) for p in pools];mobile=[];sums=collections.defaultdict(Fraction);n=collections.Counter()
  for aid,bid in pairs:
   i,j=idx[aid],idx[bid];a,b=owner[i],owner[j];num=den=0
   for x,cx in types[a].items():
    for y,cy in types[b].items():
     w=cx*(cy-int(a==b and x==y));den+=w;num+=w*int(x[-1]==y[0])
   prob=Fraction(num,den)
   if 0<prob<1:
    leaf=re.match(r'f(\d+)',rows[i]['page']).group(1);mobile.append({'left':i,'right':j,'leaf':leaf,'p':[prob.numerator,prob.denominator]});sums[leaf]+=prob;n[leaf]+=1
  assert mobile==panel['mobile'];nmob+=len(mobile);leaves=sorted(n,key=int);assert leaves==panel['leaves'];r=res['readers'][ed];observed=collections.Counter()
  for p in mobile:observed[p['leaf']]+=int(rows[p['left']]['units'][-1]==rows[p['right']]['units'][0])
  effects=[(Fraction(observed[l])-sums[l])/n[l] for l in leaves];T=float(sum(effects)/len(leaves)) if leaves else 0.;assert abs(T-r['T'])<1e-12
  for l,z in zip(leaves,r['leaf_results']):assert z['n']==n[l] and z['observed']==observed[l] and Fraction(*z['expected'])==sums[l]
  null=read(B/'artifacts'/f'{ed}_NULL_COUNTS.json.gz');rng=random.Random(1323);ts=[]
  for counts in null:
   perm=list(range(len(rows)))
   for pool in pools:
    if len(pool)>1:
     v=list(pool);rng.shuffle(v)
     for dst,src in zip(pool,v):perm[dst]=src
   score=collections.Counter()
   for p in mobile:score[p['leaf']]+=int(rows[perm[p['left']]]['units'][-1]==rows[perm[p['right']]]['units'][0])
   assert counts==[score[l] for l in leaves];ts.append(float(sum((Fraction(score[l])-sums[l])/n[l] for l in leaves)/len(leaves)));nnull+=1
  capacity=len(mobile)>=100 and len(leaves)>=10;assert len(null)==(1999 if capacity else 0)
  consistent=sum(v*T>0 for v in effects);assert consistent==r['direction_consistent_leaves'];status='NO_CAPACITY'
  if capacity:
   pv=(1+sum(abs(t)>=abs(T)-1e-12 for t in ts))/2000;assert pv==r['p_two_sided'];moving=max(ts)-min(ts)>1e-12;assert moving==r['score_mobile'];reject=moving and pv<=.05/3 and abs(T)>=.01 and 3*consistent>=2*len(leaves);status='INDEPENDENT_CHOICE_REJECTED' if reject else ('NOT_REJECTED' if moving else 'SCORE_IMMOBILE')
  assert status==r['status'];print(ed,'validated',len(mobile),len(null),flush=True)
 status='INDEPENDENT_ANAGRAM_CHOICE_REJECTED_ALL_READINGS' if all(r['status']=='INDEPENDENT_CHOICE_REJECTED' for r in res['readers'].values()) else 'NO_COMMON_ANAGRAM_CHOICE_REJECTION';assert res['status']==status
 out={'status':'PASS','original_pairs_verified':npairs,'mobile_edge_expectations_verified':nmob,'permutation_draws_rescored':nnull,'source_free_occurrence_arrangements':6,'scope':'Computational validation of existing strict panel and fixed conditional test; no independent palaeography or meaning.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

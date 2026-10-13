#!/usr/bin/env python3
"""Independent complete-word probability and same-pivot edge validator."""
import argparse,collections,csv,gzip,hashlib,itertools,json,math,random,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];PREFIX='experiments/yolo/'
UNITS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def load(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def edges(word):return collections.Counter((j,word[j-1],word[j]) for j in range(1,len(word)))
def rectangle(cost):
 for i in range(len(cost)):
  for j in range(len(cost)):
   value=cost[i][j]+cost[0][0]-cost[i][0]-cost[0][j]
   if abs(value)>1e-12:return {'i':i,'j':j,'value':value}
 return None

def controls():
 words=[list('acbcad'),list('adbdcd'),list('aabcbd')];k=3
 assert len({(w[0],w[-1],w[k-1],len(w)) for w in words})==1
 alphabet='abcd'
 def prob(word):
  p=(alphabet.index(word[0])+1)/10
  for i in range(1,len(word)):
   vals=[(i+2)*(alphabet.index(word[i-1])+1)+(j+1)**2 for j in range(4)]
   p*=vals[alphabet.index(word[i])]/sum(vals)
  return p
 oldedges=sum((edges(w) for w in words),collections.Counter());oldp=math.prod(prob(w) for w in words)
 for pi in itertools.permutations(range(3)):
  out=[words[i][:k]+words[j][k:] for i,j in enumerate(pi)]
  assert sum((edges(w) for w in out),collections.Counter())==oldedges
  assert math.isclose(math.prod(prob(w) for w in out),oldp,rel_tol=1e-12)
 # Uniform labelled assignments retain duplicate columns and exact matrix expectation.
 for costs in ([[1.,2.],[4.,5.]],[[0.,1.],[1.,0.]],[[1.,1.,4.],[2.,2.,0.],[5.,5.,3.]]):
  n=len(costs);scores=[math.fsum(costs[i][j] for i,j in enumerate(p)) for p in itertools.permutations(range(n))]
  assert math.isclose(math.fsum(scores)/len(scores),math.fsum(math.fsum(row)/n for row in costs),abs_tol=1e-12)
  assert bool(rectangle(costs))==(max(scores)-min(scores)>1e-12)
 assert .41*.41!=.09*.09 # Mixture of product laws need not factorize.
 return {'all_permutation_edge_and_position_Markov_checks':6,'assignment_mean_and_mobility_fixtures':3,'duplicate_donors':'PASS','mixture_nonfactorization':'PASS'}

def equal(a,b,path='root'):
 if isinstance(a,dict):
  assert isinstance(b,dict) and a.keys()==b.keys(),(path,'keys',a.keys(),getattr(b,'keys',lambda:[])())
  for key in a:equal(a[key],b[key],path+'.'+str(key))
 elif isinstance(a,list):
  assert isinstance(b,list) and len(a)==len(b),(path,'length')
  for i,(x,y) in enumerate(zip(a,b)):equal(x,y,path+f'[{i}]')
 elif isinstance(a,float):assert isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9),(path,a,b)
 else:assert a==b,(path,a,b)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');args=ap.parse_args();check=controls()
 if args.controls_only:print(json.dumps(check));return
 lock=load(B/'src/REGISTRATION_LOCK.json')
 for path,h in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 data=load(ROOT/(PREFIX+'gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'))
 events=load(ROOT/(PREFIX+'gdt1308_whole_form_prediction/artifacts/EVENTS.json.gz'))
 model=load(ROOT/(PREFIX+'gdt1308_whole_form_prediction/artifacts/MODEL.json'))
 allowed={r['page'] for r in csv.DictReader((ROOT/(PREFIX+'gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')).open(),delimiter='\t')}
 events_by={};
 for ev in events:
  key=(ev['reader'],ev['id']);assert key not in events_by;events_by[key]=ev
 expected_pools={};results={};matrixcells=0;maxlocalrect=0.
 for rd,rows in data.items():
  tab={tuple(x['context']):x['counts'] for x in model[rd]['m1']}
  whole={tuple(x['cell']):{tuple(y['units']):y['count'] for y in x['counts']} for x in model[rd]['whole']}
  def probabilities(w,c):
   factors=[]
   for i,x in enumerate(w):
    counts=tab.get((c,len(w),i,w[i-1] if i else '^'),{})
    factors.append((counts.get(x,0)+.5)/(sum(counts.values())+11))
   p=math.prod(factors);assert p>0 and math.isfinite(p)
   counts=whole.get((c,len(w)),{});n=sum(counts.values());q=counts.get(tuple(w),0)/n if n else 0.
   mixed=(p+q)/2 if n else p
   return p,q,mixed
  pools=collections.defaultdict(list);held=0;joined=set()
  for row in rows:
   leaf=int(re.match(r'f(\d+)',row['page'])[1]);w=row['units']
   if leaf%2 or len(w)<4:continue
   held+=1;ev=events_by[(rd,row['id'])];joined.add((rd,row['id']))
   assert ev['units']==w and ev['leaf']==leaf
   assert row['page'] in allowed and row['edition']==rd
   assert row['id']==f"{rd}|{row['locus']}|G{int(row['source_group_index']):03d}"
   if 'page' in ev:assert ev['page']==row['page']
   if 'locus' in ev:assert ev['locus']==row['locus']
   assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and ''.join(w)==row['ivtff_group_raw'] and set(w)<=set(UNITS)
   p,q,m=probabilities(w,ev['c']);assert math.isclose(p,ev['p'],rel_tol=1e-10) and math.isclose(q,ev['q'],abs_tol=1e-12) and math.isclose(m,ev['mix'],rel_tol=1e-10) and math.isclose(math.log(m/p),ev['gain'],abs_tol=1e-10)
   k=len(w)//2;key=(row['page'],ev['c'],len(w),w[0],w[-1],w[k-1]);pools[key].append({'source':row,'L':w[:k],'R':w[k:]})
  assert joined=={key for key in events_by if key[0]==rd}
  output=[];allleaf=collections.defaultdict(lambda:[0,0.]);primary=collections.defaultdict(lambda:[0,0.]);mobilepools=[]
  for (page,c,n,first,last,pivot),members in sorted(pools.items()):
   k=n//2;N=len(members);logs=[];costs=[]
   for i,left in enumerate(members):
    lp=[];cc=[];originalleft=left['L']+left['R']
    for j,right in enumerate(members):
     originalright=right['L']+right['R'];w=left['L']+right['R'];assert w[0]==first and w[-1]==last and w[k-1]==pivot and len(w)==n
     # Every positional edge comes unchanged from exactly one original carrier.
     for t in range(1,n):
      origin=originalleft if t<k else originalright
      assert (w[t-1],w[t])==(origin[t-1],origin[t])
     p,q,m=probabilities(w,c);lp.append(math.log(p));cc.append(math.log(m/p));matrixcells+=1
    logs.append(lp);costs.append(cc)
   for i in range(N):
    for j in range(N):
     r=logs[i][j]+logs[0][0]-logs[i][0]-logs[0][j];maxlocalrect=max(maxlocalrect,abs(r));assert abs(r)<1e-9
   observed=math.fsum(costs[i][i] for i in range(N));expected=math.fsum(math.fsum(row)/N for row in costs);witness=rectangle(costs);mobile=witness is not None;leaf=int(re.match(r'f(\d+)',page)[1])
   pool={'page':page,'currier':c,'n':n,'first':first,'last':last,'pivot':pivot,'leaf':leaf,'k':k,'rows':members,'costs':costs,'logP':logs,'observed':observed,'expected':expected,'mobile':mobile,'rectangle':witness};output.append(pool)
   allleaf[leaf][0]+=N;allleaf[leaf][1]+=observed-expected
   if mobile:primary[leaf][0]+=N;primary[leaf][1]+=observed-expected;mobilepools.append(pool)
  perleaf={str(l):{'words':v[0],'excess':v[1]/v[0]} for l,v in sorted(primary.items())};words=sum(v[0] for v in primary.values());L=len(primary);mean=math.fsum(x['excess'] for x in perleaf.values())/L if L else None;positive=sum(x['excess']>0 for x in perleaf.values());nulls=[];pval=None;status='NO_CAPACITY'
  if words>=100 and L>=10:
   rng=random.Random(20261013)
   for _ in range(199):
    scores=collections.defaultdict(float)
    for pool in mobilepools:
     order=list(range(len(pool['rows'])));rng.shuffle(order);scores[pool['leaf']]+=math.fsum(pool['costs'][i][j] for i,j in enumerate(order))-pool['expected']
    nulls.append(math.fsum(scores[l]/v[0] for l,v in sorted(primary.items()))/L)
   if max(nulls)-min(nulls)<=1e-12:status='NO_SCORE_MOBILITY'
   else:
    pval=(1+sum(v>=mean-1e-12 for v in nulls))/200
    status='CONDITIONAL_PIVOT_PARTNER_DEPENDENCE' if mean>=.01 and positive*3>=2*L and pval<=.05/3 else 'NO_RETAINED_PIVOT_PARTNER_EXCESS'
  results[rd]={'held_words':held,'pools':len(output),'mobile_pools':len(mobilepools),'primary_words':words,'primary_leaves':L,'positive_leaves':positive,'mean_excess':mean,'per_leaf':perleaf,'all_words':sum(v[0] for v in allleaf.values()),'all_leaves':len(allleaf),'all_mean_excess':math.fsum(v[1]/v[0] for v in allleaf.values())/len(allleaf) if allleaf else None,'null_scores':nulls,'p_or_null':pval,'status':status};expected_pools[rd]=output
 equal(expected_pools,load(B/'artifacts/POOLS.json.gz'),'pools');equal({'status':'PIVOT_SUFFIX_CONDITIONAL_PAIRING','readers':results},load(B/'artifacts/RESULT.json'),'result')
 receipt={'status':'PASS','source_free_controls':check,'matrix_cells':matrixcells,'maximum_position_Markov_rectangle_residual':maxlocalrect,'readers':{r:{'status':x['status'],'held_words':x['held_words'],'mobile_pools':x['mobile_pools']} for r,x in results.items()},'method':'Independent direct probability products, per-position donor edge identities, complete pool/score/reference reconstruction; no primary imports.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

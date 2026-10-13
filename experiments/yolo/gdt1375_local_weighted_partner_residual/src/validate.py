#!/usr/bin/env python3
"""Independent subset-DP validator, authored before primary/native weights."""
import argparse, functools, gzip, hashlib, itertools, json, math, random
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
OLD='experiments/yolo/'
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def logadd(a,b):
 m=max(a,b);return m+math.log(math.exp(a-m)+math.exp(b-m))
def weave(mask,a,b):
 aa=iter(a);bb=iter(b);out=[next(aa) if bit==0 else next(bb) for bit in mask]
 assert list(aa)==[] and list(bb)==[];return out

def dp(logweights,score):
 n=len(logweights);shift=[max(row) for row in logweights];w=[[math.exp(x-shift[i]) for x in row] for i,row in enumerate(logweights)]
 assert all(x>0 and math.isfinite(x) for row in w for x in row)
 @functools.lru_cache(None)
 def rec(mask):
  if not mask:return (1.,0.)
  row=n-mask.bit_count();terms=[];moments=[]
  for j in range(n):
   if mask>>j&1:
    z,m=rec(mask^(1<<j));terms.append(w[row][j]*z);moments.append(w[row][j]*(m+score[row][j]*z))
  z=math.fsum(terms);assert z>0 and math.isfinite(z)
  return z,math.fsum(moments)
 full=(1<<n)-1;z,m=rec(full)
 def draw(u):
  mask=full;chosen=[]
  while mask:
   i=n-mask.bit_count();denom=rec(mask)[0];cum=0.;available=[j for j in range(n) if mask>>j&1]
   for j in available:
    prob=w[i][j]*rec(mask^(1<<j))[0]/denom
    if u<cum+prob or j==available[-1]:
     u=(u-cum)/prob;assert -1e-9<=u<=1+1e-9;u=min(max(u,0.),math.nextafter(1.,0.));chosen.append(j);mask^=1<<j;break
    cum+=prob
  return chosen
 return math.fsum(shift)+math.log(z),m/z,draw

def rect(mat):
 for i in range(len(mat)):
  for j in range(len(mat)):
   v=mat[i][j]+mat[0][0]-mat[i][0]-mat[0][j]
   if abs(v)>1e-12:return {'i':i,'j':j,'value':v}
 return None

def controls():
 fixtures=[[[.2,.4],[.3,.7]],[[.2,.2,.5],[.8,.8,.1],[.3,.3,.4]],[[.5,.5],[.5,.5]]]
 for matrix in fixtures:
  n=len(matrix);logs=[[math.log(x) for x in row] for row in matrix];scores=[[float((i-j)**2) for j in range(n)] for i in range(n)]
  zz,mean,draw=dp(logs,scores);perms=list(itertools.permutations(range(n)));weights=[math.prod(matrix[i][j] for i,j in enumerate(p)) for p in perms];total=math.fsum(weights)
  assert abs(zz-math.log(total))<1e-12
  assert abs(mean-math.fsum(weight*sum(scores[i][j] for i,j in enumerate(p)) for weight,p in zip(weights,perms))/total)<1e-12
  for u in (.01,.17,.41,.63,.97):
   cum=0
   for p,weight in zip(perms,weights):
    cum+=weight/total
    if u<cum:assert tuple(draw(u))==p;break
  shifted=[[logs[i][j]+i*.4-j*.2 for j in range(n)] for i in range(n)]
  zs,_,ds=dp(shifted,scores);assert abs((zs-zz)-sum(i*.4-i*.2 for i in range(n)))<1e-12
  for u in (.11,.39,.87):assert ds(u)==draw(u)
 # Equal conditional laws give exactly zero normalized score, including row/column factors.
 p=[[math.log(.2),math.log(.8)],[math.log(.4),math.log(.6)]];m=[[p[i][j]+i-j for j in range(2)] for i in range(2)];t=[[m[i][j]-p[i][j] for j in range(2)] for i in range(2)]
 zp,mean,_=dp(p,t);zm,_,_=dp(m,t)
 assert abs(sum(t[i][i] for i in range(2))-(zm-zp))<1e-12 and abs(mean-(zm-zp))<1e-12
 p=[[math.log(.5)]*2 for _ in range(2)];m=[[math.log(.8),math.log(.2)],[math.log(.2),math.log(.8)]];t=[[m[i][j]-p[i][j] for j in range(2)] for i in range(2)]
 zp,mu,_=dp(p,t);zm,_,_=dp(m,t);r=sum(t[i][i] for i in range(2))-(zm-zp)
 assert abs(r-math.log((.64/.68)/.5))<1e-12 and mu-(zm-zp)<0
 return {'complete_enumeration_fixtures':3,'cdf_checks':15,'row_column_checks':9,'identical_conditional_law':'PASS','duplicate_labeled_donors':'PASS','known_nonnull_conditional_ratio':'PASS'}

def same(a,b,path='root'):
 if isinstance(a,dict):
  assert isinstance(b,dict) and a.keys()==b.keys(),(path,'keys')
  for k in a:same(a[k],b[k],path+'.'+str(k))
 elif isinstance(a,list):
  assert isinstance(b,list) and len(a)==len(b),(path,'length')
  for i,(x,y) in enumerate(zip(a,b)):same(x,y,path+f'[{i}]')
 elif isinstance(a,float):assert isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9),(path,a,b)
 else:assert a==b,(path,a,b)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');args=ap.parse_args();checks=controls()
 if args.controls_only:print(json.dumps(checks));return
 lock=read(B/'src/REGISTRATION_LOCK.json')
 for path,h in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 old=read(ROOT/(OLD+'gdt1374_class_stream_partner_exchange/artifacts/POOLS.json.gz'))
 model=read(ROOT/(OLD+'gdt1308_whole_form_prediction/artifacts/MODEL.json'))
 prior=read(ROOT/(OLD+'gdt1279_strict_inner_symbol_prediction/artifacts/MODEL.json'))
 result={};outpools={};maxcancel=0.
 for rd,pools in old.items():
  table={tuple(r['context']):r['counts'] for r in model[rd]['m1']};whole={tuple(r['cell']):{tuple(x['units']):x['count'] for x in r['counts']} for r in model[rd]['whole']};previous={tuple(r['context']):r['counts'] for r in prior['tables'][rd]['EXACT']}
  records=[];models=[];allleaf={};prileaf={};oldn=large=0
  for idx,pool in enumerate(pools):
   if not pool['mobile']:continue
   oldn+=1;n=len(pool['rows']);leaf=pool['leaf'];assert n>=2
   if n>8:
    large+=1;records.append({'original_pool_index':idx,'N':n,'leaf':leaf,'status':'COMPUTATION_CAP'});continue
   lp=[];lm=[];c=pool['currier'];freq=whole.get((c,len(pool['mask'])),{});total=sum(freq.values())
   for a in pool['rows']:
    prow=[];mrow=[]
    for b in pool['rows']:
     u=weave(pool['mask'],a['s0'],b['s1']);assert u[0]==pool['first'] and u[-1]==pool['last'];terms=[]
     for k,x in enumerate(u):
      key=(c,len(u),k,u[k-1] if k else '^');counts=table.get(key,{})
      if k:assert counts==previous.get(key,{})
      terms.append(math.log((counts.get(x,0)+.5)/(sum(counts.values())+11)))
     p=math.fsum(terms);q=freq.get(tuple(u),0)/total if total else 0.
     m=(logadd(p,math.log(q))-math.log(2)) if q else (p-math.log(2) if total else p)
     prow.append(p);mrow.append(m)
    lp.append(prow);lm.append(mrow)
   for i in range(n):
    for j in range(n):
     d=(lp[i][j]-pool['costs'][i][j])+(lp[0][0]-pool['costs'][0][0])-(lp[i][0]-pool['costs'][i][0])-(lp[0][j]-pool['costs'][0][j]);maxcancel=max(maxcancel,abs(d));assert abs(d)<1e-9
   t=[[lm[i][j]-lp[i][j] for j in range(n)] for i in range(n)];zp,mean,draw=dp(lp,t);zm,_,_=dp(lm,t);constant=zm-zp
   observed=math.fsum(t[i][i] for i in range(n))-constant;nullmean=mean-constant;assert nullmean<=1e-9
   witness=rect(t);mobile=witness is not None
   records.append({'original_pool_index':idx,'N':n,'leaf':leaf,'status':'COMPUTABLE','logP':lp,'logM':lm,'logZP':zp,'logZM':zm,'observed_R':observed,'null_mean_R':nullmean,'mobile':mobile,'rectangle':witness})
   bucket=allleaf.setdefault(leaf,[0,0.]);bucket[0]+=n;bucket[1]+=observed
   if mobile:
    bucket=prileaf.setdefault(leaf,[0,0.]);bucket[0]+=n;bucket[1]+=observed;models.append((leaf,n,t,constant,draw))
  perleaf={str(l):{'words':v[0],'gain':v[1]/v[0]} for l,v in sorted(prileaf.items())};words=sum(x[0] for x in prileaf.values());nleaves=len(prileaf);mean=math.fsum(v['gain'] for v in perleaf.values())/nleaves if nleaves else None;pos=sum(v['gain']>0 for v in perleaf.values());nulls=[];pval=None;status='NO_CAPACITY'
  if words>=100 and nleaves>=10:
   rng=random.Random(1375)
   for _ in range(199):
    vals={l:0. for l in prileaf}
    for leaf,n,t,constant,draw in models:
     assignment=draw(rng.random());vals[leaf]+=math.fsum(t[i][j] for i,j in enumerate(assignment))-constant
    nulls.append(math.fsum(vals[l]/v[0] for l,v in sorted(prileaf.items()))/nleaves)
   if max(nulls)-min(nulls)<=1e-12:status='NO_SCORE_MOBILITY'
   else:
    pval=(1+sum(x>=mean-1e-12 for x in nulls))/200
    status='CONDITIONAL_WHOLE_FORM_INCREMENT' if mean>=.01 and pos*3>=2*nleaves and pval<=.05/3 else 'NO_RETAINED_CONDITIONAL_WHOLE_GAIN'
  result[rd]={'original_mobile_pools':oldn,'excluded_large_pools':large,'computable_pools':len(records)-large,'residual_mobile_pools':len(models),'primary_words':words,'primary_leaves':nleaves,'positive_leaves':pos,'mean_gain':mean,'per_leaf':perleaf,'all_computable_words':sum(v[0] for v in allleaf.values()),'all_computable_leaves':len(allleaf),'all_computable_mean_gain':math.fsum(v[1]/v[0] for v in allleaf.values())/len(allleaf) if allleaf else None,'null_scores':nulls,'p_or_null':pval,'status':status};outpools[rd]=records
 same(outpools,read(B/'artifacts/POOLS.json.gz'),'pools');same({'status':'LOCAL_WEIGHTED_PARTNER_RESIDUAL','readers':result},read(B/'artifacts/RESULT.json'),'result')
 receipt={'status':'PASS','controls':checks,'maximum_full_inner_cancellation_rectangle':maxcancel,'readers':{r:{'computable_pools':v['computable_pools'],'status':v['status']} for r,v in result.items()},'method':'Independent subset DP partitions and score moments; prefix-CDF sampling from one uniform; no primary imports.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

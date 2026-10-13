from pathlib import Path
from collections import defaultdict
from itertools import permutations,accumulate
from bisect import bisect_left
import gzip,hashlib,json,math,random
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def logsum(v):
 top=max(v);ws=[math.exp(x-top) for x in v];assert all(w>0 for w in ws);return top+math.log(math.fsum(ws)),ws

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 old=read(R/'experiments/yolo/gdt1374_class_stream_partner_exchange/artifacts/POOLS.json.gz');m=read(R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts/MODEL.json');local=read(R/'experiments/yolo/gdt1279_strict_inner_symbol_prediction/artifacts/MODEL.json');result={};out={}
 for rd,pools in sorted(old.items()):
  table={tuple(x['context']):x['counts'] for x in m[rd]['m1']};exact={tuple(x['context']):x['counts'] for x in local['tables'][rd]['EXACT']};whole={tuple(x['cell']):{tuple(z['units']):z['count'] for z in x['counts']} for x in m[rd]['whole']};saved=[];distributions=[];original=excluded=0
  for pi,p in enumerate(pools):
   if not p['mobile']:continue
   original+=1;N=len(p['rows']);base={'original_pool_index':pi,'N':N,'leaf':p['leaf']}
   if N>8:saved.append({**base,'status':'COMPUTATION_CAP'});excluded+=1;continue
   assert N>=2 and p['leaf']%2==0 and not p['page'].startswith('f84') and p['page'] not in ('f1r','f116v');mask=p['mask'];c=p['currier'];n=len(mask);qs=whole.get((c,n),{});qt=sum(qs.values());lp=[];lm=[]
   for i,a in enumerate(p['rows']):
    rp=[];rm=[]
    for j,b in enumerate(p['rows']):
     s0=iter(a['s0']);s1=iter(b['s1']);u=tuple(next(s1) if bit else next(s0) for bit in mask);assert u[0]==p['first'] and u[-1]==p['last']
     if i==j:assert list(u)==a['source']['units'] and ''.join(u)==a['source']['ivtff_group_raw']
     factors=[]
     for k,s in enumerate(u):
      ctx=(c,n,k,u[k-1] if k else '^');ct=table.get(ctx,{})
      if k:assert ct==exact.get(ctx,{}),(rd,ctx)
      factors.append(math.log((ct.get(s,0)+.5)/(sum(ct.values())+11)))
     logp=math.fsum(factors);q=qs.get(u,0)/qt if qt else 0;logm=math.log((math.exp(logp)+q)/2) if qt else logp;rp.append(logp);rm.append(logm)
    lp.append(rp);lm.append(rm)
   delta=[[lp[i][j]-p['costs'][i][j] for j in range(N)] for i in range(N)]
   assert all(abs(delta[i][j]+delta[0][0]-delta[i][0]-delta[0][j])<1e-10 for i in range(N) for j in range(N))
   t=[[lm[i][j]-lp[i][j] for j in range(N)] for i in range(N)];rect=None
   for i in range(1,N):
    for j in range(1,N):
     v=t[i][j]+t[0][0]-t[i][0]-t[0][j]
     if abs(v)>1e-12:rect={'i':i,'j':j,'value':v};break
    if rect is not None:break
   pp=[];mm=[]
   for perm in permutations(range(N)):
    pp.append(math.fsum(lp[i][j] for i,j in enumerate(perm)));mm.append(math.fsum(lm[i][j] for i,j in enumerate(perm)))
   zp,weights=logsum(pp);zm,_=logsum(mm);rs=[b-a-(zm-zp) for a,b in zip(pp,mm)];norm=math.fsum(weights);mean=math.fsum(w*s for w,s in zip(weights,rs))/norm;assert mean<=1e-9;obs=math.fsum(t[i][i] for i in range(N))-(zm-zp)
   saved.append({**base,'status':'COMPUTABLE','logP':lp,'logM':lm,'logZP':zp,'logZM':zm,'observed_R':obs,'null_mean_R':mean,'mobile':rect is not None,'rectangle':rect})
   if rect is not None:distributions.append((p['leaf'],N,obs,list(accumulate(weights)),norm,rs))
  allstats=defaultdict(lambda:[0,[]]);stats=defaultdict(lambda:[0,[]])
  for p in saved:
   if p['status']!='COMPUTABLE':continue
   for st in ([allstats,stats] if p['mobile'] else [allstats]):z=st[p['leaf']];z[0]+=p['N'];z[1].append(p['observed_R'])
  per={str(l):{'words':v[0],'gain':math.fsum(v[1])/v[0]} for l,v in sorted(stats.items())};L=len(per);W=sum(v['words'] for v in per.values());gain=math.fsum(v['gain'] for v in per.values())/L if L else None;positive=sum(v['gain']>0 for v in per.values());capacity=W>=100 and L>=10;null=[];rng=random.Random(1375)
  if capacity:
   for rep in range(199):
    sums=defaultdict(list)
    for leaf,N,obs,cdf,norm,rs in distributions:
     u=rng.random()*norm;j=bisect_left(cdf,u);assert j<len(rs);sums[leaf].append(rs[j])
    null.append(math.fsum(math.fsum(sums[l])/v[0] for l,v in sorted(stats.items()))/L)
  mobile=bool(null) and max(null)-min(null)>1e-12;pv=(1+sum(v>=gain-1e-12 for v in null))/200 if mobile else None;material=gain is not None and gain>=.01 and positive*3>=2*L;status='NO_CAPACITY' if not capacity else 'NO_SCORE_MOBILITY' if not mobile else 'CONDITIONAL_WHOLE_FORM_INCREMENT' if material and pv<=.05/3 else 'NO_RETAINED_CONDITIONAL_WHOLE_GAIN'
  result[rd]={'original_mobile_pools':original,'excluded_large_pools':excluded,'computable_pools':len(saved)-excluded,'residual_mobile_pools':len(distributions),'primary_words':W,'primary_leaves':L,'positive_leaves':positive,'mean_gain':gain,'per_leaf':per,'all_computable_words':sum(v[0] for v in allstats.values()),'all_computable_leaves':len(allstats),'all_computable_mean_gain':math.fsum(math.fsum(v[1])/v[0] for v in allstats.values())/len(allstats) if allstats else None,'null_scores':null,'p_or_null':pv,'status':status};out[rd]=saved
  print(rd,status,'pools',len(distributions),'words',W,'leaves',L,'positive',positive,'gain',gain,'p',pv,'excludedlarge',excluded,flush=True)
 save('POOLS.json.gz',out);save('RESULT.json',{'status':'LOCAL_WEIGHTED_PARTNER_RESIDUAL','readers':result})
if __name__=='__main__':main()

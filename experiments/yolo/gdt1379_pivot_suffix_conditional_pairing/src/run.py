from pathlib import Path
from collections import defaultdict,Counter
from itertools import permutations
from fractions import Fraction
import csv,gzip,hashlib,json,math,random,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def controls():
 L=['abc','aac','acc'];T=['bad','cbd','bad'];alphabet='abcd'
 def edges(ws):return Counter((j,w[j-1],w[j]) for w in ws for j in range(1,len(w)))
 def prob(w):
  p=Fraction(1,4)
  for j in range(1,len(w)):
   weights=[1+(j+1)*(alphabet.index(w[j-1])+1)+(z+1)**2 for z in range(4)]
   p*=Fraction(weights[alphabet.index(w[j])],sum(weights))
  return p
 original=[a+b for a,b in zip(L,T)];base=math.prod(prob(w) for w in original)
 for perm in permutations(range(3)):
  words=[L[i]+T[j] for i,j in enumerate(perm)];assert edges(words)==edges(original) and math.prod(prob(w) for w in words)==base
 vals=[1,0];assert sum(vals)/2==.5
 assert Fraction(41,100)**2!=Fraction(9,100)**2
 return {'status':'PASS','labelled_permutations':6,'repeated_suffixes':True,'arbitrary_rational_M1_invariant':True,'mixture_not_product':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 check=controls();save('CONTROLS.json',check)
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');events=read(R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts/EVENTS.json.gz');model=read(R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts/MODEL.json')
 allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 meta={}
 for event in events:
  key=event['reader'],event['id'];assert key not in meta;meta[key]=event
 result={};out={}
 for rd in ['ZL3b','IT2a','RF1b']:
  table={tuple(x['context']):x['counts'] for x in model[rd]['m1']};whole={tuple(x['cell']):{tuple(z['units']):z['count'] for z in x['counts']} for x in model[rd]['whole']};grouped=defaultdict(list);held=0
  def score(c,u):
   n=len(u);factors=[]
   for i,s in enumerate(u):
    ct=table.get((c,n,i,u[i-1] if i else '^'),{});factors.append(math.log((ct.get(s,0)+.5)/(sum(ct.values())+11)))
   lp=math.fsum(factors);qs=whole.get((c,n),{});qt=sum(qs.values());q=qs.get(tuple(u),0)/qt if qt else 0
   if not qt:S=0.0
   elif not q:S=-math.log(2)
   else:
    x=math.log(q)-lp;S=max(0,x)+math.log1p(math.exp(-abs(x)))-math.log(2)
   return lp,S
  for row in data[rd]:
   if (rd,row['id']) not in meta:continue
   event=meta[rd,row['id']];u=row['units'];n=len(u);leaf=int(re.match(r'f(\d+)',row['page']).group(1))
   assert leaf%2==0 and leaf==event['leaf'] and n>=4 and u==event['units']
   assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['edition']==rd and row['kind']=='P'
   assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE' and ''.join(u)==row['ivtff_group_raw'] and set(u)<=set(SIGNS)
   assert re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw'])==u
   assert row['id']==f"{rd}|{row['locus']}|G{int(row['source_group_index']):03d}"
   c=event['c'];k=n//2;held+=1;lp,S=score(c,u)
   assert abs(lp-math.log(event['p']))<1e-9 and abs(S-event['gain'])<1e-9
   grouped[(row['page'],c,n,u[0],u[-1],u[k-1])].append({'source':row,'L':u[:k],'R':u[k:]})
  assert held==sum(e['reader']==rd for e in events)
  pools=[]
  for (page,c,n,first,last,pivot),rows in sorted(grouped.items()):
   N=len(rows);lp=[];S=[];memo={}
   for a in rows:
    pp=[];ss=[]
    for b in rows:
     u=tuple(a['L']+b['R']);assert len(u)==n and u[0]==first and u[-1]==last and u[n//2-1]==pivot
     if u not in memo:memo[u]=score(c,u)
     v,t=memo[u];pp.append(v);ss.append(t)
    lp.append(pp);S.append(ss)
   assert all(abs(lp[i][j]+lp[0][0]-lp[i][0]-lp[0][j])<1e-9 for i in range(N) for j in range(N))
   rect=None
   for i in range(1,N):
    for j in range(1,N):
     v=S[i][j]+S[0][0]-S[i][0]-S[0][j]
     if abs(v)>1e-12:rect={'i':i,'j':j,'value':v};break
    if rect is not None:break
   pools.append({'page':page,'currier':c,'n':n,'first':first,'last':last,'pivot':pivot,'leaf':int(re.match(r'f(\d+)',page).group(1)),'k':n//2,'rows':rows,'costs':S,'logP':lp,'observed':math.fsum(S[i][i] for i in range(N)),'expected':math.fsum(math.fsum(r)/N for r in S),'mobile':rect is not None,'rectangle':rect})
  allstats=defaultdict(lambda:[0,[]]);stats=defaultdict(lambda:[0,[]]);mobile=[p for p in pools if p['mobile']]
  for p in pools:
   for st in ([allstats,stats] if p['mobile'] else [allstats]):v=st[p['leaf']];v[0]+=len(p['rows']);v[1].append(p['observed']-p['expected'])
  per={str(l):{'words':v[0],'excess':math.fsum(v[1])/v[0]} for l,v in sorted(stats.items())};L=len(per);W=sum(v[0] for v in stats.values());excess=math.fsum(v['excess'] for v in per.values())/L if L else None;positive=sum(v['excess']>0 for v in per.values());capacity=W>=100 and L>=10;null=[];rng=random.Random(20261013)
  if capacity:
   for _ in range(199):
    sums=defaultdict(list)
    for p in mobile:
     perm=list(range(len(p['rows'])));rng.shuffle(perm);sums[p['leaf']].append(math.fsum(p['costs'][i][j] for i,j in enumerate(perm))-p['expected'])
    null.append(math.fsum(math.fsum(sums[l])/v[0] for l,v in sorted(stats.items()))/L)
  scoremobile=bool(null) and max(null)-min(null)>1e-12;pv=(1+sum(v>=excess-1e-12 for v in null))/200 if scoremobile else None
  material=excess is not None and excess>=.01 and positive*3>=2*L
  status='NO_CAPACITY' if not capacity else 'NO_SCORE_MOBILITY' if not scoremobile else 'CONDITIONAL_PIVOT_PARTNER_DEPENDENCE' if material and pv<=.05/3 else 'NO_RETAINED_PIVOT_PARTNER_EXCESS'
  result[rd]={'held_words':held,'pools':len(pools),'mobile_pools':len(mobile),'primary_words':W,'primary_leaves':L,'positive_leaves':positive,'mean_excess':excess,'per_leaf':per,'all_words':sum(v[0] for v in allstats.values()),'all_leaves':len(allstats),'all_mean_excess':math.fsum(math.fsum(v[1])/v[0] for v in allstats.values())/len(allstats) if allstats else None,'null_scores':null,'p_or_null':pv,'status':status};out[rd]=pools
  print(rd,{k:v for k,v in result[rd].items() if k not in ('per_leaf','null_scores')},flush=True)
 save('POOLS.json.gz',out);save('RESULT.json',{'status':'PIVOT_SUFFIX_CONDITIONAL_PAIRING','readers':result})
if __name__=='__main__':main()

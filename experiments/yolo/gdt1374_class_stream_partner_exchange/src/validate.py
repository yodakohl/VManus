#!/usr/bin/env python3
"""Independent reconstruction. No primary imports; controls run without native data."""
import argparse, collections, csv, gzip, hashlib, itertools, json, math, random, re
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
BASE='experiments/yolo/'
CACHE=BASE+'gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
LABELS=BASE+'gdt1264_interior_binary_alternation/artifacts/TRAIN.json'
OLD=BASE+'gdt1279_strict_inner_symbol_prediction/artifacts/'
ALLOW=BASE+'gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'

def read(p):
 p=Path(p);b=p.read_bytes()
 return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def weave(mask,a,b):
 pos=[0,0];streams=[a,b];out=[]
 for label in mask:
  out.append(streams[label][pos[label]]);pos[label]+=1
 assert pos==[len(a),len(b)]
 return out

def geometry(matrix):
 size=len(matrix)
 actual=math.fsum(matrix[i][i] for i in range(size))
 mean=math.fsum(math.fsum(row)/size for row in matrix)
 witness=None
 for i in range(size):
  for j in range(size):
   d=matrix[i][j]+matrix[0][0]-matrix[i][0]-matrix[0][j]
   if abs(d)>1e-12:
    witness={'i':i,'j':j,'value':d};break
  if witness is not None:break
 return actual,mean,witness

def controls():
 for mat in ([[1.,2.],[3.,4.]],[[0.,1.],[1.,0.]],[[2.,-1.,3.],[0.,5.,1.],[7.,-2.,4.]],[[9.]]):
  values=[math.fsum(mat[i][j] for i,j in enumerate(p)) for p in itertools.permutations(range(len(mat)))]
  _,mean,witness=geometry(mat)
  assert abs(mean-math.fsum(values)/len(values))<1e-12
  assert (witness is not None)==(max(values)-min(values)>1e-12)
 mask=[0,1,0,1,0];aa=[['a','b','z'],['a','c','z'],['a','d','z']];bb=[['x','y'],['w','x'],['y','w']]
 orig=[weave(mask,a,b) for a,b in zip(aa,bb)]
 margins=[collections.Counter(w[k] for w in orig) for k in range(len(mask))]
 for p in itertools.permutations(range(3)):
  out=[weave(mask,aa[i],bb[j]) for i,j in enumerate(p)]
  assert [collections.Counter(w[k] for w in out) for k in range(len(mask))]==margins
  assert all(w[0]=='a' and w[-1]=='z' for w in out)
  for i,j in enumerate(p):
   assert out[i]==weave([1-x for x in mask],bb[j],aa[i])
   assert [out[i][k] for k,x in enumerate(mask) if x==0]==aa[i]
   assert [out[i][k] for k,x in enumerate(mask) if x==1]==bb[j]
 return {'matrix_enumerations':4,'weave_permutations':6,'mean_mobility_endpoint_marginal_label_swap':'PASS'}

def close(a,b,path='root'):
 if isinstance(a,dict):
  assert isinstance(b,dict) and a.keys()==b.keys(),(path,'keys',a.keys(),getattr(b,'keys',lambda:[])())
  for k in a:close(a[k],b[k],path+'.'+str(k))
 elif isinstance(a,list):
  assert isinstance(b,list) and len(a)==len(b),(path,'length')
  for i,(x,y) in enumerate(zip(a,b)):close(x,y,path+f'[{i}]')
 elif isinstance(a,float):
  assert isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(path,a,b)
 else:assert a==b,(path,a,b)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--controls-only',action='store_true');args=parser.parse_args()
 checks=controls()
 if args.controls_only:
  print(json.dumps(checks));return
 lock=read(HERE/'src/REGISTRATION_LOCK.json')
 for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 data=read(ROOT/CACHE);labels=read(ROOT/LABELS)['labels'];model=read(ROOT/(OLD+'MODEL.json'));events=read(ROOT/(OLD+'EVENTS.json.gz'))
 assert 'm' not in labels and set(labels.values())=={0,1}
 allowed={row['page'] for row in csv.DictReader((ROOT/ALLOW).open(),delimiter='\t')}
 source={(rd,w['id']):w for rd,rows in data.items() for w in rows}
 meta={};seen=set()
 for ev in events:
  key=(ev['reader'],ev['id']);w=source[key];units=w['units'];i=ev['i'];assert 1<=i<len(units)
  assert (key,i) not in seen;seen.add((key,i))
  assert ev['region']==('EDGE' if i in (1,len(units)-1) else 'INNER')
  if 'status' in ev:
   assert ev['status']=='UNKNOWN_PREVIOUS_CLASS' and units[i-1] not in labels;continue
  assert ev['previous']==units[i-1] and ev['next']==units[i] and ev['n']==len(units)
  assert ev['leaf']==int(re.match(r'f(\d+)',w['page'])[1])
  if key in meta:assert meta[key]==ev['currier']
  meta[key]=ev['currier']
 allpools={};summaries={}
 for rd,rows in data.items():
  table={tuple(x['context']):x['counts'] for x in model['tables'][rd]['EXACT']}
  def score(units,c,indices):
   vals=[]
   for i in indices:
    cnt=table.get((c,len(units),i,units[i-1]),{})
    vals.append(math.log((cnt.get(units[i],0)+.5)/(math.fsum(cnt.values())+11)))
   return math.fsum(vals)
  grouped=collections.defaultdict(list);nheld=nunknown=nempty=0
  for w in rows:
   assert w['page'] in allowed and not w['page'].startswith('f84') and w['page'] not in ('f1r','f116v')
   assert w['kind']=='P' and w['left_separator']==w['right_separator']=='DEFINITE_SPACE'
   leaf=int(re.match(r'f(\d+)',w['page'])[1]);u=w['units']
   if leaf%2 or len(u)<4:continue
   nheld+=1;key=(rd,w['id'])
   assert all((key,i) in seen for i in range(1,len(u)))
   if not all(x in labels for x in u):nunknown+=1;continue
   mask=tuple(labels[x] for x in u)
   inds=[i for i in range(2,len(u)-1) if mask[i-1]!=mask[i]]
   if not inds:nempty+=1;continue
   c=meta[key]
   grouped[(w['page'],c,mask,u[0],u[-1])].append({'source':w,'s0':[u[i] for i,x in enumerate(mask) if x==0],'s1':[u[i] for i,x in enumerate(mask) if x==1]})
  pools=[];leafall=collections.defaultdict(lambda:[0,0.,0.]);leafmobile=collections.defaultdict(lambda:[0,0.,0.])
  for (page,c,mask,first,last),members in sorted(grouped.items()):
   inds=[i for i in range(2,len(mask)-1) if mask[i-1]!=mask[i]]
   costs=[]
   for a in members:
    row=[]
    for b in members:
     woven=weave(mask,a['s0'],b['s1']);assert woven[0]==first and woven[-1]==last
     row.append(score(woven,c,inds))
    costs.append(row)
   observed,expected,rect=geometry(costs);leaf=int(re.match(r'f(\d+)',page)[1]);mobile=rect is not None
   pool={'page':page,'currier':c,'mask':list(mask),'first':first,'last':last,'leaf':leaf,'inner_indices':inds,'rows':members,'costs':costs,'observed':observed,'expected':expected,'mobile':mobile,'rectangle':rect};pools.append(pool)
   edges=len(members)*len(inds)
   for bucket in ([leafall,leafmobile] if mobile else [leafall]):
    bucket[leaf][0]+=edges;bucket[leaf][1]+=observed;bucket[leaf][2]+=expected
  perleaf={str(l):{'edges':x[0],'observed':x[1]/x[0],'expected':x[2]/x[0],'excess':(x[1]-x[2])/x[0]} for l,x in sorted(leafmobile.items())}
  def mean(field):return math.fsum(v[field] for v in perleaf.values())/len(perleaf) if perleaf else None
  mobile=[p for p in pools if p['mobile']];edges=sum(x[0] for x in leafmobile.values());cap=edges>=100 and len(perleaf)>=10
  nulls=[];pval=None;status='NO_CAPACITY'
  if cap:
   rng=random.Random(1374)
   for _ in range(199):
    totals=collections.defaultdict(float)
    for pool in mobile:
     order=list(range(len(pool['rows'])));rng.shuffle(order)
     totals[pool['leaf']]+=math.fsum(pool['costs'][i][j] for i,j in enumerate(order))-pool['expected']
    nulls.append(math.fsum(totals[l]/x[0] for l,x in sorted(leafmobile.items()))/len(leafmobile))
   pval=(1+sum(x>=mean('excess')-1e-12 for x in nulls))/200
   if max(nulls)-min(nulls)<=1e-12:status='NO_SCORE_MOBILITY';pval=None
   else:status='CONDITIONAL_PARTNER_COUPLING' if mean('excess')>=.01 and sum(v['excess']>0 for v in perleaf.values())*3>=2*len(perleaf) and pval<=.05/3 else 'NO_RETAINED_PARTNER_EXCESS'
  summaries[rd]={'held_n4_words':nheld,'excluded_unclassified':nunknown,'excluded_no_cross':nempty,'pooled_words':sum(len(p['rows']) for p in pools),'pools':len(pools),'mobile_pools':len(mobile),'mobile_words':sum(len(p['rows']) for p in mobile),'mobile_edges':edges,'mobile_leaves':len(perleaf),'observed_mean':mean('observed'),'expected_mean':mean('expected'),'excess_mean':mean('excess'),'positive_leaves':sum(v['excess']>0 for v in perleaf.values()),'per_leaf':perleaf,'all_edges':sum(x[0] for x in leafall.values()),'all_leaves':len(leafall),'all_excess_mean':math.fsum((x[1]-x[2])/x[0] for x in leafall.values())/len(leafall) if leafall else None,'null_excess':nulls,'p_or_null':pval,'status':status}
  allpools[rd]=pools
 close(allpools,read(HERE/'artifacts/POOLS.json.gz'),'pools')
 close({'status':'CLASS_STREAM_PARTNER_EXCHANGE','readers':summaries},read(HERE/'artifacts/RESULT.json'),'result')
 receipt={'status':'PASS','controls':checks,'source_events':len(events),'readers':{r:{'pools':len(allpools[r]),'status':x['status']} for r,x in summaries.items()},'method':'Independent full explicit weave, frozen count log probabilities, exact assignment expectations and reconstructed 199 permutations; no primary imports.'}
 (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

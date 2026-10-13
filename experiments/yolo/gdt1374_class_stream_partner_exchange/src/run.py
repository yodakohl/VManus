from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,json,math,random,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');labels=read(R/'experiments/yolo/gdt1264_interior_binary_alternation/artifacts/TRAIN.json')['labels'];model=read(R/'experiments/yolo/gdt1279_strict_inner_symbol_prediction/artifacts/MODEL.json');events=read(R/'experiments/yolo/gdt1279_strict_inner_symbol_prediction/artifacts/EVENTS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};assert len(model['alphabet'])==22 and model['alpha']==.5 and set(labels.values())<={0,1}
 source={(rd,row['id']):row for rd,rows in data.items() for row in rows};meta={}
 for e in events:
  row=source[e['reader'],e['id']];u=row['units'];i=e['i'];assert len(u)>=4 and int(re.match(r'f(\d+)',row['page']).group(1))%2==0
  if e.get('status')=='UNKNOWN_PREVIOUS_CLASS':assert u[i-1] not in labels;continue
  assert len(u)==e['n'] and u[i-1]==e['previous'] and u[i]==e['next'];key=(e['reader'],e['id']);value=(e['currier'],e['leaf'])
  if key in meta:assert meta[key]==value
  meta[key]=value
 results={};allpools={}
 for rd,rows in sorted(data.items()):
  table={tuple(z['context']):z['counts'] for z in model['tables'][rd]['EXACT']};grouped=defaultdict(list);held=unknown=nocross=0
  for row in rows:
   assert row['edition']==rd and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   u=row['units'];raw=row['ivtff_group_raw'];assert re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',raw)==u and ''.join(u)==raw
   assert row['id']==f"{rd}|{row['locus']}|G{int(row['source_group_index']):03d}";leaf=int(re.match(r'f(\d+)',row['page']).group(1))
   if leaf%2 or len(u)<4:continue
   held+=1
   if any(s not in labels for s in u):unknown+=1;continue
   c,ml=meta[rd,row['id']];assert ml==leaf;mask=tuple(labels[s] for s in u);ix=[i for i in range(2,len(u)-1) if mask[i-1]!=mask[i]]
   if not ix:nocross+=1;continue
   grouped[(row['page'],c,mask,u[0],u[-1])].append({'source':row,'s0':[s for s in u if labels[s]==0],'s1':[s for s in u if labels[s]==1]})
  pools=[]
  for (page,c,mask,first,last),members in sorted(grouped.items()):
   ix=[i for i in range(2,len(mask)-1) if mask[i-1]!=mask[i]];N=len(members);costs=[];memo={}
   for a in members:
    rowcost=[]
    for b in members:
     cachekey=(tuple(a['s0']),tuple(b['s1']))
     if cachekey not in memo:
      s0=iter(a['s0']);s1=iter(b['s1']);word=[next(s1) if z else next(s0) for z in mask];assert word[0]==first and word[-1]==last
      values=[]
      for i in ix:
       ct=table.get((c,len(mask),i,word[i-1]),{});values.append(math.log((ct.get(word[i],0)+.5)/(sum(ct.values())+11)))
      memo[cachekey]=math.fsum(values)
     rowcost.append(memo[cachekey])
    costs.append(rowcost)
   rect=None
   for i in range(1,N):
    for j in range(1,N):
     v=costs[i][j]+costs[0][0]-costs[i][0]-costs[0][j]
     if abs(v)>1e-12:rect={'i':i,'j':j,'value':v};break
    if rect is not None:break
   obs=math.fsum(costs[i][i] for i in range(N));expected=math.fsum(math.fsum(v)/N for v in costs);leaf=int(re.match(r'f(\d+)',page).group(1))
   pools.append({'page':page,'currier':c,'mask':list(mask),'first':first,'last':last,'leaf':leaf,'inner_indices':ix,'rows':members,'costs':costs,'observed':obs,'expected':expected,'mobile':rect is not None,'rectangle':rect})
  allstats=defaultdict(lambda:[0,[],[]]);stats=defaultdict(lambda:[0,[],[]]);mobile=[p for p in pools if p['mobile']]
  for p in pools:
   for st in ([allstats,stats] if p['mobile'] else [allstats]):
    z=st[p['leaf']];z[0]+=len(p['rows'])*len(p['inner_indices']);z[1].append(p['observed']);z[2].append(p['expected'])
  per={str(l):{'edges':v[0],'observed':math.fsum(v[1])/v[0],'expected':math.fsum(v[2])/v[0],'excess':(math.fsum(v[1])-math.fsum(v[2]))/v[0]} for l,v in sorted(stats.items())};nleaf=len(per);nedges=sum(v['edges'] for v in per.values());obsmean=math.fsum(v['observed'] for v in per.values())/nleaf if nleaf else None;expmean=math.fsum(v['expected'] for v in per.values())/nleaf if nleaf else None;excess=math.fsum(v['excess'] for v in per.values())/nleaf if nleaf else None;positive=sum(v['excess']>0 for v in per.values());capacity=nedges>=100 and nleaf>=10
  null=[];rng=random.Random(1374)
  if capacity:
   for rep in range(199):
    score=defaultdict(list)
    for p in mobile:
     perm=list(range(len(p['rows'])));rng.shuffle(perm);score[p['leaf']].append(math.fsum(p['costs'][i][j] for i,j in enumerate(perm)))
    null.append(math.fsum((math.fsum(score[l])-math.fsum(v[2]))/v[0] for l,v in sorted(stats.items()))/nleaf)
  scoremobile=bool(null) and max(null)-min(null)>1e-12;pv=(1+sum(v>=excess-1e-12 for v in null))/200 if scoremobile else None;material=excess is not None and excess>=.01 and positive*3>=2*nleaf;status='NO_CAPACITY' if not capacity else 'NO_SCORE_MOBILITY' if not scoremobile else 'CONDITIONAL_PARTNER_COUPLING' if material and pv<=.05/3 else 'NO_RETAINED_PARTNER_EXCESS'
  results[rd]={'held_n4_words':held,'excluded_unclassified':unknown,'excluded_no_cross':nocross,'pooled_words':sum(len(p['rows']) for p in pools),'pools':len(pools),'mobile_pools':len(mobile),'mobile_words':sum(len(p['rows']) for p in mobile),'mobile_edges':nedges,'mobile_leaves':nleaf,'observed_mean':obsmean,'expected_mean':expmean,'excess_mean':excess,'positive_leaves':positive,'per_leaf':per,'all_edges':sum(v[0] for v in allstats.values()),'all_leaves':len(allstats),'all_excess_mean':math.fsum((math.fsum(v[1])-math.fsum(v[2]))/v[0] for v in allstats.values())/len(allstats) if allstats else None,'null_excess':null,'p_or_null':pv,'status':status};allpools[rd]=pools
  print(rd,status,'pools',len(mobile),'edges',nedges,'leaves',nleaf,'excess',excess,'positive',positive,'p',pv,flush=True)
 save('POOLS.json.gz',allpools);save('RESULT.json',{'status':'CLASS_STREAM_PARTNER_EXCHANGE','readers':results})
if __name__=='__main__':main()

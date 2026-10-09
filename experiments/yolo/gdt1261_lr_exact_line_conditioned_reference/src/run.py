import collections,gzip,hashlib,itertools,json,math,random,time
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
class CapacityStop(Exception):pass

def counted_dag(edges,target,s,budget):
 n=len(edges);nv=len(target);suffix=[[0]*nv for _ in range(n+1)]
 for i in range(n-1,-1,-1):
  suffix[i]=suffix[i+1][:]
  for v in edges[i]:suffix[i][v]+=1
 memo={};nodes=[]
 def visit(i,remaining):
  if any(x<0 or x>cap for x,cap in zip(remaining,suffix[i])):return -1
  key=(i,remaining)
  if key in memo:return memo[key]
  if len(nodes)>=s['max_states_per_component'] or budget['states']>=s['max_states_total'] or time.monotonic()-budget['start']>s['max_dp_seconds']:raise CapacityStop('fixed_DP_budget')
  ident=len(nodes);memo[key]=ident;nodes.append(None);budget['states']+=1
  if i==n:node={'i':i,'remaining':list(remaining),'count':1,'children':[]}
  else:
   children=[]
   for bit in [0,1]:
    rem=list(remaining)
    for v in edges[i]:rem[v]-=bit
    children.append(visit(i+1,tuple(rem)))
   node={'i':i,'remaining':list(remaining),'count':sum(nodes[j]['count'] for j in children if j>=0),'children':children}
  nodes[ident]=node;return ident
 root=visit(0,tuple(target));assert root>=0 and nodes[root]['count']>0
 return {'edges':edges,'target_r_degrees':target,'root':root,'nodes':nodes,'count':nodes[root]['count']}

def controls():
 checks=0;graphs=[[(0,2),(0,2)],[(0,2),(0,3),(1,2),(1,3)],[(0,3),(0,4),(1,4),(1,5),(2,5),(2,3)],[(0,2),(0,3),(1,2),(1,3),(0,2),(1,3)]]
 spec={'max_states_per_component':100000,'max_states_total':1000000,'max_dp_seconds':180};budget={'states':0,'start':time.monotonic()}
 for edges in graphs:
  assignments=list(itertools.product([0,1],repeat=len(edges)));nv=max(max(e) for e in edges)+1
  def degrees(y):
   d=[0]*nv
   for bit,edge in zip(y,edges):
    for v in edge:d[v]+=bit
   return d
  for target in sorted({tuple(degrees(y)) for y in assignments}):
   dag=counted_dag(edges,list(target),spec,budget);expected=[y for y in assignments if degrees(y)==list(target)]
   assert dag['count']==len(expected)
   for y in expected:
    at=dag['root'];numerator=1;denominator=1
    for bit in y:
     node=dag['nodes'][at];child=node['children'][bit];assert child>=0;cc=dag['nodes'][child]['count'];numerator*=cc;denominator*=node['count'];at=child
    assert numerator*len(expected)==denominator
   checks+=1
 return checks

def main():
 s=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 P=R/s['parent'];tokens=json.loads((P/'artifacts/TOKENS.json').read_text())[s['reader']];pairs=json.loads((P/'artifacts/PAIRS.json').read_text())[s['reader']];nom=set(map(tuple,json.loads((R/s['nominees']).read_text())))
 assert all(not t['page'].startswith('f84') and t['page']!='f116v' for t in tokens)
 keys=[(('L',t['page'],t['locus']),('S',t['leaf'],t['stem'],t['position'])) for t in tokens];parent={}
 def find(x):
  parent.setdefault(x,x)
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for t,(a,b) in zip(tokens,keys):
  if t['mobile']:parent[find(a)]=find(b)
 groups=collections.defaultdict(list)
 for i,t in enumerate(tokens):
  if t['mobile']:groups[find(keys[i][0])].append(i)
 components=sorted(groups.values(),key=lambda g:min(g));base=[int(t['ending']=='r') for t in tokens];dags=[];budget={'states':0,'start':time.monotonic()}
 try:
  for indices in components:
   vertices=sorted({v for i in indices for v in keys[i]});vid={v:j for j,v in enumerate(vertices)};edges=[[vid[v] for v in keys[i]] for i in indices];target=[0]*len(vertices)
   for idx,edge in zip(indices,edges):
    for v in edge:target[v]+=base[idx]
   dag=counted_dag(edges,target,s,budget);dag.update({'token_indices':indices,'vertices':[list(v) for v in vertices]});dags.append(dag)
 except CapacityStop as error:
  out={'status':'COMPUTATIONAL_CAPACITY_STOP','reason':str(error),'completed_components':len(dags),'states_before_stop':budget['states'],'elapsed_dp_seconds':time.monotonic()-budget['start'],'worlds':0,'statistic_reported':False};(B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));return
 elapsed=time.monotonic()-budget['start'];den=collections.Counter(p['leaf'] for p in pairs);scale=math.lcm(*den.values());denominator=scale*len(den);npairs=[p for p in pairs if tuple(p['stems']) in nom]
 def score(y):return sum((1 if y[p['a']]==y[p['b']] else -1)*(scale//den[p['leaf']]) for p in npairs)
 observed=score(base);rng=random.Random(s['seed']);rows=[];packed=bytearray();width=(len(tokens)+7)//8
 for world in range(s['worlds']):
  y=base[:]
  for dag in dags:
   at=dag['root']
   for idx in dag['token_indices']:
    node=dag['nodes'][at];a,b=node['children'];z0=dag['nodes'][a]['count'] if a>=0 else 0;z=node['count'];draw=rng.randrange(z);bit=int(draw>=z0);at=[a,b][bit];assert at>=0 and dag['nodes'][at]['count']>0;y[idx]=bit
  value=score(y);rows.append(value);raw=bytearray(width)
  for i,bit in enumerate(y):raw[i//8]|=bit<<(i%8)
  packed.extend(raw)
 at_least=sum(v>=observed for v in rows);rank=(1+at_least)/(1+len(rows));mean=sum(rows)/len(rows)/denominator
 out={'status':'CONDITIONAL_ASSOCIATION_RETAINED' if rank<=.05 and observed/denominator>mean else 'STRONGER_CONDITIONAL_ASSOCIATION_NOT_ESTABLISHED','reader':s['reader'],'tokens':len(tokens),'mobile_tokens':sum(t['mobile'] for t in tokens),'components':len(dags),'dp_states':budget['states'],'max_component_states':max(len(d['nodes']) for d in dags),'max_component_tokens':max(len(d['token_indices']) for d in dags),'global_assignments':math.prod(d['count'] for d in dags),'dp_seconds':elapsed,'worlds':len(rows),'seed':s['seed'],'score_denominator':denominator,'observed_numerator':observed,'observed_T':observed/denominator,'null_numerator_sum':sum(rows),'mean_T':mean,'observed_minus_mean':observed/denominator-mean,'at_least_observed':at_least,'conditional_tail_rank':rank,'null_min_T':min(rows)/denominator,'null_max_T':max(rows)/denominator,'nominated_pairs':len(npairs),'eligible_pairs':len(pairs),'evaluation_leaves':len(den),'packed_world_width_bytes':width,'source_free_controls':controls(),'claim_ceiling':'Exactuniformfinite draws; MonteCarlo fixed-family conditional rank only, not exacttailprobability or projectwide/meaning confirmation;915/916unchanged.'}
 (B/'artifacts/COUNT_DAGS.json.gz').write_bytes(gzip.compress(json.dumps(dags,separators=(',',':')).encode(),mtime=0));(B/'artifacts/WORLD_LABELS.bin').write_bytes(bytes(packed));(B/'artifacts/WORLD_SCORES.json').write_text(json.dumps(rows)+'\n');(B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':
 import sys
 if '--controls' in sys.argv:print(controls())
 else:main()

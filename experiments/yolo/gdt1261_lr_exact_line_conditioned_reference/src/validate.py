import collections,gzip,hashlib,json,math,random
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());out=json.loads((B/'artifacts/RESULT.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 if out['status']=='COMPUTATIONAL_CAPACITY_STOP':
  assert out['worlds']==0 and not out['statistic_reported'] and not(B/'artifacts/WORLD_LABELS.bin').exists()
  val={'status':'PASS_STOP_ACCOUNT_ONLY','limits':'No statistical outcome or independent reproduction of wallclock-cap trigger.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(val);return
 P=R/s['parent'];tokens=json.loads((P/'artifacts/TOKENS.json').read_text())[s['reader']];pairs=json.loads((P/'artifacts/PAIRS.json').read_text())[s['reader']];nom=set(map(tuple,json.loads((R/s['nominees']).read_text())))
 assert all(not t['page'].startswith('f84') and t['page']!='f116v' for t in tokens)
 keys=[(('L',t['page'],t['locus']),('S',t['leaf'],t['stem'],t['position'])) for t in tokens];base=[int(t['ending']=='r') for t in tokens]
 dags=json.loads(gzip.decompress((B/'artifacts/COUNT_DAGS.json.gz').read_bytes()));seen=set();vertex_component={};totalstates=0;component_counts=[]
 assert [min(d['token_indices']) for d in dags]==sorted(min(d['token_indices']) for d in dags)
 for c,dag in enumerate(dags):
  ids=dag['token_indices'];assert ids==sorted(ids) and not(seen & set(ids));seen.update(ids);assert all(tokens[i]['mobile'] for i in ids)
  vertices=sorted({v for i in ids for v in keys[i]});assert dag['vertices']==[list(v) for v in vertices]
  for v in vertices:assert v not in vertex_component;vertex_component[v]=c
  edges=[[vertices.index(v) for v in keys[i]] for i in ids];assert edges==dag['edges']
  # Independent graph traversal establishes a connected mobile component.
  adjacent=collections.defaultdict(set)
  for a,b in edges:adjacent[a].add(b);adjacent[b].add(a)
  reached={0};todo=[0]
  while todo:
   for v in adjacent[todo.pop()]:
    if v not in reached:reached.add(v);todo.append(v)
  assert len(reached)==len(vertices)
  target=[sum(base[idx] for idx,e in zip(ids,edges) if v in e) for v in range(len(vertices))];assert target==dag['target_r_degrees']
  nodes=dag['nodes'];assert len(nodes)<=s['max_states_per_component'];totalstates+=len(nodes);assert totalstates<=s['max_states_total']
  assert len({(node['i'],tuple(node['remaining'])) for node in nodes})==len(nodes)
  degrees=[[sum(v in e for e in edges[i:]) for v in range(len(vertices))] for i in range(len(edges)+1)]
  for node in nodes:
   i=node['i'];rem=node['remaining'];assert len(rem)==len(vertices) and all(0<=r<=d for r,d in zip(rem,degrees[i]))
   if i==len(edges):assert rem==[0]*len(vertices) and node['count']==1 and not node['children'];continue
   assert len(node['children'])==2;count=0
   for bit,child in enumerate(node['children']):
    expected=rem[:]
    for v in edges[i]:expected[v]-=bit
    possible=all(0<=r<=d for r,d in zip(expected,degrees[i+1]))
    if not possible:assert child==-1
    else:
     assert 0<=child<len(nodes);ch=nodes[child];assert ch['i']==i+1 and ch['remaining']==expected;count+=ch['count']
   assert type(node['count']) is int and node['count']==count
  root=nodes[dag['root']];assert root['i']==0 and root['remaining']==target and root['count']==dag['count']>0
  reachable={dag['root']};todo=[dag['root']]
  while todo:
   for child in nodes[todo.pop()]['children']:
    if child>=0 and child not in reachable:reachable.add(child);todo.append(child)
  assert len(reachable)==len(nodes)
  component_counts.append(dag['count'])
 assert seen=={i for i,t in enumerate(tokens) if t['mobile']};assert out['global_assignments']==math.prod(component_counts) and out['dp_states']==totalstates
 assert out['components']==len(dags) and out['mobile_tokens']==len(seen)
 raw=(B/'artifacts/WORLD_LABELS.bin').read_bytes();width=(len(tokens)+7)//8;assert len(raw)==width*s['worlds'];scores=json.loads((B/'artifacts/WORLD_SCORES.json').read_text());assert len(scores)==s['worlds']
 denominator=collections.Counter(p['leaf'] for p in pairs);chosen=[p for p in pairs if tuple(p['stems']) in nom]
 def score(y):return sum((Fraction(1 if y[p['a']]==y[p['b']] else -1,denominator[p['leaf']]) for p in chosen),Fraction(0))/len(denominator)
 def margins(y):
  count=collections.Counter()
  for key,bit in zip(keys,y):
   for v in key:count[(v,bit)]+=1
  return count
 targetmargins=margins(base);observed=score(base);assert observed==Fraction(out['observed_numerator'],out['score_denominator']);rng=random.Random(s['seed']);worldscores=[]
 for w in range(s['worlds']):
  packed=raw[w*width:(w+1)*width];y=[(packed[i//8]>>(i%8))&1 for i in range(len(tokens))];assert all(((packed[i//8]>>(i%8))&1)==0 for i in range(len(tokens),width*8));assert margins(y)==targetmargins
  assert all(y[i]==base[i] for i in range(len(tokens)) if i not in seen)
  for dag in dags:
   node=dag['nodes'][dag['root']]
   for idx in dag['token_indices']:
    left,right=node['children'];z0=dag['nodes'][left]['count'] if left>=0 else 0;draw=rng.randrange(node['count']);bit=int(draw>=z0);assert y[idx]==bit;child=[left,right][bit];assert child>=0;node=dag['nodes'][child];assert node['count']>0
  actual=score(y);assert actual==Fraction(scores[w],out['score_denominator']);worldscores.append(actual)
 count=sum(v>=observed for v in worldscores);rank=Fraction(1+count,1+len(worldscores));mean=sum(worldscores,Fraction(0))/len(worldscores)
 assert count==out['at_least_observed'] and float(rank)==out['conditional_tail_rank']
 assert float(observed)==out['observed_T'] and abs(float(mean)-out['mean_T'])<1e-15
 assert sum(scores)==out['null_numerator_sum'];status='CONDITIONAL_ASSOCIATION_RETAINED' if rank<=Fraction(1,20) and observed>mean else 'STRONGER_CONDITIONAL_ASSOCIATION_NOT_ESTABLISHED';assert status==out['status']
 val={'status':'PASS','dag_states_verified':totalstates,'component_counts_verified':len(dags),'worlds_full_margins_and_scores_verified':len(worldscores),'uniform_integer_branch_stream':'MATCH','observed_score_exact':str(observed),'mean_score_exact':str(mean),'tail_rank_exact':str(rank),'implementation':'No primary import; complete count-DAG proof verification, component connectivity/separation, full binary margins and Fraction scores.','limits':'Verifies exactly uniform sampler construction and accounting, not unknown natural null truth, historical mechanism, projectwide significance or meanings.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(json.dumps(val,indent=2))
if __name__=='__main__':main()

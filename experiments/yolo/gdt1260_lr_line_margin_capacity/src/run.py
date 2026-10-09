import collections,hashlib,importlib.util,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def scc(edges):
 adj=collections.defaultdict(list);rev=collections.defaultdict(list)
 for i,(u,v) in enumerate(edges):adj[u].append((v,i));rev[v].append(u);adj[v];rev[u]
 seen=set();order=[]
 for root in sorted(adj):
  if root in seen:continue
  seen.add(root);stack=[(root,0)]
  while stack:
   u,k=stack[-1]
   if k==len(adj[u]):order.append(u);stack.pop();continue
   stack[-1]=(u,k+1);v=adj[u][k][0]
   if v not in seen:seen.add(v);stack.append((v,0))
 component={}
 for root in reversed(order):
  if root in component:continue
  tag=len(component);component[root]=tag;stack=[root]
  while stack:
   u=stack.pop()
   for v in rev[u]:
    if v not in component:component[v]=tag;stack.append(v)
 return [component[u]==component[v] for u,v in edges],adj

def controls():
 fixtures=[[(0,0),(0,0)],[(0,0),(0,1),(1,0),(1,1)],[(0,0),(0,1),(1,1),(1,2),(2,2),(2,0)],[(0,0),(0,1),(1,1),(1,2)],[(0,0),(0,1),(1,0),(1,1),(0,0),(1,1)]]
 checked=0
 for graph in fixtures:
  assignments=list(itertools.product([0,1],repeat=len(graph)));margins={}
  for y in assignments:
   a=collections.Counter();b=collections.Counter()
   for (u,v),label in zip(graph,y):a[u]+=label;b[v]+=label
   margins[y]=(tuple(sorted(a.items())),tuple(sorted(b.items())))
  for y in assignments:
   edges=[('L'+str(u),'S'+str(v)) if label==0 else ('S'+str(v),'L'+str(u)) for (u,v),label in zip(graph,y)];flags,_=scc(edges)
   exact=[any(z[i]!=y[i] for z in assignments if margins[z]==margins[y]) for i in range(len(graph))];assert flags==exact;checked+=1
 # Both tokens of a pair may move together, preserving inequality.
 square=fixtures[1];y=(0,1,1,0);z=(1,0,0,1)
 assert all(a!=b for a,b in zip(y,z)) and (y[0]==y[1])==(z[0]==z[1])
 return checked

def main():
 s=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 P=R/s['parent'];ps=json.loads((P/'src/SPEC.json').read_text());old=json.loads((P/'artifacts/RESULT.json').read_text());nom=set(map(tuple,json.loads((P/'artifacts/CANDIDATES.json').read_text())));assert len(nom)==22
 spec=importlib.util.spec_from_file_location('fixed_parent',P/'src/run.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
 summaries={};alltokens={};allwitness={};allpairs={}
 for reader in s['readers']:
  data=json.loads((P/f'artifacts/SOURCE_EVALUATION_{reader}.json').read_text());d=parent.prepare(data,ps,'EVALUATION');tokens=d['tokens'];pairs=d['pairs'];assert len(pairs)==old['readings'][reader]['denominators']['eligible_pairs']
  assert all(not t['page'].startswith('f84') and t['page']!='f116v' for t in tokens)
  linekeys=[(t['page'],t['locus']) for t in tokens];stratkeys=[(t['leaf'],t['stem'],t['position']) for t in tokens]
  nodes=[('L'+json.dumps(a,separators=(',',':')),'S'+json.dumps(b,separators=(',',':'))) for a,b in zip(linekeys,stratkeys)]
  y=[int(t['ending']=='l') for t in tokens];edges=[(v,u) if label else (u,v) for (u,v),label in zip(nodes,y)]
  mobile,adj=scc(edges);nompairs=[p for p in pairs if tuple(p['stems']) in nom];endpoints=sorted({p[k] for p in nompairs for k in ['a','b']})
  def margins(labels,keys):
   c=collections.Counter()
   for label,k in zip(labels,keys):c[k]+=label
   return c
  baseline_line=margins(y,linekeys);baseline_strata=margins(y,stratkeys)
  def score(labels,leaf):return sum(1 if labels[p['a']]==labels[p['b']] else -1 for p in nompairs if p['leaf']==leaf)
  witnesses=[];done=set()
  for i in endpoints:
   if not mobile[i]:continue
   u,v=edges[i];queue=collections.deque([v]);back={v:None}
   while queue and u not in back:
    here=queue.popleft()
    for there,j in adj[here]:
     if there not in back:back[there]=(here,j);queue.append(there)
   assert u in back;cycle=[i];at=u
   while at!=v:prev,j=back[at];cycle.append(j);at=prev
   key=tuple(sorted(cycle))
   if key in done:continue
   done.add(key);assert len(cycle)==len(set(cycle));labels=y[:]
   for j in cycle:labels[j]=1-labels[j]
   assert margins(labels,linekeys)==baseline_line and margins(labels,stratkeys)==baseline_strata
   leaf=tokens[i]['leaf'];assert {tokens[j]['leaf'] for j in cycle}=={leaf}
   before=score(y,leaf);after=score(labels,leaf)
   witnesses.append({'trigger_token':i,'cycle_token_indices':cycle,'source_ids':[tokens[j]['source_id'] for j in cycle],'leaf':leaf,'before_nominated_score':before,'after_nominated_score':after,'delta':after-before})
  mobileleaves=sorted({tokens[i]['leaf'] for i in endpoints if mobile[i]});changedleaves=sorted({w['leaf'] for w in witnesses if w['delta']})
  status='INSUFFICIENT_ENDPOINT_CAPACITY' if len(mobileleaves)<s['minimum_mobile_physical_leaves'] else ('WITNESSED_SCORE_CAPACITY' if len(changedleaves)>=s['minimum_mobile_physical_leaves'] else 'ENDPOINT_CAPACITY_INCONCLUSIVE_SCORE_SEARCH')
  summaries[reader]={'status':status,'tokens':len(tokens),'eligible_pairs':len(pairs),'nominated_pairs':len(nompairs),'nominated_leaves':len({p['leaf'] for p in nompairs}),'old_mobile_nominated_leaves':old['readings'][reader]['movable_nominated_leaves'],'mobile_tokens':sum(mobile),'nominated_endpoints':len(endpoints),'mobile_nominated_endpoints':sum(mobile[i] for i in endpoints),'mobile_nominated_leaves':mobileleaves,'unique_shortest_cycles':len(witnesses),'score_changing_cycles':sum(w['delta']!=0 for w in witnesses),'witnessed_score_mobile_leaves':changedleaves}
  alltokens[reader]=[dict(t,mobile=flag) for t,flag in zip(tokens,mobile)];allpairs[reader]=pairs;allwitness[reader]=witnesses
 result={'status':summaries[s['primary_reader']]['status'],'readers':summaries,'controls':controls(),'claim_ceiling':'Necessary endpoint capacity and explicit score-change witnesses only; no new null distribution, p-value, rerun selection or meaning;915/916unchanged.'}
 for name,obj in [('RESULT',result),('TOKENS',alltokens),('PAIRS',allpairs),('WITNESSES',allwitness)]: (B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 import sys
 if '--controls' in sys.argv:print(controls())
 else:main()

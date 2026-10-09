import collections,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());P=R/s['parent'];ps=json.loads((P/'src/SPEC.json').read_text());nom=set(map(tuple,json.loads((P/'artifacts/CANDIDATES.json').read_text())))
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 load=lambda n:json.loads((B/('artifacts/'+n+'.json')).read_text())
 result=load('RESULT');claimed=load('TOKENS');savedpairs=load('PAIRS');savedw=load('WITNESSES');checks={}
 for reader in s['readers']:
  raw=json.loads((P/f'artifacts/SOURCE_EVALUATION_{reader}.json').read_text());tokens=[];pairs=[]
  for line in raw['lines']:
   m=line['metadata'];assert m['page'] in ps['partitions']['EVALUATION'] and not m['page'].startswith('f84') and m['page']!='f116v'
   if m['kind']!='P':continue
   groups=[dict(zip(raw['group_columns'],g)) for g in line['groups']];local={};leaf=int(re.match(r'f([0-9]+)',m['page']).group(1))
   for j,g in enumerate(groups):
    w=g['ivtff_group_raw']
    if not(w.isascii() and w.isalpha() and w==w.lower() and len(w)>=2 and w[-1] in ['r','l']):continue
    idx=int(g['source_group_index']);count=int(m['source_group_count']);position='SINGLE' if count==1 else 'FIRST' if idx==1 else 'LAST' if idx==count else 'INTERNAL'
    local[j]=len(tokens);tokens.append({'source_id':g['source_group_id'],'page':m['page'],'locus':m['locus'],'index':idx,'leaf':leaf,'word':w,'stem':w[:-1],'ending':w[-1],'position':position})
   for j in range(len(groups)-1):
    if j not in local or j+1 not in local:continue
    a,b=local[j],local[j+1];ga,gb=groups[j:j+2]
    if tokens[a]['stem']==tokens[b]['stem'] or int(gb['source_group_index'])!=int(ga['source_group_index'])+1 or ga['right_separator']!='DEFINITE_SPACE' or gb['left_separator']!='DEFINITE_SPACE':continue
    pairs.append({'a':a,'b':b,'stems':[tokens[a]['stem'],tokens[b]['stem']],'leaf':leaf,'page':m['page'],'locus':m['locus'],'source_ids':[tokens[a]['source_id'],tokens[b]['source_id']]})
  assert pairs==savedpairs[reader]
  assert tokens==[{k:v for k,v in t.items() if k!='mobile'} for t in claimed[reader]]
  original=[t['ending'] for t in tokens];linekeys=[('L',t['page'],t['locus']) for t in tokens];strata=[('S',t['leaf'],t['stem'],t['position']) for t in tokens];adj=collections.defaultdict(list);edges=[]
  for i,(a,b,t) in enumerate(zip(linekeys,strata,tokens)):
   edge=(a,b) if t['ending']=='r' else (b,a);edges.append(edge);adj[edge[0]].append((edge[1],i))
  # Reachability directly, without SCC implementation or parent import.
  reach={};mobile=[]
  for u,v in edges:
   if v not in reach:
    seen={v};todo=[v]
    while todo:
     node=todo.pop()
     for nxt,_ in adj[node]:
      if nxt not in seen:seen.add(nxt);todo.append(nxt)
    reach[v]=seen
   mobile.append(u in reach[v])
  assert mobile==[t['mobile'] for t in claimed[reader]]
  nominated=[p for p in pairs if tuple(p['stems']) in nom];endpoints=sorted({p[k] for p in nominated for k in ['a','b']})
  def margins(y):
   c=collections.Counter()
   for i,label in enumerate(y):c[(linekeys[i],label)]+=1;c[(strata[i],label)]+=1
   return c
  base=margins(original);bycycle={};changedleaves=set()
  for w in savedw[reader]:
   cycle=w['cycle_token_indices'];assert len(cycle)==len(set(cycle)) and w['trigger_token'] in cycle
   assert [tokens[i]['source_id'] for i in cycle]==w['source_ids']
   assert {tokens[i]['leaf'] for i in cycle}=={w['leaf']}
   y=original[:]
   for i in cycle:assert mobile[i];y[i]='l' if y[i]=='r' else 'r'
   assert margins(y)==base
   score=lambda z:sum(1 if z[p['a']]==z[p['b']] else -1 for p in nominated if p['leaf']==w['leaf'])
   assert score(original)==w['before_nominated_score'] and score(y)==w['after_nominated_score'] and score(y)-score(original)==w['delta']
   bycycle[tuple(sorted(cycle))]=w
   if w['delta']:changedleaves.add(w['leaf'])
  # Reproduce the bounded deterministic BFS search including zero-change cycles.
  expected={}
  for i in endpoints:
   if not mobile[i]:continue
   u,v=edges[i];queue=collections.deque([v]);prior={v:None}
   while queue and u not in prior:
    here=queue.popleft()
    for there,j in adj[here]:
     if there not in prior:prior[there]=(here,j);queue.append(there)
   assert u in prior;cycle=[i];at=u
   while at!=v:at,j=prior[at];cycle.append(j)
   key=tuple(sorted(cycle));expected.setdefault(key,(i,cycle))
  assert set(expected)==set(bycycle)
  for key,(trigger,cycle) in expected.items():assert bycycle[key]['trigger_token']==trigger and bycycle[key]['cycle_token_indices']==cycle
  info=result['readers'][reader];mobileleaves=sorted({tokens[i]['leaf'] for i in endpoints if mobile[i]})
  assert info['tokens']==len(tokens) and info['eligible_pairs']==len(pairs) and info['nominated_pairs']==len(nominated)
  assert info['mobile_tokens']==sum(mobile) and info['nominated_endpoints']==len(endpoints) and info['mobile_nominated_endpoints']==sum(mobile[i] for i in endpoints)
  assert info['mobile_nominated_leaves']==mobileleaves and info['witnessed_score_mobile_leaves']==sorted(changedleaves)
  assert info['unique_shortest_cycles']==len(bycycle) and info['score_changing_cycles']==sum(w['delta']!=0 for w in savedw[reader])
  status='INSUFFICIENT_ENDPOINT_CAPACITY' if len(mobileleaves)<5 else 'WITNESSED_SCORE_CAPACITY' if len(changedleaves)>=5 else 'ENDPOINT_CAPACITY_INCONCLUSIVE_SCORE_SEARCH'
  assert info['status']==status
  checks[reader]={'source_census':'MATCH','all_token_reachability':'MATCH','all_shortest_cycles':'MATCH','both_margin_systems':'EXACT','score_mobile_leaves':len(changedleaves),'status':status}
 assert result['status']==checks['ZL3b']['status']
 output={'status':'PASS','checks':checks,'independence':'Direct raw-source reconstruction and return reachability; imports neither primary runner nor915; exact margin/score checks of every cycle.','limits':'Capacity only; no conditional probability, history, meaning or revised915decision.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()

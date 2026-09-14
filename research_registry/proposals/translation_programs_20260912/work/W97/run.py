import csv,json,hashlib
from pathlib import Path
from collections import defaultdict,deque,Counter
D=Path(__file__).resolve().parent.relative_to(Path.cwd())
for f,h in json.loads((D/'SOURCE.json').read_text())['hashes'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
assert (D/'PROSE.tsv').read_bytes()==(D.parent/'W92/PROSE.tsv').read_bytes()
source=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'));assert {r['page'] for r in source}=={'f83r'}
records={};names={'qokaiin':'A','shedy':'B','lchedy':'C'};ops={'qokedy','qokeedy'}
for r in source:records.setdefault(r['record_id'],[]).extend(dict(word=w,at=r['locus']+':'+str(i),line=r['locus']) for i,w in enumerate(r['zl3b_line'].split(),1))
edges=[];alignment=[]
for rid,ts in records.items():
 last=None
 for i,t in enumerate(ts):
  if t['word'] in names:last=i
  gloss=names[t['word']]+' [Personenhypothese]' if t['word'] in names else '[Relation? '+t['word']+']' if t['word'] in ops else '⟦'+t['word']+'⟧'
  alignment.append(dict(record=rid,at=t['at'],word=t['word'],reading=gloss))
  if t['word'] not in ops:continue
  right=None
  for j in range(i+1,len(ts)):
   if ts[j]['word'] in ops:break
   if ts[j]['word'] in names:right=j;break
  edges.append(dict(record=rid,at=t['at'],word=t['word'],left=names[ts[last]['word']] if last is not None else '',left_at=ts[last]['at'] if last is not None else '',right=names[ts[right]['word']] if right is not None else '',right_at=ts[right]['at'] if right is not None else '',left_gap=' '.join(u['word'] for u in ts[last+1:i]) if last is not None else '',right_gap=' '.join(u['word'] for u in ts[i+1:right]) if right is not None else '',status='BOUND' if last is not None and right is not None else 'MISSING_BOTH' if last is None and right is None else 'MISSING_LEFT' if last is None else 'MISSING_RIGHT'))
models=[];witnesses=[]
by_at={e['at']:e for e in edges}
for step in sorted(ops):
 for sign in [1,-1]:
  key=step+('_FORWARD' if sign==1 else '_REVERSE');conflicts=[];cycles=[]
  for rid in records:
   tree=defaultdict(list)
   for e in [e for e in edges if e['record']==rid and e['status']=='BOUND']:
    queue=deque([(e['left'],0,[])]);visited={e['left']};found=None;delta=sign if e['word']==step else 0
    while queue:
     node,value,path=queue.popleft()
     if node==e['right']:found=value,path;break
     for target,weight,at,direction in tree[node]:
      if target not in visited:visited.add(target);queue.append((target,value+weight,path+[(at,direction)]))
    if found is None:
     tree[e['left']].append((e['right'],delta,e['at'],1));tree[e['right']].append((e['left'],-delta,e['at'],-1))
    else:
     actual,path=found;support=path+[(e['at'],-1)]
     w=dict(model=key,record=rid,closing_at=e['at'],implied_delta=actual,required_delta=delta,residual=actual-delta,support=support,mixed_operators=len({by_at[at]['word'] for at,d in support})==2,self_link=e['left']==e['right'])
     cycles.append(w)
     if actual!=delta:conflicts.append(w);witnesses.append(w)
  bound_step=sum(e['status']=='BOUND' and e['word']==step for e in edges)
  models.append(dict(model=key,step=step,sign=sign,equal=next(iter(ops-{step})),bound_step=bound_step,conflicting_edges=len(conflicts),mixed_conflicting_edges=sum(w['mixed_operators'] for w in conflicts),verdict='INCONSISTENT_FIXED_MODEL' if conflicts else 'NO_STEP_CAPACITY' if not bound_step else 'FORMALLY_COMPATIBLE_UNCONFIRMED'))
for name,rr in [('EDGES.tsv',edges),('ALIGNMENT.tsv',alignment)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(rr)
for name,obj in [('MODELS.json',models),('CONTRADICTIONS.json',witnesses)]: (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
md=['# W97 — alle sieben Records','Alle Person- und Relationsrollen hypothetisch. Andere Wörter bleiben ungelesen.']
for rid,ts in records.items():
 md+=['\n## '+rid]
 for r in source:
  if r['record_id']==rid:md+=['\n'+r['locus']+' `'+r['zl3b_line']+'`','\n'+' · '.join(a['reading'] for a in alignment if a['record']==rid and a['at'].rsplit(':',1)[0]==r['locus'])]
(D/'READING.md').write_text('\n'.join(md)+'\n')
result=dict(records=len(records),lines=len(source),groups=len(alignment),operators=dict(Counter(e['word'] for e in edges)),bindings=dict(Counter(e['status'] for e in edges)),models=models,confirmed_meanings=0,independent_confirmation_capacity=0,reserved_access=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
# Verify every contradiction algebraically in the original edge set.
for w in witnesses:
 m=next(m for m in models if m['model']==w['model']);balance=Counter();residual=0
 for at,direction in w['support']:
  e=by_at[at];balance[e['right']]+=direction;balance[e['left']]-=direction;residual+=direction*(m['sign'] if e['word']==m['step'] else 0)
 assert not any(balance.values()) and residual==w['residual'] and residual!=0
assert len(alignment)==341 and len(records)==7
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',scope='frozen source, full alignment, exact nonzero cycle contradiction certificates',independent_validator=False,meaning_confirmation=False),indent=2)+'\n')

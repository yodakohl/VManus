import collections, hashlib, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[4]
OUT=pathlib.Path(__file__).resolve().parents[1]/'artifacts'
lock=json.loads((OUT.parent/'src/REGISTRATION_LOCK.json').read_text())
for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
rx=re.compile(r'(qo|o)?([kt])(ch|sh)(e?)(d?)y')
events=[]; counts=collections.Counter()
for path in sorted(lock['files']):
 if 'SOURCE_' not in path: continue
 data=json.loads((ROOT/path).read_text())
 for line in data['lines']:
  m=line['metadata']; assert not m['page'].startswith(('f84','f116v'))
  if m['kind']!='P': continue
  groups={int(g[1]):g for g in line['groups']}
  for i,g in groups.items():
   match=rx.fullmatch(g[2])
   if not match: continue
   reader=m['edition']; counts[reader+' targets']+=1
   h=groups.get(i+1)
   if h is None or g[4]!='DEFINITE_SPACE' or h[3]!='DEFINITE_SPACE' or g[3] not in ('LINE_START','DEFINITE_SPACE') or h[4] not in ('LINE_END','DEFINITE_SPACE') or not re.fullmatch('[a-z]+',h[2]):
    counts[reader+' excluded']+=1; continue
   a,b,c,e,d=match.groups(); base=(a or '')+b+c+e+'y'
   leaf=re.match(r'f\d+',m['page'])[0]
   key=[base,leaf,m['section'],m['currier'],m['hand'],'FIRST' if i==1 else 'INTERNAL']
   events.append(dict(reader=reader,id=g[0],next_id=h[0],locus=m['locus'],page=m['page'],word=g[2],next_word=h[2],d=int(bool(d)),q=int(h[2].startswith('q')),key=key))
results={}; cells=[]
for reader in ('ZL3b','IT2a','RF1b'):
 groups=collections.defaultdict(list)
 for v in events:
  if v['reader']==reader: groups[tuple(v['key'])].append(v)
 leaves=collections.defaultdict(list); informative=set(); matched_events=0
 for key,vs in sorted(groups.items()):
  table=[[sum(v['d']==d and v['q']==q for v in vs) for q in (0,1)] for d in (0,1)]
  matched=all(sum(row)>0 for row in table)
  delta=table[1][1]/sum(table[1])-table[0][1]/sum(table[0]) if matched else None
  cells.append(dict(reader=reader,key=key,table=table,matched=matched,delta=delta))
  if matched:
   leaves[key[1]].append(delta); matched_events+=len(vs)
   if any(v['q']==0 for v in vs) and any(v['q']==1 for v in vs): informative.add(key[1])
 scores={k:sum(v)/len(v) for k,v in sorted(leaves.items())}
 mean=sum(scores.values())/len(scores) if scores else None
 positive=sum(v>0 for v in scores.values())
 decision='CAPACITY_STOP' if len(informative)<10 else ('MATCHED_ASSOCIATION_RETAINED' if mean>=.05 and 3*positive>=2*len(scores) else 'NOT_CONFIRMED')
 results[reader]=dict(targets=counts[reader+' targets'],excluded=counts[reader+' excluded'],eligible=sum(len(v) for v in groups.values()),strata=len(groups),matched_strata=sum(len(v) for v in leaves.values()),matched_events=matched_events,scored_leaves=len(scores),informative_leaves=len(informative),positive_leaves=positive,mean=mean,leaf_scores=scores,decision=decision)
for name,obj in [('EVENTS',events),('CELLS',cells),('RESULT',results)]: (OUT/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps(results,indent=2))

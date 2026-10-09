import collections, itertools, json, pathlib, math, hashlib
P=pathlib.Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
for path,h in lock['files'].items(): assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
forms={w+h+m+e+d+'y':(w+h+m+e+'y',int(bool(d))) for w,h,m,e,d in itertools.product(['','o','qo'],'kt',['ch','sh'],['','e'],['','d'])}
expected={}; total=collections.Counter(); rejected=collections.Counter()
for path in lock['files']:
 if 'SOURCE_' not in path: continue
 for line in json.loads((ROOT/path).read_text())['lines']:
  meta=line['metadata']
  assert meta['page'] not in ('f84','f84r','f84v','f116v')
  if meta['kind']!='P': continue
  gs=[dict(zip(['id','index','raw','left','right'],g)) for g in line['groups']]
  for g in gs:
   if g['raw'] not in forms: continue
   reader=meta['edition']; total[reader]+=1
   follows=[h for h in gs if int(h['index'])==int(g['index'])+1]
   valid=len(follows)==1
   if valid:
    h=follows[0]
    valid=(g['right']==h['left']=='DEFINITE_SPACE' and g['left'] in ['LINE_START','DEFINITE_SPACE'] and h['right'] in ['DEFINITE_SPACE','LINE_END'] and bool(h['raw']) and all('a'<=c<='z' for c in h['raw']))
   if not valid: rejected[reader]+=1; continue
   base,d=forms[g['raw']]; digits=''
   for c in meta['page'][1:]:
    if not c.isdigit(): break
    digits+=c
   key=[base,'f'+digits,meta['section'],meta['currier'],meta['hand'],'FIRST' if int(g['index'])==1 else 'INTERNAL']
   v=dict(reader=reader,id=g['id'],next_id=h['id'],locus=meta['locus'],page=meta['page'],word=g['raw'],next_word=h['raw'],d=d,q=int(h['raw'][0]=='q'),key=key)
   assert g['id'] not in expected
   expected[g['id']]=v
actual=json.loads((P/'artifacts/EVENTS.json').read_text())
assert len(actual)==len(expected)
assert {v['id']:v for v in actual}==expected
result=json.loads((P/'artifacts/RESULT.json').read_text()); actual_cells=json.loads((P/'artifacts/CELLS.json').read_text())
for reader,r in result.items():
 cells=collections.defaultdict(lambda:collections.Counter())
 for v in expected.values():
  if v['reader']==reader: cells[tuple(v['key'])][v['d'],v['q']]+=1
 leaf=collections.defaultdict(list); info=set(); ne=0
 for k,t in cells.items():
  n0=t[0,0]+t[0,1]; n1=t[1,0]+t[1,1]
  record=next(c for c in actual_cells if c['reader']==reader and c['key']==list(k))
  assert record['table']==[[t[d,q] for q in [0,1]] for d in [0,1]]
  assert record['matched']==bool(n0 and n1)
  if n0 and n1:
   delta=(t[1,1]*n0-t[0,1]*n1)/(n0*n1)
   assert math.isclose(delta,record['delta'],abs_tol=1e-12)
   leaf[k[1]].append(delta); ne+=n0+n1
   if t[0,0]+t[1,0] and t[0,1]+t[1,1]: info.add(k[1])
 scores={k:sum(a)/len(a) for k,a in leaf.items()}; mean=sum(scores.values())/len(scores); pos=sum(v>0 for v in scores.values())
 assert total[reader]==r['targets'] and rejected[reader]==r['excluded']
 assert r['eligible']==sum(sum(t.values()) for t in cells.values())
 assert r['matched_events']==ne and r['matched_strata']==sum(map(len,leaf.values()))
 assert r['scored_leaves']==len(leaf) and r['informative_leaves']==len(info) and r['positive_leaves']==pos
 assert math.isclose(mean,r['mean'],abs_tol=1e-12)
 assert all(math.isclose(v,r['leaf_scores'][k],abs_tol=1e-12) for k,v in scores.items())
 decision='CAPACITY_STOP' if len(info)<10 else ('MATCHED_ASSOCIATION_RETAINED' if mean>=.05 and pos/len(leaf)>=2/3 else 'NOT_CONFIRMED')
 assert r['decision']==decision
out={'status':'PASS','independently_reconstructed_events':len(expected),'enumerated_target_forms':len(forms),'scope':'source selection, event completeness, matched tables, leaf arithmetic, frozen gates; not semantic or independent manuscript confirmation'}
(P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

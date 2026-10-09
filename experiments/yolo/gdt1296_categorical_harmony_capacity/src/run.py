#!/usr/bin/env python3
import collections,gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def graph(words,n):
 adj=[0]*n;touch=[0]*n
 for j,word in enumerate(words):
  unique=set(word)
  for u in unique:
   touch[u]|=1<<j
   for v in unique-{u}:adj[u]|=1<<v
 return adj,touch

def enumerate_capacity(words,n):
 adj,touch=graph(words,n);full=(1<<n)-1;comp=[full&~(adj[i]|(1<<i)) for i in range(n)];candidates=[];visits=0;cache={}
 def bcount(mask):
  if mask not in cache:
   bits=0
   for i in range(n):
    if mask>>i&1:bits|=touch[i]
   cache[mask]=bits
  return cache[mask]
 def visit(a,b,start,hit):
  nonlocal visits
  visits+=1
  for i in range(start,n):
   bb=b&comp[i]
   if bb.bit_count()<2:continue
   aa=a+(i,);hh=hit|touch[i]
   if len(aa)>=2:
    hb=bcount(bb);assert not(hh&hb)
    btuple=tuple(j for j in range(n) if bb>>j&1);ca=hh.bit_count();cb=hb.bit_count()
    candidates.append({'A':list(aa),'Bmax':list(btuple),'A_groups':ca,'B_groups':cb,'balanced_groups':min(ca,cb),'covered_groups':ca+cb})
   visit(aa,bb,i+1,hh)
 visit((),full,0,0)
 def key(c):
  pair=tuple(sorted((tuple(c['A']),tuple(c['Bmax']))))
  return (-c['balanced_groups'],-c['covered_groups'],pair)
 best=min(candidates,key=key) if candidates else None
 return candidates,best,visits

def brute(words,n):
 best=None
 for labels in itertools.product(range(3),repeat=n):
  a=tuple(i for i,v in enumerate(labels) if v==1);b=tuple(i for i,v in enumerate(labels) if v==2)
  if min(len(a),len(b))<2:continue
  aa=set(a);bb=set(b);hits=[(bool(set(w)&aa),bool(set(w)&bb)) for w in words]
  if any(x and y for x,y in hits):continue
  ca=sum(x for x,y in hits);cb=sum(y for x,y in hits);key=(-min(ca,cb),-(ca+cb),tuple(sorted((a,b))))
  if best is None or key<best:best=key
 return best

def fixtures():
 pairs=list(itertools.combinations(range(5),2));count=0
 for mask in range(1<<len(pairs)):
  words=[(i,) for i in range(5)]+[e for j,e in enumerate(pairs) if mask>>j&1]
  candidates,best,_=enumerate_capacity(words,5);exact=brute(words,5)
  # Maximal-B reduction preserves optimal coverage; lex tie need not match a smaller B.
  assert (None if best is None else (-best['balanced_groups'],-best['covered_groups']))==(None if exact is None else exact[:2]);count+=1
 for words in [[],[(0,0),(0,0),(1,),(2,),(3,),(4,)],[(0,1,2,3,4)],[(0,),(1,),(2,),(3,)]]:
  n=5;c,b,_=enumerate_capacity(words,n);z=brute(words,n);assert (None if b is None else (-b['balanced_groups'],-b['covered_groups']))==(None if z is None else z[:2])
 return {'status':'PASS','all_five_vertex_graphs':count,'special_corpora':4,'scope':'Optimalcoverageversusallternaryassignments;emptysourceunscorableinnativesummary'}

def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 raw=(R/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];data=json.loads(gzip.decompress(raw));units=s['units'];idx={u:i for i,u in enumerate(units)};results={};pack={};support={};graphs={}
 for reader in s['readers']:
  rows=data[reader];words=[];edge=collections.defaultdict(list)
  for q in rows:
   assert q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE'
   assert q['units'] and ''.join(q['units'])==q['ivtff_group_raw'] and not q['page'].startswith('f84') and q['page']!='f116v'
   w=tuple(idx[u] for u in q['units']);words.append(w)
   for e in itertools.combinations(sorted(set(w)),2):edge[e].append(q['id'])
  assert len({q['id'] for q in rows})==len(rows)
  if rows:assert set(itertools.chain.from_iterable(words))==set(range(len(units)))
  c,b,visits=enumerate_capacity(words,len(units));N=len(rows)
  status='UNSCORABLE_EMPTY' if not N else 'NO_ASSIGNMENT' if b is None else 'NECESSARY_CAPACITY_ONLY' if 20*b['balanced_groups']>=N else 'LOW_ACTIVITY'
  best=None if b is None else {**b,'A_units':[units[i] for i in b['A']],'B_units':[units[i] for i in b['Bmax']],'balanced_fraction':b['balanced_groups']/N if N else None}
  if best:assert 2*best['balanced_groups']<=N
  results[reader]={'status':status,'groups':N,'cooccurrence_edges':len(edge),'eligible_A_subsets':len(c),'search_states':visits,'best':best}
  pack[reader]=c;graphs[reader]=[{'units':[units[i] for i in pair],'groups':len(ids),'first_id':min(ids)} for pair,ids in sorted(edge.items())]
  support[reader]={}
  if b:
   for role,inds in [('A',b['A']),('B',b['Bmax'])]:support[reader][role]=[q['id'] for q,w in zip(rows,words) if set(w)&set(inds)]
  print(reader,status,json.dumps(best),flush=True)
 overall='COMMON_CATEGORICAL_HARMONY_EXCLUDED' if all(z['status'] in ['NO_ASSIGNMENT','LOW_ACTIVITY'] for z in results.values()) else 'NECESSARY_CAPACITY_OR_UNSCORABLE'
 out={'status':overall,'readers':results,'scope':'Global22single-unitclasses,onewritten-groupdomain,>=2types/class,andboth>=5%stricttokens;notgeneralphonology'}
 for name,obj in [('RESULT',out),('COOCCURRENCE',graphs),('BEST_SUPPORT',support)]: (B/f'artifacts/{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
 (B/'artifacts/CANDIDATES.json.gz').write_bytes(gzip.compress(json.dumps(pack,sort_keys=True,separators=(',',':')).encode(),mtime=0))
if __name__=='__main__':
 import sys
 if '--fixtures' in sys.argv:
  o=fixtures();(B/'artifacts/FIXTURES.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o))
 else:main()

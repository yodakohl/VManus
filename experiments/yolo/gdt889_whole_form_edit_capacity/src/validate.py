"""Independent all-pairs dynamic programming and BFS; no producer import."""
import argparse,hashlib,json,re
from collections import deque
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def distance(a,b):
 row=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  nxt=[i]
  for j,y in enumerate(b,1):nxt.append(min(nxt[-1]+1,row[j]+1,row[j-1]+(x!=y)))
  row=nxt
 return row[-1]
def components(words):
 words=sorted(set(words));graph={w:[] for w in words};edges=0
 for i,a in enumerate(words):
  for b in words[:i]:
   if abs(len(a)-len(b))<=2 and distance(a,b)<=2:graph[a].append(b);graph[b].append(a);edges+=1
 unseen=set(words);out=[]
 while unseen:
  start=min(unseen);unseen.remove(start);q=deque([start]);part=[]
  while q:
   w=q.popleft();part.append(w)
   for v in graph[w]:
    if v in unseen:unseen.remove(v);q.append(v)
  out.append(sorted(part))
 return sorted(out,key=lambda x:x[0]),edges

def selftest():
 assert distance('ab','ba')==2 and distance('abc','abc')==0
 assert distance('','abc')==3 and distance('abc','axbc')==1
 assert components(['aaa','aab','bbb'])[0]==[['aaa','aab','bbb']]
 assert distance('aaa','bbb')==3
 assert components(['aaa','bbb'])[0]==[['aaa'],['bbb']]
 assert components(['abc','ac','abcd'])[0]==[['abc','abcd','ac']]
 return ['unit_edit_distance_not_transposition','transitive_collision_chain','disjoint_balls','insert_delete_and_identity']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--selftest',action='store_true');a=ap.parse_args();tests=selftest()
 if a.selftest:print('PASS',tests);return
 for name,digest in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 p=E/'artifacts/RESULT.json';r=json.loads(p.read_text());source=ROOT/r['source'];rows=json.loads(source.read_text())
 assert hashlib.sha256(source.read_bytes()).hexdigest()==r['source_sha256']
 assert len(rows)==r['group_count']==1617 and all(not x['page'].startswith('f84') for x in rows)
 assert r['physical_leaves']==sorted({re.match(r'f[0-9]+',x['page']).group() for x in rows})
 words=sorted({x['raw'] for x in rows});assert words==r['words'] and len(words)==749
 assert sorted(set(''.join(words)))==r['alphabet']
 groups,edges=components(words);assert groups==r['components']
 assert r['max_distinct_messages']==len(groups) and r['injective_possible']==all(len(g)==1 for g in groups)
 assert len(r['forest'])==len(words)-len(groups)
 forest={w:[] for w in words}
 for edge in r['forest']:
  x,y,z=edge['left'],edge['right'],edge['received'];assert x!=y and set(z)<=set(r['alphabet'])
  assert distance(x,z)<=1 and distance(y,z)<=1
  forest[x].append(y);forest[y].append(x)
 for group in groups:
  reached={group[0]};q=deque(reached)
  while q:
   for w in forest[q.popleft()]:
    if w not in reached:reached.add(w);q.append(w)
  assert reached==set(group)
 out=dict(status='PASS',independent_method='all-pairs Levenshtein DP and BFS',checked_pairs=len(words)*(len(words)-1)//2,distance_at_most_two_edges=edges,forest_edges=len(r['forest']),component_sizes=sorted(map(len,groups),reverse=True),max_distinct_messages=len(groups),selftests=tests,result_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()

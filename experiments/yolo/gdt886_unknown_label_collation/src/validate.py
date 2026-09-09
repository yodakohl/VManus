#!/usr/bin/env python3
import itertools,json,subprocess
from pathlib import Path
from run import E,ROOT,ROWS,analyse,compare,enc

def feasible(comparisons,alphabet):
 if any(c['kind']=='prefix_inversion' for c in comparisons):return False
 edges={tuple(c['symbols']) for c in comparisons if c['kind']=='edge'};left=set(alphabet)
 while left:
  zero={x for x in left if all(b!=x or a not in left for a,b in edges)}
  if not zero:return False
  left-=zero
 return True

def main():
 subprocess.run(['python3',str(E/'src/run.py'),'--check'],cwd=ROOT,check=True,capture_output=True)
 r=json.loads((E/'artifacts/RESULT.json').read_text());data=json.loads((E/'artifacts/SELECTED.json').read_text());idx={(x['edition'],x['locus']):x for x in data};checks=0
 for key,p in r['panels'].items():
  unit,ed=key.split(':');cs=[]
  for ri,locs in enumerate(p['retained_rows']):
   assert all(x in ROWS[ri] for x in locs)
   assert [ROWS[ri].index(x) for x in locs]==sorted(ROWS[ri].index(x) for x in locs)
   for a,b in zip(locs,locs[1:]):
    aa=idx[('ZL3b' if ed=='CONSENSUS' else ed,a)][unit];bb=idx[('ZL3b' if ed=='CONSENSUS' else ed,b)][unit]
    i=0
    while i<min(len(aa),len(bb)) and aa[i]==bb[i]:i+=1
    kind='edge' if i<min(len(aa),len(bb)) else 'equal' if len(aa)==len(bb) else 'prefix_correct' if len(aa)<len(bb) else 'prefix_inversion'
    c=dict(row=ri+1,loci=[a,b],kind=kind)
    if kind=='edge':c.update(symbols=[aa[i],bb[i]],position=i)
    cs.append(c)
  assert cs==p['comparisons'];checks+=len(cs)
  assert feasible(cs,p['alphabet'])==(p['joint']['status']=='COMPATIBLE_PARTIAL_ORDER')
  assert feasible([c for c in cs if c['row']==1],p['alphabet'])==(p['training']['status']=='COMPATIBLE_PARTIAL_ORDER')
  for part in ['joint','training']:
   z=p[part];cycle=z['cycle'];assert not cycle or cycle[0]==cycle[-1]
   for a,b,c in zip(cycle,cycle[1:],z['cycle_witnesses']):assert c in cs and c['symbols']==[a,b]
   if z['one_extension']:
    pos={a:i for i,a in enumerate(z['one_extension'])}
    for c in cs:
     if part=='training' and c['row']!=1:continue
     assert c['kind']!='prefix_inversion'
     if c['kind']=='edge':assert pos[c['symbols'][0]]<pos[c['symbols'][1]]
  checks+=2
 # Exhaustive tiny alphabets exercise the inverse-collation equivalence, including prefixes.
 words=['a','b','c','aa','ab','ac','ba','ca'];toy=0
 for seq in itertools.product(words,repeat=3):
  rows=[[dict(locus=str(i),symbols=list(w)) for i,w in enumerate(seq)],[]]
  got=analyse(rows)['joint']['status']=='COMPATIBLE_PARTIAL_ORDER';truth=False
  for order in itertools.permutations('abc'):
   rank={x:i for i,x in enumerate(order)};encoded=[tuple(rank[x] for x in w) for w in seq]
   if encoded==sorted(encoded):truth=True;break
  assert got==truth,seq;toy+=1
 out=dict(experiment_id='GDT886',status='PASS',comparison_and_graph_checks=checks,exhaustive_toy_sequences=toy,source_replay=True,native_order_review='separate artifact required; not validated by arithmetic')
 (E/'artifacts/VALIDATION.json').write_text(enc(out));print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()

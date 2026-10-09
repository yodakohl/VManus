from pathlib import Path
from collections import Counter
from functools import lru_cache
import json,heapq
ROOT=Path(__file__).resolve().parents[3].parent
RAW=ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_MULTIGRAPH_SHORTHAND_RAW_20261005.json'
BASE=list('abcdefghijklmnopqrstuvwxyz')+list(json.loads(RAW.read_text())['teaching_carrier']['rare_characters_in_order'])
BANKS={'I':'o ch d q s sh k t'.split(),'M':'e a i o k t ch d'.split(),'F':'y n r o l d a m'.split()}
MODELS=[f'M{merges}-R{r}' for merges in [128,512] for r in [4,6,8]]
def merge(xs,pair):
 out=[];i=0
 while i<len(xs):
  if i+1<len(xs) and (xs[i],xs[i+1])==tuple(pair):out.append(xs[i]+xs[i+1]);i+=2
  else:out.append(xs[i]);i+=1
 return out

def train(source):
 wc=Counter(w for col in ['b4','w1'] for recipe in source[col] for w in recipe['words']);wordunits={w:list(w) for w in wc};inventory=set(BASE);merges=[];snapshots={}
 assert all(set(w)<=set(BASE) for w in wc)
 for step in range(1,513):
  pairs=Counter()
  for w,us in wordunits.items():
   for pair in zip(us,us[1:]):pairs[pair]+=wc[w]
  pair=min(pairs,key=lambda p:(-pairs[p],p));merges.append(list(pair));inventory.add(''.join(pair));wordunits={w:merge(us,pair) for w,us in wordunits.items()}
  if step in [128,512]:
   counts=Counter()
   for w,us in wordunits.items():
    for u in us:counts[u]+=wc[w]
   snapshots[step]={'merges':list(merges),'weights':{u:counts[u]+1 for u in sorted(inventory)}}
 tables={}
 for count,snap in snapshots.items():
  for radix in [4,6,8]:
   heap=[];serial=0
   for unit,weight in snap['weights'].items():heap.append((weight,serial,unit));serial+=1
   dummies=(-(len(heap)-1))%(radix-1)
   for _ in range(dummies):heap.append((0,serial,None));serial+=1
   heapq.heapify(heap)
   while len(heap)>1:
    children=[heapq.heappop(heap) for _ in range(radix)];heapq.heappush(heap,(sum(x[0] for x in children),serial,[x[2] for x in children]));serial+=1
   tree=heap[0][2];codes={};dummy_paths=[]
   def walk(node,path):
    if isinstance(node,list):
     for i,child in enumerate(node):walk(child,path+[i])
    elif node is None:dummy_paths.append(path)
    else:codes[node]=path
   walk(tree,[]);assert all(codes.values())
   tables[f'M{count}-R{radix}']={'radix':radix,'merges':snap['merges'],'weights':snap['weights'],'codes':codes,'dummy_paths':dummy_paths,'tree':tree}
 return {'training':['b4','w1'],'base':BASE,'banks':BANKS,'models':tables}

def ph(i,n):return 'F' if i==n-1 else 'I' if i==0 else 'M'
class Codec:
 def __init__(self,model,tables):
  self.table=tables['models'][model];self.radix=self.table['radix'];self.codes=self.table['codes'];self.merges=self.table['merges'];self.tree=self.table['tree'];self.banks=tables['banks'];self.allowed=set(tables['base'])
  @lru_cache(maxsize=None)
  def split(word):
   assert set(word)<=self.allowed,'Character outside inventory'
   us=list(word)
   for pair in self.merges:us=merge(us,pair)
   return tuple(us)
  self.split=split
 def encode(self,words):
  state=0;out=[]
  for word in words:
   ds=[d for u in self.split(word) for d in self.codes[u]];gs=[self.banks[ph(i,len(ds))][(d+state)%self.radix] for i,d in enumerate(ds)];out.append(''.join(gs));state=(state+len(word))%4
  return out
 def decode(self,rows):
  state=0;out=[]
  for gs in rows:
   ds=[(self.banks[ph(i,len(gs))][:self.radix].index(g)-state)%self.radix for i,g in enumerate(gs)];us=[];node=self.tree
   for d in ds:
    node=node[d]
    if not isinstance(node,list):assert node is not None,'Dummy path';us.append(node);node=self.tree
   assert node is self.tree,'Truncated code';word=''.join(us);assert self.split(word)==tuple(us),'Noncanonical fragments';out.append(word);state=(state+len(word))%4
  return out

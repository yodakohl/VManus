from pathlib import Path
from collections import Counter
from functools import lru_cache
import json,heapq
ROOT=Path(__file__).resolve().parents[3].parent
RAW=ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_MULTIGRAPH_SHORTHAND_RAW_20261005.json'
BASE=list('abcdefghijklmnopqrstuvwxyz')+list(json.loads(RAW.read_text())['teaching_carrier']['rare_characters_in_order'])
INITIAL={'BEGIN':'p f sh'.split(),'V':'o ch d'.split(),'S':'q k t'.split(),'A':'s o ch'.split(),'D':'cfh m d'.split(),'P':'ckh cth cph'.split()}
MEDIAL='e a i'.split();FINAL={'E':'y n r'.split(),'C':'l o d'.split()}
MODELS=[f'M{merges}-S{s}' for merges in [128,512,2048] for s in [3,6]]
def merge(xs,pair):
 out=[];i=0
 while i<len(xs):
  if i+1<len(xs) and (xs[i],xs[i+1])==tuple(pair):out.append(xs[i]+xs[i+1]);i+=2
  else:out.append(xs[i]);i+=1
 return out

def train(source):
 wc=Counter(w for col in ['b4','w1'] for recipe in source[col] for w in recipe['words']);wordunits={w:list(w) for w in wc};inventory=set(BASE);merges=[];snapshots={}
 assert all(set(w)<=set(BASE) for w in wc)
 for step in range(1,2049):
  pairs=Counter()
  for w,us in wordunits.items():
   for pair in zip(us,us[1:]):pairs[pair]+=wc[w]
  pair=min(pairs,key=lambda p:(-pairs[p],p));merges.append(list(pair));inventory.add(''.join(pair));wordunits={w:merge(us,pair) for w,us in wordunits.items()}
  if step in [128,512,2048]:
   counts=Counter()
   for w,us in wordunits.items():
    for u in us:counts[u]+=wc[w]
   snapshots[step]={'merges':list(merges),'weights':{u:counts[u]+1 for u in sorted(inventory)}}
 tables={}
 for count,snap in snapshots.items():
  for radix in [3]:
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
   tables[str(count)]={'radix':radix,'merges':snap['merges'],'weights':snap['weights'],'codes':codes,'dummy_paths':dummy_paths,'tree':tree}
 return {'training':['b4','w1'],'base':BASE,'initial':INITIAL,'medial':MEDIAL,'final':FINAL,'inventories':tables}

def category(previous):
 if previous is None:return 'BEGIN'
 ch=previous.lower()
 if ch in 'aeiouyäöü':return 'V'
 if ch in 'lmnr':return 'S'
 if ch.isalpha():return 'A'
 if ch.isdigit():return 'D'
 return 'P'

class Codec:
 def __init__(self,model,tables):
  count,states=model.split('-');self.states=int(states[1:]);self.table=tables['inventories'][count[1:]];self.codes=self.table['codes'];self.merges=self.table['merges'];self.tree=self.table['tree'];self.allowed=set(tables['base']);self.initial=tables['initial'];self.medial=tables['medial'];self.final=tables['final']
  @lru_cache(maxsize=None)
  def split(word):
   assert set(word)<=self.allowed,'Character outside inventory'
   us=list(word)
   for pair in self.merges:us=merge(us,pair)
   return tuple(us)
  self.split=split
 def encode(self,words):
  state=0;previous=None;out=[]
  for word in words:
   us=self.split(word)
   for j,u in enumerate(us):
    ds=self.codes[u];gs=[]
    for i,d in enumerate(ds):
     if i==len(ds)-1:bank=self.final['E' if j==len(us)-1 else 'C'];rotation=state//3
     else:bank=self.initial[category(previous)] if i==0 else self.medial;rotation=state%3
     gs.append(bank[(d+rotation)%3])
    out.append(''.join(gs));previous=u[-1];state=(state+len(u))%self.states
  return out
 def decode(self,rows):
  state=0;previous=None;out=[];pending=[]
  for gs in rows:
   assert gs
   flag=next((f for f,bank in self.final.items() if gs[-1] in bank),None);assert flag is not None
   ds=[]
   for i,g in enumerate(gs):
    if i==len(gs)-1:bank=self.final[flag];rotation=state//3
    else:bank=self.initial[category(previous)] if i==0 else self.medial;rotation=state%3
    ds.append((bank.index(g)-rotation)%3)
   node=self.tree
   for d in ds:
    assert isinstance(node,list),'Multiple leaves in group';node=node[d]
   assert isinstance(node,str) and node,'Incomplete or dummy code'
   pending.append(node);previous=node[-1];state=(state+len(node))%self.states
   if flag=='E':
    word=''.join(pending);assert self.split(word)==tuple(pending),'Noncanonical source fragments';out.append(word);pending=[]
  assert not pending,'Dangling source word';return out

from pathlib import Path
from collections import Counter
from functools import lru_cache
import json,heapq
ROOT=Path(__file__).resolve().parents[3].parent
RAW=ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_MULTIGRAPH_SHORTHAND_RAW_20261005.json'
BASE=list('abcdefghijklmnopqrstuvwxyz')+list(json.loads(RAW.read_text())['teaching_carrier']['rare_characters_in_order'])
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
MEDIAL='e a i'.split();FINAL={'E':'y n r'.split(),'C':'l o d'.split()}
MODELS=['M1024-S6-K7','M1024-S7-K7','M2048-S6-K7','M2048-S7-K7']
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
  if step in [512,1024,2048]:
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
 return {'training':['b4','w1'],'base':BASE,'medial':MEDIAL,'final':FINAL,'inventories':tables}

def frontier(table,cap):
 def mass(node):
  if isinstance(node,list):return sum(mass(x) for x in node)
  return 0 if node is None else table['weights'][node]
 def locate(path):
  node=table['tree']
  for d in path:node=node[d]
  return node
 fs=[(i,) for i in range(3)]
 assert all(isinstance(locate(p),list) for p in fs),'Root has leaf; minimum two signs unavailable'
 while len(fs)+2<=cap:
  eligible=[p for p in fs if all(isinstance(ch,list) for ch in locate(p))]
  if not eligible:break
  chosen=min(eligible,key=lambda p:(-mass(locate(p)),p));fs.remove(chosen);fs.extend(chosen+(i,) for i in range(3))
 return sorted(fs,key=lambda p:(-mass(locate(p)),p))

class Codec:
 def __init__(self,model,tables,alphabets=None):
  count,states,cap=model.split('-');self.states=int(states[1:]);self.table=tables['inventories'][count[1:]];self.codes=self.table['codes'];self.merges=self.table['merges'];self.tree=self.table['tree'];self.allowed=set(tables['base']);self.frontier=frontier(self.table,int(cap[1:]));self.K=len(self.frontier);self.alphabets=alphabets or default_alphabets();self.permutation=self.alphabets['initial'];assert self.K==7;self.encoded={}
  assert len(set(self.permutation))==22
  for u,ds in self.codes.items():
   matches=[(i,p) for i,p in enumerate(self.frontier) if tuple(ds[:len(p)])==p];assert len(matches)==1
   i,p=matches[0];tail=ds[len(p):];assert tail;self.encoded[u]=(i,tail)
  @lru_cache(maxsize=None)
  def split(word):
   assert set(word)<=self.allowed,'Character outside inventory'
   us=list(word)
   for pair in self.merges:us=merge(us,pair)
   return tuple(us)
  self.split=split
 def numeric(self,words):
  state=0;previous=None;out=[]
  for word in words:
   us=self.split(word)
   for j,u in enumerate(us):
    rank,ds=self.encoded[u];style=1 if previous is None else 2 if previous in '.,;:!?' else 0;gs=[style*7+(rank+state)%7]
    for i,d in enumerate(ds):
     if i==len(ds)-1:gs.append((25 if j==len(us)-1 else 28)+d)
     else:gs.append(22+d)
    out.append(gs);state=(state+len(u))%self.states;previous=u[-1]
  return out
 def render(self,rows):
  mapping=self.permutation+self.alphabets['medial'][:3]+self.alphabets['final'][:6]
  return [''.join(mapping[g] for g in row) for row in rows]
 def encode(self,words):return self.render(self.numeric(words))
 def decode(self,rows):
  state=0;previous=None;out=[];pending=[]
  for gs in rows:
   assert len(gs)>=2
   style=1 if previous is None else 2 if previous in '.,;:!?' else 0;index=self.permutation.index(gs[0]);assert style*7<=index<style*7+7;path=self.frontier[(index-style*7-state)%7];final={'E':self.alphabets['final'][:3],'C':self.alphabets['final'][3:6]};flag=next((f for f,bank in final.items() if gs[-1] in bank),None);assert flag
   ds=list(path)
   for i,g in enumerate(gs[1:],1):
    bank=final[flag] if i==len(gs)-1 else self.alphabets['medial'][:3];rotation=0;ds.append((bank.index(g)-rotation)%3)
   node=self.tree
   for d in ds:
    assert isinstance(node,list),'Extra leaf';node=node[d]
   assert isinstance(node,str) and node,'Incomplete or dummy'
   pending.append(node);state=(state+len(node))%self.states;previous=node[-1]
   if flag=='E':
    word=''.join(pending);assert self.split(word)==tuple(pending);out.append(word);pending=[]
  assert not pending;return out

def default_alphabets():
 def extend(prefix):return prefix+[g for g in SIGNS if g not in prefix]
 return {'initial':'o ch d q k s t p f sh m ckh cth cph y n r l a i cfh e'.split(),'medial':extend('e o i'.split()),'final':extend('r n y d l o'.split())}

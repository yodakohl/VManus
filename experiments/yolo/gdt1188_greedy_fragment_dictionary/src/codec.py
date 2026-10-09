from pathlib import Path
from functools import lru_cache
import importlib.util
ROOT=Path(__file__).resolve().parents[3].parent
spec=importlib.util.spec_from_file_location('initial_base',ROOT/'experiments/yolo/gdt1187_initial_only_counter_writer/src/codec.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
SIGNS=base.SIGNS;default_alphabets=base.default_alphabets
MODELS=[f'{kind}{count}-S6-K7' for count in [512,1024,2048] for kind in ['H','R','T']]
class Codec(base.Codec):
 def __init__(self,model,tables,alphabets=None):
  super().__init__(model,tables,alphabets);kind=model[0]
  if kind!='H':
   self.encoded={};ordered=sorted(self.codes,key=lambda u:(-self.table['weights'][u],u));minimum=1 if kind=='R' else 2
   for position,u in enumerate(ordered):
    length=minimum;rank=position
    while rank>=7*3**length:rank-=7*3**length;length+=1
    first,tailnum=divmod(rank,3**length);tail=[0]*length
    for j in range(length-1,-1,-1):tailnum,tail[j]=divmod(tailnum,3)
    assert tailnum==0;self.encoded[u]=(first,tail)
  self.inverse={(rank,tuple(ds)):u for u,(rank,ds) in self.encoded.items()};assert len(self.inverse)==len(self.encoded)
  index={}
  for u in self.codes:index.setdefault(u[0],[]).append(u)
  for ch,values in index.items():values.sort(key=lambda u:(-len(u),u))
  @lru_cache(maxsize=None)
  def split(word):
   assert set(word)<=self.allowed;out=[];pos=0
   while pos<len(word):
    u=next(u for u in index[word[pos]] if word.startswith(u,pos));out.append(u);pos+=len(u)
   return tuple(out)
  self.split=split
 def decode(self,rows):
  state=0;previous=None;out=[];pending=[]
  for gs in rows:
   assert len(gs)>=2
   style=1 if previous is None else 2 if previous in '.,;:!?' else 0;index=self.permutation.index(gs[0]);assert style*7<=index<style*7+7;rank=(index-style*7-state)%7
   final={'E':self.alphabets['final'][:3],'C':self.alphabets['final'][3:6]};flag=next((f for f,bank in final.items() if gs[-1] in bank),None);assert flag
   ds=[(final[flag] if i==len(gs)-1 else self.alphabets['medial'][:3]).index(g) for i,g in enumerate(gs[1:],1)]
   unit=self.inverse[(rank,tuple(ds))];pending.append(unit);state=(state+len(unit))%self.states;previous=unit[-1]
   if flag=='E':
    word=''.join(pending);assert self.split(word)==tuple(pending);out.append(word);pending=[]
  assert not pending;return out

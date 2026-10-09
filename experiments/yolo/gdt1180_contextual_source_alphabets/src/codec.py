from pathlib import Path
from collections import Counter,defaultdict
import json
ROOT=Path(__file__).resolve().parents[3].parent
RAW=ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_MULTIGRAPH_SHORTHAND_RAW_20261005.json'
RARE=json.loads(RAW.read_text())['teaching_carrier']['rare_characters_in_order']
CUTS='sch ch ck ei ie au eu en er em es ung lich heit keit'.split()
UNITS=list('abcdefghijklmnopqrstuvwxyz')+list(RARE)+CUTS
assert len(set(UNITS))==len(UNITS)
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
ORDERS={'flat':'e o a y i n d ch r l s k t sh p f m ckh cth cph cfh'.split(),'M':'e o a y i n d ch r l s k t sh p f m ckh cth cph cfh'.split(),'I':'o ch d y a s k t p f sh e i n r l m ckh cth cph cfh'.split(),'F':'y n r l o e a i d s m k t p f ch sh ckh cth cph cfh'.split()}
MODELS=[f'V{n}-{style}' for style in ['flat','edge'] for n in [2,3,4]]
VOWELS=set('aeiouyäöü')
def units(word):
 out=[];p=0
 while p<len(word):
  matches=[u for u in CUTS if word.startswith(u,p)]
  u=sorted(matches,key=lambda x:(-len(x),x))[0] if matches else word[p]
  if u not in UNITS:raise ValueError('Character outside fixed inventory')
  out.append(u);p+=len(u)
 return out

def state(model,history):
 n=int(model[1])
 if n==2:return int(history[-1] in VOWELS)
 if n==3:return 0 if history[-1] in VOWELS else 1 if history[-1] in 'lmnr' else 2
 return 2*int(history[-2] in VOWELS)+int(history[-1] in VOWELS)

def phase(model,i,n):return 'flat' if model.endswith('flat') else 'F' if i==n-1 else 'I' if i==0 else 'M'
def train(source):
 tables={}
 for model in MODELS:
  counts=defaultdict(Counter)
  for col in ['b4','w1']:
   for r in source[col]:
    history='  '
    for word in r['words']:
     us=units(word)
     for i,u in enumerate(us):
      key=f'{state(model,history)}:{phase(model,i,len(us))}';counts[key][u]+=1;history=(history+u)[-2:]
  rows={}
  for s in range(int(model[1])):
   for ph in (['flat'] if model.endswith('flat') else ['I','M','F']):
    key=f'{s}:{ph}';c=counts[key];rank=sorted(UNITS,key=lambda u:(-c[u],u));rows[key]={'common':rank[:21],'counts':{u:c[u] for u in rank}}
  tables[model]=rows
 return {'units':UNITS,'signs':SIGNS,'orders':ORDERS,'training':['b4','w1'],'models':tables}

class Codec:
 def __init__(self,model,tables):
  self.model=model;self.tables=tables;self.rows=tables['models'][model];self.common={k:{u:g for u,g in zip(row['common'],ORDERS[k.split(':')[1]])} for k,row in self.rows.items()};self.inverse={k:{g:u for u,g in row.items()} for k,row in self.common.items()}
 def encode(self,words):
  history='  ';out=[]
  for word in words:
   us=units(word);gs=[]
   for i,u in enumerate(us):
    key=f'{state(self.model,history)}:{phase(self.model,i,len(us))}'
    if u in self.common[key]:gs.append(self.common[key][u])
    else:
     j=UNITS.index(u);gs+=['q',SIGNS[j//22],SIGNS[j%22]]
    history=(history+u)[-2:]
   out.append(''.join(gs))
  return out
 def decode(self,rows):
  history='  ';out=[]
  for gs in rows:
   pieces=[];i=0
   while i<len(gs):
    width=3 if gs[i]=='q' else 1
    assert i+width<=len(gs)
    pieces.append(gs[i:i+width]);i+=width
   us=[]
   for i,piece in enumerate(pieces):
    key=f'{state(self.model,history)}:{phase(self.model,i,len(pieces))}'
    if piece[0]=='q':
     j=22*SIGNS.index(piece[1])+SIGNS.index(piece[2]);assert j<len(UNITS);u=UNITS[j];assert u not in self.common[key]
    else:u=self.inverse[key][piece[0]]
    us.append(u);history=(history+u)[-2:]
   word=''.join(us);assert units(word)==us,'Noncanonical shortcut';out.append(word)
  return out

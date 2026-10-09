from collections import Counter
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3].parent
RAW=ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_MULTIGRAPH_SHORTHAND_RAW_20261005.json'
TEACH=json.loads(RAW.read_text());T=TEACH['teaching_carrier'];S=TEACH['design']
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
SHORT='a o e i n d y s l m k t p f ch sh ckh cth cph cfh'.split()
CHARS={chr(97+i):[g] for i,g in enumerate(T['ordinary_signs'])}
CHARS.update({chr(116+i):['q',T['ordinary_signs'][i]] for i in range(7)})
CHARS.update({c:['y',T['rare_selectors'][i//8],T['rare_selectors'][i%8]] for i,c in enumerate(T['rare_characters_in_order'])})
BACK={tuple(v):k for k,v in CHARS.items()}
CUTS=dict(zip(S['shortcuts_in_order'],S['shortcut_selectors']));CUT_BACK={v:k for k,v in CUTS.items()}

def spelling(word):
 gs=[];i=0
 while i<len(word):
  opts=[s for s in CUTS if word.startswith(s,i)]
  if opts:
   s=max(opts,key=len);gs+=['r',CUTS[s]];i+=len(s)
  else:gs+=CHARS[word[i]];i+=1
 return gs

def unit(gs,i):
 g=gs[i]
 if g=='r':return CUT_BACK[gs[i+1]],i+2
 k=2 if g=='q' else 3 if g=='y' else 1
 return BACK[tuple(gs[i:i+k])],i+k

def unspell(gs):
 out='';i=0
 while i<len(gs):
  s,i=unit(gs,i);out+=s
 assert spelling(out)==gs,'noncanonical literal'
 return out

def groups(words):
 out=[];i=0
 while i<len(words):
  size=2 if words[i].isalpha() and len(words[i])<=3 and i+1<len(words) else 1
  out.append(words[i:i+size]);i+=size
 return out

def train(source):
 c=Counter(w for col in ['b4','w1'] for r in source[col] for w in r['words'])
 return sorted(c,key=lambda w:(-c[w],w))[:503]

def rankcode(index):
 if index<20:return [SHORT[index]]
 j=index-20;assert 0<=j<483
 return ['q',SIGNS[j//22],SIGNS[j%22]]

def literal(word):return ['r']+spelling(word)+['r','cfh']

class Writer:
 def __init__(self,mode,dictionary):
  self.mode=mode;self.words=dictionary;self.index={w:i for i,w in enumerate(dictionary)};self.history=[]
 def one(self,w):
  if self.mode=='A':return spelling(w)
  if self.mode=='B':return rankcode(self.index[w]) if w in self.index else literal(w)
  for d,past in enumerate(reversed(self.history[-503:]),1):
   if past==w:return rankcode(d-1)
  return literal(w)
 def paragraph(self,words):
  rows=[]
  for pair in groups(words):
   gs=[]
   for j,w in enumerate(pair):
    if self.mode=='A' and j:gs+=['r','cth']
    gs+=self.one(w);self.history.append(w)
   rows.append(''.join(gs))
  return rows

class Reader:
 def __init__(self,mode,dictionary):self.mode=mode;self.words=dictionary;self.history=[]
 def paragraph(self,rows):
  out=[]
  for gs in rows:
   pos=0;pair=[]
   if self.mode=='A':
    pieces=[[]]
    while pos<len(gs):
     if gs[pos:pos+2]==['r','cth']:pieces.append([]);pos+=2
     else:
      start=pos;_,pos=unit(gs,pos);pieces[-1]+=gs[start:pos]
    pair=[unspell(p) for p in pieces]
   else:
    while pos<len(gs):
     if gs[pos]=='r':
      pos+=1;pieces=[]
      while gs[pos:pos+2]!=['r','cfh']:
       start=pos;_,pos=unit(gs,pos);pieces+=gs[start:pos]
      pos+=2;w=unspell(pieces)
     else:
      if gs[pos]=='q':
       index=20+22*SIGNS.index(gs[pos+1])+SIGNS.index(gs[pos+2]);pos+=3
       assert index<503
      else:index=SHORT.index(gs[pos]);pos+=1
      w=self.words[index] if self.mode=='B' else self.history[-index-1]
     pair.append(w);self.history.append(w)
   assert 1<=len(pair)<=2
   out+=pair
   if self.mode=='A':self.history+=pair
  return out

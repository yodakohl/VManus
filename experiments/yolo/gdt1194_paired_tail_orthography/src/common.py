from pathlib import Path
import importlib.util,json,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';OLD=ROOT/'experiments/yolo/gdt1193_three_source_code_cycle'
spec=importlib.util.spec_from_file_location('cycle',OLD/'src/run.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);w=x.w;SIGNS=w.c.SIGNS;BOOKS=w.BOOKS;NQ=[g for g in SIGNS if g!='q']
def prepare():
 source,tables,targets,_,_,_=x.prepare();base=json.loads((OLD/'artifacts/RESULT.json').read_text())['selected'];codec=w.c.Codec(x.MODEL,tables,base['alphabets'],base['assignment']);cache=w.fast.Cache(codec,source);return source,tables,targets,base,codec,cache

def context(body,depth):
 if not body:return 0
 if depth==1 or len(body)==1:return 1+body[-1]
 return 4+3*body[-2]+body[-1]

def contract(body,mask):
 out=[];i=0
 while i<len(body):
  pair=3*body[i]+body[i+1] if i+1<len(body) else -1
  if pair>=0 and mask&(1<<pair):out.append(3+pair);i+=2
  else:out.append(body[i]);i+=1
 return out

def coverage(p):return set(p['initial'][:21]+['o']+p['body'][:3]+[p['body'][3+i] for i in range(9) if p['mask']&(1<<i)]+[g for row in p['final'] for g in row[:6]])==set(SIGNS)
def legal(p):return len(p['initial'])==22 and set(p['initial'])==set(SIGNS) and p['initial'][p['qpos']]=='q' and p['qpos']<7 and set(p['body'])==set(NQ) and all(set(row)==set(NQ) and 'y' in row[:6] for row in p['final']) and coverage(p)

class Writer:
 def __init__(self,inner,params):self.inner=inner;self.p=params;assert legal(params)
 def numeric(self,words):return self.inner.numeric(words)
 def glyph_row(self,row):
  p=self.p;body=[d-22 for d in row[1:-1]];out=[p['initial'][row[0]]]
  if out[0]=='q':out.append('o')
  out.extend(p['body'][i] for i in contract(body,p['mask']));out.append(p['final'][context(body,p['depth'])][row[-1]-25]);return out
 def render(self,rows):return [''.join(self.glyph_row(row)) for row in rows]
 def encode(self,words):return self.render(self.numeric(words))
 def decode(self,rows):
  p=self.p;old=[]
  for gs in rows:
   assert len(gs)>=2;initial=p['initial'].index(gs[0]);assert initial<21;start=1
   if gs[0]=='q':assert len(gs)>=3 and gs[1]=='o';start=2
   body=[]
   for g in gs[start:-1]:
    idx=p['body'][:12].index(g)
    if idx<3:body.append(idx)
    else:
     pair=idx-3;assert p['mask']&(1<<pair);body.extend(divmod(pair,3))
   cat=p['final'][context(body,p['depth'])][:6].index(gs[-1]);row=[initial]+[22+d for d in body]+[25+cat];assert self.glyph_row(row)==gs,'Noncanonical body';old.append(row)
  return self.inner.decode([w.m.glyphs(word) for word in self.inner.render(old)])

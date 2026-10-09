"""Known-source teaching codec, no manuscript decoding."""
import re
PALETTE=tuple('aoeindqysrlmktp');LITERALS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -'
H,F,G,A,T,K,Z,END=PALETTE[7:15];DIGITS=PALETTE[:7]
def require(ok):
 if not ok:raise ValueError('invalid allocation encoding')
def textcode(s):
 require(isinstance(s,str) and s and any(c!=' ' for c in s) and all(c in LITERALS for c in s))
 return ''.join(DIGITS[LITERALS.index(c)//7]+DIGITS[LITERALS.index(c)%7] for c in s)
def validate_block(b):
 require(set(b)=={'left','right','batch','unit','total','rows'})
 for key in ['left','right','batch','unit']:textcode(b[key])
 require(b['left']!=b['right']);require(type(b['total']) is int and 0<=b['total']<=9999);require(isinstance(b['rows'],list) and len(b['rows'])>0)
 for pair in b['rows']:require(isinstance(pair,list) and len(pair)==2 and all(type(x) is int and x>=0 for x in pair) and sum(pair)==b['total'])
def encode(blocks):
 require(isinstance(blocks,list) and len(blocks)>0);out=[]
 for b in blocks:
  validate_block(b);fields=[b[k] for k in ['left','right','batch','unit']]+[str(b['total'])]
  out.append(H+F.join(textcode(s) for s in fields)+G)
  for a,c in b['rows']:out.append(A+T*a+K+T*c+Z)
  out.append(END)
 return ''.join(out)
def layout(s,width=24):
 require(width>0);return '\n'.join(s[i:i+width] for i in range(0,len(s),width))
def decode(rendered):
 require(isinstance(rendered,str));s=''.join(c for c in rendered if c not in ' \t\r\n');require(s and all(c in PALETTE for c in s));i=0;blocks=[]
 def expect(c):
  nonlocal i
  require(i<len(s) and s[i]==c);i+=1
 def field(stop):
  nonlocal i
  out=[]
  while i<len(s) and s[i] in DIGITS:
   require(i+1<len(s) and s[i+1] in DIGITS);j=7*DIGITS.index(s[i])+DIGITS.index(s[i+1]);require(j<len(LITERALS));out.append(LITERALS[j]);i+=2
  expect(stop);v=''.join(out);require(v and any(c!=' ' for c in v));return v
 while i<len(s):
  expect(H);values=[field(F) for _ in range(4)]+[field(G)];require(re.fullmatch('0|[1-9][0-9]*',values[4]) is not None and len(values[4])<=4)
  b=dict(zip(['left','right','batch','unit'],values[:4]));b['total']=int(values[4]);b['rows']=[]
  while i<len(s) and s[i]==A:
   i+=1;a=0;c=0
   while i<len(s) and s[i]==T:a+=1;i+=1
   expect(K)
   while i<len(s) and s[i]==T:c+=1;i+=1
   expect(Z);b['rows'].append([a,c])
  expect(END);validate_block(b);blocks.append(b)
 return blocks

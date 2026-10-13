"""Source-free controls only; no native/source corpus or lexical meanings."""
from itertools import product
import json
C="ptkmns"; V="aiu"; H="H"
S=tuple(c+v for c in C for v in V)+tuple("V"+v for v in V)+(H,)
def encode(w):
 out=[];i=0
 while i<len(w):
  c=w[i]
  if c in C:
   if i+1<len(w) and w[i+1] in V:out.append(c+w[i+1]);i+=2
   else:out.extend((H,c+"a"));i+=1
  else:assert c in V;out.append("V"+c);i+=1
 return tuple(out)
def decode(z):
 out=[];i=0
 while i<len(z):
  x=z[i]
  if x==H:
   if i+1>=len(z) or z[i+1] not in tuple(c+"a" for c in C):return None
   out.append(z[i+1][0]);i+=2
  elif x in S:
   out.append(x[1:] if x.startswith("V") else x);i+=1
  else:return None
 return "".join(out)
def direct_legal(z):
 i=0;bare=False
 while i<len(z):
  x=z[i]
  if x==H:
   if i+1>=len(z) or z[i+1] not in tuple(c+"a" for c in C):return False
   bare=True;i+=2
  else:
   if bare and x.startswith("V"):return False
   bare=False;i+=1
 return True
if __name__=="__main__":
 a=b=0
 for n in range(5):
  for chars in product(C+V,repeat=n):
   w="".join(chars);assert decode(encode(w))==w;assert direct_legal(encode(w));a+=1
 for n in range(4):
  for z in product(S,repeat=n):
   w=decode(z);canonical=w is not None and encode(w)==z
   assert direct_legal(z)==canonical;b+=1
 print(json.dumps({"status":"PASS_SOURCE_FREE_ONLY","phoneme_words_including_empty":a,"output_sequences_including_empty":b,"examples":{w:encode(w) for w in ["patak","paak","p","pa","pai","pta"]},"noncanonical_same_decoding":{"H_pa_Va":decode(("H","pa","Va")),"canonical":encode("pa")}},indent=2))

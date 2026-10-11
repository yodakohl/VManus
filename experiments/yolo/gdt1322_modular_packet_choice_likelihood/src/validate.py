import hashlib,json
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def allseq(words,n):
 if n==0:return [()]
 return [s+(w,) for s in allseq(words,n-1) for w in words]
def value(word,key,m):
 n=0
 for g in word:n=(n+key[g])%m
 return n
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 f=read(B/'src/FIXTURE.json');result=read(B/'artifacts/RESULT.json');inv=read(B/'artifacts/INVERSE27.json');packets=[]
 for i in range(22):packets.append([i])
 for i in range(22):
  for j in range(22):packets.append([i,j])
 vals=[value(w,f['weights27'],27) for w in packets];counts=[vals.count(c) for c in range(27)];assert all(counts);expected=[{'packet':w,'residue':c,'source_character':f['alphabet27'][c],'conditional_probability':[1,counts[c]]} for w,c in zip(packets,vals)];assert inv==expected
 assert ''.join(f['alphabet27'][value(p,f['weights27'],27)] for p in f['example27'])=='a z';assert value([13,15],f['weights27'],27)==value([15,13],f['weights27'],27)==1;assert sum([13,15])==28
 bank=f['bank3'];records=read(B/'artifacts/SEQUENCES3.json');pi=[Fraction(*p) for p in f['pi3']];T=[[Fraction(*p) for p in row] for row in f['T3']];checked=0
 for name,key in f['keys3'].items():
  residues={w:value(w,key,3) for w in bank};sizes={c:sum(residues[w]==c for w in bank) for c in range(3)};rr=result['toy3'][name];assert rr['classes']=={str(c):[w for w in bank if residues[w]==c] for c in range(3)};assert rr['class_weights']=={str(c):sizes[c] for c in range(3)};expected=[]
  for n in [1,2,3]:
   mass=Fraction()
   for seq in allseq(bank,n):
    cs=[residues[w] for w in seq];p=pi[cs[0]]/sizes[cs[0]]
    for left,right in zip(cs,cs[1:]):p*=T[left][right]/sizes[right]
    expected.append({'packets':list(seq),'decoded':cs,'p':[p.numerator,p.denominator]});mass+=p;checked+=1
   assert mass==1 and rr['normalized_sequence_mass'][str(n)]==[1,1]
  assert records[name]==expected
  for seq in allseq(bank,2):
   p=Fraction(1)
   for w in seq:p*=Fraction(sizes[residues[w]],5)/sizes[residues[w]]
   assert p==Fraction(1,25)
  prior=pi[residues['b']];cipher=prior/sizes[residues['b']];assert rr['b_source_prior']==[prior.numerator,prior.denominator] and rr['b_cipher_likelihood']==[cipher.numerator,cipher.denominator]
 assert result['toy3']['K1']['b_cipher_likelihood']==[1,5] and result['toy3']['K2']['b_cipher_likelihood']==[3,10]
 r={'status':'PASS','bank27_inverse_alternatives':len(inv),'exact_toy_sequence_probabilities':checked,'iid_pooling_pairs':50,'scope':'Independent modular fold, recursive output enumeration and rational normalization; no native source, fitted key or language recovery.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()

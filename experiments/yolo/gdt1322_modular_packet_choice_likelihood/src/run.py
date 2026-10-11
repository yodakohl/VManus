import collections,hashlib,itertools,json
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def pair(x):return [x.numerator,x.denominator]
def classes(bank,weights,m,q):
 if len(bank)!=len(set(bank)) or any(not w for w in bank) or any(q[w]<=0 for w in bank):raise ValueError('bank')
 d={w:sum(weights[g] for g in w)%m for w in bank};z={c:sum(q[w] for w in bank if d[w]==c) for c in range(m)}
 if any(v==0 for v in z.values()):raise ValueError('uncovered')
 return d,z
def likelihood(seq,d,z,q,pi,T=None):
 if not seq:return F(1)
 cs=[d[w] for w in seq];p=pi[cs[0]]
 for i in range(1,len(cs)):p*=pi[cs[i]] if T is None else T[cs[i-1]][cs[i]]
 for w,c in zip(seq,cs):p*=F(q[w],z[c])
 return p

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 f=read(B/'src/FIXTURE.json');bank=[(g,) for g in range(22)]+list(itertools.product(range(22),repeat=2));weights=dict(enumerate(f['weights27']));q={w:1 for w in bank};d,z=classes(bank,weights,27,q);alphabet=f['alphabet27'];decoded=''.join(alphabet[d[tuple(w)]] for w in f['example27']);assert decoded==f['source27'];assert d[13,15]==d[15,13]==1
 inv=[{'packet':list(w),'residue':d[w],'source_character':alphabet[d[w]],'conditional_probability':pair(F(1,z[d[w]]))} for w in bank]
 for c in range(27):assert sum(F(*v['conditional_probability']) for v in inv if v['residue']==c)==1
 rejected=[]
 try:classes(['a'],{'a':1},3,{'a':1})
 except ValueError:rejected.append('gcd_one_but_missing_bank_classes')
 for packet in [(22,),(0,0,0)]:
  try:d[packet]
  except KeyError:rejected.append('invalid_packet_'+str(packet))
 try:
  for c in 'A':alphabet.index(c)
 except ValueError:rejected.append('outside_source_domain')
 assert len(rejected)==4
 bank3=f['bank3'];q3={w:1 for w in bank3};pi=[F(*v) for v in f['pi3']];T=[[F(*v) for v in row] for row in f['T3']];out={};records={}
 for key,kw in f['keys3'].items():
  dec,z3=classes(bank3,kw,3,q3);norm={};cases=[]
  for n in [1,2,3]:
   rows=[]
   for seq in itertools.product(bank3,repeat=n):
    p=likelihood(seq,dec,z3,q3,pi,T);rows.append(p);cases.append({'packets':seq,'decoded':[dec[w] for w in seq],'p':pair(p)})
   norm[str(n)]=pair(sum(rows));assert sum(rows)==1
  pooling_pi=[F(z3[c],len(bank3)) for c in range(3)]
  assert all(likelihood(seq,dec,z3,q3,pooling_pi)==F(1,25) for seq in itertools.product(bank3,repeat=2))
  out[key]={'classes':{str(c):[w for w in bank3 if dec[w]==c] for c in range(3)},'class_weights':z3,'b_source_prior':pair(pi[dec['b']]),'b_cipher_likelihood':pair(likelihood(['b'],dec,z3,q3,pi,T)),'normalized_sequence_mass':norm,'iid_pooling_each_pair':[1,25]};records[key]=cases
 assert F(*out['K1']['b_source_prior'])>F(*out['K2']['b_source_prior']);assert F(*out['K1']['b_cipher_likelihood'])<F(*out['K2']['b_cipher_likelihood'])
 save('INVERSE27.json',inv);save('SEQUENCES3.json',records);save('RESULT.json',{'status':'NORMALIZED_CHANNEL_AND_RANKING_COUNTEREXAMPLE','prototype27':{'bank_entries':len(bank),'covered_residues':27,'example_packets':f['example27'],'source':decoded,'positive_sum28_residue1':[[13,15],[15,13]],'rejected_invalid_cases':rejected},'toy3':out,'ceiling':'Source-free probability and inverse check only; no native fit or unknown-key recovery.'});print(json.dumps(out,indent=2))
if __name__=='__main__':main()

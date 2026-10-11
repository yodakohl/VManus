import collections,hashlib,json
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def words(n,prefix=()):
 if not n:yield prefix;return
 for v in range(5):yield from words(n-1,prefix+(v,))
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 f=read(R/'experiments/yolo/gdt1322_modular_packet_choice_likelihood/src/FIXTURE.json');bank=f['bank3'];keys=[];labels=[];classes=[]
 for a in range(3):
  for b in range(3):
   c=[];groups=collections.defaultdict(list)
   for index,w in enumerate(bank):
    v=0
    for ch in w:v=(v+{'a':a,'b':b}[ch])%3
    c.append(v);groups[v].append(index)
   if len(groups)==3:keys.append([a,b]);labels.append(c);classes.append(groups)
 result=read(B/'artifacts/RESULT.json');conf=read(B/'artifacts/CONFUSION.json');assert keys==result['keys_ab']==conf['keys_ab'];checked=0
 for case,curve in result['cases'].items():
  pi=[Fraction(*x) for x in f['pi3']] if case=='FIXED_MARKOV' else [Fraction(1,3)]*3
  trans=[[Fraction(*x) for x in row] for row in f['T3']] if case=='FIXED_MARKOV' else [[Fraction(1,3)]*3 for _ in range(3)]
  # Prefix recursion computes joint ciphertext probabilities using exact fractions.
  def output_walk(n,prefix=(),pr=None,previous=None):
   if len(prefix)==n:yield prefix,pr;return
   for w in range(5):
    nxt=[]
    for k in range(8):
     c=labels[k][w];source=pi[c] if pr is None else trans[previous[k]][c];nxt.append((Fraction(1) if pr is None else pr[k])*source/len(classes[k][c]))
    yield from output_walk(n,prefix+(w,),nxt,[labels[k][w] for k in range(8)])
  for row in curve:
   n=row['n'];mass=[Fraction() for _ in keys];mat=[[Fraction() for _ in keys] for _ in keys];message=Fraction();table=[[] for _ in keys];dig=hashlib.sha256();peak=Fraction();count=0
   for seq,probs in output_walk(n):
    count+=1;peak+=max(probs);winners=[k for k in range(8) if probs[k]==max(probs)];integer=[]
    for k in range(8):
     mass[k]+=probs[k];table[k].append(probs[k]);p=probs[k]*row['table_denominator'];assert p.denominator==1;integer.append(int(p))
     for j in winners:
      credit=probs[k]/len(winners);mat[k][j]+=credit
      if all(labels[k][i]==labels[j][i] for i in seq):message+=credit
    dig.update((','.join(str(x) for x in integer)+'\n').encode())
   assert mass==[1]*8 and count==row['ciphertexts'] and dig.hexdigest()==row['probability_table_sha256'];assert all(sum(x)==1 for x in mat)
   expected=[[Fraction(*x) for x in z] for z in conf['conditional_true_key_rows_predicted_key_columns'][case][str(n)]];assert mat==expected
   acc=sum(mat[k][k] for k in range(8))/8;assert acc==peak/8==Fraction(*row['key_accuracy']);assert message/8==Fraction(*row['whole_source_accuracy']);groups=[];used=set()
   for k in range(8):
    if k in used:continue
    group=[j for j in range(8) if table[j]==table[k]];used.update(group);groups.append([keys[j] for j in group])
   assert groups==row['distribution_classes'];assert len(groups)==(8 if case=='FIXED_MARKOV' else 3)
   if case=='UNIFORM_IID':assert acc<=Fraction(3,8)
   if n==1:assert acc==(Fraction(9,40) if case=='FIXED_MARKOV' else Fraction(5,24))
   checked+=count*8;print(case,n,'verified',flush=True)
 # Uniform IID equal single-packet laws imply equal laws at EVERY length.
 uniform=[]
 for k in range(8):uniform.append(tuple(Fraction(1,3*len(classes[k][c])) for c in labels[k]))
 sizes=sorted(collections.Counter(uniform).values());assert sizes==[2,2,4]
 # The known scaling equivalence is included, but does not exhaust the collision.
 for k,(a,b) in enumerate(keys):assert uniform[k]==uniform[keys.index([2*a%3,2*b%3])]
 out={'status':'PASS','exact_key_ciphertext_likelihoods':checked,'confusion_matrices':12,'uniform_iid_distribution_class_sizes':sizes,'all_length_exact_key_bound':[3,8],'scope':'Independent Fraction recursion, likelihood-table hashes and exact ML risk; source-free only.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

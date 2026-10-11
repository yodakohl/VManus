import hashlib,itertools,json,math
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];D=180;S=840
def read(p):return json.loads(p.read_text())
def frac(x):return [x.numerator,x.denominator]
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 f=read(R/'experiments/yolo/gdt1322_modular_packet_choice_likelihood/src/FIXTURE.json');bank=f['bank3'];keys=[];decoded=[];sizes=[]
 for a,b in itertools.product(range(3),repeat=2):
  labels=[sum(a if ch=='a' else b for ch in w)%3 for w in bank]
  if set(labels)!=set(range(3)):continue
  keys.append([a,b]);decoded.append(labels);sizes.append([labels.count(c) for c in range(3)])
 assert keys==[list(k) for k in itertools.product(range(3),repeat=2) if k!=(0,0)];results={};confusions={}
 for case in ['FIXED_MARKOV','UNIFORM_IID']:
  pi=[Fraction(*v) for v in f['pi3']] if case=='FIXED_MARKOV' else [Fraction(1,3)]*3
  trans=[[Fraction(*v) for v in row] for row in f['T3']] if case=='FIXED_MARKOV' else [[Fraction(1,3)]*3 for _ in range(3)]
  initial=[];steps=[]
  for k in range(8):
   v=[pi[c]*D/sizes[k][c] for c in decoded[k]];q=[[trans[c][d]*D/sizes[k][d] for d in decoded[k]] for c in decoded[k]];assert all(x.denominator==1 for x in v) and all(x.denominator==1 for row in q for x in row);initial.append([int(x) for x in v]);steps.append([[int(x) for x in row] for row in q])
  curve=[];confusions[case]={}
  for n in range(1,7):
   masses=[0]*8;table=[[] for _ in keys];mat=[[0]*8 for _ in keys];message=0;maxsum=0;digest=hashlib.sha256()
   for seq in itertools.product(range(5),repeat=n):
    probs=[]
    for k in range(8):
     p=initial[k][seq[0]]
     for i,j in zip(seq,seq[1:]):p*=steps[k][i][j]
     probs.append(p);masses[k]+=p;table[k].append(p)
    digest.update((','.join(map(str,probs))+'\n').encode());best=max(probs);wins=[k for k,p in enumerate(probs) if p==best];maxsum+=best;assert S%len(wins)==0;scale=S//len(wins);source=[tuple(decoded[k][i] for i in seq) for k in range(8)]
    for true in range(8):
     for guessed in wins:
      w=probs[true]*scale;mat[true][guessed]+=w
      if source[true]==source[guessed]:message+=w
   den=D**n;assert masses==[den]*8;assert all(sum(row)==S*den for row in mat)
   acc=Fraction(sum(mat[k][k] for k in range(8)),8*S*den);assert acc==Fraction(maxsum,8*den);msg=Fraction(message,8*S*den);classes=[];remaining=set(range(8))
   while remaining:
    k=min(remaining);group=[j for j in sorted(remaining) if table[j]==table[k]];classes.append([keys[j] for j in group]);remaining.difference_update(group)
   if case=='UNIFORM_IID':assert sorted(map(len,classes))==[2,2,4] and acc<=Fraction(3,8)
   else:assert len(classes)==8
   if n==1:assert acc==(Fraction(9,40) if case=='FIXED_MARKOV' else Fraction(5,24))
   curve.append({'n':n,'ciphertexts':5**n,'key_accuracy':frac(acc),'key_accuracy_decimal':float(acc),'whole_source_accuracy':frac(msg),'whole_source_accuracy_decimal':float(msg),'distribution_classes':classes,'probability_table_sha256':digest.hexdigest(),'table_denominator':den,'all_key_masses_one':True});confusions[case][str(n)]=[[frac(Fraction(x,S*den)) for x in row] for row in mat];print(case,n,float(acc),float(msg),'classes',len(classes),flush=True)
  results[case]=curve
 save('CONFUSION.json',{'keys_ab':keys,'conditional_true_key_rows_predicted_key_columns':confusions});save('RESULT.json',{'status':'TOY_DISTINGUISHABILITY_WITH_PRIOR_DEPENDENT_RECOVERY_LIMITS','keys_ab':keys,'cases':results,'uniform_iid_all_length_key_accuracy_bound':[3,8],'scope':'Source-free exact finite oracle-channel control; no native fit or full22drawing search.'})
if __name__=='__main__':main()

"""Exact source-free expectations and finite enumeration for two fixed merges."""
import collections,hashlib,itertools,json,math
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]

def merge(tokens,left,right,new):
 out=[];i=0
 while i<len(tokens):
  if i+1<len(tokens) and tokens[i]==left and tokens[i+1]==right:out.append(new);i+=2
  else:out.append(tokens[i]);i+=1
 return out

def notation(word):return merge(merge(list(word),'A','B','M'),'M','C','N')
def rational(x):return {'numerator':x.numerator,'denominator':x.denominator}

def main():
 for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
 stop=F(1,4);more=1-stop;a=b=F(1,4);c=F(1,2)
 raw_B=b/stop;raw_AB=more*a*b/stop;raw_ABC=more**2*a*b*c/stop
 vals={'raw_B':raw_B,'raw_AB':raw_AB,'raw_ABC':raw_ABC,
       'M_count':raw_AB-raw_ABC,'M_final':more*a*b,
       'B_count':raw_B-raw_AB,'B_final':b-more*a*b}
 vals['M_final_rate']=vals['M_final']/vals['M_count'];vals['B_final_rate']=vals['B_final']/vals['B_count']
 vals['first_merge_M_final_rate']=vals['M_final']/raw_AB
 N=8;den=16**N;weights=collections.Counter();cases=0;examples=[]
 for n in range(1,N+1):
  for word in itertools.product('ABC',repeat=n):
   tokens=notation(word);weight=3**(n-1)*2**word.count('C')*16**(N-n)
   weights['mass']+=weight;weights['M_count']+=weight*tokens.count('M');weights['B_count']+=weight*tokens.count('B')
   weights['M_final']+=weight*(tokens[-1]=='M');weights['B_final']+=weight*(tokens[-1]=='B');cases+=1
 for s in ['AB','ABC','ABCAB','AAB','ABAB','CABCA']:
  examples.append({'word':s,'first_pass':merge(list(s),'A','B','M'),'final_tokens':notation(s)})
 q=float(vals['M_final_rate']);r=float(vals['B_final_rate'])
 gain=q*math.log2(q/r)+(1-q)*math.log2((1-q)/(1-r))
 out={'status':'SOURCE_FREE_SELECTION_COUNTEREXAMPLE','infinite_expectations':{k:rational(v) for k,v in vals.items()},
 'M_own_vs_component_expected_bit_gain':gain,'finite_max_length':N,'finite_words':cases,
 'finite_weighted_expectations':{k:rational(F(v,den)) for k,v in weights.items()},'examples':examples,
 'scope':'Fixed merge-table IID counterexample for one boundary feature; not trained BPE, actual608gap attribution, native data or meanings.'}
 (P/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()

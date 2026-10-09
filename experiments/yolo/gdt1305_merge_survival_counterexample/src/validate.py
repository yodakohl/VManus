"""Independent streaming transducer and exact absorbing-state rewards."""
import collections,hashlib,itertools,json,math
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
PROB={'A':F(1,4),'B':F(1,4),'C':F(1,2)}

def step(state,char,second=True):
 pending,last=state;emitted=[]
 if pending=='A' and char=='B':return ('M',last),emitted
 if pending=='M' and char=='C' and second:return ('','N'),['N']
 if pending:emitted.append(pending)
 pending='A' if char=='A' else ''
 if char!='A':emitted.append(char)
 return (pending,emitted[-1] if emitted else last),emitted

def stream(word,second=True):
 state=('',None);out=[]
 for c in word:
  state,emitted=step(state,c,second);out+=emitted
 if state[0]:out.append(state[0])
 return out

def solve(A,b):
 matrix=[list(row)+[v] for row,v in zip(A,b)];n=len(matrix)
 for col in range(n):
  pivot=next(i for i in range(col,n) if matrix[i][col]);matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
  scale=matrix[col][col];matrix[col]=[v/scale for v in matrix[col]]
  for row in range(n):
   if row==col:continue
   scale=matrix[row][col]
   if scale:matrix[row]=[x-scale*y for x,y in zip(matrix[row],matrix[col])]
 return [row[-1] for row in matrix]

def infinite(second=True):
 initial=[step(('',None),c,second)[0] for c in PROB];states=list(dict.fromkeys(initial))
 for state in states:
  for char in PROB:
   nxt,_=step(state,char,second)
   if nxt not in states:states.append(nxt)
 index={s:i for i,s in enumerate(states)};n=len(states);stop=F(1,4);more=1-stop
 A=[[F(i==j) for j in range(n)] for i in range(n)]
 for i,state in enumerate(states):
  for char,pr in PROB.items():A[i][index[step(state,char,second)[0]]]-=more*pr
 results={}
 for wanted in ['M_count','B_count','M_final','B_final']:
  symbol=wanted[0];is_final=wanted.endswith('final');rhs=[]
  for state in states:
   pending,last=state
   end_reward=int((pending or last)==symbol) if is_final else int(pending==symbol)
   value=stop*end_reward
   if not is_final:
    value+=more*sum(pr*step(state,c,second)[1].count(symbol) for c,pr in PROB.items())
   rhs.append(value)
  future=solve(A,rhs)
  value=F(0)
  for char,pr in PROB.items():
   nxt,emitted=step(('',None),char,second)
   value+=pr*(future[index[nxt]]+(0 if is_final else emitted.count(symbol)))
  results[wanted]=value
 return results,n

def unpack(x):return F(x['numerator'],x['denominator'])

def main():
 for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
 r=json.loads((P/'artifacts/RESULT.json').read_text());recorded={k:unpack(v) for k,v in r['infinite_expectations'].items()}
 computed,nstates=infinite();baseline,_=infinite(False)
 for k,v in computed.items():assert recorded[k]==v,(k,v,recorded[k])
 assert recorded['M_final_rate']==computed['M_final']/computed['M_count']==F(2,5)
 assert recorded['B_final_rate']==computed['B_final']/computed['B_count']==F(1,4)
 assert recorded['first_merge_M_final_rate']==baseline['M_final']/baseline['M_count']==F(1,4)
 assert baseline['M_count']==recorded['raw_AB'] and computed['M_count']==baseline['M_count']-recorded['raw_ABC']
 assert computed['B_count']+baseline['M_count']==recorded['raw_B']==1
 # Recompute finite weighted statistics with direct per-word probabilities.
 totals=collections.defaultdict(F);cases=0;N=r['finite_max_length']
 for length in range(1,N+1):
  for word in itertools.product('ABC',repeat=length):
   pr=F(1,4)*F(3,4)**(length-1)
   for c in word:pr*=PROB[c]
   tokens=stream(word);s=''.join(word)
   # Separate count identities on raw strings; AB and ABC cannot self-overlap.
   assert tokens.count('M')==s.count('AB')-s.count('ABC')
   assert tokens.count('B')==s.count('B')-s.count('AB')
   totals['mass']+=pr
   for symbol in ['M','B']:
    totals[symbol+'_count']+=pr*tokens.count(symbol)
    totals[symbol+'_final']+=pr*int(tokens[-1]==symbol)
   cases+=1
 assert cases==r['finite_words']==9840
 assert dict(totals)=={k:unpack(v) for k,v in r['finite_weighted_expectations'].items()}
 assert totals['mass']==1-F(3,4)**N
 for example in r['examples']:
  assert stream(example['word'],False)==example['first_pass']
  assert stream(example['word'])==example['final_tokens']
 # Cross-entropy difference calculated separately, not by the runner's KL formula.
 q=F(2,5);p=F(1,4)
 cross=lambda prediction:-float(q)*math.log2(float(prediction))-float(1-q)*math.log2(float(1-prediction))
 assert abs(cross(p)-cross(q)-r['M_own_vs_component_expected_bit_gain'])<1e-12
 v={'status':'PASS','absorbing_transducer_states':nstates,'rational_reward_systems':8,'finite_words_checked':cases,'infinite_M_final_rate':'2/5','infinite_B_final_rate':'1/4','before_second_merge_M_final_rate':'1/4','scope':'Source-free mathematical/software check, no native effect attribution or independent decipherment.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))

if __name__=='__main__':main()

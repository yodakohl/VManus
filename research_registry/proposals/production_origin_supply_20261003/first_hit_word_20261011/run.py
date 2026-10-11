from pathlib import Path
from fractions import Fraction as F
import hashlib,itertools,json
B=Path(__file__).resolve().parent

def main():
 for name,digest in json.loads((B/'LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest
 # h[d]: expected draws from remaining residue d to first hit0; h[0]=0.
 a=[[F(22*int(i==j)) for j in range(1,27)]+[F(22)] for i in range(1,27)]
 for d in range(1,27):
  for step in range(1,23):
   rest=(d-step)%27
   if rest:a[d-1][rest-1]-=1
 for k in range(26):
  pivot=next(i for i in range(k,26) if a[i][k]);a[k],a[pivot]=a[pivot],a[k];v=a[k][k];a[k]=[x/v for x in a[k]]
  for i in range(26):
   if i!=k:
    v=a[i][k];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
 h=[F(0)]+[row[-1] for row in a];means=[F(1)+sum(h[(-step)%27] for step in range(1,23))/22]+h[1:];assert all(v>=22 for v in means) and means[0]==27
 accepted=0;rejected=0
 def decode(w):
  totals=[];s=0
  for step in w:s=(s+step)%27;totals.append(s)
  if totals[-1] in totals[:-1]:return None
  return totals[-1]
 for n in range(1,4):
  for w in itertools.product(range(1,23),repeat=n):
   c=decode(w)
   if c is None:rejected+=1
   else:
    s=0
    for i,step in enumerate(w):s=(s+step)%27;assert (s==c)==(i==len(w)-1)
    accepted+=1
 examples={}
 for c in range(27):
  w=[c] if 1<=c<=22 else [5,22] if c==0 else [c-22,22];assert decode(w)==c;examples[str(c)]=w
 assert decode([1,5,22]) is None and decode([5,1,22])==1
 out={'status':'VALID_CHANNEL_HIGH_EXPECTED_LENGTH_NOT_SELECTED','means_exact':[str(v) for v in means],'means_decimal':[float(v) for v in means],'minimum_expected_length':float(min(means)),'maximum_expected_length':float(max(means)),'universal_hazard_bound':'1/22','universal_mean_lower_bound':22,'target_zero_expected_length':27,'paths_length1to3_accepted':accepted,'paths_length1to3_rejected':rejected,'constructive_targets':examples,'order_sensitive_witness':{'invalid':[1,5,22],'valid':[5,1,22],'decoded_target':1},'native_data_used':False};(B/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k not in ['means_exact','means_decimal','constructive_targets']})
if __name__=='__main__':main()

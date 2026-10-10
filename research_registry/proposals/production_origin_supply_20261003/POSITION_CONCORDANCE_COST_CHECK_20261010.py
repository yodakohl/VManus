"""Small checks of authored examples and the cost arithmetic; no corpus run."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent
raw=json.loads((B/'SELF_CONTAINED_POSITION_CONCORDANCE_RAW_20261010.json').read_text())
checks=[]
for ex in raw['hand_examples']:
 fields=ex['complete_integer_fields'];it=iter(fields);N=next(it);L=next(it);ns=[next(it) for _ in range(L)];D=next(it);assert sum(ns)==N and L>=1
 positions={};tokens=[];A=0
 for _ in range(D):
  m=next(it);assert m>0;chars=[next(it) for _ in range(m)];assert all(33<=c<=126 for c in chars);word=''.join(map(chr,chars));k=next(it);ps=[next(it) for _ in range(k)];assert k>0 and ps==sorted(set(ps));tokens.append(word);A+=m
  for p in ps:assert 1<=p<=N and p not in positions;positions[p]=word
 assert next(it,None) is None and sorted(positions)==list(range(1,N+1)) and tokens==sorted(set(tokens))
 lines=[];i=1
 for n in ns:lines.append(' '.join(positions[j] for j in range(i,i+n)));i+=n
 assert '\n'.join(lines)==ex['source'];M=len(fields);assert M==N+A+2*D+L+3 and max(fields)<=max(M,127)
 for val,ds in ex.get('base22_examples',{}).items():
  assert all(0<=d<22 for d in ds) and (len(ds)==1 or ds[0]!=0);out=0
  for d in ds:out=out*22+d
  assert out==int(val)
 checks.append({'groups':M,'recovered':True,'max_field':max(fields)})
assert 22**10==26559922791424
r={'status':'PASS','examples':checks,'eleven_digit_minimum':22**10,'scope':'Finite authored-example inverses and arithmetic only; proof of the general field bound is in POSITION_CONCORDANCE_COST_20261010.json. No encoder, native test or handwriting validation.'}
(B/'POSITION_CONCORDANCE_COST_VALIDATION_20261010.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

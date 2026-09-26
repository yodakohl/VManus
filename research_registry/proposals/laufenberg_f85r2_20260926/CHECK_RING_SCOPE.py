#!/usr/bin/env python3
"""Enumerate RAW559's declared finite model; no manuscript/decoder input."""
from itertools import product
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
card=B/'ideas/29_ring_state_outcome_modal_scope.json'
axis=[(False,False),(True,False),(True,True)]
states=list(product(axis,repeat=2))
profiles=[tuple(states[i] for i in range(9) if mask>>i&1) for mask in range(1,512)]
def terms(R,q):
 return tuple(v for j in range(2) for v in (not q(s[j][0] for s in R),not q(not s[j][1] for s in R)))
def counts(rs):
 out={'profiles':len(rs)}
 for name,q in [('ALL',all),('SOME',any)]:
  vs=[terms(r,q) for r in rs]
  out[name]={'heat_pair':sum(a and b for a,b,c,d in vs),'moisture_pair':sum(c and d for a,b,c,d in vs),'all_four':sum(all(v) for v in vs)}
 return out
sets={'unrestricted_declared':profiles,'single_outcome':[r for r in profiles if len(r)==1],'both_qualities_present_in_every_outcome':[r for r in profiles if all(all(axis[0] for axis in s) for s in r)]}
result={'status':'CONDITIONAL_MODEL_ENUMERATION_NOT_MANUSCRIPT_TEST','raw_card_sha256':hashlib.sha256(card.read_bytes()).hexdigest(),'results':{k:counts(v) for k,v in sets.items()},'semantic_input':'Only the RAW finite truth tables. No target rows, image data or inferred ownership.','source_restriction':'Conditional: all evaluated states remain living-person states inheriting heat/moisture contributions; this is not observed target data.','claim_ceiling':'No word confirmation, source identity, statistical significance or target-level rejection.'}
(B/'RING_SCOPE_ENUMERATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert result['results']['unrestricted_declared']['ALL']['all_four']==322
assert result['results']['unrestricted_declared']['SOME']['all_four']==0
assert result['results']['both_qualities_present_in_every_outcome']['profiles']==15
assert result['results']['both_qualities_present_in_every_outcome']['ALL']['all_four']==0

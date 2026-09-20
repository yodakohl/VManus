#!/usr/bin/env python3
"""No manuscript input: exhaustive short fixtures and generated two-tense codes."""
import itertools,json,random
from datetime import datetime,timezone
from pathlib import Path
from core import factor,ORDERS,length_failure
from validate import independently_factor,canon
E=Path(__file__).resolve().parents[1]
def make(rs,ps,t,o):return [[''.join(dict(R=r,P=p,T=t)[k] for k in o) for r in rs] for p in ps]
def check(m):
 for o in ORDERS:assert canon(factor(m,o))==canon(independently_factor(m,o)),(m,o)
count=0
for words in itertools.product(['a','b','aa','ab','ba','bb'],repeat=4):
 check([list(words[:2]),list(words[2:])]);count+=1
rng=random.Random(998)
strings=['','a','b','aa','ab','ba','bb','aaa','aab','aba','abb','baa','bab','bba','bbb']
positive=0;corrupted=0;empty_person=0;empty_tense=0
for o in ORDERS:
 for _ in range(12):
  rs=rng.sample(strings[1:],3);ps=rng.sample(strings,6)
  for t in rng.sample(strings,2):
   m=make(rs,ps,t,o);assert length_failure(m) is None;check(m)
   expected=dict(order=o,roots=rs,persons=ps,tense=t);assert expected in factor(m,o)
   positive+=1;empty_person+=int('' in ps);empty_tense+=int(t=='')
   changed=[row[:] for row in m];changed[2][1]+='x';assert length_failure(changed) is not None;check(changed);corrupted+=1
out=dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),exhaustive_2x2_matrices=count,orders_per_matrix=6,generated_6x3_positive=positive,one_cell_mutations=corrupted,positive_empty_person=empty_person,positive_empty_tense=empty_tense,manuscript_input_accessed=False,meaning_or_significance=False)
(E/'artifacts/PREFLIGHT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))

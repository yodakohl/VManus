from itertools import product
from pathlib import Path
from datetime import datetime,timezone
import json
from model import models,direct
from validate import parse

M=models('abc');words=[w for n in range(1,6)for w in product('abc',repeat=n)]
roundtrips=comparisons=0
for m in M:
 g=m['missing_singleton'];long=tuple(m['compound'])
 for source in words:
  output=tuple(x for ch in source for x in(long if ch==g else(ch,)))
  assert parse(output,g,long)==source
  roundtrips+=1
 for w in words:
  d=parse(w,g,long);k=direct(w,m)
  assert (d is None)==(k is None)
  if d is not None:assert d.count(g)==k
  comparisons+=1
suffix={'missing_singleton':'b','companion':'a','side':'before'}
assert direct(tuple('aababa'),suffix)==2
assert parse(tuple('aababa'),'b',tuple('ab'))==tuple('abba')
double={'missing_singleton':'a','companion':'a','side':'after'}
assert direct(tuple('aabaa'),double)==2 and direct(tuple('aaba'),double)is None
out={'status':'PASS','codebooks':len(M),'source_roundtrips':roundtrips,'output_comparisons':comparisons,'completed_utc':datetime.now(timezone.utc).isoformat(),'named':['suffix overlap ABBA to aababa','even versus odd doubled-sign runs']}
Path('experiments/yolo/gdt1237_one_compound_letter_exceptions/artifacts/FIXTURES.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

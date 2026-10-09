#!/usr/bin/env python3
"""Source-free pre-output checks of the existing writer's necessary bound."""
from pathlib import Path
from itertools import product
import importlib.util,json,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2]
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1194_paired_tail_orthography/src'))
import common as old
p=json.loads((ROOT/'experiments/yolo/gdt1195_final_table_feasibility_witness/artifacts/RESULT.json').read_text())['best']['params']
w=old.Writer(None,p)
rows=[w.glyph_row([a,25+f]) for a in range(21) for f in range(6)]
two=[row for row in rows if len(row)==2]
assert len(rows)==126 and len(two)==120 and len({row[-1] for row in two})==6
assert {row[-1] for row in two}==set(p['final'][0][:6])
cases=0
for n in range(5):
 for body in product(range(3),repeat=n):
  for mask in range(512):
   compressed=old.contract(body,mask);expanded=[]
   for c in compressed:
    if c<3:expanded.append(c)
    else:expanded.extend(divmod(c-3,3))
   assert expanded==list(body)
   assert (len(compressed)==0)==(n==0)
   for depth in (1,2):
    if n==0:assert old.context(body,depth)==0
   cases+=1
assert cases==61952
result={'status':'PASS','relaxed_empty_body_rows':len(rows),'two_glyph_rows':len(two),'two_glyph_final_types':len({r[-1] for r in two}),'mask_body_cases':cases,'native_rows_read':0,'scope':'Finite fixtures plus manual non-erasing-loop proof; dictionary/state constraints relaxed.'}
(D/'artifacts/PRE_OUTPUT_FIXTURES.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

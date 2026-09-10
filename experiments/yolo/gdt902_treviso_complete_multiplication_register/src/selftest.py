#!/usr/bin/env python3
import itertools,json,random
from pathlib import Path
from domains import build
def main():
 base=Path(__file__).resolve().parents[1];source=json.loads((base/'artifacts/SOURCE_INPUT.json').read_text())
 digits=dict(zip('0123456789','ABCDEFGHIJ'))
 code={a:('mul' if a=='OP:fia' else 'eq') if a.startswith('OP:') else ''.join(digits[c] for c in a[4:]) for a in source['atoms']}
 paragraphs=[{'words':['background']+[code[a] for a in r['sequence']]+['background']} for r in source['records']]
 r=build(source,paragraphs);assert r['status']=='FULL_DECIMAL_SOLVER_REQUIRED' and all(code[a] in r['domains'][a] for a in code)
 assert any(p['fia']=='mul' and p['fa']=='eq' for p in r['operator_pairs'])
 assert build(source,paragraphs[:7])['status']=='CAPACITY_STOP'
 toy={'records':[{'row_count':1,'sequence':['OP:fia','OP:fa']},{'row_count':2,'sequence':['OP:fia','OP:fa']*2}],'atoms':['OP:fa','OP:fia']}
 assert build(toy,[{'words':['f','e']},{'words':['e','f','e','f']}])['status']=='OPERATOR_PAIR_DOMAINS_UNSAT'
 rng=random.Random(902)
 for _ in range(100):
  ps=[{'words':[rng.choice('fen') for _ in range(rng.randint(1,7))]} for j in range(3)]
  words=set(w for p in ps for w in p['words']);sat=False
  for f,e in itertools.permutations(words,2):
   if all(any([w for w in p['words'] if w in (f,e)]==[f,e]*n for p in ps) for n in [1,2]):sat=True
  status=build(toy,ps)['status'];assert (status=='FULL_DECIMAL_SOLVER_REQUIRED')==sat
 print(json.dumps({'status':'PASS','checks':['complete220field_decimal_witness_preserved','capacity','equal_counts_incompatible_operator_order'],'exhaustive_operator_oracle_cases':100}))
if __name__=='__main__':main()

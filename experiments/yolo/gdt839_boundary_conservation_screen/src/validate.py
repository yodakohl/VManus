import argparse,itertools,json
from collections import defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def census(rows):
 buckets=defaultdict(list)
 for x in rows:
  assert ''.join(x['atoms'][:x['split']])==x['words'][0]
  assert ''.join(x['atoms'][x['split']:])==x['words'][1]
  buckets[''.join(x['words'])].append(x)
 pairs=[]
 for group in buckets.values():
  for a,b in itertools.combinations(group,2):
   if a['leaf']!=b['leaf'] and a['atoms']==b['atoms'] and 0<abs(a['split']-b['split'])<4:pairs.append(sorted([a['id'],b['id']]))
 return sorted(pairs)
p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
if a.self_test:
 rows=[dict(id='a',leaf='1',atoms=list('abcdefgh'),split=3,words=['abc','defgh']),dict(id='b',leaf='2',atoms=list('abcdefgh'),split=4,words=['abcd','efgh'])]
 assert census(rows)==[['a','b']]
 rows[1]['leaf']='1';assert census(rows)==[]
 rows[1]['leaf']='2';rows[1]['split']=3;rows[1]['words']=['abc','defgh'];assert census(rows)==[]
 name='FIXTURE_VALIDATION.json';obj=dict(status='PASS',fixtures=3)
else:
 rows=json.loads((E/'artifacts/OCCURRENCES.json').read_text());pairs=census(rows)
 assert pairs==json.loads((E/'artifacts/PAIRS.json').read_text())
 assert len(pairs)==json.loads((E/'artifacts/RESULT.json').read_text())['qualifying_pairs']
 name='VALIDATION.json';obj=dict(status='PASS',independent_pair_census=True,shared_source_extraction=True,occurrences=len(rows),pairs=len(pairs))
data=json.dumps(obj,sort_keys=True,indent=2)+'\n';path=E/'artifacts'/name
if a.check:assert path.read_text()==data
else:path.write_text(data)
print(data)

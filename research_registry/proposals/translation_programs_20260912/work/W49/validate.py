import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path(__file__).parent;s=json.loads((D/'SPEC.json').read_text())
def rows(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
pairs=rows(s['pairs']);pids={r['paragraph'] for r in pairs if r['status']=='CONDITIONAL_TYPE_DIFFERENCE'}
features={f['form'] for f in json.loads(Path(s['features']).read_text())['features'] if f['axis']=='thermal' and f['kind']=='STANDALONE'}
flat=rows(s['flat']);aa=rows(s['arguments']);rr=rows(D/'ALL_THERMAL_BINDINGS.tsv');rules=json.loads(Path(s['rules']).read_text());mats=set(rules['material_roles']);acts=set(rules['action_roles'])
expected={(r['branch'],r['edition'],r['paragraph'],g,r['id']) for r in flat if r['paragraph'] in pids and r['role']=='STATE' and r['form'] in features for g in ['B','J','M']}
assert expected=={tuple(r[k] for k in ['branch','edition','paragraph','grammar','mention']) for r in rr} and len(rr)==len(expected)
for r in rr:
 key=(r['branch'],r['edition'],r['paragraph']);fs=[x for x in flat if (x['branch'],x['edition'],x['paragraph'])==key];by={x['id']:x for x in fs};x=by[r['mention']];pos=int(x['offset'])
 prev=[y for y in fs if y['locus']==x['locus'] and y['role'] in acts and int(y['offset'])<pos];nxt=[int(y['offset']) for y in fs if y['locus']==x['locus'] and y['role'] in acts and int(y['offset'])>pos]
 lo=int(prev[-1]['offset']) if prev else -1;hi=min(nxt,default=10**9)
 mm=[y for y in fs if y['locus']==x['locus'] and y['role'] in mats and lo<int(y['offset'])<hi];left=[y for y in mm if int(y['offset'])<pos];right=[y for y in mm if int(y['offset'])>pos]
 patient=(left[-1] if left else right[0] if right else {}).get('id','')
 if not patient and prev:
  a=next(a for a in aa if (a['branch'],a['edition'],a['paragraph'],a['grammar'],a['operation'])==key+(r['grammar'],prev[-1]['id']));patient=a['patient']
 assert r['patient']==patient and r['patient_form']==(by[patient]['form'] if patient else '')
 assert r['patient_form']!='cheo' and r['eligible']=='False'
res=json.loads((D/'RESULT.json').read_text());assert res['eligible_later_requirements']==0 and res['thermal_binding_cases']==len(rr)
c=rows(D/'CANDIDATES.tsv');assert {x['identity'] for x in c}=={'SAME','NEW'} and all(x['decision']=='NO_BOUND_THERMAL_TEST' for x in c)
out=dict(status='PASS',complete_thermal_cases=len(rr),patient_forms=dict(Counter(r['patient_form'] or 'UNBOUND' for r in rr)),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

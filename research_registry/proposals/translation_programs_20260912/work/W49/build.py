import ast,csv,json,hashlib
from pathlib import Path
D=Path(__file__).parent;s=json.loads((D/'SPEC.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def rows(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
def table(n,rr,cols):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
pairs=rows(s['pairs']);selected=[r for r in pairs if r['status']=='CONDITIONAL_TYPE_DIFFERENCE'];pids={r['paragraph'] for r in selected};allflat=rows(s['flat']);allargs=rows(s['arguments'])
rules=read(s['rules']);ACT=set(rules['action_roles']);MAT=set(rules['material_roles'])
fn=next(n for n in ast.parse(Path(s['function']).read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='requal');exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_W13_requal','exec'))
features={f['form']:f for f in read(s['features'])['features'] if f['kind']=='STANDALONE' and f['axis']=='thermal'}
result=[];inventory=[];keys=sorted({(r['branch'],r['edition'],r['paragraph']) for r in allflat if r['paragraph'] in pids})
for b,ed,pid in keys:
 flat=[dict(r,index=int(r['index']),offset=int(r['offset'])) for r in allflat if (r['branch'],r['edition'],r['paragraph'])==(b,ed,pid)];by={r['id']:r for r in flat}
 for g in ['B','J','M']:
  aa=[r for r in allargs if (r['branch'],r['edition'],r['paragraph'],r['grammar'])==(b,ed,pid,g)]
  targets=[r for r in selected if (r['branch'],r['paragraph'],r['grammar'])==(b,pid,g)]
  for x in flat:
   if x['role']!='STATE' or x['form'] not in features:continue
   f=features[x['form']];q=requal(dict(mention=x['id'],kind='STANDALONE',form=x['form'],axis='thermal',value=f['value']),flat,aa)
   # Corresponding target location is the same locus/index only within selected IT;
   # alternate rows are fully retained without pretending index alignment.
   eligible=any(ed==t['edition'] and q['patient_form']==t['sheey_material'] and q['patient'] and x['offset']>max(by[t['sheey']]['offset'],by[t['sheey_patient']]['offset']) for t in targets)
   result.append(dict(branch=b,edition=ed,paragraph=pid,grammar=g,**q,eligible=eligible))
  inventory.append(dict(branch=b,edition=ed,paragraph=pid,grammar=g,groups=len(flat)))
table('ALL_THERMAL_BINDINGS.tsv',result,['branch','edition','paragraph','grammar','mention','kind','form','axis','value','patient','patient_form','rule','debts','eligible'])
table('PARAGRAPHS.tsv',inventory,['branch','edition','paragraph','grammar','groups'])
n=sum(r['eligible'] for r in result)
res=dict(paragraph_readings=len({(ed,pid) for b,ed,pid in keys}),worlds=len(inventory),thermal_binding_cases=len(result),eligible_later_requirements=n,state_simulation='NOT_STARTED_NO_CAPACITY' if n==0 else 'REQUIRED_NOT_YET_RUN',independent_meaning_confirmations=0)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n')
table('CANDIDATES.tsv',[dict(identity=x,requirements=n,decision='NO_BOUND_THERMAL_TEST' if n==0 else 'NEEDS_REPLAY') for x in ['SAME','NEW']],['identity','requirements','decision']);print(json.dumps(res,indent=2))

import csv,json,hashlib
from collections import defaultdict,Counter
from pathlib import Path
D=Path(__file__).parent;s=json.loads((D/'SPEC.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def rows(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ctx=read(s['context']);flats=rows(D/'SOURCE_FLAT.tsv');args=rows(D/'ARGUMENTS.tsv');pairs=rows(D/'ALL_PAIRS.tsv');uses=rows(D/'ALL_TYPED_USES.tsv');targets=rows(D/'TARGETS.tsv')
roles={b:{r['form']:r['role'] for r in rows(p)} for b,p in s['roles'].items()};source={}
for b in roles:
 for p in ctx['paragraphs']:
  key=(b,p['edition'],p['id']);rr=[r for r in flats if (r['branch'],r['edition'],r['paragraph'])==key]
  expected=[(l['locus']+':'+str(i),word) for l in p['lines'] for i,word in enumerate(l['words'],1)]
  assert [(r['id'],r['form']) for r in rr]==expected
  assert all(r['role']==roles[b].get(r['form'],'OPEN') and int(r['offset'])==i for i,r in enumerate(rr));source[key]={r['id']:r for r in rr}
ag=defaultdict(list)
for a in args:
 k=(a['branch'],a['edition'],a['paragraph']);ss=source[k];assert ss[a['operation']]['form']==a['form']
 for f in ['patient','coingredient']:
  if a[f]:assert ss[a[f]]['role'] in read(s['rules'])['material_roles']
 assert int(a['completion'])==max(int(ss[q]['offset']) for q in [a['operation'],a['patient'],a['coingredient']] if q)
 ag[k+(a['grammar'],)].append(a)
expected_pairs={};expected_targets=set();expected_uses={}
for k,aa in ag.items():
 ss=source[k[:3]];sh=[a for a in aa if a['form']=='sheey'];qs=[a for a in aa if a['form']=='qokeor']
 assert {a['operation'] for a in aa}=={i for i,r in ss.items() if r['role'] in read(s['rules'])['action_roles']}
 for a in sh:
  expected_targets.add(k+(a['operation'],))
  for q in qs:
   if int(q['completion'])<=int(a['completion']):continue
   same=bool(a['patient'] and q['patient'] and a['patient_form']==q['patient_form']);initial=q['patient_form'] in s['extracts']
   status='MISSING_PATIENT' if not a['patient'] or not q['patient'] else 'DIFFERENT_MATERIAL' if not same else 'ALREADY_EXTRACT' if initial else 'CONDITIONAL_TYPE_DIFFERENCE'
   expected_pairs[k+(a['operation'],q['operation'])]=(a,q,status,same,initial)
 for q in qs:
  same=any(a['patient'] and q['patient'] and a['patient_form']==q['patient_form'] and int(a['completion'])<int(q['completion']) for a in sh)
  expected_uses[k+(q['operation'],)]=('EXTRACT' if q['patient_form'] in s['extracts'] else 'UNKNOWN','EXTRACT' if q['patient_form'] in s['extracts'] or same else 'UNKNOWN')
assert len(pairs)==len(expected_pairs)
for r in pairs:
 k=tuple(r[x] for x in ['branch','edition','paragraph','grammar']);a,q,status,same,initial=expected_pairs[k+(r['sheey'],r['qokeor'])];ss=source[k[:3]]
 assert r['status']==status and r['W_type']==('EXTRACT' if initial else 'UNKNOWN') and r['E_type']==('EXTRACT' if initial or same else 'UNKNOWN')
 assert r['sheey_debts']==a['debts'] and r['qokeor_debts']==q['debts']
 assert r['unread_between']==';'.join(i for i,x in ss.items() if int(a['completion'])<int(x['offset'])<int(q['completion']) and x['role']=='OPEN')
 assert r['intervening_actions']==';'.join(x['operation'] for x in ag[k] if same and x['patient_form']==a['patient_form'] and int(a['completion'])<int(x['completion'])<int(q['completion']))
assert {tuple(r[x] for x in ['branch','edition','paragraph','grammar','operation']) for r in targets}==expected_targets
assert len(uses)==len(expected_uses)
for r in uses:assert (r['W_type'],r['E_type'])==expected_uses[tuple(r[x] for x in ['branch','edition','paragraph','grammar','qokeor'])]
missing=rows(D/'NO_PARAGRAPH_CAPACITY.tsv');assert missing==[r for r in rows(s['occurrences']) if r['paragraph']=='NO_COMPLETE_PARAGRAPH']
res=read(D/'RESULT.json');assert res['statuses']==dict(Counter(r['status'] for r in pairs))
assert res['different_type_uses']==sum(r['W_type']!=r['E_type'] for r in uses)
out=dict(status='PASS',paragraphs=len(ctx['paragraphs']),source_role_rows=len(flats),action_rows=len(args),target_cases=len(targets),typed_use_cases=len(uses),all_forward_pairs=len(pairs),scope='source completeness and independent pair/type consequences; inherited argument parser not independently reimplemented',independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
cols=['edition','paragraph','sheey','sheey_material','qokeor','qokeor_material','status','NEW_continuity'];project=defaultdict(list)
for r in pairs:project[tuple(r[c] for c in cols)].append(r['branch']+'/'+r['grammar'])
groups=rows(D/'PREDICTION_GROUPS.tsv');assert len(groups)==len(project)
for r in groups:assert r['dependent_variants']==';'.join(project[tuple(r[c] for c in cols)])
leadids={r['paragraph'] for r in pairs if r['status']=='CONDITIONAL_TYPE_DIFFERENCE'};reader=(D/'READING.md').read_text()
for p in ctx['paragraphs']:
 if p['id'] in leadids:
  for l in p['lines']:assert l['locus']+' `'+ ' '.join(l['words'])+'`' in reader
out['projection_groups']=len(groups);out['complete_lead_readers']=sum(p['id'] in leadids for p in ctx['paragraphs'])
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')

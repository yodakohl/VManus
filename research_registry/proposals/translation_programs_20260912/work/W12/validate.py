"""Separate expected-consequence reconstruction; never imports the builder."""
import csv,json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(p):return json.loads(p.read_text())
s=js(E/'SPEC.json')
for f in s['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];rules=js(W/'W05/SPEC.json')
lex={r['form']:r['role'] for r in rows(W/'W02/LEXICON.tsv')}
for w,o in rules['word_overrides'].items():lex[w]=o['role']
flat={};all_targets=set()
for edition,ll in alt.items():
 m={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];f=[]
  for l in p['lines']:
   loc=l['locus'];assert not loc.startswith('f84')
   for i,g in enumerate(m[loc]['groups'],1):
    word=g['ivtff_group_raw'];f.append((loc+':'+str(i),loc,word,lex.get(word,'OPEN')))
    if word=='qokeeo':all_targets.add((edition,loc+':'+str(i)))
  flat[(edition,p['id'])]=f
assert len(all_targets)==6
baseline={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W05/ARGUMENTS.tsv')}
actual=rows(E/'ARGUMENTS.tsv');assert len(actual)==len(baseline)*3+18
index={};deltas=0
for a in actual:
 key=(a['edition'],a['variant'],a['operation']);uid=(a['model'],)+key;assert uid not in index;index[uid]=a
 if key not in baseline:
  assert a['model']=='R' and (a['edition'],a['operation']) in all_targets
  continue
 expected=baseline[key].copy()
 if a['model']!='U':
  expected['debts']=';'.join(d for d in expected['debts'].split(';') if d not in ('UNREAD_BETWEEN:f99r.50:1','UNREAD_BETWEEN:f99r.50:5'))
  if expected['debts']!=baseline[key]['debts']:deltas+=1
 for k in ('patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption'):assert a[k]==expected[k],(uid,k)
assert deltas==54
trs=rows(E/'TARGETS.tsv');assert len(trs)==54
for model in ('U','R','C'):
 for v in ('B','J','M'):assert {(t['edition'],t['mention']) for t in trs if t['model']==model and t['variant']==v}==all_targets
for t in trs:
 f=flat[(t['edition'],t['paragraph'])];positions={x[0]:i for i,x in enumerate(f)};at=positions[t['mention']]
 if t['model']=='U':assert not t['patient'] and not t['antecedent'];continue
 if t['model']=='R':
  # Both target lines have no material at all; the unchanged rule must carry last material.
  assert not any(x[3] in rules['material_roles'] for x in f if x[1]=='f99r.50')
  before=[x for x in f[:at] if x[3] in rules['material_roles']];assert before
  patient=before[-1];assert t['patient']==patient[0] and t['patient_form']==patient[2]
  assert not t['antecedent']
  a=index[('R',t['edition'],t['variant'],t['mention'])]
  expected_gaps=[x[0] for x in f[positions[patient[0]]+1:at] if x[3]=='OPEN' and x[2]!='qokeeo']
  assert a['rule']=='PARAGRAPH_CARRY' and not a['coingredient']
  assert a['debts']==';'.join(['UNREAD_BETWEEN:'+x for x in expected_gaps]+['IMPLICIT_SUBJECT_CONTINUATION'])
 else:
  before=[x for x in f[:at] if x[3] in rules['action_roles'] and x[2]!='qokeeo'];assert before
  op=before[-1];assert t['antecedent']==op[0] and t['antecedent_form']==op[2]
  a=index[('C',t['edition'],t['variant'],op[0])];assert t['patient']==a['patient'] and t['patient_form']==a['patient_form']
  expected=['ANTECEDENT_UNREAD_BETWEEN:'+x[0] for x in f[positions[op[0]]+1:at] if x[3]=='OPEN' and x[2]!='qokeeo']
  if op[1]!=f[at][1]:expected+=['CROSS_LINE_ACTION_CARRY']
  expected+=['ONGOING_ACTION_NOT_ESTABLISHED']+['INHERITED:'+d for d in a['debts'].split(';') if d]
  assert t['debts']==';'.join(expected)
 expected_gap=[x[0] for x in f[positions[t['patient']]+1:at] if x[3]=='OPEN' and x[2]!='qokeeo']
 assert t['patient_to_target_unread']==';'.join(expected_gap)
# Complete future-action enumeration, including the later second stir in R.
future=rows(E/'FUTURES.tsv')
for t in trs:
 f=flat[(t['edition'],t['paragraph'])];pos={x[0]:i for i,x in enumerate(f)}
 expected={a['operation'] for a in actual if a['edition']==t['edition'] and a['model']==t['model'] and a['variant']==t['variant'] and a['paragraph']==t['paragraph'] and pos[a['operation']]>pos[t['mention']]}
 rr=[r for r in future if r['edition']==t['edition'] and r['model']==t['model'] and r['variant']==t['variant'] and r['target']==t['mention']]
 assert {r['later_action'] for r in rr}==expected
 for r in rr:
  a=index[(t['model'],t['edition'],t['variant'],r['later_action'])];assert r['patient']==a['patient']
# Full reader projection fidelity and unchanged annotation outside qokeeo.
before=rows(W/'W10/ALIGNMENT.tsv');after=rows(E/'ALIGNMENT.tsv');assert len(before)==len(after)==900
for a,b in zip(before,after):
 for k,v in a.items():assert b[k]==v
 assert b['U']==a['H']
 if a['raw']!='qokeeo':assert b['R']==b['C']==a['H']
ctx=rows(E/'CONTEXTS.tsv')
for r in ctx:assert r['raw']==' '.join(x[2] for x in flat[(r['edition'],r['paragraph'])] if x[1]==r['locus'])
assert len(ctx)==54
# Complete quantities, states and all material nouns, no newly invented interpretation.
obs=rows(E/'OBSERVABLES.tsv');wanted={'AMOUNT','NUMBER','DISTRIBUTIVE','STATE','QUALITY_VALUE','MATERIAL_DOSE','MATERIAL'}
for edition in alt:
 f=flat[(edition,'f99r|f99r.47-f99r.52')];expected={x[0] for x in f if x[3] in wanted}
 for model in ('U','R','C'):
  for v in ('B','J','M'):assert {r['mention'] for r in obs if r['edition']==edition and r['model']==model and r['variant']==v}==expected
result={'status':'PASS','source_and_preregistration_hashes':True,'argument_rows_checked':len(actual),'target_rows_checked':len(trs),'old_patient_changes':0,'old_debt_changes':deltas,'complete_future_census':True,'primary_groups':900,'semantic_truth_checked':False,'independent_meaning_confirmation':0}
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

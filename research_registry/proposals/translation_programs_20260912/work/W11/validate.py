"""Independent expected-delta check; does not import or run build.py."""
import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
s=json.loads((E/'SPEC.json').read_text())
for f in s['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
old=rows(W/'W05/ARGUMENTS.tsv');actual=rows(E/'ARGUMENTS.tsv');assert len(actual)==len(old)*3
baseline={(r['edition'],r['variant'],r['operation']):r for r in old}
keys=set();changes=0
for r in actual:
 key=(r['edition'],r['variant'],r['operation']);unique=(r['model'],)+key;assert unique not in keys;keys.add(unique)
 expected=baseline[key].copy()
 if r['model']=='P' and r['operation']=='f102v2.31:2':
  assert expected['patient']=='' and expected['debts']=='MISSING_PATIENT'
  expected.update(patient='f102v2.31:3',patient_form='sheeody',rule='LOCAL_RIGHT',debts='');changes+=1
 for col in ('patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption'):assert r[col]==expected[col],(unique,col)
 assert bool(r['instrument'])==(r['model']=='T' and r['operation']=='f102v2.31:2')
 if r['model']=='T':assert r['patient_form']!='sheeody'
assert changes==9
source=json.loads((W/'W02/SOURCE.json').read_text());alt=json.loads((W/'W02/ALTERNATE_LINES.json').read_text())['readings']
allowed={l['locus'] for t in source['targets'] for l in t['hosts']['ZL3b'][0]['lines']};assert len(allowed)==152
expected_targets=set()
for edition,ll in alt.items():
 for l in ll:
  locus=l['metadata']['locus']
  if locus not in allowed:continue
  assert not locus.startswith('f84')
  words=[g['ivtff_group_raw'] for g in l['groups']]
  for i,w in enumerate(words,1):
   if w=='sheeody':
    expected_targets.add((edition,locus+':'+str(i)))
    assert (locus,i) in [('f93r.8',2),('f102v2.31',3)]
    assert words[i-2] in ('lor','ckhy')
for model in ('U','T','P'):
 assert {(r['edition'],r['mention']) for r in rows(E/'TARGETS.tsv') if r['model']==model}==expected_targets
assert len(expected_targets)==6
before=rows(W/'W10/ALIGNMENT.tsv');after=rows(E/'ALIGNMENT.tsv');assert len(before)==len(after)==900
for a,b in zip(before,after):
 for k,v in a.items():assert b[k]==v
 assert b['U']==a['H']
 if a['raw']!='sheeody':assert b['T']==b['P']==a['H']
assert not rows(E/'QUALITY_DEBTS.tsv')
# All qualifying lor / ckhy / material-dose positions in both full contexts.
lex={r['form']:r['role'] for r in rows(W/'W02/LEXICON.tsv')}
expected_census=set()
for edition,ll in alt.items():
 for l in ll:
  loc=l['metadata']['locus']
  if loc not in allowed or not loc.startswith(('f93r.','f102v2.')):continue
  for i,g in enumerate(l['groups'],1):
   w=g['ivtff_group_raw']
   if w in ('lor','ckhy') or lex.get(w)=='MATERIAL_DOSE':expected_census.add((edition,loc+':'+str(i)))
for model in ('U','T','P'):
 actualc=[r for r in rows(E/'ROLE_CENSUS.tsv') if r['model']==model]
 assert {(r['edition'],r['mention']) for r in actualc}==expected_census
 assert all(r['debt']=='MISSING_GOVERNING_ACTION' for r in actualc if r['form']=='lor')
result={'status':'PASS','validation':'source hashes; 2709 argument rows independently checked against frozen baseline plus the sole local delta; all target/role census positions; full 900-group fidelity','argument_rows':len(actual),'distinct_exposed_target_contexts_per_reading':2,'changed_rows':changes,'semantic_validation':False,'independent_meaning_confirmation':0}
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

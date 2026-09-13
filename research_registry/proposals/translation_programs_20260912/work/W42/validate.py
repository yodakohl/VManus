"""Independent event-interval and frozen-pair audit of W42 accounts."""
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text())
def rows(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
raw=rows(S['source']);fields=rows(D/'FIELDS.tsv');pred=rows(D/'PREDICTIONS.tsv');accounts=rows(D/'ACTIVITY_ACCOUNTS.tsv');totals=rows(D/'RECORD_ACCOUNTS.tsv');al=rows(D/'ALIGNMENT.tsv')
lex={r['form']:r['meaning_hypothesis'] for r in rows(S['lexicon'])};mat=set(json.loads(Path(S['materials']).read_text())['material_forms'])
assert len(raw)==145 and len(fields)==sum(r['word']=='daiin' for r in raw)==8
assert [f['at'] for f in fields]==[r['at'] for r in raw if r['word']=='daiin']
# Old S07 targets, independently preserved at both pair constructions.
cases=json.loads((D.parent/'S07/CASES.json').read_text());paired={}
for c in cases:
 if not c['kind'].startswith('DOSE'):continue
 rr=[r for r in raw if r['record']==c['record']];ids=[r['at'] for r in rr]
 qs=[r for r in rr[ids.index(c['start']):ids.index(c['end'])+1] if r['word']=='daiin']
 for q,t in zip(qs,c['targets']):paired[q['at']]=t['at']
expected_actions=[]
for rec in S['records']:
 rr=[r for r in raw if r['record']==rec];loc={r['at']:i for i,r in enumerate(rr)}
 acts=[(i,r) for i,r in enumerate(rr) if r['word'] in S['actions']]
 for k,(i,a) in enumerate(acts):
  stop=acts[k+1][0] if k+1<len(acts) else len(rr)
  qids=[r['at'] for r in rr[i+1:stop] if r['word']=='daiin']
  account=next(x for x in accounts if x['at']==a['at'])
  assert account['value_loci']==(','.join(qids) or 'NONE')
  assert int(account['fields'])==len(qids)
  expected_actions.append(a['at'])
 for f in [f for f in fields if f['record']==rec]:
  left=rr[:loc[f['at']]];ms=[r for r in left if r['word'] in mat]
  expected_m=paired.get(f['at'],ms[-1]['at'] if ms else 'MISSING')
  assert f['material_at']==expected_m
  if expected_m!='MISSING':assert f['material_word']==rr[loc[expected_m]]['word']
  previous=[a for i,a in acts if i<loc[f['at']]]
  expected_a=previous[-1]['at'] if previous else 'MISSING';assert f['action_at']==expected_a
  if previous:
   gap=rr[loc[expected_a]+1:loc[f['at']]]
   assert f['action_to_value_raw']==' '.join(r['word'] for r in gap)
   assert int(f['unknown_between'])==sum(r['word'] not in lex for r in gap)
 assert next(t for t in totals if t['record']==rec)['groups']==str(len(rr))
assert [a['at'] for a in accounts]==expected_actions
for rec in S['records']:
 fs=[f for f in fields if f['record']==rec];aa=[a for a in accounts if a['record']==rec];t=next(t for t in totals if t['record']==rec)
 unique_actions={f['action_at'] for f in fs if f['action_at']!='MISSING'}
 pairs={(f['action_at'],f['material_word']) for f in fs if 'MISSING' not in [f['action_at'],f['material_word']]}
 assert int(t['E_priced_work_units'])==len(unique_actions)
 assert int(t['L_priced_work_units'])==len(pairs)
 assert int(t['actions_without_daiin'])==len(aa)-len(unique_actions)
 for a in aa:
  pairs_a=sorted(m for x,m in pairs if x==a['at'])
  assert a['distinct_materials']==(','.join(pairs_a) or 'NONE')
  assert a['E_partial_work']==('Q*U_E' if a['at'] in unique_actions else 'UNKNOWN_UNPRICED')
  assert a['L_partial_work']==(str(len(pairs_a))+'*Q*U_E' if pairs_a else 'UNKNOWN_UNPRICED')
  assert a['T_partial_work']==('Q*U_E/U_M*('+'+'.join('m('+m+')' for m in pairs_a)+')' if pairs_a else 'UNKNOWN_UNPRICED')
assert {(p['model'],p['at']) for p in pred}=={(m,f['at']) for m in S['models'] for f in fields}
for m in S['models']:
 ar=[a for a in al if a['model']==m]
 assert [(a['at'],a['word']) for a in ar]==[(r['at'],r['word']) for r in raw]
 for a in ar:
  if a['word']!='daiin':assert a['reading']==lex.get(a['word'],'⟦'+a['word']+'⟧')
  else:assert a['reading']==next(p['prediction'] for p in pred if p['model']==m and p['at']==a['at'])
text=(D/'READING.md').read_text()
for line in dict.fromkeys(r['locus'] for r in raw):assert line+': `'+ ' '.join(r['word'] for r in raw if r['locus']==line)+'`' in text
result=dict(status='PASS',hash_bound_files=len(S['hashes']),raw_groups=len(raw),all_value_fields=len(fields),old_pair_targets_preserved=len(paired),activity_occurrences=len(accounts),complete_alignment_rows=len(al),predictions=len(pred),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

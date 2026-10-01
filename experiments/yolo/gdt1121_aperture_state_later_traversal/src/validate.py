#!/usr/bin/env python3
"""Independent verification of the narrow diagnostic, not meaning validation."""
import csv, hashlib, json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
spec=json.loads((E/'src/SPEC.json').read_text());d={}
for key,b in spec['inputs'].items():
    raw=(ROOT/b['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256'];d[key]=json.loads(raw)
a,t,p,s=[d[k] for k in ('author','target','priors','signatures')]
assert a['lexical_roots']==s['lexical_roots'] and a['whole_form_residuals']==s['whole_form_residuals']
lex={x['surface']:x for x in a['lexical_roots']+a['whole_form_residuals']}
raw=[dict(zip(line['columns'],g)) for line in t['raw_lines'] for g in line['groups']]
assert len(raw)==182 and all(x['page']=='f85r1' for x in raw)
byid={x['source_group_id']:x for x in raw}
for x in a['positions']:
    assert byid[x['id']]['ivtff_group_raw']==x['raw_surface']==''.join(x['segmentation'])
trace=json.loads((E/'artifacts/TRACE.json').read_text())
assert len(trace['prefix'])==13
for row,x in zip(trace['prefix'],a['positions']):
    assert row['surface']==x['raw_surface'] and row['source_id']==x['id']
    expected=lex['shedy']['sort'] if x['segmentation']==['d','shedy'] else lex[x['raw_surface']]['sort']
    assert row['declared_sort']==expected
assert [x['position'] for x in trace['events']]==[3,6,8,11,13]
assert all(x['declared_sort']=='UnaryProcess(Material)' for x in trace['events'])
assert trace['accepted_sorts']==s['common_G3_finite_domains']['qocthdy']['domain']==['Motion(Material)']
assert trace['compatible_events']==[] and trace['conflict'] is True
assert trace['modifier']==a['positions'][13]
intro={x['surface'] for x in lex.values() if x['sort'] in ('InputMaterialIntroduction','ContainerIntroduction')}
assert intro=={'pdsheody','shdol'}
init=json.loads((E/'artifacts/INITIALIZATION.json').read_text());assert len(init)==6
profiles={x['form']:x for x in p['profiles']}
for row in init:
    owned=[x['source_group_id'] for x in raw if x['edition']==row['edition'] and x['ivtff_group_raw']==row['form']]
    assert row['source_ids']==owned
    assert row['admitted_exact_count']==profiles[row['form']]['editions'][row['edition']]['count']==len(owned)==1
    assert row['outside_occurrences']==0
r=json.loads((E/'artifacts/RESULT.json').read_text())
assert r['local_conflict_position']==14 and r['outside_whole_initialization_upper_bound']==0
assert r['seed_positions']=={w:[x['position'] for x in a['positions'] if x['raw_surface']==w] for w in ('chy','qokeey','chor')}
assert r['seed_positions']=={'chy':[27],'qokeey':[57],'chor':[58]}
assert r['aperture_tests_scored']==0 and r['external_paragraph_search'] is False
with (E/'artifacts/CANDIDATE_TABLE.tsv').open() as f: rows=list(csv.DictReader(f,delimiter='\t'))
assert [(x['candidate'],x['predicted_state_if_completed_and_bound'],x['aperture_test_scored']) for x in rows]==[('A','CLOSED','False'),('B','OPEN','False')]
v=dict(status='PASS',coverage='Four input hashes, unchanged lexical inventory, 182 raw group bindings, 60 nominated surfaces, 13-position sort trace, six introduction counts, seed order and rival table',meanings_validated=False,full_grammar_parser=False,aperture_meaning_test=False,confirmed_words=0)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))

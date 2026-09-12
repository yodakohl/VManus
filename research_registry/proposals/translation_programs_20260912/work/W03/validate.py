"""Document/coverage validation, not an independent meaning test."""
import collections, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parent
P = E.parent / 'W02'
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
spec = json.loads((E / 'SPEC.json').read_text())
result = json.loads((E / 'RESULT.json').read_text())
def read(name):
    return list(csv.DictReader((E / name).open(), delimiter='\t'))

for src in spec['inputs']:
    assert hashlib.sha256((ROOT / src['path']).read_bytes()).hexdigest() == src['sha256']
source = json.loads((P / 'SOURCE.json').read_text())
lex = {r['form']:r for r in csv.DictReader((P/'LEXICON.tsv').open(), delimiter='\t')}
paragraphs = [t['hosts']['ZL3b'][0] for t in source['targets']]
expected = [(p['id'], l['locus'], str(i), w) for p in paragraphs for l in p['lines'] for i,w in enumerate(l['words'], 1)]
alignment = read('ALIGNMENT.tsv')
assert [(r['paragraph'], r['locus'], r['index'], r['raw']) for r in alignment] == expected
assert len(expected) == 900 and len(paragraphs) == 13
assert len({r['locus'] for r in alignment}) == 152
assert not any(l.startswith('f84') for _,l,_,_ in expected)
changed_forms = {f['form'] for f in spec['features'] if f['kind'] == 'BARE_NOMINAL'} | {'qotchy'}
for r in alignment:
    if r['raw'] not in lex:
        assert r['status'] == 'UNREAD' and r['Q1_T'] == '[ungelesen: ' + r['raw'] + ']' == r['Q1_V']
    elif r['raw'] not in changed_forms:
        assert r['Q1_T'] == r['Q1_V'] == lex[r['raw']]['hypothesis']
    if r['raw'] != 'qotchy':
        assert r['Q1_T'] == r['Q1_V']
assert sum(r['status']=='UNREAD' for r in alignment) == result['unread'] == 370
for variant in ['T','V']:
    text = (E / ('READING_Q1_' + variant + '.md')).read_text()
    for p in paragraphs:
        for l in p['lines']:
            assert text.count(l['locus'] + ': `' + ' '.join(l['words']) + '`') == 1

qualities = read('QUALITY_BINDINGS.tsv')
required = collections.Counter((q, locus+':'+idx, f['kind'], f['axis'], f['value'])
    for _,locus,idx,word in expected for f in spec['features'] if f['form']==word for q in ['Q0','Q1'])
observed = collections.Counter((r['model'],r['mention'],r['kind'],r['axis'],r['value']) for r in qualities)
assert observed == required
q0 = [r for r in qualities if r['model']=='Q0']
q1 = [r for r in qualities if r['model']=='Q1']
assert len(q0)==len(q1)==136
for a,b in zip(q0,q1):
    assert {k:v for k,v in a.items() if k not in {'model','scope'}} == {k:v for k,v in b.items() if k not in {'model','scope'}}
    assert a['scope']=='PHYSICAL'
    assert b['scope']==('CONSTITUTION' if b['kind']=='BARE_NOMINAL' else 'PHYSICAL')
    if a['patient']:
        assert a['patient'].rsplit(':',1)[0] == a['locus']
        assert lex[a['patient_form']]['role'] in {'MATERIAL','MATERIAL_DOSE'}
assert sum(not r['patient'] for r in q0)==result['quality_unbound_per_model']==18
conflicts = read('QUALITY_CONTRADICTIONS.tsv')
expected_conflicts = {
    'Q0': {('f9v.10','oty','chy'), ('f9v.11','chshoty','oky'), ('f17v.9','shol','kchol'),
           ('f22v.9','shody','chol'), ('f93r.2','chol','sheo')},
    'Q1': {('f9v.10','oty','chy'), ('f22v.9','shody','chol')},
}
for q, required in expected_conflicts.items():
    assert {(r['locus'],r['first_form'],r['second_form']) for r in conflicts if r['model']==q} == required
    assert len(result['conflicts'][q]) == len(required)
# Check every bound opposition from the published assertion table: no omitted rows.
actual_pairs = collections.Counter((r['model'],r['first'],r['second'],r['patient'],r['axis']) for r in conflicts)
all_pairs = []
for i,a in enumerate(qualities):
    for b in qualities[i+1:]:
        if not a['patient'] or any(a[k]!=b[k] for k in ['model','locus','patient','axis','scope']):
            continue
        opposites = {frozenset(v) for v in spec['opposed'][a['axis']]}
        if frozenset([a['value'],b['value']]) in opposites:
            all_pairs.append((a['model'],a['mention'],b['mention'],a['patient'],a['axis']))
assert actual_pairs == collections.Counter(all_pairs)

pairs = read('RELATION_CANDIDATES.tsv')
assert [(r['operation'],r['A_form'],r['B_form']) for r in pairs] == [
    ('f22v.8:1','cthy','qokol'), ('f24r.12:2','tol','tod'), ('f93r.13:2','shodaiin','kchol')]
assert all(r['decision']=='T_V_UNRESOLVED' for r in pairs)
alternate = json.loads((P / 'ALTERNATE_LINES.json').read_text())['readings']
required_occurrences = collections.Counter((ed, line['metadata']['locus'],str(i))
    for ed,lines in alternate.items() for line in lines
    for i,g in enumerate(line['groups'],1) if g['ivtff_group_raw']=='qotchy')
occurrences = read('ALL_READING_QOTCHY_OCCURRENCES.tsv')
all_bindings = read('ALL_READING_RELATION_BINDINGS.tsv')
for rows in [occurrences,all_bindings]:
    assert collections.Counter((r['edition'],r['locus'],r['index']) for r in rows) == required_occurrences
assert len(all_bindings)==10
incomplete = [r for r in all_bindings if r['complete']=='False']
assert [(r['edition'],r['locus'],r['A_form'],r['B_form']) for r in incomplete] == [('IT2a','f22v.14','','')]
assert len(read('CRITICAL_QUALITY_ALTERNATE_LINES.tsv')) == 15
assert result['meaning_identifications']==0 and result['independent_confirmation_capacity']==0
assert not result['held_access'] and not result['significance_claim']

validation = dict(status='PASS', executed_utc=datetime.now(timezone.utc).isoformat(),
    checks=['FROZEN_INPUT_HASHES', 'EXACT_900_GROUP_SCOPE', 'NO_NEW_UNKNOWN_WORD_GLOSSES',
            'FULL_T_V_RENDERING', 'COMPLETE_QUALITY_ASSERTIONS_AND_OPPOSITIONS',
            'ONLY_REGISTERED_QUALITY_SCOPE_CHANGE', 'ALL_ALTERNATE_QOTCHY_OCCURRENCES'],
    independent_semantic_observation=False, meaning_confirmation=False)
(E / 'VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(validation))

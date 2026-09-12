"""Check exhaustive source/argument consequences without importing the builder."""
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
W2, W5 = E.parent / 'W02', E.parent / 'W05'
spec = json.loads((E / 'SPEC.json').read_text())
for f in spec['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']

def rows(p):
    with p.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

source = json.loads((W2 / 'SOURCE.json').read_text())
editions = json.loads((W2 / 'ALTERNATE_LINES.json').read_text())['readings']
lex = {r['form']: r for r in rows(W2 / 'LEXICON.tsv')}
forms = {w for w in lex if lex[w]['role'] == 'MIX'}
assert forms == set(spec['mix_forms'])
hosts = [t['hosts']['ZL3b'][0] for t in source['targets']]
packet = {}
for ed, lines in editions.items():
    lm = {l['metadata']['locus']: l['groups'] for l in lines}
    for p in hosts:
        assert not p['page'].startswith('f84')
        wordpairs = [(f"{l['locus']}:{i}", g['ivtff_group_raw'])
                     for l in p['lines'] for i, g in enumerate(lm[l['locus']], 1)]
        packet[ed, p['id']] = wordpairs

old = rows(W5 / 'ARGUMENTS.tsv')
def key(r): return r['edition'], r.get('grammar', r.get('variant')), r['paragraph'], r['operation']
oldmix = {key(r): r for r in old if r['form'] in forms}
new = rows(E / 'MIX_COMPARISON.tsv')
indexed = {(key(r), r['model']): r for r in new}
expected_mix = {(ed, grammar, p, ident) for (ed, p), words in packet.items()
                for ident, word in words if word in forms for grammar in spec['grammars']}
assert set(oldmix) == expected_mix
assert len(indexed) == len(new) == len(oldmix) * 2
assert set(indexed) == {(k, m) for k in expected_mix for m in spec['mix_models']}
for k, a in oldmix.items():
    for model in spec['mix_models']:
        b = indexed[k, model]
        for field in ['form', 'patient', 'patient_form', 'rule', 'additional_grammar_assumption']:
            assert b[field] == a[field], (k, field)
        assert b['inherited_second'] == a['coingredient']
        assert b['inherited_debts'] == a['debts']
        actual_debts = set(filter(None, b['remaining_debts'].split(';')))
        wanted = set(filter(None, a['debts'].split(';')))
        if model == 'U': wanted.discard('MISSING_COINGREDIENT')
        assert wanted == actual_debts
        assert b['second_used_by_mix'] == (a['coingredient'] if model == 'D' else '')
        assert b['second_not_used_by_mix'] == (a['coingredient'] if model == 'U' else '')
        owners = {r['operation'] for r in old if key(r)[:3] == k[:3] and r['operation'] != a['operation']
                  and a['coingredient'] and a['coingredient'] in [r['patient'], r['coingredient']]}
        assert set(filter(None, b['second_other_operations'].split(';'))) == owners
        composition = 'X(' + a['patient'] + ')' if a['patient'] else 'UNBOUND_PATIENT'
        if model == 'D': composition += '+X(' + a['coingredient'] + ')' if a['coingredient'] else '+UNBOUND_SECOND'
        assert b['composition'] == composition and not b['written_product_name']
        complete = bool(a['patient'] and (model == 'U' or a['coingredient']))
        assert (b['status'] == 'CONDITIONAL_COMPOSITION') == complete

lm = rows(E / 'LATER_MATERIALS.tsv')
la = rows(E / 'LATER_ACTIONS.tsv')
st = rows(E / 'LATER_MIXED_STATES.tsv')
seq = rows(E / 'RELATION_SEQUENCES.tsv')
expected_lm, expected_la, expected_st, expected_seq = set(), set(), set(), set()
for k, a in oldmix.items():
    words = packet[k[0], k[2]]
    positions = {ident: i for i, (ident, word) in enumerate(words)}
    names = dict(words)
    ins = set(filter(None, [a['patient'], a['coingredient']]))
    cut = max(positions[i] for i in ins | {a['operation']})
    later_words = [(i, w) for i, w in words if positions[i] > cut]
    expected_lm |= {(k, i) for i, w in later_words if lex.get(w, {}).get('role') in spec['material_roles']}
    expected_st |= {(k, i) for i, w in words if w == 'oees' and positions[i] > positions[a['operation']]}
    followers = [r for r in old if key(r)[:3] == k[:3] and positions[r['operation']] > positions[a['operation']]]
    expected_la |= {(k, r['operation']) for r in followers}
    expected_seq |= {(k, r['operation'], m, v) for r in followers if r['form'] == 'qotchy'
                     for m in spec['mix_models'] for v in spec['relation_rivals']}
    for r in lm:
        if key(r) == k:
            same = r['material'] in {names[i] for i in ins}
            assert (r['same_form_as_input'] == 'True') == same
            assert r['identity'] == ('SAME_OR_NEW_UNRESOLVED' if same else 'DIFFERENT_FORM_NO_PRODUCT_BINDING')
            assert r['independently_bound_composition'] == 'False'
    followmap = {r['operation']: r for r in followers}
    for r in la:
        if key(r) == k:
            following = followmap[r['next_operation']]
            assert r['next_patient'] == following['patient'] and r['next_second'] == following['coingredient']
            overlap = ins & set(filter(None, [following['patient'], following['coingredient']]))
            assert set(filter(None, r['identical_written_inputs'].split(';'))) == overlap
    for r in seq:
        if key(r) != k: continue
        following = followmap[r['next_operation']]
        nxt = set(filter(None, [following['patient'], following['coingredient']]))
        same = bool(a['patient'] and a['coingredient'] and following['patient'] and following['coingredient'] and ins == nxt)
        assert (r['identical_complete_pair'] == 'True') == same
        expected = 'NO_IDENTICAL_COMPLETE_INPUT_PAIR'
        if same:
            expected = {('D', 'T'): 'JOIN_THEN_SEPARATE_SAME_WRITTEN_PAIR',
                        ('U', 'T'): 'WORK_THEN_SEPARATE_PRIOR_JOIN_NOT_ESTABLISHED',
                        ('D', 'V'): 'JOIN_THEN_JOIN_AGAIN_NO_AUTOMATIC_CONTRADICTION',
                        ('U', 'V'): 'WORK_THEN_JOIN_SAME_WRITTEN_PAIR'}[r['model'], r['rival']]
        assert r['consequence'] == expected and r['meaning_evidence'] == 'False'

for data, actual, expected in [
    (lm, {(key(r), r['mention']) for r in lm}, expected_lm),
    (la, {(key(r), r['next_operation']) for r in la}, expected_la),
    (st, {(key(r), r['mention']) for r in st}, expected_st),
    (seq, {(key(r), r['next_operation'], r['model'], r['rival']) for r in seq}, expected_seq)]:
    assert len(data) == len(actual) and actual == expected

alignment = rows(E / 'ALIGNMENT.tsv')
original = rows(W5 / 'ALIGNMENT.tsv')
assert [(r['paragraph'], r['locus'], r['index'], r['raw'], r['status']) for r in alignment] == [
    (r['paragraph'], r['locus'], r['index'], r['raw'], r['status']) for r in original]
for a, b in zip(alignment, original):
    assert a['U'] == (spec['U_gloss'] if a['raw'] in forms else b['unchanged_W04_C'])
    assert a['D'] == (spec['D_gloss'] if a['raw'] in forms else b['unchanged_W04_C'])
reading = (E / 'READING.md').read_text()
for p in hosts:
    for line in p['lines']:
        assert reading.count(line['locus'] + ': `' + ' '.join(line['words']) + '`') == 1
human = (E / 'F6V_U_READING.md').read_text()
for p in hosts:
    if p['page'] == 'f6v':
        for line in p['lines']:
            assert human.count('`' + ' '.join(line['words']) + '`') == 1
coverage = rows(E / 'COVERAGE.tsv')
assert len(coverage) == len(packet)
for r in coverage:
    words = packet[r['edition'], r['paragraph']]
    assert int(r['groups']) == len(words)
    assert int(r['mix_events']) == sum(w in forms for i, w in words)

# Salient narrative consequences and alternate-reader limitations.
assert {(r['operation'], r['form']) for r in new if r['edition'] == 'ZL3b'} == {
    ('f6v.10:2', 'ychear'), ('f6v.15:1', 'chockhy'), ('f22v.10:1', 'qokchy'),
    ('f22v.15:4', 'qokchy'), ('f24r.12:1', 'qokchy')}
positive = [r for r in seq if r['consequence'] == 'JOIN_THEN_SEPARATE_SAME_WRITTEN_PAIR']
assert {(r['edition'], r['grammar'], r['operation'], r['next_operation']) for r in positive} == {
    (ed, gr, 'f24r.12:1', 'f24r.12:2') for ed in editions for gr in ['J', 'M']}
stamp = [r for r in la if r['operation'] == 'f24r.12:1' and r['next_operation'] == 'f24r.12:5']
assert {r['edition'] for r in stamp} == {'ZL3b', 'IT2a'}
assert all(r['next_patient'] == 'f24r.12:4' and r['next_form'] == 'ckhy' for r in stamp)
assert {r['edition'] for r in lm if r['same_form_as_input'] == 'True'} == {'IT2a'}

result = json.loads((E / 'RESULT.json').read_text())
summary = rows(E / 'MODEL_SUMMARY.tsv')
for r in summary:
    selected = [x for x in new if all(x[k] == r[k] for k in ['edition', 'grammar', 'model'])]
    assert int(r['mix_events']) == len(selected)
    assert int(r['complete_input_sets']) == sum(x['status'] == 'CONDITIONAL_COMPOSITION' for x in selected)
    assert int(r['missing_seconds']) == sum('MISSING_COINGREDIENT' in x['remaining_debts'] for x in selected)
    assert int(r['events_with_other_debts']) == sum(bool(set(filter(None, x['remaining_debts'].split(';'))) - {'MISSING_COINGREDIENT'}) for x in selected)
    assert int(r['written_second_not_used_by_mix']) == sum(bool(x['second_not_used_by_mix']) for x in selected)
    assert int(r['unused_second_without_other_operation']) == sum(bool(x['second_not_used_by_mix']) and not x['second_other_operations'] for x in selected)
    assert int(r['conditional_join_then_separate']) == sum(all(x[k] == r[k] for k in ['edition', 'grammar', 'model']) for x in positive)
assert result['primary_groups'] == len(alignment) == 900
assert result['later_material_rows'] == len(lm) and result['later_action_rows'] == len(la)
assert result['later_same_form_material_rows'] == sum(r['same_form_as_input'] == 'True' for r in lm)
assert result['meaning_identifications'] == result['independent_confirmation_capacity'] == 0
assert not result['held_access'] and not result['significance_claim']
assessment = json.loads((E / 'ASSESSMENT.json').read_text())
assert assessment['new_global_winner'] is None
assert assessment['primary_mix_events'] == 5 and assessment['primary_mix_forms'] == len(forms)
assert assessment['meaning_identifications'] == assessment['independent_confirmation_capacity'] == 0
assert not assessment['held_access'] and not assessment['significance_claim']
out = dict(status='PASS', verified='frozen sources; all three MIX words in all 13 paragraphs and alternate projections; all 90 event contracts; all later materials/actions/states; all T/V sequences; full text and unchanged other words',
           meaning_validation=False, independent_observer=False, primary_groups=len(alignment),
           events=len(new), later_material_rows=len(lm), later_action_rows=len(la),
           conditional_pair_cases=len(positive), distinct_primary_pair_cases=1,
           script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(E / 'VALIDATION.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False))

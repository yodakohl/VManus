"""Separate coverage and contract audit; no import of W07's builder."""
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
W2, W5 = E.parent / 'W02', E.parent / 'W05'
spec = json.loads((E / 'SPEC.json').read_text())
for f in spec['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256']

def read(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

source = json.loads((W2 / 'SOURCE.json').read_text())
alternate = json.loads((W2 / 'ALTERNATE_LINES.json').read_text())['readings']
lex = {r['form']: r for r in read(W2 / 'LEXICON.tsv')}
hosts = [t['hosts']['ZL3b'][0] for t in source['targets']]
old = read(W5 / 'ARGUMENTS.tsv')
packet = {}
for ed, lines in alternate.items():
    lm = {l['metadata']['locus']: l['groups'] for l in lines}
    for p in hosts:
        assert not p['page'].startswith('f84')
        pairs = [(f"{l['locus']}:{i}", g['ivtff_group_raw']) for l in p['lines'] for i, g in enumerate(lm[l['locus']], 1)]
        packet[ed, p['id']] = pairs
cases = read(E / 'CASES.tsv')
fields = read(E / 'QUANTITY_FIELDS.tsv')
prior = read(E / 'PRIOR_ACTIONS.tsv')
future = read(E / 'CONTINUATIONS.tsv')
models = read(E / 'CANDIDATES.tsv')
def key(r): return r['edition'], r['paragraph'], r['target']
expected_cases = {(ed, p, ident) for (ed, p), pairs in packet.items() for ident, w in pairs if w == 'dam'}
assert len(cases) == len(expected_cases) == 9 and {key(r) for r in cases} == expected_cases
assert {r['target'] for r in cases if r['edition'] == 'ZL3b'} == {'f22v.8:5', 'f24r.16:4', 'f93r.3:5'}
assert len(models) == 36
assert {(key(r), r['model'], r['qotchy_rival']) for r in models} == {
    (k, m, v) for k in expected_cases for m in ['R', 'P'] for v in ['T', 'V']}

expected_fields, expected_prior, expected_future = set(), set(), set()
for c in cases:
    k = key(c)
    pairs = packet[k[:2]]
    words = dict(pairs)
    pos = {i: n for n, (i, w) in enumerate(pairs)}
    same_line = [i for i, w in pairs if i.rsplit(':', 1)[0] == k[2].rsplit(':', 1)[0]]
    aa = [r for r in old if r['edition'] == k[0] and r['paragraph'] == k[1]]
    ops = {r['operation'] for r in aa}
    quantity_ids = [i for i in same_line if lex.get(words[i], {}).get('role') in spec['quantity_roles']]
    assert c['same_line_quantity_fields'].split(';') == quantity_ids
    for q in quantity_ids:
        expected_fields.add((k, q))
        # Compare every possible material in order, retaining only the same
        # line region not separated by any fixed action position.
        eligible = [i for i in same_line if lex.get(words[i], {}).get('role') in spec['material_roles'] and
                    not any(min(pos[q], pos[i]) < pos[o] < max(pos[q], pos[i]) for o in ops)]
        l = [i for i in eligible if pos[i] < pos[q]]
        r = [i for i in eligible if pos[i] > pos[q]]
        carrier = l[-1] if l else r[0] if r else ''
        got = [f for f in fields if key(f) == k and f['quantity'] == q]
        assert len(got) == 1
        f = got[0]
        assert f['carrier'] == carrier and f['carrier_form'] == words.get(carrier, '')
        debt = {f'UNREAD_BETWEEN:{i}' for i in same_line if carrier and
                min(pos[q], pos[carrier]) < pos[i] < max(pos[q], pos[carrier]) and words[i] not in lex}
        if not carrier: debt = {'MISSING_QUANTITY_CARRIER'}
        assert set(filter(None, f['debts'].split(';'))) == debt
        assert not f['numerical_value'] and not f['equation']
        if q == k[2]:
            assert c['carrier'] == carrier and c['attachment_debts'] == f['debts']
    cut = max(pos[k[2]], pos[c['carrier']])
    repeats = {i for i, w in pairs if pos[i] > cut and w == c['carrier_form']}
    assert set(filter(None, c['later_same_form_mentions'].split(';'))) == repeats
    for i, w in pairs:
        role = lex.get(w, {}).get('role')
        if pos[i] > cut and role in spec['quantity_roles'] + spec['material_roles']:
            kind = 'MATERIAL' if role in spec['material_roles'] else 'QUANTITY'
            expected_future.add((k, 'ALL', kind, i))
    local_candidates = {}
    for g in ['B', 'J', 'M']:
        local_candidates[g] = []
        for a in [r for r in aa if r['variant'] == g]:
            ident = a['operation']
            ins = set(filter(None, [a['patient'], a['coingredient']]))
            if pos[ident] < pos[k[2]]:
                expected_prior.add((k, g, ident))
                rr = [r for r in prior if key(r) == k and r['grammar'] == g and r['operation'] == ident]
                assert len(rr) == 1
                row = rr[0]
                assert row['patient'] == a['patient'] and row['second'] == a['coingredient'] and row['debts'] == a['debts']
                local = bool(a['form'] == 'qotchy' and a['patient'] and a['coingredient'] and c['carrier'] in ins)
                assert (row['relation'] == 'LOCAL_REMAINDER_PAIR_CANDIDATE') == local
                if local: local_candidates[g].append(ident)
            else:
                expected_future.add((k, g, 'ACTION', ident))
                rr = [r for r in future if key(r) == k and r['grammar'] == g and r['mention'] == ident and r['kind'] == 'ACTION']
                assert len(rr) == 1
                row = rr[0]
                assert row['patient'] == a['patient'] and row['second'] == a['coingredient'] and row['debts'] == a['debts']
                relation = ('SAME_WRITTEN_CARRIER' if c['carrier'] in ins else
                            'SAME_REMENTION_ASSUMPTION_REQUIRED' if ins & repeats else 'NO_IDENTIFIED_REMAINDER_REFERENCE')
                assert row['relation_to_dam'] == relation
    assert local_candidates['B'] == local_candidates['J'] == local_candidates['M']
    assert set(filter(None, c['local_pair_operations'].split(';'))) == set(local_candidates['B'])
    for r in models:
        if key(r) != k: continue
        assert r['carrier'] == c['carrier'] and r['carrier_form'] == c['carrier_form']
        assert r['attachment_debts'] == c['attachment_debts'] and r['later_same_form_mentions'] == c['later_same_form_mentions']
        active = r['model'] == 'R' and r['qotchy_rival'] == 'T' and bool(local_candidates['B'])
        assert bool(r['possible_separation']) == active
        assert r['status'] == ('PORTION_WITHOUT_SUBTRACTION_CLAIM' if r['model'] == 'P' else
                               'SEPARATED_PAIR_WITHOUT_WRITTEN_ORIGIN_STOCK' if active else 'NO_BOUND_ORIGIN_OR_WITHDRAWAL')
        # Frozen W03/W05 arguments are pair relations, with no source/output
        # quantity binding. Validate that W07 has not invented those fields.
        assert r['written_remainder_reference'] == (k[2] if r['model'] == 'R' else '')
        assert all(not r[f] for f in ['origin_stock', 'bound_withdrawal', 'symbolic_equation'])
        assert r['independent_confirmation_capacity'] == '0'

for data, got, expected in [
    (fields, {(key(r), r['quantity']) for r in fields}, expected_fields),
    (prior, {(key(r), r['grammar'], r['operation']) for r in prior}, expected_prior),
    (future, {(key(r), r['grammar'], r['kind'], r['mention']) for r in future}, expected_future)]:
    assert len(data) == len(got) and got == expected

a = read(E / 'ALIGNMENT.tsv')
oldalign = read(W5 / 'ALIGNMENT.tsv')
assert len(a) == len(oldalign) == 900
mixes = {w for w in lex if lex[w]['role'] == 'MIX'}
for x, y in zip(a, oldalign):
    assert all(x[k] == y[k] for k in ['paragraph', 'locus', 'index', 'raw', 'status'])
    for m in ['R', 'P']:
        for mix in ['U', 'D']:
            expected = spec['models'][m] if x['raw'] == 'dam' else (
                'arbeite gleichmäßig durch' if mix == 'U' else 'vermische zwei Materialien') if x['raw'] in mixes else y['unchanged_W04_C']
            assert x[m + '_' + mix] == expected
text = (E / 'READING.md').read_text()
for p in hosts:
    for l in p['lines']:
        assert text.count(l['locus'] + ': `' + ' '.join(l['words']) + '`') == 1
coverage = read(E / 'COVERAGE.tsv')
assert len(coverage) == len(packet)
for r in coverage:
    pairs = packet[r['edition'], r['paragraph']]
    assert int(r['groups']) == len(pairs) and int(r['dam']) == sum(w == 'dam' for i, w in pairs)

# This is the actual alternate-reading limit of the proposed reuse chain.
dry = [r for r in future if r['kind'] == 'ACTION' and r['relation_to_dam'] == 'SAME_REMENTION_ASSUMPTION_REQUIRED']
assert {r['edition'] for r in dry} == {'ZL3b'}
assert {(r['target'], r['mention']) for r in dry} == {
    ('f24r.16:4', 'f24r.18:2'), ('f24r.16:4', 'f24r.18:4'), ('f24r.16:4', 'f24r.19:3')}
assert len(dry) == 9
result = json.loads((E / 'RESULT.json').read_text())
assert result['source_cases'] == len(cases) and result['candidate_rows'] == len(models)
assert result['prior_action_rows'] == len(prior) and result['continuation_rows'] == len(future)
assert result['quantity_fields'] == len(fields) and result['local_separation_candidates'] == 1
assert result['primary_later_same_form_cases'] == 2
assert result['empirical_global_winner'] is None and not result['held_access'] and not result['significance_claim']
assert result['meaning_identifications'] == result['independent_confirmation_capacity'] == 0
out = dict(status='PASS', scope='all frozen source groups; all dam and same-line quantity fields; all prior/following fixed arguments; R/P and T/V consequences; alternate-reading reuse limit',
    source_cases=len(cases), candidate_rows=len(models), quantity_fields=len(fields), prior_action_rows=len(prior),
    continuation_rows=len(future), meaning_validation=False, independent_observer=False,
    origin_limit='No new source/product quantity binder is supplied; absence is a limitation of this fixed authored model, not a manuscript-wide proof.',
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(E / 'VALIDATION.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False))

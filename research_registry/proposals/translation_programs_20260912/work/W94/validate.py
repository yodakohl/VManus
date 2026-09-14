"""Separate reverse-index bindings and mass-incidence elimination; no builder import."""
import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

D = Path(__file__).resolve().parent.relative_to(Path.cwd())
B = D.parent

def eliminate(rows, width, stop=None):
    a = [[Q(x) for x in row] for row in rows]
    row = 0
    for col in range(width if stop is None else stop):
        choice = next((j for j in range(row, len(a)) if a[j][col]), None)
        if choice is None: continue
        pivot = a.pop(choice)
        divisor = pivot[col]; pivot = [x/divisor for x in pivot]
        a.insert(row, pivot)
        for j in range(len(a)):
            if j == row: continue
            mult = a[j][col]
            a[j] = [a[j][k]-mult*pivot[k] for k in range(width)]
        row += 1
    return a

def canonical(rows):
    return [[str(x) for x in row] for row in eliminate(rows, 3) if any(row)]

for f, h in json.loads((D/'FROZEN_INPUTS.json').read_text()).items():
    assert hashlib.sha256(Path(f).read_bytes()).hexdigest() == h, f
ps = json.loads((B/'W89/PARAGRAPHS.json').read_text())
model = json.loads((B/'P14/MODEL.json').read_text())
fs = list(csv.DictReader((D/'FIELDS.tsv').open(), delimiter='\t'))
seen = {}; predicted_fields = {}; source_tokens = []
for p in ps:
    assert not p['page'].startswith('f84') and p['page'] != 'f116v'
    ts = []
    for l in p['lines']:
        assert len(l['words']) == len(l['source_ids'])
        ts.extend((w, at, l['locus']) for w, at in zip(l['words'], l['source_ids']))
    assert len(ts) == p['groups']
    for w, at, line in ts:
        source_tokens.append((p['edition'], p['id'], at, w))
    for scope in ['RECORD', 'LINE']:
        for i, (w, at, line) in enumerate(ts):
            if w not in model['values']: continue
            prev = [(v, a) for v, a, ln in ts[:i] if v in model['materials'] and (scope == 'RECORD' or ln == line)]
            numerator = prev[-1] if prev else ('', '')
            denominator = next(((v, a) for v, a in reversed(prev) if v != numerator[0]), ('', ''))
            predicted_fields[p['edition'], p['id'], scope, at] = (numerator, denominator, model['values'][w])
for f in fs:
    key = f['edition'], f['paragraph'], f['scope'], f['at']
    assert key not in seen; seen[key] = True
    n, d, v = predicted_fields[key]
    assert (f['numerator'], f['numerator_at']) == n
    assert (f['denominator'], f['denominator_at']) == d
    assert f['value'] == v
    assert f['M_status'] == ('BOUND' if n[0] else 'MISSING_MATERIAL')
    assert f['R_status'] == ('BOUND' if n[0] and d[0] else 'MISSING_DENOMINATOR' if n[0] else 'MISSING_BOTH')
assert set(seen) == set(predicted_fields)
al = list(csv.DictReader((D/'ALIGNMENT.tsv').open(), delimiter='\t'))
assert [(a['edition'], a['paragraph'], a['at'], a['word']) for a in al] == source_tokens

systems = json.loads((D/'SYSTEMS.json').read_text())
assert len(systems) == len(ps)*8
independent_bases = {}; matrix_count = 0; witness_count = 0
for s in systems:
    key = s['edition'], s['paragraph'], s['scope'], s['reading'], s['identity']
    edges = []
    for (ed, para, scope, at), (n, d, v) in predicted_fields.items():
        if (ed, para, scope) != key[:3] or not n[0] or (s['reading'] == 'R' and not d[0]): continue
        k = 0 if s['identity'] == 'TYPE' else 1
        edges.append(dict(at=at, value=v, numerator=n[k], denominator=d[k] if s['reading'] == 'R' else 'UNIT'))
    assert edges == s['edges']
    nodes = sorted({e[k] for e in edges for k in ['numerator', 'denominator']})
    matrix = []
    for e in edges:
        row = [0]*(len(nodes)+3)
        row[nodes.index(e['numerator'])] += 1
        row[nodes.index(e['denominator'])] -= 1
        row[len(nodes)+'ABC'.index(e['value'])] -= 1
        matrix.append(row)
    reduced = eliminate(matrix, len(nodes)+3, len(nodes))
    constraints = [r[len(nodes):] for r in reduced if not any(r[:len(nodes)])]
    basis = canonical(constraints)
    assert basis == s['basis'], key
    assert canonical([c['coefficients'] for c in s['chords']]) == basis
    lookup = {e['at']: row for e, row in zip(edges, matrix)}
    for c in s['chords']:
        total = [sum(sign*lookup[at][k] for at, sign in c['support']) for k in range(len(nodes)+3)]
        assert not any(total[:len(nodes)])
        assert [-x for x in total[len(nodes):]] == c['coefficients']
        assert c['nontrivial'] == any(c['coefficients'])
        witness_count += 1
    independent_bases[key] = basis; matrix_count += 1
for s in json.loads((D/'CONSEQUENCES.json').read_text()):
    key = s['edition'], s['scope'], s['reading'], s['identity']
    rows = [r for (ed, para, scope, read, identity), bb in independent_bases.items()
            if (ed, scope, read, identity) == key for r in bb]
    basis = canonical(rows)
    assert basis == s['basis'] and len(basis) == s['rank']
    assert s['forced_one'] == [v for i, v in enumerate('ABC') if canonical(rows+[[int(i == j) for j in range(3)]]) == basis]
    assert s['forced_equal'] == [a+'='+b for i, a in enumerate('ABC') for j, b in enumerate('ABC') if i < j
                                  and canonical(rows+[[int(i == k)-int(j == k) for k in range(3)]]) == basis]
result = json.loads((D/'RESULT.json').read_text())
assert result['groups'] == len(source_tokens) == 8600
assert result['paragraph_transcriptions'] == len(ps) == 140
assert result['physical_leaves'] == len({p['leaf'] for p in ps})
assert result['editions'] == dict(Counter(p['edition'] for p in ps))
validation = dict(status='PASS', paragraph_transcriptions=len(ps), aligned_positions=len(source_tokens),
                  value_bindings=len(fs), separate_incidence_systems=matrix_count, all_cycle_witnesses=witness_count,
                  scope='frozen source and complete bindings, separate exact mass elimination and all witness equations',
                  author='root; distinct reconstruction, not an independent semantic observer',
                  independent_meaning_confirmation=False)
(D/'VALIDATION.json').write_text(json.dumps(validation, indent=2)+'\n')
print(json.dumps(validation, indent=2))

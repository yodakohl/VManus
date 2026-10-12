#!/usr/bin/env python3
"""Check five old certificates and signature arithmetic; not manuscript semantics."""
import hashlib
import itertools
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
REVIEW = BASE / 'BROAD_REPETITION_REVIEW_20261012.json'
ROOT = BASE.parents[2]
review = json.loads(REVIEW.read_text())
source = 'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json'
path = ROOT / source
expected_hash = next(s['sha256'] for s in review['sources'] if s['path'] == source)
assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
hits = json.loads(path.read_text())
forms = ['sheol', 'okaiin', 'chol', 'ytaiin', 'qokedy']
loc_start = [('f104v.27', 3), ('f40r.9', 6), ('f47r.7', 4), ('f86v3.3', 2), ('f79v.19', 5)]
readers = ['ZL3b', 'IT2a', 'RF1b']
records = []
for reader in readers:
    for form, (locus, start) in zip(forms, loc_start):
        if reader == 'RF1b' and form == 'qokedy':
            start = 6
        matching = [h for h in hits if h['edition'] == reader and h['locus'] == locus and int(h['start_index']) == start and h['raw'] == form]
        assert len(matching) == 1
        h = matching[0]
        ids = [f'{reader}|{locus}|G{i:03d}' for i in range(start, start + 3)]
        assert h['source_ids'] == ids
        assert list(map(int, h['source_indices'])) == list(range(start, start + 3))
        assert len(h['groups']) == 3
        for g, sid in zip(h['groups'], ids):
            assert g['source_group_id'] == sid
            assert g['ivtff_group_raw'] == form
            assert g['left_separator'] == g['right_separator'] == 'DEFINITE_SPACE'
        records.append({'edition': reader, 'locus': locus, 'start_index': str(start), 'raw': form, 'source_ids': ids})
assert sorted(records, key=str) == sorted(review['old_certificate_checks']['records'], key=str)

# Independent tokenizer on these five fixed literals only; no corpus parsing.
def units(raw):
    out = []
    while raw:
        width = 2 if raw[:2] in ('ch', 'sh') else 1
        out.append(raw[:width])
        raw = raw[width:]
    return out

blocks = [units(w) for w in forms]
assert dict(zip(forms, blocks)) == review['declared_block_units']
alphabet = sorted(set(itertools.chain.from_iterable(blocks)))
assert len(alphabet) == 13
vectors = {unit: tuple(sum(x == unit for x in block) for block in blocks) for unit in alphabet}
classes = []
unassigned = set(alphabet)
while unassigned:
    unit = min(unassigned)
    same = sorted(x for x in unassigned if vectors[x] == vectors[unit])
    classes.append(same)
    unassigned.difference_update(same)
assert sorted(classes) == sorted(c['members'] for c in review['signature_classes'])
for c in review['signature_classes']:
    assert all(list(vectors[x]) == c['counts'] for x in c['members'])
assert len(classes) == 11
singles = sorted(c[0] for c in classes if len(c) == 1)
assert singles == review['derived_constraints']['forced_singleton_units']
assert len(singles) == 9
assert sorted(c for c in classes if len(c) > 1) == [['a', 'n'], ['d', 'q']]

# Distinct signatures yield an interval count discrepancy >=3 on an old W^3.
for a, b in itertools.combinations(alphabet + ['UNOBSERVED'], 2):
    va = vectors.get(a, (0,) * 5)
    vb = vectors.get(b, (0,) * 5)
    if va != vb:
        assert any(abs(3 * (x-y)) >= 3 for x,y in zip(va,vb))

# Necessary signature condition is actually attainable for this certificate set.
# Each maximal proposed pool projects to a concatenation of complete cycles.
for block in blocks:
    for pool in classes:
        projected = [x for x in block * 3 if x in pool]
        assert len(projected) % len(pool) == 0
        for start in range(0, len(projected), len(pool)):
            assert sorted(projected[start:start+len(pool)]) == pool

# Independent finite sanity check of the interval bound on arbitrarily ordered
# three-cycle pools through size3. Algebra in the review supplies the general proof.
fixture_intervals = 0
for size in (2, 3):
    perms = list(itertools.permutations(range(size)))
    for first, second, third in itertools.product(perms, repeat=3):
        seq = first + second + third
        for lo in range(len(seq)+1):
            for hi in range(lo,len(seq)+1):
                counts = [seq[lo:hi].count(x) for x in range(size)]
                assert max(counts)-min(counts) <= 2
                fixture_intervals += 1
print(json.dumps({'status':'PASS_SOURCE_AND_SIGNATURE_ARITHMETIC_ONLY','old_reader_certificates':len(records),'present_working_units':len(alphabet),'forced_singletons':singles,'certificate_pool_minimum':len(classes),'finite_interval_sanity_checks':fixture_intervals,'limits':'No new native census, no original image verification, no historical alias-pool proof, no meanings; algebraic conclusion conditional on fixed disjoint pool contract.'}, indent=2))

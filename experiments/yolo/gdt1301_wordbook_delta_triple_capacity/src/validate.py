"""Separate validator: modular second differences and exhaustive finite toys."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]


def symbolic(rows, v):
    inside = set()
    starts = [set() for _ in range(v)]
    for row in rows:
        for a, b, c, d in zip(row, row[1:], row[2:], row[3:]):
            if (a-2*b+c) % v == (b-2*c+d) % v == 0:
                inside.add((b-a) % v)
        if len(row) >= 3:
            x, y, z = row[:3]
            if (x-2*y+z) % v == 0:
                starts[(2*x-y) % v].add((y-x) % v)
    return [inside | s for s in starts], inside, starts


def brute(rows, v, anchor):
    residues = set()
    for row in rows:
        previous = anchor
        codes = []
        for word in row:
            codes.append((word-previous) % v)
            previous = word
        for j in range(2, len(codes)):
            if len(set(codes[j-2:j+1])) == 1:
                residues.add(codes[j])
    return residues


def main():
    for name, digest in json.loads((HERE/'src/REGISTRATION_LOCK.json').read_text()).items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
    result = json.loads((HERE/'artifacts/RESULT.json').read_text())
    source = json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text())
    checked = {}
    for book, recipes in source.items():
        words = sorted(set(itertools.chain.from_iterable(r['words'] for r in recipes)))
        index = dict(zip(words, range(len(words))))
        rows = [[index[w] for w in r['words']] for r in recipes]
        capacities, interior, starts = symbolic(rows, len(words))
        r = result['books'][book]
        assert set(map(int, r['interior'])) == interior
        assert {a: s for a, s in enumerate(starts) if s} == {
            int(a): set(map(int, ds)) for a, ds in r['initial_by_anchor'].items()}
        maximum = max(map(len, capacities))
        assert r['maximum_capacity'] == maximum
        assert r['capacity_anchor_zero'] == len(capacities[0])
        assert r['maximizing_anchors'] == [a for a, s in enumerate(capacities) if len(s) == maximum]
        assert r['vocabulary_size'] == len(words)
        assert r['source_words'] == sum(map(len, rows))
        assert r['primary'] == ('PRIMARY_CAPACITY_EXCLUDED' if maximum < 4 else 'NOT_EXCLUDED')
        assert r['reader_sensitivity'] == {ed: maximum < n for ed,n in [('ZL3b',6),('IT2a',7),('RF1b',5)]}
        # Source readback independently via cumulative sums, at two anchors.
        for anchor in {0, len(words)-1}:
            for recipe, row in zip(recipes, rows):
                deltas = [(y-x) % len(words) for x,y in zip([anchor]+row, row)]
                recovered = [words[(anchor+s) % len(words)] for s in itertools.accumulate(deltas)]
                assert recovered == recipe['words']
        checked[book] = {'maximum_capacity': maximum, 'all_anchors_checked': len(words),
            'source_words': sum(map(len, rows)), 'interior_windows': sum(max(0,len(r)-3) for r in rows)}
    cases = 0
    # Every short sequence including degeneracy V=1, zero, order2, order3 steps.
    for v in range(1,5):
        for n in range(7):
            for row in itertools.product(range(v), repeat=n):
                sets, _, _ = symbolic([row], v)
                for anchor in range(v):
                    assert sets[anchor] == brute([row],v,anchor)
                    cases += 1
    # No bridge across paragraph boundaries, shared anchor only.
    reset_cases = 0
    for flat in itertools.product(range(3), repeat=5):
        for cut in range(6):
            rows = [flat[:cut],flat[cut:]]
            sets,_,_ = symbolic(rows,3)
            for anchor in range(3):
                assert sets[anchor] == brute(rows,3,anchor)
                reset_cases += 1
    examples = [([0,1,2,3],4),([0,2,0,2],4),([0,1,2,0],3),([1,1,1,1],4),([1,2,3],4)]
    for row,v in examples:
        assert symbolic([row],v)[0][0] == brute([row],v,0)
        assert brute([row],v,0)
    hits = json.loads((ROOT/'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json').read_text())
    eds = ['ZL3b','IT2a','RF1b']
    common = None
    for ed in eds:
        hh = [h for h in hits if h['edition'] == ed]
        forms = sorted({h['raw'] for h in hh})
        assert result['native_reader_forms'][ed] == forms
        coords = {(h['locus'],int(h['start_index']),h['raw']) for h in hh}
        common = coords if common is None else common & coords
    assert result['native_common_coordinates'] == [list(x) for x in sorted(common)]
    assert len({x[2] for x in common}) == 4
    output = {'status':'PASS','books':checked,'exhaustive_anchor_cases':cases,
        'reset_anchor_cases':reset_cases,'known_cycle_examples':len(examples),
        'scope':'Separate implementation by same root author; not independent data or blinded replication.'}
    (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()

"""Exhaustive tiny prefix tables; fixtures run before native output."""
from itertools import product, combinations
from pathlib import Path
from datetime import datetime, timezone
import json
from engine import derive


def parse(w, C):
    used = []
    while w:
        p = [c for c in C if w[:len(c)] == c]
        if not p:
            return None
        assert len(p) == 1
        used.append(p[0])
        w = w[len(p[0]):]
    return used


def run():
    universe = [w for n in range(1, 4) for w in product('ab', repeat=n)]
    books = []
    for mask in range(1, 1 << len(universe)):
        C = tuple(universe[i] for i in range(len(universe)) if mask >> i & 1)
        if all(not (a != b and b[:len(a)] == a) for a in C for b in C):
            parses = {w: parse(w, C) for w in universe}
            books.append((C, parses))
    sets = compatible = nontrivial = 0
    for size in range(1, 4):
        for W in combinations(universe, size):
            sets += 1
            cert = derive(W)
            assert cert['status'] == 'COMPLETE'
            R = [tuple(n['word']) for n in cert['nodes']]
            s = cert['summary']
            for C, parsed in books:
                if any(parsed[w] is None for w in W):
                    continue
                compatible += 1
                assert all(parse(r, C) is not None for r in R)
                assert all((f,) in C for f in s['F'])
                used_long = {c[0] for w in W for c in parsed[w] if len(c) > 1}
                for g in used_long:
                    nontrivial += 1
                    assert s['heads'][g]['bound'] is not None
                    assert len(C) >= s['heads'][g]['bound'] >= s['heads'][g]['direct_bound']
    named = []
    for words in [('a','ab','ac'), ('a','ba','bc'), ('aa','ab','ba','bb'), ('aba',)]:
        cert = derive(words)
        named.append({'W': words, 'certificate': cert})
    assert named[0]['certificate']['summary']['status'] == 'ALL_USED_CODES_SINGLETON'
    assert named[1]['certificate']['summary']['necessary_nontrivial_bound'] == 3
    assert named[2]['certificate']['summary']['necessary_nontrivial_bound'] == 4
    assert 'b' not in named[3]['certificate']['summary']['H']
    assert named[3]['certificate']['summary']['heads']['b']['bound'] == 2
    return {'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
            'word_sets': sets, 'prefix_codebooks': len(books), 'compatible_pairs': compatible,
            'used_long_head_checks': nontrivial, 'named': named}


if __name__ == '__main__':
    r = run()
    (Path(__file__).resolve().parents[1] / 'artifacts/FIXTURES.json').write_text(json.dumps(r, indent=2) + '\n')
    print({k: v for k, v in r.items() if k != 'named'})

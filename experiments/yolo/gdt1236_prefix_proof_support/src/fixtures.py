from itertools import product, combinations
from pathlib import Path
from datetime import datetime, timezone
import json
from engine import weighted


def closure(words):
    current = set(words)
    while True:
        more = {v[k:] for v in current for k in range(1, len(v)) if v[:k] in current}
        if more <= current:
            return current
        current |= more


def check(source):
    c = weighted(source)
    weights = dict(zip(map(tuple, c['universe']), c['weights']))
    for threshold in set(source.values()):
        expected = closure({w for w, n in source.items() if n >= threshold})
        assert expected == {w for w, n in weights.items() if n >= threshold}
    return c


def main():
    words = [p for n in (1, 2, 3) for p in product('ab', repeat=n)]
    cases = 0
    for size in (1, 2, 3):
        for group in combinations(words, size):
            for weights in product((1, 2, 3), repeat=size):
                check(dict(zip(group, weights)))
                cases += 1
    named = []
    for source in ({('a',): 5, ('a','b'): 7, ('b',): 1},
                   {('a',): 5, ('a','b'): 1},
                   {('a',): 9, ('a','b'): 8, ('b','a','b'): 6}):
        named.append({'source': [[list(w), n] for w,n in source.items()], 'certificate': check(source)})
    first = named[0]['certificate']; assert dict(zip(map(tuple,first['universe']),first['weights']))[('b',)] == 5
    result = {'status': 'PASS', 'cases': cases, 'named': named, 'completed_utc': datetime.now(timezone.utc).isoformat()}
    Path('experiments/yolo/gdt1236_prefix_proof_support/artifacts/FIXTURES.json').write_text(json.dumps(result,indent=2)+'\n')
    print({'status': result['status'], 'cases': cases})

if __name__ == '__main__': main()

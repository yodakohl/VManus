#!/usr/bin/env python3
"""Post-result finite certificate for the reported solver contradiction only.

Not preregistered, not a target rescan, and imports no model/solver code.
"""
import collections
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
A = E / 'artifacts'


def nonoverlap(text, piece):
    total = 0
    position = 0
    while position <= len(text) - len(piece):
        if text[position:position + len(piece)] == piece:
            total += 1
            position += len(piece)
        else:
            position += 1
    return total


def main():
    source = json.loads((E / 'src/SOURCE.json').read_text())
    all_cases = json.loads((A / 'CASES.json').read_text())
    cases = [c for c in all_cases if c['status'] == 'UNSAT_SOLVER']
    assert len(cases) == 1
    certificates = []
    for case in cases:
        assert case['writer'] == 'PREFIX'
        atoms = source['streams']['PREFIX']['atoms']
        counts = collections.Counter(atoms)
        words = case['words']
        text = ''.join(words)
        pieces = {w[i:j] for w in words for i in range(len(w))
                  for j in range(i + 1, len(w) + 1)}
        domains = {}
        for atom in ('BATH', 'WATER_OF'):
            maximum = min(max(map(len, words)),
                          (len(text) - len(atoms) + counts[atom]) // counts[atom])
            domains[atom] = sorted(p for p in pieces if len(p) <= maximum
                                  and sum(nonoverlap(w, p) for w in words) >= counts[atom])
        assert domains == {'BATH': ['o'], 'WATER_OF': ['o', 'y']}
        # Injectivity forces WATER_OF=y once BATH=o.
        starts = [i for i in range(len(atoms) - 1)
                  if atoms[i:i+2] == ['WATER_OF', 'BATH']]
        assert all(b >= a + 2 for a, b in zip(starts, starts[1:]))
        capacity = nonoverlap(text, 'yo')
        assert len(starts) == 15 and capacity == 1
        certificates.append(dict(edition=case['edition'], paragraph=case['paragraph'],
            writer=case['writer'], source_counts={a: counts[a] for a in domains},
            necessary_domains=domains, forced_by_injectivity={'BATH': 'o', 'WATER_OF': 'y'},
            disjoint_source_pair_starts=starts, required_yo=15, maximum_yo=capacity,
            conclusion='CONTRADICTION'))
    result = dict(status='PASS', scope='Post-result independent finite replay of all reported solver UNSAT cases, same author; no rescan or meaning validation',
        original_validator_preserved=True, solver_cases_checked=len(cases),
        input_sha256={n: hashlib.sha256((E / n).read_bytes()).hexdigest()
                      for n in ('src/SOURCE.json', 'artifacts/CASES.json')},
        certificates=certificates)
    (A / 'SUPPLEMENTARY_UNSAT_CERTIFICATE.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

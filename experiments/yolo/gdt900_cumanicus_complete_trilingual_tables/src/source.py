#!/usr/bin/env python3
"""Fixed cell/grapheme compilers; pairing never depends on target data."""
import itertools
import json
from pathlib import Path
SCHEMES = ['LETTER', 'PAIR_LEFT', 'PAIR_RIGHT']
TRAVERSALS = [{'columns': list(c), 'major': major} for c in itertools.permutations(range(3)) for major in ['ROW', 'COLUMN']]
def units(atoms, scheme):
    atoms = tuple(atoms)
    if scheme == 'LETTER':
        return tuple((a,) for a in atoms)
    if scheme == 'PAIR_LEFT':
        return tuple(atoms[i:i+2] for i in range(0, len(atoms), 2))
    assert scheme == 'PAIR_RIGHT'
    offset = len(atoms) % 2
    return ((atoms[:1],) if offset else ()) + tuple(atoms[i:i+2] for i in range(offset, len(atoms), 2))
def tables(source, variant, scheme, traversal):
    result = []
    for table in source['tables']:
        positions = [(r, c) for r in range(6) for c in traversal['columns']] if traversal['major'] == 'ROW' else [(r, c) for c in traversal['columns'] for r in range(6)]
        records = []
        for r, c in positions:
            cell = table['rows'][r][c]
            atoms = cell['graphemes']
            if cell['id'] in source['variant_cells']:
                atoms = cell['alternatives'][variant[cell['id']]]
            records.append({'id': cell['id'], 'units': units(atoms, scheme)})
        result.append({'id': table['id'], 'cells': records})
    return result

def load(path):
    p = json.loads(Path(path).read_text())
    assert p['schema'] == 'GDT900_FROZEN_SOURCE_V1'
    assert len(p['tables']) == 2 and len(p['variants']) == 4
    assert [t['id'] for t in p['tables']] == ['PRESENT', 'IMPERFECT']
    assert all(len(t['rows']) == 6 and all(len(r) == 3 for r in t['rows']) for t in p['tables'])
    for variant in p['variants']:
        for scheme in SCHEMES:
            for traversal in TRAVERSALS:
                ts = tables(p, variant, scheme, traversal)
                words = [tuple(c['units']) for t in ts for c in t['cells']]
                assert len(words) == len(set(words)) == 36
                for seq in words:
                    assert seq and all(len(u) in [1, 2] for u in seq)
    return p

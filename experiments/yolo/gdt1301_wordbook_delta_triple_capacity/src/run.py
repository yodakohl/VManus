"""Necessary whole-word delta capacity; no glyph-codebook fitting."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
SOURCE = ROOT / 'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
HITS = ROOT / 'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json'


def capacity(recipes):
    vocabulary = sorted({w for recipe in recipes for w in recipe['words']})
    assert vocabulary and all(isinstance(w, str) and w for w in vocabulary)
    ranks = {w: i for i, w in enumerate(vocabulary)}
    v = len(vocabulary)
    interior, initial = {}, defaultdict(dict)
    total_words = 0
    for recipe in recipes:
        words = recipe['words']
        rr = [ranks[w] for w in words]
        total_words += len(rr)
        dd = [(y-x) % v for x, y in zip(rr, rr[1:])]
        # Three consecutive transitions between FOUR actual source words.
        for j in range(len(dd)-2):
            if dd[j] == dd[j+1] == dd[j+2]:
                d = dd[j]
                interior.setdefault(d, {'recipe': recipe['id'], 'start': j,
                    'words': words[j:j+4], 'ranks': rr[j:j+4]})
        if len(dd) >= 2 and dd[0] == dd[1]:
            d = dd[0]
            a = (rr[0]-d) % v
            initial[a].setdefault(d, {'recipe': recipe['id'], 'words': words[:3],
                'ranks': rr[:3]})
        # Exact numerical channel readback, anchor zero.
        state = 0
        encoded = []
        for r in rr:
            encoded.append((r-state) % v)
            state = r
        state = 0
        decoded = []
        for d in encoded:
            state = (state+d) % v
            decoded.append(vocabulary[state])
        assert decoded == words
    counts = [len(set(interior) | set(initial[a])) for a in range(v)]
    best = max(counts)
    return {'vocabulary_size': v, 'recipes': len(recipes), 'source_words': total_words,
        'interior': {str(d): w for d, w in sorted(interior.items())},
        'initial_by_anchor': {str(a): {str(d): w for d, w in sorted(ds.items())}
            for a, ds in sorted(initial.items()) if ds},
        'capacity_anchor_zero': counts[0], 'maximum_capacity': best,
        'maximizing_anchors': [a for a, n in enumerate(counts) if n == best],
        'primary': 'PRIMARY_CAPACITY_EXCLUDED' if best < 4 else 'NOT_EXCLUDED',
        'reader_sensitivity': {ed: best < n for ed, n in {'ZL3b': 6, 'IT2a': 7, 'RF1b': 5}.items()},
        'roundtrip': 'PASS'}


def main():
    lock = json.loads((HERE/'src/REGISTRATION_LOCK.json').read_text())
    for path, digest in lock.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    hits = json.loads(HITS.read_text())
    forms = defaultdict(set)
    coords = defaultdict(set)
    for hit in hits:
        assert not hit['page'].startswith('f84')
        raw = hit['raw']
        assert len(hit['groups']) == 3
        assert all(g['ivtff_group_raw'] == raw and
            g['left_separator'] == g['right_separator'] == 'DEFINITE_SPACE' for g in hit['groups'])
        forms[hit['edition']].add(raw)
        coords[hit['edition']].add((hit['locus'], int(hit['start_index']), raw))
    assert {ed: len(ss) for ed, ss in forms.items()} == {'ZL3b': 6, 'IT2a': 7, 'RF1b': 5}
    common = set.intersection(*coords.values())
    assert len(common) == 4 and {c[2] for c in common} == {'sheol','okaiin','chol','ytaiin'}
    assert all(c[1] >= 2 for c in common)
    books = json.loads(SOURCE.read_text())
    result = {'native_common_coordinates': sorted(common),
        'native_reader_forms': {ed: sorted(ss) for ed, ss in forms.items()},
        'books': {book: capacity(recipes) for book, recipes in books.items()}}
    (HERE/'artifacts/RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({b: {k: r[k] for k in ['vocabulary_size','source_words','maximum_capacity','primary']}
        for b, r in result['books'].items()}, indent=2))


if __name__ == '__main__':
    main()

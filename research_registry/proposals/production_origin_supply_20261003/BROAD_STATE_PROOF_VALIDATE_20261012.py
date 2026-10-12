"""Replay existing integer certificates and source-free S3 scope fixture only."""
import hashlib
import json
from pathlib import Path

P = Path('research_registry/proposals/production_origin_supply_20261003')
D = Path('experiments/yolo/gdt1286_paragraph_additive_lattice/artifacts')

def product(a, b):
    return tuple(b[a[i]] for i in range(len(a)))

def inverse(a):
    return tuple(a.index(i) for i in range(len(a)))

def main():
    matrices = json.loads((D / 'MATRICES.json').read_text())
    certificates = json.loads((D / 'CERTIFICATES.json').read_text())
    receipts = {}
    for edition in ('ZL3b', 'IT2a'):
        a = matrices[edition]['matrix']
        c = certificates[edition]['coefficients']
        assert len(c) == 23 and all(len(row) == 23 for row in a)
        ca = [[sum(coefficient * a[int(index)][j] for index, coefficient in row.items())
               for j in range(23)] for row in c]
        assert ca == [[int(i == j) for j in range(23)] for i in range(23)]
        receipts[edition] = {'identity_dimension': 23, 'retained_matrix_rows': len(a), 'integer_left_inverse': True}
    toy_path = P / 'PARAGRAPH_STATE_SCOPE_RESULT_20261009.json'
    toy = json.loads(toy_path.read_text())
    a, c = toy['augmented_toy_counts'], toy['integer_left_inverse']
    assert [[sum(c[i][k] * a[k][j] for k in range(4)) for j in range(3)] for i in range(3)] == [[int(i == j) for j in range(3)] for i in range(3)]
    generators = [tuple(toy['three_state_maps'][s]) for s in ('A', 'B')]
    identity = (0, 1, 2)
    group = {identity}
    while True:
        expanded = group | {product(g, s) for g in group for s in generators}
        if expanded == group:
            break
        group = expanded
    assert len(group) == 6
    stabilizer = {g for g in group if g[0] == 0}
    assert len(stabilizer) == 2 and {g[0] for g in group} == {0, 1, 2}
    normal = all(product(product(inverse(g), h), g) in stabilizer for g in group for h in stabilizer)
    assert not normal
    traces = {}
    for word in toy['toy_words']:
        state, trace = 0, [0]
        for letter in word:
            state = toy['three_state_maps'][letter][state]
            trace.append(state)
        assert state == 0 and trace == toy['traces_from_zero'][word]
        traces[word] = trace
    result = {'status': 'PASS_INHERITED_CERTIFICATES_AND_SOURCE_FREE_COUNTERMODEL',
              'readers': receipts, 'toy': {'group_order': len(group), 'orbit_size': 3, 'stabilizer_order': 2, 'stabilizer_normal': normal, 'traces': traces, 'integer_left_inverse': True},
              'hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (D / 'MATRICES.json', D / 'CERTIFICATES.json', toy_path)},
              'limit': 'Certificate arithmetic and artificial group fixture only. Infinite-group theorem requires the written proof review; no new native census, semantic evidence or state-machine fit.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == '__main__':
    main()

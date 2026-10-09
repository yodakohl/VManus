"""Independent certificate checker; imports no experimental engine."""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import gzip, json, hashlib

D = Path(__file__).resolve().parents[1]
A = D / 'artifacts'


def check(W, cert):
    W = set(map(tuple, W))
    nodes = cert['nodes']
    ordered = []
    seeds = set()
    seen = set()
    for index, n in enumerate(nodes):
        w = tuple(n['word'])
        assert w and w not in seen
        seen.add(w)
        p = n['parents']
        if p is None:
            assert w in W
            seeds.add(w)
        else:
            i, j = p
            assert 0 <= i < index and 0 <= j < index
            assert ordered[i] + w == ordered[j]
        ordered.append(w)
    assert seeds == W and cert['status'] == 'COMPLETE'
    for w in seen:
        for cut in range(1, len(w)):
            if w[:cut] in seen:
                assert w[cut:] in seen
    used = {x for w in W for x in w}
    first = set()
    singleton = set()
    pairs = set()
    second = defaultdict(set)
    for w in seen:
        first.add(w[0])
        if len(w) == 1:
            singleton.add(w[0])
        else:
            second[w[0]].add(w[1])
        if len(w) == 2:
            pairs.add(w)
    reach = {a: {a} for a in used}
    for a, b in pairs:
        reach[b].add(a)
    for middle in sorted(used):
        for target in sorted(used):
            if middle in reach[target]:
                reach[target].update(reach[middle])
    heads = {}
    for g in sorted(used):
        N = reach[g]
        assert N <= first | {g}
        conflict = sorted(N & singleton)
        assert bool(conflict) == (g in singleton)
        direct = len(first | {g}) - 1 + max(1, len(second[g]))
        total = sum(max(1, len(second[h])) if h in N else 1 for h in first | {g})
        heads[g] = {'predecessors': sorted(N), 'forced_conflict': conflict,
                    'direct_bound': None if conflict else direct, 'bound': None if conflict else total}
    P = {w for w in seen if all(w[:cut] not in seen for cut in range(1, len(w)))}
    for w in seen:
        tail = w
        while tail:
            codes = [tail[:cut] for cut in range(1, len(tail) + 1) if tail[:cut] in P]
            assert len(codes) == 1
            tail = tail[len(codes[0]):]
    values = [v['bound'] for v in heads.values() if v['bound'] is not None]
    lower = min(values) if values else None
    summary = {'used_signs': sorted(used), 'H': sorted(first), 'F': sorted(singleton),
               'T': [list(t) for t in sorted(pairs)], 'second_signs': {h: sorted(second[h]) for h in used},
               'heads': heads, 'necessary_nontrivial_bound': lower,
               'prefix_basis': [list(w) for w in sorted(P, key=lambda w: (len(w), w))],
               'prefix_basis_size': len(P), 'status': 'ALL_USED_CODES_SINGLETON' if not values else 'NECESSARY_BOUND_ONLY',
               'caps': {str(k): 'EXCLUDED_NONTRIVIAL' if not values or lower > k else 'NOT_EXCLUDED' for k in (22, 26, 28)}}
    assert summary == cert['summary']
    return {'status': 'PASS', 'initial_types': len(W), 'closure_nodes': len(nodes),
            'derived_nodes': len(nodes) - len(W), 'prefix_basis_size': len(P), 'summary_recomputed': True}


def main():
    fixtures = json.loads((A / 'FIXTURES.json').read_text())
    fixture_checks = [check(f['W'], f['certificate']) for f in fixtures['named']]
    lock = json.loads((A / 'REGISTRATION_LOCK.json').read_text())
    for p, h in lock['files'].items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == h, p
    S = json.loads((D / 'src/SPEC.json').read_text())
    groups = json.loads(gzip.decompress(Path(S['source']).read_bytes()))
    result = json.loads((A / 'RESULT.json').read_text())
    checks = {}
    for reader in S['readers']:
        cert = json.loads(gzip.decompress((A / ('CERTIFICATE_' + reader + '.json.gz')).read_bytes()))
        W = {tuple(r['units']) for r in groups[reader]}
        assert len(groups[reader]) == result['readers'][reader]['groups']
        assert len(W) == result['readers'][reader]['types']
        assert cert['summary'] == result['readers'][reader]['summary']
        checks[reader] = check(W, cert)
    output = {'status': 'PASS', 'validated_utc': datetime.now(timezone.utc).isoformat(),
              'fixtures': fixture_checks, 'readers': checks, 'immutable_input_hashes': 'PASS',
              'source_scope': 'Immutable1233eligible groups; its original selector-first reconstruction retained. No new source query.'}
    (A / 'VALIDATION.json').write_text(json.dumps(output, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()

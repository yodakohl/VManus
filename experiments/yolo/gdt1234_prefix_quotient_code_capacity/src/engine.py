"""Finite left-quotient certificate and necessary prefix-code bounds."""
import time


def derive(words, seconds=120):
    started = time.monotonic()
    words = sorted(set(map(tuple, words)), key=lambda w: (len(w), w))
    nodes = [{'word': list(w), 'parents': None} for w in words]
    known = {w: i for i, w in enumerate(words)}
    rounds = 0
    while True:
        rounds += 1
        before = len(nodes)
        for vi in range(before):
            v = tuple(nodes[vi]['word'])
            for cut in range(1, len(v)):
                u, r = v[:cut], v[cut:]
                if u in known and r not in known:
                    known[r] = len(nodes)
                    nodes.append({'word': list(r), 'parents': [known[u], vi]})
            if time.monotonic() - started > seconds:
                return {'status': 'UNKNOWN_TIMEOUT', 'nodes': nodes, 'rounds': rounds}
        if len(nodes) == before:
            break
    return {'status': 'COMPLETE', 'nodes': nodes, 'rounds': rounds,
            'summary': summarize(known, {x for w in words for x in w})}


def summarize(R, used):
    R = set(R)
    H = {w[0] for w in R}
    F = {w[0] for w in R if len(w) == 1}
    T = {(w[0], w[1]) for w in R if len(w) == 2}
    second = {h: sorted({w[1] for w in R if w[0] == h and len(w) > 1}) for h in used}
    heads = {}
    for g in sorted(used):
        N = {g}
        while True:
            new = N | {a for a, b in T if b in N}
            if new == N:
                break
            N = new
        assert N <= H | {g}
        conflict = sorted(N & F)
        heads[g] = {'predecessors': sorted(N), 'forced_conflict': conflict,
                    'direct_bound': None if conflict else len(H | {g}) + max(1, len(second[g])) - 1,
                    'bound': None if conflict else len(H | {g}) + sum(max(1, len(second[h])) - 1 for h in N)}
    bounds = [v['bound'] for v in heads.values() if v['bound'] is not None]
    P = sorted((w for w in R if not any(w[:i] in R for i in range(1, len(w)))), key=lambda w: (len(w), w))
    bound = min(bounds) if bounds else None
    return {'used_signs': sorted(used), 'H': sorted(H), 'F': sorted(F), 'T': [list(e) for e in sorted(T)],
            'second_signs': second, 'heads': heads, 'necessary_nontrivial_bound': bound,
            'prefix_basis': [list(w) for w in P], 'prefix_basis_size': len(P),
            'status': 'ALL_USED_CODES_SINGLETON' if not bounds else 'NECESSARY_BOUND_ONLY',
            'caps': {str(k): 'EXCLUDED_NONTRIVIAL' if not bounds or bound > k else 'NOT_EXCLUDED' for k in (22, 26, 28)}}

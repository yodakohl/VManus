"""Finite shared-domain conjunction. Pure generic calculation, no source access."""
import itertools
import time


def compute(roles, atoms, deadline=float('inf')):
    universes = {a: sorted(set().union(*(set(c['domains'].get(a, [])) for role in roles for c in role))) for a in atoms}
    full = {a: (1 << len(u)) - 1 for a, u in universes.items()}
    index = {a: {v: i for i, v in enumerate(u)} for a, u in universes.items()}
    def masks(c):
        return tuple(sum(1 << index[a][v] for v in c['domains'][a]) if a in c['domains'] else full[a] for a in atoms)
    encoded = {c['index']: masks(c) for role in roles for c in role}
    factors = []
    support = {str(c['index']): 0 for role in roles for c in role}
    eligible_total = surviving_total = 0
    for prefix in itertools.product(*roles[:-1]):
        if time.monotonic() > deadline:
            raise TimeoutError('finite run ceiling; no partial absence decision')
        leaves = {c['leaf'] for c in prefix}
        eligible = surviving = 0
        if len(leaves) == len(prefix):
            common = tuple(full[a] for a in atoms)
            for c in prefix:
                common = tuple(x & y for x, y in zip(common, encoded[c['index']]))
            for j, c in enumerate(roles[-1]):
                if c['leaf'] in leaves:
                    continue
                eligible |= 1 << j
                if all(x & y for x, y in zip(common, encoded[c['index']])):
                    surviving |= 1 << j
                    support[str(c['index'])] += 1
            n = surviving.bit_count()
            for c in prefix:
                support[str(c['index'])] += n
        eligible_total += eligible.bit_count()
        surviving_total += surviving.bit_count()
        factors.append([*[c['index'] for c in prefix], format(eligible, 'x'), format(surviving, 'x')])
    return dict(factors=factors, case_support=support, distinct_leaf_tuples=eligible_total,
                surviving_tuples=surviving_total)

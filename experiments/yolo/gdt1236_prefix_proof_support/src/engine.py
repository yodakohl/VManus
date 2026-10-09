"""Maximum bottleneck of all finite prefix-quotient proofs."""
import time


def weighted(source, seconds=120):
    start = time.monotonic()
    universe = sorted({w[k:] for w in source for k in range(len(w))}, key=lambda w: (len(w), w))
    ids = {w: i for i, w in enumerate(universe)}
    weight = [0] * len(universe)
    last = [-1] * len(universe)
    events = []
    for w in sorted(source, key=lambda w: (len(w), w)):
        i = ids[w]
        weight[i] = source[w]
        last[i] = len(events)
        events.append([i, source[w], None])
    edges = [(ids[v[:k]], j, ids[v[k:]]) for j, v in enumerate(universe)
             for k in range(1, len(v)) if v[:k] in ids]
    rounds = 0
    while True:
        rounds += 1
        changed = False
        for a, b, r in edges:
            value = min(weight[a], weight[b])
            if value > weight[r]:
                events.append([r, value, [last[a], last[b]]])
                weight[r] = value
                last[r] = len(events) - 1
                changed = True
        if time.monotonic() - start > seconds:
            raise TimeoutError('weighted proof time cap')
        if not changed:
            break
    return {'universe': [list(w) for w in universe], 'weights': weight, 'final_event': last,
            'events': events, 'rounds': rounds, 'edges': len(edges)}

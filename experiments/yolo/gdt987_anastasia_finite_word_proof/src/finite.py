"""Bounded complete enumeration of fixed, word-aligned prefix-code equations."""
import bisect
import collections
import time


class Limit(Exception):
    pass


def solve(atoms, words, seconds=10, max_nodes=500000, forbidden=None):
    start = time.monotonic()
    deadline = start + seconds
    text = ''.join(words)
    n = len(text)
    counts = collections.Counter(atoms)
    word_ends = []
    offset = 0
    limit = [0] * (n + 1)
    starts = []
    for word in words:
        starts.append(offset)
        end = offset + len(word)
        for j in range(offset, end):
            limit[j] = end
        word_ends.append(end)
        offset = end
    if not words or not atoms:
        raise ValueError('nonempty complete source and target required')
    longest = max(map(len, words))
    upper = {a: min(longest, (n - len(atoms) + k) // k) for a, k in counts.items()}
    pieces = {w[i:j] for w in words for i in range(len(w))
              for j in range(i + 1, len(w) + 1)}
    occurrences = {p: sum(w.count(p) for w in words) for p in pieces}
    forced_starts = {p: sum(w.startswith(p) for w in words) for p in pieces}
    domains = {a: {p for p in pieces if len(p) <= upper[a]
                  and occurrences[p] >= k and forced_starts[p] <= k
                  and (forbidden is None or (a, p) != tuple(forbidden))}
               for a, k in counts.items()}
    nodes = 0
    prunes = collections.Counter()
    code = {}
    solution = None
    remaining = [None] * (len(atoms) + 1)
    remaining[-1] = {}
    for i in range(len(atoms) - 1, -1, -1):
        remaining[i] = remaining[i + 1].copy()
        a = atoms[i]
        remaining[i][a] = remaining[i].get(a, 0) + 1
    suffix_cap = {}

    def capacity(value, position):
        if value not in suffix_cap:
            length = len(value)
            table = [0] * (n + 1)
            for j in range(n - 1, -1, -1):
                table[j] = (1 + table[j + length]
                            if j + length <= limit[j] and text.startswith(value, j)
                            else table[j + 1])
            suffix_cap[value] = table
        return suffix_cap[value][position]

    def walk(i, pos):
        nonlocal nodes, solution
        nodes += 1
        if nodes > max_nodes or (nodes % 128 == 0 and time.monotonic() >= deadline):
            raise Limit
        if i == len(atoms):
            if pos == n:
                solution = dict(code)
                return True
            prunes['terminal_length'] += 1
            return False
        if pos == n:
            prunes['target_exhausted'] += 1
            return False
        low = high = 0
        for a, k in remaining[i].items():
            if a in code:
                value = code[a]
                low += k * len(value)
                high += k * len(value)
                if k > 1 and capacity(value, pos) < k:
                    prunes['assigned_suffix_capacity'] += 1
                    return False
            else:
                low += k * minimum[a]
                high += k * maximum[a]
        if not low <= n - pos <= high:
            prunes['remaining_length'] += 1
            return False
        if len(word_ends) - bisect.bisect_right(word_ends, pos) > len(atoms) - i:
            prunes['remaining_word_seams'] += 1
            return False
        a = atoms[i]
        if a in code:
            v = code[a]
            if pos + len(v) <= limit[pos] and text.startswith(v, pos):
                return walk(i + 1, pos + len(v))
            prunes['assigned_value_mismatch'] += 1
            return False
        last = min(limit[pos], pos + maximum[a])
        for end in range(pos + minimum[a], last + 1):
            value = text[pos:end]
            if value not in domains[a]:
                continue
            if any(value.startswith(v) or v.startswith(value) for v in code.values()):
                continue
            if remaining[i][a] > 1 and capacity(value, pos) < remaining[i][a]:
                continue
            code[a] = value
            if walk(i + 1, end):
                return True
            del code[a]
        prunes['all_new_value_branches_exhausted'] += 1
        return False

    empty = sorted(a for a in domains if not domains[a])
    try:
        if empty:
            status = 'UNSAT_FINITE'
            prunes['empty_initial_domain'] += 1
        else:
            minimum = {a: min(map(len, d)) for a, d in domains.items()}
            maximum = {a: max(map(len, d)) for a, d in domains.items()}
            status = 'SAT' if walk(0, 0) else 'UNSAT_FINITE'
    except Limit:
        status = 'UNKNOWN_FINITE_LIMIT'
    result = dict(status=status, nodes=nodes, prunes=dict(sorted(prunes.items())),
                  empty_initial_domains=empty,
                  initial_domain_sizes={a: len(d) for a, d in sorted(domains.items())},
                  elapsed_seconds=time.monotonic() - start)
    if status == 'SAT':
        result['code'] = solution
    return result

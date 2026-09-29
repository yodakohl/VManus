"""Exact finite encoding of a complete nonempty prefix-code equation."""
from collections import Counter
import time

from ortools.sat.python import cp_model


def suffix_classes(text):
    """Return SA, inverse SA and all (lo, hi, min_length, max_length) classes.

    Each class is an edge of the compressed trie of nonempty target suffixes.
    Inclusive suffix-rank intervals contain exactly the suffixes beginning with
    each represented substring; every length in the class range is represented.
    """
    n = len(text)
    sa = sorted(range(n), key=lambda p: text[p:])
    rank = [0] * n
    lcp = [0] * n
    for r, p in enumerate(sa):
        rank[p] = r
        if r:
            q = sa[r - 1]
            k = 0
            while p + k < n and q + k < n and text[p + k] == text[q + k]:
                k += 1
            lcp[r] = k
    groups = {}
    for length in range(1, n + 1):
        lo = 0
        while lo < n:
            if n - sa[lo] < length:
                lo += 1
                continue
            hi = lo
            while hi + 1 < n and lcp[hi + 1] >= length:
                hi += 1
            if (lo, hi) not in groups:
                groups[lo, hi] = [length, length]
            else:
                assert groups[lo, hi][1] == length - 1
                groups[lo, hi][1] = length
            lo = hi + 1
    return sa, rank, [(lo, hi, *bounds) for (lo, hi), bounds in sorted(groups.items())]


def build(atoms, text, domains=None, hints=None):
    """Domains are optional proved restrictions, never inferred glosses."""
    n, m = len(text), len(atoms)
    model = cp_model.CpModel()
    if not atoms or n < m:
        model.add(False)
        return model, {}, [], {'classes': 0}
    sa, ranks, classes = suffix_classes(text)
    counts = Counter(atoms)
    variables, intervals = {}, []
    for number, atom in enumerate(sorted(counts)):
        bound = (n - m + counts[atom]) // counts[atom]
        lo = model.new_int_var(0, n - 1, f'lo{number}')
        hi = model.new_int_var(0, n - 1, f'hi{number}')
        length = model.new_int_var(1, bound, f'len{number}')
        if domains is not None and atom in domains:
            rows = []
            for word in domains[atom]:
                positions = [r for r, p in enumerate(sa) if text.startswith(word, p)]
                assert positions and len(word) <= bound
                rows.append((positions[0], positions[-1], len(word)))
            model.add_allowed_assignments([lo, hi, length], rows)
        else:
            lowlen = model.new_int_var(1, bound, f'minlen{number}')
            highlen = model.new_int_var(1, bound, f'maxlen{number}')
            rows = [(a, b, c, min(d, bound)) for a, b, c, d in classes
                    if c <= bound and b - a + 1 >= counts[atom]]
            model.add_allowed_assignments([lo, hi, lowlen, highlen], rows)
            model.add(length >= lowlen)
            model.add(length <= highlen)
        size = model.new_int_var(1, n, f'size{number}')
        end = model.new_int_var(1, n, f'end{number}')
        model.add(size == hi - lo + 1)
        model.add(end == hi + 1)
        intervals.append(model.new_interval_var(lo, size, end, f'code{number}'))
        variables[atom] = (lo, hi, length)
        if hints is not None:
            word = hints[atom]
            positions = [r for r, p in enumerate(sa) if text.startswith(word, p)]
            for var, value in zip((lo, hi, length), (positions[0], positions[-1], len(word))):
                model.add_hint(var, value)
    model.add_no_overlap(intervals)
    boundaries = [model.new_int_var(i, n - m + i, f'p{i}') for i in range(m + 1)]
    model.add(boundaries[0] == 0)
    model.add(boundaries[-1] == n)
    hint_position = 0
    for i, atom in enumerate(atoms):
        lo, hi, length = variables[atom]
        model.add(boundaries[i + 1] == boundaries[i] + length)
        rank = model.new_int_var(0, n - 1, f'rank{i}')
        model.add_element(boundaries[i], ranks, rank)
        model.add(rank >= lo)
        model.add(rank <= hi)
        if hints is not None:
            model.add_hint(boundaries[i], hint_position)
            hint_position += len(hints[atom])
    if hints is not None:
        model.add_hint(boundaries[-1], hint_position)
    return model, variables, boundaries, {'classes': len(classes), 'types': len(counts),
                                         'occurrences': m, 'characters': n}


def solve(atoms, text, domains=None, seconds=30, workers=4, hints=None):
    started = time.monotonic()
    model, variables, boundaries, meta = build(atoms, text, domains, hints)
    built = time.monotonic()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1097
    status = solver.solve(model)
    result = dict(meta, status=solver.status_name(status), build_seconds=built-started,
                  solver_seconds=solver.wall_time, total_seconds=time.monotonic()-started,
                  conflicts=solver.num_conflicts, branches=solver.num_branches,
                  response_stats=solver.response_stats(), full_code=None, alignment=None)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        positions = [solver.value(p) for p in boundaries]
        code = {}
        rows = []
        for i, atom in enumerate(atoms):
            word = text[positions[i]:positions[i+1]]
            if atom in code:
                assert code[atom] == word
            code[atom] = word
            rows.append(dict(index=i, atom=atom, start=positions[i], end=positions[i+1], code=word))
        result.update(full_code=code, alignment=rows,
                      suffix_intervals={a: [solver.value(v) for v in vs] for a, vs in variables.items()})
    return result

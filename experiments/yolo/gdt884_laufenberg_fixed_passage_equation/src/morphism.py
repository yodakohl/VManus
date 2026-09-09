"""Exact erasing-morphism search for one fixed source/target word equation.

Symbols are opaque strings.  No normalization, injectivity, language model, or
minimum image length is imposed.  Every supplied source group must have a
nonempty image.  Interrupted searches never report UNSAT or completeness.
"""
import math
import time
from collections import Counter


def solve(groups, target, node_limit=1000000, seconds=60, max_solutions=1000):
    started = time.monotonic()
    if not isinstance(groups, list) or any(not isinstance(group, list) for group in groups):
        raise ValueError('groups must be a list of symbol lists')
    if any(not isinstance(symbol, str) or not symbol for group in groups for symbol in group):
        raise ValueError('each symbol identifier must be a nonempty string')
    if not isinstance(target, str):
        raise ValueError('target must be a string')
    if type(node_limit) is not int or node_limit < 0:
        raise ValueError('node_limit must be a nonnegative integer')
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0:
        raise ValueError('seconds must be a finite nonnegative number')
    if type(max_solutions) is not int or max_solutions < 1:
        raise ValueError('max_solutions must be a positive integer')

    deadline = started + seconds
    nodes = 0
    solutions = []
    halt = None

    def output(complete=False, reason=None):
        status = ('SAT_COMPLETE' if solutions else 'UNSAT') if complete else ('SAT_PARTIAL' if solutions else 'UNKNOWN_BUDGET')
        return dict(status=status, nodes=nodes, reason=reason or halt or 'SEARCH_EXHAUSTED', solutions=solutions)

    # Check node limits before wall time for a deterministic reason when both bind.
    if node_limit == 0:
        return output(reason='NODE_LIMIT')
    if time.monotonic() >= deadline:
        return output(reason='TIME_LIMIT')
    if any(not group for group in groups):
        return output(complete=True, reason='EMPTY_SOURCE_GROUP')

    flat_symbols = [symbol for group in groups for symbol in group]
    symbols = list(dict.fromkeys(flat_symbols))  # Fixed first-occurrence order.
    indexes = {symbol: i for i, symbol in enumerate(symbols)}
    source = [indexes[symbol] for symbol in flat_symbols]
    count_map = Counter(source)
    frequencies = [count_map[i] for i in range(len(symbols))]
    group_masks = sorted({sum(1 << indexes[symbol] for symbol in set(group)) for group in groups})
    size, target_size = len(symbols), len(target)

    # reachable[d][r]: r is an unbounded nonnegative integer combination of
    # frequencies for variables d,...,size-1.  Exactly size+1 rows suffice,
    # because the next newly bound variable always follows first-occurrence order.
    reachable = [None] * (size + 1)
    reachable[size] = bytearray(target_size + 1)
    reachable[size][0] = 1
    for depth in range(size - 1, -1, -1):
        if time.monotonic() >= deadline:
            return output(reason='TIME_LIMIT')
        row = bytearray(reachable[depth + 1])
        frequency = frequencies[depth]
        for residual in range(frequency, target_size + 1):
            if row[residual - frequency]:
                row[residual] = 1
        reachable[depth] = row

    images = [None] * size  # None is unbound; '' is a bound, erasing image.

    def visit(position, offset, depth, residual, positive_mask):
        nonlocal nodes, halt
        if halt:
            return
        if nodes >= node_limit:
            halt = 'NODE_LIMIT'
            return
        if time.monotonic() >= deadline:
            halt = 'TIME_LIMIT'
            return
        nodes += 1

        # A group image is nonempty iff at least one of its symbols is positive.
        bound_mask = (1 << depth) - 1
        required_mask = 0
        for group_mask in group_masks:
            if group_mask & positive_mask:
                continue
            candidates = group_mask & ~bound_mask
            if not candidates:
                return
            if candidates & (candidates - 1) == 0:
                required_mask |= candidates
        minimum = sum(frequencies[i] for i in range(depth, size) if required_mask & (1 << i))
        if residual < minimum or not reachable[depth][residual - minimum]:
            return

        # Consume every already-bound symbol, checking exact target substrings.
        while position < len(source):
            symbol_index = source[position]
            image = images[symbol_index]
            if image is None:
                break
            if not target.startswith(image, offset):
                return
            offset += len(image)
            position += 1
        if position == len(source):
            if offset != target_size:
                return
            assert depth == size and residual == 0
            mapping = {symbol: images[indexes[symbol]] for symbol in sorted(symbols)}
            spans = []
            end = 0
            for group in groups:
                start = end
                end += sum(len(mapping[symbol]) for symbol in group)
                assert end > start
                spans.append([start, end])
            assert end == target_size
            solutions.append(dict(mapping=mapping, group_spans=spans))
            if len(solutions) >= max_solutions:
                halt = 'SOLUTION_LIMIT'
            return

        symbol_index = source[position]
        assert symbol_index == depth
        minimum_length = int(bool(required_mask & (1 << depth)))
        other_minimum = minimum - minimum_length * frequencies[depth]
        maximum_length = min(target_size - offset, (residual - other_minimum) // frequencies[depth])
        # Each length vector is visited once; its images are forced by prefixes.
        for length in range(minimum_length, maximum_length + 1):
            images[depth] = target[offset:offset + length]
            visit(position, offset, depth + 1, residual - frequencies[depth] * length,
                  positive_mask | ((1 << depth) if length else 0))
            images[depth] = None
            if halt:
                break

    visit(0, 0, 0, target_size, 0)
    return output(complete=halt is None)


def selftest():
    """Small source-free fixtures plus independent exhaustive tiny-map checks."""
    import itertools

    def replay(groups, target, solution):
        mapping = solution['mapping']
        expected_symbols = {symbol for group in groups for symbol in group}
        assert set(mapping) == expected_symbols
        outputs = [''.join(mapping[symbol] for symbol in group) for group in groups]
        assert all(outputs) and ''.join(outputs) == target
        offset = 0
        for output, span in zip(outputs, solution['group_spans']):
            assert span == [offset, offset + len(output)]
            offset += len(output)
        assert len(outputs) == len(solution['group_spans'])

    fixtures = [
        ('erasing_image_allowed', [['A', 'B', 'A']], 'b', 'SAT_COMPLETE'),
        ('homophony_allowed', [['A'], ['B']], 'aa', 'SAT_COMPLETE'),
        ('repeated_image_conflict', [['A'], ['A']], 'ab', 'UNSAT'),
        ('group_nonempty', [['A'], ['B']], 'a', 'UNSAT'),
        ('empty_source_group', [[]], '', 'UNSAT'),
        ('empty_equation', [], '', 'SAT_COMPLETE'),
    ]
    report = []
    for name, groups, target, expected in fixtures:
        result = solve(groups, target)
        assert result['status'] == expected, (name, result)
        for solution in result['solutions']:
            replay(groups, target, solution)
        report.append(dict(case=name, status='PASS'))
    erased = solve([['A', 'B', 'A']], 'b')['solutions']
    assert erased == [dict(mapping={'A': '', 'B': 'b'}, group_spans=[[0, 1]])]
    assert solve([['A']], 'a', node_limit=0)['status'] == 'UNKNOWN_BUDGET'
    assert solve([['A']], 'a', seconds=0)['reason'] == 'TIME_LIMIT'
    limited = solve([['A', 'B']], 'a', max_solutions=1)
    assert limited['status'] == 'SAT_PARTIAL' and limited['reason'] == 'SOLUTION_LIMIT'
    report.append(dict(case='budget_statuses', status='PASS'))

    # Brute force over every image word on {a,b}, not prefix/length DFS.
    # A used image longer than the target cannot be part of a solution.
    cases = 0
    targets = ['', 'a', 'b', 'aa', 'ab', 'ba', 'bb']
    for length in range(1, 4):
        for flat in itertools.product(['A', 'B'], repeat=length):
            for cuts in itertools.product([False, True], repeat=length - 1):
                groups, current = [], [flat[0]]
                for cut, symbol in zip(cuts, flat[1:]):
                    if cut:
                        groups.append(current)
                        current = []
                    current.append(symbol)
                groups.append(current)
                symbols = sorted(set(flat))
                for target in targets:
                    candidates = [''.join(word) for n in range(len(target) + 1) for word in itertools.product('ab', repeat=n)]
                    expected = set()
                    for images in itertools.product(candidates, repeat=len(symbols)):
                        mapping = dict(zip(symbols, images))
                        outputs = [''.join(mapping[symbol] for symbol in group) for group in groups]
                        if all(outputs) and ''.join(outputs) == target:
                            expected.add(tuple(sorted(mapping.items())))
                    result = solve(groups, target)
                    assert result['status'] in ['UNSAT', 'SAT_COMPLETE']
                    found = {tuple(sorted(solution['mapping'].items())) for solution in result['solutions']}
                    assert found == expected, (groups, target, result, expected)
                    assert len(found) == len(result['solutions'])
                    for solution in result['solutions']:
                        replay(groups, target, solution)
                    cases += 1
    report.append(dict(case='independent_exhaustive_tiny_maps', cases=cases, status='PASS'))
    return report


if __name__ == '__main__':
    import json

    print(json.dumps(selftest(), sort_keys=True, indent=2))

#!/usr/bin/env python3
"""Independent finite square/capacity proof checker; never calls the solver.

Only INPUT.json and ANALYTIC_CERTIFICATE.json supply research data.  Substring
capacity uses interval dynamic programming, independently of greedy witnesses.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

E = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def maximum_disjoint(text, image):
    """Maximum number of pairwise disjoint fixed-string occurrence intervals."""
    if not image:
        raise ValueError('empty images impose no occurrence-capacity constraint')
    size, width = len(text), len(image)
    optimum = [0] * (size + 1)
    for position in range(size - 1, -1, -1):
        optimum[position] = optimum[position + 1]
        if text.startswith(image, position):
            optimum[position] = max(optimum[position], 1 + optimum[position + width])
    return optimum[0]


def check_case(groups, target, certificate):
    assert len(groups) >= 3
    assert groups[1]['codes'] == groups[2]['codes'] == ['A1', 'C1']
    assert not {'A1', 'C1'} & set(groups[0]['codes'])
    assert all(group['codes'] for group in groups)
    flat = [symbol for group in groups for symbol in group['codes']]
    frequencies = Counter(flat)
    remaining = Counter(symbol for group in groups[3:] for symbol in group['codes'])
    singleton_positions = {i: symbol for i, symbol in enumerate(flat) if frequencies[symbol] == 1}
    assert target.count('x') == 1
    x_position = target.index('x')
    x_suffix = target[x_position + 1:]
    after_x_letters = Counter(x_suffix)

    expected = {}
    squares = 0
    for start in range(1, len(target)):
        for width in range(1, (len(target) - start) // 2 + 1):
            word = target[start:start + width]
            end = start + 2 * width
            if word != target[start + width:end]:
                continue
            squares += 1
            # This fixed target satisfies the length condition at every square.
            # Stop if the certificate's two-reason schema is insufficient.
            assert len(target) - end >= len(groups) - 3
            for split in range(width + 1):
                images = {'A1': word[:split], 'C1': word[split:]}
                shortages = {}
                for symbol, image in images.items():
                    if image:
                        capacity = maximum_disjoint(target[end:], image)
                        if capacity < remaining[symbol]:
                            shortages[symbol] = dict(image=image, required=remaining[symbol], available=capacity)
                if shortages:
                    expected[start, width, split] = dict(images=images, reason='substring_capacity', shortages=shortages)
                    continue
                allocations = {}
                for source_position, symbol in singleton_positions.items():
                    after_slot = Counter(flat[source_position + 1:])
                    required = Counter()
                    for known_symbol, image in images.items():
                        for letter in image:
                            required[letter] += after_slot[known_symbol]
                    violations = {letter: dict(required=count, available=after_x_letters[letter])
                                  for letter, count in required.items() if count > after_x_letters[letter]}
                    allocations[source_position] = dict(code=symbol, violations=violations)
                # Every occurrence of the target's unique x must belong to one
                # of these singleton-code images, even when other images erase.
                assert all(row['violations'] for row in allocations.values()), (start, width, split)
                expected[start, width, split] = dict(images=images, reason='unique_x_tail', allocations=allocations)

    assert certificate['status'] == 'UNSAT_ANALYTIC'
    assert certificate['target_length'] == len(target)
    assert certificate['source_units'] == len(flat)
    assert certificate['source_types'] == len(frequencies)
    assert certificate['square_split_count'] == len(expected)
    assert certificate['survivors'] == []
    reasons = Counter(row['reason'] for row in expected.values())
    assert certificate['substring_rejected'] == reasons['substring_capacity']
    assert certificate['unique_x_rejected'] == reasons['unique_x_tail']

    reported = {(row['start'], row['width'], row['split']): row for row in certificate['candidates']}
    assert len(reported) == len(certificate['candidates'])
    assert set(reported) == set(expected)
    allocation_checks = 0
    for key, independent in expected.items():
        row = reported[key]
        assert row['reason'] == independent['reason']
        assert row['A1'] == independent['images']['A1']
        assert row['C1'] == independent['images']['C1']
        if row['reason'] == 'substring_capacity':
            symbol = row['code']
            assert symbol in independent['shortages']
            witness = independent['shortages'][symbol]
            assert all(row[field] == witness[field] for field in ['image', 'required', 'available'])
            assert row['required'] > row['available']
        else:
            assert row['x_position'] == x_position and row['x_suffix'] == x_suffix
            allocated = {entry['source_position']: entry for entry in row['allocations']}
            assert len(allocated) == len(row['allocations'])
            assert set(allocated) == set(singleton_positions)
            for position, witness in allocated.items():
                independent_allocation = independent['allocations'][position]
                assert witness['code'] == independent_allocation['code']
                assert witness['letter'] in independent_allocation['violations']
                shortage = independent_allocation['violations'][witness['letter']]
                assert witness['required'] == shortage['required']
                assert witness['available'] == shortage['available']
                assert witness['required'] > witness['available']
                allocation_checks += 1
    return dict(edition=certificate['edition'], variant=certificate['variant'],
                status='UNSAT_ANALYTIC', squares=squares, square_split_count=len(expected),
                substring_rejected=reasons['substring_capacity'], unique_x_rejected=reasons['unique_x_tail'],
                singleton_allocations_checked=allocation_checks, survivors=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assert maximum_disjoint('aaaaa', 'aaa') == 1
    assert maximum_disjoint('aaaaaa', 'aa') == 3
    assert maximum_disjoint('ababa', 'aba') == 1
    source_bytes = (E / 'artifacts/INPUT.json').read_bytes()
    certificate_bytes = (E / 'artifacts/ANALYTIC_CERTIFICATE.json').read_bytes()
    source = json.loads(source_bytes)
    certificate = json.loads(certificate_bytes)
    assert certificate['status'] == 'UNSAT_ANALYTIC'
    assert certificate['input_sha256'] == digest(source_bytes)
    assert certificate['method'] == 'post-search necessary conditions; frozen solver unchanged'
    # The original solver artifact remains unopened and unchanged by this check.
    base_hash = certificate['base_result_sha256']
    assert isinstance(base_hash, str) and len(base_hash) == 64 and set(base_hash) <= set('0123456789abcdef')
    targets = {variant['id']: variant['text'] for variant in source['source_variants']}
    assert len(targets) == len(source['source_variants'])
    cases = {(case['edition'], case['variant']): case for case in certificate['cases']}
    assert len(cases) == len(certificate['cases'])
    assert set(cases) == {(edition, variant) for edition in source['editions'] for variant in targets}
    checks = [check_case(source['editions'][edition], targets[variant], cases[edition, variant])
              for edition, variant in sorted(cases)]
    output = dict(status='PASS', proof_status='ALL_CASES_UNSAT_ANALYTIC', input_sha256=digest(source_bytes),
                  certificate_sha256=digest(certificate_bytes), capacity_algorithm='interval_dynamic_programming',
                  case_count=len(checks), square_split_count=sum(case['square_split_count'] for case in checks),
                  substring_rejected=sum(case['substring_rejected'] for case in checks),
                  unique_x_rejected=sum(case['unique_x_rejected'] for case in checks),
                  singleton_allocations_checked=sum(case['singleton_allocations_checked'] for case in checks),
                  cases=checks)
    text = json.dumps(output, sort_keys=True, separators=(',', ':')) + '\n'
    destination = E / 'artifacts/ANALYTIC_VALIDATION.json'
    if args.check:
        assert destination.read_text() == text
    else:
        destination.write_text(text)
    print(json.dumps({key: value for key, value in output.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()

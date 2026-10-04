#!/usr/bin/env python3
"""Independent multiset enumeration and joint-ratio MI calculation."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math

EXP = Path(__file__).resolve().parents[1]


def orders(counts, prefix=()):
    if not any(counts.values()):
        yield prefix
    else:
        for pair in sorted(counts):
            if counts[pair]:
                counts[pair] -= 1
                yield from orders(counts, prefix + (pair,))
                counts[pair] += 1


def joint(order):
    c = Counter((left[1], right[0]) for left, right in zip(order, order[1:]))
    return tuple(c[a, b] for a in 'ab' for b in 'ab')


def mi(c):
    n = sum(c)
    rows = (c[0] + c[1], c[2] + c[3])
    cols = (c[0] + c[2], c[1] + c[3])
    return sum(v / n * math.log2(v * n / (rows[i // 2] * cols[i % 2]))
               for i, v in enumerate(c) if v)


def main():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    result = json.loads((EXP / 'artifacts/RESULT.json').read_text())
    words = spec['tokens']
    classes = Counter((w[0], w[-1]) for w in words)
    assert classes == {('a', 'a'): 2, ('a', 'b'): 2, ('b', 'a'): 2, ('b', 'b'): 2}
    histogram = Counter(joint(order) for order in orders(classes.copy()))
    assert sum(histogram.values()) == 2520
    expanded = {k: v * 16 for k, v in histogram.items()}
    stored = json.loads((EXP / 'artifacts/EDGE_TABLE_HISTOGRAM.json').read_text())
    assert expanded == {tuple(r['counts']): r['multiplicity'] for r in stored['rows']}
    observed = mi(joint(tuple((w[0], w[-1]) for w in words)))
    mean = math.fsum(mi(k) * v for k, v in histogram.items()) / 2520
    assert abs(observed - result['edges']['observed_bits']) < 1e-12
    assert abs(mean - result['edges']['shuffle_mean_bits']) < 1e-12
    assert abs(observed - mean - result['edges']['excess_bits']) < 1e-12
    assert result['edges']['destination_entropy_bits'] == 1
    assert result['identity']['destination_entropy_bits'] == 3
    assert result['identity']['excess_bits'] == result['identity']['excess_share'] == 0
    assert abs(result['identity']['observed_bits'] - math.log2(7)) < 1e-12
    assert len(result['identity']['permutation_value_histogram']) == 1
    assert list(result['identity']['permutation_value_histogram'].values()) == [40320]
    assert result['permutations'] == math.factorial(8)
    assert result['target_records_read'] == result['confirmed_meanings'] == 0
    assert observed > mean and observed < math.log2(7)
    assert result['raw_data_processing_holds'] and result['edge_excess_exceeds_identity_excess']
    assert result['status'] == 'SHUFFLE_EXCESS_ORDERING_IS_NOT_INFORMATION_LOCALIZATION'
    lock = json.loads((EXP / 'artifacts/PREREG_LOCK.json').read_text())
    for name, digest in lock['files'].items():
        assert hashlib.sha256((EXP / name).read_bytes()).hexdigest() == digest
    validation = {'status': 'PASS',
                  'independent_method': '2520 multiset orders, 16 identity orders per class order; direct joint probability ratio',
                  'histogram_cells': len(histogram), 'full_permutations': 40320,
                  'checked': ['complete histogram', 'observed edge MI', 'exact edge null', 'identity singleton proof',
                              'normalization', 'decision', 'protocol hashes', 'zero manuscript input']}
    (EXP / 'artifacts/VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()

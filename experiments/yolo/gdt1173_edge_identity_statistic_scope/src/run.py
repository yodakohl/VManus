#!/usr/bin/env python3
"""Exact tiny estimator demonstration; only its bound artificial input is read."""
import collections
import hashlib
import itertools
import json
import math
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]


def entropy(values):
    counts = collections.Counter(values)
    n = sum(counts.values())
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def information(pairs):
    return (entropy([x for x, y in pairs]) + entropy([y for x, y in pairs])
            - entropy(pairs))


def table(words):
    counts = collections.Counter((a[-1], b[0]) for a, b in zip(words, words[1:]))
    return tuple(counts[a, b] for a in 'ab' for b in 'ab')


def main():
    lock = json.loads((EXP / 'artifacts/PREREG_LOCK.json').read_text())
    for name, expected in lock['files'].items():
        assert hashlib.sha256((EXP / name).read_bytes()).hexdigest() == expected
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    words = tuple(spec['tokens'])
    assert len(words) == len(set(words)) == 8
    assert spec['vocabulary_cap'] >= len(words) and not spec['target_data']
    histogram = collections.Counter()
    identity_values = collections.Counter()
    edge_values = []
    for order in itertools.permutations(words):
        identity = information(list(zip(order, order[1:])))
        identity_values[format(identity, '.12f')] += 1
        edge_values.append(information([(a[-1], b[0]) for a, b in zip(order, order[1:])]))
        histogram[table(order)] += 1
    word_observed = information(list(zip(words, words[1:])))
    edge_observed = information([(a[-1], b[0]) for a, b in zip(words, words[1:])])
    word_null = sum(float(k) * v for k, v in identity_values.items()) / math.factorial(8)
    edge_null = math.fsum(edge_values) / len(edge_values)
    # Exact singleton algebra supplies zero; retain the numerical residual too.
    assert abs(word_observed - word_null) < 1e-11
    excess = edge_observed - edge_null
    result = {
        'status': 'SHUFFLE_EXCESS_ORDERING_IS_NOT_INFORMATION_LOCALIZATION'
                  if excess > 0 else 'FIXED_COUNTEREXAMPLE_FAILED',
        'tokens': list(words), 'permutations': len(edge_values),
        'identity': {'observed_bits': word_observed,
                     'shuffle_mean_bits': math.log2(7), 'excess_bits': 0.0,
                     'destination_entropy_bits': entropy(words), 'excess_share': 0.0,
                     'numeric_residual': word_observed - word_null,
                     'permutation_value_histogram': dict(identity_values)},
        'edges': {'observed_bits': edge_observed, 'shuffle_mean_bits': edge_null,
                  'excess_bits': excess, 'destination_entropy_bits': entropy([w[0] for w in words]),
                  'excess_share': excess / entropy([w[0] for w in words])},
        'raw_data_processing_holds': edge_observed <= word_observed,
        'edge_excess_exceeds_identity_excess': excess > 0,
        'target_records_read': 0, 'confirmed_meanings': 0,
    }
    (EXP / 'artifacts/EDGE_TABLE_HISTOGRAM.json').write_text(json.dumps(
        {'cell_order': ['aa', 'ab', 'ba', 'bb'],
         'rows': [{'counts': list(k), 'multiplicity': v} for k, v in sorted(histogram.items())]},
        indent=2) + '\n')
    (EXP / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Synthetic algorithm crosscheck plus authorized frozen-source projection.

Never opens target packets. Public output contains only hashes and counts.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time

import independent_runs as independent
import run as primary


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def direct_decode(cipher, key, index):
    """Independent position simulation, consumes first symbol as indicator."""
    anchor = cipher[0]
    output = []
    for c in cipher[1:]:
        value = (key[c] - key[anchor] + index) % 24
        if value >= 20:
            anchor = c
        else:
            output.append(independent.LETTERS[value])
    return ''.join(output)


def checks(source_pool, source_projection):
    checked = {}
    comparisons = 0
    # Exhaust every three-run length choice1..2, and binary plaintext up to
    # maximum output length, for every index. Binary alphabet includes index.
    for j, letter in enumerate(independent.LETTERS):
        other = 'a' if letter != 'a' else 'b'
        for lengths in itertools.product((1, 2), repeat=3):
            cipher = ''.join(c * r for c, r in zip('xyx', lengths))
            for size in range(len(cipher)):
                for chars in itertools.product((letter, other), repeat=size):
                    plain = ''.join(chars)
                    a = independent.run_accepts(cipher, plain, j)
                    b = primary.runs_accept(lengths, primary.PlainMasks(plain), j)
                    assert a == b, ('run mismatch', j, lengths, plain)
                    comparisons += 1
    checked['run_language'] = {'status': 'PASS', 'comparisons': comparisons,
                               'all_twenty_indices': True}

    # Enumerate real injective positions independently of the primary DFS.
    # Fixed first glyph is the sole rotation gauge; no length/code masks used.
    families, assignments = 0, 0
    fixtures = [('xyyx', 'b'), ('xyx', ''), ('xyzx', 'ab'),
                ('xyzyx', 'bb'), ('xyz', 'a'), ('xyz', '')]
    for j in (0, 1, 8, 19):
        for cipher, plain in fixtures:
            names = sorted(set(cipher) - {'x'})
            expected = set()
            for positions in itertools.permutations(range(1, 24), len(names)):
                key = {'x': 0, **dict(zip(names, positions))}
                assignments += 1
                if direct_decode(cipher, key, j) == plain:
                    expected.add(tuple(sorted(key.items())))
            actual = list(primary.local_extensions(cipher, plain, j, {'x': 0},
                          time.monotonic() + 30, Counter(local_nodes=0)))
            actual_set = {tuple(sorted(k.items())) for k in actual}
            assert len(actual) == len(actual_set), 'duplicate local model'
            assert actual_set == expected, ('local family mismatch', cipher, plain, j)
            families += 1
    checked['complete_local_families'] = {'status': 'PASS', 'families': families,
                                          'brute_position_assignments': assignments}

    key = {c: i for i, c in enumerate('abcdefghijklmnopqrstuvwx')}
    forward_cases = 0
    for j in range(20):
        for plan in ({}, {0: [20, 23], 2: [21], 4: [22, 20]}):
            cipher = independent.forward_encode('abiu', key, j, 'q', plan)
            replay = list(primary.local_extensions(cipher, 'abiu', j, key,
                          time.monotonic() + 30, Counter(local_nodes=0)))
            assert replay == [key], 'forward encoded full-key replay mismatch'
            forward_cases += 1
    checked['forward_encoder_replay'] = {'status': 'PASS', 'cases': forward_cases,
                                         'consecutive_and_trailing_controls': True}

    # Two disconnected messages: second position has23 real offset choices.
    # Two distinct source IDs with equal text allow2 assignments:46 models.
    joined = primary.panel_models(
        [{'id': 'first', 'cipher': 'xx'}, {'id': 'second', 'cipher': 'yy'}],
        [{'id': 's1', 'plain': 'b'}, {'id': 's2', 'plain': 'b'}], seconds=30, limit=100)
    assert joined['enumeration_complete'] and joined['status'] == 'COMPLETE_SAT'
    assert len(joined['models']) == 46
    signatures = set()
    for model in joined['models']:
        assert model['index'] == 1 and model['positions']['x'] == 0
        assert model['positions']['y'] in range(1, 24)
        signatures.add((tuple(map(tuple, model['assignments'])), model['positions']['y']))
    assert len(signatures) == 46
    checked['global_disconnected_alias_fixture'] = {'status': 'PASS', 'complete_models': 46}

    # Hash gate precedes parsing. This script has no target input parameter.
    pool_hash = digest(source_pool)
    assert pool_hash == primary.SPEC['source_pool_sha256'], 'source hash mismatch'
    pool = json.loads(source_pool.read_bytes())
    projected = independent.source_projection(pool['entries'])
    assert projected == primary.project(pool['entries']), 'source projection mismatch'
    assert primary.projection_artifact(projected) == json.loads(source_projection.read_bytes())
    checked['frozen_source_projection'] = {
        'status': 'PASS', 'original_entries': len(pool['entries']),
        'accepted': len(projected['entries']), 'excluded': len(projected['exclusions']),
        'source_pool_sha256': pool_hash, 'projection_sha256': digest(source_projection)}
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-pool', required=True, type=Path)
    parser.add_argument('--source-projection', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    directory = Path(__file__).parent
    before = {name: digest(directory / name) for name in
              ('run.py', 'independent_runs.py', 'SPEC.json', 'check_preparation.py')}
    result = checks(args.source_pool, args.source_projection)
    assert before == {name: digest(directory / name) for name in before}, 'sources changed during check'
    artifact = {'schema': 'GDT896_PREPARATION_VALIDATION_V1', 'status': 'PASS',
                'target_accessed': False, 'source_hashes': before, 'checks': result,
                'claim_ceiling': 'Engineering and source projection only; no manuscript compatibility or decipherment finding.'}
    args.output.write_text(json.dumps(artifact, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'target_accessed': False}))


if __name__ == '__main__':
    main()

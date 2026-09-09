#!/usr/bin/env python3
"""Independent guarded source reconstruction and BFS equality-certificate replay."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict, deque
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def components(graph):
    unseen = set(graph)
    result = []
    while unseen:
        first = min(unseen)
        unseen.remove(first)
        found = {first}
        queue = deque([first])
        while queue:
            for node in graph[queue.popleft()]:
                if node in unseen:
                    unseen.remove(node)
                    found.add(node)
                    queue.append(node)
        result.append(sorted(found))
    return sorted(result, key=lambda row: row[0])


def reachable(graph, start, end):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            return True
        for nxt in graph[node] - seen:
            seen.add(nxt)
            queue.append(nxt)
    return False


def panel_check(selected, panel, name):
    sequences = [(row['id'], list(row['raw']) if name == 'literal_eva' else row['sta']) for row in selected]
    sequences = [(gid, seq) for gid, seq in sequences if seq is not None]
    alphabet = sorted({symbol for _, seq in sequences for symbol in seq})
    graph = {side + symbol: set() for symbol in alphabet for side in ['L:', 'R:']}
    witnesses = {}
    adjacency_count = 0
    for gid, seq in sequences:
        for position, (left, right) in enumerate(zip(seq, seq[1:])):
            adjacency_count += 1
            witnesses.setdefault((left, right), {'pair': [left, right], 'group_id': gid, 'position': position})
            graph['R:' + left].add('L:' + right)
            graph['L:' + right].add('R:' + left)
    closure = components(graph)
    lookup = {node: i for i, part in enumerate(closure) for node in part}
    symbol_pairs = {symbol: [lookup['L:' + symbol], lookup['R:' + symbol]] for symbol in alphabet}
    by_pair = defaultdict(list)
    for symbol, pair in symbol_pairs.items():
        by_pair[tuple(pair)].append(symbol)
    collisions = sorted(sorted(group) for group in by_pair.values() if len(group) > 1)
    # Reconstruct the specified lexicographic forest using BFS connectivity,
    # independently of the producer's disjoint-set implementation.
    forest_graph = {node: set() for node in graph}
    forest = []
    for pair in sorted(witnesses):
        left, right = 'R:' + pair[0], 'L:' + pair[1]
        if not reachable(forest_graph, left, right):
            forest.append(witnesses[pair])
            forest_graph[left].add(right)
            forest_graph[right].add(left)
    assert components(forest_graph) == closure
    underlying = set()
    for _, seq in sequences:
        assert seq
        for left, right in zip(seq, seq[1:]):
            assert symbol_pairs[left][1] == symbol_pairs[right][0]
        underlying.add(tuple([symbol_pairs[seq[0]][0]] + [symbol_pairs[symbol][1] for symbol in seq]))
    expected = dict(alphabet=alphabet, groups=len(sequences), occurrences=adjacency_count,
                    pair_types=len(witnesses), components=closure, symbol_pairs=symbol_pairs,
                    forest=forest, forced_collision_classes=collisions,
                    underlying_distinct_sequences=len(underlying),
                    status='INJECTIVE_OVERLAPPING_PAIR_MODEL_EXCLUDED' if collisions else 'EXACT_OVERLAPPING_PAIR_MODEL_COMPATIBLE')
    for key, value in expected.items():
        assert panel[key] == value, (name, key)
    return dict(groups=len(sequences), components=len(closure), forced_collision_classes=len(collisions),
                forest_edges=len(forest), all_constraints_verified=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    lock = json.loads((E / 'src/PREREG_LOCK.json').read_text())
    for name, digest in lock.items():
        assert sha(ROOT / name) == digest, name
    spec = json.loads((E / 'src/SPEC.json').read_text())
    assert sha(ROOT / spec['source_lines']) == spec['source_lines_sha256']
    source = json.loads((ROOT / spec['source_lines']).read_text())
    assert sorted(row['locus'] for row in source) == spec['allowed_loci']
    assert not any(locus.startswith('f84') for locus in spec['allowed_loci'])
    result = json.loads((E / 'artifacts/RESULT.json').read_text())
    assert result['status'] == 'EXACT_OVERLAPPING_PAIR_CONSTRAINTS_COMPLETED'
    assert result['source_lines_sha256'] == spec['source_lines_sha256']
    assert result['source_sta_sha256'] == sha(ROOT / spec['sta_atlas'])
    selected = json.loads((E / 'artifacts/SELECTED_GROUPS.json').read_text())
    argv = ['./vmanus-exp', 'query-tsv', spec['sta_atlas'], '--selector', 'locus']
    for locus in spec['allowed_loci']:
        argv.extend(['--allow', locus])
    argv.extend(['--columns', ','.join(spec['sta_columns']), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r'])
    assert result['guard']['argv'] == argv
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, check=True)
    assert hashlib.sha256(proc.stdout.encode()).hexdigest() == result['guard']['sha256']
    projected = list(csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'))
    by_id = {row['source_group_id']: row for row in projected}
    assert len(by_id) == len(projected)
    expected_ids = set()
    expected_groups = []
    exclusions = Counter()
    for line in sorted(source, key=lambda row: row['locus']):
        readings = {reading['edition']: reading for reading in line['readings']}
        assert set(readings) == set(spec['editions'])
        for edition, reading in readings.items():
            groups = reading['groups']
            assert len(reading['source_group_ids']) == len(groups)
            assert len(reading['internal_separators']) == len(groups) - 1
            for i, group_id in enumerate(reading['source_group_ids']):
                assert group_id not in expected_ids
                expected_ids.add(group_id)
                row = by_id[group_id]
                assert row['edition'] == edition and row['locus'] == line['locus']
                assert int(row['source_group_index']) == i + 1
                assert int(row['source_group_count']) == len(groups)
                assert row['left_separator'] == ('LINE_START' if i == 0 else reading['internal_separators'][i - 1])
                assert row['right_separator'] == ('LINE_END' if i == len(groups) - 1 else reading['internal_separators'][i])
                assert len(row['primary_sta_codes'].split()) == int(row['primary_sta_symbol_count'])
                assert int(row['alternative_site_count']) >= 0
        ordered = [readings[edition] for edition in spec['editions']]
        if any(reading['groups'] != ordered[0]['groups'] for reading in ordered[1:]):
            exclusions['line_group_boundary_disagreement'] += 1
            continue
        for i, raw in enumerate(ordered[0]['groups']):
            ids = {edition: readings[edition]['source_group_ids'][i] for edition in spec['editions']}
            rows = [by_id[ids[edition]] for edition in spec['editions']]
            if any(row['left_separator'] not in ['DEFINITE_SPACE', 'LINE_START'] or row['right_separator'] not in ['DEFINITE_SPACE', 'LINE_END'] for row in rows):
                exclusions['group_uncertain_outer_boundary'] += 1
                continue
            codes = [row['primary_sta_codes'].split() for row in rows]
            assert all(codes)
            sta = codes[0]
            if any(int(row['alternative_site_count']) != 0 for row in rows):
                exclusions['sta_group_marked_alternative'] += 1
                sta = None
            elif codes[1:] != codes[:-1]:
                exclusions['sta_group_member_disagreement'] += 1
                sta = None
            expected_groups.append(dict(id=line['locus'] + '#' + str(i + 1), locus=line['locus'], page=line['page'],
                                        group_index=i + 1, raw=raw, source_group_ids=ids, sta=sta))
    assert expected_ids == set(by_id)
    assert expected_groups == selected
    assert dict(exclusions) == result['exclusions']
    assert set(result['panels']) == set(spec['panels'])
    checks = {name: panel_check(selected, result['panels'][name], name) for name in spec['panels']}
    output = dict(status='PASS', source_selection_reconstructed=True, selected_groups=len(selected), panels=checks)
    text = json.dumps(output, sort_keys=True, separators=(',', ':')) + '\n'
    path = E / 'artifacts/VALIDATION.json'
    if args.check:
        assert path.read_text() == text
    else:
        path.write_text(text)
    print(text)


if __name__ == '__main__':
    main()

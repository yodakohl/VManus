#!/usr/bin/env python3
"""Necessary connector constraints, conditional on the existing surface cells."""
import hashlib
import itertools
import json
from collections import defaultdict, deque
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


class Equalities:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}

    def find(self, node):
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def join(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def edge_path(edges, start, goal):
    graph = defaultdict(list)
    for edge in edges:
        a, b = edge['nodes']
        graph[a].append((b, edge))
        graph[b].append((a, edge))
    queue = deque([(start, [])])
    seen = {start}
    while queue:
        node, path = queue.popleft()
        if node == goal:
            return path
        for nxt, edge in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, path + [edge]))
    return None


def main():
    cp = BASE / 'HAND_WRITER_ENTRY_CONSTRAINTS_CONTRACT_20261005.json'
    contract = json.loads(cp.read_text())
    for name in ('source', 'proposal'):
        assert hashlib.sha256((ROOT / contract[name]).read_bytes()).hexdigest() == contract[name + '_sha256']
    data = json.loads((ROOT / contract['source']).read_text())
    results = []
    for reader in contract['readers']:
        rows = [r for r in data['records'] if r['edition'] == reader]
        eligible, excluded, edges = [], [], []
        for row in rows:
            assert not row['locus'].startswith('f84')
            ref = {'locus': row['locus'], 'group': row['source_group_index'],
                   'raw': row['ivtff_group_raw']}
            if row['left_separator'] not in {'DEFINITE_SPACE', 'LINE_START'} or row['right_separator'] not in {'DEFINITE_SPACE', 'LINE_END'}:
                excluded.append(ref)
                continue
            units = [x['surface'] for x in row['G1_post_application_extension']]
            assert all(x['resolved_symbolically'] for x in row['G1_post_application_extension'])
            assert ''.join(units) == row['ivtff_group_raw']
            eligible.append(dict(ref, units=units))
            edges.append({'nodes': ['LOW', 'E:' + units[0]], 'type': 'word_reset', 'source': ref})
            for i, (a, b) in enumerate(zip(units, units[1:])):
                edges.append({'nodes': ['X:' + a, 'E:' + b], 'type': 'adjacency', 'offset': i, 'source': ref})
        units = sorted({u for row in eligible for u in row['units']})
        nodes = ['LOW'] + ['E:' + u for u in units] + ['X:' + u for u in units]
        eq = Equalities(nodes)
        for edge in edges:
            eq.join(*edge['nodes'])
        buckets = defaultdict(list)
        for n in nodes:
            buckets[eq.find(n)].append(n)
        components = sorted((sorted(v) for v in buckets.values()), key=lambda x: (not ('LOW' in x), x))
        free = components[1:]
        assert len(free) <= 16, 'Stop rather than enlarge the declared small audit.'
        # Explicit satisfying assignments provide a separate truth-table check.
        assignments = []
        for bits in itertools.product((0, 1), repeat=len(free)):
            assignment = {n: 0 for n in components[0]}
            for comp, bit in zip(free, bits):
                assignment.update({n: bit for n in comp})
            # Reconstruct requirements directly from the complete selected groups.
            assert all(assignment['E:' + row['units'][0]] == 0 and
                       all(assignment['X:' + a] == assignment['E:' + b]
                           for a, b in zip(row['units'], row['units'][1:]))
                       for row in eligible)
            assignments.append(assignment)
        pair_results = []
        for a, b in itertools.combinations(units, 2):
            merged = Equalities(nodes)
            for edge in edges:
                merged.join(*edge['nodes'])
            merged.join('X:' + a, 'X:' + b)
            possible = merged.find('E:' + a) != merged.find('E:' + b)
            models = [v for v in assignments if v['X:' + a] == v['X:' + b] and v['E:' + a] != v['E:' + b]]
            assert possible == bool(models)
            extra = {'nodes': ['X:' + a, 'X:' + b], 'type': 'hypothesized_common_body_exit'}
            pair_results.append({'pair': [a, b], 'possible': possible,
                                 'assignment_count': len(models),
                                 'equality_witness': None if possible else edge_path(edges + [extra], 'E:' + a, 'E:' + b)})
        item = {'reader': reader, 'eligible_groups': eligible, 'excluded_groups': excluded,
                'observed_units': units, 'constraints': edges, 'components': components,
                'forced_low_entries': [u for u in units if eq.find('E:' + u) == eq.find('LOW')],
                'free_components': free, 'binary_assignments_checked': len(assignments),
                'pair_results': pair_results,
                'compatible_pairs': [r['pair'] for r in pair_results if r['possible']],
                'validation': 'Equality merge and explicit truth-table comparison agree for every pair.'}
        results.append(item)
        print(reader, 'groups', len(eligible), 'units', len(units), 'LOW', item['forced_low_entries'],
              'free', free, 'compatible', item['compatible_pairs'])
    result = {'status': 'CONDITIONAL_CONNECTOR_CONSTRAINTS_NO_NATIVE_BODY_IDENTIFICATION',
              'contract_sha256': hashlib.sha256(cp.read_bytes()).hexdigest(),
              'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_sha256': contract['source_sha256'], 'results': results,
              'claim_ceiling': 'Necessary constraints only. All-LOW with distinct bodies always fits; '
                              'feasible pair identities are not native allographs or meanings. '
                              'Pairs tested separately, not jointly promoted to one alphabet.'}
    (BASE / 'HAND_WRITER_ENTRY_CONSTRAINTS_RESULT_20261005.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()

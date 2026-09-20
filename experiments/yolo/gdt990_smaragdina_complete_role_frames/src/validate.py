#!/usr/bin/env python3
"""Independent source/order, necessary-certificate and witness reconstruction.

Does not import the primary model. --source-only never opens the target packet.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'
CHECKS = []


def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def eq(a, b, label):
    assert a == b, (label, a, b)
    CHECKS.append(label)


def nodes(tree, order, cid, slot=0, address=()):
    if type(tree) is str:
        return [dict(root=tree, role=slot, clause=cid, path=list(address), terminal=True)]
    name = tree[0]
    own = dict(root=name, role=0, clause=cid, path=list(address), terminal=False)
    children = [nodes(tree[i], order, cid, i, address + (i,)) for i in range(1, len(tree))]
    if name in ('AND', 'IF', 'PURPOSE', 'BECAUSE'):
        assert len(children) == 2
        return children[0] + [own] + children[1]
    if order.split('_')[1] == 'REVERSE':
        children = list(reversed(children))
    flat = [r for chunk in children for r in chunk]
    return [own] + flat if order.split('_')[0] == 'PREFIX' else flat + [own]


def source_check():
    source = read(E / 'src/SOURCE.json')
    for path, digest in source['source_files'].items():
        eq(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, 'source_hash:' + path)
    collation_path = next(p for p in source['source_files'] if 'MEDIEVAL_SOURCE_COLLATION' in p)
    collation = read(ROOT / collation_path)
    eq(source['normalized_lines'], collation['normalized_lines'], 'entire_native_text')
    eq(source['source_uncertainties'], collation['uncertainty_apparatus'], 'all_native_uncertainties')
    eq(set(source['coverage']), {r['id'] for r in collation['content_outline']}, 'all19_source_units')
    expected = {f'VERSA_{a}__GLORY_{b}' for a in ('TOPIC', 'VIS') for b in ('TOPIC_PAST', 'TOPIC_FUTURE', 'YOU_FUTURE')}
    eq(set(source['variants']), expected, 'six_source_branches')
    eq(set(source['writers']), {'PREFIX_FORWARD', 'PREFIX_REVERSE', 'POSTFIX_FORWARD', 'POSTFIX_REVERSE'}, 'four_orders')
    streams = {}
    for v, data in source['variants'].items():
        eq({x for values in source['coverage'].values() for x in values}, {r['id'] for r in data['clauses']}, 'coverage:' + v)
        eq(len(data['clauses']), 21, 'clause_count:' + v)
        for order in source['writers']:
            stream = [item for c in data['clauses'] for item in nodes(c['tree'], order, c['id'])]
            eq(stream, data['streams'][order], 'independent_stream:' + v + ':' + order)
            counts = collections.Counter(r['root'] for r in stream)
            eq(dict(counts), data['counts'], 'root_counts:' + v + ':' + order)
            eq((len(stream), len(counts), sum(n == 1 for n in counts.values())),
               (data['forms'], data['root_types'], data['singleton_types']), 'counts:' + v + ':' + order)
            assert not any('UNRESOLVED' in r or r in ('TRANSFORMATION_SUBJECT', 'GLORY_TENSE', 'GLORY_SUBJECT') for r in counts)
            streams[(v, order)] = stream
    fixture = read(A / 'PRE_RUN_FIXTURES.json')
    eq(fixture['status'], 'PASS', 'pre_fit_fixture_receipt')
    eq(len(fixture['rows']), 4, 'four_fixture_orders')
    return source, streams


def necessity(events, words):
    count = collections.Counter(e['root'] for e in events)
    chars = sum(len(w) for w in words)
    d = len(set(''.join(words)))
    lengths = []
    size = 1
    while len(lengths) < len(count) and d:
        lengths.extend([size] * min(d ** size, len(count) - len(lengths)))
        size += 1
    bound = sum(n * l for n, l in zip(sorted(count.values(), reverse=True), lengths)) if d else None
    basic = dict(forms=len(events), root_types=len(count), characters=chars, groups=len(words),
                 alphabet=d, injective_root_length_bound=bound)
    if chars < len(events):
        return 'CONTRADICTED_NONEMPTY_LENGTH', basic
    if len(words) > len(events):
        return 'CONTRADICTED_WORD_BOUNDARIES', basic
    if bound is None or chars < bound:
        return 'CONTRADICTED_INJECTIVE_LENGTH', basic
    substrings = set()
    for word in words:
        for length in range(1, len(word) + 1):
            substrings.update(word[i:i + length] for i in range(len(word) - length + 1))
    def capacity(piece):
        total = 0
        for word in words:
            offset = 0
            while True:
                index = word.find(piece, offset)
                if index < 0:
                    break
                total += 1
                offset = index + len(piece)
        return total
    capacity_by_piece = {p: capacity(p) for p in substrings}
    empty = []
    for root, n in count.items():
        if n <= 1:
            continue
        upper = min(max(len(w) for w in words), (chars - len(events) + n) // n)
        if not any(len(p) <= upper and k >= n for p, k in capacity_by_piece.items()):
            empty.append(root)
    if empty:
        basic['empty_roots'] = sorted(empty)
        return 'CONTRADICTED_REPEATED_ROOT_DOMAIN', basic
    return 'REQUIRES_FULL_EQUATION', basic


def positive(events, words, roots, frames):
    assert set(roots) == {r['root'] for r in events}
    assert all(type(s) is str and len(s) > 0 for s in roots.values())
    assert len(set(roots.values())) == len(roots)
    roles = {r['role'] for r in events if r['role']}
    assert set(frames) == {a + str(r) for r in roles for a in ('P', 'S')}
    assert all(type(s) is str for s in frames.values())
    strings = []
    endpoints = {0}
    for e in events:
        value = roots[e['root']]
        if e['role']:
            value = frames['P' + str(e['role'])] + value + frames['S' + str(e['role'])]
        strings.append(value)
        endpoints.add(sum(len(x) for x in strings))
    assert ''.join(strings) == ''.join(words)
    cursor = 0
    for word in words:
        cursor += len(word)
        assert cursor in endpoints
    return strings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    source, streams = source_check()
    if args.source_only:
        result = dict(status='PASS', scope='source/coverage/orders and fixture receipt only; no target opened', checks=len(CHECKS))
        (A / 'SOURCE_VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
        return
    for p, digest in read(E / 'PREREG_LOCK.json')['files'].items():
        eq(hashlib.sha256((ROOT / p).read_bytes()).hexdigest(), digest, 'lock:' + p)
    panel = read(ROOT / source['input_paragraphs'])
    cases = read(A / 'CASES.json.gz')
    indexed = {(c['edition'], c['paragraph'], c['variant'], c['writer']): c for c in cases}
    eq(len(indexed), len(cases), 'unique_case_ids')
    eq([c['case'] for c in cases], list(range(1, len(cases) + 1)), 'all_case_numbers')
    wanted = {(ed, p['id'], v, w) for ed, ps in panel.items() for p in ps for v in source['variants'] for w in source['writers']}
    eq(set(indexed), wanted, 'complete_24_case_panel')
    positives = alternatives = 0
    solver_claims = collections.Counter()
    for ed, paragraphs in panel.items():
        for p in paragraphs:
            assert not p['page'].startswith('f84') and p['page'] != 'f116v'
            words = sum((line['words'] for line in p['lines']), [])
            assert len(words) == p['groups']
            eligible = all(x['anchor_eligible'] for x in p['lines'])
            for v in source['variants']:
                need, basic = necessity(streams[(v, source['writers'][0])], words) if eligible else ('UNKNOWN_SOURCE', {})
                for w in source['writers']:
                    c = indexed[(ed, p['id'], v, w)]
                    assert (c['leaf'], c['page'], c['target_groups']) == (p['leaf'], p['page'], len(words))
                    assert c['source_forms'] == len(streams[(v, w)]) and c['source_root_types'] == 97
                    assert c['independent_meaning_confirmation_capacity'] == 0
                    if need != 'REQUIRES_FULL_EQUATION':
                        assert c['status'] == need, (c['case'], need, c['status'])
                        if eligible:
                            assert c['necessary'] == dict(basic, status=need)
                        else:
                            assert c['ineligible_lines'] == [x['locus'] for x in p['lines'] if not x['anchor_eligible']]
                        continue
                    assert c['status'] in ('SAT', 'UNSAT', 'UNKNOWN_SOLVER', 'UNKNOWN_QUEUE_LIMIT', 'UNKNOWN_GLOBAL_LIMIT', 'UNKNOWN_PROCESS_LIMIT', 'ERROR_WORKER', 'ERROR_PROTOCOL')
                    solver_claims[c['status']] += 1
                    if c['status'] != 'SAT':
                        continue
                    events = streams[(v, w)]
                    forms = positive(events, words, c['roots'], c['frames'])
                    assert forms == [x['value'] for x in c['witness']['alignment']]
                    assert c['witness']['valid']
                    counter = collections.Counter(e['root'] for e in events)
                    keys = {'root:' + r for r, n in counter.items() if n > 1} | {'frame:' + f for f in c['frames']}
                    assert set(c['projections']) == keys
                    for key, q in c['projections'].items():
                        family, name = key.split(':', 1)
                        source_values = c['roots'] if family == 'root' else c['frames']
                        assert q['first_value'] == source_values[name]
                        assert q['status'] in ('SAT', 'UNSAT', 'UNKNOWN_SOLVER')
                        if q['status'] == 'SAT':
                            positive(events, words, q['roots'], q['frames'])
                            assert (q['roots'] if family == 'root' else q['frames'])[name] != q['first_value']
                            alternatives += 1
                    positives += 1
    result = read(A / 'RESULT.json')
    eq(result['cases'], len(cases), 'reported_case_count')
    eq(result['status_counts'], dict(collections.Counter(c['status'] for c in cases)), 'reported_statuses')
    eq(result['conditional_witness_cases'], positives, 'reported_witnesses')
    eq(result['solver_jobs'], sum(solver_claims.values()), 'reported_solver_jobs')
    eq(result['paragraph_counts'], {e: len(ps) for e, ps in panel.items()}, 'reported_panel')
    assert result['confirmed_translated_words'] == result['independent_meaning_confirmation_capacity'] == 0
    assert result['significance_claim'] is result['unique_inverse_decoding_claim'] is False
    with (A / 'CANDIDATES.tsv').open() as f:
        tab = list(csv.DictReader(f, delimiter='\t'))
    eq(len(tab), len(cases), 'table_all_rows')
    for row, case in zip(tab, cases):
        assert all(row[k] == str(case[k]) for k in row), case['case']
    validation = dict(status='PASS', cases=len(cases), full_witnesses=positives, alternative_witnesses=alternatives,
                      solver_statuses=dict(solver_claims), grouped_checks=len(CHECKS),
                      coverage='independent streams, complete panel, necessary certificates and positive equations; solver UNSAT not independently proved; no meaning validation')
    (A / 'VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()

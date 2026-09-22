#!/usr/bin/env python3
"""Independent GDT1039 oracle: author event ledger, deque recency, old fixtures.

No primary runner import or execution. --self-test replays the target-derived
authored event stream with synthetic values; it is NOT target-independent.
--execute requires the public preregistration receipt and every locked byte.
The independent event oracle was written before reading any new result artifact.
"""
import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
OLD = ROOT / 'experiments/yolo/gdt1015_coupled_hour_day_reading'
POLICIES = ('DEFERRED_CONSUMING', 'DEFERRED_NONCONSUMING',
            'EAGER_CONSUMING', 'EAGER_NONCONSUMING',
            'UNTYPED_RECENT', 'GLOBAL_CONSUMPTION')
SPANS = ((1, 8), (9, 16), (17, 24), (25, 29), (30, 33), (34, 39),
         (40, 43), (44, 47), (48, 55), (56, 63), (64, 75), (76, 80))
FIXED_HASHES = {
    'src/SOURCE.json': '0f153227137654abf67b5c7465ebe445fb31f7e1f52a883e6148afa8878ac076',
    'MODEL_v01.json': '07fdeb0b6f53fad8d9f2a253c585699c8c5d248c9206d4599d43e3ceaf5171c7',
    'READING_v01.md': '9d96ef4198c8623183e25724331559c9bc2bad3b159fcdabcaee07ebb26f7840',
    'REPORT.md': 'f067ae4313f4e3b155bcdf524e6ae578fceab0e28d8227a80a8e0da7e1810f34',
    'SCOPE_CORRECTION.md': '0308a1a0d592c759c7b8ffd4c3d425f44371b33f0b9e932eb3cb0da1461f9001',
    'src/run.py': '5acfe03f8f51935ce6a1f806c337e1a6ab9eedeba48518f54bd3309ebf48fdee',
    'artifacts/ROWS.json': '67058011d5b2f2a951c89979d5b548c0a150920450ff136d4fc1ee8f9d65283d',
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def oracle(policy):
    """Independent complete constructor sequence; no desired-ID selection table."""
    require(policy in POLICIES, 'unknown policy')
    eager = policy.startswith('EAGER_')
    consume = 'NONCONSUMING' not in policy
    global_use = policy == 'GLOBAL_CONSUMPTION'
    untyped = policy == 'UNTYPED_RECENT'
    newest = deque()
    types = {}
    used = set()
    events, fetches = [], []
    stopped = None
    clause = ''

    def snap():
        return {'recency': list(newest), 'used': sorted(used), 'types': dict(types)}

    def action(op, identity=None, typ=None, position=None):
        before = snap()
        if op == 'publish':
            require(identity not in types, 'duplicate publication')
            types[identity] = typ
            newest.appendleft(identity)
        elif op == 'touch':
            require(identity in types, 'touch before publication')
            newest.remove(identity)
            newest.appendleft(identity)
        elif op == 'reset':
            if not global_use:
                used.clear()
        events.append({'clause': clause, 'op': op, 'id': identity,
                       'type': typ, 'position': position,
                       'before': before, 'after': snap()})

    def fetch(typ, pos=None):
        nonlocal stopped
        before = snap()
        candidates = [x for x in newest if x not in used and
                      (untyped or types[x] == typ)]
        chosen = candidates[0] if candidates else None
        status = 'OK'
        if chosen is None:
            status = 'EMPTY_DOMAIN'
        elif types[chosen] != typ:
            status = 'TYPE_CONFLICT'
        if status == 'OK':
            newest.remove(chosen)
            newest.appendleft(chosen)
            if consume:
                used.add(chosen)
        row = {'call': 'F' + str(len(fetches) + 1), 'clause': clause,
               'position': pos, 'required_type': typ, 'chosen_id': chosen,
               'chosen_type': types.get(chosen), 'status': status,
               'eligible': candidates, 'before': before, 'after': snap()}
        fetches.append(row)
        events.append({'clause': clause, 'op': 'fetch', **row})
        if status != 'OK':
            stopped = row

    for index in range(1, 13):
        clause = f'C{index:02d}'
        action('reset')
        if index == 1:
            action('publish', 'D', 'DAY', 2)
        elif index == 3:
            action('publish', 'U', 'HOUR_UNIT', 19)
        elif index == 4:
            fetch('DAY', 25)
        elif index == 5:
            action('publish', 'R_init', 'RULER', 32)
        elif index == 6:
            action('touch', 'D', position=36)
            action('touch', 'U', position=37)
            action('publish', 'R_hour', 'RULER', 39)
        elif index == 7:
            fetch('DAY', 40)
            if stopped is None:
                fetch('HOUR_UNIT', 43)
                action('publish', 'N', 'DAY_COUNT', 43)
        elif index == 8:
            action('touch', 'U', position=44)
            action('touch', 'U', position=46)
        elif index == 9:
            fetch('DAY_COUNT', 54)
        elif index == 10:
            action('touch', 'D', position=60)
            action('touch', 'U', position=62)
            action('publish', 'A', 'METHOD', 63)
            action('publish', 'RA', 'RULER_RESULT', 63)
        elif index == 11:
            action('local_open', 'B', 'METHOD', 64)
            action('local_result', 'RB', 'RULER_RESULT', 74)
            if eager:
                action('publish', 'B', 'METHOD', 74)
                action('publish', 'RB', 'RULER_RESULT', 74)
            fetch('RULER_RESULT', 75)
            if stopped is None and not eager:
                action('publish', 'B', 'METHOD', 75)
                action('publish', 'RB', 'RULER_RESULT', 75)
        elif index == 12:
            fetch('METHOD', 76)
            if stopped is None:
                fetch('METHOD', 78)
            if stopped is None:
                action('touch', 'U', position=79)
        if stopped is not None:
            break
    return {'policy': policy, 'events': events, 'fetches': fetches,
            'stop': stopped, 'final': snap()}


def truths(trace, a, b):
    """Only comparison truth: deliberately no claim of whole-model coherence."""
    if trace['stop'] is not None:
        return None, None, None
    chosen = [x['chosen_id'] for x in trace['fetches']]
    values = {'A': a, 'RA': a, 'B': b, 'RB': b}
    c11 = b == values[chosen[4]]
    c12 = values[chosen[5]] == values[chosen[6]]
    return c11, c12, c11 and c12


def self_test():
    n = 0
    expected = {
        POLICIES[0]: ['D', 'D', 'U', 'N', 'RA', 'B', 'A'],
        POLICIES[1]: ['D', 'D', 'U', 'N', 'RA', 'B', 'B'],
        POLICIES[2]: ['D', 'D', 'U', 'N', 'RB', 'B', 'A'],
        POLICIES[3]: ['D', 'D', 'U', 'N', 'RB', 'B', 'B'],
    }
    for p, wanted in expected.items():
        t = oracle(p)
        require([f['chosen_id'] for f in t['fetches']] == wanted, p)
        require(t['stop'] is None and len(t['final']['types']) == 9, p)
        n += 2
        for a, b in [(0, 0), (3, 3), (0, 1), (6, 2), (-1, 99)]:
            actual = truths(t, a, b)
            eq = a == b
            wanted_truth = {'DEFERRED_CONSUMING': (eq, eq, eq),
                            'DEFERRED_NONCONSUMING': (eq, True, eq),
                            'EAGER_CONSUMING': (True, eq, eq),
                            'EAGER_NONCONSUMING': (True, True, True)}[p]
            require(actual == wanted_truth, (p, a, b)); n += 1
        publications = [e['id'] for e in t['events'] if e['op'] == 'publish']
        require(Counter(publications) == Counter(t['final']['types'].keys()), 'publish once'); n += 1
    u = oracle('UNTYPED_RECENT')
    require((u['stop']['clause'], u['stop']['chosen_id'], u['stop']['status']) ==
            ('C04', 'U', 'TYPE_CONFLICT'), 'untyped stop'); n += 1
    g = oracle('GLOBAL_CONSUMPTION')
    require((g['stop']['clause'], g['stop']['call'], g['stop']['status']) ==
            ('C07', 'F2', 'EMPTY_DOMAIN'), 'global stop'); n += 1
    require(g['stop']['before']['used'] == ['D'], 'D not reborn'); n += 1
    for t in (u, g):
        require(truths(t, 3, 3) == (None, None, None), 'unbound not false'); n += 1
    for p in POLICIES[:4]:
        t = oracle(p)
        require('RA' in t['final']['types'] and 'RB' in t['final']['types'],
                'provenance distinct independent of value'); n += 1
    return n


def check_registration():
    lock = read(HERE / 'PREREG_LOCK.json')
    receipt = read(HERE / 'artifacts/PUBLIC_REGISTRATION.json')
    require(lock['status'] == 'REGISTERED_BEFORE_EXECUTION', 'lock status')
    require(receipt.get('registered_before_execution') is True, 'no public gate')
    require(receipt.get('public_ref') == 'origin/main', 'public ref')
    require(re.fullmatch('[0-9a-f]{40}', receipt.get('commit', '')) is not None,
            'public commit')
    locked = {}
    for entry in lock['files']:
        rel = entry['path']
        require(not Path(rel).is_absolute() and '..' not in Path(rel).parts, 'lock path')
        require(rel not in locked, 'duplicate lock path')
        require(sha(ROOT / rel) == entry['sha256'], 'lock mismatch: ' + rel)
        locked[rel] = entry['sha256']
    for rel, expected in FIXED_HASHES.items():
        path = OLD / rel
        require(sha(path) == expected, 'legacy changed: ' + rel)
        require(str(path.relative_to(ROOT)) in locked, 'legacy not locked: ' + rel)
    for name in ('DECISION.md', 'METHOD.md', 'PREREGISTRATION.md', 'src/SPEC.json', 'src/run.py', 'src/validate.py'):
        require(str((HERE / name).relative_to(ROOT)) in locked, 'new input not locked: ' + name)
    return receipt


def original_inventory():
    source, model = read(OLD / 'src/SOURCE.json'), read(OLD / 'MODEL_v01.json')
    words = source['words']
    require(len(words) == 80, '80 positions')
    require([w for r in source['records'] for w in r['raw'].split()] == words, 'source rows')
    require(len(model['lexicon']) == 60 and set(model['lexicon']) == set(words), '60 words')
    require(sum(v == 1 for v in Counter(words).values()) == 45, '45 singleton types')
    require(len(model['clauses']) == 12, '12 constructors')
    coverage = []
    for i, (c, (start, end)) in enumerate(zip(model['clauses'], SPANS), 1):
        require((c['id'], c['start'], c['end']) == (f'C{i:02d}', start, end), 'clause range')
        require(c['words'] == words[start-1:end], 'whole source coverage')
        require(c['pattern'] == [model['lexicon'][w]['value'] for w in c['words']], 'fixed values')
        coverage.extend(range(start, end+1))
    require(coverage == list(range(1, 81)), 'each position once')
    fixtures = read(OLD / 'artifacts/ROWS.json')
    require(len(fixtures) == 357, '357 original numeric fixtures')
    require(len({(x['setting'], x['initial_phase']) for x in fixtures}) == 357, 'unique fixture keys')
    variants = {c['id']: c for c in model['candidates']}
    for row in fixtures:
        c = variants[row['candidate']]
        require(row['extra_scope_assumptions'] == c['grammar_changes'], 'scope costs unchanged')
        require(row['new_word_changes'] == c['word_changes'], 'word costs unchanged')
    return source, model, fixtures


def validate_spec():
    """Metadata agreement checked against independent constants, never used as oracle."""
    spec = read(HERE / 'src/SPEC.json')
    require([p['id'] for p in spec['policies']] == list(POLICIES), 'six policy order')
    require(spec['frozen_contract']['constructions'] == 12, 'spec constructors')
    require(spec['frozen_contract']['source_positions'] == 80, 'spec positions')
    require(spec['frozen_contract']['old_numeric_rows'] == 357, 'spec fixtures')
    require(spec['frozen_contract']['fetches'] == 7, 'spec fetches')
    expected = [('C04', 25, 'DAY'), ('C07', 40, 'DAY'),
                ('C07', 43, 'HOUR_UNIT'), ('C09', 54, 'DAY_COUNT'),
                ('C11', 75, 'RULER_RESULT'), ('C12', 76, 'METHOD'),
                ('C12', 78, 'METHOD')]
    actual = [(f['construction'], f['position'], f['required_type'])
              for f in spec['fetches']]
    require(actual == expected, 'all seven source fetch sites')
    declarations = {r['id']: r for r in spec['registry']['records']}
    for identity, typ in oracle(POLICIES[0])['final']['types'].items():
        require(declarations[identity]['type'] == typ and
                declarations[identity]['eligible'] is True, 'record ' + identity)
    require(declarations['H']['eligible'] is False, 'global H not selectable')
    calls = [event.get('fetch') for event in spec['event_inventory'] if event.get('fetch')]
    require(calls == ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'], 'event inventory omits fetch')
    for policy in POLICIES:
        trace = oracle(policy)
        good = [f['chosen_id'] if f['status'] == 'OK' else None for f in trace['fetches']]
        good += [None] * (7 - len(good))
        require(spec['predicted_reference_traces'][policy] == good, 'predicted calls')
        for equality, a, b in [('equal', 0, 0), ('unequal', 0, 1)]:
            c11, c12, both = truths(trace, a, b)
            require(spec['truth_table'][equality][policy] ==
                    {'c11': c11, 'c12': c12, 'joint': both}, 'spec truth table')
    return spec


def validate_artifacts(source, model, fixtures):
    directory = HERE / 'artifacts'
    traces = read(directory / 'EVENT_TRACES.json')
    require(list(traces) == list(POLICIES), 'all six trace policies in order')
    expected_traces = {p: oracle(p) for p in POLICIES}
    fetch_count = 0
    statuses = {'OK': 'FETCHED', 'EMPTY_DOMAIN': 'STOP_UNBOUND',
                'TYPE_CONFLICT': 'STOP_WRONG_TYPE'}
    for policy, actual in traces.items():
        expected = expected_traces[policy]
        stop = expected['stop']['clause'] if expected['stop'] else None
        require(actual['policy'] == policy and actual['stop'] == stop, 'policy stop')
        require(actual['complete'] is (stop is None), 'complete trace flag')
        require(len(actual['fetches']) == len(expected['fetches']), 'fetch count')
        selected = {}
        for got, want in zip(actual['fetches'], expected['fetches']):
            require(got['fetch'] == want['call'], 'call ID')
            require(got['required_type'] == want['required_type'], 'required type')
            require(got['selected'] == want['chosen_id'], 'independent chosen referent')
            require(got['status'] == statuses[want['status']], 'fetch status')
            require(got.get('selected_type') == want['chosen_type'], 'selected type')
            require(got['eligible'] == want['eligible'], 'full eligible ordered domain')
            before = want['before']
            require([(r['id'], r['type']) for r in got['registry_before']] ==
                    [(x, before['types'][x]) for x in before['recency']], 'full recency snapshot')
            times = [r['recency'] for r in got['registry_before']]
            require(all(a > b for a, b in zip(times, times[1:])), 'strict recency order')
            require(got['used_before'] == before['used'], 'used before')
            require(got['used_after'] == want['after']['used'], 'used after')
            if want['status'] == 'OK':
                selected[want['call']] = want['chosen_id']
            fetch_count += 1
        require(actual['selected'] == selected, 'all selected IDs retained')
        # Check every effective publication/touch/fetch, not only the seven choices.
        observed_events = []
        for event in actual['events']:
            op = event['operation']
            if event.get('status') in ('SKIPPED_AFTER_STOP', 'PRIVATE', 'NOT_APPLICABLE'):
                continue
            if op in ('publish', 'touch') and event.get('record') != 'H':
                observed_events.append((op, event['record']))
            elif op == 'fetch':
                observed_events.append((op, event['fetch']))
        wanted_events = [(e['op'], e['call'] if e['op'] == 'fetch' else e['id'])
                         for e in expected['events'] if e['op'] in ('publish', 'touch', 'fetch')]
        require(observed_events == wanted_events, 'complete effective event sequence: ' + policy)
    table = read(directory / 'COMPARISON_TABLE.json')
    require(len(table) == 357 * 6, 'all 2142 comparison rows')
    numeric_keys = ('setting', 'candidate', 'daylight_hours', 'initial_phase',
                    'method_a_hour_offset', 'method_a_ruler_index', 'method_b_steps',
                    'method_b_ruler_index', 'complete_cycles_removed', 'remainder',
                    'source_continuous_hours')
    aggregation = {p: Counter() for p in POLICIES}
    for index, old in enumerate(fixtures):
        for offset, policy in enumerate(POLICIES):
            row = table[index * 6 + offset]
            require((row['row_index'], row['policy']) == (index, policy), 'row order/identity')
            a, b = old['method_a_ruler_index'], old['method_b_ruler_index']
            expected = expected_traces[policy]
            c11, c12, joint = truths(expected, a, b)
            require(row['truth'] == {'c11': c11, 'c12': c12, 'joint': joint}, 'independent truth')
            require(row['equal_pair'] is (a == b), 'numeric equality')
            stop = expected['stop']['clause'] if expected['stop'] else None
            require(row['first_stop'] == stop, 'numeric row stop')
            require(row['reference_override'] is (old['candidate'] == 'SAME_METHOD_REFERENCE'),
                    'old reference replacement disclosed')
            inherited = {key: old[key] for key in numeric_keys}
            inherited.update(old_c11_same=old['C11_same'], old_c12_agrees=old['C12_agrees'],
                             old_argument_coherent=old['argument_coherent'])
            require(row['inherited_numeric'] == inherited, 'all declared numeric fields unchanged')
            require(row['nonreference_costs'] == {
                'extra_scope_assumptions': old['extra_scope_assumptions'],
                'new_word_changes': old['new_word_changes']}, 'all nonreference costs unchanged')
            aggregation[policy]['unbound' if joint is None else 'true' if joint else 'false'] += 1
    positions = []
    source_path = str((OLD / 'src/SOURCE.json').relative_to(ROOT))
    for record in source['records']:
        for word in record['raw'].split():
            positions.append({'position': len(positions) + 1, 'locus': record['locus'],
                              'word': word, 'inherited_source': source_path})
    coverage = read(directory / 'SOURCE_COVERAGE.json')
    require(coverage == {'status': 'INHERITED_SOURCE_COVERAGE', 'position_count': 80,
                         'source': source_path, 'source_sha256': FIXED_HASHES['src/SOURCE.json'],
                         'positions': positions}, 'full exact 80-position source coverage')
    result = read(directory / 'RESULT.json')
    require(result['experiment'] == 'GDT1039' and
            result['status'] == 'COMPLETE_CONDITIONAL_REFERENCE_AUDIT', 'result status')
    for key, value in [('rows', 357), ('policies', 6), ('comparison_rows', 2142),
                       ('fetches', 7), ('source_coverage', 80), ('semantic_confirmation', 0)]:
        require(result[key] == value, 'result count ' + key)
    require(result['complete_coherence_claim'] is False, 'no whole-coherence claim')
    require(result['policy_stops'] == {p: t['stop']['clause'] if t['stop'] else None
                                      for p, t in expected_traces.items()}, 'result stops')
    receipt = read(directory / 'PUBLIC_REGISTRATION.json')
    require(result['registered_commit'] == receipt['commit'], 'result publication receipt')
    require(result['claim_ceiling'] == read(HERE / 'src/SPEC.json')['claim_ceiling'], 'claim ceiling')
    return {'validated_rows': len(table), 'validated_positions': 80,
            'validated_constructor_inventory': 12, 'validated_fetch_records': fetch_count,
            'policy_joint_truths': {p: dict(c) for p, c in aggregation.items()},
            'legacy_fixture_sha256': FIXED_HASHES['artifacts/ROWS.json'],
            'legacy_full_fixtures_retained_at': str((OLD / 'artifacts/ROWS.json').relative_to(ROOT)),
            'artifact_schema_adapted_after_independent_oracle': True,
            'prepublic_oracle_exposure': 'full authored target event stream with five synthetic numeric pairs'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    require(args.self_test != args.execute, 'choose exactly --self-test or --execute')
    receipt = check_registration() if args.execute else None
    checks = self_test()
    if args.self_test:
        print(json.dumps({'status': 'PASS', 'synthetic_checks': checks,
                          'authored_target_event_replay': True,
                          'numeric_values': 'synthetic_only',
                          'actual_357_fixture_replay': False}))
        return 0
    source, model, fixtures = original_inventory()
    validate_spec()
    outcome = validate_artifacts(source, model, fixtures)
    outcome.update(status='PASS', synthetic_checks=checks, public_commit=receipt['commit'],
                   independent_oracle='deque_event_model_no_primary_import',
                   confirmed_words=0, independent_meaning_capacity=0)
    (HERE / 'artifacts/VALIDATION.json').write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: outcome[k] for k in ('status', 'synthetic_checks', 'validated_rows')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Independent narrow accounting and Boolean-state check; no builder imports."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(name):
    return json.loads((HERE / name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    plan = read('RESERVE80_PLAN_20261015.json')
    result = read('RESERVE80_READING_20261015.json')
    source_path = ROOT / plan['source']['path']
    assert digest(source_path) == plan['source']['sha256']
    source = json.loads(source_path.read_text())
    for path, expected in result['input_sha256'].items():
        assert digest(ROOT / path) == expected, path
    assert result['builder_sha256'] == digest(HERE / 'RESERVE80_BUILD_20261015.py')
    assert result['assumptions'] == plan['assumptions']
    assert '115' in plan['operator']['mention']
    assert 'DISTINCT' in plan['operator']['I_rival']
    assert result['preserved_documents'] == source['documents']
    assert result['explicit_anchor_sites'] == source['explicit_anchor_sites']
    assert len(source['explicit_anchor_sites']) == 5

    packets = {p: read(n) for p, n in [
        ('f45r', 'F45R_WHOLE_PAGE_SOURCE_20261015.json'),
        ('f89r1', 'F89R1_Q2_SOURCE_20261015.json')]}
    raw = {}
    for packet in packets.values():
        it = packet['readers']['IT2a']
        for line in it['lines']:
            for vector in line['groups']:
                row = dict(zip(it['group_columns'], vector))
                assert row['source_group_id'] not in raw
                raw[row['source_group_id']] = row

    expected_ops, expected_other, descriptions = [], [], {}
    timelines = {}
    for doc in source['documents']:
        timeline = doc['trace']
        timelines[doc['page']] = timeline
        for token in timeline:
            assert token['raw'] == raw[token['id']]['ivtff_group_raw']
        for record in doc['records']:
            for entry in record['ordered_entries']:
                descriptions.setdefault(entry['referent'], set()).add(entry['descriptor'])
            for construction in record['constructions']:
                descriptions.setdefault(construction['argument'], set()).add(construction['descriptor'])
                for relation in construction['relations']:
                    if relation['relation'] != 'daiin':
                        expected_other.append(dict(construction=construction['id'], **relation))
                    else:
                        expected_ops.append((doc['page'], record['context'], construction))
    assert result['other_relations'] == expected_other
    assert len(expected_other) == 10
    assert {r['relation'] for r in expected_other} == {'cthy', 'cthey', 'or', 'dy'}
    actual_ops = result['operations']
    assert len(actual_ops) == len(expected_ops) == 10
    for page, context, con in expected_ops:
        found = [o for o in actual_ops if o['id'] == con['id']]
        assert len(found) == 1
        op = found[0]
        assert op['page'] == page and op['context'] == context
        for key in ('source_ids', 'raw', 'descriptor', 'anchor_source_id'):
            assert op[key] == con[key], key
        assert op['resource_variable'] == con['argument']
        assert op['resource_identity'] is None and op['initial_availability'] is None
        assert op['native_evaluation'] == 'UNKNOWN'
        assert op['distinct_use'] == 'ASSUMED_NOT_SOURCE_CONFIRMED'
    used = [sid for op in actual_ops for sid in op['source_ids']]
    assert len(used) == len(set(used)) == 17
    resource_variables = {op['resource_variable'] for op in actual_ops}
    assert len(resource_variables) == 10
    descriptions = {v: ds for v, ds in descriptions.items() if v in resource_variables}
    assert len(result['nominal_resources']) == len(descriptions)
    for row in result['nominal_resources']:
        assert row['unknown_descriptions'] == sorted(descriptions.pop(row['variable']))
        assert row['identity'] is None and row['availability'] is None
    assert not descriptions

    interval_lengths, direct = {}, []
    checked_pairs = 0
    for page, timeline in timelines.items():
        indices = {t['id']: i for i, t in enumerate(timeline)}
        ops = sorted((o for o in actual_ops if o['page'] == page),
                     key=lambda o: indices[o['source_ids'][0]])
        interval_lengths[page] = []
        for a, b in zip(ops, ops[1:]):
            gap = timeline[indices[a['source_ids'][-1]] + 1:indices[b['source_ids'][0]]]
            interval_lengths[page].append(len(gap))
            span = timeline[indices[a['source_ids'][0]]:indices[b['source_ids'][-1]] + 1]
            seams = [dict(left_id=x['id'], right_id=y['id'],
                          right_separator=raw[x['id']]['right_separator'],
                          left_separator=raw[y['id']]['left_separator'])
                     for x, y in zip(span, span[1:])]
            safe = not gap and a['context'] == b['context'] and all(
                s['right_separator'] == s['left_separator'] == 'DEFINITE_SPACE' for s in seams)
            matches = [p for p in result['consecutive_operation_pairs']
                       if (p['first'], p['second']) == (a['id'], b['id'])]
            assert len(matches) == 1
            p = matches[0]
            assert p['page'] == page and p['intervening_groups'] == gap
            assert p['intervening_count'] == len(gap) and p['seams'] == seams
            assert p['state_propagation'] == ('CONDITIONAL_DIRECT_LOCAL_ONLY' if safe else 'UNKNOWN')
            if safe:
                direct.append([t['raw'] for t in span])
            checked_pairs += 1
    assert interval_lengths == {'f45r': [17, 1, 16, 23], 'f89r1': [7, 3, 0, 11]}
    assert checked_pairs == len(result['consecutive_operation_pairs']) == 8
    assert direct == [['oiiin', 'daiin', 'qokeey', 'daiin']]

    assert set(result['reader_span']) == {'IT2a', 'ZL3b', 'RF1b'}
    for edition, saved in result['reader_span'].items():
        packet = packets['f89r1']['readers'][edition]
        line = next(l for l in packet['lines'] if l['metadata']['locus'] == 'f89r1.9')
        assert saved['metadata'] == line['metadata']
        assert saved['group_columns'] == packet['group_columns']
        assert saved['complete_source_line'] == line['groups']
        strings = [dict(zip(packet['group_columns'], v))['ivtff_group_raw'] for v in line['groups']]
        hits = [i for i in range(len(strings) - 3) if strings[i:i+4] == direct[0]]
        assert len(hits) == 1
        assert saved['exact_span'] == line['groups'][hits[0]:hits[0]+4]

    # Independent Boolean availability model. These are supplied synthetic
    # identities; they do not assign resource identities to the manuscript.
    scenarios = result['formal_scenarios']
    assert scenarios['status'] == 'SYNTHETIC_IDENTITY_INPUTS_NOT_NATIVE_BINDINGS'
    for mode in ('R', 'I'):
        for same in (True, False):
            names = ('x', 'x' if same else 'y')
            available = {name: True for name in names}
            expected_steps = []
            for name in names:
                before = {k: 'AVAILABLE' if v else 'COMMITTED' for k, v in available.items()}
                valid = mode == 'I' or available[name]
                if valid:
                    available[name] = False
                after = {k: 'AVAILABLE' if v else 'COMMITTED' for k, v in available.items()} if valid else None
                expected_steps.append(dict(resource=name, before=before,
                    status='OK' if valid else 'INVALID_ALREADY_COMMITTED', after=after))
                if not valid:
                    break
            got = scenarios[mode + ('_same' if same else '_different')]
            assert got['identity_input'] == ('SAME' if same else 'DIFFERENT')
            assert got['steps'] == expected_steps
            assert got['both_execute'] == (mode == 'I' or not same)
    total = sum(len(t) for t in timelines.values())
    assert total == 132
    assert result['summary'] == dict(raw_groups=132, operations=10, operation_raw_groups=17,
        other_raw_groups=115, retained_anchor_occurrences=5, consecutive_pairs=8,
        direct_pairs=1, unknown_transition_pairs=7, unknown_other_relation_occurrences=10,
        confirmed_words=0)
    return dict(status='PASS', preserved_raw_groups=total, preserved_anchors=5,
        operation_groups=17, unread_other_groups=115, other_relation_occurrences=10,
        interval_lengths=interval_lengths, direct_pairs=1, reader_full_lines_and_spans=3,
        synthetic_scenarios=4, native_identity_or_semantic_validation=False,
        limits='Source/accounting and supplied-identity Boolean scenario check only; no native execution or meaning selection.')


if __name__ == '__main__':
    receipt = validate()
    receipt['hashes'] = {n: digest(HERE / n) for n in (
        'RESERVE80_PLAN_20261015.json', 'RESERVE80_READING_20261015.json',
        'RESERVE80_VALIDATE_20261015.py')}
    (HERE / 'RESERVE80_VALIDATION_20261015.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))

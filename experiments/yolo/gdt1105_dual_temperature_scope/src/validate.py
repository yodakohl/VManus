#!/usr/bin/env python3
"""Independent source, owner and finite-constraint validation; no meanings."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
source_path = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/CF_FULL_LEAVES.json'
source = json.loads(source_path.read_text())
spec = json.loads((BASE / 'src/MODEL.json').read_text())
result = json.loads((BASE / 'artifacts/RESULT.json').read_text())
packet = json.loads((BASE / 'artifacts/RUNS.json').read_text())
lock = json.loads((BASE / 'PREREG_LOCK.json').read_text())
for path, digest in lock['sha256'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
for path, digest in result['input_hashes'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
assert packet['input_sha256'] == hashlib.sha256(source_path.read_bytes()).hexdigest()
assert hashlib.sha256((ROOT / source['command'][2]).read_bytes()).hexdigest() == source['source_sha256']
assert len(source['rows']) == 1070 and len(source['lines']) == 129
assert {r['page'] for r in source['rows']} == {'f9r', 'f9v', 'f50r', 'f50v'}
assert all(not r['page'].startswith('f84') for r in source['rows'])
vocab = set(spec['nominals']) | set(spec['fields']) | set(spec['compound'])
expected_vocabulary_ids = {r['source_group_id'] for r in source['rows'] if r['ivtff_group_raw'] in vocab}
actual_vocabulary_rows = [r for run in packet['runs'] for r in run['groups']]
assert {r['source_group_id'] for r in actual_vocabulary_rows} == expected_vocabulary_ids
assert len(actual_vocabulary_rows) == len(expected_vocabulary_ids) == 93
assert len(packet['runs']) == 62
source_by_id = {r['source_group_id']: r for r in source['rows']}
for row in actual_vocabulary_rows:
    assert row == source_by_id[row['source_group_id']]

# Determine a field's source interval by walking original raw neighbours,
# independently of the runner's retained-run/owner functions.
reference = {}
for line in source['lines']:
    rows = line['groups']
    for index, row in enumerate(rows):
        if row['ivtff_group_raw'] not in spec['fields'] | spec['compound']:
            continue
        left, right = index, index
        while left > 0 and rows[left - 1]['ivtff_group_raw'] in vocab:
            left -= 1
        while right + 1 < len(rows) and rows[right + 1]['ivtff_group_raw'] in vocab:
            right += 1
        heads = [i for i in range(left, right + 1) if rows[i]['ivtff_group_raw'] in spec['nominals']]
        previous = [i for i in heads if i < index]
        following = [i for i in heads if i > index]
        owner = previous[-1] if previous else following[0] if following else None
        split_owner = owner
        if previous and following and following[0] - previous[-1] == 3 and index == following[0] - 1:
            split_owner = following[0]
        reference[row['source_group_id']] = {
            'row': row, 'LEFT_FLAT': rows[owner]['source_group_id'] if owner is not None else None,
            'PAIR_SPLIT': rows[split_owner]['source_group_id'] if split_owner is not None else None}
assert len(reference) == 66
models = {(m['ownership'], m['polarity'], m['mask']): m for m in result['models']}
assert len(models) == 64
assert set(models) == {(p, sign, mask) for p in spec['ownership_models'] for sign in spec['polarity_orders'] for mask in range(16)}
expected_survivors = []
for (policy, polarity, mask), model in models.items():
    reported = {c['source']: c for c in model['bound_claims'] + model['unbound_fields'] if c['kind'] == 'whole_field_C0'}
    assert set(reported) == set(reference)
    for identity, ref in reference.items():
        raw = ref['row']['ivtff_group_raw']
        field = spec['fields'].get(raw) or spec['compound'][raw]
        domain = field.get('domain')
        if domain is None:
            cell = 2 * field['wrapped'] + field['tail_value']
            domain = 'natural' if mask & (1 << cell) else 'physical'
        thermal = 'hot' if (field['polarity'] == 'k') == (polarity == 'k_hot') else 'cold'
        assert reported[identity]['owner'] == ref[policy]
        assert reported[identity]['domain'] == domain and reported[identity]['thermal'] == thermal
    grouped = defaultdict(set)
    for claim in model['bound_claims']:
        assert claim['owner'] is not None
        grouped[(claim['edition'], claim['owner'], claim['domain'])].add(claim['thermal'])
    clashes = {k for k, values in grouped.items() if len(values) == 2}
    assert clashes == {(c['edition'], c['owner'], c['domain']) for c in model['contradictions']}
    assert model['survives_all_readers_conditionally'] == (not clashes)
    # Solve the three complete raw focal constructions symbolically.
    bits = [(mask >> i) & 1 for i in range(4)]
    expected = bits[2] != bits[3]
    if policy == 'LEFT_FLAT':
        expected = expected and bits[1] != bits[3]
    if polarity == 'k_hot':
        expected = expected and bits[1] == bits[2] == 0
    assert model['survives_all_readers_conditionally'] == expected
    if expected:
        expected_survivors.append(model['id'])
assert result['survivors'] == expected_survivors and len(expected_survivors) == 16
assert len(result['surviving_prediction_groups']) == 8
assert sorted(x for group in result['surviving_prediction_groups'] for x in group) == sorted(expected_survivors)
for group in result['surviving_prediction_groups']:
    matches = [m for m in models.values() if m['id'] in group]
    assert all(m['bound_claims'] == matches[0]['bound_claims'] and m['unbound_fields'] == matches[0]['unbound_fields'] for m in matches)
assert result['observed_feature_cells'] == [1, 2, 3]
assert result['confirmed_words'] == result['independent_meaning_confirmation_leaves'] == 0
receipt = {'status': 'PASS_SOURCE_AND_CONDITIONAL_MODEL_REPLAY_NOT_MEANING',
    'meaning_verified': False, 'models': 64, 'conditional_survivors': 16,
    'distinct_surviving_observed_predictions': 8, 'source_groups': 1070,
    'written_vocabulary_positions': 93, 'fields': 66,
    'checks': ['preregistered hashes and original source bytes', 'all source vocabulary positions conserved',
        'independent raw-neighbour owner calculation', 'all64 domain and polarity assignments',
        'direct symbolic solution of every clash-producing site', 'all indistinguishable pairs retained'],
    'file_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
        (source_path, BASE / 'src/MODEL.json', BASE / 'PREREG_LOCK.json', BASE / 'src/run.py',
         BASE / 'src/scope_models.py', BASE / 'src/validate.py', BASE / 'artifacts/RESULT.json', BASE / 'artifacts/RUNS.json')}}
(BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], '64models;16conditional survivors;8 observed prediction groups')

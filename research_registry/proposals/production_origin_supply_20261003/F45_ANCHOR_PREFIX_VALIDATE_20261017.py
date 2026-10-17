#!/usr/bin/env python3
"""Compare authored output with saved independent precomputation; not semantics."""
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(name):
    return json.loads((D / name).read_text())


a = read('F45_ANCHOR_PREFIX_READING_20261017.json')
b = read('F45_ANCHOR_PREFIX_INDEPENDENT_20261017.json')
parent = read('F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json')
old = read('F45COPY.json')
for pin in a['pins']:
    assert sha(ROOT / pin['path']) == pin['sha256']
for path, digest in b['pins'].items():
    p = D / path if Path(path).parent == Path('.') else ROOT / path
    assert sha(p) == digest, path
assert a['original_trace'] == b['original_trace'] == parent['trace'] == old['original_trace']
assert not b['primary_new_output_compared']
assert [r['record'] for r in a['records']] == ['P1', 'P2', 'P3']
coverage, copies = [], []
for record, before in zip(a['records'], old['records'], strict=True):
    name = record['record']
    assert record['A_words'] == b['expanded_A_words'][name]
    assert record['B'] == b['unchanged_B'][name] == before['B']
    normalized = [{**{k: v for k, v in item.items() if k != 'copy_via'},
                   'copy_events': item['copy_via']} for item in record['A']]
    assert normalized == b['expanded_A_with_provenance'][name]
    for step in record['program']:
        coverage.extend(step['event']['source_ids'] if step['kind'] == 'UNCHANGED_B'
                        else step['source_ids'])
        if step['kind'] == 'COPY_ANCHOR_PREFIX':
            copies.append(step)
assert coverage == [r['id'] for r in parent['trace']] and len(set(coverage)) == 86
assert len(copies) == len(b['two_copied_payloads']) == 2
for actual, expected in zip(copies, b['two_copied_payloads'], strict=True):
    for key in ['source_ids', 'source_record', 'target_record', 'anchor_source_id',
                'insertion_offset', 'payload_length']:
        assert actual[key] == expected[key], key
    assert actual['payload_words'] == expected['payload_descriptors']
final = b['final_DALDAIIN']
assert final['unchanged_from_R1_and_1104'] and final['resolved_entity'] == 'P2.subject'
assert a['records'][2]['B']['daiin']['value'] == final['resolved_entity']
assert a['summary']['new_expanded_A_lengths'] == [27, 24, 36]
assert a['summary']['non_DY_field_events'] == 12
assert all(r['B'] == {k: v for k, v in pr['fields'].items() if k != 'dy'}
           for r, pr in zip(a['records'], parent['records'], strict=True))
result = {
    'status': 'PASS_ACCOUNTING_ONLY_NOT_MEANING',
    'checks': ['input bytes', 'all86original groups and order', 'all three exact A-lists',
               'every copied occurrence provenance', 'two exact anchor-prefix payloads',
               'all12non-DY events and B-fields', 'finalDALDAIIN retains P2reference'],
    'independent_precomputation_sha256': sha(D / 'F45_ANCHOR_PREFIX_INDEPENDENT_20261017.json'),
    'reading_sha256': sha(D / 'F45_ANCHOR_PREFIX_READING_20261017.json'),
    'validator_sha256': sha(Path(__file__)),
    'limits': ['Expected counts were disclosed; no blind prediction.',
               'Separate derivation of the same assumptions is not manuscript confirmation.',
               'No word meaning, COPY choice or prefix-scope preference established.']
}
(D / 'F45_ANCHOR_PREFIX_VALIDATION_20261017.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result))

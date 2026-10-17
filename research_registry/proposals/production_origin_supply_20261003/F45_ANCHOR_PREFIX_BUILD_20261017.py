#!/usr/bin/env python3
"""Derive one exploratory f45r scope alternative; no decoder or word meanings."""
import collections
import copy
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]


def read(name):
    return json.loads((D / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parent = read('F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json')
old = read('F45COPY.json')
rules = read('F45R_RECORD_SYNTHESIS_RULES_20261015.json')
assert sha(D / 'F45R_RECORD_SYNTHESIS_RULES_20261015.json') == parent['rules_sha256']
assert sha(ROOT / rules['source']) == parent['source_sha256'] == rules['source_sha256']
assert parent['trace'] == old['original_trace']
for pin in old['pins']:
    assert sha(ROOT / pin['path']) == pin['sha256'], pin['path']

trace = {r['id']: r for r in parent['trace']}
events = {e['id']: e for r in parent['records'] for e in r['field_events']}
snapshots = {}
finished = {}
records = []
copy_events = []
coverage = []

for before in old['records']:
    name = before['record']
    body, program, anchors = [], [], []
    for step in before['program']:
        kind = step['kind']
        if kind == 'UNCHANGED_B':
            program.append(copy.deepcopy(step))
            coverage.extend(step['event']['source_ids'])
            continue
        coverage.extend(step['source_ids'])
        if kind in ('LITERAL_A', 'LOCAL_A_FROM_FREE_DY'):
            body.append({'descriptor': step['descriptor'], 'origin_record': name,
                         'origin_source_ids': list(step['source_ids']), 'copy_via': []})
            program.append(copy.deepcopy(step))
            if kind == 'LITERAL_A':
                source_id, = step['source_ids']
                assert trace[source_id]['kind'] == 'subject_description'
                assert trace[source_id]['descriptor'] == step['descriptor']
                snapshots[source_id] = copy.deepcopy(body)
                anchors.append({'source_id': source_id, 'descriptor': step['descriptor'],
                                'prefix_length': len(body)})
            continue
        assert kind == 'COPY_A', kind
        source_id, = step['source_ids']
        ev = events[trace[source_id]['event']]
        assert ev['kind'] == 'bound_field' and ev['roles'] == ['dy']
        assert ev['raw'][0] in ('opchaldy', 'daldy')
        source_record = step['source_record']
        assert source_record in finished and ev['anchor_record'] == source_record
        candidates = [a for a in finished[source_record]['anchors']
                      if a['descriptor'] == ev['descriptor']]
        anchor, = candidates
        payload = copy.deepcopy(snapshots[anchor['source_id']])
        for item in payload:
            item['copy_via'].append(source_id)
        assert len(body) == step['insertion_offset']
        new_step = {'kind': 'COPY_ANCHOR_PREFIX', 'source_ids': list(step['source_ids']),
                    'source_record': source_record, 'target_record': name,
                    'anchor_source_id': anchor['source_id'],
                    'anchor_descriptor': ev['descriptor'],
                    'insertion_offset': len(body), 'payload_length': len(payload),
                    'payload_words': [x['descriptor'] for x in payload],
                    'old_completed_payload_length': step['payload_length']}
        body.extend(payload)
        program.append(new_step)
        copy_events.append(new_step)
    record = {'record': name, 'subject': before['subject'], 'A': body,
              'A_words': [x['descriptor'] for x in body], 'B': copy.deepcopy(before['B']),
              'program': program, 'anchors': anchors}
    records.append(record)
    finished[name] = record

assert coverage == [r['id'] for r in parent['trace']]
assert len(coverage) == len(set(coverage)) == 86
assert [len(r['A']) for r in records] == [27, 24, 36]
assert [e['payload_length'] for e in copy_events] == [7, 18]
assert all(a['B'] == b['B'] for a, b in zip(records, old['records'], strict=True))

facts = collections.defaultdict(set)
for record in records:
    facts[record['subject']].update(record['A_words'])
    for field in record['B'].values():
        facts[field['value']].update(field['descriptions'])
assert 'kol' not in facts['P2.subject'] and 'kol' in facts['P3.subject']
assert {'dor', 'otydal'} <= facts['P2.subject']

changes = []
for before, after in zip(old['records'], records, strict=True):
    missing = collections.Counter(before['A_words']) - collections.Counter(after['A_words'])
    added = collections.Counter(after['A_words']) - collections.Counter(before['A_words'])
    changes.append({'record': after['record'], 'old_A_length': len(before['A']),
                    'new_A_length': len(after['A']), 'removed_occurrences': dict(sorted(missing.items())),
                    'added_occurrences': dict(sorted(added.items())),
                    'old_chol_count': before['A_words'].count('chol'),
                    'new_chol_count': after['A_words'].count('chol'),
                    'old_ykeol_count': before['A_words'].count('ykeol'),
                    'new_ykeol_count': after['A_words'].count('ykeol')})

signed = []
for q, base in [('qoky', 'oky'), ('qokaiin', 'okaiin')]:
    signed.append({'q_form': q, 'base_form': base,
                   'old_P3_contains_both': q in old['records'][2]['A_words'] and base in old['records'][2]['A_words'],
                   'new_P3_contains_both': q in records[2]['A_words'] and base in records[2]['A_words']})

inputs = ['F45_ANCHOR_PREFIX_PROPOSAL_20261017.json', 'F45COPY.json',
          'F45_COPY_PROFILES_20261017.json', 'F45R_RECORD_SYNTHESIS_RULES_20261015.json',
          'F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json']
paths = [D / n for n in inputs] + [ROOT / rules['source'], Path(__file__)]
result = {
    'status': 'COMPLETE_EXPLORATORY_SCOPE_ALTERNATIVE_NO_SEMANTIC_SELECTION',
    'original_trace': parent['trace'],
    'summary': {'original_groups': 86, 'paragraph_groups': [33, 21, 32],
                'old_expanded_A_lengths': [27, 44, 62],
                'new_expanded_A_lengths': [len(r['A']) for r in records],
                'copied_payload_lengths': [e['payload_length'] for e in copy_events],
                'copied_A_occurrences': sum(e['payload_length'] for e in copy_events),
                'non_DY_field_events': sum(s['kind'] == 'UNCHANGED_B' for r in records for s in r['program']),
                'confirmed_words': 0},
    'records': records,
    'content_changes_from_completed_copy': changes,
    'new_subject_and_B_descriptor_constraints': {k: sorted(v) for k, v in sorted(facts.items())},
    'optional_old_signed_pair_presence': signed,
    'signed_ceiling': 'No q meaning or empirical preference: the old clash is absent only after changing the copy scope with that clash already visible. Original whole-copy failure remains.',
    'limits': ['COPY, its anchor relation and the new snapshot scope are authored, not decoded.',
               'Known field typing, free/bound distinction, reader disagreements and counterexamples are not resolved.',
               'Expanded A alone is not a unique inverse; the complete original trace is retained.',
               'Order and repeated entries are preserved, but their human purpose and root meanings remain unknown.',
               'No native image, new query, reserve, language key or translated word.'],
    'pins': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in paths]
}
(D / 'F45_ANCHOR_PREFIX_READING_20261017.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result['summary']))

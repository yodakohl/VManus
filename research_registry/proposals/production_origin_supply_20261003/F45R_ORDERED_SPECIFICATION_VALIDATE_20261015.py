#!/usr/bin/env python3
"""Bounded Q1 accounting audit. No builder import, new corpus or model test."""
import collections
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').is_file())
NAMES = {
    'proposal': 'F45R_ORDERED_SPECIFICATION_PROPOSAL_20261015.json',
    'builder': 'F45R_ORDERED_SPECIFICATION_BUILD_20261015.py',
    'derivation': 'F45R_ORDERED_SPECIFICATION_DERIVATION_20261015.json',
}


def read(name):
    return json.loads((HERE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proposal = read(NAMES['proposal'])
    design = proposal['design']
    source = read(design['source'])
    r1 = read(design['r1_derivation'])
    actual = read(NAMES['derivation'])
    assert sha(HERE / design['source']) == design['source_sha256'] == actual['source_sha256']
    assert sha(HERE / design['r1_derivation']) == design['r1_derivation_sha256'] == actual['frozen_lexing_sha256']
    assert sha(HERE / NAMES['proposal']) == actual['proposal_sha256']
    assert actual['primary_reader'] == 'IT2a'
    # Independently obtain record spans from the unchanged source flags.
    primary = source['readers']['IT2a']
    paragraphs, flat, current = [], [], None
    for line in sorted(primary['lines'], key=lambda x: int(x['metadata']['source_row_index'])):
        m = line['metadata']
        assert m['edition'] == 'IT2a' and m['page'] == 'f45r' and m['kind'] == 'P'
        groups = [dict(zip(primary['group_columns'], g)) for g in line['groups']]
        assert len(groups) == int(m['source_group_count'])
        assert [int(g['source_group_index']) for g in groups] == list(range(1, len(groups) + 1))
        if m['paragraph_start'] == '1':
            assert current is None
            current = []
        assert current is not None
        for g in groups:
            t = dict(id=g['source_group_id'], raw=g['ivtff_group_raw'], locus=m['locus'])
            current.append(t)
            flat.append(t)
        if m['paragraph_end'] == '1':
            paragraphs.append(current)
            current = None
    assert current is None
    assert len(flat) == len({t['id'] for t in flat})
    assert [{k: t[k] for k in ('id', 'raw', 'locus')} for t in r1['trace']] == flat
    assert [{k: t[k] for k in ('id', 'raw', 'locus')} for t in actual['trace']] == flat

    # R1 provides only occurrence grouping. Its entities, equalities, records'
    # resolved arguments and previous-paragraph candidates are never read.
    trace_by_id = {t['id']: t for t in r1['trace']}
    graph = collections.defaultdict(set)
    kinds, assertions, equalities, records, prior, ambiguities = {}, [], [], [], [], []
    expected_trace = []

    def add(name, kind):
        if name in kinds:
            assert kinds[name] == kind
        kinds[name] = kind
        graph[name]

    def connect(left, right, reason, ids):
        graph[left].add(right)
        graph[right].add(left)
        equalities.append(dict(left=left, right=right, reason=reason, source_ids=ids))

    for index, paragraph in enumerate(paragraphs, 1):
        rid = f'P{index}'
        record = dict(record=rid, entries=[], field_events=[], fields={})
        traces = [trace_by_id[t['id']] for t in paragraph]
        assert all(t['record'] == rid for t in traces)
        seen_events = set()
        for eid, grouped in itertools.groupby(traces, key=lambda t: t['event']):
            group = list(grouped)
            assert eid not in seen_events
            seen_events.add(eid)
            first = group[0]
            descriptor, roles = first['descriptor'], first['roles']
            ids = [t['id'] for t in group]
            position = None
            if first['kind'] == 'subject_description':
                assert len(group) == 1 and roles == [] and descriptor == first['raw']
                position = f'{rid}.S{len(record["entries"]) + 1:03d}'
                ref = position + '.referent'
                add(ref, 'entry_referent')
                record['entries'].append(dict(position=position, referent=ref,
                                              descriptor=descriptor, source_id=ids[0]))
                assertions.append(dict(entity=ref, descriptor=descriptor,
                                       source_ids=ids, origin='ordinary_entry'))
            else:
                assert first['kind'] in {'free_field', 'bound_field'} and roles
                if first['kind'] == 'free_field':
                    assert all(t['kind'] == 'free_marker' and t['descriptor'] is None for t in group[1:])
                    assert [t['raw'] for t in group[1:]] == roles
                else:
                    assert len(group) == 1
                argument = eid + '.argument'
                add(argument, 'field_argument')
                # Each occurrence is a candidate; repetitions in one record
                # deliberately remain separate instead of set-deduplication.
                matches = [e for e in prior if e['descriptor'] == descriptor]
                event = dict(id=eid, kind=first['kind'], descriptor=descriptor,
                             roles=roles, source_ids=ids, raw=[t['raw'] for t in group],
                             argument=argument, prior_candidates=[e['position'] for e in matches])
                assertions.append(dict(entity=argument, descriptor=descriptor,
                                       source_ids=ids, origin='field_argument'))
                for role in roles:
                    field = rid + '.field.' + role
                    add(field, 'field_value')
                    connect(field, argument, 'one field value per role and paragraph', ids)
                if len(matches) == 1:
                    anchor = matches[0]
                    event.update(anchor_position=anchor['position'], anchor_source_id=anchor['source_id'])
                    connect(argument, anchor['referent'], 'stipulated unique prior occurrence reprise', ids)
                elif len(matches) > 1:
                    ambiguities.append(dict(event=eid, candidates=event['prior_candidates']))
                record['field_events'].append(event)
            for t in group:
                expected_trace.append(dict(t, kind='ordinary_entry' if t['kind'] == 'subject_description' else t['kind'],
                                           ordinary_position=position))
        records.append(record)
        prior.extend(record['entries'])  # only now is this paragraph completed

    # Connected components are independent of the builder's union-find code.
    canonical, entities, identity_obligations = {}, [], []
    remaining = set(kinds)
    while remaining:
        component = {min(remaining)}
        queue = list(component)
        while queue:
            for other in graph[queue.pop()]:
                if other not in component:
                    component.add(other)
                    queue.append(other)
        remaining -= component
        refs = sorted(n for n in component if kinds[n] == 'entry_referent')
        fields = sorted(n for n in component if kinds[n] == 'field_value')
        cid = (refs or fields)[0]
        canonical.update({n: cid for n in component})
        if len(refs) > 1:
            identity_obligations.append(refs)
        descriptions = [a for a in assertions if a['entity'] in component]
        entities.append(dict(id=cid, entry_referents=refs, field_values=fields,
                             descriptions=descriptions, descriptor_set=sorted({a['descriptor'] for a in descriptions})))
    for record in records:
        for entry in record['entries']:
            entry['resolved_referent'] = canonical[entry['referent']]
        for event in record['field_events']:
            event['resolved_referent'] = canonical[event['argument']]
            for role in event['roles']:
                slot = record['fields'].setdefault(role, dict(value=canonical[record['record'] + '.field.' + role], descriptions=[], events=[]))
                assert slot['value'] == event['resolved_referent']
                slot['descriptions'].append(event['descriptor'])
                slot['events'].append(event['id'])
    assert records == actual['records']
    assert equalities == actual['equalities']
    assert expected_trace == actual['trace']
    # Assertion construction order is immaterial; source IDs and multiplicity
    # are not. The ordered entries and the source trace were compared exactly.
    def normalized_entities(items):
        return sorted([dict(e, descriptions=sorted(e['descriptions'], key=lambda x: json.dumps(x, sort_keys=True)))
                       for e in items], key=lambda e: e['id'])
    assert normalized_entities(entities) == normalized_entities(actual['entities'])
    summary = dict(raw_groups=len(flat), paragraph_groups=[len(p) for p in paragraphs],
                   ordered_entries=[len(r['entries']) for r in records],
                   total_ordered_entries=sum(len(r['entries']) for r in records),
                   field_mentions=sum(len(r['field_events']) for r in records),
                   functional_fields=sum(len(r['fields']) for r in records),
                   explicit_reprises=sum('anchor_position' in e for r in records for e in r['field_events']),
                   unknown_description_types=len({a['descriptor'] for a in assertions}),
                   reference_ambiguities=ambiguities, competing_anchor_identities=identity_obligations,
                   group_roles=dict(collections.Counter(t['kind'] for t in expected_trace)))
    assert summary == actual['summary']
    repeats = {w: [{'position': e['position'], 'source_id': e['source_id']} for r in records
                   for e in r['entries'] if e['descriptor'] == w]
               for w in ['chol', 'ykeol', 'okaiin']}
    assert all(len(entries) == 2 and len({e['position'] for e in entries}) == 2 for entries in repeats.values())
    anchors = [{k: e[k] for k in ['id', 'descriptor', 'source_ids', 'anchor_position', 'anchor_source_id']}
               for r in records for e in r['field_events'] if 'anchor_position' in e]
    dal = next(e for e in entities if 'P2.S011.referent' in e['entry_referents'])
    assert set(dal['descriptor_set']) == {'dal', 'kol', 'dor', 'otydal'}
    assert dal['entry_referents'] == ['P2.S011.referent']
    assert not any('.subject' in n for n in kinds)
    pins = [HERE / name for name in NAMES.values()] + [HERE / design['source'], HERE / design['r1_derivation']]
    report = dict(status='PASS_INDEPENDENT_Q1_ACCOUNTING_NOT_MEANING',
                  method='Source-flag paragraphs; event grouping only from frozen R1 trace; occurrence-list reprise search; independent graph components. No builder import or execution.',
                  input_sha256={str(p.relative_to(ROOT)): sha(p) for p in pins},
                  validator_sha256=sha(Path(__file__)), derived_summary=summary,
                  anchor_occurrences=anchors, retained_repeated_positions=repeats,
                  dal_entry_constraint=dict(entry='P2.S011', source_id='IT2a|f45r.6|G007',
                                            descriptors=dal['descriptor_set'], field_values=dal['field_values']),
                  checked_limits=[
                      'All86rawgroup IDs/spellings/order preserved exactly once; own IT paragraph flags give33/21/32.',
                      'Ordinary positions are27/17/17; consumed field hosts are not duplicated as ordinary entries.',
                      'Lookup uses earlier completed ordinary occurrences only. Multiple same-word occurrences in one paragraph are not collapsed into one candidate.',
                      'Only R1 token grouping is inherited, not any paragraph-subject equality or inferred property.',
                      'KOL/DOR/OTYDAL constrain the one referenced DAL entry, not all P2 positions or one whole-paragraph subject.',
                      'Functional slots belong to records; separate semantic positions do not assert unequal real-world referents.',
                      'This verifies the authored bookkeeping, not nominality, lexical values, actual reference, semantic order or translation.',
                  ], changes='Only this existing-dossier validator and its accounting report are written.')
    (HERE / 'F45R_ORDERED_SPECIFICATION_ACCOUNTING_20261015.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'summary': summary}, sort_keys=True))


if __name__ == '__main__':
    main()

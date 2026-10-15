#!/usr/bin/env python3
"""Independent bounded Q2 accounting; no builder import or corpus scan."""
import collections
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').is_file())
PROPOSAL = 'F45R_LATEST_MENTION_PROPOSAL_20261015.json'
DERIVATION = 'F45R_LATEST_MENTION_DERIVATION_20261015.json'
BUILDER = 'F45R_LATEST_MENTION_BUILD_20261015.py'


def read(name):
    return json.loads((HERE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proposal = read(PROPOSAL)
    rules = proposal['design']
    source, q1, actual = read(rules['source']), read(rules['q1_source']), read(DERIVATION)
    assert sha(HERE / rules['source']) == rules['source_sha256'] == actual['source_sha256']
    assert sha(HERE / rules['q1_source']) == rules['q1_source_sha256'] == actual['q1_sha256']
    assert sha(HERE / PROPOSAL) == actual['proposal_sha256']
    assert actual['primary_reader'] == 'IT2a'
    source_rows = source['readers']['IT2a']
    flat, paragraph_lengths, current = [], [], None
    for line in sorted(source_rows['lines'], key=lambda l: int(l['metadata']['source_row_index'])):
        m = line['metadata']
        assert m['kind'] == 'P' and m['page'] == 'f45r' and m['edition'] == 'IT2a'
        groups = [dict(zip(source_rows['group_columns'], g)) for g in line['groups']]
        assert len(groups) == int(m['source_group_count'])
        assert [int(g['source_group_index']) for g in groups] == list(range(1, len(groups) + 1))
        if m['paragraph_start'] == '1':
            assert current is None
            current = 0
        assert current is not None
        for g in groups:
            flat.append((g['source_group_id'], g['ivtff_group_raw'], m['locus']))
            current += 1
        if m['paragraph_end'] == '1':
            paragraph_lengths.append(current)
            current = None
    assert current is None and len({t[0] for t in flat}) == len(flat)
    assert [(t['id'], t['raw'], t['locus']) for t in q1['trace']] == flat
    assert actual['trace'] == q1['trace']
    source_index = {t[0]: i for i, t in enumerate(flat)}
    groups = [(eid, list(g)) for eid, g in itertools.groupby(q1['trace'], key=lambda t: t['event'])]
    assert len({eid for eid, _ in groups}) == len(groups)
    assert actual['event_order'] == [eid for eid, _ in groups]

    # Build positions solely from the fixed trace. Q1 identities are not used.
    records = {f'P{i + 1}': dict(record=f'P{i + 1}', entries=[], field_events=[], fields={})
               for i in range(len(paragraph_lengths))}
    ordinary = []
    for eid, group in groups:
        t = group[0]
        assert all(x['record'] == t['record'] for x in group)
        if t['kind'] != 'ordinary_entry':
            continue
        assert len(group) == 1 and t['descriptor'] == t['raw'] and t['roles'] == []
        record = records[t['record']]
        position = f'{t["record"]}.S{len(record["entries"]) + 1:03d}'
        assert t['ordinary_position'] == position
        entry = dict(position=position, referent=position + '.referent',
                     descriptor=t['descriptor'], source_id=t['id'])
        record['entries'].append(entry)
        ordinary.append(entry)

    graph = collections.defaultdict(set)
    kinds, assertions, equalities, anchor_rows = {}, [], [], []

    def node(name, kind):
        if name in kinds:
            assert kinds[name] == kind
        kinds[name] = kind
        graph[name]

    def edge(a, b, reason, ids):
        graph[a].add(b)
        graph[b].add(a)
        equalities.append(dict(left=a, right=b, reason=reason, source_ids=ids))

    for entry in ordinary:
        node(entry['referent'], 'entry')
        assertions.append(dict(entity=entry['referent'], descriptor=entry['descriptor'],
                               source_ids=[entry['source_id']], origin='ordinary_entry'))
    for eid, group in groups:
        t = group[0]
        if t['kind'] == 'ordinary_entry':
            continue
        assert t['kind'] in {'free_field', 'bound_field'}
        if t['kind'] == 'free_field':
            assert all(x['kind'] == 'free_marker' and x['descriptor'] is None for x in group[1:])
            assert [x['raw'] for x in group[1:]] == t['roles']
        else:
            assert len(group) == 1
        assert all(x['ordinary_position'] is None for x in group)
        argument = eid + '.argument'
        node(argument, 'argument')
        ids = [x['id'] for x in group]
        # Independent per-event prefix query, not the builder's mutable cache.
        candidates = [e for e in ordinary if e['descriptor'] == t['descriptor']
                      and source_index[e['source_id']] < source_index[t['id']]]
        event = dict(id=eid, kind=t['kind'], descriptor=t['descriptor'], roles=t['roles'],
                     source_ids=ids, raw=[x['raw'] for x in group], argument=argument,
                     earlier_ordinary_candidates=[e['position'] for e in candidates])
        assertions.append(dict(entity=argument, descriptor=t['descriptor'], source_ids=ids, origin='field_argument'))
        for role in t['roles']:
            slot = t['record'] + '.field.' + role
            node(slot, 'field')
            edge(slot, argument, 'one functional field per paragraph', ids)
        if candidates:
            anchor = max(candidates, key=lambda e: source_index[e['source_id']])
            event.update(anchor_position=anchor['position'], anchor_source_id=anchor['source_id'])
            edge(argument, anchor['referent'], 'latest earlier ordinary exact mention', ids)
            anchor_rows.append(dict(event=eid, descriptor=t['descriptor'], source_ids=ids,
                                    anchor_position=anchor['position'], anchor_source_id=anchor['source_id']))
        records[t['record']]['field_events'].append(event)

    # Graph components independently reconstruct field-value equalities.
    remaining, canonical, entities, obligations = set(kinds), {}, [], []
    while remaining:
        component = {min(remaining)}
        pending = list(component)
        while pending:
            for other in graph[pending.pop()]:
                if other not in component:
                    component.add(other)
                    pending.append(other)
        remaining -= component
        refs = sorted(n for n in component if kinds[n] == 'entry')
        fields = sorted(n for n in component if kinds[n] == 'field')
        cid = (refs or fields)[0]
        canonical.update({n: cid for n in component})
        if len(refs) > 1:
            obligations.append(refs)
        desc = [a for a in assertions if a['entity'] in component]
        entities.append(dict(id=cid, entry_referents=refs, field_values=fields,
                             descriptions=desc, descriptor_set=sorted({a['descriptor'] for a in desc})))
    changes = []
    q1_fields = {e['id']: e for r in q1['records'] for e in r['field_events']}
    for record in records.values():
        for entry in record['entries']:
            entry['resolved_referent'] = canonical[entry['referent']]
        for event in record['field_events']:
            value = canonical[event['argument']]
            event['resolved_referent'] = value
            for role in event['roles']:
                slot = record['fields'].setdefault(role, dict(value=canonical[record['record'] + '.field.' + role], descriptions=[], events=[]))
                assert slot['value'] == value
                slot['descriptions'].append(event['descriptor'])
                slot['events'].append(event['id'])
            old = q1_fields[event['id']]
            if old.get('anchor_position') != event.get('anchor_position'):
                changes.append(dict(event=event['id'], source_ids=event['source_ids'],
                                    q1=old.get('anchor_position'), q2=event.get('anchor_position')))
    assert list(records.values()) == actual['records']
    assert equalities == actual['equalities']

    def comparable(items):
        return sorted([dict(e, descriptions=sorted(e['descriptions'], key=lambda a: json.dumps(a, sort_keys=True)))
                       for e in items], key=lambda e: e['id'])

    assert comparable(entities) == comparable(actual['entities'])
    summary = dict(raw_groups=len(flat), ordered_entries=[len(r['entries']) for r in records.values()],
                   ordinary_positions=len(ordinary), field_mentions=sum(len(r['field_events']) for r in records.values()),
                   functional_fields=sum(len(r['fields']) for r in records.values()),
                   explicit_reprises=len(anchor_rows), changed_anchor_events=changes,
                   competing_anchor_identities=obligations)
    assert summary == actual['summary']
    assert changes == [dict(event='P3.event26', source_ids=['IT2a|f45r.11|G005'],
                            q1='P2.S011', q2='P3.S013')]
    by_entity = {e['id']: e for e in entities}
    assert set(by_entity['P2.S011.referent']['descriptor_set']) == {'dal', 'kol', 'dor'}
    assert set(by_entity['P3.S013.referent']['descriptor_set']) == {'dal', 'otydal'}
    dain = next(e for e in records['P3']['field_events'] if e['id'] == 'P3.event03')
    assert dain['descriptor'] == 'dain' and dain['roles'] == ['cthey']
    assert dain['earlier_ordinary_candidates'] == [] and 'anchor_position' not in dain
    assert dain['resolved_referent'] == 'P3.field.cthey'
    assert next(e for e in records['P3']['entries'] if e['descriptor'] == 'dain')['position'] == 'P3.S003'
    assert not any('.subject' in n for n in kinds)
    paths = [HERE / n for n in [PROPOSAL, BUILDER, DERIVATION, rules['q1_source'], rules['source']]]
    report = dict(status='PASS_INDEPENDENT_Q2_ACCOUNTING_NOT_MEANING',
                  method='Exact source sequence and own paragraph flags; frozen Q1 event grouping only; independent strict-earlier occurrence queries per field; graph-component equality reconstruction. No builder import or execution.',
                  input_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths},
                  validator_sha256=sha(Path(__file__)), derived_summary=summary,
                  source_paragraph_groups=paragraph_lengths, anchor_occurrences=anchor_rows,
                  dal_referent_constraints={k: by_entity[k]['descriptor_set'] for k in ['P2.S011.referent', 'P3.S013.referent']},
                  earlier_dain_field=dict(event=dain['id'], source_ids=dain['source_ids'],
                                          prior_candidates=dain['earlier_ordinary_candidates'], resolved_referent=dain['resolved_referent'],
                                          later_dain_position='P3.S003', later_dain_used_as_anchor=False),
                  limits=[
                      'Every86rawgroup preserved exactly once/order; all15field events independently reconstructed. Four actual source anchors; only finalDALDAIIN changes fromQ1.',
                      'Only earlier ordinary exact occurrences are candidates. Field mentions, prior resolutions, inferred properties and future ordinary occurrences cannot refresh the lookup.',
                      'Functional fields can resolve earlier open variables; this is not retrospective source-anchor selection. DAINCTHEY remains unanchored despite later ordinaryDAIN.',
                      'Old DAL carriesKOL/DOR; new DAL carriesOTYDAL. Neither these two source positions nor different canonical node names assert unequal real objects.',
                      'Q1 grouping/positions are reused, but noQ1referent equalities inherited. Record fields remain distinct from described objects.',
                      'Bookkeeping of an exposed authored alternative only, not confirmation, word meaning, nominality, source-language fit or historical superiority.',
                  ], changes='Only this validator and its compact accounting report are written; source/proposal/builders/derivations unchanged.')
    (HERE / 'F45R_LATEST_MENTION_ACCOUNTING_20261015.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'summary': summary}, sort_keys=True))


if __name__ == '__main__':
    main()

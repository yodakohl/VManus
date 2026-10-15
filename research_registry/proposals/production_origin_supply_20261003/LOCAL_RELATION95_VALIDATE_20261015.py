#!/usr/bin/env python3
"""Bounded audit of two already-authored passages with open identities."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').is_file())


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan_path = HERE / 'LOCAL_RELATION95_PLAN_20261015.json'
    result_path = HERE / 'LOCAL_RELATION95_READING_20261015.json'
    plan, actual = read(plan_path), read(result_path)
    assert actual['plan_sha256'] == sha(plan_path)
    documents, anchors, extra_groups, input_paths = [], [], [], []
    for pin in plan['scope']['inputs']:
        path = HERE / pin['file']
        input_paths.append(path)
        assert sha(path) == pin['sha256']
        data = read(path)
        trace = data['trace']
        page = trace[0]['id'].split('|')[1].split('.')[0]
        assert all(t['id'].split('|')[1].split('.')[0] == page for t in trace)
        assert len({t['id'] for t in trace}) == len(trace)
        source_order = {t['id']: i for i, t in enumerate(trace)}
        if 'records' in data:
            old_records = data['records']
        else:
            old_records = [dict(record='P1', entries=data['entries'], field_events=data['field_events'], fields=data['fields'])]
        original_entries = {e['source_id']: e for r in old_records for e in r['entries']}
        original_events = {e['id']: e for r in old_records for e in r['field_events']}
        original_records = {r['record']: r for r in old_records}
        records = {r['record']: dict(context=page + '/' + r['record'], ordered_entries=[], constructions=[]) for r in old_records}
        positions = {}
        # Reconstruct ordinary positions from unchanged token order, not from
        # their former resolved identity/value fields.
        for t in trace:
            if t['kind'] != 'ordinary_entry':
                continue
            rid = t.get('record', 'P1')
            rr = records[rid]
            position = f'{rid}.S{len(rr["ordered_entries"]) + 1:03d}'
            old = original_entries[t['id']]
            assert old['position'] == position and old['descriptor'] == t['descriptor'] == t['raw']
            entry = dict(position=position, source_id=t['id'], descriptor=t['raw'], referent='ref:' + t['id'])
            rr['ordered_entries'].append(entry)
            positions[t['id']] = entry
        assert set(positions) == set(original_entries)
        seen_events = set()
        for event_id, grouped in itertools.groupby(trace, key=lambda t: t['event']):
            group = list(grouped)
            assert event_id not in seen_events
            seen_events.add(event_id)
            first = group[0]
            if first['kind'] == 'ordinary_entry':
                assert len(group) == 1
                continue
            rid = first.get('record', 'P1')
            record, old = records[rid], original_events[event_id]
            ids = [t['id'] for t in group]
            assert ids == old['source_ids']
            assert [t['raw'] for t in group] == old['raw']
            assert first['descriptor'] == old['descriptor'] and first['roles'] == old['roles']
            assert all(t['roles'] == old['roles'] for t in group)
            if first['kind'] == 'free_field':
                assert [t['raw'] for t in group[1:]] == old['roles']
                assert all(t['kind'] == 'free_marker' and t['descriptor'] is None for t in group[1:])
            else:
                assert first['kind'] == 'bound_field' and len(group) == 1
            # Verify inherited Q2 anchor choice against ordinary source
            # occurrences, never against former field/inferred descriptions.
            earlier = [e for e in positions.values() if e['descriptor'] == old['descriptor']
                       and source_order[e['source_id']] < source_order[ids[0]]]
            anchor = (max(earlier, key=lambda e: source_order[e['source_id']])['source_id']
                      if earlier and not old.get('unresolved_local_seams') else None)
            assert anchor == old.get('anchor_source_id')
            argument = 'ref:' + anchor if anchor else 'arg:' + ids[0]
            context = record['context']
            construction = dict(id=context + '/' + event_id, source_ids=ids, raw=old['raw'],
                                descriptor=old['descriptor'], roles=old['roles'], argument=argument,
                                anchor_source_id=anchor,
                                relations=[dict(relation=s, context=context, argument=argument) for s in old['roles']])
            record['constructions'].append(construction)
            if anchor:
                anchors.append(dict(construction=construction['id'], source_ids=ids, anchor_source_id=anchor))
            for role in old['roles']:
                prior_value = old.get('resolved_referent')
                if prior_value is None:
                    prior_value = old['field_values'][role]
                assert prior_value == original_records[rid]['fields'][role]['value']
        assert sum(len(r['constructions']) for r in records.values()) == len(original_events)
        for record in records.values():
            role_order = list(dict.fromkeys(s for c in record['constructions'] for s in c['roles']))
            for role in role_order:
                group = [c for c in record['constructions'] if role in c['roles']]
                arguments = list(dict.fromkeys(c['argument'] for c in group))
                if len(arguments) < 2:
                    continue
                extra_groups.append(dict(context=record['context'], role=role,
                                         constructions=[c['id'] for c in group], arguments=arguments,
                                         descriptors=[c['descriptor'] for c in group],
                                         q2_adds=[dict(left=arguments[0], right=a) for a in arguments[1:]],
                                         current_status='identity_open_not_asserted_unequal'))
        documents.append(dict(page=page, source=pin, records=list(records.values()), trace=trace))
    assert documents == actual['documents']
    assert anchors == actual['explicit_anchor_sites']
    assert extra_groups == actual['q2_extra_identity_groups']
    trace = [t for d in documents for t in d['trace']]
    assert len(trace) == len({t['id'] for t in trace})
    constructions = [c for d in documents for r in d['records'] for c in r['constructions']]
    summary = dict(raw_groups=len(trace), paragraphs=sum(len(d['records']) for d in documents),
                   ordinary_positions=sum(len(r['ordered_entries']) for d in documents for r in d['records']),
                   local_constructions=len(constructions), relation_mentions=sum(len(c['roles']) for c in constructions),
                   explicit_anchor_sites=len(anchors), distinct_source_anchors=len({a['anchor_source_id'] for a in anchors}),
                   unanchored_argument_variables=sum(c['anchor_source_id'] is None for c in constructions),
                   q2_identity_groups=len(extra_groups), q2_added_equality_links=sum(len(g['q2_adds']) for g in extra_groups),
                   claimed_inequalities=0, assigned_word_meanings=0)
    assert summary == actual['summary']
    by_start = {c['source_ids'][0]: c for c in constructions}
    old_dal = 'ref:IT2a|f45r.6|G007'
    young_dal = 'ref:IT2a|f45r.10|G009'
    assert by_start['IT2a|f45r.10|G006']['argument'] == old_dal
    assert by_start['IT2a|f45r.10|G007']['argument'] == old_dal
    assert by_start['IT2a|f45r.11|G005']['argument'] == young_dal
    open_examples = ['IT2a|f45r.9|G008', 'IT2a|f45r.9|G001', 'IT2a|f45r.8|G007',
                     'IT2a|f89r1.8|G006', 'IT2a|f89r1.9|G002', 'IT2a|f89r1.9|G004', 'IT2a|f89r1.10|G009']
    for sid in open_examples:
        c = by_start[sid]
        assert c['anchor_source_id'] is None and c['argument'] == 'arg:' + sid
    assert all(set(c) == {'id', 'source_ids', 'raw', 'descriptor', 'roles', 'argument', 'anchor_source_id', 'relations'}
               for c in constructions)
    paths = [plan_path, result_path, HERE / 'LOCAL_RELATION95_BUILD_20261015.py'] + input_paths
    report = dict(status='PASS_LOCAL_RELATION95_ACCOUNTING_NO_IDENTITY_SELECTION',
                  method='Independent construction from preserved traces/ordinary positions; exact strict-prefix Q2 anchor check; record-role argument partition comparison. No builder import, new corpus or semantic experiment.',
                  input_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths}, validator_sha256=sha(Path(__file__)),
                  derived_summary=summary, preserved_explicit_anchors=anchors,
                  q2_additional_identity_groups=extra_groups,
                  inspected_open_arguments=[dict(source_id=s, descriptor=by_start[s]['descriptor'],
                                                  argument=by_start[s]['argument']) for s in open_examples],
                  limits=[
                      '132exact sourcegroups/order,98ordinarypositions and20constructions retained; all20 local argument assignments independently checked.',
                      'Five assumed Q2 anchors point to four source occurrences. DALDY/DALOR still share the old DAL source anchor; final DALDAIIN retains the young DAL anchor.',
                      'KOL/DOR no longer receive equality to oldDAL merely through a marker; OTYDAL no longer receives equality to youngDAL. The four free f89r1 descriptions retain separate open variables.',
                      'Q2 adds seven record-role equality groups represented by ten star links. This is a comparison of imposed constraints, not ten independent observations.',
                      'Distinct local argument identifiers assert neither real-object equality nor inequality. Explicit source anchors remain hypotheses, not established semantic identity.',
                      'Removing functionality weakens the model; increased compatibility is no empirical victory and does not refute Q2. Original IDEA95 identity discrimination remains unexecuted.',
                      'No lexical value, relation meaning, physical event, historical source or translated word is confirmed.',
                  ], changes='Only this validator and its accounting JSON written; all models and source artifacts unchanged.')
    (HERE / 'LOCAL_RELATION95_ACCOUNTING_20261015.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'summary': summary}, sort_keys=True))


if __name__ == '__main__':
    main()

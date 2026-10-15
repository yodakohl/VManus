#!/usr/bin/env python3
"""Bounded source/accounting audit of the existing f89r1 Q2 continuation."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').is_file())


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan_path = HERE / 'F89R1_Q2_CONTINUATION_PLAN_20261015.json'
    source_path = HERE / 'F89R1_Q2_SOURCE_20261015.json'
    result_path = HERE / 'F89R1_Q2_READING_20261015.json'
    plan, source, actual = read(plan_path), read(source_path), read(result_path)
    model_path = ROOT / plan['model']
    model = read(model_path)
    r1_path = HERE / 'F45R_RECORD_SYNTHESIS_RULES_20261015.json'
    r1 = read(r1_path)
    assert model['design']['version'] == 'Q2'
    assert sha(model_path) == plan['model_sha256'] == actual['model_sha256']
    assert sha(plan_path) == actual['plan_sha256'] and sha(source_path) == actual['source_sha256']
    assert plan['fixed_rules']['free_markers'] == r1['free_markers']
    assert plan['fixed_rules']['bound_forms'] == {
        word: [v['descriptor'], v['role']] for word, v in r1['bound_forms'].items()}
    loci = plan['scope']['loci']
    assert loci == [f'f89r1.{i}' for i in range(6, 11)]
    assert actual['scope'] == plan['scope'] and actual['primary_reader'] == 'IT2a'
    for pin in source['sources']:
        path = ROOT / pin['path']
        assert sha(path) == pin['sha256']
        old = read(path)
        ed = old['lines'][0]['metadata']['edition']
        expected = [l for l in old['lines'] if l['metadata']['locus'] in loci]
        assert source['readers'][ed]['group_columns'] == old['group_columns']
        assert source['readers'][ed]['lines'] == expected
        # Page-wide recency has no earlier ordinary P input in this page.
        # This checks metadata, not semantic status of preceding labels.
        first_row = min(int(l['metadata']['source_row_index']) for l in expected)
        assert not any(l['metadata']['page'] == 'f89r1' and l['metadata']['kind'] == 'P'
                       and int(l['metadata']['source_row_index']) < first_row for l in old['lines'])
    primary = source['readers']['IT2a']
    lines = sorted(primary['lines'], key=lambda l: int(l['metadata']['source_row_index']))
    assert [l['metadata']['locus'] for l in lines] == loci
    tokens = []
    for n, line in enumerate(lines):
        m = line['metadata']
        assert m['edition'] == 'IT2a' and m['kind'] == 'P' and m['page'] == 'f89r1'
        assert m['paragraph_start'] == ('1' if n == 0 else '0')
        assert m['paragraph_end'] == ('1' if n == len(lines) - 1 else '0')
        groups = [dict(zip(primary['group_columns'], g)) for g in line['groups']]
        assert len(groups) == int(m['source_group_count'])
        assert [int(g['source_group_index']) for g in groups] == list(range(1, len(groups) + 1))
        for g in groups:
            tokens.append(dict(id=g['source_group_id'], raw=g['ivtff_group_raw'], locus=m['locus'],
                               left=g['left_separator'], right=g['right_separator'], index=len(tokens)))
    assert len(tokens) == len({t['id'] for t in tokens})
    markers, bound = set(plan['fixed_rules']['free_markers']), plan['fixed_rules']['bound_forms']
    # Reverse grouping independently collects marker runs with their host.
    pieces, waiting = [], []
    for t in reversed(tokens):
        if t['raw'] in markers:
            waiting.insert(0, t)
        elif t['raw'] in bound:
            assert not waiting
            descriptor, role = bound[t['raw']]
            pieces.append(('bound_field', descriptor, [role], [t]))
        elif waiting:
            pieces.append(('free_field', t['raw'], [m['raw'] for m in waiting], [t] + waiting))
            waiting = []
        else:
            pieces.append(('ordinary_entry', t['raw'], [], [t]))
    assert not waiting
    pieces.reverse()
    entries, events, trace = [], [], []
    for number, (kind, descriptor, roles, used) in enumerate(pieces, 1):
        eid = f'E{number:03d}'
        first = used[0]
        if not roles:
            entries.append(dict(position=f'P1.S{len(entries) + 1:03d}', descriptor=descriptor,
                                source_id=first['id'], source_index=first['index'],
                                referent=first['id'] + '.referent'))
        else:
            seams = [dict(left=a['id'], right=b['id'], left_flag=a['right'], right_flag=b['left'])
                     for a, b in zip(used, used[1:]) if a['locus'] == b['locus']
                     and (a['right'] != 'DEFINITE_SPACE' or b['left'] != 'DEFINITE_SPACE')]
            events.append(dict(id=eid, kind=kind, descriptor=descriptor, roles=roles,
                               source_ids=[t['id'] for t in used], raw=[t['raw'] for t in used],
                               unresolved_local_seams=seams, source_index=first['index']))
        for j, token in enumerate(used):
            trace.append(dict(token, event=eid, kind='free_marker' if kind == 'free_field' and j else kind,
                              descriptor=None if kind == 'free_field' and j else descriptor, roles=roles))
    assert entries == actual['entries'] and trace == actual['trace']
    assert [t['id'] for t in trace] == [t['id'] for t in tokens]
    # Each anchor is fixed by the literal prefix at its own occurrence.
    for event in events:
        candidates = [e for e in entries if e['descriptor'] == event['descriptor']
                      and e['source_index'] < event['source_index']]
        event['earlier_ordinary_candidates'] = [e['source_id'] for e in candidates]
        if candidates and not event['unresolved_local_seams']:
            latest = max(candidates, key=lambda e: e['source_index'])
            event.update(anchor_source_id=latest['source_id'], anchor_position=latest['position'])
    fields = {}
    for role in sorted({r for e in events for r in e['roles']}):
        matching = [e for e in events if role in e['roles']]
        anchors = list(dict.fromkeys(e['anchor_source_id'] for e in matching if 'anchor_source_id' in e))
        fields[role] = dict(descriptions=[e['descriptor'] for e in matching],
                            events=[e['id'] for e in matching], anchors=anchors,
                            identity_obligation=anchors if len(anchors) > 1 else [],
                            value=anchors[0] + '.referent' if anchors else 'P1.field.' + role,
                            descriptor_set=sorted({e['descriptor'] for e in matching}))
    drawings = [dict(left=a['id'], right=b['id'], right_index=b['index'])
                for a, b in zip(tokens, tokens[1:]) if a['locus'] == b['locus']
                and 'DRAWING_INTERRUPTION' in {a['right'], b['left']}]
    indices = {t['id']: t['index'] for t in tokens}
    for event in events:
        event['field_values'] = {r: fields[r]['value'] for r in event['roles']}
        spans = [sorted((indices[a], event['source_index'])) for r in event['roles'] for a in fields[r]['anchors']]
        event['drawings_between_inherited_anchor_and_event'] = [gap for gap in drawings
            if any(low < gap['right_index'] <= high for low, high in spans)]
    assert events == actual['field_events'] and fields == actual['fields']
    assert drawings == actual['drawing_interruptions']
    f45_path = HERE / 'F45R_LATEST_MENTION_DERIVATION_20261015.json'
    f45 = read(f45_path)
    assert f45['proposal_sha256'] == plan['model_sha256']
    old_types, current_types = {t['raw'] for t in f45['trace']}, {t['raw'] for t in tokens}
    reuse = dict(exact_shared_types=sorted(old_types & current_types), shared_type_count=len(old_types & current_types),
                 shared_occurrences=sum(t['raw'] in old_types for t in tokens),
                 new_whole_type_count=len(current_types - old_types),
                 new_whole_occurrences=sum(t['raw'] not in old_types for t in tokens), meanings_transferred=0)
    assert reuse == actual['reuse_from_f45r']
    summary = dict(raw_groups=len(tokens), ordinary_positions=len(entries), field_descriptions=len(events),
                   free_marker_groups=sum(t['kind'] == 'free_marker' for t in trace), functional_fields=len(fields),
                   explicit_reference_hits=sum('anchor_source_id' in e for e in events),
                   local_unresolved_bindings=sum(bool(e['unresolved_local_seams']) for e in events))
    assert summary == actual['summary']
    assert fields['daiin']['anchors'] == ['IT2a|f89r1.7|G004']
    assert fields['daiin']['descriptor_set'] == ['ckhhy', 'dal', 'oiiin', 'qokechy', 'qokeey']
    later_dal = [e for e in entries if e['descriptor'] == 'dal'
                 and e['source_index'] > indices['IT2a|f89r1.7|G007']]
    assert [e['source_id'] for e in later_dal] == ['IT2a|f89r1.7|G009', 'IT2a|f89r1.10|G007']
    assert len(drawings) == 3 and all(not e['unresolved_local_seams'] for e in events)
    assert not any((gap['left'] in e['source_ids'] and gap['right'] in e['source_ids'])
                   for gap in drawings for e in events)
    paths = [plan_path, source_path, result_path, model_path, r1_path, f45_path,
             HERE / 'F89R1_Q2_READTHROUGH_20261015.py']
    report = dict(status='PASS_BOUNDED_SOURCE_AND_Q2_ACCOUNTING_NOT_CONFIRMATION',
                  method='Exact915projection and ownITparagraph flags; reverse host/marker grouping; independent strict-prefix reference lookup; one-field aggregation and drawing-boundary accounting. No readthrough import or execution.',
                  input_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths}, validator_sha256=sha(Path(__file__)),
                  derived_summary=summary, reuse_from_f45r=reuse, functional_field=fields,
                  explicit_anchor=[dict(source_ids=e['source_ids'], anchor=e['anchor_source_id'], position=e['anchor_position'])
                                   for e in events if 'anchor_source_id' in e],
                  later_dal_does_not_reanchor=[e['source_id'] for e in later_dal],
                  drawing_interruptions=drawings,
                  limits=[
                      'All46ITgroups retained exactly once/order;37ordinarypositions and5DAIINfields. Only DALDAIIN has an actual reference-search hit.',
                      'QOKECHY/OIIIN/QOKEEY/CKHHY share its referent through the imposed paragraph-field identity, not four further retrieved antecedents.',
                      'The three drawing interruptions are outside the four free host-marker pairs. Scope of one field across these drawings remains a conditional semantic-ownership assumption.',
                      'The second known DALDAIIN context was historically exposed. No held prediction, selected meaning, physical identity or independent confirmation follows.',
                      'Seven reused raw types cover14groups;31newwholetypes cover32groups. None acquires translated content by this accounting.',
                      'Other-reader raw rows are preserved; their flags and spellings are not normalized or borrowed to establish IT semantics.',
                  ], changes='Only this validator and its accounting JSON are written; all inputs and readthrough code unchanged.')
    (HERE / 'F89R1_Q2_ACCOUNTING_20261015.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': report['status'], 'summary': summary, 'reuse': reuse}, sort_keys=True))


if __name__ == '__main__':
    main()

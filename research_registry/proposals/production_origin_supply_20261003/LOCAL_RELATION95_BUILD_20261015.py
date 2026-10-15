#!/usr/bin/env python3
"""Expose local arguments without inheriting Q2's functional-field equalities."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    plan_path = HERE/'LOCAL_RELATION95_PLAN_20261015.json'
    plan = json.loads(plan_path.read_text())
    result = dict(status='COMPLETE_EXPLORATORY_READING_WITH_OPEN_IDENTITIES',
                  plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),
                  documents=[], explicit_anchor_sites=[], q2_extra_identity_groups=[])
    for source in plan['scope']['inputs']:
        path = HERE/source['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
        data = json.loads(path.read_text())
        page = data['trace'][0]['id'].split('|')[1].split('.')[0]
        source_records = data.get('records', [dict(record='P1', entries=data.get('entries'),
                                                  field_events=data.get('field_events'))])
        document = dict(page=page, source=source, records=[], trace=data['trace'])
        by_source = {}
        for old_record in source_records:
            for e in old_record['entries']:
                by_source[e['source_id']] = e
        for old_record in source_records:
            context = page+'/'+old_record['record']
            record = dict(context=context, ordered_entries=[], constructions=[])
            for entry in old_record['entries']:
                record['ordered_entries'].append(dict(position=entry['position'],
                    source_id=entry['source_id'], descriptor=entry['descriptor'],
                    referent='ref:'+entry['source_id']))
            grouped = defaultdict(list)
            for old in old_record['field_events']:
                anchor = old.get('anchor_source_id')
                if anchor:
                    assert anchor in by_source
                    assert by_source[anchor]['descriptor'] == old['descriptor']
                argument = ('ref:'+anchor) if anchor else ('arg:'+old['source_ids'][0])
                construction = dict(id=context+'/'+old['id'], source_ids=old['source_ids'],
                    raw=old['raw'], descriptor=old['descriptor'], roles=old['roles'],
                    argument=argument, anchor_source_id=anchor,
                    relations=[dict(relation=s,context=context,argument=argument) for s in old['roles']])
                record['constructions'].append(construction)
                if anchor:
                    result['explicit_anchor_sites'].append(dict(construction=construction['id'],
                        source_ids=old['source_ids'], anchor_source_id=anchor))
                for role in set(old['roles']):
                    grouped[role].append(construction)
            for role, constructions in grouped.items():
                arguments = list(dict.fromkeys(c['argument'] for c in constructions))
                if len(arguments)>1:
                    result['q2_extra_identity_groups'].append(dict(context=context, role=role,
                        constructions=[c['id'] for c in constructions], arguments=arguments,
                        descriptors=[c['descriptor'] for c in constructions],
                        q2_adds=[dict(left=arguments[0],right=a) for a in arguments[1:]],
                        current_status='identity_open_not_asserted_unequal'))
            document['records'].append(record)
        result['documents'].append(document)
    traces = [t for d in result['documents'] for t in d['trace']]
    constructions = [c for d in result['documents'] for r in d['records'] for c in r['constructions']]
    assert len(traces)==len({t['id'] for t in traces})==132
    result['summary'] = dict(raw_groups=132, paragraphs=sum(len(d['records']) for d in result['documents']),
        ordinary_positions=sum(len(r['ordered_entries']) for d in result['documents'] for r in d['records']),
        local_constructions=len(constructions), relation_mentions=sum(len(c['roles']) for c in constructions),
        explicit_anchor_sites=len(result['explicit_anchor_sites']),
        distinct_source_anchors=len({s['anchor_source_id'] for s in result['explicit_anchor_sites']}),
        unanchored_argument_variables=sum(c['anchor_source_id'] is None for c in constructions),
        q2_identity_groups=len(result['q2_extra_identity_groups']),
        q2_added_equality_links=sum(len(g['q2_adds']) for g in result['q2_extra_identity_groups']),
        claimed_inequalities=0, assigned_word_meanings=0)
    result['limits'] = ['Explicit source anchors are still Q2 reference hypotheses, not observed semantic edges.',
        'Removing functionality weakens the construction; greater compatibility does not favor it empirically.',
        'Open variables may denote the same actual referent. Original IDEA95 identity discriminator remains unexecuted.',
        'Source/lexing, ordered-content, paragraph-context, finite-compound and recency assumptions remain.',
        'No new page, source, reserve or lexical value used.']
    (HERE/'LOCAL_RELATION95_READING_20261015.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['summary'],indent=2))


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""One Q2 sweep of the existing f45r grouping; no new corpus or lexical values."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    path = HERE / name
    return json.loads(path.read_text()), hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proposal, proposal_hash = load('F45R_LATEST_MENTION_PROPOSAL_20261015.json')
    rules = proposal['design']
    q1, q1_hash = load(rules['q1_source'])
    source, source_hash = load(rules['source'])
    assert q1_hash == rules['q1_source_sha256']
    assert source_hash == rules['source_sha256'] == q1['source_sha256']
    primary = source['readers']['IT2a']
    columns = {v: i for i, v in enumerate(primary['group_columns'])}
    raw = [(g[columns['source_group_id']], g[columns['ivtff_group_raw']])
           for row in sorted(primary['lines'], key=lambda r: int(r['metadata']['source_row_index']))
           for g in row['groups']]
    assert raw == [(t['id'], t['raw']) for t in q1['trace']]
    assert len(raw) == len(set(i for i, _ in raw)) == 86

    old_entries = {e['source_id']: e for r in q1['records'] for e in r['entries']}
    old_fields = {e['id']: e for r in q1['records'] for e in r['field_events']}
    records = {r['record']: dict(record=r['record'], entries=[], field_events=[], fields={})
               for r in q1['records']}
    parent, kinds = {}, {}
    mentions = defaultdict(list)
    assertions, equalities, event_order, seen = [], [], [], set()

    def node(n, kind):
        if n not in parent:
            parent[n] = n
            kinds[n] = kind
        return n

    def find(n):
        while parent[n] != n:
            n = parent[n]
        return n

    def join(a, b, reason, source_ids):
        parent[find(b)] = find(a)
        equalities.append(dict(left=a, right=b, reason=reason, source_ids=source_ids))

    for token in q1['trace']:
        event_id = token['event']
        if event_id in seen:
            continue
        seen.add(event_id)
        event_order.append(event_id)
        record = records[token['record']]
        if token['kind'] == 'ordinary_entry':
            old = old_entries[token['id']]
            entry = {k: old[k] for k in ['position', 'referent', 'descriptor', 'source_id']}
            node(entry['referent'], 'entry')
            record['entries'].append(entry)
            mentions[entry['descriptor']].append(entry)
            assertions.append(dict(entity=entry['referent'], descriptor=entry['descriptor'],
                                   source_ids=[entry['source_id']], origin='ordinary_entry'))
            continue
        old = old_fields[event_id]
        event = {k: old[k] for k in ['id', 'kind', 'descriptor', 'roles', 'source_ids', 'raw']}
        arg = node(event_id + '.argument', 'argument')
        event['argument'] = arg
        candidates = mentions[event['descriptor']]
        event['earlier_ordinary_candidates'] = [e['position'] for e in candidates]
        assertions.append(dict(entity=arg, descriptor=event['descriptor'],
                               source_ids=event['source_ids'], origin='field_argument'))
        for role in event['roles']:
            slot = node(record['record'] + '.field.' + role, 'field')
            join(slot, arg, 'one functional field per paragraph', event['source_ids'])
        if candidates:
            anchor = candidates[-1]
            event['anchor_position'] = anchor['position']
            event['anchor_source_id'] = anchor['source_id']
            join(arg, anchor['referent'], 'latest earlier ordinary exact mention', event['source_ids'])
        record['field_events'].append(event)
        # Neither a field mention nor a later inference updates mentions.

    components = defaultdict(list)
    for n in parent:
        components[find(n)].append(n)
    entities, canonical, obligations = [], {}, []
    for nodes in components.values():
        entries = sorted(n for n in nodes if kinds[n] == 'entry')
        fields = sorted(n for n in nodes if kinds[n] == 'field')
        name = entries[0] if entries else fields[0]
        canonical.update({n: name for n in nodes})
        if len(entries) > 1:
            obligations.append(entries)
        desc = [a for a in assertions if a['entity'] in nodes]
        entities.append(dict(id=name, entry_referents=entries, field_values=fields,
                             descriptions=desc, descriptor_set=sorted({a['descriptor'] for a in desc})))
    changes = []
    for record in records.values():
        for entry in record['entries']:
            entry['resolved_referent'] = canonical[entry['referent']]
        for event in record['field_events']:
            event['resolved_referent'] = canonical[event['argument']]
            for role in event['roles']:
                field = record['fields'].setdefault(role, dict(value=event['resolved_referent'], descriptions=[], events=[]))
                assert field['value'] == event['resolved_referent']
                field['descriptions'].append(event['descriptor'])
                field['events'].append(event['id'])
            old = old_fields[event['id']]
            if old.get('anchor_position') != event.get('anchor_position'):
                changes.append(dict(event=event['id'], source_ids=event['source_ids'],
                                    q1=old.get('anchor_position'), q2=event.get('anchor_position')))
    summary = dict(raw_groups=86, ordered_entries=[len(r['entries']) for r in records.values()],
                   ordinary_positions=sum(len(r['entries']) for r in records.values()),
                   field_mentions=sum(len(r['field_events']) for r in records.values()),
                   functional_fields=sum(len(r['fields']) for r in records.values()),
                   explicit_reprises=sum('anchor_position' in e for r in records.values() for e in r['field_events']),
                   changed_anchor_events=changes, competing_anchor_identities=obligations)
    result = dict(status='Q2_AUTHORED_REFERENCE_CHANGE_MEANINGS_UNASSIGNED', primary_reader='IT2a',
                  proposal_sha256=proposal_hash, q1_sha256=q1_hash, source_sha256=source_hash,
                  summary=summary, event_order=event_order, records=list(records.values()),
                  entities=sorted(entities, key=lambda e:e['id']), equalities=equalities, trace=q1['trace'],
                  limits=['Source anchor changes do not establish different physical referents.',
                          'Hypothesis selected after viewing the DAL sequence; no independent prediction.',
                          'Exact final position and field-order changes within one mention interval remain unexplained.',
                          'No ordinary meaning, quantity, action or source language assigned.'])
    (HERE/'F45R_LATEST_MENTION_DERIVATION_20261015.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

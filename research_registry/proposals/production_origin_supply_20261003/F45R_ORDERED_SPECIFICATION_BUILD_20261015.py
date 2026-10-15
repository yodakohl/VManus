#!/usr/bin/env python3
"""Derive Q1 from frozen R1 token grouping, without inheriting its identities."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    path = HERE / name
    return json.loads(path.read_text()), hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proposal, proposal_sha = read('F45R_ORDERED_SPECIFICATION_PROPOSAL_20261015.json')
    design = proposal['design']
    r1, r1_sha = read(design['r1_derivation'])
    source, source_sha = read(design['source'])
    assert r1_sha == design['r1_derivation_sha256']
    assert source_sha == design['source_sha256'] == r1['source_sha256']
    primary = source['readers']['IT2a']
    columns = {v: i for i, v in enumerate(primary['group_columns'])}
    rows = sorted(primary['lines'], key=lambda x: int(x['metadata']['source_row_index']))
    raw = [(g[columns['source_group_id']], g[columns['ivtff_group_raw']])
           for row in rows for g in row['groups']]
    assert raw == [(t['id'], t['raw']) for t in r1['trace']]
    assert len(raw) == len(set(i for i, _ in raw)) == 86

    parent, metadata = {}, {}
    assertions, equalities, records, previous, ambiguities = [], [], [], [], []

    def node(name, kind, **details):
        if name not in parent:
            parent[name] = name
            metadata[name] = dict(kind=kind, **details)
        return name

    def find(name):
        while parent[name] != name:
            name = parent[name]
        return name

    def union(a, b, reason, source_ids):
        parent[find(b)] = find(a)
        equalities.append(dict(left=a, right=b, reason=reason, source_ids=source_ids))

    for old in r1['records']:
        rid = old['record']
        record = dict(record=rid, entries=[], field_events=[], fields={})
        for item in old['ordinary']:
            position = f'{rid}.S{len(record["entries"])+1:03d}'
            ref = node(position + '.referent', 'entry_referent', position=position,
                       source_id=item['source_id'], record=rid)
            entry = dict(position=position, referent=ref, **item)
            record['entries'].append(entry)
            assertions.append(dict(entity=ref, descriptor=item['descriptor'],
                                   source_ids=[item['source_id']], origin='ordinary_entry'))
        for old_event in old['field_events']:
            event = {k: old_event[k] for k in ['id', 'kind', 'descriptor', 'roles', 'source_ids', 'raw']}
            arg = node(event['id'] + '.argument', 'field_argument', record=rid)
            event['argument'] = arg
            matches = [e for e in previous if e['descriptor'] == event['descriptor']]
            event['prior_candidates'] = [e['position'] for e in matches]
            assertions.append(dict(entity=arg, descriptor=event['descriptor'],
                                   source_ids=event['source_ids'], origin='field_argument'))
            for role in event['roles']:
                value = node(rid + '.field.' + role, 'field_value', record=rid, role=role)
                union(value, arg, 'one field value per role and paragraph', event['source_ids'])
            if len(matches) == 1:
                anchor = matches[0]
                event['anchor_position'] = anchor['position']
                event['anchor_source_id'] = anchor['source_id']
                union(arg, anchor['referent'], 'stipulated unique prior occurrence reprise', event['source_ids'])
            elif len(matches) > 1:
                ambiguities.append(dict(event=event['id'], candidates=event['prior_candidates']))
            record['field_events'].append(event)
        records.append(record)
        previous.extend(record['entries'])

    components = defaultdict(list)
    for n in parent:
        components[find(n)].append(n)
    entities, canonical, identity_obligations = [], {}, []
    for nodes in components.values():
        refs = sorted(n for n in nodes if metadata[n]['kind'] == 'entry_referent')
        fields = sorted(n for n in nodes if metadata[n]['kind'] == 'field_value')
        canonical_id = refs[0] if refs else fields[0]
        if len(refs) > 1:
            identity_obligations.append(refs)
        canonical.update({n: canonical_id for n in nodes})
        desc = [a for a in assertions if a['entity'] in nodes]
        entities.append(dict(id=canonical_id, entry_referents=refs, field_values=fields,
                             descriptions=desc, descriptor_set=sorted({a['descriptor'] for a in desc})))
    by_source = {}
    for record in records:
        for entry in record['entries']:
            entry['resolved_referent'] = canonical[entry['referent']]
            by_source[entry['source_id']] = entry['position']
        for event in record['field_events']:
            event['resolved_referent'] = canonical[event['argument']]
            for role in event['roles']:
                field = record['fields'].setdefault(role, dict(value=event['resolved_referent'],
                                                              descriptions=[], events=[]))
                assert field['value'] == event['resolved_referent']
                field['descriptions'].append(event['descriptor'])
                field['events'].append(event['id'])
    trace = [dict(t, kind=('ordinary_entry' if t['kind'] == 'subject_description' else t['kind']),
                  ordinary_position=by_source.get(t['id'])) for t in r1['trace']]
    assert sum(t['ordinary_position'] is not None for t in trace) == 61
    summary = dict(raw_groups=86, paragraph_groups=r1['summary']['paragraph_groups'],
                   ordered_entries=[len(r['entries']) for r in records], total_ordered_entries=61,
                   field_mentions=sum(len(r['field_events']) for r in records),
                   functional_fields=sum(len(r['fields']) for r in records),
                   explicit_reprises=sum('anchor_position' in e for r in records for e in r['field_events']),
                   unknown_description_types=len({a['descriptor'] for a in assertions}),
                   reference_ambiguities=ambiguities, competing_anchor_identities=identity_obligations,
                   group_roles=dict(Counter(t['kind'] for t in trace)))
    result = dict(status='CONSTRUCTED_ORDERED_SPECIFICATION_MEANINGS_UNASSIGNED', primary_reader='IT2a',
                  proposal_sha256=proposal_sha, source_sha256=source_sha, frozen_lexing_sha256=r1_sha,
                  summary=summary, records=records, entities=sorted(entities, key=lambda e:e['id']),
                  equalities=equalities, trace=trace,
                  limits=['Ordered semantic positions are hypothesized, not independently decoded.',
                          'Field assertion ordering and final DALDAIIN placement remain unexplained.',
                          'Different positions need not denote distinct physical entities.',
                          'This is not a calibrated empirical test or a translation.'])
    (HERE/'F45R_ORDERED_SPECIFICATION_DERIVATION_20261015.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

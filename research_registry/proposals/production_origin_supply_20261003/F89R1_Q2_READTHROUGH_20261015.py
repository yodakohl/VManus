#!/usr/bin/env python3
"""One complete exposed paragraph under the existing Q2 commitments."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'vmanus-work').is_file())


def read(name):
    p = HERE/name
    return json.loads(p.read_text()), hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    plan, plan_hash = read('F89R1_Q2_CONTINUATION_PLAN_20261015.json')
    assert hashlib.sha256((ROOT/plan['model']).read_bytes()).hexdigest() == plan['model_sha256']
    source, source_hash = read('F89R1_Q2_SOURCE_20261015.json')
    data = source['readers']['IT2a']
    c = {x:i for i,x in enumerate(data['group_columns'])}
    rows = sorted(data['lines'], key=lambda x:int(x['metadata']['source_row_index']))
    assert [r['metadata']['locus'] for r in rows] == plan['scope']['loci']
    assert rows[0]['metadata']['paragraph_start'] == '1'
    assert rows[-1]['metadata']['paragraph_end'] == '1'
    tokens = []
    for row in rows:
        assert row['metadata']['kind'] == 'P'
        for g in row['groups']:
            tokens.append(dict(id=g[c['source_group_id']], raw=g[c['ivtff_group_raw']],
                               locus=row['metadata']['locus'], left=g[c['left_separator']],
                               right=g[c['right_separator']], index=len(tokens)))
    assert len(tokens) == 46 and len({t['id'] for t in tokens}) == 46
    markers = set(plan['fixed_rules']['free_markers'])
    bound = plan['fixed_rules']['bound_forms']
    drawings = [dict(left=a['id'], right=b['id'], right_index=b['index'])
                for a,b in zip(tokens,tokens[1:])
                if a['locus']==b['locus'] and
                ('DRAWING_INTERRUPTION' in (a['right'], b['left']))]
    entries, events, trace, errors = [], [], [], []
    mentions = defaultdict(list)
    fields = {}
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t['raw'] in markers:
            errors.append(dict(code='orphan_marker',source_id=t['id']))
            break
        if t['raw'] in bound:
            descriptor, role = bound[t['raw']]
            roles, used, kind = [role], [t], 'bound_field'
        else:
            j = i+1
            while j<len(tokens) and tokens[j]['raw'] in markers:
                j += 1
            roles = [x['raw'] for x in tokens[i+1:j]]
            used, descriptor = tokens[i:j] if roles else [t], t['raw']
            kind = 'free_field' if roles else 'ordinary_entry'
        event_id = f'E{len(entries)+len(events)+1:03d}'
        if not roles:
            entry = dict(position=f'P1.S{len(entries)+1:03d}', descriptor=descriptor,
                         source_id=t['id'], source_index=t['index'], referent=f'{t["id"]}.referent')
            entries.append(entry)
            mentions[descriptor].append(entry)
        else:
            seams = [dict(left=a['id'],right=b['id'],left_flag=a['right'],right_flag=b['left'])
                     for a,b in zip(used,used[1:]) if a['locus']==b['locus'] and
                     (a['right']!='DEFINITE_SPACE' or b['left']!='DEFINITE_SPACE')]
            candidates = mentions[descriptor]
            event = dict(id=event_id, kind=kind, descriptor=descriptor, roles=roles,
                         source_ids=[x['id'] for x in used], raw=[x['raw'] for x in used],
                         earlier_ordinary_candidates=[x['source_id'] for x in candidates],
                         unresolved_local_seams=seams, source_index=t['index'])
            if candidates and not seams:
                event['anchor_source_id'] = candidates[-1]['source_id']
                event['anchor_position'] = candidates[-1]['position']
            for role in roles:
                f = fields.setdefault(role, dict(descriptions=[], events=[], anchors=[]))
                f['descriptions'].append(descriptor)
                f['events'].append(event_id)
                if event.get('anchor_source_id') not in f['anchors'] and event.get('anchor_source_id'):
                    f['anchors'].append(event['anchor_source_id'])
            events.append(event)
        for n,u in enumerate(used):
            trace.append(dict(u, event=event_id,
                              kind='free_marker' if kind=='free_field' and n else kind,
                              descriptor=None if kind=='free_field' and n else descriptor,
                              roles=roles))
        i += len(used)
    assert not errors, errors
    assert [t['id'] for t in trace] == [t['id'] for t in tokens]
    # Source choices stay fixed. Shared fields add constraints, not new searches.
    for role, f in fields.items():
        f['identity_obligation'] = f['anchors'] if len(f['anchors'])>1 else []
        f['value'] = f['anchors'][0]+'.referent' if f['anchors'] else 'P1.field.'+role
        f['descriptor_set'] = sorted(set(f['descriptions']))
    by_id = {t['id']:t for t in tokens}
    for event in events:
        event['field_values'] = {r:fields[r]['value'] for r in event['roles']}
        anchors = [a for r in event['roles'] for a in fields[r]['anchors']]
        event['drawings_between_inherited_anchor_and_event'] = [d for d in drawings
            if any(min(by_id[a]['index'],event['source_index']) < d['right_index']
                   <= max(by_id[a]['index'],event['source_index']) for a in anchors)]
    old,_ = read('F45R_LATEST_MENTION_DERIVATION_20261015.json')
    old_types = {t['raw'] for t in old['trace']}
    here_types = {t['raw'] for t in tokens}
    reuse = dict(exact_shared_types=sorted(old_types&here_types),
                 shared_type_count=len(old_types&here_types),
                 shared_occurrences=sum(t['raw'] in old_types for t in tokens),
                 new_whole_type_count=len(here_types-old_types),
                 new_whole_occurrences=sum(t['raw'] not in old_types for t in tokens),
                 meanings_transferred=0)
    result = dict(status='COMPLETE_LOCAL_ALIGNMENT_CONDITIONAL_SHARED_FIELD_SCOPE',
                  plan_sha256=plan_hash, model_sha256=plan['model_sha256'], source_sha256=source_hash,
                  primary_reader='IT2a', scope=plan['scope'], entries=entries, field_events=events,
                  fields=fields, trace=trace, drawing_interruptions=drawings, reuse_from_f45r=reuse,
                  summary=dict(raw_groups=len(tokens), ordinary_positions=len(entries),
                               field_descriptions=len(events), free_marker_groups=sum(t['kind']=='free_marker' for t in trace),
                               functional_fields=len(fields), explicit_reference_hits=sum('anchor_source_id' in e for e in events),
                               local_unresolved_bindings=sum(bool(e['unresolved_local_seams']) for e in events)),
                  limits=['Paragraph-wide field identity across drawing interruptions is an assumption, not a source-bound relation.',
                          'All46positions are structurally assigned;31newwhole types remain unassigned content.',
                          'The selected second DALDAIIN context was already inspected; this is not a held test.',
                          'Only one actual reference search succeeds; other descriptions share its value through the imposed field rule.'])
    (HERE/'F89R1_Q2_READING_20261015.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(summary=result['summary'], fields=fields, reuse=reuse),indent=2))


if __name__=='__main__':
    main()

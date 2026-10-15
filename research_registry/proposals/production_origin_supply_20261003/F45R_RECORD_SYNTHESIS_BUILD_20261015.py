#!/usr/bin/env python3
"""Replay one authored whole-page draft; no statistical or meaning test."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'vmanus-work').is_file())
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    rp = HERE/'F45R_RECORD_SYNTHESIS_RULES_20261015.json'
    rules = json.loads(rp.read_text())
    sp = ROOT/rules['source']
    assert sha(sp) == rules['source_sha256']
    source = json.loads(sp.read_text())
    reader = source['readers']['IT2a']
    c = {name:i for i,name in enumerate(reader['group_columns'])}
    lines = sorted(reader['lines'], key=lambda x:int(x['metadata']['source_row_index']))
    markers = set(rules['free_markers']); bound = rules['bound_forms']
    parent = {}; node_meta = {}; descriptions = []; equalities = []; trace = []

    def add(node, kind, **meta):
        if node not in parent:
            parent[node] = node
            node_meta[node] = dict(kind=kind, **meta)
        return node

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a, b, reason, source_ids):
        parent[find(b)] = find(a)
        equalities.append(dict(left=a, right=b, reason=reason, source_ids=source_ids))

    records = []; previous = []; expected_ids = []
    for para in source['primary_paragraphs']:
        start=int(para['first_locus'].split('.')[-1]); end=int(para['last_locus'].split('.')[-1])
        owned=[x for x in lines if start <= int(x['metadata']['locus'].split('.')[-1]) <= end]
        assert owned[0]['metadata']['paragraph_start']=='1'
        assert owned[-1]['metadata']['paragraph_end']=='1'
        tokens=[]
        for line in owned:
            assert line['metadata']['page']=='f45r' and line['metadata']['kind']=='P'
            for i,g in enumerate(line['groups']):
                if i: assert g[c['left_separator']]=='DEFINITE_SPACE' and line['groups'][i-1][c['right_separator']]=='DEFINITE_SPACE'
                tokens.append(dict(id=g[c['source_group_id']],raw=g[c['ivtff_group_raw']],locus=line['metadata']['locus']))
        assert len(tokens)==para['groups']
        expected_ids += [t['id'] for t in tokens]
        rid=para['label']; subject=add(rid+'.subject','subject',record=rid)
        record=dict(record=rid,subject=subject,first_locus=para['first_locus'],last_locus=para['last_locus'],group_count=len(tokens),ordinary=[],field_events=[],fields={},reference_ambiguities=[])
        i=0
        while i<len(tokens):
            t=tokens[i];raw=t['raw'];event_id=f'{rid}.event{len(record["ordinary"])+len(record["field_events"])+1:02d}'
            if raw in markers:
                raise ValueError('Unbound marker in this authored draft: '+t['id'])
            if raw in bound:
                descriptor=bound[raw]['descriptor'];roles=[bound[raw]['role']];used=[t];kind='bound_field'
            else:
                j=i+1
                while j<len(tokens) and tokens[j]['raw'] in markers:j+=1
                roles=[v['raw'] for v in tokens[i+1:j]]
                descriptor=raw;used=tokens[i:j] if roles else [t]
                kind='free_field' if roles else 'subject_description'
            if not roles:
                record['ordinary'].append(dict(descriptor=descriptor,source_id=t['id']))
                descriptions.append(dict(entity=subject,descriptor=descriptor,source_ids=[t['id']],origin='ordinary_subject'))
            else:
                arg=add(event_id+'.argument','argument_mention',record=rid)
                source_ids=[u['id'] for u in used]
                candidates=[p['record'] for p in previous if descriptor in p['ordinary_descriptor_set']]
                event=dict(id=event_id,kind=kind,descriptor=descriptor,roles=roles,argument=arg,source_ids=source_ids,raw=[u['raw'] for u in used],prior_candidates=candidates)
                record['field_events'].append(event)
                descriptions.append(dict(entity=arg,descriptor=descriptor,source_ids=source_ids,origin=kind))
                for role in roles:
                    slot=add(rid+'.field.'+role,'field_value',record=rid,role=role)
                    union(slot,arg,'same functional field / same marker-run argument',source_ids)
                if len(candidates)==1:
                    target=next(p['subject'] for p in previous if p['record']==candidates[0])
                    union(arg,target,'declared unique completed-paragraph reprise',source_ids)
                    event['anchor_record']=candidates[0]
                elif len(candidates)>1:
                    record['reference_ambiguities'].append(dict(event=event_id,candidates=candidates))
            for k,u in enumerate(used):
                trace.append(dict(**u,record=rid,event=event_id,kind=('free_marker' if kind=='free_field' and k else kind),descriptor=(None if kind=='free_field' and k else descriptor),roles=roles))
            i+=len(used)
        record['ordinary_descriptor_set']=sorted({x['descriptor'] for x in record['ordinary']})
        records.append(record);previous.append(record)

    components=defaultdict(list)
    for node in parent:components[find(node)].append(node)
    canonical={};entities=[];identity_obligations=[]
    for nodes in components.values():
        subjects=sorted(n for n in nodes if node_meta[n]['kind']=='subject')
        fields=sorted(n for n in nodes if node_meta[n]['kind']=='field_value')
        cid=subjects[0] if subjects else fields[0]
        if len(subjects)>1:identity_obligations.append(subjects)
        for n in nodes:canonical[n]=cid
        asserted=[x for x in descriptions if x['entity'] in nodes]
        entities.append(dict(id=cid,subject_nodes=subjects,field_nodes=fields,descriptions=asserted,descriptor_set=sorted({x['descriptor'] for x in asserted})))
    for record in records:
        for event in record['field_events']:
            event['resolved_entity']=canonical[event['argument']]
            for role in event['roles']:
                slot=record['fields'].setdefault(role,dict(value=canonical[record['record']+'.field.'+role],descriptions=[],events=[]))
                slot['descriptions'].append(event['descriptor']);slot['events'].append(event['id'])
    assert [x['id'] for x in trace]==expected_ids
    assert len(trace)==86 and len(set(expected_ids))==86
    summary=dict(raw_groups=86,paragraph_groups=[r['group_count'] for r in records],raw_types=len({x['raw'] for x in trace}),description_predicates=len({x['descriptor'] for x in descriptions}),free_marker_types=len(markers),finite_bound_forms=len(bound),ordinary_description_occurrences=sum(len(r['ordinary']) for r in records),field_description_occurrences=sum(len(r['field_events']) for r in records),field_values=sum(len(r['fields']) for r in records),explicit_reprise_events=sum('anchor_record' in e for r in records for e in r['field_events']),source_groups_by_role=dict(Counter(x['kind'] for x in trace)),reference_ambiguities=sum(len(r['reference_ambiguities']) for r in records),competing_anchor_identity_obligations=identity_obligations)
    result=dict(status='COMPLETE_AUTHORED_PRIMARY_STRUCTURE_MEANINGS_UNASSIGNED',rules_sha256=sha(rp),source_sha256=sha(sp),primary_reader='IT2a',summary=summary,records=records,entities=sorted(entities,key=lambda x:x['id']),equalities=equalities,trace=trace,limits=['All86 positions are conditionally organized, not translated.','Record fields and described referents have different types.','Different variable names do not assert distinct real objects.','Positive unknown predicates permit easy consistency; no likelihood or meaning confirmation.','Alternate readers are preserved in source packet but not normalized or claimed parsed.'])
    (HERE/'F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()

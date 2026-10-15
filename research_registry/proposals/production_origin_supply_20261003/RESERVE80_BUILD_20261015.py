"""Small authored Reserve/EnsureCommitted reading; no decoder or native execution."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reserve(state, resource):
    """A distinct exclusive commitment; missing state is unknown, not available."""
    if resource not in state:
        return 'UNKNOWN', None
    if state[resource] != 'AVAILABLE':
        return 'INVALID_ALREADY_COMMITTED', None
    return 'OK', dict(state, **{resource: 'COMMITTED'})


def ensure_committed(state, resource):
    if resource not in state:
        return 'UNKNOWN', None
    return 'OK', dict(state, **{resource: 'COMMITTED'})


def demo(operator, same):
    # These identities are supplied synthetic inputs, never native assignments.
    resources = ['x', 'x' if same else 'y']
    state = {r: 'AVAILABLE' for r in resources}
    steps = []
    for resource in resources:
        before = dict(state)
        status, after = operator(state, resource)
        steps.append(dict(resource=resource, before=before, status=status, after=after))
        if after is None:
            break
        state = after
    return dict(identity_input='SAME' if same else 'DIFFERENT', steps=steps,
                both_execute=len(steps) == 2 and all(s['status'] == 'OK' for s in steps))


def main():
    plan_path = HERE / 'RESERVE80_PLAN_20261015.json'
    plan = json.loads(plan_path.read_text())
    source_path = ROOT / plan['source']['path']
    assert sha(source_path) == plan['source']['sha256']
    source = json.loads(source_path.read_text())
    paths = [plan_path, source_path]
    packets, rows = {}, {}
    for page, filename in [('f45r', 'F45R_WHOLE_PAGE_SOURCE_20261015.json'),
                           ('f89r1', 'F89R1_Q2_SOURCE_20261015.json')]:
        path = HERE / filename
        paths.append(path)
        packets[page] = json.loads(path.read_text())
        reader = packets[page]['readers']['IT2a']
        for line in reader['lines']:
            for group in line['groups']:
                rows[group[0]] = dict(zip(reader['group_columns'], group))
    operations, pairs, other_relations, nominal = [], [], [], {}
    for document in source['documents']:
        trace = document['trace']
        indices = {g['id']: i for i, g in enumerate(trace)}
        assert len(indices) == len(trace)
        for group in trace:
            assert rows[group['id']]['ivtff_group_raw'] == group['raw']
        doc_ops = []
        for record in document['records']:
            for entry in record['ordered_entries']:
                nominal.setdefault(entry['referent'], set()).add(entry['descriptor'])
            for construction in record['constructions']:
                nominal.setdefault(construction['argument'], set()).add(construction['descriptor'])
                for relation in construction['relations']:
                    if relation['relation'] != 'daiin':
                        other_relations.append(dict(construction=construction['id'], **relation))
                        continue
                    op = dict(id=construction['id'], page=document['page'], context=record['context'],
                              source_ids=construction['source_ids'], raw=construction['raw'],
                              descriptor=construction['descriptor'], resource_variable=construction['argument'],
                              anchor_source_id=construction['anchor_source_id'],
                              proposed_operator='R: Reserve', rival='I: EnsureCommitted',
                              distinct_use='ASSUMED_NOT_SOURCE_CONFIRMED',
                              resource_identity=None, initial_availability=None, native_evaluation='UNKNOWN')
                    assert [trace[indices[s]]['raw'] for s in op['source_ids']] == op['raw']
                    doc_ops.append(op)
        doc_ops.sort(key=lambda op: indices[op['source_ids'][0]])
        operations.extend(doc_ops)
        for first, second in zip(doc_ops, doc_ops[1:]):
            end, start = indices[first['source_ids'][-1]], indices[second['source_ids'][0]]
            intervening = trace[end + 1:start]
            span = trace[indices[first['source_ids'][0]]:indices[second['source_ids'][-1]] + 1]
            seams = [dict(left_id=a['id'], right_id=b['id'],
                          right_separator=rows[a['id']]['right_separator'],
                          left_separator=rows[b['id']]['left_separator']) for a, b in zip(span, span[1:])]
            clear = all(s['right_separator'] == s['left_separator'] == 'DEFINITE_SPACE' for s in seams)
            adjacent = not intervening and first['context'] == second['context'] and clear
            pairs.append(dict(page=document['page'], first=first['id'], second=second['id'],
                              intervening_groups=intervening, intervening_count=len(intervening), seams=seams,
                              state_propagation='CONDITIONAL_DIRECT_LOCAL_ONLY' if adjacent else 'UNKNOWN',
                              reason='No intervening text; pure descriptor lookup assumed' if adjacent else
                              'Unread intervening text or boundary; not an identity state transition'))
    spans = {}
    target = ['oiiin', 'daiin', 'qokeey', 'daiin']
    for reader, packet in packets['f89r1']['readers'].items():
        line = next(l for l in packet['lines'] if l['metadata']['locus'] == 'f89r1.9')
        matches = [i for i in range(len(line['groups']) - 3)
                   if [g[2] for g in line['groups'][i:i + 4]] == target]
        assert len(matches) == 1
        i = matches[0]
        spans[reader] = dict(group_columns=packet['group_columns'], metadata=line['metadata'],
                             complete_source_line=line['groups'], exact_span=line['groups'][i:i + 4],
                             scope='Alternative reading, not an independent observation; original seams unchanged')
    ids = [s for op in operations for s in op['source_ids']]
    assert len(operations) == 10 and len(ids) == len(set(ids)) == 17
    assert len(pairs) == 8 and sum(p['state_propagation'] != 'UNKNOWN' for p in pairs) == 1
    assert {r['relation'] for r in other_relations} == {'cthy', 'cthey', 'or', 'dy'}
    result = dict(status='EXPLORATORY_RESERVATION_CONTENT_NO_LEXICAL_PREFERENCE_OR_NATIVE_EXECUTION',
                  input_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths}, builder_sha256=sha(Path(__file__)),
                  preserved_documents=source['documents'], explicit_anchor_sites=source['explicit_anchor_sites'],
                  nominal_resources=[dict(variable=v, unknown_descriptions=sorted(ds), identity=None,
                                          availability=None, type='HYPOTHESIZED_RESOURCE_NOT_COUNTED_GROUP')
                                     for v, ds in sorted(nominal.items())
                                     if v in {op['resource_variable'] for op in operations}],
                  operations=operations, other_relations=other_relations, consecutive_operation_pairs=pairs,
                  reader_span=spans,
                  formal_scenarios=dict(status='SYNTHETIC_IDENTITY_INPUTS_NOT_NATIVE_BINDINGS',
                                        R_same=demo(reserve, True), R_different=demo(reserve, False),
                                        I_same=demo(ensure_committed, True), I_different=demo(ensure_committed, False)),
                  summary=dict(raw_groups=sum(len(d['trace']) for d in source['documents']),
                               operations=len(operations), operation_raw_groups=len(ids), other_raw_groups=132-len(ids),
                               retained_anchor_occurrences=len(source['explicit_anchor_sites']),
                               consecutive_pairs=len(pairs), direct_pairs=1, unknown_transition_pairs=7,
                               unknown_other_relation_occurrences=len(other_relations), confirmed_words=0),
                  assumptions=plan['assumptions'],
                  limits=[
                      'Preserved documents are source/alignment history. Their DAIIN relations receive proposed R or rival I semantics here.',
                      'Different variable names never imply different resources; no group lift, quantity, member individuation or fresh-identity repair.',
                      'Only the direct four-group span supports conditional state composition. No complete page execution or final inventory is derived.',
                      'The direct R scenario requires different resources for two successful distinct commitments, not observed manuscript inequality.',
                      'Q2 same-field identity is not inherited from relaxed IDEA95. If separately imposed on the direct pair, R conflicts and I does not, conditionally.',
                      'Only explicitly modeled descriptor/anchor lookup is side-effect-free. All115 unread groups remain unknown transitions, never proven no-ops or resource declarations.',
                      'Resource typing is proposed only for the ten operation argument variables; other nominal entries retain untyped source alignment. I reasserts the same commitment; R treats occurrences as distinct commitments.',
                      'Material meanings, identity, availability and distinct-use interpretation remain unbound. No operator preference or independent confirmation.'])
    (HERE / 'RESERVE80_READING_20261015.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()

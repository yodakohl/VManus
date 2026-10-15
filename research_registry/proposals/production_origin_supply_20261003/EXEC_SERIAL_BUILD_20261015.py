"""Source-aligned exploratory selector/application trace, not a decoder."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(tables, order, initial, reset=False):
    state, steps = initial, []
    for name in order:
        argument = initial if reset else state
        table = tables[name]
        if argument not in table:
            steps.append(dict(function=name, input=argument, status='UNDEFINED', output=None))
            return dict(steps=steps, executable=False, final=None)
        state = table[argument]
        steps.append(dict(function=name, input=argument, status='DEFINED', output=state))
    return dict(steps=steps, executable=True, final=state)


def examples():
    specs = [
        ('serial_versus_reset', {'F': {0: 1, 1: 2}, 'G': {0: 3, 1: 4}}, ['F', 'G']),
        ('idempotent', {'F': {0: 1, 1: 1}}, ['F', 'F']),
        ('involution', {'F': {0: 1, 1: 0}}, ['F', 'F']),
        ('partial_exhaustion', {'F': {0: 1}}, ['F', 'F']),
    ]
    return [dict(name=name, finite_domain=[0, 1, 2, 3, 4],
                 function_tables={k: [[a, b] for a, b in v.items()] for k, v in tables.items()},
                 input=0, order=order, serial=evaluate(tables, order, 0),
                 reset_rival=evaluate(tables, order, 0, True)) for name, tables, order in specs]


def main():
    plan_path = HERE / 'EXEC_SERIAL_PLAN_20261015.json'
    plan = json.loads(plan_path.read_text())
    loaded, pins = [], {str(plan_path.relative_to(ROOT)): sha(plan_path)}
    for pin in plan['design']['sources']:
        path = ROOT / pin['path']
        assert sha(path) == pin['sha256']
        pins[pin['path']] = sha(path)
        loaded.append(json.loads(path.read_text()))
    old, repeat, f45, f89 = loaded
    rows, source_documents = {}, []
    for page, packet in [('f45r', f45), ('f89r1', f89)]:
        reader = packet['readers']['IT2a']
        lines = sorted(reader['lines'], key=lambda l: int(l['metadata']['locus'].split('.')[1]))
        source_documents.append(dict(page=page, group_columns=reader['group_columns'], lines=lines))
    rep = repeat['readers']['IT2a']['records'][0]
    source_documents.append(dict(page='f115r', group_columns=rep['group_columns'], lines=[rep['line']]))
    order = {}
    for doc in source_documents:
        flat = []
        for line in doc['lines']:
            for group in line['groups']:
                row = dict(zip(doc['group_columns'], group))
                row['locus'] = line['metadata']['locus']
                rows[group[0]] = row
                flat.append(group[0])
        order[doc['page']] = flat
    constructions, other = [], []
    for doc in old['documents']:
        for record in doc['records']:
            for c in record['constructions']:
                if c['roles'] == ['daiin']:
                    assert c['raw'] == [rows[s]['ivtff_group_raw'] for s in c['source_ids']]
                    fused = len(c['source_ids']) == 1
                    if fused:
                        assert plan['design']['grammar']['bound'][c['raw'][0]] == [c['descriptor'], 'daiin']
                    constructions.append(dict(id=c['id'], page=doc['page'], head=c['descriptor'],
                                              source_ids=c['source_ids'], raw=c['raw'],
                                              encoding='FINITE_FUSION' if fused else 'FREE',
                                              application_source_ids=[c['source_ids'][-1]]))
                else:
                    other.append(c)
    selected = ['IT2a|f115r.17|G003', 'IT2a|f115r.17|G004', 'IT2a|f115r.17|G005']
    assert [rows[s]['ivtff_group_raw'] for s in selected] == ['qotchy', 'daiin', 'daiin']
    constructions.append(dict(id='f115r.17/G003-G005', page='f115r', head='qotchy',
                              source_ids=selected, raw=['qotchy', 'daiin', 'daiin'], encoding='FREE_REPEAT',
                              application_source_ids=selected[1:]))
    chains, applications, links = [], [], []
    for page, ids in order.items():
        positions = {sid: i for i, sid in enumerate(ids)}
        candidates = sorted([c for c in constructions if c['page'] == page],
                            key=lambda c: positions[c['source_ids'][0]])
        previous = None
        for c in candidates:
            start, end = positions[c['source_ids'][0]], positions[c['source_ids'][-1]]
            local_ids = ids[start:end + 1]
            assert local_ids == c['source_ids']
            assert all(rows[a]['right_separator'] == rows[b]['left_separator'] == 'DEFINITE_SPACE'
                       for a, b in zip(local_ids, local_ids[1:]))
            adjacent = previous is not None and start == previous[0] + 1
            if adjacent:
                a, b = rows[ids[previous[0]]], rows[ids[start]]
                adjacent = a['locus'] == b['locus'] and a['right_separator'] == b['left_separator'] == 'DEFINITE_SPACE'
            if not adjacent:
                chain = dict(id=f'CHAIN{len(chains)+1:02}', page=page, source_ids=[], applications=[],
                             boundary_input='UNBOUND_NOT_RESET', expression=f's_boundary_{len(chains)+1}',
                             native_executability='UNKNOWN_PARTIAL_FUNCTIONS_AND_INPUT')
                chains.append(chain)
            chain['source_ids'].extend(c['source_ids'])
            for sid in c['application_source_ids']:
                aid = f'APPLY{len(applications)+1:02}'
                before = chain['expression']
                after = f'F[{c["head"]}]({before})'
                if chain['applications']:
                    links.append(dict(from_application=chain['applications'][-1], to_application=aid,
                                      kind='CONDITIONAL_SERIAL_OUTPUT_TO_INPUT'))
                applications.append(dict(id=aid, construction=c['id'], source_id=sid, head=c['head'],
                                         function=f'F[{c["head"]}]', chain=chain['id'], input=before,
                                         output_if_defined=after, status='SYMBOLIC_NOT_NATIVE_EXECUTION'))
                chain['applications'].append(aid)
                chain['expression'] = after
            previous = (end, c)
    used = [s for c in constructions for s in c['source_ids']]
    assert len(rows) == 143 and len(used) == len(set(used)) == 20
    assert (len(constructions), len(applications), len(chains), len(links)) == (11, 12, 10, 2)
    spans = {r: dict(f115r17=entry['records'], f89r1_9=dict(
        group_columns=f89['readers'][r]['group_columns'],
        line=next(l for l in f89['readers'][r]['lines'] if l['metadata']['locus'] == 'f89r1.9')))
             for r, entry in repeat['readers'].items()}
    result = dict(status='EXPLORATORY_SERIAL_APPLICATION_NO_IDENTIFIED_TRANSFORMATIONS',
                  input_sha256=pins, builder_sha256=sha(Path(__file__)), source_documents=source_documents,
                  prior_alignment_documents=old['documents'],
                  old_anchors=dict(status='INACTIVE_PROVENANCE_ONLY', sites=old['explicit_anchor_sites']),
                  constructions=constructions, applications=applications, local_chains=chains,
                  serial_links=links, unknown_other_constructions=other, reader_local_full_spans=spans,
                  unread_source_ids=[sid for ids in order.values() for sid in ids if sid not in set(used)],
                  function_identity=dict(rule='Same exact head, same unknown partial function; different heads may alias',
                                         heads=sorted({c['head'] for c in constructions}), native_assignments={}),
                  formal_examples=dict(status='FINITE_SYNTHETIC_TABLES_NOT_NATIVE_FUNCTION_VALUES', cases=examples()),
                  summary=dict(raw_groups=len(rows), constructions=len(constructions), applications=len(applications),
                               contributing_groups=len(used), unread_groups=len(rows)-len(used),
                               local_chains=len(chains), serial_links=len(links), inactive_anchors=5, confirmed_words=0),
                  assumptions=plan['design']['assumptions'], limits=plan['design']['semantics'])
    (HERE / 'EXEC_SERIAL_TRACE_20261015.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()

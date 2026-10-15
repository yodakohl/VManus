"""Six fixed exploratory scoped readings and four finite illustrative worlds."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())
OPERATORS = {'qokar', 'tol', 'daiin'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def class_of(word, semantics):
    if word in OPERATORS:
        return None
    return semantics['primitive_classes'].get(word,
           semantics['finite_joined_classes'].get(word, ['N_' + word]))


def definite(a, b):
    return a['right_separator'] == b['left_separator'] == 'DEFINITE_SPACE'


def parse(unit, phase, semantics):
    groups = [dict(zip(unit['group_columns'], g)) for line in unit['lines'] for g in line['groups']]
    frames = [dict(id='FRAME1', quantifier='EXISTS', restriction=[], binder_source_ids=[],
                   implicit=True, variable='x1', body=[])]
    errors, events = [], []
    pairs = {tuple(p) for p in semantics['local_split_' + phase]}
    i = 0
    while i < len(groups):
        g = groups[i]
        w = g['ivtff_group_raw']
        nxt = groups[i + 1] if i + 1 < len(groups) else None
        v = nxt['ivtff_group_raw'] if nxt else None
        frame = frames[-1]
        if w in {'qokar', 'tol'}:
            # Binder priority consumes one immediately following class-valued raw group.
            if nxt is None or class_of(v, semantics) is None:
                error = dict(source_ids=[g['source_group_id']], error='MISSING_OR_OPERATOR_BINDER_ARGUMENT')
                errors.append(error)
                events.append(dict(kind='ERROR', **error))
                i += 1
                continue
            frame['closed_before_source_id'] = g['source_group_id']
            frame = dict(id=f'FRAME{len(frames)+1}', quantifier='EXISTS' if w == 'qokar' else 'ALL',
                         restriction=class_of(v, semantics), binder_source_ids=[g['source_group_id'], nxt['source_group_id']],
                         implicit=False, variable=f'x{len(frames)+1}', body=[])
            frames.append(frame)
            events.append(dict(kind='BINDER', frame=frame['id'], source_ids=frame['binder_source_ids']))
            i += 2
            continue
        if w == 'daiin':
            error = dict(source_ids=[g['source_group_id']], error='ORPHAN_DAIIN')
            errors.append(error)
            events.append(dict(kind='ERROR', **error))
            i += 1
            continue
        n = 1
        if nxt and (w, v) in pairs and definite(g, nxt):
            node = dict(kind='LOCAL_EXISTS', predicates=class_of(w, semantics) + class_of(v, semantics),
                        variable=f'z{len(events)+1}', changes_current=False)
            n = 2
        elif nxt and v == 'daiin' and definite(g, nxt):
            node = dict(kind='PREDICATE', predicates=class_of(w, semantics),
                        variable=frame['variable'], explicit_daiin=True)
            n = 2
        else:
            node = dict(kind='PREDICATE', predicates=class_of(w, semantics),
                        variable=frame['variable'], explicit_daiin=False)
        node['source_ids'] = [x['source_group_id'] for x in groups[i:i+n]]
        node['raw'] = [x['ivtff_group_raw'] for x in groups[i:i+n]]
        frame['body'].append(node)
        events.append(dict(kind=node['kind'], frame=frame['id'], source_ids=node['source_ids']))
        i += n
    frames[-1]['closed_at_selected_endpoint'] = True
    consumed = [s for e in events for s in e['source_ids']]
    assert consumed == [g['source_group_id'] for g in groups]
    opaque = {}
    for g in groups:
        atoms = class_of(g['ivtff_group_raw'], semantics)
        if atoms and atoms[0].startswith('N_'):
            opaque.setdefault(atoms[0], []).append(g['source_group_id'])
    all_ap = [f for f in frames if f['quantifier'] == 'ALL' and set(f['restriction']) == {'A', 'P'}]
    forcing = [n['source_ids'] for f in all_ap for n in f['body']
               if n['kind'] == 'PREDICATE' and 'Q' in n['predicates']]
    ap_witness = [f['id'] for f in frames if f['quantifier'] == 'EXISTS'
                  and {'A', 'P'} <= set(f['restriction'])]
    local_aq = [n['source_ids'] for f in all_ap for n in f['body']
                if n['kind'] == 'LOCAL_EXISTS' and {'A', 'Q'} <= set(n['predicates'])]
    return dict(id=phase + '_' + unit['edition'], phase=phase, reader=unit['edition'],
                source_group_count=len(groups), source_unit=unit, frames=frames, events=events, errors=errors,
                unknown_atoms=opaque, native_truth='UNASSIGNED_PREDICATE_INTERPRETATIONS',
                endpoint_status='ADDITIONAL_WINDOW_ENDPOINT_ASSUMPTION' if unit['edition'] == 'RF1b'
                                else 'SOURCE_FLAGGED_PARAGRAPH_ENDPOINT',
                scope_consequences=dict(AP_subset_Q_direct_body=bool(forcing), source_sites=forcing,
                                        AP_nonempty_explicit_frames=ap_witness,
                                        local_AQ_exists_under_ALL_sites=local_aq,
                                        AQ_nonempty_from_AP_and_local_exists=bool(ap_witness and local_aq)))


def world(name, atoms):
    domain = {'a', 'b'}
    predicates = {p: set(domain) for p in atoms | {'A', 'B', 'P', 'Q'}}
    if name == 'SELECTIVE_Q':
        predicates['Q'] = {'b'}
    elif name == 'RF_TAIL':
        predicates.update(A={'b'}, Q={'b'}, N_otar={'a'})
    elif name == 'EMPTY_AP':
        predicates['A'] = set()
    return dict(domain=sorted(domain), predicates={p: sorted(v) for p, v in sorted(predicates.items())})


def evaluate(case, model):
    domain, p = model['domain'], model['predicates']
    def holds(atoms, x):
        return all(x in p[a] for a in atoms)
    values = []
    for f in case['frames']:
        rows = []
        for x in domain:
            body = [any(holds(n['predicates'], z) for z in domain) if n['kind'] == 'LOCAL_EXISTS'
                    else holds(n['predicates'], x) for n in f['body']]
            restricted = holds(f['restriction'], x)
            rows.append(dict(entity=x, restriction=restricted, body_terms=body, body=all(body)))
        truth = (any(r['restriction'] and r['body'] for r in rows) if f['quantifier'] == 'EXISTS'
                 else all(not r['restriction'] or r['body'] for r in rows))
        values.append(dict(frame=f['id'], quantifier=f['quantifier'], rows=rows, truth=truth))
    return dict(frames=values, complete_truth=None if case['errors'] else all(v['truth'] for v in values))


def main():
    plan_path = HERE / 'R771_WITNESS_PLAN_20261016.json'
    plan = json.loads(plan_path.read_text())
    pin = plan['sources'][0]
    path = ROOT / pin['path']
    assert sha(path) == pin['sha256']
    source = json.loads(path.read_text())
    cases = [parse(unit, phase, plan['semantics']) for phase in ['POST', 'PRE'] for unit in source['units']]
    atoms = {a for c in cases for a in c['unknown_atoms']}
    worlds = {name: world(name, atoms) for name in plan['toy_models'] if name != 'purpose'}
    for case in cases:
        case['toy_results'] = {name: evaluate(case, model) for name, model in worlds.items()}
    result = dict(status='COMPLETE_CONDITIONAL_CLASS_READING_NOT_MEANING_SELECTION',
                  plan_sha256=sha(plan_path), source=dict(path=pin['path'], sha256=sha(path)),
                  builder_sha256=sha(Path(__file__)), source_units=source['units'], cases=cases,
                  toy_worlds=worlds, toy_status='COMPLETE_FINITE_INTERPRETATIONS_NOT_NATIVE_VALUES',
                  summary=dict(source_reader_groups=sum(sum(len(l['groups']) for l in u['lines']) for u in source['units']),
                               model_cases=len(cases), physical_manuscript_paragraphs=1,
                               parsed_model_positions=sum(c['source_group_count'] for c in cases),
                               parser_errors=sum(len(c['errors']) for c in cases), confirmed_words=0),
                  assumptions=plan['assumptions'], retained_stops=plan['retained_stops'],
                  limits=['Six informed variants reuse225reader groups;450parsed model positions are not independent evidence.',
                          'All unknown exact forms are uniformly class-typed, not translated. Marked strings are never normalized.',
                          'Local existential clauses stay inside frame bodies; ALL uses implication and adds no existence alone.',
                          'DAIIN explicit membership is truth-conditionally redundant with ordinary membership in this model.',
                          'Direct-body subset consequences are structural deductions, not corpus findings; failed toy worlds select no reader or grammar.',
                          'Bound variables do not escape frames; separate variable names imply no physical inequality.'])
    (HERE / 'R771_WITNESS_READING_20261016.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary'], sort_keys=True))
    for c in cases:
        print(c['id'], len(c['frames']), c['scope_consequences']['AP_subset_Q_direct_body'],
              {n: v['complete_truth'] for n, v in c['toy_results'].items()})


if __name__ == '__main__':
    main()

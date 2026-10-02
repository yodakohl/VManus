"""Reproduce the finite shared-root reduction from retained manually authored V1.

This constructs logical predicates, not a text decoder or a universal parser.
The 17 syntax/identity bindings are explicitly authored inputs in V1. This file
makes the shared semantic reduction executable and exposes its intermediate
outputs; it does not infer those bindings or choose manuscript meanings.
"""
from pathlib import Path
import copy
import hashlib
import inspect
import json

BASE = Path(__file__).resolve().parent
V1 = BASE / 'GD_SHARED_CONSTRUCTION_AUTHOR_20261002_V1.json'
OUT = BASE / 'GD_SHARED_CONSTRUCTION_AUTHOR_20261002.json'
V1_SHA = '8cfca47e06db72c6b8843929101920b95dc021287d0f0c232779d41a465c36c0'


def atom(predicate, *arguments):
    return {'op': 'ATOM', 'predicate': predicate, 'arguments': list(arguments)}


def conjunction(*arguments):
    return {'op': 'AND', 'arguments': list(arguments)}


def witness_package(event, condition):
    return {'op': 'WITNESS_PACKAGE', 'exported_ports': [event],
            'condition': condition}


def profile(root, owner, world, time, interval):
    if root['kind'] == 'STATE':
        return atom(root['relation'], world, owner, time)
    return atom('CAPABLE', world, owner,
                {'root_relation': root['relation'], 'grade': root['grade'],
                 'argument': owner, 'interval': interval})


def realized(root, owner, world, time, interval, event):
    if root['kind'] == 'STATE':
        return conjunction(
            atom(root['relation'], world, owner, time),
            witness_package(event, conjunction(
                atom('ACTUAL', world, event),
                atom('ATTAINS_STATE', world, event, owner, root['relation']),
                atom('BEFORE', {'event_end': event, 'world': world}, time))))
    conditions = [atom('ACTUAL', world, event),
                  atom(root['relation'], world, event, owner, interval)]
    if root['grade'] == 'CONTINUOUS':
        conditions.append(atom('CONTINUOUS_FULL_PHASE', world, event, interval))
    return witness_package(event, conjunction(*conditions))


def realize_frame(formula, frame, owner, world, event, host_event):
    if frame == 'QOK_NOMINAL_LIQUID':
        return conjunction(atom('LIQUID', world, owner), formula)
    if frame == 'LK_INSTRUMENT_MATERIAL':
        return conjunction(formula, atom('USING', world, host_event, event))
    return formula


def construct(core, raw, owner, world, time, interval, event, host_event=None):
    # Lookup licenses a root/mode/frame route; it never returns a whole meaning.
    route = core['finite_surface_licenses'][raw]
    root = copy.deepcopy(core['roots'][route['root']])
    if 'grade' in route:
        root['grade'] = route['grade']
    formula = (profile(root, owner, world, time, interval)
               if route['mode'] == 'EY' else
               realized(root, owner, world, time, interval, event))
    return realize_frame(formula, route['frame'], owner, world, event, host_event)


def replace(value, old, new):
    if isinstance(value, str):
        return new if value == old else value
    if isinstance(value, list):
        return [replace(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: replace(item, old, new) for key, item in value.items()}
    return value


def conditions(value):
    # Exported ports receive one joint existential scope at discourse closure.
    if isinstance(value, list):
        return [conditions(item) for item in value]
    if isinstance(value, dict):
        if value.get('op') == 'WITNESS_PACKAGE':
            return conditions(value['condition'])
        return {key: conditions(item) for key, item in value.items()}
    return value


def build():
    prior_bytes = V1.read_bytes()
    assert hashlib.sha256(prior_bytes).hexdigest() == V1_SHA
    result = json.loads(prior_bytes)
    core = result['core']
    core['generic_operator_pseudocode'] = '\n\n'.join(
        inspect.getsource(fun) for fun in
        (profile, realized, realize_frame, construct))
    for raw, item in result['computed_form_templates'].items():
        item['reduced_template'] = construct(
            core, raw, '$x', '$w', '$t', '$I', '$e', '$host_event')

    rows = result['full_17_written_order_reduction']
    # These are ES's paid manual syntax/context bindings, not inferred rules.
    contexts = {
        3: ('$next_appositional_material_head', 'T25', 'I25', 'E_clarify', None),
        4: ('M', 'T25', 'I25', None, None),
        5: ('M', 'T25', 'I25', 'E_carrier', '$next_motion_event'),
        6: ('$next_material_noun', 'T25', 'I25', None, None),
        8: ('F', 'T25', 'I25', 'E_fraction', None),
        9: ('F', 'T25', 'I25', None, None),
        14: ('D', 'T26', 'I26', 'E_out', None),
    }
    for index, (owner, time, interval, event, host) in contexts.items():
        row = rows[index]
        row['returned_template'] = result['computed_form_templates'][row['raw']]['reduced_template']
        row['kernel_reduction'] = {
            'input': {'owner': owner, 'world': 'W_actual', 'time': time,
                      'interval': interval, 'event_port': event, 'host_port': host},
            'output': construct(core, row['raw'], owner, 'W_actual', time,
                                interval, event, host),
            'binding_provenance': 'Manual finite ES syntax/context binding; not a universal parser'}

    # Consume the returned modifier and instrument ports in written order.
    rows[4]['lexical_predicates'] = [
        rows[4]['kernel_reduction']['output'],
        replace(rows[3]['kernel_reduction']['output'],
                '$next_appositional_material_head', 'M')]
    instrument = rows[5]['kernel_reduction']['output']
    rows[5]['lexical_predicates'] = [instrument['arguments'][0]]
    rows[5]['pending_relation_template'] = instrument['arguments'][1]
    rows[7]['lexical_predicates'][-1] = replace(
        rows[6]['kernel_reduction']['output'], '$next_material_noun', 'F')
    rows[8]['lexical_predicates'] = [
        rows[8]['kernel_reduction']['output'],
        replace(rows[5]['pending_relation_template'], '$next_motion_event', 'E_fraction')]
    rows[9]['lexical_predicates'] = [rows[9]['kernel_reduction']['output']]
    rows[14]['lexical_predicates'][0] = rows[14]['kernel_reduction']['output']

    facts = [item for row in rows for item in row['lexical_predicates']]
    binding_facts = [item for row in rows for item in row['paid_binding_predicates']
                     if isinstance(item, dict)]
    onset_facts = [atom('SAME_TIME', 'T25', {'phase_start': 'I25'}),
                   atom('SAME_TIME', 'T26', {'phase_start': 'I26'})]
    result['explicit_time_binding_predicates'] = onset_facts
    closure = result['discourse_existential_closure']
    ports = closure['entities'] + closure['events'] + closure['times'] + closure['phases']
    result['complete_conjunction'] = {
        'op': 'EXISTS', 'binders': ports,
        'body': conditions(conjunction(*(facts + binding_facts + onset_facts)))}
    result['comparison']['complete_mood_rival']['formula']['body'] = replace(
        result['complete_conjunction'], 'W_actual', 'W_plan')
    result['comparison']['manual_counterhistories'].append({
        'id': 'H_NO_FLOW_KEEP_ATTAINMENT',
        'change_from_H_ACTUAL': 'Keep prior actual E_clarify and all present material/capability properties; remove E_carrier, E_fraction, E_out and receiver entry.',
        'strict_ES_constructor': 'UNSAT at G006 actual instrumental flow, G009 actual fraction flow, G015 actual output flow and G016-G017 entry.',
        'possible_world_rival': 'Can remain satisfiable if an accessible planned world supplies those same flow/entry witnesses.',
        'purpose': 'Isolate the actual-flow branch without also changing the clarification history.'})
    result['exploratory_revision'] = {
        'prior_version_file': V1.name, 'prior_version_sha256': V1_SHA,
        'diagnosis': 'V1 frame pseudocode omitted LK USING while its template loop appended USING manually.',
        'change': 'Executable realize_frame now produces USING for the scoped LK instrumental frame; seven templates and their shared-root row reductions are generated by this function.',
        'new_word_values': 0, 'semantic_confirmation': False,
        'binding_status': '17 finite bindings manually supplied; no universal syntax parser.'}
    result['generator_source'] = {
        'file': Path(__file__).name,
        'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Small logical-constructor materializer from owned manual bindings; no source search or decoder.'}
    result['mechanical_checks']['LK_frame_generated_USING'] = True
    result['mechanical_checks']['explicit_T25_T26_onset_atoms_present'] = True
    result['mechanical_checks']['kernel_rows_materialized'] = len(contexts)
    assert len(rows) == 17
    assert [row['source_group_id'] for row in rows] == [
        source_id for line in result['source_preservation']['primary_IT_unit']['lines']
        for source_id in line['source_ids']]
    assert 'LIQUID' not in json.dumps(result['computed_form_templates']['qokeedy']['reduced_template'])
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    build()
    print(OUT.name, hashlib.sha256(OUT.read_bytes()).hexdigest())

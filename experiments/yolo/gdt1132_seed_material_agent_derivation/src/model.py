"""Finite GDT1132 material-to-person projection and actual consumer evaluator.

No lexical values or clause schemas are learned here. The pinned predecessor
compiler is reused; its global-actor executor is not called.
"""
from copy import deepcopy

POLICIES = ('ORIGIN', 'LAST_WORKING', 'ADDRESSEE', 'BODILY_SUPPORT')
DAIIN_POSITIONS = (9, 18, 35)
AIIN_POSITIONS = (5, 13, 23)


def aN(material):
    if material.get('type') != 'SeedGroup' or material.get('id') != 'G':
        return {'status': 'TYPE_MISMATCH', 'value': None}
    return {'status': 'KNOWN', 'value': deepcopy(material)}


def derive_person(policy, material, state, history, provenance, imperative):
    """d consumes actual aN material plus separately priced history/relations."""
    assert policy in POLICIES
    root = aN(material)
    result = {'policy': policy, 'interface': 'd+(a+N)' if policy != 'ADDRESSEE' else 'whole ADDRESSEE',
              'root_operation': root, 'arguments': {'material': deepcopy(material)},
              'status': 'MISSING', 'value': None, 'evidence': []}
    if root['status'] != 'KNOWN':
        result['status'] = root['status']; return result
    if policy == 'ADDRESSEE':
        values = [imperative] if imperative is not None else []
        result['evidence'] = [{'input': 'independent imperative addressee', 'Person': imperative}]
    elif policy == 'ORIGIN':
        containers = [r for r, groups in provenance['initial_contains'].items()
                      if groups.get(material['id']) == material['members']]
        events = [e for e in history if e['op'] == 'TAKE' and e['completed']
                  and e['object'] in containers]
        values = sorted({e['actor'] for e in events})
        result['evidence'] = [{'initial_contains': deepcopy(provenance['initial_contains']),
                               'original_container_ids': containers,
                               'completed_acquisitions': deepcopy(events)}]
    elif policy == 'LAST_WORKING':
        original = [r for r, groups in provenance['initial_contains'].items()
                    if groups.get(material['id']) == material['members']]
        containers = original + ([state['current_container']] if state['current_container'] else [])
        events = [e for e in history if e['completed'] and e['op'] in {'TAKE', 'EXTRACT', 'PLACE', 'BIND'}
                  and (e.get('material') == material['id'] or e['object'] in containers)]
        values = [events[-1]['actor']] if events else []
        result['evidence'] = deepcopy(events[-1:])
    else:
        supported = (state['current_container'] == 'C' and state['contents'] == material['members']
                     and state['bound_person'] is not None)
        values = [state['bound_person']] if supported else []
        result['evidence'] = [{'IN': ['G', 'C'], 'ON': ['C', 'NECK('+str(state['bound_person'])+')'],
                               'body_part_person': state['bound_person']}] if supported else []
    if len(values) == 1:
        result['status'] = 'KNOWN'; result['value'] = values[0]; result['returned_type'] = 'Person'
    elif len(values) > 1:
        result['status'] = 'AMBIGUOUS'; result['alternatives'] = values
    return result


def execute(graph, counts, world, policy, intervention='NONE', forced_person=None,
            instrument_owner_override=None):
    """Run five fixed clauses with three live daiin-to-consumer bindings.

    forced_person/instrument_owner_override are engineering probes only.
    Physical countercase order and t_bind knowledge duties are retained.
    """
    assert graph['status'] == 'COMPLETE' and policy in POLICIES
    assert all(isinstance(n, int) and n >= 0 for n in counts)
    c = graph['candidate']; imperative = world['actor']; recipient = world['recipient']
    seed_groups = [[f'r{i}s{j}' for j in range(n)] for i, n in enumerate(counts)]
    seeds = [s for g in seed_groups for s in g]
    material = {'id': 'G', 'type': 'SeedGroup', 'members': seeds.copy()}
    provenance = {'initial_contains': {'R': {'G': seeds.copy()}},
                  'initial_seed_raisin_membership': {s: f'r{i}' for i, g in enumerate(seed_groups) for s in g},
                  'scope': 'one complete f31r.1-5 rite',
                  'imperative_actor_input': {'type': 'Person', 'value': imperative,
                                           'independent_of_daiin': True, 'paid': True}}
    state = {'raisins': {f'r{i}': g.copy() for i, g in enumerate(seed_groups)},
             'taken': False, 'loose': [], 'contents': [], 'bound': None, 'claims': [],
             'current_container': 'R', 'bound_person': None}
    plan = deepcopy(graph['actions'])
    if intervention == 'BIND_BEFORE_PLACE': plan[2], plan[3] = plan[3], plan[2]
    pure = dict(world['purity'])
    if intervention == 'PURITY_ONLY_EARLIER': pure = {p: False for p in pure}
    trace = []; history = []; refs = []; roots = []; knowledge = []
    first = None; first_position = None; errors = []; status = 'COMPLETE'
    knowledge_person = None; completed = 0; purity_check = None

    def root_reference(position, consumer):
        value = aN(material)
        roots.append({'position': position, 'raw': 'aiin', 'root': value,
                      'consumer': consumer, 'same_material_id': 'G', 'same_members': seeds.copy()})
        return value

    def resolve(position, consumer):
        result = derive_person(policy, material, state, history, provenance, imperative)
        if forced_person and position in forced_person:
            result['engineering_override'] = True
            result['unmodified_policy_value'] = result.get('value')
            result['value'] = forced_person[position]; result['status'] = 'KNOWN'
        refs.append({'position': position, 'raw': 'daiin', 'derivation': result,
                     'consumer': consumer, 'actual_consumed_person': result['value'],
                     'history_completed_operations': len(history)})
        return result

    for step, original_action in enumerate(plan, 1):
        action = deepcopy(original_action); op = action['op']; local = []
        before = deepcopy(state)
        # C03 lies between EXTRACT and the C04 actions. Its Person is bound now;
        # assertion truth is still required at BIND's fixed t_bind, as in1027.
        if step == 3:
            r = resolve(18, 'KNOWS subject at t_bind')
            if r['status'] != 'KNOWN':
                status = r['status'] + '_REFERENCE'; first = step; first_position = 18
                errors = ['REFERENCE_'+r['status']+'_POSITION18']; break
            knowledge_person = r['value']
            root_reference(23, 'C04 PLACE/BIND same G; resolved before either physical action')
        if op == 'TAKE':
            action['actor'] = imperative
            root_reference(5, 'C01 quantity/CONTAINS and completed TAKE provenance')
            if not counts: local.append('EMPTY_RAISIN_SET')
            elif c['quantity'] == 'TOTAL' and len(seeds) != 4: local.append('QUANTITY_TOTAL')
            elif c['quantity'] == 'EACH' and any(n != 4 for n in counts): local.append('QUANTITY_EACH')
            if not local: state['taken'] = True
        elif op == 'EXTRACT':
            r = resolve(9, 'EXTRACT actor and NAILS owner')
            action['actor'] = r['value']
            if r['status'] != 'KNOWN':
                local.append('REFERENCE_'+r['status']+'_POSITION9')
                status = r['status'] + '_REFERENCE'; first_position = 9
                action['using'] = None; action['forbidden'] = None
            else:
                p = r['value']; owner = instrument_owner_override if instrument_owner_override is not None else p
                action['using'] = f'NAILS({owner})'; action['forbidden'] = f'MOUTH({p})'
                refs[-1]['actual_instrument'] = {'kind': 'NAILS', 'owner': owner}
                refs[-1]['source_imperative_actor_duty'] = imperative
                if p not in world['knowledge']: local.append('EXTRACT_PERSON_TYPE')
                if p != imperative: local.append('EXTRACT_SOURCE_ACTOR')
                if owner != p: local.append('INSTRUMENT_OWNER')
                if not state['taken']: local.append('NOT_TAKEN')
                if intervention == 'MOUTH':
                    action['attempted_instrument'] = f'MOUTH({p})'
                    local.append('MOUTH_PROHIBITED_BY_INSTRUCTION')
                root_reference(13, 'EXTRACT exact G from R')
                if not local:
                    state['loose'] = seeds.copy(); state['raisins'] = {r: [] for r in state['raisins']}
                    state['current_container'] = 'LOOSE'
        elif op == 'PLACE':
            action['actor'] = imperative
            attempted = seeds.copy()
            if intervention == 'SUBSTITUTE_SEEDS': attempted = [f'new{i}' for i in range(len(seeds))]
            if intervention == 'DROP_SEED': attempted = attempted[:-1]
            if intervention == 'EXTRA_SEED': attempted.append('new_extra')
            if set(attempted) != set(seeds) or set(state['loose']) != set(seeds): local.append('SEED_IDENTITIES')
            if not local:
                state['contents'] = attempted; state['loose'] = []; state['current_container'] = 'C'
        elif op == 'BIND':
            action['actor'] = imperative
            if set(state['contents']) != set(seeds) or not state['taken']: local.append('BIND_CONTENTS')
            for assertion in graph['knowledge']:
                positive = assertion['person'] == 'A'
                person = knowledge_person if positive else recipient
                actual = world['knowledge'].get(person, {}).get(assertion['object'])
                knowledge.append({'source_position': 18 if positive else 20, 'subject': person,
                                  'object': assertion['object'], 'time': assertion['time'],
                                  'required_value': assertion['value'], 'actual_value': actual})
                if actual != assertion['value']:
                    local.append('ACTOR_KNOWLEDGE' if positive else 'RECIPIENT_IGNORANCE')
            refs[-1]['actual_knowledge_content'] = deepcopy(knowledge)
            person = imperative if graph['purity']['person'] == 'A' else recipient
            purity_check = {'person':person,'time':'t_bind','actual_value':pure[person],
                            'required_value':True,'attachment':c['purity'],
                            'source_actor_condition_retained':c['purity']=='ACTOR'}
            if not pure[person]: local.append('PURITY_AT_BIND')
            if not local:
                state['bound'] = f'NECK({recipient})'; state['bound_person'] = recipient
        elif op == 'CLAIM':
            r = resolve(35, 'source-attributed RELEASE claim actor')
            action['actor'] = r['value']
            if r['status'] != 'KNOWN':
                local.append('REFERENCE_'+r['status']+'_POSITION35')
                status = r['status'] + '_REFERENCE'; first_position = 35
            else:
                p = r['value']; action['recipient'] = recipient
                action['content'] = f'RELEASE({p},{recipient},Q) BY_GRACE(GOD)'
                attempted_claim = {'actor': p, 'recipient': recipient, 'condition': 'Q', 'grace': 'GOD',
                                   'content': action['content'], 'status': 'SOURCE_ATTRIBUTED_ONLY'}
                refs[-1]['actual_attempted_claim_content'] = deepcopy(attempted_claim)
                refs[-1]['source_actor_duty_match'] = p == imperative
                if p != imperative: local.append('CLAIM_SOURCE_ACTOR')
                if state['bound'] != f'NECK({recipient})': local.append('NOT_BOUND')
                if not local:
                    state['claims'].append(attempted_claim); refs[-1]['actual_claim_content'] = deepcopy(attempted_claim)
        else: raise ValueError(op)
        trace.append({'step': step, 'operation': action, 'before': before,
                      'violations': local, 'after': deepcopy(state)})
        if local:
            errors = local; first = step
            if status == 'COMPLETE': status = 'INSTRUCTION_CONTRADICTION'
            break
        completed += 1
        history.append({'event': 'E'+str(step), 'op': op, 'actor': action['actor'],
                        'object': action.get('object', 'CLAIM'), 'material': 'G' if op in {'TAKE','EXTRACT','PLACE','BIND'} else None,
                        'completed': True, 'scope': provenance['scope']})
    after_failed = plan[first:] if first else []
    if first_position == 18: after_failed = plan[first-1:]
    reached = {r['position'] for r in refs}
    completed_ops = {e['op'] for e in history}
    attempted_ops = {e['operation']['op'] for e in trace}
    clause_accounting = []
    for clause in graph['clauses']:
        cid = clause['id']
        duties = {'C01':['TAKE'],'C02':['EXTRACT'],'C03':['KNOWS'],
                  'C04':['PLACE','BIND'],'C05':['PURITY_AT_BIND','CLAIM']}[cid]
        if cid=='C03':
            done = ['KNOWS'] if knowledge and all(x['actual_value']==x['required_value'] for x in knowledge) else []
            attempted = ['KNOWS'] if knowledge_person is not None else []
        elif cid=='C05':
            done = (['PURITY_AT_BIND'] if purity_check and purity_check['actual_value'] else []) + (['CLAIM'] if 'CLAIM' in completed_ops else [])
            attempted = (['PURITY_AT_BIND'] if purity_check else []) + (['CLAIM'] if 'CLAIM' in attempted_ops else [])
        else:
            done = [d for d in duties if d in completed_ops]
            attempted = [d for d in duties if d in attempted_ops]
        clause_accounting.append({'id':cid,'source_positions':clause['positions'],
                                  'required_duties':duties,'completed_duties':done,'attempted_duties':attempted,
                                  'unexecuted_duties':[d for d in duties if d not in attempted],
                                  'status':'DUTIES_COMPLETED' if done==duties else 'PARTIAL_OR_FAILED' if attempted else 'UNEXECUTED'})
    return {'policy': policy, 'coherent': not errors, 'status': status,
            'first_failure_step': first, 'first_failure_position': first_position,
            'first_violations': errors, 'completed_actions': completed,
            'unexecuted': [a['op'] for a in after_failed], 'unexecuted_plan': after_failed,
            'unexecuted_daiin_positions': [p for p in DAIIN_POSITIONS if p not in reached],
            'unexecuted_aiin_positions': [p for p in AIIN_POSITIONS if p not in {r['position'] for r in roots}],
            'reference_bindings': refs, 'bare_root_bindings': roots, 'knowledge_assertions': knowledge,
            'knowledge_staging':{'subject_resolution':'after completed EXTRACT, at source18',
                                 'truth_check':'at BIND t_bind; no KNOWN inference from purity'},
            'purity_check':purity_check,'clause_accounting':clause_accounting,
            'provenance': provenance, 'completed_history': history, 'trace': trace, 'final': state,
            'scope_costs': {'imperative_input': 1, 'material_case_register': 1,
                            'initial_membership_retention': 1, 'completed_action_history': 1,
                            'unique_acquisition_projection': int(policy == 'ORIGIN'),
                            'latest_relevant_history_projection': int(policy == 'LAST_WORKING'),
                            'explicit_addressee_input': int(policy == 'ADDRESSEE'),
                            'current_support_and_body_projection': int(policy == 'BODILY_SUPPORT'),
                            'live_person_to_three_consumers': 3},
            'source_purity_attachment': 'ACTOR_RETAINED' if c['purity']=='ACTOR' else 'ACTOR_SOURCE_CONDITION_OMITTED'}


def late_bodily_diagnostic(baseline_output):
    """Conditional late prefix inspection, never completion of failed support policy."""
    if not baseline_output['coherent']:
        return {'status': 'NOT_AVAILABLE_FAILED_BASELINE_PREFIX', 'full_candidate_status': 'MISSING_AT9'}
    state = baseline_output['trace'][-1]['before']
    provenance = baseline_output['provenance']
    material = {'id':'G','type':'SeedGroup','members':provenance['initial_contains']['R']['G']}
    history = [e for e in baseline_output['completed_history'] if e['op']!='CLAIM']
    ref = derive_person('BODILY_SUPPORT', material, state, history, provenance,
                        provenance['imperative_actor_input']['value'])
    if ref['status'] != 'KNOWN': return {'status': ref['status'], 'derivation': ref}
    old = baseline_output['final']['claims'][0]; p = ref['value']
    claim = {'actor':p,'recipient':old['recipient'],'condition':old['condition'],'grace':old['grace'],
             'content':f"RELEASE({p},{old['recipient']},{old['condition']}) BY_GRACE({old['grace']})",
             'status':'SOURCE_ATTRIBUTED_ONLY'}
    return {'status':'CONDITIONAL_LOCAL_DIAGNOSTIC_ONLY', 'position':35, 'derivation':ref,
            'baseline_prefix_completed_actions':4, 'full_candidate_status':'MISSING_AT9',
            'original_claim':old,'actual_attempted_claim':claim, 'actor_changed':p!=old['actor'],
            'source_actor_duty_match':p==old['actor'],
            'gate_violations':[] if p==old['actor'] else ['CLAIM_SOURCE_ACTOR'],
            'conforming_claim_append':claim if p==old['actor'] else None,
            'not_a_complete_candidate':True}

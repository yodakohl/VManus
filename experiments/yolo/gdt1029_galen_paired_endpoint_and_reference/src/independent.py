"""Separate source/tag and declarative checks; no import of model.py."""
from common import parent_source
CONTACT_CASES={
 'AIR_FAILURE':{'AIR'},'COLD_FAILURE':{'COLD_WATER'},'BOTH_FAILURE':{'AIR','COLD_WATER'},
 'AIR_ORDINARY_SOFT_ONLY':{'AIR'},'COLD_ORDINARY_SOFT_ONLY':{'COLD_WATER'},
 'AIR_PROPER_SOFT':{'AIR'},'COLD_PROPER_SOFT':{'COLD_WATER'},'BOTH_PROPER_SOFT':{'AIR','COLD_WATER'}}

def compile_reverse(old_lines,new_lines,lex,src):
    old_words=[w for l in old_lines for w in l['words']];new_words=[w for l in new_lines for w in l['words']]
    if any(w not in lex for w in old_words+new_words):return 'UNBOUND_FORMS'
    wanted=[v for p in parent_source()['whole_paragraph_productions'] for v in p['value_sequence']]
    if [lex[w]['value'] for w in old_words][::-1]!=wanted[::-1]:return 'PARENT_GRAMMAR_GAP'
    if len(new_words)!=46:return 'NEW_GRAMMAR_GAP'
    flat=[None]*46
    for cl in src['new_discontinuous_productions']:
        for pos,value in zip(cl['positions'],cl['values']):
            assert flat[pos-1] is None;flat[pos-1]=value
    return 'COMPLETE_POSITION_GRAPH' if [lex[w]['value'] for w in new_words][::-1]==flat[::-1] else 'NEW_GRAMMAR_GAP'

def prediction(c,name):
    cid=c['id'];r=dict(candidate=cid,case=name,status='',factual_violations='[]',norm_conformant='NA',norm_violations='[]',capability_satisfied='NA',forbidden_endpoint='NA',failure_trigger='NA',endpoint_violated='NA',nature_reference='NA',desired_opposite='NA',ordinary_endpoint='NOT_EXECUTED',total_boiling_events=0,independent_meaning_capacity=0)
    static={'LOCAL_E_M_D_INSTRUCTION':'INSTRUCTS_THOROUGH_M_D_FOR_E_WHILE_PARENT_FORBIDS_FULL_BOIL_E','EXECUTE_REPRISE':'NEW_EXECUTION_REQUIRES_CURRENT_W0_ORIGIN_WITHOUT_RESET_AFTER_W1_TRANSFER','STRICT_ORIGINAL36':'STRICT_RETENTION_DENOTATION_DOES_NOT_BIND_CONTACT_NORM'}
    if cid in static:
        r.update(status='UNBOUND_SEMANTIC_GENERALIZATION' if cid=='STRICT_ORIGINAL36' else 'STATIC_CONTRADICTION',factual_violations=static[cid]);return r
    contact=CONTACT_CASES.get(name,set())
    cap=name=='JOINT_CAPABILITY_AVAILABLE' if cid=='JOINT_EFFECT_CAPABILITY' else name!='ONLY_EVACUATION_CAPABILITY'
    trig=False if cid=='RESET_BY_CURRENT_HEAT' else name.startswith('BOTH_') if cid=='CONJUNCTIVE_CONTACT' else bool(contact)
    kind='ORDINARY_SOFT' if cid=='ENDPOINTS_COLLAPSED' else 'PROPER_SOFT'
    bad_endpoint=trig and (name.endswith('PROPER_SOFT') or (kind=='ORDINARY_SOFT' and name.endswith('ORDINARY_SOFT_ONLY')))
    bad=[]
    if not cap:bad.append('CAPABILITY:'+('JOINT_HISTORY' if cid=='JOINT_EFFECT_CAPABILITY' else 'EACH_HAS_A_HISTORY'))
    if bad_endpoint:bad.append('PERSISTENT_FAILURE:'+kind)
    ref='B' if name=='ORIGINAL_B_CURRENT_A' else 'A'
    if cid=='CURRENT_NATURE_REFERENCE':ref='B' if name=='ORIGINAL_A_CURRENT_B' else 'A'
    r.update(status='CONTRADICTED_BY_HYPOTHETICAL_FACTS' if bad else 'COMPATIBLE_WITH_HYPOTHETICAL_FACTS',factual_violations='|'.join(bad) or '[]',norm_conformant=int(not contact),norm_violations='|'.join(sorted(contact)) or '[]',capability_satisfied=int(cap),forbidden_endpoint=kind,failure_trigger=int(trig),endpoint_violated=int(bad_endpoint),nature_reference=ref,desired_opposite='A' if ref=='B' else 'B',ordinary_endpoint='PENDING_FINITE_OBSERVATION' if name.endswith('FAILURE') or name=='NO_CONTACT_PENDING' else 'OBSERVED_IN_FIXTURE',total_boiling_events=2)
    return r

def validate_graph(g,s):
    assert g['whole_groups']==95
    assert [p for cl in g['parent']['clauses'] for p in cl['positions']]==list(range(1,50))
    assert sorted(p for cl in g['new_clauses'] for p in cl['positions'])==list(range(1,47))
    for a,b in zip(g['new_clauses'],s['new_discontinuous_productions']):
        assert a['positions']==b['positions'] and a['values']==b['values']
    assert g['capability']['E_alias_positions']==[8,18,45]
    assert g['naming']['quoted_boils']==[21,22] and g['naming']['ordered_stages']==['E0','E1']
    assert not g['naming']['execute']
    assert g['references']['food_positions']==[23,29,32] and g['references']['replacement_water_positions']==[44,46]
    assert g['warning']['memory_instruction']['priority']=='ABOVE_ALL' and g['warning']['memory_instruction']['actual_memory'] is None
    assert g['method_extension']['actual_change'] is None and g['capability']['actual_effects']==[]
    assert g['source_speaker']!=g['cook']

def validate_output(g,f,o):
    cid=g['candidate']['id']
    if cid=='STRICT_ORIGINAL36':
        assert o['status']=='UNBOUND_SEMANTIC_GENERALIZATION' and o['executed_events']==[];return
    if cid=='LOCAL_E_M_D_INSTRUCTION':
        assert g['reprise']['method']=='M_D' and g['reprise']['purpose']=='E'
        assert g['references']['X'].startswith('P_E')
        assert g['parent']['norm']['forbidden']==['FULLY','BOIL','P_E']
        assert o['status']=='STATIC_CONTRADICTION' and o['executed_events']==[];return
    if cid=='EXECUTE_REPRISE':
        assert g['reprise']['mode']=='EXECUTE_AGAIN' and g['reprise']['origin'].endswith('=W0')
        assert g['parent']['dry']['steps'][-1]['medium']=='W1'
        assert o['completed_parent_witness']['final']['location']==o['actual_new_origin']=='W1'
        assert o['required_new_origin']=='W0' and o['new_reprise_events']==[]
        assert len(o['completed_parent_witness']['final']['events'])==2
        assert o['status']=='STATIC_CONTRADICTION' and o['executed_events']==[];return
    assert not f['proper_soft'] or f['ordinary_soft']
    facts={effect:{i for i,h in enumerate(f['capability_histories']) if effect in h} for effect in ['EVACUATION','CHECKING_BELLY']}
    cap=bool(facts['EVACUATION'] & facts['CHECKING_BELLY']) if cid=='JOINT_EFFECT_CAPABILITY' else bool(facts['EVACUATION']) and bool(facts['CHECKING_BELLY'])
    assert cap==o['capability_satisfied']
    contact=set(f['contacts']);assert o['norm_conformant']==(len(contact)==0)
    assert o['norm_violations']==sorted(contact)
    trigger=(not f['current_hot']) if cid=='RESET_BY_CURRENT_HEAT' else len(contact)==2 if cid=='CONJUNCTIVE_CONTACT' else len(contact)>0
    assert trigger==o['failure_trigger']
    endpoint=f['ordinary_soft'] if cid=='ENDPOINTS_COLLAPSED' else f['proper_soft']
    assert o['endpoint_violated']==(trigger and endpoint)
    assert (o['status']=='COMPATIBLE_WITH_HYPOTHETICAL_FACTS')==(cap and not (trigger and endpoint))
    ref=f['current_nature'] if cid=='CURRENT_NATURE_REFERENCE' else f['original_nature']
    assert o['nature_reference']==ref and o['desired_opposite']==f['opposites'][ref]
    tr=o['parent_trace'];records=tr['trace'];assert len(records)==3
    assert [x['action']['op'] for x in records]==['DISCARD','IMMEDIATE_TRANSFER','THOROUGH_REBOIL']
    assert records[0]['after']==records[1]['before'] and records[1]['after']==records[2]['before']
    assert tr['final']['food']=='P_D' and tr['final']['location']=='W1' and tr['final']['available_water']==['W1']
    assert tr['final']['events']==[['E0','BOIL','P_D','W0'],['E1','THOROUGH_REBOIL','P_D','W1']]
    assert tr['final']['soft']==f['ordinary_soft']
    assert not o['instantiated_parent_fixture']['exposed_soft_unreachable']
    assert all(x['before']['exposure']==x['after']['exposure']==tr['final']['exposure'] for x in records)
    assert o['clinical_observations']==tr['final']['medical_outcomes']==[]
    assert o['reprise_new_events']==0 and not o['naming_executes']

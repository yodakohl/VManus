from copy import deepcopy
from common import load_parent,parent_main,read,P
PM=load_parent('model')
NEW_TAGS='LENTIL_SOUP PREVIOUSLY_SAID CABBAGE PREPARE_LIKE BOTH CAN_CAUSE CHECKING_BELLY EVACUATION ONION LEEK ESPECIALLY WILD_LEEK GARLIC ANY_OTHER DESIRE ORIGINAL_NATURE OPPOSITE THIS_USE CALLED BOTH_THUS_PREPARED BOIL BOIL FOOD NO FOR REMEMBER_ABOVE_ALL BOIL PROPERLY_SOFT FOOD NO_LONGER LIQUID IMMEDIATE_TRANSFER IN AIR COLD WATER TOUCH HOWEVER_LONG BOIL AS_JUST_SAID FORMER READY_HOT IN THAT_WATER THIS_USE THAT_WATER'.split()
CLAUSES=[list(range(1,9))+[18,45],[19,20,21,22],list(range(9,18)),list(range(23,28))+list(range(34,38)),[28,29,30,38,39,43,44],[31,32,33,40,41,42,46]]
def no(domain,predicate):return not any(predicate(x) for x in domain)

def compile_pair(old_lines,new_lines,lex,c):
    ow=[w for l in old_lines for w in l['words']];nw=[w for l in new_lines for w in l['words']]
    unknown=sorted((set(ow)|set(nw))-set(lex))
    if unknown:return dict(status='UNBOUND_FORMS',unknown=unknown)
    parent=PM.compile_reading(old_lines,lex,parent_main())
    if parent['status']!='COMPLETE_GRAPH':return dict(status='PARENT_GRAMMAR_GAP',parent=parent)
    if [lex[w]['value'] for w in nw]!=NEW_TAGS:return dict(status='NEW_GRAMMAR_GAP')
    cid=c['id'];clauses=[dict(id=f'N{i+1:02}',positions=pos,words=[nw[n-1] for n in pos],values=[NEW_TAGS[n-1] for n in pos]) for i,pos in enumerate(CLAUSES)]
    return dict(status='COMPLETE_POSITION_GRAPH',candidate=c,whole_groups=len(ow)+len(nw),parent=parent,new_clauses=clauses,
        literal_parent_values=35 if cid!='STRICT_ORIGINAL36' else 36,parent_broadening=[] if cid=='STRICT_ORIGINAL36' else ['qoky'],new_value_rebindings=c['modified_new_entries'],
        semantic_binding='STRICT_RETENTION_DENOTATION_DOES_NOT_BIND_CONTACT_NORM' if cid=='STRICT_ORIGINAL36' else 'COMPLETE_CONDITIONAL',
        source_speaker='S',cook='A',prior_discourse=dict(N01='earlier source speech',N06='old C01 M_D'),
        capability=dict(food='LENTIL_SOUP',effects=['EVACUATION','CHECKING_BELLY'],scope='JOINT_HISTORY' if cid=='JOINT_EFFECT_CAPABILITY' else 'EACH_HAS_A_HISTORY',E_alias_positions=[8,18,45],actual_effects=[]),
        naming=dict(food_pair=['LENTIL_SOUP','CABBAGE'],condition='prepared_by_M_D',quoted_boils=[21,22],ordered_stages=['E0','E1'],execute=False),
        method_extension=dict(foods=['ONION','LEEK','WILD_LEEK','GARLIC'],especially=['WILD_LEEK','GARLIC'],other_guard='DESIRE_OPPOSITE',nature_reference='CURRENT' if cid=='CURRENT_NATURE_REFERENCE' else 'ORIGINAL',actual_change=None),
        warning=dict(food='X',planned_stage='E1 after E0',method='M_D',forbidden_media=['AIR','COLD_WATER'],quantifier='GENERALIZED_NO',memory_instruction=dict(agent='A',priority='ABOVE_ALL',actual_memory=None)),
        failure=dict(food='X',trigger='CURRENT_NOT_HOT' if cid=='RESET_BY_CURRENT_HEAT' else 'BOTH_CONTACTS' if cid=='CONJUNCTIVE_CONTACT' else 'EITHER_CONTACT',endpoint='ORDINARY_SOFT' if cid=='ENDPOINTS_COLLAPSED' else 'PROPER_SOFT',water='W1',duration='even_very_long'),
        reprise=dict(mode='EXECUTE_AGAIN' if cid=='EXECUTE_REPRISE' else 'RESTATE_SAME_PLAN',method='M_D',purpose='E' if cid=='LOCAL_E_M_D_INSTRUCTION' else 'D',food='X',origin='FORMER(LIQUID31)=W0',destination='W1',ready_hot=True,postcondition='IN(X,W1)'),
        references=dict(food_positions=[23,29,32],X='P_E in the explicitly local E instance' if cid=='LOCAL_E_M_D_INSTRUCTION' else 'P_D in a D instance',first_water='W0',replacement_water_positions=[44,46],replacement_water='W1',cold_water_position=36,cold_at='contact_time',E_positions=[18,45],E='parent evacuation purpose; N01 capability',origin_semantics='old preparation origin; no container geometry or separate measured lift'))

def evaluate(g,f=None):
    c=g['candidate'];cid=c['id'];assert g['whole_groups']==95
    if cid=='STRICT_ORIGINAL36':return dict(status='UNBOUND_SEMANTIC_GENERALIZATION',binding_gap=g['semantic_binding'],whole_groups=95,executed_events=[])
    if cid=='LOCAL_E_M_D_INSTRUCTION':
        assert g['reprise']['purpose']=='E' and g['parent']['norm']['case']=='E'
        return dict(status='STATIC_CONTRADICTION',violations=['INSTRUCTS_THOROUGH_M_D_FOR_E_WHILE_PARENT_FORBIDS_FULL_BOIL_E'],whole_groups=95,executed_events=[])
    if cid=='EXECUTE_REPRISE':
        completed=PM.dry_trace(g['parent'],read(P/'src/CASES.json')[0])
        assert completed['endpoint']=='OBSERVED_IN_FIXTURE' and completed['final']['location']=='W1'
        required_origin='W0';actual_origin=completed['final']['location']
        assert required_origin!=actual_origin
        return dict(status='STATIC_CONTRADICTION',violations=['NEW_EXECUTION_REQUIRES_CURRENT_W0_ORIGIN_WITHOUT_RESET_AFTER_W1_TRANSFER'],whole_groups=95,executed_events=[],completed_parent_witness=completed,required_new_origin=required_origin,actual_new_origin=actual_origin,new_reprise_events=[])
    assert not f['proper_soft'] or f['ordinary_soft'],'INVALID_FIXTURE: proper soft implies ordinary soft'
    effects=g['capability']['effects'];histories=f['capability_histories']
    capability=any(all(e in h for e in effects) for h in histories) if g['capability']['scope']=='JOINT_HISTORY' else all(any(e in h for h in histories) for e in effects)
    contacts=set(f['contacts']);assert contacts<=set(g['warning']['forbidden_media'])
    norm_ok=no(['X'],lambda x:bool(contacts))
    trigger={'CURRENT_NOT_HOT':not f['current_hot'],'BOTH_CONTACTS':{'AIR','COLD_WATER'}<=contacts,'EITHER_CONTACT':bool(contacts)}[g['failure']['trigger']]
    endpoint='ordinary_soft' if g['failure']['endpoint']=='ORDINARY_SOFT' else 'proper_soft'
    violation=bool(trigger and f[endpoint]);bad=[]
    if not capability:bad.append('CAPABILITY:'+g['capability']['scope'])
    if violation:bad.append('PERSISTENT_FAILURE:'+g['failure']['endpoint'])
    reference=f['current_nature'] if g['method_extension']['nature_reference']=='CURRENT' else f['original_nature']
    assert reference in f['opposites'];desired=f['opposites'][reference]
    pf=deepcopy(read(P/'src/CASES.json')[0]);pf.update(appearance_moderate=f['appearance_moderate'],replacement_hot=f['replacement_water_hot_at_transfer'],soft_observations=[f['ordinary_soft']],transfer_exposure='AIR' if 'AIR' in contacts else 'COLD_WATER' if contacts else 'NONE',exposed_soft_unreachable=False)
    # S is a supplied observation, Q is a distinct source predicate. Original parent fixtures are untouched.
    trace=PM.dry_trace(g['parent'],pf)
    return dict(status='COMPATIBLE_WITH_HYPOTHETICAL_FACTS' if not bad else 'CONTRADICTED_BY_HYPOTHETICAL_FACTS',whole_groups=95,factual_violations=bad,norm_conformant=norm_ok,norm_violations=sorted(contacts),capability_satisfied=capability,forbidden_endpoint=g['failure']['endpoint'],failure_trigger=trigger,endpoint_violated=violation,ordinary_soft=f['ordinary_soft'],proper_soft=f['proper_soft'],nature_reference=reference,desired_opposite=desired,parent_trace=trace,instantiated_parent_fixture=pf,naming_executes=False,reprise_new_events=0,memory_claim='instruction only; no actual memory observation',clinical_observations=[])

def projection(c,name,o):
    r=dict(candidate=c['id'],case=name,status=o['status'],factual_violations='[]',norm_conformant='NA',norm_violations='[]',capability_satisfied='NA',forbidden_endpoint='NA',failure_trigger='NA',endpoint_violated='NA',nature_reference='NA',desired_opposite='NA',ordinary_endpoint='NOT_EXECUTED',total_boiling_events=0,independent_meaning_capacity=0)
    if o['status'] in ['STATIC_CONTRADICTION','UNBOUND_SEMANTIC_GENERALIZATION']:
        r['factual_violations']='|'.join(o.get('violations',[o.get('binding_gap','')])) or '[]';return r
    r.update(factual_violations='|'.join(o['factual_violations']) or '[]',norm_conformant=int(o['norm_conformant']),norm_violations='|'.join(o['norm_violations']) or '[]',capability_satisfied=int(o['capability_satisfied']),forbidden_endpoint=o['forbidden_endpoint'],failure_trigger=int(o['failure_trigger']),endpoint_violated=int(o['endpoint_violated']),nature_reference=o['nature_reference'],desired_opposite=o['desired_opposite'],ordinary_endpoint=o['parent_trace']['endpoint'],total_boiling_events=len(o['parent_trace']['final']['events']))
    return r

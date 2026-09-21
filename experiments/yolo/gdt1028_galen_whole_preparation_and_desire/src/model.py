from copy import deepcopy
RULES=[
 'DESIRE DRY MOIST_BELLY WHEN SEEMS_MODERATELY_BOILED DISCARD FIRST IMMEDIATE_TRANSFER WATER IN OTHER WATER LIQUID HOT IN THAT_WATER THOROUGH_REBOIL UNTIL BOILED_FOOD SOFT'.split(),
 'FOR EVACUATION BOIL NOT FULLY'.split(),
 'FULLY BOIL BECAUSE FOR THIS_USE DESIRE RETAIN FULLY AS_POSSIBLE OWN LIQUID'.split(),
 'NO BOILED_FOOD CAN_RETAIN LIQUID COMPLETELY'.split(),
 'LONGER MORE LIQUID BOIL FOR EVACUATION LOSE THEREFORE'.split()]
ORDER=['ZERO','SOME','MORE','ALL']
REBOUND={'chody':'OWN serving-associated cooking liquor rather than intrinsic juice','oteedy':'RETAIN that associated cooking liquor','dy':'LOSE that associated cooking liquor'}

def compile_reading(lines,lex,c):
    words=[w for line in lines for w in line['words']]
    unknown=sorted(set(words)-set(lex))
    if unknown:return dict(status='UNBOUND_FORMS',unknown=unknown)
    tags=[lex[w]['value'] for w in words];cursor=0;clauses=[]
    for i,rule in enumerate(RULES):
        if tags[cursor:cursor+len(rule)]!=rule:return dict(status='GRAMMAR_CONTRADICTION',clause=f'C{i+1:02}',position=cursor+1)
        clauses.append(dict(id=f'C{i+1:02}',positions=list(range(cursor+1,cursor+len(rule)+1)),words=words[cursor:cursor+len(rule)],values=rule));cursor+=len(rule)
    if cursor!=len(words):return dict(status='GRAMMAR_CONTRADICTION',clause='TAIL')
    assert c['ownership'] in ['INTRINSIC','LIQUOR'] and c['comparison_scope'] in ['GENERAL','EVAC_ONLY']
    assert c['goal_mode'] in ['UNBRIDGED','BRIDGED','IDEAL_ALL']
    kind='J' if c['ownership']=='INTRINSIC' else 'K'
    transfer='W0' if c['syntax']=='NEAREST_WATER_TRANSFER' else 'P_D'
    static=[]
    if transfer=='W0':static.append('TRANSFER_EXPECTS_FOOD_BUT_W0_IS_WATER')
    if c['syntax']=='EXECUTED_REPRISE':static.append('EVAC_PROHIBITS_AND_INSTRUCTS_FULLY_BOIL')
    rebound=dict(REBOUND) if kind=='K' else {}
    if c['goal_mode']=='IDEAL_ALL':rebound['qokeedy']='AS_POSSIBLE qualifies a feasible approach to an ideal endpoint, replacing the main feasibility-qualified desired amount'
    return dict(status='COMPLETE_GRAPH',candidate=c,consumed=cursor,clauses=clauses,static_contradictions=static,
        rebound_denotations=rebound,
        references=[dict(position=7,reference='FIRST(WATER9)=W0'),dict(position=8,reference=transfer),dict(position=12,reference='OTHER(WATER)=W1'),dict(position=13,reference='W1'),dict(position=16,reference='W1'),dict(position=19,reference='P_D'),dict(position=30,reference='E'),dict(position=36,reference=f'{kind}(P_E)'),dict(position=38,reference='X:BOILED_FOOD'),dict(position=40,reference=f'{kind}(X)'),dict(position=44,reference=f'{kind}(X)')],
        food_cases=dict(D='P_D',E='P_E',identity='counterpart portions of same kind; not one simultaneous history'),
        dry=dict(guard='SEEMS_MODERATELY_BOILED(P_D,E0)',prior_event=['E0','BOIL','P_D','W0'],steps=[dict(op='DISCARD',object='W0'),dict(op='IMMEDIATE_TRANSFER',object=transfer,destination='W1'),dict(op='THOROUGH_REBOIL',object='P_D',medium='W1',event='E1',after='E0',until='SOFT(P_D)')]),
        norm=dict(case='E',forbidden=['FULLY','BOIL','P_E']),
        reprise=dict(case='E',mode='INSTRUCTED' if c['syntax']=='EXECUTED_REPRISE' else 'QUOTED_EXPLANANDUM',operation=['FULLY','BOIL','P_E'],explanandum='C02 prohibition'),
        goal=dict(agent='A',case='E',owner='P_E',liquid=f'{kind}(P_E)',mode=c['goal_mode'],actual_event=None),
        capacity=dict(domain='source cooked foods X',formula=f'NO X CAN_RETAIN(X,{kind}(X),ALL)'),
        comparison=dict(domain=['D','E'] if c['comparison_scope']=='GENERAL' else ['E'],liquid_kind=kind,relation='otherwise matched LONGER(BOIL) -> MORE(LOSE)',purpose_relevance='EVACUATION'))

def dry_trace(g,f):
    state=dict(food='P_D',location='W0',available_water=['W0','W1'],events=[['E0','BOIL','P_D','W0']],exposure=f['transfer_exposure'],soft=None,medical_outcomes=[])
    trace=[];violations=[];endpoint='UNEXECUTED'
    if not f['appearance_moderate']:return dict(violations=[],endpoint='INACTIVE_GUARD',trace=[],final=state,unexecuted=['DISCARD','IMMEDIATE_TRANSFER','THOROUGH_REBOIL'])
    if f['water_ids']['W0']==f['water_ids']['W1']:return dict(violations=['DISTINCT_WATERS'],endpoint=endpoint,trace=[],final=state,unexecuted=['DISCARD','IMMEDIATE_TRANSFER','THOROUGH_REBOIL'])
    if not f['replacement_hot']:return dict(violations=['HOT_REPLACEMENT_REQUIRED'],endpoint=endpoint,trace=[],final=state,unexecuted=['DISCARD','IMMEDIATE_TRANSFER','THOROUGH_REBOIL'])
    for n,a in enumerate(g['dry']['steps'],1):
        before=deepcopy(state);op=a['op']
        if op=='DISCARD':
            assert a['object']=='W0';state['available_water'].remove('W0');state['location']='AWAITING_TRANSFER'
        elif op=='IMMEDIATE_TRANSFER':
            assert a['object']=='P_D' and a['destination']=='W1' and 'W1' in state['available_water']
            state['location']='W1'
            # Immediacy and present heat never reset the given exposure history.
        elif op=='THOROUGH_REBOIL':
            assert state['location']==a['medium']=='W1'
            state['events'].append(['E1','THOROUGH_REBOIL','P_D','W1'])
            if f['exposed_soft_unreachable']:
                assert f['transfer_exposure'] in ['AIR','COLD_WATER'] and not any(f['soft_observations'])
                endpoint='UNREACHABLE_UNDER_SOURCE_CONTEXT';state['soft']=False
            elif any(f['soft_observations']):endpoint='OBSERVED_IN_FIXTURE';state['soft']=True
            else:endpoint='PENDING_FINITE_OBSERVATION';state['soft']=False
        else:raise ValueError(op)
        trace.append(dict(step=n,action=a,before=before,after=deepcopy(state)))
    return dict(violations=violations,endpoint=endpoint,trace=trace,final=state,unexecuted=[])

def goal_content(c,f):
    k='J' if c['ownership']=='INTRINSIC' else 'K';h=f['admissible_e'][k]
    if h['kind']=='FINITE':
        ds=h['degrees'];assert ds and all(d in ORDER for d in ds)
        positive=any(ORDER.index(d)>0 for d in ds);best=max(ds,key=ORDER.index);best_exists=True
        if 'ALL' in ds:assert f['can_retain_all']['P_E'][k]
    else:
        assert h['kind']=='ASCENDING_NO_GREATEST';positive=True;best=None;best_exists=False
    premises=dict(B16a=f['same_initial_own_liquid'],B16b=positive,B16c_best=best_exists,B16c_intention=f['intention_to_choose_best'],B16d=f['endpoint_complement'][k])
    mode=c['goal_mode'];licensed=mode=='BRIDGED' and all(premises.values())
    if mode=='BRIDGED':
        status='LICENSED' if licensed else 'PREMISES_UNAVAILABLE';extent=best if licensed else 'NO_LICENSED_BEST_OPTION'
    elif mode=='UNBRIDGED':status='NOT_ASSUMED';extent='FEASIBILITY_QUALIFIED_DESIDERATUM'
    else:status='IDEAL_NOT_BRIDGED';extent='ALL'
    actual=f['actual_retention'][k]
    return dict(bridge=status,premises=premises,intended_extent=extent,intended_not_lose_all='DERIVED' if licensed else 'NOT_DERIVED',ideal_feasibility=('ATTAINABLE_IN_FIXTURE' if f['can_retain_all']['P_E'][k] else 'UNATTAINABLE_IN_FIXTURE') if mode=='IDEAL_ALL' else 'NOT_AN_ALL_IDEAL',approach_qualification='FEASIBLE_APPROACH_TO_IDEAL; no actual attempt or greatest attainable option asserted' if mode=='IDEAL_ALL' else 'NOT_REINTERPRETED',actual_retention=actual,actual_lose_all=('TRUE' if actual=='ZERO' else 'FALSE') if actual is not None and f['endpoint_complement'][k] else 'NOT_ASSERTED',best_proof='For every u_n the admissible successor u_(n+1) is greater, hence no greatest' if not best_exists else 'maximum in stated finite ordered fixture')

def evaluate(g,f):
    assert g['status']=='COMPLETE_GRAPH'
    if g['static_contradictions']:return dict(status='STATIC_CONTRADICTION',violations=g['static_contradictions'],whole_groups=g['consumed'],executed_events=[])
    c=g['candidate'];k=g['comparison']['liquid_kind'];d=dry_trace(g,f);goal=goal_content(c,f)
    bad=list(d['violations'])
    for x in ['P_D','P_E']:
        if f['can_retain_all'][x][k]:bad.append(f'C04_FULL_RETENTION_CAPACITY:{x}:{k}')
    for case in g['comparison']['domain']:
        small,big=f['comparisons'][case][k]
        if ORDER.index(big)<=ORDER.index(small):bad.append(f'C05_LOSS_ORDER:{case}:{k}')
    omissions=[]
    if c['ownership']=='LIQUOR':omissions.append('INTRINSIC_JUICE_REFERENT_REPLACED')
    if c['comparison_scope']=='EVAC_ONLY':omissions.append('GENERAL_COMPARISON_SCOPE_NOT_RENDERED')
    if c['goal_mode']=='IDEAL_ALL':omissions.append('FEASIBILITY_QUALIFIED_AMOUNT_REINTERPRETED_AS_IDEAL_APPROACH')
    if goal['intended_not_lose_all']!='DERIVED':omissions.append('SEPARATE_NOT_LOSE_ALL_INTENTION_NOT_DERIVED')
    return dict(status='CONTRADICTED_FIXTURE' if bad else 'COHERENT_CONDITIONAL_CONTENT',violations=bad,whole_groups=g['consumed'],dry=d,goal=goal,source_obligation_omissions=omissions,source_completeness='CONDITIONAL_ON_ALL_LISTED_ASSUMPTIONS' if not omissions else 'SOURCE_CONTENT_GAP_OR_RIVAL',source_law_facts=dict(capacity=f['can_retain_all'],loss_comparisons=f['comparisons']),medical_outcomes=[])

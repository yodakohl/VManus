"""Second, declarative implementation; imports neither compiler nor executor.
This is a same-author software cross-check, not independent semantic evidence.
"""
RANK={'ZERO':0,'SOME':1,'MORE':2,'ALL':3}

def compile_reverse(lines,lex,productions):
    words=[w for line in lines for w in line['words']]
    if any(w not in lex for w in words):return 'UNBOUND_FORMS'
    actual=[lex[w]['value'] for w in words][::-1]
    expected=[v for p in productions for v in p['production'].split()][::-1]
    return 'COMPLETE_GRAPH' if actual==expected else 'GRAMMAR_CONTRADICTION'

def predict(c,name):
    """Named-fixture predictions written before any target compilation."""
    out=dict(candidate=c['id'],case=name)
    if c['syntax']!='QUOTED_FOOD_TRANSFER':
        bad='TRANSFER_EXPECTS_FOOD_BUT_W0_IS_WATER' if c['syntax']=='NEAREST_WATER_TRANSFER' else 'EVAC_PROHIBITS_AND_INSTRUCTS_FULLY_BOIL'
        return {**out,'status':'STATIC_CONTRADICTION','violations':bad,'endpoint':'NOT_EXECUTED','bridge':'NOT_EVALUATED','not_lose_all':'NOT_EVALUATED','extent':'NOT_EVALUATED','actual_lose_all':'NOT_EVALUATED','source_complete':0}
    bad=[];k='J' if c['ownership']=='INTRINSIC' else 'K'
    if name=='COLD_REPLACEMENT':bad.append('HOT_REPLACEMENT_REQUIRED')
    if name=='SAME_WATER':bad.append('DISTINCT_WATERS')
    if name=='ALL_RETAINABLE_'+c['ownership']:bad.append('C04_FULL_RETENTION_CAPACITY:P_E:'+k)
    if name=='EVAC_'+c['ownership']+'_FLAT':bad.append('C05_LOSS_ORDER:E:'+k)
    if name=='DRY_'+c['ownership']+'_FLAT' and c['comparison_scope']=='GENERAL':bad.append('C05_LOSS_ORDER:D:'+k)
    endpoint={'DRY_GUARD_FALSE':'INACTIVE_GUARD','COLD_REPLACEMENT':'UNEXECUTED','SAME_WATER':'UNEXECUTED','SOFT_NOT_YET_OBSERVED':'PENDING_FINITE_OBSERVATION','EXPOSED_ENDPOINT_UNREACHABLE':'UNREACHABLE_UNDER_SOURCE_CONTEXT'}.get(name,'OBSERVED_IN_FIXTURE')
    missing=name in ['ONLY_ZERO_RETENTION','PREFERENCE_WITHOUT_SELECTION_INTENTION'] or (k=='J' and name in ['INTRINSIC_NO_MAXIMUM','INTRINSIC_ENDPOINT_UNBOUND'])
    if c['goal_mode']=='BRIDGED':
        bridge='PREMISES_UNAVAILABLE' if missing else 'LICENSED'
        extent='NO_LICENSED_BEST_OPTION' if missing else ('ALL' if name=='ALL_RETAINABLE_'+c['ownership'] else 'MORE')
    elif c['goal_mode']=='UNBRIDGED':bridge='NOT_ASSUMED';extent='FEASIBILITY_QUALIFIED_DESIDERATUM'
    else:bridge='IDEAL_NOT_BRIDGED';extent='ALL'
    derived=bridge=='LICENSED'
    return {**out,'status':'CONTRADICTED_FIXTURE' if bad else 'COHERENT_CONDITIONAL_CONTENT','violations':'|'.join(bad) or '[]','endpoint':endpoint,'bridge':bridge,'not_lose_all':'DERIVED' if derived else 'NOT_DERIVED','extent':extent,'actual_lose_all':'TRUE' if name=='ACTUAL_ZERO_INTENDED_PARTIAL' else 'NOT_ASSERTED','source_complete':int(derived and k=='J' and c['comparison_scope']=='GENERAL')}

def observe(c,name,out):
    if out['status']=='STATIC_CONTRADICTION':
        return dict(candidate=c['id'],case=name,status=out['status'],violations='|'.join(out['violations']),endpoint='NOT_EXECUTED',bridge='NOT_EVALUATED',not_lose_all='NOT_EVALUATED',extent='NOT_EVALUATED',actual_lose_all='NOT_EVALUATED',source_complete=0)
    return dict(candidate=c['id'],case=name,status=out['status'],violations='|'.join(out['violations']) or '[]',endpoint=out['dry']['endpoint'],bridge=out['goal']['bridge'],not_lose_all=out['goal']['intended_not_lose_all'],extent=out['goal']['intended_extent'],actual_lose_all=out['goal']['actual_lose_all'],source_complete=int(not out['source_obligation_omissions']))

def validate_output(c,f,g,out):
    assert g['consumed']==out['whole_groups']==49
    assert [p for cl in g['clauses'] for p in cl['positions']]==list(range(1,50))
    refs={r['position']:r['reference'] for r in g['references']}
    assert refs[7]=='FIRST(WATER9)=W0' and refs[12]=='OTHER(WATER)=W1'
    assert refs[13]==refs[16]=='W1' and refs[19]=='P_D' and refs[30]=='E'
    k='J' if c['ownership']=='INTRINSIC' else 'K'
    assert refs[36]==k+'(P_E)' and refs[40]==refs[44]==k+'(X)'
    rebound=set() if k=='J' else {'chody','oteedy','dy'}
    if c['goal_mode']=='IDEAL_ALL':rebound.add('qokeedy')
    assert set(g['rebound_denotations'])==rebound
    if c['syntax']!='QUOTED_FOOD_TRANSFER':
        assert observe(c,'STATIC_WHOLE_GRAPH',out)==predict(c,'STATIC_WHOLE_GRAPH')
        assert out['executed_events']==[]
        return
    assert refs[8]=='P_D' and g['reprise']['mode']=='QUOTED_EXPLANANDUM'
    assert observe(c,f['name'],out)==predict(c,f['name'])
    d=out['dry'];tr=d['trace'];final=d['final']
    active=f['appearance_moderate'] and len(set(f['water_ids'].values()))==2 and f['replacement_hot']
    assert len(tr)==(3 if active else 0)
    assert len(final['events'])==(2 if active else 1)
    assert final['food']=='P_D' and final['exposure']==f['transfer_exposure']
    assert final['medical_outcomes']==out['medical_outcomes']==[]
    assert final['location']==('W1' if active else 'W0')
    assert final['available_water']==(['W1'] if active else ['W0','W1'])
    if active:
        assert [r['action']['op'] for r in tr]==['DISCARD','IMMEDIATE_TRANSFER','THOROUGH_REBOIL']
        assert tr[0]['after']['location']=='AWAITING_TRANSFER'
        assert tr[1]['after']['location']=='W1' and tr[1]['after']['events']==tr[0]['before']['events']
        assert tr[2]['after']['events']==[['E0','BOIL','P_D','W0'],['E1','THOROUGH_REBOIL','P_D','W1']]
        assert tr[1]['before']==tr[0]['after'] and tr[2]['before']==tr[1]['after']
        assert all(r['before']['exposure']==r['after']['exposure']==f['transfer_exposure'] for r in tr)
        assert final['soft']==any(f['soft_observations'])
    else:assert final['soft'] is None and len(d['unexecuted'])==3
    bad=[]
    if f['appearance_moderate']:
        if len(set(f['water_ids'].values()))!=2:bad.append('DISTINCT_WATERS')
        elif not f['replacement_hot']:bad.append('HOT_REPLACEMENT_REQUIRED')
    bad += ['C04_FULL_RETENTION_CAPACITY:'+x+':'+k for x in ['P_D','P_E'] if f['can_retain_all'][x][k]]
    domain=['D','E'] if c['comparison_scope']=='GENERAL' else ['E']
    bad += ['C05_LOSS_ORDER:'+x+':'+k for x in domain if RANK[f['comparisons'][x][k][1]]<=RANK[f['comparisons'][x][k][0]]]
    assert out['violations']==bad
    h=f['admissible_e'][k];goal=out['goal']
    if h['kind']=='FINITE':
        degrees=sorted(h['degrees'],key=lambda d:RANK[d])
        positive=any(d!='ZERO' for d in degrees);best=True
    else:
        # The predeclared successor witness rules out a greatest element.
        assert h['kind']=='ASCENDING_NO_GREATEST';positive=True;best=False
    premises=[f['same_initial_own_liquid'],positive,best,f['intention_to_choose_best'],f['endpoint_complement'][k]]
    assert list(goal['premises'].values())==premises
    if goal['bridge']=='LICENSED':
        assert all(premises) and RANK[goal['intended_extent']]>0
        assert goal['intended_extent']==degrees[-1]
    assert goal['actual_retention']==f['actual_retention'][k]
    assert g['goal']['actual_event'] is None

"""Relational reconstruction; no import of the new constructor or join."""
def facts(parsed):
    assert [x['kind'] for x in parsed]==['N'+str(i) for i in range(1,12)]
    v={x['kind']:[t[1] for t in x['tokens']] for x in parsed}
    c=v['N4'][3];w=v['N5'][3];o=v['N2'][0];pair=[v['N1'][1],v['N1'][4]]
    assert pair==['WEAVE','UNRAVEL'] and v['N5'][4]=='FIRST_OF_ORDERED_PAIR'
    assert v['N5'][2]==v['N6'][1]==v['N7'][4]==v['N10'][4]==c
    assert v['N7'][6]==o and v['N8'][4]==v['N10'][8]
    state_condition=dict(kind='STATE_TRUTH',predicate=v['N10'][8],cloth=c)
    return dict(pair=pair,cloth=c,worker=w,audience=o,patient_pending=False,
        beliefs=[dict(audience=o,content=dict(kind='APPEARANCE_OF_VISIBLE_PROGRESS',cloth=c,phase=v['N2'][5]),period='PRIOR',asserts_completion=False)],
        judgments=[dict(audience=o,basis=v['N3'][2],period='PRIOR')],
        knowledge=[dict(audience=o,action=pair[1],cloth=c,period='PRIOR',known=False)],
        topics=[dict(kind='ACTIVITY_SPECIFICATION',action=v['N4'][2],cloth=c,illumination=v['N1'][6],asserted=False),dict(kind='CLOTH',cloth=c,asserted=False)],
        habits=[dict(id='V3',action=pair[0],cloth=c,worker=w,period='PRIOR',phase=v['N1'][3])],
        requirements=[dict(predicate=v['N7'][1],cloth=c,requester=o,period='PRIOR',asserted_truth=False)],
        bounded=[dict(id='Z3',action=v['N8'][2],worker=w,cloth=c,compulsion=v['N8'][1],endpoint=dict(predicate=v['N8'][4],cloth=c),after='PRIOR')],
        states=[dict(clause='N6',predicate='FINISHED',cloth=c,at='PRIOR',truth=False),dict(clause='N8',predicate=v['N8'][4],cloth=c,at='Z3',truth=True),dict(clause='N9',predicate='FINISHED',cloth=c,at='PRIOR',truth=False)],
        progress=[dict(id='G',cloth=c,phase=v['N10'][3],period='PRIOR',realizes='V3',before='Z3',onset_of=state_condition)],
        recurrence=[dict(referent='G',period='PRIOR',each_phase=v['N11'][5],count=None,amount=None)],
        trace=[dict(clause=x['kind'],start=x['start'],end=x['end'],patient_bound=i>=3,worker_bound=i>=4) for i,x in enumerate(parsed)],
        declared_phase=dict(kind='REGION_MEMBERSHIP',region=v['N1'][3]),illumination=v['N1'][6])

def verify_joint(new,old,mode,result):
    h={e['action']:e for e in old['events'] if e['kind']=='HABIT'}
    z=next(e for e in old['events'] if e['kind']=='BOUNDED_ACTION');d=next(e for e in old['events'] if e['kind']=='DISCOVER')
    v=new['habits'][0];nz=new['bounded'][0];constraints={}
    for k in ('cloth','worker','audience'):constraints['SAME_'+k.upper()]=new[k]==old[k]
    constraints['SAME_ORDERED_ACTIVITY_TYPES']=tuple(new['pair'])==tuple(old['action_pairs'][-1]['actions'])
    topic=new['topics'][0];constraints['NOMINAL_UNRAVEL_REFERENT']=(topic['action'],topic['cloth'])==(h['UNRAVEL']['action'],h['UNRAVEL']['cloth'])
    for k in ('action','cloth','worker'):constraints['WEAVE_'+k.upper()]=v[k]==h['WEAVE'][k]
    constraints['SAME_EARLIER_PERIOD']={v['period'],h['WEAVE']['period'],h['UNRAVEL']['period']}=={'PRIOR'}
    if mode=='SHARED_FRAME':constraints['SHARED_V_SOLE_PHASE']=len({v['phase'],h['WEAVE']['phase']})==1
    for k in ('action','cloth','worker','compulsion'):constraints['COMPLETION_'+k.upper()]=nz[k]==z[k]
    constraints['SAME_FINISHED_ENDPOINT']=nz['endpoint']==z['asserted_state']
    constraints['REQUIRED_NOT_ACHIEVED']=all((x['asserted_truth'],x['predicate'],x['cloth'])==(False,nz['endpoint']['predicate'],new['cloth']) for x in new['requirements'])
    constraints['FIRST_RETURNS_ACTIVITY']=new['pair'][0] in ('WEAVE','UNRAVEL') and v['action']==new['pair'][0]
    constraints['NO_ADDED_NOMINAL_EVENT']=not any(x['asserted'] for x in new['topics'])
    constraints['NO_ACTUAL_MARRIAGE']='MARRIAGE' not in {x['kind'] for x in old['events']}
    mapping={'V3':h['WEAVE']['id'] if mode=='SHARED_FRAME' else 'V3','Z3':z['id'],'G':'G','PRIOR':'PRIOR'}
    assert result['frame_map']==mapping
    states=[dict(predicate=x['predicate'],cloth=x['cloth'],at=mapping[x['at']],truth=x['truth']) for x in new['states']]
    assert result['states']==states
    positives={(x['predicate'],x['cloth'],x['at']) for x in states if x['truth']};negatives={(x['predicate'],x['cloth'],x['at']) for x in states if not x['truth']}
    constraints['PHASE_SCOPED_STATE_CONSISTENCY']=not positives&negatives
    constraints['EARLIER_NOT_FINISHED_LATER_FINISHED']=all(x['at']!='PRIOR' or not x['truth'] for x in states) and any(x['at']==z['id'] and x['truth'] for x in states)
    constraints['EARLIER_IGNORANCE_LATER_DISCOVERY']=all((x['period'],x['known'],x['action'],x['cloth'],x['audience'])==('PRIOR',False,'UNRAVEL',h['UNRAVEL']['cloth'],old['audience']) for x in new['knowledge']) and d['knowledge'] is True and d['content']==h['UNRAVEL']['id']
    constraints['PROGRESS_SAME_WEAVE_CONTEXT']=all((x['realizes'],x['phase'],x['period'],x['cloth'],x['before'])==('V3',v['phase'],v['period'],v['cloth'],'Z3') for x in new['progress'])
    constraints['RECURRENCE_REFERENT']=all((x['referent'],x['period'],x['each_phase'])==(new['progress'][0]['id'],'PRIOR',new['progress'][0]['phase']) for x in new['recurrence'])
    edges=old['temporal_edges']+[['PRIOR',d['id'],True],['G',d['id'],True],['G',z['id'],True],[mapping['V3'],d['id'],True]]
    assert result['temporal_edges']==edges
    rel={(a,b):bool(strict) for a,b,strict in edges};nodes=set(x for a,b,_ in edges for x in (a,b))
    for k in nodes:
        for a in nodes:
            for b in nodes:
                if (a,k) in rel and (k,b) in rel:rel[a,b]=rel.get((a,b),False) or rel[a,k] or rel[k,b]
    constraints['JOINT_TEMPORAL_ORDER']=not any(rel.get((x,x),False) for x in nodes)
    assert {x['binding']:x['satisfied'] for x in result['checks']}==constraints
    errors=sorted(k for k,v in constraints.items() if not v);assert result['errors']==errors
    assert result['status']==('CONTRADICTED' if errors else 'COHERENT')
    if result['temporal_witness'] is not None:
        t=result['temporal_witness']
        assert all(t[b]>=t[a]+int(strict) for a,b,strict in edges)
    assert result['habitual_action_frames']==(2 if mode=='SHARED_FRAME' else 3)
    assert result['bounded_action_frames']==1 and result['asserted_marriages']==0
    return errors

"""Typed new assertion construction and explicit joint identity constraints."""
from common import temporal_witness

def condition(kind,value,cloth=None):
    if kind=='TIME_PHASE':return dict(kind='REGION_MEMBERSHIP',region=value)
    if kind=='FINISH_PREDICATE' and cloth is not None:return dict(kind='STATE_TRUTH',predicate=value,cloth=cloth)
    raise ValueError('INVALID_WHEN_OPERAND')

def first(pair):
    if not pair or any(t not in ('WEAVE','UNRAVEL') for t in pair):raise ValueError('FIRST_REQUIRES_ACTIVITY_PAIR')
    return pair[0]

def construct(parsed):
    g=dict(pair=None,cloth=None,worker=None,audience=None,patient_pending=True,
           beliefs=[],judgments=[],knowledge=[],topics=[],habits=[],requirements=[],
           bounded=[],states=[],progress=[],recurrence=[],trace=[])
    def need(ok,error):
        if not ok:raise ValueError(error)
    for c in parsed:
        kind=c['kind'];t=c['tokens'];v=[x[1] for x in t]
        if kind=='N1':
            g['pair']=[v[1],v[4]];g['declared_phase']=condition(t[3][0],v[3]);g['illumination']=v[6]
            need(g['pair']==['WEAVE','UNRAVEL'],'PAIR_ACTIVITY_TYPES')
        elif kind=='N2':
            g['audience']=v[0]
            g['beliefs'].append(dict(audience=v[0],content=dict(kind='APPEARANCE_OF_VISIBLE_PROGRESS',cloth='$PATIENT',phase=v[5]),period='PRIOR',asserts_completion=False))
        elif kind=='N3':
            need(g['audience'] is not None and g['pair'] is not None,'MISSING_EXPERIENCER_OR_PAIR')
            g['judgments'].append(dict(audience=g['audience'],basis=v[2],period='PRIOR'))
            g['knowledge'].append(dict(audience=g['audience'],action=g['pair'][1],cloth='$PATIENT',period='PRIOR',known=False))
        elif kind=='N4':
            need(g['patient_pending'],'DUPLICATE_PATIENT_BINDING')
            g['cloth']=v[3];g['patient_pending']=False
            g['topics'].append(dict(kind='ACTIVITY_SPECIFICATION',action=v[2],cloth=v[3],illumination=g['illumination'],asserted=False))
        elif kind=='N5':
            need(g['cloth']==v[2] and g['pair'] is not None,'UNBOUND_OR_DIFFERENT_PATIENT')
            g['worker']=v[3];act=first(g['pair'])
            need(v[4]=='FIRST_OF_ORDERED_PAIR','CHANGED_FIRST')
            g['habits'].append(dict(id='V3',action=act,cloth=g['cloth'],worker=v[3],period='PRIOR',phase=g['declared_phase']['region']))
        elif kind=='N6':
            need(g['cloth']==v[1],'TOPIC_PATIENT')
            g['topics'].append(dict(kind='CLOTH',cloth=v[1],asserted=False))
            g['states'].append(dict(clause=kind,predicate='FINISHED',cloth=v[1],at='PRIOR',truth=False))
        elif kind=='N7':
            need(v[4]==g['cloth'] and v[6]==g['audience'],'REQUEST_ARGUMENTS')
            g['requirements'].append(dict(predicate=v[1],cloth=v[4],requester=v[6],period='PRIOR',asserted_truth=False))
        elif kind=='N8':
            need(g['worker'] is not None and g['cloth'] is not None,'MISSING_COMPLETION_ARGUMENTS')
            g['bounded'].append(dict(id='Z3',action=v[2],worker=g['worker'],cloth=g['cloth'],compulsion=v[1],endpoint=dict(predicate=v[4],cloth=g['cloth']),after='PRIOR'))
            g['states'].append(dict(clause=kind,predicate=v[4],cloth=g['cloth'],at='Z3',truth=True))
        elif kind=='N9':
            need(g['bounded'],'NO_LATER_OUTCOME_FOR_CONTRAST')
            g['states'].append(dict(clause=kind,predicate='FINISHED',cloth=g['cloth'],at='PRIOR',truth=False))
        elif kind=='N10':
            need(v[4]==g['cloth'],'PROGRESS_PATIENT')
            cond=condition(t[8][0],v[8],g['cloth'])
            end=next((b for b in reversed(g['bounded']) if b['endpoint']==dict(predicate=cond['predicate'],cloth=cond['cloth'])),None)
            need(end is not None,'NO_ATTAINED_STATE_FOR_ONSET')
            g['progress'].append(dict(id='G',cloth=v[4],phase=v[3],period='PRIOR',realizes='V3',before=end['id'],onset_of=cond))
        elif kind=='N11':
            need(g['progress'],'NO_PROGRESS_REFERENT')
            g['recurrence'].append(dict(referent=g['progress'][-1]['id'],period='PRIOR',each_phase=v[5],count=None,amount=None))
        else:raise ValueError('UNKNOWN_NEW_PRODUCTION')
        g['trace'].append(dict(clause=kind,start=c['start'],end=c['end'],patient_bound=not g['patient_pending'],worker_bound=g['worker'] is not None))
    need(not g['patient_pending'],'UNBOUND_PATIENT')
    need(len(g['habits'])==len(g['bounded'])==len(g['progress'])==len(g['recurrence'])==1,'INCOMPLETE_NEW_GRAPH')
    def resolve(x):
        if isinstance(x,dict):return {k:resolve(v) for k,v in x.items()}
        if isinstance(x,list):return [resolve(v) for v in x]
        return g['cloth'] if x=='$PATIENT' else x
    return resolve(g)

def join(new,old,mode):
    assert mode in ('SHARED_FRAME','SEPARATE_V_DIAGNOSTIC')
    errors=[];checks=[]
    def check(name,ok):
        checks.append(dict(binding=name,satisfied=bool(ok)))
        if not ok:errors.append(name)
    v=new['habits'][0];z=new['bounded'][0]
    weave=next(e for e in old['events'] if e['kind']=='HABIT' and e['action']=='WEAVE')
    unravel=next(e for e in old['events'] if e['kind']=='HABIT' and e['action']=='UNRAVEL')
    final=next(e for e in old['events'] if e['kind']=='BOUNDED_ACTION')
    discovery=next(e for e in old['events'] if e['kind']=='DISCOVER')
    for key in ('cloth','worker','audience'):check('SAME_'+key.upper(),new[key]==old[key])
    check('SAME_ORDERED_ACTIVITY_TYPES',new['pair']==old['action_pairs'][-1]['actions'])
    check('NOMINAL_UNRAVEL_REFERENT',new['topics'][0]['action']==unravel['action'] and new['topics'][0]['cloth']==unravel['cloth'])
    for key in ('action','cloth','worker'):check('WEAVE_'+key.upper(),v[key]==weave[key])
    check('SAME_EARLIER_PERIOD',v['period']==weave['period']==unravel['period']=='PRIOR')
    if mode=='SHARED_FRAME':check('SHARED_V_SOLE_PHASE',v['phase']==weave['phase'])
    for key in ('action','cloth','worker','compulsion'):check('COMPLETION_'+key.upper(),z[key]==final[key])
    check('SAME_FINISHED_ENDPOINT',z['endpoint']==final['asserted_state'])
    check('REQUIRED_NOT_ACHIEVED',all(not x['asserted_truth'] and x['predicate']==z['endpoint']['predicate'] and x['cloth']==new['cloth'] for x in new['requirements']))
    check('FIRST_RETURNS_ACTIVITY',v['action']==first(new['pair']))
    check('NO_ADDED_NOMINAL_EVENT',all(x['asserted'] is False for x in new['topics']))
    check('NO_ACTUAL_MARRIAGE',all(e['kind']!='MARRIAGE' for e in old['events']))
    mapping={'V3':weave['id'] if mode=='SHARED_FRAME' else 'V3','Z3':final['id'],'G':'G','PRIOR':'PRIOR'}
    states=[dict(predicate=x['predicate'],cloth=x['cloth'],at=mapping[x['at']],truth=x['truth']) for x in new['states']]
    state_values={}
    for x in states:state_values.setdefault((x['predicate'],x['cloth'],x['at']),set()).add(x['truth'])
    check('PHASE_SCOPED_STATE_CONSISTENCY',all(len(vals)==1 for vals in state_values.values()))
    check('EARLIER_NOT_FINISHED_LATER_FINISHED',all(not x['truth'] for x in states if x['at']=='PRIOR') and any(x['truth'] for x in states if x['at']==final['id']))
    check('EARLIER_IGNORANCE_LATER_DISCOVERY',all(x['period']=='PRIOR' and x['known'] is False and x['action']==unravel['action'] and x['cloth']==unravel['cloth'] and x['audience']==old['audience'] for x in new['knowledge']) and discovery['knowledge'] is True and discovery['content']==unravel['id'])
    check('PROGRESS_SAME_WEAVE_CONTEXT',all(x['realizes']=='V3' and x['phase']==v['phase'] and x['period']==v['period'] and x['cloth']==v['cloth'] and x['before']=='Z3' for x in new['progress']))
    check('RECURRENCE_REFERENT',all(x['referent']==new['progress'][0]['id'] and x['period']=='PRIOR' and x['each_phase']==new['progress'][0]['phase'] for x in new['recurrence']))
    ids=[e['id'] for e in old['events']]+['PRIOR','G']+(['V3'] if mode=='SEPARATE_V_DIAGNOSTIC' else [])
    edges=old['temporal_edges']+[['PRIOR',discovery['id'],True],['G',discovery['id'],True],['G',final['id'],True],[mapping['V3'],discovery['id'],True]]
    try:ranks=temporal_witness([dict(id=x) for x in ids],edges);check('JOINT_TEMPORAL_ORDER',True)
    except ValueError:ranks=None;check('JOINT_TEMPORAL_ORDER',False)
    return dict(status='CONTRADICTED' if errors else 'COHERENT',errors=sorted(errors),checks=checks,frame_map=mapping,states=states,temporal_edges=edges,temporal_witness=ranks,habitual_action_frames=2+int(mode=='SEPARATE_V_DIAGNOSTIC'),bounded_action_frames=1,asserted_marriages=0,new_habit_phase=v['phase'],old_habit_phase=weave['phase'])

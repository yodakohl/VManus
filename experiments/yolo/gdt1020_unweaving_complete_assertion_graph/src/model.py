"""Typed construction parser and temporal assertion graph; no story lookup."""
from common import temporal_witness

def parse_all(words,spec):
    unknown=[dict(position=i+1,word=w) for i,w in enumerate(words) if w not in spec['lexicon']]
    if unknown:return [],unknown
    tokens=[spec['lexicon'][w] for w in words];memo={len(words):[[]]}
    def rec(i):
        if i in memo:return memo[i]
        out=[]
        for kind,shape in spec['productions'].items():
            part=tokens[i:i+len(shape)]
            if [t[0] for t in part]==shape:
                for tail in rec(i+len(shape)):out.append([dict(kind=kind,start=i,end=i+len(shape),tokens=part)]+tail)
        memo[i]=out;return out
    return rec(0),[]

def construct(parsed,pairing):
    cloth=None;worker=None;audience=None;needs_audience=False
    pairs=[];props=[];habits=[];endpoints=[];events=[];discoveries=[];edges=[];trace=[]
    def require(test,reason):
        if not test:raise ValueError(reason)
    def event(kind,cl,**fields):
        e=dict(id='E'+str(len(events)+1),kind=kind,clause=cl,**fields);events.append(e);return e
    def same_cloth(value):
        nonlocal cloth
        if cloth is None:cloth=value
        require(cloth==value,'DIFFERENT_CLOTH')
    for ci,cl in enumerate(parsed,1):
        kind=cl['kind'];v=[t[1] for t in cl['tokens']];cid='C'+str(ci);before=len(events);refs=[]
        if kind=='ACTION_PAIR':
            same_cloth(v[3]);pairs.append(dict(id='A'+str(len(pairs)+1),actions=[v[0],v[2]],cloth=cloth))
        elif kind=='PREREQUISITE':
            require(cloth is not None,'NO_CLOTH_FOR_PREREQUISITE')
            props.append(dict(id='P'+str(len(props)+1),predicate=v[0],cloth=cloth,social_act=v[1],worker=None,asserted=False))
        elif kind=='SECRET_HABIT':
            require(cloth is not None,'NO_CLOTH_FOR_HABIT');worker=v[2];needs_audience=True
            e=event('HABIT',cid,action=v[1],worker=worker,cloth=cloth,period='PRIOR',phase=None,concealed=True,audience='AUDIENCE_SLOT');habits.append(e)
        elif kind=='PUBLIC_PLEDGE':
            require(props and worker is not None,'NO_TYPED_PREREQUISITE_OR_WORKER');needs_audience=True
            p=props[-1];p['worker']=worker
            event('PLEDGE',cid,worker=worker,audience='AUDIENCE_SLOT',content=p['id'],period='PRIOR',phase=v[1]);refs.append(p['id'])
        elif kind=='UNTIL_HABIT':
            require(cloth is not None and worker is not None,'NO_HABIT_ARGUMENTS')
            require(v[3]==v[4],'DIFFERENT_DISTRIBUTIVE_ROW_VALUES')
            ep=dict(id='T'+str(len(endpoints)+1),predicate=v[1],action=v[2],worker=worker,cloth=cloth,prospective=True);endpoints.append(ep)
            e=event('HABIT',cid,action=v[2],worker=worker,cloth=cloth,period='PRIOR',phase=None,concealed=False,endpoint=ep['id'],distribution=dict(kind='DISTRIBUTIVE',unit=v[3],written_repetitions=2));habits.append(e)
        elif kind=='RESPECTIVE_TIMES':
            require(cloth is not None and v[3]==cloth and pairs,'NO_COMPATIBLE_ACTION_PAIR')
            pair=next((p for p in reversed(pairs) if p['cloth']==cloth),None);require(pair is not None,'NO_SAME_CLOTH_PAIR')
            times=v[4:6] if pairing=='direct' else v[4:6][::-1]
            for action,phase in zip(pair['actions'],times,strict=True):
                chosen=next((h for h in reversed(habits) if h['action']==action and h['cloth']==cloth),None)
                require(chosen is not None,'MISSING_EXISTING_HABIT')
                require(chosen['phase'] in (None,phase),'CONFLICTING_HABIT_PHASE')
                chosen['phase']=phase;refs.append(chosen['id'])
            refs.insert(0,pair['id'])
        elif kind=='REPORT_DISCOVERY':
            prior=next((h for h in reversed(habits) if h['concealed']),None);require(prior is not None,'NO_CONCEALED_CONTENT')
            require(audience in (None,v[2]),'INCOMPATIBLE_AUDIENCE');audience=v[2]
            report=event('INFORM',cid,speaker=v[0],audience='AUDIENCE_SLOT',content=prior['id'])
            discovery=event('DISCOVER',cid,subject='AUDIENCE_SLOT',content=prior['id'],phase=v[4],knowledge=True);discoveries.append(discovery)
            edges.append([report['id'],discovery['id'],False])
            for e in events:
                if e.get('period')=='PRIOR':edges.append([e['id'],discovery['id'],True])
            refs.append(prior['id'])
        elif kind=='THEN_COMPLETE':
            require(discoveries and cloth is not None,'NO_PRECEDING_DISCOVERY')
            require(worker==v[3],'CHANGED_FINAL_WORKER')
            ep=next((e for e in reversed(endpoints) if (e['action'],e['worker'],e['cloth'])==(v[2],v[3],cloth)),None)
            require(ep is not None,'NO_COMPATIBLE_WRITTEN_ENDPOINT')
            e=event('BOUNDED_ACTION',cid,action=v[2],worker=v[3],cloth=cloth,compulsion=v[1],endpoint=ep['id'],asserted_state=dict(predicate=ep['predicate'],cloth=cloth),phase=None)
            edges.append([discoveries[-1]['id'],e['id'],True]);refs.extend([discoveries[-1]['id'],ep['id']])
        else:raise ValueError('UNIMPLEMENTED_CONSTRUCTION')
        trace.append(dict(clause=cid,kind=kind,start=cl['start'],end=cl['end'],new_events=[e['id'] for e in events[before:]],references=refs))
    require(not needs_audience or audience is not None,'UNRESOLVED_AUDIENCE')
    require(all(p['worker'] is not None for p in props),'UNRESOLVED_PREREQUISITE_WORKER')
    require(all(h['phase'] is not None for h in habits),'UNRESOLVED_HABIT_PHASE')
    for e in events:
        for key in ['audience','subject']:
            if e.get(key)=='AUDIENCE_SLOT':e[key]=audience
    times=temporal_witness(events,edges)
    knowledge=[dict(content=h['id'],audience=audience,before_discovery=False) for h in habits if h['concealed']]
    knowledge += [dict(content=d['content'],audience=audience,at=d['id'],known=True) for d in discoveries]
    return dict(cloth=cloth,worker=worker,audience=audience,action_pairs=pairs,prerequisites=props,endpoints=endpoints,events=events,temporal_edges=edges,temporal_witness=times,knowledge=knowledge,trace=trace)

def inverse(parsed,spec):
    reverse={tuple(v):w for w,v in spec['lexicon'].items()};assert len(reverse)==len(spec['lexicon'])
    return [reverse[tuple(t)] for cl in parsed for t in cl['tokens']]

def evaluate(words,spec,pairing):
    parses,unknown=parse_all(words,spec)
    if unknown:return dict(status='SOURCE_FORMS_UNBOUND',unknown=unknown,parses=[])
    if not parses:return dict(status='NO_COMPLETE_PARSE',parses=[])
    rows=[]
    for parsed in parses:
        assert inverse(parsed,spec)==words
        try:graph=construct(parsed,pairing);rows.append(dict(status='COMPLETE_CONDITIONAL_READING',parse=parsed,graph=graph))
        except ValueError as e:rows.append(dict(status='INCOMPLETE_OR_CONTRADICTED',parse=parsed,error=str(e)))
    count=sum(r['status']=='COMPLETE_CONDITIONAL_READING' for r in rows)
    return dict(status='COMPLETE_CONDITIONAL_READING' if count==1 else 'AMBIGUOUS_READING' if count>1 else 'INCOMPLETE_OR_CONTRADICTED',parses=rows)

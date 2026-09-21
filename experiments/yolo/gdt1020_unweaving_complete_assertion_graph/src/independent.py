"""Reverse chart plus relational interpretation of prior construction records.
Does not import the forward parser, graph constructor or temporal solver.
"""

def parses(words,spec):
    if any(w not in spec['lexicon'] for w in words):return []
    tokens=[spec['lexicon'][w] for w in words];chart={0:[[]]}
    for end in range(1,len(words)+1):
        chart[end]=[]
        for k,shape in spec['productions'].items():
            start=end-len(shape)
            if start>=0 and [t[0] for t in tokens[start:end]]==shape:
                chart[end]+=[prefix+[dict(kind=k,start=start,end=end,tokens=tokens[start:end])] for prefix in chart[start]]
    return chart[len(words)]

def facts(parsed,pairing):
    values=[[t[1] for t in c['tokens']] for c in parsed];kinds=[c['kind'] for c in parsed]
    def prior(k,i,predicate=lambda j:True):return [j for j in range(i) if kinds[j]==k and predicate(j)]
    def latest(k,i,predicate=lambda j:True):
        eligible=prior(k,i,predicate)
        if not eligible:raise ValueError('MISSING_TYPED_BINDING:'+k)
        return eligible[-1]
    def cloth(i):return values[latest('ACTION_PAIR',i+1)][3]
    def worker(i):return values[latest('SECRET_HABIT',i+1)][2]
    def eid(i,k):return 'C'+str(i+1)+':'+k
    def require(ok):
        if not ok:raise ValueError('RELATIONAL_CONTRADICTION')
    events=[];props={};endpoints={};times={};concealed=[];pairs=[];temporal=[]
    # Every record is derived from its production and prior typed records.
    for i,(kind,v) in enumerate(zip(kinds,values,strict=True)):
        if kind=='ACTION_PAIR':
            if prior('ACTION_PAIR',i):require(v[3]==cloth(i-1))
            pairs.append((v[0],v[2],v[3]))
        elif kind=='PREREQUISITE':props[i]=dict(predicate=v[0],cloth=cloth(i),social_act=v[1],worker=None)
        elif kind=='SECRET_HABIT':
            events.append(dict(id=eid(i,'HABIT'),kind='HABIT',action=v[1],worker=v[2],cloth=cloth(i),phase=None,concealed=True));concealed.append(i)
        elif kind=='PUBLIC_PLEDGE':
            pi=latest('PREREQUISITE',i);props[pi]['worker']=worker(i)
            events.append(dict(id=eid(i,'PLEDGE'),kind='PLEDGE',worker=worker(i),phase=v[1],content='C'+str(pi+1)+':PREREQUISITE'))
        elif kind=='UNTIL_HABIT':
            require(v[3]==v[4]);ep=dict(predicate=v[1],action=v[2],worker=worker(i),cloth=cloth(i));endpoints[i]=ep
            events.append(dict(id=eid(i,'HABIT'),kind='HABIT',action=v[2],worker=worker(i),cloth=cloth(i),phase=None,concealed=False,endpoint=eid(i,'ENDPOINT'),distribution=(v[3],2)))
        elif kind=='RESPECTIVE_TIMES':
            pair=latest('ACTION_PAIR',i,lambda j:values[j][3]==v[3]);require(v[3]==cloth(i))
            actions=[values[pair][0],values[pair][2]];phases=v[4:6] if pairing=='direct' else list(reversed(v[4:6]))
            for action,phase in zip(actions,phases,strict=True):
                eligible=[j for j in range(i) if (kinds[j]=='SECRET_HABIT' and values[j][1]==action or kinds[j]=='UNTIL_HABIT' and values[j][2]==action) and cloth(j)==v[3]]
                require(bool(eligible));j=eligible[-1]
                require(j not in times or times[j]==phase);times[j]=phase
        elif kind=='REPORT_DISCOVERY':
            u=latest('SECRET_HABIT',i);content=eid(u,'HABIT')
            events.append(dict(id=eid(i,'INFORM'),kind='INFORM',speaker=v[0],audience=v[2],content=content))
            events.append(dict(id=eid(i,'DISCOVER'),kind='DISCOVER',subject=v[2],phase=v[4],content=content))
            temporal.append((eid(i,'INFORM'),eid(i,'DISCOVER'),False))
            temporal += [(e['id'],eid(i,'DISCOVER'),True) for e in events if e['kind'] in ('HABIT','PLEDGE')]
        elif kind=='THEN_COMPLETE':
            d=latest('REPORT_DISCOVERY',i);require(v[3]==worker(i));c=cloth(i)
            u=latest('UNTIL_HABIT',i,lambda j:(values[j][2],worker(j),cloth(j))==(v[2],v[3],c))
            ep=endpoints[u]
            events.append(dict(id=eid(i,'BOUNDED_ACTION'),kind='BOUNDED_ACTION',action=v[2],worker=v[3],cloth=c,compulsion=v[1],endpoint=eid(u,'ENDPOINT'),asserted_state=(ep['predicate'],c),phase=None))
            temporal.append((eid(d,'DISCOVER'),eid(i,'BOUNDED_ACTION'),True))
        else:raise ValueError('UNKNOWN_CONSTRUCTION')
    audience_values={values[i][2] for i,k in enumerate(kinds) if k=='REPORT_DISCOVERY'}
    require(len(audience_values)==1);audience=next(iter(audience_values))
    require(all(p['worker'] is not None for p in props.values()))
    for e in events:
        i=int(e['id'].split(':')[0][1:])-1
        if e['kind']=='HABIT':
            require(i in times);e['phase']=times[i]
            if e['concealed']:e['audience']=audience
        elif e['kind']=='PLEDGE':e['audience']=audience
    ids=[e['id'] for e in events];relation={(a,b):strict for a,b,strict in temporal}
    for k in ids:
        for i in ids:
            for j in ids:
                if (i,k) in relation and (k,j) in relation:relation[i,j]=relation.get((i,j),False) or relation[i,k] or relation[k,j]
    require(not any(relation.get((i,i),False) for i in ids))
    return dict(events=events,prerequisites=[dict(id=eid(i,'PREREQUISITE'),**p) for i,p in props.items()],endpoints=[dict(id=eid(i,'ENDPOINT'),**p) for i,p in endpoints.items()],action_pairs=pairs,temporal_edges=temporal,audience=audience)

def primary_facts(graph):
    """Lossless comparison view for semantically relevant asserted graph fields."""
    names={e['id']:e['clause']+':'+e['kind'] for e in graph['events']}
    pclauses=[r['clause'] for r in graph['trace'] if r['kind']=='PREREQUISITE'];eclauses=[r['clause'] for r in graph['trace'] if r['kind']=='UNTIL_HABIT']
    names.update({p['id']:cl+':PREREQUISITE' for p,cl in zip(graph['prerequisites'],pclauses,strict=True)})
    names.update({p['id']:cl+':ENDPOINT' for p,cl in zip(graph['endpoints'],eclauses,strict=True)})
    result=[]
    for e in graph['events']:
        row={k:v for k,v in e.items() if k not in ('clause','period','knowledge')};row['id']=names[e['id']]
        for k in ['content','endpoint']:
            if k in row:row[k]=names[row[k]]
        if 'distribution' in row:row['distribution']=(row['distribution']['unit'],row['distribution']['written_repetitions'])
        if 'asserted_state' in row:row['asserted_state']=(row['asserted_state']['predicate'],row['asserted_state']['cloth'])
        result.append(row)
    return dict(events=result,prerequisites=[dict(id=names[p['id']],**{k:v for k,v in p.items() if k not in ('id','asserted')}) for p in graph['prerequisites']],endpoints=[dict(id=names[p['id']],**{k:v for k,v in p.items() if k not in ('id','prospective')}) for p in graph['endpoints']],action_pairs=[tuple(p['actions']+[p['cloth']]) for p in graph['action_pairs']],temporal_edges=[(names[a],names[b],v) for a,b,v in graph['temporal_edges']],audience=graph['audience'])

def validate_graph(parsed,graph,pairing):
    expected=facts(parsed,pairing);actual=primary_facts(graph)
    assert actual==expected,(actual,expected)
    # The assertedness distinction is checked explicitly, not discarded by view.
    assert all(p['asserted'] is False for p in graph['prerequisites'])
    assert all(p['prospective'] is True for p in graph['endpoints'])
    for e in graph['events']:
        assert ('asserted_state' in e)==(e['kind']=='BOUNDED_ACTION')
        if e['kind']=='DISCOVER':assert e['knowledge'] is True
    required=[]
    for e in graph['events']:
        if e.get('concealed'):required.append(dict(content=e['id'],audience=graph['audience'],before_discovery=False))
    for e in graph['events']:
        if e['kind']=='DISCOVER':required.append(dict(content=e['content'],audience=graph['audience'],at=e['id'],known=True))
    assert graph['knowledge']==required
    for a,b,strict in graph['temporal_edges']:assert graph['temporal_witness'][b]>=graph['temporal_witness'][a]+int(strict)
    return expected

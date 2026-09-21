import copy

def compile_program(lines,lexicon,clauses,branch,mode):
    assert branch in ('E','H') and len(lines)==len(clauses)==9
    parsed=[];raw=[];offset=0
    for line,c in zip(lines,clauses):
        words=line['raw'].split();tags=[lexicon[w]['tag'] for w in words]
        assert tags==c['terminal_tags'],c['id']
        parsed.append(dict(id=c['id'],production=c['production'],start=offset,end=offset+len(words),tags=tags))
        raw+=words;offset+=len(words)
    part_kind='E' if mode=='CHOICE_IN_IMAGE' else branch
    image_kind=branch if mode=='CHOICE_IN_IMAGE' else 'E'
    item='I' if mode=='IMAGE_AS_PART' else 'P'
    plan=[['C01','TAKE','S'],['C01','GOAL','ENCLOSE','A']]
    if mode=='EARLY_ENCLOSE':plan.append(['C01','ENCLOSE','A'])
    plan += [['C03','ENGRAVE','S','I',image_kind],['C03','PREPARE','G']]
    choices=['E','H'] if mode=='BOTH_BRANCHES' else [part_kind]
    for choice in choices:
        clause='C06' if choice=='E' else 'C07'
        if choice=='E':plan.append([clause,'PREPARE_ITEMS',item,'G'])
        plan.append([clause,'PLACE',item,'G','S',choice])
    plan += [['C08','ENCLOSE','A'],['C08','WEAR','W','A'],
             ['C08','CLAIM_PROTECTION','A','W','Cyranides I.1.1-38'],
             ['C09','CLAIM_SOCIAL','A','W','RULERS','GREAT_PEOPLE','PEOPLE_OF_STANDING'],
             ['C09','CLAIM_OTHER','A'],['C09','CLOSE_SECTION','FIRST','ALPHA']]
    return dict(branch=branch,mode=mode,clauses=parsed,raw_roundtrip=raw,plan=plan,
        types={'S':'Stone','G':'GrapeSeed','P':'MaterialPart','I':'Depiction','A':'Assembly','W':'Person'},
        part_kind=part_kind,required_under=['G','P'],planned_components=['G','P','S'],
        invariants={'image_host':'S','depicted_kind':'E','physical_part_kind':branch},
        anatomy='WING_OR_FEATHER_TIP',goal_purposes=['AMULET','WEAR','PROTECTION'],
        typed_of=[dict(left='FORM_OF_I',left_type='Form',right=image_kind,right_type='BirdKind',relation='representation'),
                  dict(left='P',left_type='MaterialPart',right='B',right_type='BirdBody',relation='provenance')],
        body_source=dict(body='B',kind=part_kind,part='P'),
        with_relations=[dict(left='P',right='G',result='PG'),dict(left='PG',right='S',result='FRAME')])

def initial(graph):
    return dict(loose=['G','P','S'],taken=False,image_host=None,depicted_kind=None,
                under=[],components=[],enclosed=False,worn_by=None,goals=[],claims=[],closed_section=None)

def step(graph,state,operation):
    clause,op,*args=operation;errors=[];s=copy.deepcopy(state)
    def need(ok,error):
        if not ok:errors.append(error)
    def material(item):
        need(graph['types'].get(item) in ('Stone','GrapeSeed','MaterialPart'),'NOT_MATERIAL:'+item)
        need(item in s['loose'],'NOT_LOOSE_AVAILABLE:'+item)
    if op=='TAKE':material(args[0])
    elif op=='GOAL':
        need(args==['ENCLOSE','A'],'BAD_TYPED_GOAL')
    elif op=='ENGRAVE':
        need(s['taken'],'STONE_NOT_TAKEN');need(not s['enclosed'],'ALREADY_ENCLOSED')
        need(args[:2]==['S','I'],'WRONG_IMAGE_HOST');need(s['image_host'] is None,'IMAGE_ALREADY_EXISTS')
    elif op in ('PREPARE','PREPARE_ITEMS'):
        for item in args:material(item)
    elif op=='PLACE':
        part,seed,carrier,kind=args
        need(s['taken'],'STONE_NOT_TAKEN');need(carrier=='S','WRONG_CARRIER')
        for item in (part,seed):
            material(item);need(item in graph['required_under'],'MISSING_POSE:'+item)
        need(graph['types'].get(part)=='MaterialPart','NOT_BIRD_PART:'+part)
        need(graph['part_kind']==kind,'WRONG_PART_KIND')
    elif op=='ENCLOSE':
        need(args==['A'],'WRONG_ASSEMBLY');need(not s['enclosed'],'ALREADY_ENCLOSED')
        need(s['image_host']=='S','MISSING_HOSTED_IMAGE')
        for item in ('G','P'):need(item in s['under'],'MISSING_UNDER:'+item)
        need(s['components']==graph['planned_components'],'INCOMPLETE_COMPONENTS')
    elif op=='WEAR':
        need(args==['W','A'],'WRONG_WEARER_OR_ASSEMBLY');need(s['enclosed'],'NOT_ENCLOSED')
    elif op.startswith('CLAIM_') or op=='CLOSE_SECTION':pass
    else:raise AssertionError('unknown operation')
    if errors:return s,sorted(set(errors))
    if op=='TAKE':s['taken']=True
    elif op=='GOAL':s['goals'].append(dict(operation='ENCLOSE',object='A',purposes=graph['goal_purposes']))
    elif op=='ENGRAVE':s['image_host']=args[0];s['depicted_kind']=args[2]
    elif op=='PLACE':
        s['under']=sorted(set(s['under'])|set(args[:2]));s['components']=sorted(set(['S'])|set(s['under']))
        s['loose']=[x for x in s['loose'] if x not in s['components']]
    elif op=='ENCLOSE':s['enclosed']=True
    elif op=='WEAR':s['worn_by']=args[0]
    elif op.startswith('CLAIM_'):s['claims'].append([op,*args])
    elif op=='CLOSE_SECTION':s['closed_section']=args
    return s,[]

def execute(graph,override=None):
    state=initial(graph)
    if override:state.update(copy.deepcopy(override))
    trace=[];failure=[]
    for index,op in enumerate(graph['plan']):
        before=copy.deepcopy(state);state,errors=step(graph,state,op)
        trace.append(dict(index=index,operation=op,before=before,after=copy.deepcopy(state),errors=errors))
        if errors:failure=errors;break
    content=[]
    if not failure:
        if state['depicted_kind']!='E':content.append('C03_C05_IMAGE_NOT_E')
        if graph['part_kind']!=graph['branch']:content.append('C06_C07_PART_CHOICE_WRONG')
    return dict(physical_status='BLOCKED' if failure else 'COMPLETE',first_failure=failure,
                content_mismatches=content,final_state=state,trace=trace,
                unexecuted_plan=graph['plan'][len(trace):])

"""Reverse clause coverage and independently represented fact transitions."""
import copy

def compile_reverse(lines,lexicon,clauses,branch,mode):
    assert branch in ('E','H') and len(lines)==len(clauses)==9
    raw=[w for l in lines for w in l['raw'].split()];end=len(raw);parsed=[]
    for line,c in zip(lines[::-1],clauses[::-1]):
        start=end-len(line['raw'].split());tags=[lexicon[w]['tag'] for w in raw[start:end]]
        assert tags==c['terminal_tags']
        parsed.insert(0,dict(id=c['id'],production=c['production'],start=start,end=end,tags=tags));end=start
    assert end==0
    depicted=branch if mode=='CHOICE_IN_IMAGE' else 'E'
    origin='E' if mode=='CHOICE_IN_IMAGE' else branch
    component={'IMAGE_AS_PART':'I'}.get(mode,'P')
    body=[['C01','TAKE','S'],['C01','GOAL','ENCLOSE','A']]
    if mode=='EARLY_ENCLOSE':body += [['C01','ENCLOSE','A']]
    body += [['C03','ENGRAVE','S','I',depicted],['C03','PREPARE','G']]
    for c in (['E','H'] if mode=='BOTH_BRANCHES' else [origin]):
        if c=='E':body += [['C06','PREPARE_ITEMS',component,'G'],['C06','PLACE',component,'G','S','E']]
        else:body += [['C07','PLACE',component,'G','S','H']]
    body += [['C08','ENCLOSE','A'],['C08','WEAR','W','A'],['C08','CLAIM_PROTECTION','A','W','Cyranides I.1.1-38'],
             ['C09','CLAIM_SOCIAL','A','W','RULERS','GREAT_PEOPLE','PEOPLE_OF_STANDING'],['C09','CLAIM_OTHER','A'],['C09','CLOSE_SECTION','FIRST','ALPHA']]
    return dict(branch=branch,mode=mode,clauses=parsed,raw_roundtrip=raw,plan=body,
        types=dict(S='Stone',G='GrapeSeed',P='MaterialPart',I='Depiction',A='Assembly',W='Person'),
        part_kind=origin,required_under=['G','P'],planned_components=['G','P','S'],
        invariants=dict(image_host='S',depicted_kind='E',physical_part_kind=branch),
        anatomy='WING_OR_FEATHER_TIP',goal_purposes=['AMULET','WEAR','PROTECTION'],
        typed_of=[dict(left='FORM_OF_I',left_type='Form',right=depicted,right_type='BirdKind',relation='representation'),
                  dict(left='P',left_type='MaterialPart',right='B',right_type='BirdBody',relation='provenance')],
        body_source=dict(body='B',kind=origin,part='P'),
        with_relations=[dict(left='P',right='G',result='PG'),dict(left='PG',right='S',result='FRAME')])

def execute_facts(graph,override=None):
    facts={('loose',x) for x in ['G','P','S']};claims=[];goals=[];section=None
    def normalized():
        return dict(loose=sorted(x[1] for x in facts if x[0]=='loose'),taken=('taken','S') in facts,
            image_host=next((x[1] for x in facts if x[0]=='host'),None),
            depicted_kind=next((x[1] for x in facts if x[0]=='depicts'),None),
            under=sorted(x[1] for x in facts if x[0]=='under'),
            components=sorted(x[1] for x in facts if x[0]=='component'),enclosed=('enclosed','A') in facts,
            worn_by=next((x[1] for x in facts if x[0]=='wearer'),None),goals=copy.deepcopy(goals),
            claims=copy.deepcopy(claims),closed_section=copy.deepcopy(section))
    if override:
        assert set(override)<=set(['loose'])
        facts={x for x in facts if x[0]!='loose'}|{('loose',x) for x in override['loose']}
    history=[];failure=[]
    for i,operation in enumerate(graph['plan']):
        clause,op,*args=operation;before=normalized();errors=set()
        material_args=args if op in ['TAKE','PREPARE','PREPARE_ITEMS'] else args[:2] if op=='PLACE' else []
        for item in material_args:
            if graph['types'].get(item) not in ['Stone','GrapeSeed','MaterialPart']:errors.add('NOT_MATERIAL:'+item)
            if ('loose',item) not in facts:errors.add('NOT_LOOSE_AVAILABLE:'+item)
        if op=='GOAL' and args!=['ENCLOSE','A']:errors.add('BAD_TYPED_GOAL')
        if op=='ENGRAVE':
            if ('taken','S') not in facts:errors.add('STONE_NOT_TAKEN')
            if ('enclosed','A') in facts:errors.add('ALREADY_ENCLOSED')
            if args[:2]!=['S','I']:errors.add('WRONG_IMAGE_HOST')
            if any(x[0]=='host' for x in facts):errors.add('IMAGE_ALREADY_EXISTS')
        if op=='PLACE':
            if ('taken','S') not in facts:errors.add('STONE_NOT_TAKEN')
            if args[2]!='S':errors.add('WRONG_CARRIER')
            for x in args[:2]:
                if x not in graph['required_under']:errors.add('MISSING_POSE:'+x)
            if graph['types'].get(args[0])!='MaterialPart':errors.add('NOT_BIRD_PART:'+args[0])
            if args[3]!=graph['part_kind']:errors.add('WRONG_PART_KIND')
        if op=='ENCLOSE':
            if args!=['A']:errors.add('WRONG_ASSEMBLY')
            if ('enclosed','A') in facts:errors.add('ALREADY_ENCLOSED')
            if ('host','S') not in facts:errors.add('MISSING_HOSTED_IMAGE')
            errors.update('MISSING_UNDER:'+x for x in ['G','P'] if ('under',x) not in facts)
            if {x[1] for x in facts if x[0]=='component'}!=set(graph['planned_components']):errors.add('INCOMPLETE_COMPONENTS')
        if op=='WEAR':
            if args!=['W','A']:errors.add('WRONG_WEARER_OR_ASSEMBLY')
            if ('enclosed','A') not in facts:errors.add('NOT_ENCLOSED')
        if not errors:
            if op=='TAKE':facts.add(('taken','S'))
            elif op=='GOAL':goals.append(dict(operation='ENCLOSE',object='A',purposes=graph['goal_purposes']))
            elif op=='ENGRAVE':facts|={('host',args[0]),('depicts',args[2])}
            elif op=='PLACE':
                facts|={('under',x) for x in args[:2]}|{('component',x) for x in ['S',*args[:2]]}
                facts-={('loose',x) for x in ['S',*args[:2]]}
            elif op=='ENCLOSE':facts.add(('enclosed','A'))
            elif op=='WEAR':facts.add(('wearer',args[0]))
            elif op.startswith('CLAIM_'):claims.append([op,*args])
            elif op=='CLOSE_SECTION':section=args
        history.append(dict(index=i,operation=operation,before=before,after=normalized(),errors=sorted(errors)))
        if errors:failure=sorted(errors);break
    mismatches=[];end=normalized()
    if not failure:
        if ('depicts','E') not in facts:mismatches.append('C03_C05_IMAGE_NOT_E')
        if graph['branch']!=graph['part_kind']:mismatches.append('C06_C07_PART_CHOICE_WRONG')
    return dict(physical_status='BLOCKED' if failure else 'COMPLETE',first_failure=failure,
        content_mismatches=mismatches,final_state=end,trace=history,unexecuted_plan=graph['plan'][len(history):])

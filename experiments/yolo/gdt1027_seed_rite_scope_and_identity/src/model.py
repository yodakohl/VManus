from copy import deepcopy

RULES=[
 'TAKE RAISINS FOUR THE GRAPE_SEEDS CONTAINING THEREFORE'.split(),
 'EXTRACT YOU FINGERNAILS USING THE GRAPE_SEEDS NOT_USING MOUTH'.split(),
 'KNOWS THIS_RITE YOU KNOWS RECIPIENT NOT'.split(),
 'THE GRAPE_SEEDS PLACE CLOTH IN NECK ON BIND'.split(),
 'PURE BEING WHILE ATTRIBUTED_CLAIM BY_GRACE YOU RELEASE GOD'.split()]

def compile_reading(lines, lexicon, candidate):
    words=[w for line in lines for w in line['words']]
    unknown=sorted(set(words)-set(lexicon))
    if unknown: return dict(status='UNBOUND_FORMS',unknown=unknown)
    tags=[lexicon[w]['tag'] for w in words]
    cursor=0; clauses=[]
    for i,rule in enumerate(RULES):
        if tags[cursor:cursor+len(rule)]!=rule:
            return dict(status='GRAMMAR_CONTRADICTION',clause=f'C{i+1:02}',position=cursor+1)
        clauses.append(dict(id=f'C{i+1:02}',positions=list(range(cursor+1,cursor+len(rule)+1)),words=words[cursor:cursor+len(rule)],tags=rule))
        cursor+=len(rule)
    if cursor!=len(words): return dict(status='GRAMMAR_CONTRADICTION',clause='EXTRA_GROUPS',position=cursor+1)
    assert candidate['quantity'] in ['TOTAL','EACH']
    assert candidate['knowledge'] in ['SAME_OBJECT','DIFFERENT_OBJECTS']
    assert candidate['purity'] in ['ACTOR','RECIPIENT']
    objects=['P_rite','P_rite'] if candidate['knowledge']=='SAME_OBJECT' else ['P_attach','P_purpose']
    return dict(status='COMPLETE',candidate=candidate,clauses=clauses,consumed=cursor,
        seed_references=[dict(position=p+1,reference='G') for p,t in enumerate(tags) if t=='GRAPE_SEEDS'],
        actor_references=[dict(position=p+1,reference='A') for p,t in enumerate(tags) if t=='YOU'],
        knowledge=[dict(position=16,person='A',object=objects[0],time='t_bind',value=True),dict(position=19,person='W',object=objects[1],time='t_bind',value=False)],
        purity=dict(person='A' if candidate['purity']=='ACTOR' else 'W',time='t_bind'),
        actions=[dict(op='TAKE',actor='A',object='R'),dict(op='EXTRACT',actor='A',object='G',source='R',using='NAILS(A)',forbidden='MOUTH(A)'),dict(op='PLACE',actor='A',object='G',destination='C'),dict(op='BIND',actor='A',object='C',destination='NECK(W)'),dict(op='CLAIM',actor='A',recipient='W',condition='Q',content='RELEASE(A,W,Q) BY_GRACE(GOD)',kind='SOURCE_ATTRIBUTED_ONLY')],
        references=dict(R='selected raisins',G='all seed identities from R',C='cloth',A='YOU same person',W='RECIPIENT',Q='source-context quartan reference'),
        reference_macro_cost='chey=P_rite' if objects[0]=='P_rite' else 'chey=P_attach; recipient implicit object=P_purpose; one changed macro value')

def execute(graph, counts, world, intervention='NONE', store_trace=False):
    assert graph['status']=='COMPLETE'
    assert all(isinstance(n,int) and n>=0 for n in counts)
    c=graph['candidate']; actor=world['actor']; recipient=world['recipient']
    assert actor in world['knowledge'] and recipient in world['knowledge']
    seed_groups=[[f'r{i}s{j}' for j in range(n)] for i,n in enumerate(counts)]
    seeds=[s for group in seed_groups for s in group]
    state=dict(raisins={f'r{i}':g.copy() for i,g in enumerate(seed_groups)},taken=False,loose=[],contents=[],bound=None,claims=[])
    trace=[]; errors=[]; first=None
    plan=deepcopy(graph['actions'])
    if intervention=='BIND_BEFORE_PLACE': plan[2],plan[3]=plan[3],plan[2]
    pure=dict(world['purity'])
    if intervention=='PURITY_ONLY_EARLIER': pure={p:False for p in pure}
    for step,a in enumerate(plan,1):
        op=a['op']; local=[]; before=deepcopy(state) if store_trace else None
        if op=='TAKE':
            if not counts: local.append('EMPTY_RAISIN_SET')
            elif c['quantity']=='TOTAL' and len(seeds)!=4: local.append('QUANTITY_TOTAL')
            elif c['quantity']=='EACH' and any(n!=4 for n in counts): local.append('QUANTITY_EACH')
            if not local: state['taken']=True
        elif op=='EXTRACT':
            if not state['taken']: local.append('NOT_TAKEN')
            if intervention=='MOUTH': local.append('MOUTH_PROHIBITED_BY_INSTRUCTION')
            if not local:
                state['loose']=seeds.copy()
                state['raisins']={r:[] for r in state['raisins']}
        elif op=='PLACE':
            attempted=seeds.copy()
            if intervention=='SUBSTITUTE_SEEDS': attempted=[f'new{i}' for i in range(len(seeds))]
            if intervention=='DROP_SEED': attempted=attempted[:-1]
            if intervention=='EXTRA_SEED': attempted.append('new_extra')
            if set(attempted)!=set(seeds) or set(state['loose'])!=set(seeds): local.append('SEED_IDENTITIES')
            if not local: state['contents']=attempted; state['loose']=[]
        elif op=='BIND':
            if set(state['contents'])!=set(seeds) or not state['taken']: local.append('BIND_CONTENTS')
            for assertion in graph['knowledge']:
                person=actor if assertion['person']=='A' else recipient
                if world['knowledge'][person][assertion['object']]!=assertion['value']:
                    local.append('ACTOR_KNOWLEDGE' if assertion['person']=='A' else 'RECIPIENT_IGNORANCE')
            person=actor if graph['purity']['person']=='A' else recipient
            if not pure[person]: local.append('PURITY_AT_BIND')
            if not local: state['bound']=f'NECK({recipient})'
        elif op=='CLAIM':
            if state['bound']!=f'NECK({recipient})': local.append('NOT_BOUND')
            if not local: state['claims'].append(dict(actor=actor,recipient=recipient,condition='Q',grace='GOD',status='SOURCE_ATTRIBUTED_ONLY'))
        else: raise ValueError(op)
        if store_trace: trace.append(dict(step=step,operation=a,before=before,violations=local,after=deepcopy(state)))
        if local: errors=local; first=step; break
    return dict(coherent=not errors,first_failure_step=first,first_violations=errors,completed_actions=(first-1 if first else len(plan)),unexecuted=[a['op'] for a in plan[first:]] if first else [],trace=trace,final=state)

"""Separate flat reverse coverage and declarative fact/set validation; same author."""
from itertools import product

def compile_reverse(lines, lex, c):
    forms=sum((x['words'] for x in lines),[])
    if any(w not in lex for w in forms): return 'UNBOUND_FORMS'
    tags=[lex[w]['tag'] for w in forms]
    expected=[
        ('PURE','BEING','WHILE','ATTRIBUTED_CLAIM','BY_GRACE','YOU','RELEASE','GOD'),
        ('THE','GRAPE_SEEDS','PLACE','CLOTH','IN','NECK','ON','BIND'),
        ('KNOWS','THIS_RITE','YOU','KNOWS','RECIPIENT','NOT'),
        ('EXTRACT','YOU','FINGERNAILS','USING','THE','GRAPE_SEEDS','NOT_USING','MOUTH'),
        ('TAKE','RAISINS','FOUR','THE','GRAPE_SEEDS','CONTAINING','THEREFORE')]
    for clause in expected:
        if tuple(tags[-len(clause):])!=clause: return 'GRAMMAR_CONTRADICTION'
        del tags[-len(clause):]
    return 'COMPLETE' if not tags else 'GRAMMAR_CONTRADICTION'

def fact_violations(c, counts, w, intervention='NONE'):
    errors=[]
    if not counts: errors.append('EMPTY_RAISIN_SET')
    elif c['quantity']=='TOTAL' and sum(counts)!=4: errors.append('QUANTITY_TOTAL')
    elif c['quantity']=='EACH' and set(counts)!={4}: errors.append('QUANTITY_EACH')
    a=w['actor']; r=w['recipient']
    pa,pr=('P_rite','P_rite') if c['knowledge']=='SAME_OBJECT' else ('P_attach','P_purpose')
    if w['knowledge'][a][pa] is not True: errors.append('ACTOR_KNOWLEDGE')
    if w['knowledge'][r][pr] is not False: errors.append('RECIPIENT_IGNORANCE')
    p=a if c['purity']=='ACTOR' else r
    if not w['purity'][p] or intervention=='PURITY_ONLY_EARLIER': errors.append('PURITY_AT_BIND')
    if intervention=='MOUTH': errors.append('MOUTH_PROHIBITED_BY_INSTRUCTION')
    if intervention in ['SUBSTITUTE_SEEDS','DROP_SEED','EXTRA_SEED']: errors.append('SEED_IDENTITIES')
    if intervention=='BIND_BEFORE_PLACE': errors.append('BIND_CONTENTS')
    return errors

def independent_worlds():
    result=[]
    for count in [2,1]:
        ps=['A','W'][:count]
        for k in product([False,True], repeat=count*3):
            for p in product([False,True], repeat=count):
                result.append(dict(id=f'W{len(result):03}',actor='A',recipient=ps[-1],knowledge={person:dict(zip(('P_rite','P_attach','P_purpose'),k[3*i:3*i+3])) for i,person in enumerate(ps)},purity=dict(zip(ps,p))))
    return result

def validate_trace(c, counts, w, result, intervention='NONE'):
    # Replay conservation, role identity and attributed-only terminal state from
    # facts, without invoking the main transition function.
    seeds={f'r{i}s{j}' for i,n in enumerate(counts) for j in range(n)}
    reached=[]
    prior=None
    for row in result['trace']:
        if prior is not None: assert row['before']==prior
        prior=row['after']; op=row['operation']['op']
        if row['violations']: assert row['before']==row['after']; break
        reached.append(op)
        if op=='TAKE': assert prior['taken'] and set().union(*map(set,prior['raisins'].values()))==seeds
        elif op=='EXTRACT': assert set(prior['loose'])==seeds and all(not x for x in prior['raisins'].values())
        elif op=='PLACE': assert set(prior['contents'])==seeds and not prior['loose']
        elif op=='BIND': assert prior['bound']==f"NECK({w['recipient']})" and set(prior['contents'])==seeds
        elif op=='CLAIM': assert prior['claims']==[dict(actor=w['actor'],recipient=w['recipient'],condition='Q',grace='GOD',status='SOURCE_ATTRIBUTED_ONLY')]
        assert set(prior)=={'raisins','taken','loose','contents','bound','claims'}
    assert result['coherent']==(not fact_violations(c,counts,w,intervention))
    if result['coherent']: assert reached==['TAKE','EXTRACT','PLACE','BIND','CLAIM']
    return True

#!/usr/bin/env python3
"""Independent carry-free unbounded-integer source-bag encoding."""
import itertools,time
from collections import Counter,defaultdict
import z3
def solve(groups,W,signs,limits):
    start=time.monotonic();stats={'preparation_seconds':0.0,'solve_seconds':0.0}
    def stopped(reason):
        stats['preparation_seconds']=time.monotonic()-start
        return {'status':'UNKNOWN','reason':reason,'stats':stats.copy()}
    def expired():return time.monotonic()-start>limits['preparation_seconds']
    assert signs and len(signs)==len(set(signs)) and all(u in signs for g in groups for u in g)
    assert all(isinstance(w,str) for w in W)
    if not groups:
        return {'status':'SAT','key':{c:signs[0] for c in sorted(set(''.join(W)))},'words':[],
                'reason':'VACUOUS_TARGET_SET','stats':stats}
    if not W:return {'status':'UNSAT','reason':'EMPTY_SOURCE_VOCABULARY','stats':stats}
    W=sorted(set(W));alphabet=sorted(set(''.join(W)))
    longest=max(max(map(len,W),default=0),max(map(len,groups),default=0));base=max(2,longest+1)
    powers=[base**i for i in range(len(signs))];value=dict(zip(signs,powers))
    stats.update(base=base,maximum_word_length=longest,source_characters=len(alphabet),unit_values=len(signs))
    f={c:z3.Int('letter_'+str(i)) for i,c in enumerate(alphabet)};solver=z3.Solver()
    for v in f.values():
        if expired():return stopped('PREPARATION_CAP')
        solver.add(z3.Or([v==power for power in powers]))
    profiles=defaultdict(set)
    for w in W:
        if expired():return stopped('PREPARATION_CAP')
        profiles[len(w)].add(tuple(sorted(Counter(w).items())))
    expressions={}
    lengths={len(g) for g in groups}
    for n in sorted(lengths):
        expressions[n]=[]
        for profile in sorted(profiles[n]):
            if expired():return stopped('PREPARATION_CAP')
            expressions[n].append(z3.Sum([count*f[c] for c,count in profile]))
    bags=sorted({tuple(sorted(Counter(g).items())) for g in groups})
    equalities=0
    for bag in bags:
        if expired():return stopped('PREPARATION_CAP')
        n=sum(count for u,count in bag)
        if not expressions[n]:
            stats['preparation_seconds']=time.monotonic()-start
            return {'status':'UNSAT','reason':'MISSING_SOURCE_WORD_LENGTH','stats':stats.copy()}
        target=sum(count*value[u] for u,count in bag)
        solver.add(z3.Or([expr==target for expr in expressions[n]]));equalities+=len(expressions[n])
    if expired():return stopped('PREPARATION_CAP')
    stats.update(preparation_seconds=time.monotonic()-start,distinct_target_bags=len(bags),candidate_equalities=equalities)
    solver.set(timeout=int(1000*limits['solver_seconds']));before=time.monotonic();answer=solver.check();stats['solve_seconds']=time.monotonic()-before
    if answer==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown(),'stats':stats}
    if answer==z3.unsat:return {'status':'UNSAT','reason':'EXHAUSTIVE_INTEGER_PACKED_EQUALITIES','stats':stats}
    model=solver.model();inverse=dict(zip(powers,signs));key={c:inverse[model.eval(v).as_long()] for c,v in f.items()}
    index=defaultdict(list)
    for w in W:index[tuple(sorted(Counter(key[c] for c in w).items()))].append(w)
    words=[index[tuple(sorted(Counter(g).items()))][0] for g in groups]
    assert all(Counter(key[c] for c in w)==Counter(g) for w,g in zip(words,groups))
    return {'status':'SAT','key':key,'words':words,'stats':stats}
def fixtures():
    checked=0;limits={'preparation_seconds':5,'solver_seconds':5}
    banks=[['a'],['a','b'],['aa'],['ab'],['aa','ab'],['a','ab'],['aa','bb'],['a','b','ab']]
    targets=[[['x']],[['y']],[['x','x']],[['x','y']],[['x'],['y']]]
    for W in banks:
        letters=sorted(set(''.join(W)))
        for groups in targets:
            possible=False
            for values in itertools.product('xy',repeat=len(letters)):
                k=dict(zip(letters,values));bags=[Counter(k[c] for c in w) for w in W]
                if all(Counter(g) in bags for g in groups):possible=True;break
            r=solve(groups,W,list('xy'),limits);assert r['status']==('SAT' if possible else 'UNSAT');checked+=1
    assert solve([list('xxx')],['abc'],list('xyz'),limits)['status']=='SAT'
    assert solve([list('xyz')],['aaa'],list('xyz'),limits)['status']=='UNSAT'
    assert solve([list('zyx')],['abc'],list('xyz'),limits)['status']=='SAT'
    assert solve([list('xy')],['a'],list('xyz'),limits)['status']=='UNSAT'
    assert solve([['x']],[],list('xyz'),limits)['status']=='UNSAT'
    assert solve([],['a'],list('xyz'),limits)['status']=='SAT'
    assert solve([[]],[''],list('xyz'),limits)['status']=='SAT'
    # Under too-small base2, two copies of digit0 would masquerade as digit1.
    assert 2*2**0==2**1 and 2*3**0!=3**1
    r=solve([list('xxx')],['abc'],list('xyz'),limits);assert r['stats']['base']>3
    return {'status':'PASS','complete_function_cases':checked,'named_checks':9,
            'carry_counterexample_checked':True,'mergers_allowed':True,'three_unit_cases':True,
            'encoding':'Unbounded integer powers, base greater than complete word lengths; no bitvector overflow',
            'shared_backend':'Z3; independent formulation, not independent solver engine',
            'prelock_correction':'Empty-target set treated vacuously SAT; one empty word can cover one empty group. Original actual control/native domain remains nonempty and unchanged.'}

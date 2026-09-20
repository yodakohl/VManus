"""GDT993 independent bit replay, copied with one preregistered generalization.
Cargo visibility includes explicit names anywhere in the current clause, as
GDT993 compile_reading and GDT994 binding_error specify. This changes the
prior-cargo list for newly permitted PAIR reference placements; legacy bytes
and all32old outcomes remain unchanged. Source-only stress fixtures bind this.
"""
def replay(parsed,v):
    clause_ends={p['start']:p['end'] for p in parsed}
    names=('M','B','C','G','W');bits={n:1<<i for i,n in enumerate(names)}
    symbols=[s for c in parsed for s in c['symbols']]
    first_positions={n:symbols.index(n) for n in ('W','G','C') if n in symbols}
    cargo=set(first_positions);events=[];hazards=set();references=[];pair=None
    def cargo_ref(word,start,cid):
        if word in cargo:return word
        prior=sorted((x for x in cargo if first_positions[x]<clause_ends[start]),key=first_positions.get)
        if word=='FIRST_CARGO':answer=prior[0] if v['first']=='FIRST' else prior[-1]
        elif word=='OTHER_CARGO':
            if v['other']=='FIRST':answer=prior[0]
            else:
                rest=set(prior)-set(pair);assert len(rest)==1;answer=next(iter(rest))
        else:raise AssertionError(word)
        references.append(dict(clause=cid,symbol=word,value=answer,prior_cargo=prior));return answer
    for n,c in enumerate(parsed,1):
        s=c['symbols'];k=c['kind'];i=c['start'];cid=f'S{n:02d}';r=lambda word:cargo_ref(word,i,cid)
        event=[cid,k,None,None]
        if k=='PAIR':pair=(r(s[0]),r(s[3]));hazards.add(tuple(sorted(pair)))
        elif k=='COPY':
            other=r('OTHER_CARGO');new=(other,pair[1]) if v['copy']=='FIRST' else (pair[0],other);hazards.add(tuple(sorted(new)))
        elif k=='WITH_OUT':event[2:]=['OUT',r(s[3])]
        elif k=='EXCLUDE':event[2:]=[v['exclude'],r(s[1])]
        elif k=='FERRY':event[2:]=['OPPOSITE',r(s[1])]
        elif k=='WITH_RETURN':event[2:]=['RETURN',r(s[1])]
        elif k=='CONVEY':event[2:]=['OUT',r(s[2])]
        elif k=='ALONE':event[2:]=['RETURN',None]
        elif k=='FINAL_TRIP':event[2:]=['OUT',r(s[4])]
        elif k=='RESULT':event[3]=r(s[3])
        events.append(event)
    def bank(state,n):return bool(state&bits[n])
    def positions(state):return {n:('R' if bank(state,n) else 'L') for n in names}
    # Paths carry independent compact state, not mutable position dictionaries.
    paths=[(0,[dict(clause='INITIAL',load=None,positions=positions(0))],None,[],None,None,False,[])]
    for cid,k,mode,arg in events:
        future=[]
        for state,trace,failure,assertions,last,stay,finished,theres in paths:
            if failure is not None:future.append((state,trace,failure,assertions,last,stay,finished,theres));continue
            if mode is not None:
                target=not bank(state,'M') if mode=='OPPOSITE' else mode=='OUT'
                loads=[None]+sorted(x for x in cargo if bank(state,x)==bank(state,'M') and x!=arg) if mode=='EXCLUDING' else [arg]
                for load in loads:
                    errors=[]
                    if finished:errors.append('TRIP_AFTER_FINALLY')
                    if bank(state,'B')!=bank(state,'M'):errors.append('BOAT_NOT_AT_AGENT')
                    if load is not None and bank(state,load)!=bank(state,'M'):errors.append('CARGO_NOT_AT_AGENT')
                    if target==bank(state,'M'):errors.append('NO_INTERBANK_CROSSING')
                    if errors:
                        failure=dict(clause=cid,attempted_load=load,destination='R' if target else 'L',reasons=errors)
                        future.append((state,trace,failure,list(assertions),last,stay,finished,list(theres)));continue
                    toggle=bits['M']|bits['B']|(bits[load] if load else 0);after=state^toggle;checks=list(assertions)
                    if stay is not None and load!=stay[0] and bank(after,stay[0])!=stay[1]:checks.append(dict(clause=cid,reason='STAY_VIOLATED'))
                    future.append((after,trace+[dict(clause=cid,load=load,positions=positions(after))],None,checks,load,None,k=='FINAL_TRIP',list(theres)))
            else:
                checks=list(assertions);there=True if v['there']=='GOAL' else bank(state,'M');locs=list(theres)
                if k=='STAY':
                    if last is None:checks.append(dict(clause=cid,reason='NO_CARGO_FOR_STAY'))
                    else:
                        if bank(state,last)!=there:checks.append(dict(clause=cid,reason='STAY_BANK_FALSE'))
                        stay=(last,there)
                    locs.append(dict(clause=cid,bank='R' if there else 'L'))
                elif k=='RESULT':
                    if last is None or arg not in cargo-{last} or any(bank(state,x)!=bank(state,'M') for x in cargo):checks.append(dict(clause=cid,reason='JOINING_RESULT_FALSE'))
                elif k=='CONCLUSION':
                    if any(bank(state,x)!=there for x in (*cargo,'M')):checks.append(dict(clause=cid,reason='FINAL_LOCAL_ASSERTION_FALSE'))
                    locs.append(dict(clause=cid,bank='R' if there else 'L'))
                future.append((state,trace,None,checks,last,stay,finished,locs))
        paths=future
    output=[]
    for state,trace,failure,assertions,last,stay,finished,theres in paths:
        bad=[dict(after=t['clause'],pair=list(pair),bank=t['positions'][pair[0]]) for t in trace for pair in sorted(hazards) if t['positions'][pair[0]]==t['positions'][pair[1]]!=t['positions']['M']]
        goal=all(bank(state,x) for x in (*cargo,'M')) if failure is None else None
        unsafeless=failure is None and not assertions and goal
        p=dict(positions=positions(state),trace=trace,physical_failure=failure,assertions=assertions,safety_violations=bad,physical_complete=failure is None,goal_reached=goal,without_safety_consistent=unsafeless,consistent=unsafeless and not bad)
        if theres:p['there_references']=theres
        output.append(p)
    return output,[list(p) for p in sorted(hazards)],references

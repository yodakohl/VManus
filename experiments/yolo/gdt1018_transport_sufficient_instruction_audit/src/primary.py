"""Forward all-eligible-prefix evaluator; no fitted choices or world search."""
from common import *
import copy

def evaluate(parsed,variant):
    s=inputs();model=load(s['model'],'compiler993')
    try:program=model.compile_reading(parsed,variant)
    except ValueError as error:return dict(status='INVALID',error=str(error))
    cargo=program['cargo'];hazards=program['hazards'];failures=[];successes=[];choices=[]
    def bad(st):return [list(p) for p in hazards if st[p[0]]==st[p[1]]!=st['M']]
    def failure(cid,reason,trace,**detail):failures.append(dict(clause=cid,reason=reason,trace=trace,**detail))
    def rec(i,st,last,stay,finished,trace):
        if i==len(program['nodes']):
            if all(st[x]=='R' for x in ['M',*cargo]):successes.append(trace)
            else:failure('END','GOAL_UNREACHED',trace,positions=st)
            return
        n=program['nodes'][i];cid=n['clause'];k=n['kind']
        if n.get('op')=='TRIP':
            dst=('R' if st['M']=='L' else 'L') if n['mode']=='OPPOSITE' else ('R' if n['mode']=='OUT' else 'L')
            opened=n['mode']=='EXCLUDING'
            loads=[None]+[c for c in cargo if st[c]==st['M'] and c!=n['load']] if opened else [n['load']]
            permitted=[];excluded=[]
            for load_ in loads:
                reasons=[];after=dict(st)
                if finished:reasons.append('TRIP_AFTER_FINALLY')
                if st['B']!=st['M']:reasons.append('BOAT_NOT_AT_AGENT')
                if load_ is not None and st[load_]!=st['M']:reasons.append('CARGO_NOT_AT_AGENT')
                if dst==st['M']:reasons.append('NO_INTERBANK_CROSSING')
                if not reasons:
                    after['M']=after['B']=dst
                    if load_ is not None:after[load_]=dst
                    if stay is not None and load_!=stay[0] and after[stay[0]]!=stay[1]:reasons.append('STAY_VIOLATED')
                    if bad(after):reasons.append('UNSAFE_STATE')
                step=dict(clause=cid,load=load_,positions=after)
                if reasons:
                    if opened:excluded.append(dict(load=load_,reasons=reasons))
                    else:failure(cid,'FIXED_TRIP_FAILED',trace,attempt=step,reasons=reasons)
                else:permitted.append((load_,after,step))
            if opened:
                choices.append(dict(clause=cid,before=st,eligible=[p[0] for p in permitted],excluded=excluded,prefix=trace))
                if not permitted:failure(cid,'NO_PERMISSIBLE_LOAD',trace,excluded=excluded)
            for load_,after,step in permitted:rec(i+1,after,load_,None,bool(n.get('final')),trace+[step])
            return
        bank='R' if variant['there']=='GOAL' else st['M'];reason=None
        if k=='STAY':
            if last is None:reason='NO_CARGO_FOR_STAY'
            elif st[last]!=bank:reason='STAY_BANK_FALSE'
            else:stay=(last,bank)
        elif k=='RESULT':
            if last is None or n['explicit_cargo'] not in set(cargo)-{last} or len({st[x] for x in ['M',*cargo]})!=1:reason='JOINING_RESULT_FALSE'
        elif k=='CONCLUSION':
            if any(st[x]!=bank for x in ['M',*cargo]):reason='FINAL_LOCAL_ASSERTION_FALSE'
        if reason:failure(cid,reason,trace,positions=st)
        else:rec(i+1,st,last,stay,finished,trace)
    initial={x:'L' for x in ['M','B',*cargo]}
    rec(0,initial,None,None,False,[])
    return dict(status='SUFFICIENT' if not failures and successes else 'INSUFFICIENT',cargo=cargo,hazards=hazards,
                successful_paths=len(successes),failed_prefixes=len(failures),failures=failures,successes=successes,choices=choices)

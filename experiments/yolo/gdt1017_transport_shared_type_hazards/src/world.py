"""Complete Boolean-location world model; no paragraph-length reduction."""
import itertools,z3
CARGO=('W','G','C');REQ=('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION')
def vals(g,t):return g['types'][t[1:]] if t.startswith('@') else [t]
def OR(xs):return z3.Or(xs) if xs else z3.BoolVal(False)
def build(p,lex,g,variant,timeout=20000,fixed_layout=None):
    raw=p['words'];n=len(raw);symbols=sorted(set(lex.values())|{v for pat in g['patterns'].values() for t in pat for v in vals(g,t)});num={v:i for i,v in enumerate(symbols)}
    xs={w:z3.Int('x'+str(i)) for i,w in enumerate(sorted(set(raw)-lex.keys()))};s=z3.Solver();s.set(timeout=timeout)
    for x in xs.values():s.add(x>=0,x<len(symbols))
    v=[z3.IntVal(num[lex[w]]) if w in lex else xs[w] for w in raw]
    named=[OR([x==num[c] for x in v]) for c in CARGO]
    seen=[[z3.Bool('seen'+str(k)+'_'+str(i)) for i in range(n+1)] for k in range(3)]
    first=[z3.Int('first'+str(i)) for i in range(n+1)];recent=[z3.Int('recent'+str(i)) for i in range(n+1)]
    s.add(first[0]==-1,recent[0]==-1)
    for k in range(3):s.add(z3.Not(seen[k][0]))
    for i,x in enumerate(v):
        direct=z3.If(x==num['W'],0,z3.If(x==num['G'],1,z3.If(x==num['C'],2,-1)))
        fresh=OR([z3.And(x==num[name],z3.Not(seen[k][i])) for k,name in enumerate(CARGO)])
        s.add(first[i+1]==z3.If(first[i]>=0,first[i],direct),recent[i+1]==z3.If(fresh,direct,recent[i]))
        for k,name in enumerate(CARGO):s.add(seen[k][i+1]==z3.Or(seen[k][i],x==num[name]))
    agent=[z3.Bool('agent'+str(i)) for i in range(n+1)]
    loc=[[z3.Bool('cargo'+str(k)+'_'+str(i)) for i in range(n+1)] for k in range(3)]
    last=[z3.Int('last'+str(i)) for i in range(n+1)];final=[z3.Bool('final'+str(i)) for i in range(n+1)]
    pa=[z3.Int('pairA'+str(i)) for i in range(n+1)];pb=[z3.Int('pairB'+str(i)) for i in range(n+1)]
    s.add(z3.Not(agent[0]),agent[n],last[0]==-1,z3.Not(final[0]),pa[0]==-1,pb[0]==-1)
    for k in range(3):s.add(z3.Not(loc[k][0]),z3.Implies(named[k],loc[k][n]))
    for xs_ in [last,pa,pb]:
        for x in xs_:s.add(x>=-1,x<3)
    hazards={pair:z3.Bool('hazard'+''.join(map(str,pair))) for pair in itertools.combinations(range(3),2)};causes={pair:[] for pair in hazards}
    edges=[];flags=[]
    allowed_layout=None if fixed_layout is None else {(x['start'],x['end'],x['kind']) for x in fixed_layout}
    for kind,pat in g['patterns'].items():
        for lo in range(n-len(pat)+1):
            hi=lo+len(pat)
            if (lo==0)!=(kind=='INITIAL') or (hi==n)!=(kind=='CONCLUSION'):continue
            if allowed_layout is not None and (lo,hi,kind) not in allowed_layout:continue
            domains=[vals(g,t) for t in pat]
            if any(w in lex and lex[w] not in domains[j] for j,w in enumerate(raw[lo:hi])):continue
            b=z3.Bool('edge'+str(len(edges)));edges.append((lo,hi,kind));flags.append(b)
            cond=[OR([v[lo+j]==num[x] for x in domain]) for j,domain in enumerate(domains)]
            def reference(offset=None,force_other=False):
                x=z3.IntVal(num['OTHER_CARGO']) if force_other else v[lo+offset]
                f=first[hi] if variant['first']=='FIRST' else recent[hi]
                if variant['other']=='FIRST':other=first[hi];other_ok=other>=0
                else:
                    other=3-pa[lo]-pb[lo]
                    other_ok=z3.And(pa[lo]>=0,pb[lo]>=0,pa[lo]!=pb[lo],OR([z3.And(other==k,seen[k][hi]) for k in range(3)]))
                cond.extend([z3.Implies(x==num['FIRST_CARGO'],f>=0),z3.Implies(x==num['OTHER_CARGO'],other_ok)])
                return z3.If(x==num['W'],0,z3.If(x==num['G'],1,z3.If(x==num['C'],2,z3.If(x==num['FIRST_CARGO'],f,other))))
            if kind=='PAIR':
                left=reference(0);right=reference(3);cond.extend([left!=right,pa[hi]==left,pb[hi]==right])
            else:
                cond.extend([pa[hi]==pa[lo],pb[hi]==pb[lo]])
                if kind=='COPY':
                    other=reference(force_other=True);cond.extend([pa[lo]>=0,pb[lo]>=0])
                    left,right=(other,pb[lo]) if variant['copy']=='FIRST' else (pa[lo],other)
                    cond.append(left!=right)
            if kind in ('PAIR','COPY'):
                for (i,j) in hazards:causes[(i,j)].append(z3.And(b,z3.Or(z3.And(left==i,right==j),z3.And(left==j,right==i))))
            trip=kind in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP')
            if trip:
                if kind=='ALONE':load=z3.IntVal(-1)
                elif kind=='EXCLUDE' and variant['exclude']=='EXCLUDING':
                    excluded=reference(1);load=z3.Int('load'+str(len(edges)));cond.extend([load>=-1,load<3,load!=excluded])
                else:load=reference({'WITH_OUT':3,'EXCLUDE':1,'FERRY':1,'WITH_RETURN':1,'CONVEY':2,'FINAL_TRIP':4}[kind])
                dst=z3.Not(agent[lo]) if kind=='FERRY' else z3.BoolVal(kind in ('WITH_OUT','CONVEY','FINAL_TRIP'))
                cond.extend([z3.Not(final[lo]),dst!=agent[lo],agent[hi]==dst,last[hi]==load,final[hi]==z3.BoolVal(kind=='FINAL_TRIP')])
                for k in range(3):cond.extend([z3.Implies(load==k,z3.And(named[k],loc[k][lo]==agent[lo])),loc[k][hi]==z3.If(load==k,dst,loc[k][lo])])
            else:
                cond.extend([agent[hi]==agent[lo],last[hi]==last[lo],final[hi]==final[lo]])
                cond.extend(loc[k][hi]==loc[k][lo] for k in range(3))
                bank=agent[lo] if variant['there']=='CURRENT' else z3.BoolVal(True)
                if kind=='STAY':cond.append(OR([z3.And(last[lo]==k,loc[k][lo]==bank) for k in range(3)]))
                if kind=='RESULT':
                    target=reference(3);cond.extend([last[lo]>=0,target!=last[lo],OR([z3.And(target==k,named[k]) for k in range(3)])])
                    cond.extend(z3.Implies(named[k],loc[k][lo]==agent[lo]) for k in range(3))
                if kind=='CONCLUSION':
                    cond.append(agent[lo]==bank);cond.extend(z3.Implies(named[k],loc[k][lo]==bank) for k in range(3))
            s.add(z3.Implies(b,z3.And(cond)))
    for pos in range(n):s.add(z3.Sum([z3.If(b,1,0) for b,(lo,hi,k) in zip(flags,edges) if lo<=pos<hi])==1)
    for kind in REQ:s.add(z3.Sum([z3.If(b,1,0) for b,(_,_,k) in zip(flags,edges) if k==kind])==1)
    for (i,j),h in hazards.items():
        s.add(h==OR(causes[(i,j)]))
        if (i,j)==(0,1):s.add(z3.Not(h))  # W-G contradicts the fixed original world.
        inherited=z3.And(named[i],named[j]) if 2 in (i,j) else z3.BoolVal(False)
        required=z3.Or(h,inherited)
        for pos in range(n+1):s.add(z3.Implies(required,z3.Not(z3.And(loc[i][pos]==loc[j][pos],loc[i][pos]!=agent[pos]))))
    return dict(solver=s,xs=xs,symbols=symbols,num=num,edges=edges,flags=flags,lexicon=lex,paragraph=p,variant=variant,agent=agent,cargo=loc)

def solve(p,lex,g,variant,timeout=20000,fixed_layout=None):
    built=build(p,lex,g,variant,timeout,fixed_layout);s=built['solver'];answer=str(s.check());out=dict(status=answer)
    if answer=='sat':
        m=s.model();aliases={w:built['symbols'][m.eval(x,model_completion=True).as_long()] for w,x in built['xs'].items()};code={**lex,**aliases}
        selected=sorted(e for e,b in zip(built['edges'],built['flags']) if z3.is_true(m.eval(b,model_completion=True)))
        parsed=[dict(start=lo,end=hi,kind=k,symbols=[code[w] for w in p['words'][lo:hi]]) for lo,hi,k in selected]
        out['witness']=dict(aliases=code,parse=parsed,variant=variant)
    elif answer=='unknown':out['reason']=s.reason_unknown()
    return out

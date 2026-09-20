"""Shared exact code plus Boolean-location whole-world constraints."""
import z3
REQ=('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION');CARGO=('W','G','C')
def vals(g,t):return g['types'][t[1:]] if t.startswith('@') else [t]
def build(ps,lex,g,milliseconds=5000):
    assert sum(len(g['patterns'][k]) for k in REQ)==26
    assert len(g['patterns']['PAIR'])==6 and min(len(g['patterns'][k]) for k in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP'))==2
    assert all(26<=len(p['words'])<38 for p in ps)
    symbols=sorted(set(lex.values())|{v for pat in g['patterns'].values() for t in pat for v in vals(g,t)});num={v:i for i,v in enumerate(symbols)}
    unknown=sorted(set(w for p in ps for w in p['words'])-lex.keys());xs={w:z3.Int('x'+str(i)) for i,w in enumerate(unknown)}
    s=z3.Solver();s.set(timeout=milliseconds)
    for x in xs.values():s.add(x>=0,x<len(symbols))
    other_first=z3.Bool('other_first');there_current=z3.Bool('there_current');meta=[]
    def value(w):return z3.IntVal(num[lex[w]]) if w in lex else xs[w]
    for pi,p in enumerate(ps):
        raw=p['words'];n=len(raw);v=[value(w) for w in raw];tag='p'+str(pi)+'_'
        named=[z3.Or([x==num[c] for x in v]) for c in CARGO]
        a=[z3.Bool(tag+'a'+str(i)) for i in range(n+1)];loc=[[z3.Bool(tag+'c'+str(k)+'_'+str(i)) for i in range(n+1)] for k in range(3)]
        last=[z3.Int(tag+'last'+str(i)) for i in range(n+1)];final=[z3.Bool(tag+'final'+str(i)) for i in range(n+1)];first=[z3.Int(tag+'first'+str(i)) for i in range(n+1)]
        s.add(z3.Not(a[0]),last[0]==-1,z3.Not(final[0]),first[0]==-1,a[n])
        for k in range(3):s.add(z3.Not(loc[k][0]),z3.Implies(named[k],loc[k][n]))
        for i,x in enumerate(v):
            direct=z3.If(x==num['W'],0,z3.If(x==num['G'],1,z3.If(x==num['C'],2,-1)))
            s.add(first[i+1]==z3.If(first[i]>=0,first[i],direct))
        for x in last:s.add(x>=-1,x<3)
        edges=[];flags=[]
        for kind,pat in g['patterns'].items():
            if kind in ('PAIR','COPY'):continue # proved >=38 groups for coherent PAIR; COPY requires PAIR
            width=len(pat)
            for lo in range(n-width+1):
                hi=lo+width
                if (lo==0)!=(kind=='INITIAL') or (hi==n)!=(kind=='CONCLUSION'):continue
                allowed=[vals(g,t) for t in pat]
                if any(w in lex and lex[w] not in allowed[j] for j,w in enumerate(raw[lo:hi])):continue
                b=z3.Bool(tag+'e'+str(len(edges)));edges.append((lo,hi,kind));flags.append(b)
                conditions=[z3.Or([v[lo+j]==num[t] for t in vs]) for j,vs in enumerate(allowed)]
                def ref(offset):
                    x=v[lo+offset];r=z3.If(x==num['W'],0,z3.If(x==num['G'],1,z3.If(x==num['C'],2,first[hi])))
                    conditions.append(z3.Implies(x==num['FIRST_CARGO'],first[hi]>=0))
                    conditions.append(z3.Implies(x==num['OTHER_CARGO'],z3.And(other_first,first[hi]>=0)))
                    return r
                trip=kind in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP')
                if trip:
                    if kind=='ALONE':load=z3.IntVal(-1)
                    elif kind=='EXCLUDE':
                        excluded=ref(1);load=z3.Int(tag+'load'+str(len(edges)))
                        conditions.extend([load>=-1,load<3,load!=excluded])
                    else:load=ref({'WITH_OUT':3,'FERRY':1,'WITH_RETURN':1,'CONVEY':2,'FINAL_TRIP':4}[kind])
                    dst=z3.Not(a[lo]) if kind=='FERRY' else z3.BoolVal(kind in ('WITH_OUT','CONVEY','FINAL_TRIP'))
                    conditions.extend([z3.Not(final[lo]),dst!=a[lo],a[hi]==dst,last[hi]==load,final[hi]==z3.BoolVal(kind=='FINAL_TRIP')])
                    for k in range(3):conditions.extend([z3.Implies(load==k,z3.And(named[k],loc[k][lo]==a[lo])),loc[k][hi]==z3.If(load==k,dst,loc[k][lo])])
                else:
                    conditions.extend([a[hi]==a[lo],last[hi]==last[lo],final[hi]==final[lo]])
                    conditions.extend(loc[k][hi]==loc[k][lo] for k in range(3))
                    if kind=='STAY':
                        bank=z3.If(there_current,a[lo],z3.BoolVal(True));conditions.append(z3.Or([z3.And(last[lo]==k,loc[k][lo]==bank) for k in range(3)]))
                    if kind=='RESULT':
                        cargo=ref(3);conditions.extend([last[lo]>=0,cargo!=last[lo],z3.Or([z3.And(cargo==k,named[k]) for k in range(3)])])
                        conditions.extend(z3.Implies(named[k],loc[k][lo]==a[lo]) for k in range(3))
                    if kind=='CONCLUSION':
                        bank=z3.If(there_current,a[lo],z3.BoolVal(True));conditions.append(a[lo]==bank)
                        conditions.extend(z3.Implies(named[k],loc[k][lo]==bank) for k in range(3))
                s.add(z3.Implies(b,z3.And(conditions)))
        for pos in range(n):s.add(z3.Sum([z3.If(b,1,0) for b,(lo,hi,k) in zip(flags,edges) if lo<=pos<hi])==1)
        for k in REQ:s.add(z3.Sum([z3.If(b,1,0) for b,(_,_,kind) in zip(flags,edges) if k==kind])==1)
        meta.append(dict(edges=edges,flags=flags,agent=a,cargo=loc,last=last,first=first,final=final))
    return dict(solver=s,symbols=symbols,num=num,xs=xs,other_first=other_first,there_current=there_current,meta=meta,paragraphs=ps,lexicon=lex)

def witness(built):
    m=built['solver'].model();aliases={w:built['symbols'][m.eval(x,model_completion=True).as_long()] for w,x in built['xs'].items()};full={**built['lexicon'],**aliases};parsed=[]
    for p,meta in zip(built['paragraphs'],built['meta']):
        es=sorted(e for e,b in zip(meta['edges'],meta['flags']) if z3.is_true(m.eval(b,model_completion=True)))
        parsed.append([dict(start=lo,end=hi,kind=k,symbols=[full[w] for w in p['words'][lo:hi]]) for lo,hi,k in es])
    variant=dict(exclude='EXCLUDING',first='FIRST',other='FIRST' if z3.is_true(m.eval(built['other_first'],model_completion=True)) else 'OTHER',there='CURRENT' if z3.is_true(m.eval(built['there_current'],model_completion=True)) else 'GOAL',copy='FIRST')
    return dict(aliases=aliases,parses=parsed,variant=variant)

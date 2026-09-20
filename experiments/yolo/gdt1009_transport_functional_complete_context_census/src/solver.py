"""Exact shared-alias, whole-position clause coverage encoding."""
import z3
REQ=('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION')
def values(g,slot):return g['types'][slot[1:]] if slot.startswith('@') else [slot]
def solve(paragraphs,lex,g,timeout=20000,witness_limit=2,family="FUNCTIONAL"):
    terminals=sorted(set(lex.values())|{v for p in g['patterns'].values() for t in p for v in values(g,t)})
    num={v:i for i,v in enumerate(terminals)};unknown=sorted(set(w for p in paragraphs for w in p['words'])-lex.keys())
    xs={w:z3.Int('x'+str(i)) for i,w in enumerate(unknown)};s=z3.Solver();s.set(timeout=timeout)
    for x in xs.values():s.add(x>=0,x<len(terminals))
    assert family in ("FUNCTIONAL","BIJECTIVE")
    if family=="BIJECTIVE":s.add(z3.Distinct([xs[w] if w in xs else z3.IntVal(num[lex[w]]) for w in sorted(set(paragraphs[0]["words"]))]))
    edges=[];flags=[]
    for pi,p in enumerate(paragraphs):
        raw=p['words'];es=[];bs=[]
        for kind,pattern in g['patterns'].items():
            for lo in range(len(raw)-len(pattern)+1):
                hi=lo+len(pattern)
                if (lo==0)!=(kind=='INITIAL') or (hi==len(raw))!=(kind=='CONCLUSION'):continue
                vs=[values(g,t) for t in pattern]
                if any(w in lex and lex[w] not in vs[j] for j,w in enumerate(raw[lo:hi])):continue
                b=z3.Bool('e'+str(pi)+'_'+str(len(es)));es.append((lo,hi,kind));bs.append(b)
                for j,w in enumerate(raw[lo:hi]):
                    if w in xs:s.add(z3.Implies(b,z3.Or([xs[w]==num[v] for v in vs[j]])))
        for pos in range(len(raw)):s.add(z3.Sum([z3.If(b,1,0) for b,(lo,hi,_) in zip(bs,es) if lo<=pos<hi])==1)
        for k in (g["patterns"] if pi==0 else REQ):s.add(z3.Sum([z3.If(b,1,0) for b,(_,_,kind) in zip(bs,es) if k==kind])==(1+int(pi==0 and k=="THEN")))
        edges.append(es);flags.append(bs)
    witnesses=[];queries=[];exhaustive=False
    while len(witnesses)<witness_limit:
        answer=str(s.check());queries.append(answer)
        if answer!='sat':exhaustive=answer=='unsat';break
        m=s.model();aliases={w:terminals[m.eval(x,model_completion=True).as_long()] for w,x in xs.items()};full={**lex,**aliases};parses=[];selected=[]
        for p,es,bs in zip(paragraphs,edges,flags):
            chosen=[(lo,hi,k,b) for (lo,hi,k),b in zip(es,bs) if z3.is_true(m.eval(b,model_completion=True))];chosen.sort()
            parses.append([dict(start=lo,end=hi,kind=k,symbols=[full[w] for w in p['words'][lo:hi]]) for lo,hi,k,b in chosen]);selected.extend(b for lo,hi,k,b in chosen)
        witnesses.append(dict(aliases=aliases,parses=parses));s.add(z3.Or([x!=num[aliases[w]] for w,x in xs.items()]+[z3.Not(b) for b in selected]))
    return dict(status='SAT' if witnesses else 'UNSAT' if exhaustive else 'UNKNOWN',queries=queries,exhaustive=exhaustive,witnesses=witnesses,code_ambiguity='MULTIPLE_ASSIGNMENTS_OR_PARSES' if len(witnesses)>1 else 'ONE_EXHAUSTIVE_WITHIN_MODEL' if witnesses and exhaustive else 'ALTERNATIVES_UNRESOLVED' if witnesses else 'NO_WITNESS')

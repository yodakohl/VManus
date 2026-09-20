"""All complete clause permutations and unfixed whole-word values, Z3 coverage."""
import collections,z3

def build(raw,g,family,pinned=None,timeout=2000):
    symbols=sorted({v for p in g['patterns'].values() for t in p for v in (g['types'][t[1:]] if t.startswith('@') else [t])});num={v:i for i,v in enumerate(symbols)}
    words=sorted(set(raw));xs={w:z3.Int('word'+str(i)) for i,w in enumerate(words)};s=z3.Solver();s.set(timeout=timeout)
    variant=z3.Int('meaning_variant');s.add(variant>=0,variant<32)
    for w,x in xs.items():
        s.add(x>=0,x<len(symbols))
        if pinned is not None:s.add(x==num[pinned[w]])
    if family=='BIJECTIVE':s.add(z3.Distinct(list(xs.values())))
    else:assert family=='FUNCTIONAL'
    es=[];flags=[]
    for kind,pattern in g['patterns'].items():
        for lo in range(len(raw)-len(pattern)+1):
            hi=lo+len(pattern)
            if (lo==0)!=(kind=='INITIAL') or (hi==len(raw))!=(kind=='CONCLUSION'):continue
            allowed=[g['types'][t[1:]] if t.startswith('@') else [t] for t in pattern]
            b=z3.Bool('edge'+str(len(es)));es.append((lo,hi,kind));flags.append(b)
            for j,w in enumerate(raw[lo:hi]):s.add(z3.Implies(b,z3.Or([xs[w]==num[v] for v in allowed[j]])))
    for pos in range(len(raw)):s.add(z3.Sum([z3.If(b,1,0) for b,(lo,hi,k) in zip(flags,es) if lo<=pos<hi])==1)
    for k in g['patterns']:s.add(z3.Sum([z3.If(b,1,0) for b,(_,_,kind) in zip(flags,es) if kind==k])==(2 if k=='THEN' else 1))
    return dict(solver=s,words=words,xs=xs,num=num,symbols=symbols,edges=es,flags=flags,raw=raw,family=family,variant=variant)

def extract(b):
    m=b['solver'].model();code={w:b['symbols'][m.eval(x).as_long()] for w,x in b['xs'].items()}
    selected=sorted(e for e,f in zip(b['edges'],b['flags']) if z3.is_true(m.eval(f,model_completion=True)))
    parsed=[dict(start=lo,end=hi,kind=k,symbols=[code[w] for w in b['raw'][lo:hi]]) for lo,hi,k in selected]
    return dict(code=code,parse=parsed,solver_variant=m.eval(b['variant'],model_completion=True).as_long())

def block_exact(b,w):
    selected={(p['start'],p['end'],p['kind']) for p in w['parse']}
    b['solver'].add(z3.Or([x!=b['num'][w['code'][word]] for word,x in b['xs'].items()]+[z3.Not(flag) for e,flag in zip(b['edges'],b['flags']) if e in selected]))

def block_projection(b,values,variant_index=None):
    choices=[b['xs'][w]!=b['num'][v] for w,v in values.items()]
    if variant_index is not None:choices.append(b['variant']!=variant_index)
    b['solver'].add(z3.Or(choices))

def ground(w,raw,g,family):
    assert set(w['code'])==set(raw)
    symbols={v for p in g['patterns'].values() for t in p for v in (g['types'][t[1:]] if t.startswith('@') else [t])}
    assert set(w['code'].values())<=symbols
    if family=='BIJECTIVE':assert len(set(w['code'].values()))==len(w['code'])
    cursor=0
    for p in w['parse']:
        assert p['start']==cursor and p['end']==cursor+len(g['patterns'][p['kind']]);cursor=p['end']
        assert p['symbols']==[w['code'][t] for t in raw[p['start']:p['end']]]
        assert all(v in g['types'][t[1:]] if t.startswith('@') else v==t for v,t in zip(p['symbols'],g['patterns'][p['kind']]))
    assert cursor==len(raw) and w['parse'][0]['kind']=='INITIAL' and w['parse'][-1]['kind']=='CONCLUSION'
    assert collections.Counter(p['kind'] for p in w['parse'])==collections.Counter({k:2 if k=='THEN' else 1 for k in g['patterns']})

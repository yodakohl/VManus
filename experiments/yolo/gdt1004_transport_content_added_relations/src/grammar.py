"""Exact shared-alias, whole-position clause coverage encoding."""
import z3
REQ=('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION')
def values(g,slot):return g['types'][slot[1:]] if slot.startswith('@') else [slot]
def build(paragraphs,lex,g,timeout=5000):
    terminals=sorted(set(lex.values())|{v for p in g['patterns'].values() for t in p for v in values(g,t)})
    num={v:i for i,v in enumerate(terminals)};unknown=sorted(set(w for p in paragraphs for w in p['words'])-lex.keys())
    xs={w:z3.Int('x'+str(i)) for i,w in enumerate(unknown)};s=z3.Solver();s.set(timeout=timeout)
    for x in xs.values():s.add(x>=0,x<len(terminals))
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
        for k in REQ:s.add(z3.Sum([z3.If(b,1,0) for b,(_,_,kind) in zip(bs,es) if k==kind])==1)
        edges.append(es);flags.append(bs)
    return dict(solver=s,xs=xs,num=num,terminals=terminals,edges=edges,flags=flags)

"""Independent trimmed-word enumeration and unary-function formulation."""
import collections
from cvc5 import pythonic as c

def relations_independent(words):
    vocab={w for w in words if w and all('a'<=x<='z' for x in w)};d=collections.defaultdict(set)
    for whole in vocab:
        for n in (1,2,3):
            if len(whole)<=n:continue
            base=whole[n:]
            if base in vocab:d[('L',whole[:n])].add((base,whole))
            base=whole[:-n]
            if base in vocab:d[('R',whole[-n:])].add((base,whole))
    return [dict(side=k[0],affix=k[1],pairs=[list(p) for p in sorted(v)]) for k,v in sorted(d.items()) if len(v)>1]

def constrain(solver,raw,lex,xs,code):
    for group in relations_independent(set(raw)|set(lex)):
        f=c.Function('wrapper_'+group['side']+'_'+group['affix'],c.IntSort(),c.IntSort())
        def value(w):return c.IntVal(code[lex[w]]) if w in lex else xs[w]
        for a,b in group['pairs']:solver.add(f(value(a))==value(b))

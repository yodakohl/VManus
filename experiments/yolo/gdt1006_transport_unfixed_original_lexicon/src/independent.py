"""Independent cvc5 boundary-flow encoding with exact content inventory."""
from cvc5 import pythonic as c
import cvc5

def build(raw,g,family,pinned=None,timeout=30000):
    values=set()
    for pat in g['patterns'].values():
        for t in pat:values.update(g['types'][t[1:]] if t.startswith('@') else [t])
    alphabet=sorted(values);number={a:i for i,a in enumerate(alphabet)};xs={w:c.Int('v'+str(i)) for i,w in enumerate(sorted(set(raw)))}
    s=c.Solver();s.set('tlimit-per',timeout)
    variant=c.Int('meaning_variant');s.add(variant>=0,variant<32)
    for w,x in xs.items():
        s.add(x>=0,x<len(alphabet))
        if pinned is not None:s.add(x==number[pinned[w]])
    if family=='BIJECTIVE':s.add(c.Distinct(*xs.values()))
    else:assert family=='FUNCTIONAL'
    incoming=[[] for _ in range(len(raw)+1)];outgoing=[[] for _ in incoming];kinds={k:[] for k in g['patterns']};edges={}
    total=lambda a:sum(a,c.IntVal(0))
    for lo in range(len(raw)):
        for kind,pat in g['patterns'].items():
            hi=lo+len(pat)
            if hi>len(raw) or (lo==0 and kind!='INITIAL') or (kind=='INITIAL' and lo!=0) or (hi==len(raw) and kind!='CONCLUSION') or (kind=='CONCLUSION' and hi!=len(raw)):continue
            b=c.Bool(str(lo)+'_'+kind);edges[(lo,hi,kind)]=b;weight=c.If(b,1,0);outgoing[lo].append(weight);incoming[hi].append(weight);kinds[kind].append(weight)
            for j,t in enumerate(pat):
                choices=[xs[raw[lo+j]]==number[v] for v in (g['types'][t[1:]] if t.startswith('@') else [t])]
                s.add(c.Implies(b,choices[0] if len(choices)==1 else c.Or(*choices)))
    s.add(total(outgoing[0])==1,total(incoming[-1])==1)
    for i in range(1,len(raw)):s.add(total(incoming[i])==total(outgoing[i]),total(incoming[i])<=1)
    for k,flags in kinds.items():s.add(total(flags)==(1+int(k=='THEN')))
    return dict(solver=s,xs=xs,num=number,edges=edges,variant=variant)

def block_exact(b,w):
    alternatives=[b['xs'][word]!=b['num'][value] for word,value in w['code'].items()]
    alternatives.extend(c.Not(b['edges'][(p['start'],p['end'],p['kind'])]) for p in w['parse']);b['solver'].add(c.Or(*alternatives))

def block_projection(b,values,variant_index=None):
    choices=[b['xs'][w]!=b['num'][v] for w,v in values.items()]
    if variant_index is not None:choices.append(b['variant']!=variant_index)
    b['solver'].add(c.Or(*choices))

"""Independent cvc5 boundary-flow existence encoding; no primary solver import."""
import json,sys
from cvc5 import pythonic as c
import cvc5

def check(ps,lex,g,timeout=20000,blocked=None,family="FUNCTIONAL",blocked_layouts=None):
    alphabet=set(lex.values())
    for pat in g['patterns'].values():
        for t in pat:alphabet.update(g['types'][t[1:]] if t.startswith('@') else [t])
    alphabet=sorted(alphabet);n={a:i for i,a in enumerate(alphabet)}
    words=set()
    for p in ps:words.update(p['words'])
    vs={w:c.Int('a'+str(i)) for i,w in enumerate(sorted(words-lex.keys()))}
    s=c.Solver();s.set('tlimit-per',timeout);edge_variables={}
    for x in vs.values():s.add(x>=0,x<len(alphabet))
    assert family in ("FUNCTIONAL","BIJECTIVE")
    if family=="BIJECTIVE":s.add(c.Distinct(*[vs[w] if w in vs else c.IntVal(n[lex[w]]) for w in sorted(set(ps[0]["words"]))]))
    def total(xs):return sum(xs,c.IntVal(0))
    for pi,p in enumerate(ps):
        raw=p['words'];incoming=[[] for _ in range(len(raw)+1)];outgoing=[[] for _ in incoming];kinds={k:[] for k in g['patterns']}
        for start in range(len(raw)):
            for kind,pat in g['patterns'].items():
                end=start+len(pat)
                if end>len(raw) or (start==0 and kind!='INITIAL') or (kind=='INITIAL' and start!=0) or (end==len(raw) and kind!='CONCLUSION') or (kind=='CONCLUSION' and end!=len(raw)):continue
                allowed=[g['types'][t[1:]] if t.startswith('@') else [t] for t in pat]
                if any(w in lex and lex[w] not in allowed[j] for j,w in enumerate(raw[start:end])):continue
                b=c.Bool('p'+str(pi)+'_'+str(start)+'_'+kind);edge_variables[(pi,start,end,kind)]=b;q=c.If(b,1,0);outgoing[start].append(q);incoming[end].append(q);kinds[kind].append(q)
                for j,w in enumerate(raw[start:end]):
                    if w not in lex:
                        choices=[vs[w]==n[v] for v in allowed[j]]
                        s.add(c.Implies(b,choices[0] if len(choices)==1 else c.Or(*choices)))
        s.add(total(outgoing[0])==1,total(incoming[-1])==1)
        for pos in range(1,len(raw)):s.add(total(incoming[pos])==total(outgoing[pos]),total(incoming[pos])<=1)
        for k in (g['patterns'] if pi==0 else ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION')):s.add(total(kinds[k])==(1+int(pi==0 and k=='THEN')))
    for layout in blocked_layouts or []:
        keys=[(0,node['start'],node['end'],node['kind']) for node in layout]
        if any(key not in edge_variables for key in keys):continue
        chosen=[edge_variables[key] for key in keys]
        s.add(c.Or(*[c.Not(b) for b in chosen]))
    if blocked:
        disj=[vs[w]!=n[v] for w,v in blocked['aliases'].items()]
        disj += [c.Not(edge_variables[(pi,node['start'],node['end'],node['kind'])]) for pi,parsed in enumerate(blocked['parses']) for node in parsed]
        s.add(disj[0] if len(disj)==1 else c.Or(*disj))
    return dict(status=str(s.check()),solver='cvc5',version=cvc5.__version__)
if __name__=='__main__':
    job=json.load(sys.stdin);print(json.dumps(check(job['paragraphs'],job['lexicon'],job['grammar'],job.get('timeout',20000),job.get('blocked'))))

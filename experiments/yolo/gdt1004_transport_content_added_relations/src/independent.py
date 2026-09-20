"""Independent cvc5 boundary-flow existence encoding; no primary solver import."""
import json,sys
from cvc5 import pythonic as c
import cvc5

def build(ps,lex,g,timeout=5000):
    alphabet=set(lex.values())
    for pat in g['patterns'].values():
        for t in pat:alphabet.update(g['types'][t[1:]] if t.startswith('@') else [t])
    alphabet=sorted(alphabet);n={a:i for i,a in enumerate(alphabet)}
    words=set()
    for p in ps:words.update(p['words'])
    vs={w:c.Int('a'+str(i)) for i,w in enumerate(sorted(words-lex.keys()))}
    s=c.Solver();s.set('tlimit-per',timeout);edge_variables={}
    for x in vs.values():s.add(x>=0,x<len(alphabet))
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
        for k in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'):s.add(total(kinds[k])==1)
    return s,vs,n

def run(job):
    import time
    started=time.monotonic();s,xs,num=build(job['paragraphs'],job['lexicon'],job['grammar'],job.get('timeout',5000));out=[]
    for q in job['queries']:
        s.push()
        for w,v in ({q['word']:q['value']} if 'word' in q else q.get('values',{})).items():s.add(xs[w]==num[v])
        for values in q.get('blocked_tuples',[]):s.add(c.Or(*[xs[w]!=num[v] for w,v in values.items()]))
        remaining=job.get('worker_seconds',600)-(time.monotonic()-started)
        if remaining<=0:status='unknown_batch_limit'
        else:s.set('tlimit-per',max(1,min(job.get('timeout',5000),int(remaining*1000))));status=str(s.check())
        out.append(dict(id=q['id'],status=status));s.pop()
    return dict(solver='cvc5',version=cvc5.__version__,queries=out)
if __name__=='__main__':print(json.dumps(run(json.load(sys.stdin))))

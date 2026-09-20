"""Independent cvc5 integer-bank, explicit-boat, pending-STAY flow encoding."""
import json,sys,time
from cvc5 import pythonic as c
import cvc5
CARGOS=('W','G','C')
def OR(xs):return c.BoolVal(False) if not xs else xs[0] if len(xs)==1 else c.Or(*xs)
def AND(xs):return c.BoolVal(True) if not xs else xs[0] if len(xs)==1 else c.And(*xs)
def SUM(xs):return sum(xs,c.IntVal(0))
def build(ps,lex,g,timeout=5000):
    mandatory=['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'];assert sum(map(len,[g['patterns'][k] for k in mandatory]))==26
    assert all(26<=len(p['words'])<38 for p in ps) and len(g['patterns']['PAIR'])==6
    alphabet=set(lex.values())
    for pat in g['patterns'].values():
        for t in pat:alphabet.update(g['types'][t[1:]] if t.startswith('@') else [t])
    alphabet=sorted(alphabet);code={a:i for i,a in enumerate(alphabet)};new=sorted(set(w for p in ps for w in p['words'])-lex.keys());xs={w:c.Int('word'+str(i)) for i,w in enumerate(new)}
    solver=c.Solver();solver.set('tlimit-per',timeout)
    for x in xs.values():solver.add(x>=0,x<len(alphabet))
    other=c.Int('other_first');there=c.Int('there_current');solver.add(other>=0,other<=1,there>=0,there<=1)
    for pi,p in enumerate(ps):
        raw=p['words'];n=len(raw);tag='row'+str(pi)+'_';value=[c.IntVal(code[lex[w]]) if w in lex else xs[w] for w in raw]
        named=[OR([x==code[name] for x in value]) for name in CARGOS]
        state=[[c.Int(tag+'loc'+str(obj)+'_'+str(i)) for i in range(n+1)] for obj in range(5)] # agent, boat, W,G,C
        last=[c.Int(tag+'last'+str(i)) for i in range(n+1)];final=[c.Int(tag+'final'+str(i)) for i in range(n+1)];stay=[c.Int(tag+'stay'+str(i)) for i in range(n+1)];staybank=[c.Int(tag+'staybank'+str(i)) for i in range(n+1)]
        for obj in state:
            solver.add(obj[0]==0)
            for x in obj:solver.add(x>=0,x<=1)
        for i in range(n+1):solver.add(last[i]>=-1,last[i]<=2,stay[i]>=-1,stay[i]<=2,final[i]>=0,final[i]<=1,staybank[i]>=0,staybank[i]<=1)
        solver.add(last[0]==-1,stay[0]==-1,final[0]==0,state[0][n]==1)
        for k in range(3):solver.add(c.Implies(named[k],state[k+2][n]==1))
        first=[]
        for stop in range(n+1):
            term=c.IntVal(-1)
            for x in reversed(value[:stop]):term=c.If(x==code['W'],0,c.If(x==code['G'],1,c.If(x==code['C'],2,term)))
            first.append(term)
        incoming=[[] for _ in range(n+1)];outgoing=[[] for _ in incoming];kind_edges={k:[] for k in g['patterns']}
        for lo in range(n):
            for kind,pat in g['patterns'].items():
                if kind in ('PAIR','COPY'):continue
                hi=lo+len(pat)
                if hi>n or (lo==0 and kind!='INITIAL') or (kind=='INITIAL' and lo!=0) or (hi==n and kind!='CONCLUSION') or (kind=='CONCLUSION' and hi!=n):continue
                allowed=[g['types'][t[1:]] if t.startswith('@') else [t] for t in pat]
                if any(w in lex and lex[w] not in allowed[j] for j,w in enumerate(raw[lo:hi])):continue
                edge=c.Bool(tag+str(lo)+'_'+kind);weight=c.If(edge,1,0);outgoing[lo].append(weight);incoming[hi].append(weight);kind_edges[kind].append(weight)
                cond=[OR([value[lo+j]==code[v] for v in vs]) for j,vs in enumerate(allowed)]
                def arg(offset):
                    x=value[lo+offset];cond.append(c.Implies(x==code['FIRST_CARGO'],first[hi]>=0));cond.append(c.Implies(x==code['OTHER_CARGO'],AND([other==1,first[hi]>=0])))
                    return c.If(x==code['W'],0,c.If(x==code['G'],1,c.If(x==code['C'],2,first[hi])))
                moving=kind in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP')
                if moving:
                    if kind=='EXCLUDE':
                        omitted=arg(1);load=c.Int(tag+'choice'+str(lo));cond.extend([load>=-1,load<=2,load!=omitted])
                    elif kind=='ALONE':load=c.IntVal(-1)
                    else:load=arg({'WITH_OUT':3,'FERRY':1,'WITH_RETURN':1,'CONVEY':2,'FINAL_TRIP':4}[kind])
                    destination=1-state[0][lo] if kind=='FERRY' else c.IntVal(1 if kind in ('WITH_OUT','CONVEY','FINAL_TRIP') else 0)
                    cond.extend([state[1][lo]==state[0][lo],destination!=state[0][lo],final[lo]==0,state[0][hi]==destination,state[1][hi]==destination,last[hi]==load,final[hi]==(1 if kind=='FINAL_TRIP' else 0),stay[hi]==-1,staybank[hi]==staybank[lo]])
                    for k in range(3):
                        cond.extend([c.Implies(load==k,AND([named[k],state[k+2][lo]==state[0][lo]])),state[k+2][hi]==c.If(load==k,destination,state[k+2][lo]),c.Implies(AND([stay[lo]==k,load!=k]),state[k+2][hi]==staybank[lo])])
                else:
                    cond.extend(state[obj][hi]==state[obj][lo] for obj in range(5));cond.extend([last[hi]==last[lo],final[hi]==final[lo]])
                    bank=c.If(there==1,state[0][lo],1)
                    if kind=='STAY':
                        cond.extend([last[lo]>=0,stay[hi]==last[lo],staybank[hi]==bank]);cond.extend(c.Implies(last[lo]==k,state[k+2][lo]==bank) for k in range(3))
                    else:cond.extend([stay[hi]==stay[lo],staybank[hi]==staybank[lo]])
                    if kind=='RESULT':
                        target=arg(3);cond.extend([last[lo]>=0,target!=last[lo],OR([AND([target==k,named[k]]) for k in range(3)])]);cond.extend(c.Implies(named[k],state[k+2][lo]==state[0][lo]) for k in range(3))
                    if kind=='CONCLUSION':cond.append(state[0][lo]==bank);cond.extend(c.Implies(named[k],state[k+2][lo]==bank) for k in range(3))
                solver.add(c.Implies(edge,AND(cond)))
        solver.add(SUM(outgoing[0])==1,SUM(incoming[-1])==1)
        for pos in range(1,n):solver.add(SUM(incoming[pos])==SUM(outgoing[pos]),SUM(incoming[pos])<=1)
        for k in mandatory:solver.add(SUM(kind_edges[k])==1)
    return solver,xs,code,other,there

def run(job):
    started=time.monotonic()
    s,xs,num,other,there=build(job['paragraphs'],job['lexicon'],job['grammar'],job.get('timeout',5000));out=[]
    for q in job.get('queries',[dict(id='exists')]):
        s.push()
        if 'word' in q:s.add(xs[q['word']]==num[q['value']])
        if 'blocked_tuples' in q:
            for values in q['blocked_tuples']:s.add(OR([xs[w]!=num[v] for w,v in values.items()]))
        if 'other_first' in q:s.add(other==int(q['other_first']))
        if 'there_current' in q:s.add(there==int(q['there_current']))
        remaining=job.get('worker_seconds',600)-(time.monotonic()-started)
        if remaining<=0:status='unknown_batch_limit'
        else:
            s.set('tlimit-per',max(1,min(job.get('timeout',5000),int(remaining*1000))));status=str(s.check())
        out.append(dict(id=q['id'],status=status));s.pop()
    return dict(solver='cvc5',version=cvc5.__version__,queries=out)
if __name__=='__main__':print(json.dumps(run(json.load(sys.stdin))))

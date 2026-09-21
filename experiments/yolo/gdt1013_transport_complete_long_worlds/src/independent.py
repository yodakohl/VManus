"""Independent integer-state boundary-flow model with explicit boat and STAY."""
import itertools
from cvc5 import pythonic as c
import cvc5
NAMES=('W','G','C');PAIRS=list(itertools.permutations(range(3),2))
def OR(xs):return c.BoolVal(False) if not xs else xs[0] if len(xs)==1 else c.Or(*xs)
def AND(xs):return c.BoolVal(True) if not xs else xs[0] if len(xs)==1 else c.And(*xs)
def SUM(xs):return sum(xs,c.IntVal(0))
def check(p,lex,g,variant,timeout=30000,fixed_layout=None):
    raw=p['words'];n=len(raw);alphabet=set(lex.values())
    for pat in g['patterns'].values():
        for t in pat:alphabet.update(g['types'][t[1:]] if t.startswith('@') else [t])
    alphabet=sorted(alphabet);code={a:i for i,a in enumerate(alphabet)};xs={w:c.Int('word'+str(i)) for i,w in enumerate(sorted(set(raw)-lex.keys()))}
    solver=c.Solver();solver.set('tlimit-per',timeout)
    for x in xs.values():solver.add(x>=0,x<len(alphabet))
    values=[c.IntVal(code[lex[w]]) if w in lex else xs[w] for w in raw]
    named=[OR([v==code[name] for v in values]) for name in NAMES]
    appearance=[[c.Int('introduced'+str(k)+'_'+str(i)) for i in range(n+1)] for k in range(3)]
    for k,name in enumerate(NAMES):
        solver.add(appearance[k][0]==-1)
        for i,v in enumerate(values):solver.add(appearance[k][i+1]==c.If(appearance[k][i]>=0,appearance[k][i],c.If(v==code[name],i,-1)))
    earliest=[];latest=[]
    for stop in range(n+1):
        e=c.IntVal(-1);l=c.IntVal(-1)
        for k in range(3):
            present=appearance[k][stop]>=0
            before=AND([c.Or(appearance[j][stop]<0,appearance[k][stop]<appearance[j][stop]) for j in range(3) if j!=k])
            after=AND([appearance[k][stop]>appearance[j][stop] for j in range(3) if j!=k])
            e=c.If(c.And(present,before),k,e);l=c.If(c.And(present,after),k,l)
        earliest.append(e);latest.append(l)
    positions=[[c.Int('loc'+str(k)+'_'+str(i)) for i in range(n+1)] for k in range(5)] # M,B,W,G,C
    last=[c.Int('load'+str(i)) for i in range(n+1)];final=[c.Int('final'+str(i)) for i in range(n+1)]
    pair=[c.Int('pair'+str(i)) for i in range(n+1)];stay=[c.Int('stay'+str(i)) for i in range(n+1)];staybank=[c.Int('staybank'+str(i)) for i in range(n+1)]
    for line in positions:
        solver.add(line[0]==0)
        for x in line:solver.add(x>=0,x<=1)
    for i in range(n+1):solver.add(last[i]>=-1,last[i]<=2,final[i]>=0,final[i]<=1,pair[i]>=-1,pair[i]<6,stay[i]>=-1,stay[i]<=2,staybank[i]>=0,staybank[i]<=1)
    solver.add(last[0]==-1,final[0]==0,pair[0]==-1,stay[0]==-1,positions[0][n]==1)
    for k in range(3):solver.add(c.Implies(named[k],positions[k+2][n]==1))
    hazards={p:c.Int('hazard'+str(p[0])+str(p[1])) for p in itertools.combinations(range(3),2)};causes={p:[] for p in hazards}
    incoming=[[] for _ in range(n+1)];outgoing=[[] for _ in incoming];kinds={k:[] for k in g['patterns']};edges=[]
    fixed=None if fixed_layout is None else {(x['start'],x['end'],x['kind']) for x in fixed_layout}
    def member(which,at):
        answer=c.IntVal(-1)
        for i,parts in enumerate(PAIRS):answer=c.If(pair[at]==i,parts[which],answer)
        return answer
    for start in range(n):
        for kind,pat in g['patterns'].items():
            end=start+len(pat)
            if end>n or (start==0)!=(kind=='INITIAL') or (end==n)!=(kind=='CONCLUSION'):continue
            if fixed is not None and (start,end,kind) not in fixed:continue
            domains=[g['types'][x[1:]] if x.startswith('@') else [x] for x in pat]
            if any(w in lex and lex[w] not in domains[j] for j,w in enumerate(raw[start:end])):continue
            edge=c.Bool('edge'+str(start)+'_'+kind);edges.append((start,end,kind,edge));weight=c.If(edge,1,0);outgoing[start].append(weight);incoming[end].append(weight);kinds[kind].append(weight)
            cond=[OR([values[start+j]==code[a] for a in d]) for j,d in enumerate(domains)]
            def reference(offset=None):
                token=c.IntVal(code['OTHER_CARGO']) if offset is None else values[start+offset]
                first=earliest[end] if variant['first']=='FIRST' else latest[end]
                if variant['other']=='FIRST':other=earliest[end];valid_other=other>=0
                else:
                    available=[AND([pair[start]>=0,appearance[k][end]>=0,member(0,start)!=k,member(1,start)!=k]) for k in range(3)]
                    other=c.If(available[0],0,c.If(available[1],1,2));valid_other=SUM([c.If(a,1,0) for a in available])==1
                cond.append(c.Implies(token==code['FIRST_CARGO'],first>=0));cond.append(c.Implies(token==code['OTHER_CARGO'],valid_other))
                return c.If(token==code['W'],0,c.If(token==code['G'],1,c.If(token==code['C'],2,c.If(token==code['FIRST_CARGO'],first,other))))
            if kind=='PAIR':
                left=reference(0);right=reference(3);cond.append(left!=right)
                cond.append(OR([AND([left==a,right==b,pair[end]==i]) for i,(a,b) in enumerate(PAIRS)]))
            else:
                cond.append(pair[end]==pair[start])
                if kind=='COPY':
                    ref=reference();cond.append(pair[start]>=0)
                    left,right=(ref,member(1,start)) if variant['copy']=='FIRST' else (member(0,start),ref)
                    cond.append(left!=right)
            if kind in ('PAIR','COPY'):
                for a,b in hazards:causes[(a,b)].append(AND([edge,OR([AND([left==a,right==b]),AND([left==b,right==a])])]))
            moving=kind in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP')
            if moving:
                if kind=='ALONE':load=c.IntVal(-1)
                elif kind=='EXCLUDE' and variant['exclude']=='EXCLUDING':
                    excluded=reference(1);load=c.Int('choice'+str(start));cond.extend([load>=-1,load<=2,load!=excluded])
                else:load=reference({'WITH_OUT':3,'EXCLUDE':1,'FERRY':1,'WITH_RETURN':1,'CONVEY':2,'FINAL_TRIP':4}[kind])
                dest=1-positions[0][start] if kind=='FERRY' else c.IntVal(1 if kind in ('WITH_OUT','CONVEY','FINAL_TRIP') else 0)
                cond.extend([positions[1][start]==positions[0][start],dest!=positions[0][start],final[start]==0,positions[0][end]==dest,positions[1][end]==dest,last[end]==load,final[end]==(1 if kind=='FINAL_TRIP' else 0),stay[end]==-1,staybank[end]==staybank[start]])
                for k in range(3):
                    cond.extend([c.Implies(load==k,AND([named[k],positions[k+2][start]==positions[0][start]])),positions[k+2][end]==c.If(load==k,dest,positions[k+2][start]),c.Implies(AND([stay[start]==k,load!=k]),positions[k+2][end]==staybank[start])])
            else:
                cond.extend(positions[k][end]==positions[k][start] for k in range(5));cond.extend([last[end]==last[start],final[end]==final[start]])
                bank=positions[0][start] if variant['there']=='CURRENT' else c.IntVal(1)
                if kind=='STAY':
                    cond.extend([last[start]>=0,stay[end]==last[start],staybank[end]==bank]);cond.extend(c.Implies(last[start]==k,positions[k+2][start]==bank) for k in range(3))
                else:cond.extend([stay[end]==stay[start],staybank[end]==staybank[start]])
                if kind=='RESULT':
                    target=reference(3);cond.extend([last[start]>=0,target!=last[start],OR([AND([target==k,named[k]]) for k in range(3)])]);cond.extend(c.Implies(named[k],positions[k+2][start]==positions[0][start]) for k in range(3))
                if kind=='CONCLUSION':cond.append(positions[0][start]==bank);cond.extend(c.Implies(named[k],positions[k+2][start]==bank) for k in range(3))
            solver.add(c.Implies(edge,AND(cond)))
    solver.add(SUM(outgoing[0])==1,SUM(incoming[-1])==1)
    for stop in range(1,n):solver.add(SUM(incoming[stop])==SUM(outgoing[stop]),SUM(incoming[stop])<=1)
    for kind in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'):solver.add(SUM(kinds[kind])==1)
    for (a,b),hazard in hazards.items():
        solver.add(hazard==c.If(OR(causes[(a,b)]),1,0))
        for stop in range(n+1):solver.add(c.Implies(hazard==1,c.Or(positions[a+2][stop]!=positions[b+2][stop],positions[a+2][stop]==positions[0][stop])))
    answer=str(solver.check());out=dict(status=answer,solver='cvc5',version=cvc5.__version__)
    if answer=='sat':
        m=solver.model();aliases={w:alphabet[m.eval(x,model_completion=True).as_long()] for w,x in xs.items()};full={**lex,**aliases}
        chosen=sorted((lo,hi,k) for lo,hi,k,b in edges if c.is_true(m.eval(b,model_completion=True)))
        parsed=[dict(start=lo,end=hi,kind=k,symbols=[full[w] for w in raw[lo:hi]]) for lo,hi,k in chosen]
        out['witness']=dict(aliases=full,parse=parsed,variant=variant)
    return out

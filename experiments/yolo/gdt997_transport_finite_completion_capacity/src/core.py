"""Exact finite grammar consequences, never target normalization."""
import time

REQUIRED=('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION')
BITS={k:1<<i for i,k in enumerate(REQUIRED)}
FULL=(1<<len(REQUIRED))-1

def domains(spec):
    return {k:[set(spec['types'][s[1:]]) if s.startswith('@') else {s} for s in pat]
            for k,pat in spec['patterns'].items()}

def endpoints(words,lex,spec):
    n=len(words);pats=domains(spec);minimum=sum(len(pats[k]) for k in REQUIRED)
    conflicts=[];ds={}
    if n<minimum:conflicts.append(dict(kind='MINIMUM_COMPLETE_SCOPE',observed=n,required=minimum))
    for k,start in [('INITIAL',0),('CONCLUSION',n-len(pats['CONCLUSION']))]:
        if start<0 or start+len(pats[k])>n:continue
        for off,allowed in enumerate(pats[k]):
            i=start+off;w=words[i]
            if w in lex:
                if lex[w] not in allowed:conflicts.append(dict(kind='KNOWN_VALUE',position=i+1,raw=w,value=lex[w],required=sorted(allowed),clause=k))
            else:
                ds[w]=ds.get(w,allowed)&allowed
                if not ds[w]:conflicts.append(dict(kind='SHARED_ENDPOINT_VALUE',position=i+1,raw=w,clause=k))
    return dict(pass_=not conflicts,conflicts=conflicts,unknown_domains={w:sorted(v) for w,v in sorted(ds.items())})

def edges(words,lex,spec):
    pats=domains(spec);n=len(words);out=[[] for _ in range(n+1)]
    for i in range(n):
        for kind,pat in pats.items():
            j=i+len(pat)
            if j>n or (kind=='INITIAL' and i!=0) or (kind=='CONCLUSION' and j!=n):continue
            if i==0 and kind!='INITIAL':continue
            if j==n and kind!='CONCLUSION':continue
            if all(w not in lex or lex[w] in allowed for w,allowed in zip(words[i:j],pat)):
                out[i].append(dict(kind=kind,start=i,end=j,allowed=[sorted(d) for d in pat]))
    return out

def relaxed_path(words,lex,spec):
    graph=edges(words,lex,spec);seen={(0,0):None}
    for i in range(len(words)):
        for _,mask in sorted(x for x in seen if x[0]==i):
            for e in graph[i]:
                bit=BITS.get(e['kind'],0)
                if bit and mask&bit:continue
                key=(e['end'],mask|bit)
                if key not in seen:seen[key]=(i,mask,e)
    key=(len(words),FULL);path=[]
    if key in seen:
        while seen[key] is not None:
            i,mask,e=seen[key];path.append(e);key=(i,mask)
        path.reverse()
    return dict(feasible=bool(path),reachable_states=len(seen),witness=path),graph

def shared_path(words,lex,spec,maxstates,seconds):
    graph=edges(words,lex,spec);start=time.monotonic();memo=set();states=0
    class Limit(Exception):pass
    def rec(i,mask,bindings):
        nonlocal states
        states+=1
        if states>maxstates or time.monotonic()-start>seconds:raise Limit
        if i==len(words):return ([],bindings) if mask==FULL else None
        key=(i,mask,tuple(sorted((w,tuple(v)) for w,v in bindings.items())))
        if key in memo:return None
        for e in graph[i]:
            bit=BITS.get(e['kind'],0)
            if bit and mask&bit:continue
            new=bindings.copy();ok=True
            for w,allowed in zip(words[e['start']:e['end']],e['allowed']):
                if w in lex:continue
                vals=sorted(set(new.get(w,allowed))&set(allowed))
                if not vals:ok=False;break
                new[w]=vals
            if ok:
                tail=rec(e['end'],mask|bit,new)
                if tail is not None:return ([e]+tail[0],tail[1])
        memo.add(key);return None
    try:
        ans=rec(0,0,{})
        if ans is None:return dict(status='SHARED_UNSAT',states=states,elapsed=time.monotonic()-start)
        path,bindings=ans;aliases={w:v[0] for w,v in sorted(bindings.items())};complete={**lex,**aliases}
        parse=[dict(kind=e['kind'],start=e['start'],end=e['end'],symbols=[complete[w] for w in words[e['start']:e['end']]]) for e in path]
        return dict(status='SHARED_SAT',states=states,elapsed=time.monotonic()-start,parse=parse,aliases=aliases,alias_domains={w:v for w,v in sorted(bindings.items())})
    except Limit:return dict(status='UNKNOWN_SEARCH_LIMIT',states=states,elapsed=time.monotonic()-start)

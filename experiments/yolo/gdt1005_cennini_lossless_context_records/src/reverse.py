"""Independent right-to-left whole-equation search with type-local prefix checks."""
import collections,itertools,time

def ground(atoms,words,types,code):
    assert set(code)==set(atoms)==set(types) and all(isinstance(x,str) and x for x in code.values())
    for a,b in itertools.combinations(code,2):
        if types[a]==types[b]:assert not code[a].startswith(code[b]) and not code[b].startswith(code[a])
    cursor=0
    for word in words:
        suffix=word
        while suffix:
            assert cursor<len(atoms);v=code[atoms[cursor]];assert suffix.startswith(v)
            suffix=suffix[len(v):];cursor+=1
    assert cursor==len(atoms)

def replay(atoms,words,types,seconds=10,max_nodes=1000000,max_solutions=2,pinned=None,record_ends=None):
    started=time.monotonic();deadline=started+seconds;text=''.join(words);N=len(text);freq=collections.Counter(atoms)
    starts=[0]*(N+1);pos=0
    for word in words:
        for end in range(pos+1,pos+len(word)+1):starts[end]=pos
        pos+=len(word)
    pieces=set()
    for word in words:
        for lo in range(len(word)):
            for hi in range(lo+1,len(word)+1):pieces.add(word[lo:hi])
    occurrences={p:sum(w.count(p) for w in words) for p in pieces}
    domains={}
    for a,k in freq.items():
        mx=min(max(map(len,words)),(N-len(atoms)+k)//k)
        ds=[p for p in ([pinned[a]] if pinned is not None and a in pinned else pieces) if p in pieces and len(p)<=mx and occurrences[p]>=k]
        if pinned is not None and a in pinned:ds=[p for p in ds if p==pinned[a]]
        domains[a]=sorted(ds)
    if any(not x for x in domains.values()):return dict(status='UNSAT_REPLAY',nodes=0,exhaustive=True,codes=[],reason='empty_domain')
    if time.monotonic()>=deadline:return dict(status="UNKNOWN_REPLAY_LIMIT",nodes=0,exhaustive=False,codes=[],reason="PREPARATION_TIME_LIMIT")
    low={a:min(map(len,x)) for a,x in domains.items()};high={a:max(map(len,x)) for a,x in domains.items()}
    prefix=[collections.Counter()]
    for a in atoms:prefix.append(prefix[-1]+collections.Counter([a]))
    code={};nodes=0;solutions=[]
    class Deadline(Exception):pass
    record_index={0:0, **{e:j+1 for j,e in enumerate(record_ends or range(1,len(atoms)+1))}}
    word_starts={0};z=0
    for w in words:z+=len(w);word_starts.add(z)
    def visit(i,end,next_record=None):
        if next_record is None:next_record=len(record_index)-1
        nonlocal nodes
        nodes+=1
        if nodes>max_nodes or (nodes%128==0 and time.monotonic()>=deadline):raise Deadline
        if end in word_starts and end!=N:
            if i not in record_index or next_record-record_index[i] not in (1,2):return False
            next_record=record_index[i]
        elif i in record_index and next_record-record_index[i]>=2:return False
        if i==0:
            if end==0:
                solutions.append(dict(code));return len(solutions)>=max_solutions
            return False
        if end==0:return False
        lo=sum(k*(len(code[a]) if a in code else low[a]) for a,k in prefix[i].items())
        hi=sum(k*(len(code[a]) if a in code else high[a]) for a,k in prefix[i].items())
        if not lo<=end<=hi:return False
        a=atoms[i-1]
        if a in code:
            v=code[a];begin=end-len(v)
            return begin>=starts[end] and text[begin:end]==v and visit(i-1,begin,next_record)
        for v in domains[a]:
            begin=end-len(v)
            if begin<starts[end] or text[begin:end]!=v:continue
            if any(types[a]==types[b] and (v.startswith(w) or w.startswith(v)) for b,w in code.items()):continue
            code[a]=v
            if visit(i-1,begin,next_record):return True
            del code[a]
        return False
    try:
        capped=visit(len(atoms),N);status='SAT_REPLAY' if solutions else 'UNSAT_REPLAY';exhaustive=not capped
    except Deadline:status='SAT_REPLAY' if solutions else 'UNKNOWN_REPLAY_LIMIT';exhaustive=False
    for c in solutions:ground(atoms,words,types,c)
    return dict(status=status,nodes=nodes,exhaustive=exhaustive,codes=solutions,elapsed_seconds=time.monotonic()-started)

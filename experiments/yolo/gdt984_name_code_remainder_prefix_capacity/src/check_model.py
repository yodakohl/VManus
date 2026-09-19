"""Independent packed finite-frontier recognizer and ground witness checker."""
def decide(atoms,text,codes,bounds=False):
    n=len(text);full=(1<<(n+1))-1;reachable=1;names=list(codes.values());memo={};history=[1]
    starts={a:sum(1<<i for i in range(n) if text.startswith(v,i)) for a,v in codes.items()}
    for i,a in enumerate(atoms):
        if a in codes:
            reachable=(reachable & starts[a])<<len(codes[a])
            if not reachable:return False,i,'NO_NAME_BOUNDARY'
        else:
            pending=reachable;best=n+1
            while pending:
                low=pending & -pending;b=low.bit_length()-1;pending-=low
                if b>=best:break
                if b not in memo:
                    memo[b]=n+1
                    for end in range(b+1,min(n,b+max(map(len,names)))+1):
                        value=text[b:end]
                        if all(not value.startswith(c) and not c.startswith(value) for c in names):memo[b]=end;break
                best=min(best,memo[b])
            if best>n:return False,i,'NO_NONNAME_BOUNDARY'
            reachable=full^((1<<best)-1)
        if bounds:history.append(reachable)
    if not reachable&(1<<n):return False,len(atoms),'FINAL_BOUNDARY_MISSING'
    if not bounds:return True,None,None
    cuts=[n];end=n
    for i in range(len(atoms)-1,-1,-1):
        a=atoms[i]
        if a in codes:b=end-len(codes[a])
        else:
            pending=history[i]&((1<<end)-1);b=None
            while pending:
                bit=pending & -pending;start=bit.bit_length()-1;pending-=bit
                value=text[start:end]
                if all(not value.startswith(c) and not c.startswith(value) for c in names):b=start;break
            assert b is not None
        assert history[i]&(1<<b)
        cuts.append(b);end=b
    cuts.reverse();ground(atoms,text,codes,cuts)
    return True,None,None,cuts

def ground(atoms,text,codes,bounds):
    assert len(bounds)==len(atoms)+1 and bounds[0]==0 and bounds[-1]==len(text)
    for i,a in enumerate(atoms):
        b,e=bounds[i:i+2];assert 0<=b<e<=len(text);value=text[b:e]
        if a in codes:assert value==codes[a]
        else:assert all(not value.startswith(c) and not c.startswith(value) for c in codes.values())

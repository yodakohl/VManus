"""Exact prefix-complement segmentation of a whole atom stream."""
def legal_minima(text,names):
    n=len(text);infty=n+1;end=[infty]*(n+1)
    for b in range(n):
        active=list(names)
        for j in range(b,n):
            length=j-b+1
            active=[c for c in active if len(c)>=length and c[length-1]==text[j]]
            if any(len(c)==length for c in active):break
            if not active:end[b]=j+1;break
    suffix=end[:];where=list(range(n+1))
    for b in range(n-1,-1,-1):
        if suffix[b+1]<suffix[b]:suffix[b]=suffix[b+1];where[b]=where[b+1]
    return end,suffix,where

def segment(atoms,text,codes,witness=False):
    assert len(codes)==2 and all(codes.values())
    names=list(codes.values());assert not names[0].startswith(names[1]) and not names[1].startswith(names[0])
    n=len(text);ends,suffix,where=legal_minima(text,names)
    occurrences={a:tuple(i for i in range(n) if text.startswith(c,i)) for a,c in codes.items()}
    state=('SET',(0,));trace=[];predecessors=[]
    for i,a in enumerate(atoms):
        mode,vals=state
        if a in codes:
            opts=occurrences[a]
            good=[b for b in opts if b>=vals] if mode=='INTERVAL' else [b for b in opts if b in vals]
            state=('SET',tuple(b+len(codes[a]) for b in good));predecessors.append(None)
            if not good:return dict(status='CONTRADICTED_PREFIX_PARTITION',failed_atom=i,reason='NO_NAME_BOUNDARY')
        else:
            if mode=='INTERVAL':b=where[vals];e=suffix[vals]
            else:
                b=min(vals,key=lambda p:(ends[p],p));e=ends[b]
            if e>n:return dict(status='CONTRADICTED_PREFIX_PARTITION',failed_atom=i,reason='NO_NONNAME_BOUNDARY')
            state=('INTERVAL',e);predecessors.append(b)
        if witness:trace.append(state)
    mode,vals=state
    if not (n>=vals if mode=='INTERVAL' else n in vals):return dict(status='CONTRADICTED_PREFIX_PARTITION',failed_atom=len(atoms),reason='FINAL_BOUNDARY_MISSING')
    result=dict(status='PARTIAL_PREFIX_PARTITION',failed_atom=None,reason=None)
    if witness:
        boundaries=[n];end=n
        for i in range(len(atoms)-1,-1,-1):
            a=atoms[i];b=end-len(codes[a]) if a in codes else predecessors[i]
            prev=('SET',(0,)) if i==0 else trace[i-1]
            assert (b>=prev[1] if prev[0]=='INTERVAL' else b in prev[1])
            value=text[b:end];assert value
            if a in codes:assert value==codes[a]
            else:assert all(not value.startswith(c) and not c.startswith(value) for c in names)
            boundaries.append(b);end=b
        assert end==0
        result['boundaries']=list(reversed(boundaries))
    return result

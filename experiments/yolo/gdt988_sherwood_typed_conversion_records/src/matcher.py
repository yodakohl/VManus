"""Finite typed three-piece word equations; no source or target I/O."""
from itertools import product
from time import monotonic

def dictionary_unique(code):
    qs=[k for k in code if k.startswith('Q:')]
    ts=[k for k in code if k.startswith('T:')]
    values=[code[q]+code[s]+code[p] for q,s,p in product(qs,ts,ts)]
    return len(values)==len(set(values))

def bind(code,key,value):
    if not value: return None
    if key in code: return code if code[key]==value else None
    typ=key.split(':',1)[0]
    if any(k.split(':',1)[0]==typ and v==value for k,v in code.items()): return None
    return dict(code,**{key:value})

def solve(record,words,writer,limits):
    chunks=record if writer=='FUSED' else [[x] for c in record for x in c]
    if len(chunks)!=len(words): return {'status':'COUNT_MISMATCH','codes':[],'nodes':0,'reason':f'expected {len(chunks)} groups; observed {len(words)}'}
    equal={}; reverse={}
    for c,w in zip(chunks,words):
        c=tuple(c)
        if c in equal and equal[c]!=w: return {'status':'REPEAT_CONFLICT','codes':[],'nodes':0,'reason':f'repeated {c} differs: {equal[c]} versus {w}'}
        equal[c]=w
        if len(c)==1:
            tag=(c[0].split(':',1)[0],w)
            if tag in reverse and reverse[tag]!=c[0]: return {'status':'TYPE_COLLISION','codes':[],'nodes':0,'reason':f'{c[0]} and {reverse[tag]} have same typed code {w}'}
            reverse[tag]=c[0]
    todo=list(zip(chunks,words)); codes=[]; nodes=0; stopped=False; start=monotonic()
    def rec(i,code):
        nonlocal nodes,stopped
        if stopped:return
        nodes+=1
        if nodes>limits['nodes_per_case'] or (nodes%128==0 and monotonic()-start>limits['seconds_per_case']): stopped=True;return
        if i==len(todo):
            if writer=='FUSED' and not dictionary_unique(code):return
            codes.append(dict(sorted(code.items())))
            if len(codes)>=limits['maximum_complete_local_assignments']:stopped=True
            return
        keys,w=todo[i]
        if len(keys)==1:
            new=bind(code,keys[0],w)
            if new is not None:rec(i+1,new)
            return
        for a in range(1,len(w)-1):
            for b in range(a+1,len(w)):
                new=code
                for k,v in zip(keys,(w[:a],w[a:b],w[b:])):
                    new=bind(new,k,v)
                    if new is None:break
                if new is not None:rec(i+1,new)
                if stopped:return
    rec(0,{})
    unique={tuple(c.items()):c for c in codes}
    return {'status':'UNKNOWN_COMPUTATION' if stopped else ('LOCAL_FIT' if unique else 'UNSAT_FINITE'),'codes':list(unique.values()),'nodes':nodes,'reason':'enumeration cutoff' if stopped else 'complete typed enumeration'}

def encode(record,code,writer):
    return [''.join(code[x] for x in c) for c in record] if writer=='FUSED' else [code[x] for c in record for x in c]

def join(left,right,writer):
    code=dict(left)
    for k,v in right.items():
        code=bind(code,k,v)
        if code is None:return None
    if writer=='FUSED' and not dictionary_unique(code):return None
    return dict(sorted(code.items()))

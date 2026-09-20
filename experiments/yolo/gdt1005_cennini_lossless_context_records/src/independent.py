"""Inverse actual code strings without consulting predicted atom positions."""
import collections,itertools
FIELDS=('scope','modality','subject','predicate','object')

def decode(words,writer,order,code):
    namespaces=collections.defaultdict(dict)
    for atom,value in code.items():
        assert value and atom[:2] in ('V:','M:')
        ns=atom[:2];assert value not in namespaces[ns];namespaces[ns][value]=atom[2:]
    for values in namespaces.values():
        for a,b in itertools.combinations(values,2):assert not a.startswith(b) and not b.startswith(a)
    result=[];state={};ownership=[]
    for word in words:
        pos=0;owned=[]
        def take(ns):
            nonlocal pos
            matches=[(v,a) for v,a in namespaces[ns].items() if word.startswith(v,pos)]
            assert len(matches)==1,(ns,pos,word)
            v,a=matches[0];pos+=len(v);return a
        while pos<len(word):
            before=dict(state)
            if writer=='DELTA':
                mask=take('M:');assert len(mask)==5 and set(mask)<=set('01')
                changed={k for k,b in zip(FIELDS,mask) if b=='1'}
            else:changed=set(FIELDS)
            for key in order:
                if key in changed:state[key]=take('V:')
            assert set(state)==set(FIELDS)
            if writer=='DELTA':assert changed=={k for k in FIELDS if before.get(k)!=state[k]}
            result.append(dict(state));owned.append(len(result))
            assert len(owned)<=2
        assert pos==len(word) and len(owned) in (1,2);ownership.append(owned)
    return result,ownership

def capacity(freqs,alphabet):
    total=0
    for values in freqs.values():
        weights=sorted(values.values())
        if not weights:continue
        if len(weights)==1:total+=weights[0];continue
        if alphabet<2:return None
        weights=[0]*((1-len(weights))%(alphabet-1))+weights
        while len(weights)>1:
            merged=sum(weights[:alphabet]);weights=sorted(weights[alphabet:]+[merged]);total+=merged
    return total

def pack(minima,lengths):
    # Backward states, independent of forward packing and its stop shortcut.
    reachable={len(minima)}
    for length in reversed(lengths):
        previous=set()
        for end in reachable:
            for n in (1,2):
                start=end-n
                if start>=0 and sum(minima[start:end])<=length:previous.add(start)
        reachable=previous
    return 0 in reachable

def bound_check(records,writer,words):
    frequencies=collections.defaultdict(collections.Counter);minimum=[];previous={}
    for row in records:
        changed=[k for k in FIELDS if previous.get(k)!=row[k]] if writer=='DELTA' else list(FIELDS)
        if writer=='DELTA':frequencies['MASK']['M:'+''.join(str(int(k in changed)) for k in FIELDS)]+=1
        for k in changed:frequencies['VALUE']['V:'+row[k]]+=1
        minimum.append(len(changed)+int(writer=='DELTA'));previous=dict(row)
    n=len(words);chars=sum(map(len,words));N=len(records)
    if not ((N+1)//2<=n<=N):return 'CONTRADICTED_RECORD_COUNT'
    if chars<sum(minimum):return 'CONTRADICTED_MINIMUM_CHARACTERS'
    if not pack(minimum,list(map(len,words))):return 'CONTRADICTED_RECORD_PACKING'
    bound=capacity(frequencies,len(set(''.join(words))))
    if bound is None or chars<bound:return 'CONTRADICTED_PREFIX_CAPACITY'
    return 'EXACT_SEARCH_REQUIRED'

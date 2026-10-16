#!/usr/bin/env python3
"""Exact differential whole-word-state source-window capacity, no meanings."""
import hashlib,itertools,json
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(A/n).write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
def constraints(groups):
    seen={};out=[]
    for i,g in enumerate(groups):
        if g in seen:out.append([seen[g],i])
        else:seen[g]=i
    return out

def search(values,groups,modulus,reverse=False):
    width=len(groups);count=max(0,len(values)-width+1);pairs=constraints(groups)
    alive=np.ones((count,modulus),dtype=bool)
    prefix=np.concatenate((np.zeros(1,dtype=np.int64),np.cumsum(values,dtype=np.int64)))
    b=np.arange(modulus,dtype=np.int64);survivors=[count*modulus]
    for i,j in pairs:
        lo,hi=(width-1-j,width-1-i) if reverse else (i+1,j+1)
        sums=(prefix[hi:hi+count]-prefix[lo:lo+count])%modulus
        alive &= sums[:,None]==((j-i)*b%modulus)[None,:]
        survivors.append(int(alive.sum()))
    hits=[[int(x),int(y)] for x,y in np.argwhere(alive)]
    return hits,survivors

def certificate(values,groups,b,modulus):
    state=0;states={groups[0]:0}
    for j in range(1,len(groups)):
        state=(state+int(values[j])-b)%modulus
        if groups[j] in states:assert states[groups[j]]==state
        else:states[groups[j]]=state
    incoming=(b-int(values[0]))%modulus
    assert [(states[groups[i]]-(incoming if i==0 else states[groups[i-1]])+b)%modulus for i in range(len(groups))]==list(values)
    return states,incoming

def patterns(length,prefix=()):
    if len(prefix)==length:yield prefix;return
    for x in range(max(prefix,default=-1)+2):yield from patterns(length,prefix+(x,))

def controls():
    checked=0
    for mod in [2,3]:
        for width in range(1,5):
            for groups in patterns(width):
                keys=sorted(set(groups));oracle={}
                for vals in itertools.product(range(mod),repeat=len(keys)-1):
                    h=dict(zip(keys,(0,)+vals))
                    for b in range(mod):
                        tail=tuple((h[groups[j]]-h[groups[j-1]]+b)%mod for j in range(1,width))
                        for first in range(mod):oracle.setdefault((first,)+tail,set()).add(b)
                for values in itertools.product(range(mod),repeat=width):
                    for reverse in [False,True]:
                        message=values[::-1] if reverse else values
                        hits,counts=search(values,groups,mod,reverse)
                        assert [b for start,b in hits]==sorted(oracle.get(message,set()))
                        for start,b in hits:certificate(message,groups,b,mod)
                        assert counts[-1]==len(hits);checked+=1
    values=[9,1,2,3];groups=['a','b','c','a']
    assert search(values,groups,27)[0]==[[0,2],[0,11],[0,20]]
    assert search(values,groups,27,True)[0]==[[0,4],[0,13],[0,22]]
    native=['w'+str((i*i+3*i)%11) for i in range(77)]
    states={g:(5*j+1)%27 for j,g in enumerate(sorted(set(native)))};b=7;incoming=13
    message=[(states[g]-(incoming if i==0 else states[native[i-1]])+b)%27 for i,g in enumerate(native)]
    source=[2,4,6]+message+[1,2]
    assert [3,b] in search(source,native,27)[0]
    for start,beta in search(source,native,27)[0]:certificate(source[start:start+77],native,beta,27)
    revsource=[1]+message[::-1]+[3]
    assert [1,b] in search(revsource,native,27,True)[0]
    assert search([1,2],native,27)==([], [0]*(len(constraints(native))+1))
    return dict(status='PASS',exhaustive_message_pattern_direction_cases=checked,composite27_noninvertible_distance=True,sourcefree77group_window=True,reverse_source_chunk_not_group_order=True)

def main():
    lock=read(E/'LOCK.json')
    for name,digest in lock['files'].items():assert sha(ROOT/name)==digest,name
    spec=read(E/'src/SPEC.json');save('CONTROLS.json',controls())
    source=read(ROOT/spec['projections_path']);native=read(ROOT/spec['native_path'])['original_source']
    assert native==read(ROOT/spec['worksheet_path'])['source_original_wrapper']['source_unit']
    assert native['edition']=='IT2a' and [l['metadata']['locus'] for l in native['lines']]==spec['required_loci']
    rows=[g for line in native['lines'] for g in line['groups']];groups=[g[2] for g in rows]
    assert len(groups)==spec['width']==77
    for pin in [source['source_pin'],source['record_pin']]:assert sha(ROOT/pin['path'])==pin['sha256']
    assert len(source['projections'])==70
    cases=[]
    for projection in source['projections']:
        text=projection['text'];offsets=projection['source_offsets'];assert len(text)==len(offsets)==projection['characters']
        unsupported=sorted(set(text)-set('abcdefghijklmnopqrstuvwxyz'))
        for direction in spec['directions']:
            count=max(0,len(text)-76);hits=[];counts=[];witnesses=[]
            if not unsupported:
                values=[ord(c)-96 for c in text]
                hits,counts=search(values,groups,27,direction=='REVERSE')
                for start,b in hits[:spec['witness_limit_per_case']]:
                    window=text[start:start+77];decoded=window if direction=='FWD' else window[::-1]
                    h,initial=certificate([ord(c)-96 for c in decoded],groups,b,27)
                    witnesses.append(dict(start=start,beta=b,source_window=window,decoded_text=decoded,state_by_form=h,incoming_state=initial,source_start_offset=offsets[start],source_last_offset=offsets[start+76]))
            cases.append(dict(projection_id=projection['id'],direction=direction,source_characters=len(text),source_windows=count,unsupported_chars=unsupported,decision='SOURCE_UNSUPPORTED' if unsupported else 'DIFFERENTIAL_CAPACITY_ONLY' if hits else 'NO_DIFFERENTIAL_WINDOW',offset_pairs=0 if unsupported else 27*count,surviving_pairs=len(hits),surviving_windows=len({x[0] for x in hits}),pairs=hits,survivor_pairs_by_constraint=counts,witnesses=witnesses))
    save('RESULT.json',dict(experiment_id='GDT1415',status='COMPLETE_FIXED_SOURCE_DIFFERENTIAL_CAPACITY',native_group_count=len(groups),distinct_native_forms=len(set(groups)),return_constraints=constraints(groups),cases=cases,word_meanings_assigned=0,claim_ceiling=spec['claim_ceiling']))
    print(json.dumps(dict(cases=len(cases),unsupported=sum(c['decision']=='SOURCE_UNSUPPORTED' for c in cases),surviving_cases=sum(c['surviving_pairs']>0 for c in cases),surviving_pairs=sum(c['surviving_pairs'] for c in cases))))
if __name__=='__main__':main()

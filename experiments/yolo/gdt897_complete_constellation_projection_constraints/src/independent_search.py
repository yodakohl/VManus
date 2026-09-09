"""Independent finite sign-CSP search. No geometric coordinates are read.

Full tensor alternation is checked before reducing constraints to unordered
source tuples. Certified supporting-face incidence supplies only necessary
domain bounds. DFS enforces all-different and every newly closed tuple.
Timeout never certifies UNSAT. A witness certifies only invariant compatibility.
"""
import gzip
import hashlib
import itertools as it
import json
import random
import sys
import time

def flip(mask):
    return ((mask & 1)<<2) | (mask & 2) | ((mask & 4)>>2)

def index(t,n):
    out=0
    for x in t:
        out=out*n+x
    return out

def check_tensor(a,n,k):
    if len(a)!=n**k or any(type(m) is not int or not 0<=m<=7 for m in a):
        raise ValueError('invalid mask tensor')
    for t in it.product(range(n),repeat=k):
        m=a[index(t,n)]
        if len(set(t))<k:
            if m!=0:
                raise ValueError('repeated index must have mask zero')
            continue
        expected=a[index(sorted(t),n)]
        if sum(t[i]>t[j] for i in range(k) for j in range(i+1,k))%2:
            expected=flip(expected)
        if m!=expected or not m:
            raise ValueError('tensor is not an alternating sign enclosure')

def face_counts(a,n,k,certified):
    counts=[0]*n
    for face in it.combinations(range(n),k-1):
        common=5
        for v in range(n):
            if v in face:
                continue
            m=a[index(face+(v,),n)]
            if certified and m not in (1,4):
                common=0
                break
            common &= m
            if not common:
                break
        if common:
            for v in face:
                counts[v]+=1
    return counts

class Budget(Exception):
    pass

def solve_orientation(source,target,n,k,g,seconds,source_degrees,target_degrees):
    end=time.monotonic()+seconds
    mapping={}
    nodes=0
    source=[flip(m) for m in source] if g==-1 else source
    def tick():
        if time.monotonic()>=end:
            raise Budget
    def matches(t):
        return bool(source[index(t,n)] & target[index(tuple(mapping[u] for u in t),n)])
    def dfs(domains):
        nonlocal nodes
        tick(); nodes+=1
        if not domains:
            return [mapping[u] for u in range(n)]
        u=min(domains,key=lambda x:(len(domains[x]),-source_degrees[x],x))
        old=tuple(mapping)
        # Prior domains already satisfy constraints against all prior assignments.
        subsets=list(it.combinations(old,k-2)) if k>=2 else [()]
        for value in sorted(domains[u]):
            tick()
            mapping[u]=value
            # Check tuples closed by this assignment (also covers small n cases).
            if any(not matches(tuple(sorted(c+(u,)))) for c in it.combinations(old,k-1)):
                del mapping[u]
                continue
            nextdomains={}
            feasible=True
            for v,domain in domains.items():
                if v==u:
                    continue
                allowed=set()
                tuples=[tuple(sorted(c+(u,v))) for c in subsets]
                for candidate in domain:
                    tick()
                    if candidate==value:
                        continue
                    mapping[v]=candidate
                    if all(matches(t) for t in tuples):
                        allowed.add(candidate)
                    del mapping[v]
                if not allowed:
                    feasible=False
                    break
                nextdomains[v]=allowed
            if feasible and nextdomains:
                # Necessary Hall condition for the entire residual domain union.
                feasible=len(set().union(*nextdomains.values()))>=len(nextdomains)
            if feasible:
                result=dfs(nextdomains)
                if result is not None:
                    return result
            del mapping[u]
        return None
    domains={u:{v for v in range(n) if target_degrees[v]>=source_degrees[u]} for u in range(n)}
    try:
        witness=None if any(not d for d in domains.values()) else dfs(domains)
        status='INVARIANT_COMPATIBLE' if witness is not None else 'UNSAT'
        if witness is not None:
            assert len(set(witness))==n
            assert all(source[index(t,n)] & target[index(tuple(witness[u] for u in t),n)]
                       for t in it.combinations(range(n),k))
    except Budget:
        witness=None; status='UNKNOWN_BUDGET'
    return dict(status=status,orientation=g,witness=witness,nodes=nodes,
                elapsed_seconds=time.monotonic()-(end-seconds))

def solve_case(case,seconds=120):
    n=case['n']; mode=case['mode']
    if type(n) is not int or n<1 or mode not in ('gnomonic','stereographic'):
        raise ValueError('invalid case size/mode')
    k=3 if mode=='gnomonic' else 4
    source=case['source_masks']; target=case['target_masks']
    check_tensor(source,n,k); check_tensor(target,n,k)
    # A certified face needs at least one other point.
    sd=face_counts(source,n,k,True) if n>=k else [0]*n
    td=face_counts(target,n,k,False) if n>=k else [0]*n
    runs=[]
    for g in (1,-1):
        result=solve_orientation(source,target,n,k,g,seconds,sd,td)
        runs.append(result)
        if result['status']=='INVARIANT_COMPATIBLE':
            break
    status=('INVARIANT_COMPATIBLE' if any(r['status']=='INVARIANT_COMPATIBLE' for r in runs)
            else 'UNSAT' if all(r['status']=='UNSAT' for r in runs) else 'UNKNOWN_BUDGET')
    return dict(case_id=case['case_id'],mode=mode,n=n,status=status,orientations=runs)

def selftest():
    def tensor(n,k,canonical):
        out=[0]*(n**k)
        for t in it.product(range(n),repeat=k):
            if len(set(t))<k:
                continue
            m=canonical(tuple(sorted(t)))
            if sum(t[i]>t[j] for i in range(k) for j in range(i+1,k))%2:
                m=flip(m)
            out[index(t,n)]=m
        return out
    for k,mode in ((3,'gnomonic'),(4,'stereographic')):
        n=k+1
        s=tensor(n,k,lambda t:1 if sum(t)%2 else 4)
        for target,expected in ((s,'INVARIANT_COMPATIBLE'),
                                 (tensor(n,k,lambda t:2),'UNSAT'),
                                 (tensor(n,k,lambda t:7),'INVARIANT_COMPATIBLE')):
            case=dict(case_id='invented',mode=mode,n=n,source_masks=s,target_masks=target)
            result=solve_case(case,2)
            # Direct all-permutation oracle has no DFS/domain or facet logic.
            oracle=any(all((flip(s[index(t,n)]) if g==-1 else s[index(t,n)]) &
                           target[index(tuple(p[u] for u in t),n)]
                           for t in it.combinations(range(n),k))
                       for g in (1,-1) for p in it.permutations(range(n)))
            assert result['status']==expected
            assert oracle==(expected=='INVARIANT_COMPATIBLE')
        case=dict(case_id='timeout',mode=mode,n=n,source_masks=s,target_masks=s)
        assert solve_case(case,0)['status']=='UNKNOWN_BUDGET'
        rng=random.Random(897+k)
        for fixture in range(12):
            keys=list(it.combinations(range(n),k))
            sm={t:rng.randrange(1,8) for t in keys}
            tm={t:rng.randrange(1,8) for t in keys}
            ss=tensor(n,k,sm.__getitem__); tt=tensor(n,k,tm.__getitem__)
            case=dict(case_id='random_synthetic',mode=mode,n=n,source_masks=ss,target_masks=tt)
            result=solve_case(case,2)
            oracle=any(all((flip(ss[index(t,n)]) if g==-1 else ss[index(t,n)]) &
                           tt[index(tuple(p[u] for u in t),n)] for t in keys)
                       for g in (1,-1) for p in it.permutations(range(n)))
            assert result['status']==('INVARIANT_COMPATIBLE' if oracle else 'UNSAT')
    return {'status':'PASS','scope':'invented tensors, exhaustive permutation oracle, both modes and timeout'}

def main():
    if sys.argv[1:]==['--selftest']:
        print(json.dumps(selftest())); return
    if len(sys.argv)!=3:
        raise SystemExit('usage: independent_search.py SEARCH_PACKET.json[.gz] OUTPUT.json')
    path,output=sys.argv[1:]
    raw=open(path,'rb').read()
    packet=json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)
    if packet.get('schema')!='GDT897_SEARCH_PACKET_V1':
        raise ValueError('unexpected packet schema')
    results=[solve_case(c) for c in packet['cases']]
    record=dict(schema='GDT897_INDEPENDENT_SEARCH_V1',packet_sha256=hashlib.sha256(raw).hexdigest(),
                source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest(),
                seconds_per_case_orientation=120,cases=results)
    with open(output,'w') as f:
        json.dump(record,f,indent=2); f.write('\n')

if __name__=='__main__':
    main()

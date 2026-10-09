"""Necessary code capacity; free UD, no prefix assumption."""
from collections import deque,Counter
import time


def ud_certificate(code):
    code=tuple(code);queue=deque();seen={}
    for i,a in enumerate(code):
        for j,b in enumerate(code):
            if i!=j and b[:len(a)]==a:
                r=b[len(a):]
                if r not in seen:seen[r]=([i],[j]);queue.append(r)
    while queue:
        r=queue.popleft();left,right=seen[r]
        for i,c in enumerate(code):
            if c==r:return {'status':'NON_UD','left':left+[i],'right':right}
            if r[:len(c)]==c:
                tail=r[len(c):];newleft,newright=left+[i],right
            elif c[:len(r)]==r:
                tail=c[len(r):];newleft,newright=right,left+[i]
            else:continue
            assert tail
            if tail not in seen:seen[tail]=(newleft,newright);queue.append(tail)
    return {'status':'UD','residuals':[list(r) for r in sorted(seen)]}


def inputs(words,alphabet):
    W=set(map(tuple,words));A=tuple(alphabet)
    assert W and {g for w in W for g in w}==set(A)
    singles={w[0] for w in W if len(w)==1};pairs={w for w in W if len(w)==2}
    seconds={h:{w[1] for w in W if len(w)>1 and w[0]==h} for h in A}
    return W,A,singles,pairs,seconds


def subcode(S,pairs):
    return sorted({(a,) for a in S}|{p for p in pairs if any(a not in S for a in p)},key=lambda w:(len(w),w))


def lower_bound(S,code,seconds,A):
    existing=Counter(w[0] for w in code)
    extra={h:max(0,len(seconds[h])-existing[h]) for h in A if h not in S}
    return max(len(code)+sum(extra.values()),len(S)+1),extra


def enumerate_cases(words,alphabet,seconds_limit=120):
    started=time.monotonic();W,A,S0,pairs,seconds=inputs(words,alphabet);free=sorted(set(A)-S0);rows=[]
    for mask in range((1<<len(free))-1):
        S=S0|{g for i,g in enumerate(free) if mask>>i&1};B=subcode(S,pairs);cert=ud_certificate(B)
        row={'mask':mask,'singletons':sorted(S),'forced_code_count':len(B),'ud':cert}
        if cert['status']=='UD':row['bound'],row['extra_head_codes']=lower_bound(S,B,seconds,A)
        rows.append(row)
        if time.monotonic()-started>seconds_limit:return {'status':'UNKNOWN_TIMEOUT','rows':rows}
    valid=[r for r in rows if r['ud']['status']=='UD'];values=[r['bound'] for r in valid];bound=min(values)if values else None
    forced=set(A)
    for row in valid:forced &= set(row['singletons'])
    summary={'initial_singletons':sorted(S0),'optional_signs':free,'whole_pair_types':len(pairs),'original_second_signs':{h:sorted(seconds[h])for h in A},'proper_sets':len(rows),'non_ud_subcodes':len(rows)-len(valid),'ud_subcodes':len(valid),'forced_singletons_from_short_code_condition':sorted(forced),'necessary_nontrivial_bound':bound,'bound_histogram':{str(k):n for k,n in sorted(Counter(values).items())},'minimum_sets':[r['mask']for r in valid if r['bound']==bound],'caps':{str(k):'EXCLUDED_NONTRIVIAL'if bound is None or bound>k else 'NOT_EXCLUDED'for k in(22,26,28)},'decision':'ONLY_IDENTITY'if not valid else'NECESSARY_BOUND_ONLY','identity':'Always compatible; no used longer code can coexist with all alphabet singletons.'}
    return {'status':'COMPLETE','rows':rows,'summary':summary}

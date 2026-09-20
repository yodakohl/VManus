"""Finite stage-cut enumerator. No corpus loading or heuristic search."""
import itertools
NAMES = ['MEMBRINA', 'PRASINUS', 'POSC', 'ROSA', 'LUMINA', 'VENEDA']
def encode(c, writer):
    pairs = [('MEMBRINA',None),('PRASINUS',None),('POSC','FIRST'),('ROSA','FIRST'),('LUMINA','FIRST'),('VENEDA',None),('POSC','SECOND'),('ROSA','SECOND'),('LUMINA','SECOND')]
    return [c[n] if t is None else c[t]+c[n] if writer=='STAGE_PREFIX' else c[n]+c[t] for n,t in pairs]
def solve(heads, writer):
    assert len(heads)==9 and writer in ('STAGE_PREFIX','STAGE_SUFFIX')
    codes=[]; rejected={}; cuts=0
    duplicates=[[i+1,j+1] for i,j in itertools.combinations(range(9),2) if heads[i]==heads[j]]
    if duplicates:return dict(status='CONTRADICTION',reason='COMPLETE_HEADER_COLLISION',codes=[],duplicate_positions=duplicates,cuts=0,rejected_cuts={})
    for a,b in itertools.product(range(1,len(heads[2])),range(1,len(heads[6]))):
        cuts+=1
        if writer=='STAGE_PREFIX':
            s1,s2=heads[2][:a],heads[6][:b]
            cores=[h[len(s):] if h.startswith(s) else None for h,s in zip([heads[i] for i in (2,3,4,6,7,8)],[s1]*3+[s2]*3)]
        else:
            s1,s2=heads[2][-a:],heads[6][-b:]
            cores=[h[:-len(s)] if h.endswith(s) else None for h,s in zip([heads[i] for i in (2,3,4,6,7,8)],[s1]*3+[s2]*3)]
        why=None
        if s1==s2: why='SAME_STAGE_CODE'
        elif not all(cores): why='STAGE_OR_NONEMPTY_CORE_CONFLICT'
        elif cores[:3]!=cores[3:]: why='NAME_CORE_CONFLICT'
        else:
            c=dict(zip(NAMES,[heads[0],heads[1],*cores[:3],heads[5]]))
            if len(set(c.values()))!=6: why='NAME_CODE_COLLISION'
            else:
                c.update(FIRST=s1,SECOND=s2);assert encode(c,writer)==heads
                codes.append(c)
        if why: rejected[why]=rejected.get(why,0)+1
    return dict(status='HEADER_FIT' if codes else 'CONTRADICTION',reason='ALL_HEADER_EQUATIONS_SATISFIED' if codes else 'NO_ALLOWED_STAGE_CUT',codes=codes,duplicate_positions=[],cuts=cuts,rejected_cuts=rejected)

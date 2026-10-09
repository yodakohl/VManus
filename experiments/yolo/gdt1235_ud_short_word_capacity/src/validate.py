"""Nonimporting independent finite-subcode and residual closure verification."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,gzip,hashlib
D=Path(__file__).resolve().parents[1];AOUT=D/'artifacts'


def independent_ud(C):
    C=set(map(tuple,C));frontier={v[len(u):]for u in C for v in C if u!=v and v[:len(u)]==u};visited=set()
    while frontier:
        r=frontier.pop()
        if r in C:return False,None
        visited.add(r)
        for w in C:
            for longer,shorter in ((r,w),(w,r)):
                if longer[:len(shorter)]==shorter:
                    tail=longer[len(shorter):]
                    if not tail:return False,None
                    if tail not in visited:frontier.add(tail)
    return True,visited


def verify_ud(C,cert):
    valid,residuals=independent_ud(C)
    if valid:
        assert cert['status']=='UD'
        assert residuals=={tuple(r)for r in cert['residuals']}
    else:
        assert cert['status']=='NON_UD';left,right=cert['left'],cert['right'];assert left!=right and left and right
        assert all(0<=i<len(C)for i in left+right)
        assert sum((C[i]for i in left),())==sum((C[i]for i in right),())
    return valid


def check(words,alphabet,cert):
    words=set(map(tuple,words));alphabet=set(alphabet);assert {g for w in words for g in w}==alphabet
    S0={w[0]for w in words if len(w)==1};free=sorted(alphabet-S0);pairs=sorted(w for w in words if len(w)==2);seconds={g:set()for g in alphabet}
    for w in words:
        if len(w)>=2:seconds[w[0]].add(w[1])
    assert cert['status']=='COMPLETE'and len(cert['rows'])==2**len(free)-1
    vals=[];masks=[];forced=set(alphabet);bad=0
    for mask,row in enumerate(cert['rows']):
        S=set(S0)
        for i,g in enumerate(free):
            if mask&(2**i):S.add(g)
        assert row['mask']==mask and row['singletons']==sorted(S)
        C=[(g,)for g in S]
        for a,b in pairs:
            if not(a in S and b in S):C.append((a,b))
        C=sorted(C,key=lambda w:(len(w),w));assert row['forced_code_count']==len(C)
        if not verify_ud(C,row['ud']):bad+=1;assert 'bound'not in row;continue
        extra={}
        for g in alphabet-S:
            heads=[c for c in C if c[0]==g]
            extra[g]=max(0,len(seconds[g])-len(heads))
        lower=len(C)+sum(extra.values());lower=max(lower,len(S)+1)
        assert row['bound']==lower and row['extra_head_codes']==extra
        vals.append(lower);masks.append((mask,lower));forced &= S
    minimum=min(vals)if vals else None
    summary={'initial_singletons':sorted(S0),'optional_signs':free,'whole_pair_types':len(pairs),'original_second_signs':{h:sorted(seconds[h])for h in alphabet},'proper_sets':len(cert['rows']),'non_ud_subcodes':bad,'ud_subcodes':len(vals),'forced_singletons_from_short_code_condition':sorted(forced),'necessary_nontrivial_bound':minimum,'bound_histogram':{str(k):n for k,n in sorted(Counter(vals).items())},'minimum_sets':[mask for mask,n in masks if n==minimum],'caps':{str(k):'EXCLUDED_NONTRIVIAL'if minimum is None or minimum>k else'NOT_EXCLUDED'for k in(22,26,28)},'decision':'ONLY_IDENTITY'if not vals else'NECESSARY_BOUND_ONLY','identity':'Always compatible; no used longer code can coexist with all alphabet singletons.'}
    assert summary==cert['summary']
    return {'status':'PASS','sets':len(cert['rows']),'non_ud':bad,'short_subcode_ud':len(vals),'bound':minimum}


def main():
    F=json.loads((AOUT/'FIXTURES.json').read_text())
    named=[check(f['W'],f['alphabet'],f['certificate'])for f in F['named']]
    lock=json.loads((AOUT/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    S=json.loads((D/'src/SPEC.json').read_text());groups=json.loads(gzip.decompress(Path(S['source']).read_bytes()));R=json.loads((AOUT/'RESULT.json').read_text());checks={}
    for reader in S['readers']:
        C=json.loads(gzip.decompress((AOUT/f'CERTIFICATE_{reader}.json.gz').read_bytes()));rows=groups[reader];W={tuple(r['units'])for r in rows}
        assert R['readers'][reader]['groups']==len(rows)and R['readers'][reader]['types']==len(W)
        assert R['readers'][reader]['summary']==C['summary'];checks[reader]=check(W,S['signs'],C)
    out={'status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'fixture_replays':named,'readers':checks,'immutable_inputs':'PASS','new_native_query':False,'independent_manuscript_validation':False}
    (AOUT/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)


if __name__=='__main__':main()

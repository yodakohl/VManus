#!/usr/bin/env python3
"""Target-free full positives, mutations, and direct codebook oracle."""
import itertools,json,random
from pathlib import Path
from matcher import solve,encode,NAMES
from validate import independent
E=Path(__file__).resolve().parents[1]
def canon(xs):return sorted(json.dumps(x,sort_keys=True) for x in xs)
def main():
    tests=[];rng=random.Random(989)
    for writer in ('STAGE_PREFIX','STAGE_SUFFIX'):
        for values in [ ['m','pr','abc','de','fgh','v','a','bc'],['b','bb','ab','ba','aaa','bab','a','aa'],['m','p','ooo','rrrr','ll','vvvv','ff','ssss'] ]:
            c=dict(zip(NAMES+['FIRST','SECOND'],values));heads=encode(c,writer)
            assert len(set(heads))==9
            a=solve(heads,writer)['codes'];b=independent(heads,writer)
            assert canon(a)==canon(b) and c in a
            tests.append(dict(kind='PLANTED_POSITIVE',writer=writer,heads=heads,planted_code=c,codes=len(a)))
            bad=heads.copy();bad[7]='z'+bad[7]+'z'
            assert not solve(bad,writer)['codes'] and not independent(bad,writer)
            tests.append(dict(kind='ONE_FAMILY_STAGE_CHANGED',writer=writer,heads=bad,status='NO_CODE'))
            bad=heads.copy();bad[1]=bad[0]
            assert not solve(bad,writer)['codes'] and not independent(bad,writer)
            tests.append(dict(kind='NAME_COLLISION',writer=writer,status='NO_CODE'))
            # Opposite orientation is also exhaustively enumerated, not presumed impossible.
            other='STAGE_SUFFIX' if writer=='STAGE_PREFIX' else 'STAGE_PREFIX'
            assert canon(solve(heads,other)['codes'])==canon(independent(heads,other))
    # Direct oracle: enumerate each of all eight code values over binary words <=2.
    # Fixed M/P/V outside this alphabet makes all name distinctions explicit.
    universe=['a','b','aa','ab','ba','bb']; indexed={w:{} for w in ('STAGE_PREFIX','STAGE_SUFFIX')}
    for writer in indexed:
        for o,r,l,a,b in itertools.product(universe,repeat=5):
            if len({o,r,l})!=3 or a==b:continue
            c=dict(zip(NAMES+['FIRST','SECOND'],['m','p',o,r,l,'v',a,b]));h=tuple(encode(c,writer))
            if len(set(h))!=9:continue
            indexed[writer].setdefault(h,[]).append(c)
        # Codebook enumeration is bounded; compare exactly the solutions in its domain.
        trials=list(indexed[writer]);rng.shuffle(trials);trials=trials[:200]
        trials += [tuple(['m','p']+[rng.choice(universe) for _ in range(3)]+['v']+[rng.choice(universe) for _ in range(3)]) for _ in range(200)]
        for h in trials:
            a=solve(list(h),writer)['codes'];b=independent(list(h),writer)
            assert canon(a)==canon(b)
            bounded=[c for c in a if all(c[n] in universe for n in ['POSC','ROSA','LUMINA','FIRST','SECOND'])]
            assert canon(bounded)==canon(indexed[writer].get(h,[]))
        tests.append(dict(kind='DIRECT_CODEBOOK_ORACLE',writer=writer,enumerated_assignments=len(universe)**5,distinct_valid_headers=len(indexed[writer]),trials=len(trials)))
    out=dict(status='PASS',target_data_loaded=False,fixtures=tests,oracle_trials=800,independent_meaning_validation=False)
    (E/'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','fixtures':len(tests),'oracle_trials':800}))
if __name__=='__main__':main()

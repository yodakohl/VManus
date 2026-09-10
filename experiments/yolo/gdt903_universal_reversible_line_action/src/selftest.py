#!/usr/bin/env python3
import itertools,json,random
from fold import fold,replay
from independent_subgroup import fold_generators,differences

def main():
    fixtures=[(['a','b'],False),(['a','aa','ab'],True),(['a','aa'],False),(['aa','bb','ab','ba'],False),(['aba','abba'],False)]
    for words,full in fixtures:
        r,_=fold(words,['a','b']);assert r['full_group']==full
        if not full:replay(words,r['completion'])
    rng=random.Random(903)
    for _ in range(100):
        words=[''.join(rng.choice('ab') for _ in range(rng.randint(1,12))) for i in range(rng.randint(2,12))]
        r,_=fold(words,['a','b']);encoded=[[1 if a=='a' else 2 for a in w] for w in words]
        g=fold_generators(differences(encoded,encoded[0]),2)
        assert r['core']['vertices']==g['vertex_count'] and r['core']['edges']==g['positive_edges']
        assert r['full_group']==g['equals_full_free_group']
    perms=list(itertools.permutations(range(3)));words=[''.join(w) for n in range(1,5) for w in itertools.product('ab',repeat=n)];checked=0
    for p,q in itertools.product(perms,repeat=2):
        buckets={i:[] for i in range(3)}
        for w in words:
            state=0
            for a in w:state=(p if a=='a' else q)[state]
            buckets[state].append(w)
        for bucket in buckets.values():
            if not bucket:continue
            r,_=fold(bucket,['a','b']);assert not r['full_group'] or p[0]==q[0]==0;checked+=1
    print(json.dumps({'status':'PASS','fixtures':len(fixtures),'independent_subgroup_parity_cases':100,'known_finite_action_cases':checked,'scope':'Invented examples only; no manuscript graph folded.'}))
if __name__=='__main__':main()

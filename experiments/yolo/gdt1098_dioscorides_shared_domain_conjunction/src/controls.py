"""Synthetic exact-oracle controls before source-domain conjunction."""
import itertools
import json
import random
from pathlib import Path
from model import compute
from validate import enumerate_sets


def main():
    rng = random.Random(1098)
    tested = 0
    for nroles in (2,3,4):
        for case in range(80):
            roles = []
            index = 0
            for r in range(nroles):
                choices = []
                for j in range(rng.randint(1,3)):
                    domains = {a: sorted(v for v in ('a','b','c') if rng.randrange(2)) for a in ('x','y') if rng.randrange(3)}
                    choices.append(dict(index=index,leaf=rng.randrange(nroles+1),domains=domains))
                    index += 1
                roles.append(choices)
            # Guarantee a nonempty finite universe; empty per-case domains stay.
            roles[0][0]['domains'] = {'x':['a','b','c'],'y':['a','b','c']}
            a = compute(roles,['x','y'])
            b = enumerate_sets(roles,['x','y'])
            assert a == b, (nroles,case)
            tested += 1
    cycle = [[dict(index=i,leaf=i,domains={'x':s})] for i,s in enumerate((['a','b'],['b','c'],['a','c']))]
    assert all(set(cycle[i][0]['domains']['x']) & set(cycle[j][0]['domains']['x']) for i,j in itertools.combinations(range(3),2))
    assert compute(cycle,['x']) == enumerate_sets(cycle,['x'])
    assert compute(cycle,['x'])['surviving_tuples'] == 0
    positive = [[dict(index=i,leaf=i,domains={'x':['a','b']} if i != 2 else {})] for i in range(4)]
    assert compute(positive,['x']) == enumerate_sets(positive,['x'])
    assert compute(positive,['x'])['surviving_tuples'] == 1
    positive[-1][0]['leaf']=0
    assert compute(positive,['x']) == enumerate_sets(positive,['x'])
    assert compute(positive,['x'])['distinct_leaf_tuples'] == 0
    report = dict(status='PASS_SYNTHETIC_CALCULATION_ONLY',random_finite_problems=tested,
                  explicit_globally_empty_pairwise_positive=1,nonparticipating_role_positive=1,repeated_leaf_negative=1,
                  target_domain_conjunctions_run=0)
    target = Path(__file__).resolve().parents[1]/'artifacts/CONTROLS.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()

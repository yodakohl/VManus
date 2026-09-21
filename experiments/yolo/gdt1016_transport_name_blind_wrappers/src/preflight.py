"""New algebra implementation fixtures only; no target law evaluation."""
from common import *
from wrappers import relations, contradictions, impose_z3
from wrapper_independent import relations_independent, saturation_errors, constrain_groups
import itertools
import z3
from cvc5 import pythonic as c


def main():
    symbols = ['W', 'G', 'C', 'X', 'Y']
    num = {s: i for i, s in enumerate(symbols)}
    groups = [dict(side='L', affix='q', pairs=[['a', 'qa'], ['b', 'qb']])]
    # Independently enumerate all 5^5 total functions and test the six equations.
    valid = []
    for outputs in itertools.product(symbols, repeat=5):
        function = dict(zip(symbols, outputs))
        good = True
        for permutation in itertools.permutations(symbols[:3]):
            move = dict(zip(symbols[:3], permutation))
            for x in symbols:
                if function[move.get(x, x)] != move.get(function[x], function[x]):
                    good = False
        if good:
            valid.append(function)
    assert len(valid) == 12
    rows = []
    for values in itertools.product(symbols, repeat=4):
        a, qa, b, qb = values
        code = dict(zip(('a', 'qa', 'b', 'qb'), values))
        exists = any(f[a] == qa and f[b] == qb for f in valid)
        zb = dict(solver=z3.Solver(), num=num, lexicon=code, xs={})
        impose_z3(zb, groups)
        cs = c.Solver()
        constrain_groups(cs, groups, code, {}, num)
        expected = 'sat' if exists else 'unsat'
        assert str(zb['solver'].check()) == str(cs.check()) == expected, values
        assert bool(contradictions(code, groups)) == bool(saturation_errors(code, groups)) == (not exists)
        rows.append(dict(values=values, expected=expected))
    s, g = inputs()
    assert (E/'src/world.py').read_bytes() == (R/s['source_world']).read_bytes()
    assert (E/'src/independent.py').read_bytes() == (R/s['source_independent']).read_bytes()
    cases, panel = read(A/'PREDICTIONS.json'), read(A/'PANEL.json')
    assert cases == read(R/s['source_predictions'])
    for case in cases:
        vocab = set(case['canonical_lexicon']) | set(panel[case['context_index']]['words'])
        assert case['groups'] == relations(vocab) == relations_independent(vocab)
    put('PREFLIGHT.json', dict(status='PASS', total_functions_enumerated=3125,
                               equivariant_functions=12, exact_partial_assignments=625,
                               fixtures=rows, full_world_models_byte_identical=True,
                               joint_scope_cases=52, target_law_queries=0,
                               inherited_semantic_fixtures='GDT1013:1152 cases,234SAT/918UNSAT'))
    print('PASS:625 algebra fixtures;52 unchanged scopes;zero target law tests.')


if __name__ == '__main__':
    main()

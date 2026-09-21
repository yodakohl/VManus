"""Prerequisite only: audit the existing quotient against fixed original graphs."""
from common import *
import itertools
import collections


def main():
    s, g = inputs()
    model = load(s['model'], 'original993')
    binding = load(s['binding_checker'], 'binding994')
    bits = load(s['bit_replay'], 'independent1006')
    originals = read(A/'ORIGINAL_CANDIDATES.json')
    original_by_id = {row['id']: row for row in originals}
    cases = read(A/'PREDICTIONS.json')
    settings = [dict(zip(g['variants'], v)) for v in itertools.product(*g['variants'].values())]
    original_checks = []
    for row in originals:
        center = row['code']['qokedy']
        expected = sorted(sorted((center, x)) for x in ('W', 'G', 'C') if x != center)
        for vi in row['valid_variants']:
            variant = settings[vi]
            assert binding.binding_error(row['parse'], variant) is None
            compiled = model.compile_reading(row['parse'], variant)
            _, other_hazards, _ = bits.replay(row['parse'], variant)
            assert compiled['cargo'] == ['C', 'G', 'W']
            assert compiled['hazards'] == other_hazards == expected
            original_checks.append(dict(original=row['id'], variant_index=vi, center=center, hazards=expected))
    members = []
    inverse_count = 0
    for case in cases:
        assert case['variant'] == settings[case['variant_index']]
        for member in case['members']:
            row = original_by_id[member['original_id']]
            graph = model.compile_reading(row['parse'], case['variant'])['hazards']
            for rename in member['original_to_canonical']:
                translated = sorted(sorted(rename.get(x, x) for x in edge) for edge in graph)
                assert rename[row['code']['qokedy']] == 'C'
                assert translated == [['C', 'G'], ['C', 'W']]
                inverse_count += 1
            members.append((row['id'], case['context_index'], case['variant_index']))
    expected_members = [(row['id'], pi, vi) for row in originals for pi in (2, 4) for vi in row['valid_variants']]
    assert collections.Counter(members) == collections.Counter(expected_members)
    first_steps = []
    for cargo_load in (None, 'W', 'G', 'C'):
        positions = {x: 'L' for x in ('W', 'G', 'C')}
        positions['M'] = 'R'
        if cargo_load:
            positions[cargo_load] = 'R'
        bad = [list(edge) for edge in itertools.combinations(('C', 'G', 'W'), 2)
               if positions[edge[0]] == positions[edge[1]] != positions['M']]
        assert bad
        first_steps.append(dict(load=cargo_load, positions=positions, triangle_violations=bad))
    put('SOURCE_GRAPH_CHECK.json', dict(status='PASS', original_settings=original_checks,
                                      member_cases=len(members), inverse_maps=inverse_count,
                                      canonical_graph=[['C', 'G'], ['C', 'W']],
                                      triangle_first_step_proof=first_steps,
                                      scope='Existing original graph/quotient prerequisite;no added-paragraph union test or new fit.'))
    print(json.dumps(dict(status='PASS', original_settings=len(original_checks), members=len(members), inverse_maps=inverse_count)))


if __name__ == '__main__':
    main()

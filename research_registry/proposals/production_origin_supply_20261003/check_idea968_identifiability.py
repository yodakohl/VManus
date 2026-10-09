"""Small synthetic design check; no manuscript input or fitted model."""
from itertools import combinations, product
from math import comb
import json

def whole_base_copy(choice):
    base = ('ala', 'ara')[choice]
    return base + base + 'dy'

def feature_agreement(choice):
    # Two fixed positions realize a binary feature; no whole-base copy operation.
    feature = ('l', 'r')[choice]
    return ''.join(('a', feature, 'a', 'a', feature, 'a', 'd', 'y'))

def stored_whole(choice):
    return ('alaalady', 'araarady')[choice]

def main():
    # Equality holds pointwise for each input; arbitrary probability laws therefore agree.
    outputs = [whole_base_copy(i) for i in (0, 1)]
    assert outputs == [feature_agreement(i) for i in (0, 1)]
    assert outputs == [stored_whole(i) for i in (0, 1)]
    for n in range(7):
        for choices in product((0, 1), repeat=n):
            assert [whole_base_copy(c) for c in choices] == [feature_agreement(c) for c in choices]
    left = ['ala'] * 8 + ['ara'] * 8
    assert all(len(x) == 3 and x[0] == x[-1] == 'a' for x in left)
    # Equal half-length and identical seam a/a, single stipulated metadata stratum.
    observed = 16
    hist = {}
    for positions in combinations(range(16), 8):
        a_positions = set(positions)
        right = ['ala' if i in a_positions else 'ara' for i in range(16)]
        matches = sum(a == b for a, b in zip(left, right))
        hist[matches] = hist.get(matches, 0) + 1
    analytical = {2*k: comb(8, k)**2 for k in range(9)}
    assert hist == analytical
    assert sum(hist.values()) == comb(16, 8) == 12870
    assert hist[observed] == 1
    # A different genuine-copy corpus: seam-stratified reassignment cannot change identity.
    frozen = ['al'] * 8 + ['or'] * 8
    strata = {}
    for base in frozen:
        strata.setdefault((len(base), base[-1], base[0]), []).append(base)
    assert len(strata) == 2
    assert all(len(set(values)) == 1 for values in strata.values())
    out = {
        'status': 'MECHANISM_NOT_IDENTIFIABLE_BY_PROPOSED_STATISTIC',
        'scope': 'Synthetic mathematical design counterexample only; no Voynich observation or native word meaning.',
        'pointwise_equal_outputs': outputs,
        'mechanisms': ['whole-base copying', 'binary feature realized in two template positions', 'stored whole lookup'],
        'distribution_claim': 'Pointwise equality for either input implies identical observable distributions for any shared input law; not only equal repetition scores.',
        'synthetic_conditional_null': {'half_length': 3, 'seam': 'a/a', 'left_counts': {'ala': 8, 'ara': 8}, 'right_counts': {'ala': 8, 'ara': 8}, 'observed_matches': observed, 'permutation_histogram': dict(sorted(hist.items())), 'upper_tail': {'numerator': 1, 'denominator': 12870}, 'interpretation': 'Correctly rejects exchangeable independent pairing for this artificial corpus; cannot select copying among the three observationally identical mechanisms. This is not a manuscript p-value.'},
        'true_copy_zero_mobility_example': {'bases': ['al', 'or'], 'copies_per_base': 8, 'strata': [list(k) for k in strata], 'all_conditional_matches': 16, 'interpretation': 'No contrast capacity, not evidence against copying.'},
        'decision': 'Do not run IDEA968 as a discriminator of copying versus ordinary word-building. A descriptive pairing statistic remains mathematically possible but has no selected downstream writer decision.',
        'limits': ['Does not reject a real repeated-base construction.', 'Does not show these artificial words occur in the manuscript.', 'Does not invalidate conditional permutation tests when their actual null is justified.', 'Does not prove all future observable consequences of distinct fully specified writers equivalent.']
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

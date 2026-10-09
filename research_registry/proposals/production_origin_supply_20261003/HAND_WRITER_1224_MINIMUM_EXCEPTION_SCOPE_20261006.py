"""Reproduce the post-result final-category relaxation; no native acquisition."""
from pathlib import Path
import hashlib
import itertools
import json

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).with_suffix('.json')


def main():
    retained = json.loads(REPORT.read_text())
    source = ROOT / retained['source_path']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == retained['source_sha256']
    original = json.loads(source.read_text())
    capacity = original['model_final_capacity']
    assert capacity == 6
    for reader, row in original['readings'].items():
        counts = row['final_counts']
        total = row['internal_two_glyph_groups']
        assert len(counts) == 12 and sum(counts.values()) == total
        direct = total - sum(sorted(counts.values(), reverse=True)[:capacity])
        # Separate enumeration of every six-member allowed alphabet.
        alternatives = []
        for chosen in itertools.combinations(counts, capacity):
            excluded = set(counts).difference(chosen)
            alternatives.append((sum(counts[x] for x in excluded), sorted(chosen)))
        minimum = min(value for value, chosen in alternatives)
        optima = [chosen for value, chosen in alternatives if value == minimum]
        assert len(alternatives) == 924 and direct == minimum
        saved = retained['readings'][reader]
        assert saved['final_counts'] == counts
        assert saved['sample_groups'] == row['sample_groups']
        assert saved['eligible_internal_two_sign_groups'] == total
        assert saved['allowed_category_capacity'] == capacity
        assert saved['optimistic_minimum_exception_groups'] == minimum
        assert saved['fraction_of_eligible'] == minimum / total
        assert saved['fraction_of_full_saved_sample'] == minimum / row['sample_groups']
        assert saved['optimal_allowed_finals'] == optima
        assert saved['relaxed_final_only_covered_groups'] == total - minimum
        assert saved['exhaustive_subset_count'] == len(alternatives)
        print(f'{reader}: {minimum}/{total} short groups; '
              f'{minimum}/{row["sample_groups"]} saved groups; '
              f'optimal finals {optima}')
    print('PASS: saved arithmetic and all 924 subsets per reading agree')


if __name__ == '__main__':
    main()

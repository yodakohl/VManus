from pathlib import Path
from collections import Counter
import argparse
import hashlib
import itertools
import json

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
BOOKS = ('b4', 'w1', 'bs1', 'gr1')
READERS = ('IT2a', 'RF1b', 'ZL3b')
N = 8000


def read(path):
    return json.loads(path.read_text())


def run_budget(word):
    assert word
    _, group = next(itertools.groupby(reversed(word)))
    terminal = sum(1 for _ in group)
    return len(word), terminal, 1 + min(terminal, len(word) - 1)


def distribute(frequency, cells):
    assert frequency >= 0 and cells >= 1
    allocated = [0] * cells
    for occurrence in range(frequency):
        allocated[occurrence % cells] += 1
    return [n for n in allocated if n > 0]


def top(values, k):
    return sum(sorted(values, reverse=True)[:k])


def allocations(total, slots):
    if slots == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in allocations(total - first, slots - 1):
                yield (first,) + tail


def source_free_controls():
    allocation_checks = global_checks = merge_checks = 0
    for frequency in range(9):
        for budget in range(1, 5):
            balanced = distribute(frequency, budget)
            assert sum(balanced) == frequency
            assert len(balanced) == min(frequency, budget)
            assert balanced == sorted(balanced, reverse=True)
            for other in allocations(frequency, budget):
                assert sum(n > 0 for n in other) <= len(balanced)
                for k in range(budget + 1):
                    assert top(balanced, k) <= top(other, k)
                allocation_checks += 1
                # Check concatenation with unrelated counts, not only one block.
                for background in [(), (2, 5), (1, 1, 4)]:
                    for k in range(budget + len(background) + 1):
                        assert top(balanced + list(background), k) <= top(other + background, k)
                    global_checks += 1
    for size in range(2, 6):
        for values in itertools.product((1, 2, 3), repeat=size):
            for i, j in itertools.combinations(range(size), 2):
                merged = [v for k, v in enumerate(values) if k not in (i, j)] + [values[i] + values[j]]
                assert len(merged) == len(values) - 1
                assert all(top(merged, k) >= top(values, k) for k in range(size + 1))
                merge_checks += 1
    assert run_budget('.') == (1, 1, 1)
    assert run_budget('a') == (1, 1, 1)
    assert run_budget('aaaa') == (4, 4, 4)
    assert run_budget('abb') == (3, 2, 3)
    assert run_budget('aba') == (3, 1, 2)
    assert run_budget('a\u0301') == (2, 1, 2)  # no implicit Unicode normalization
    return {'status': 'PASS', 'source_free': True, 'source_or_native_data_read': False,
            'primary_runner_read_or_imported': False, 'allocation_checks': allocation_checks,
            'with_background_checks': global_checks, 'collision_checks': merge_checks,
            'run_budget_fixtures': 6}


def main():
    for path, expected in read(BASE / 'src/REGISTRATION_LOCK.json')['hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    source = read(ROOT / 'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json')
    old = read(ROOT / 'experiments/yolo/gdt1202_whole_word_two_alias_capacity/artifacts/RESULT.json')
    targets = read(ROOT / 'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json')['targets']
    result = read(BASE / 'artifacts/RESULT.json')
    frequencies = read(BASE / 'artifacts/FREQUENCIES.json')
    assert result['status'] == 'TERMINAL_RUN_VARIANT_ENVELOPE'
    assert set(source) == set(BOOKS) and set(result['books']) == set(BOOKS)
    assert set(frequencies) == set(BOOKS) and set(targets) == set(READERS)
    limits = {}
    for reader in READERS:
        target = targets[reader]
        assert target['tokens'] == N
        raw_types, raw_top = target['type_ratio'] * N, target['top10_share'] * N
        types, concentration = round(raw_types), round(raw_top)
        assert abs(raw_types - types) < 1e-12 and abs(raw_top - concentration) < 1e-12
        limits[reader] = {'native_types': types, 'native_top10_count': concentration,
                          'types_lower_count': types - 400, 'top10_upper_count': concentration + 400}
    assert limits == old['native_limits'] == result['native_limits']
    word_rows = source_tokens = comparisons = 0
    receipts = {}
    for book in BOOKS:
        flattened = [word for record in source[book] for word in record['words']]
        assert len(flattened) >= N and all(isinstance(w, str) and w for w in flattened)
        sample = flattened[:N]
        digest = hashlib.sha256(json.dumps(sample, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        counts = Counter(sample)
        table, mass, old_mass = [], [], []
        budget_counts = Counter()
        gains = losses = gaining_words = losing_words = 0
        for word, frequency in sorted(counts.items()):
            length, terminal, budget = run_budget(word)
            allocation = distribute(frequency, budget)
            old_allocation = distribute(frequency, 2)
            table.append({'word': word, 'count': frequency, 'length': length,
                          'terminal_run': terminal, 'alias_budget': budget, 'balanced_counts': allocation})
            mass.extend(allocation)
            old_mass.extend(old_allocation)
            budget_counts[budget] += 1
            difference = len(allocation) - len(old_allocation)
            gains += max(0, difference)
            losses += max(0, -difference)
            gaining_words += difference > 0
            losing_words += difference < 0
            word_rows += 1
        assert sum(mass) == sum(old_mass) == N
        old_book = old['books'][book]
        assert old_book['source_types'] == len(counts)
        assert old_book['two_alias_types_upper_count'] == len(old_mass)
        assert old_book['two_alias_top10_lower_count'] == top(old_mass, 10)
        upper, lower = len(mass), top(mass, 10)
        assert upper == len(old_mass) + gains - losses
        conditions = {}
        for reader in READERS:
            type_ok = upper >= limits[reader]['types_lower_count']
            top_ok = lower <= limits[reader]['top10_upper_count']
            conditions[reader] = {'types_not_excluded': type_ok,
                                  'concentration_not_excluded': top_ok,
                                  'not_excluded': type_ok and top_ok}
            comparisons += 1
        expected = {'source_types': len(counts),
                    'budget_type_counts': {str(k): v for k, v in sorted(budget_counts.items())},
                    'types_upper': upper, 'top10_lower': lower,
                    'type_gains_vs_two': gains, 'type_losses_vs_two': losses,
                    'gaining_words': gaining_words, 'losing_words': losing_words,
                    'top10_delta_vs_two': lower - top(old_mass, 10),
                    'ordered_sample_sha256': digest, 'reader_conditions': conditions}
        assert frequencies[book] == table, (book, 'frequency_table')
        assert result['books'][book] == expected, (book, 'summary')
        receipts[book] = {'types_upper': upper, 'top10_lower': lower,
                          'reader_conditions': conditions, 'old_two_alias_counts_verified': True}
        source_tokens += len(sample)
    controls = source_free_controls()
    output = {'status': 'PASS', 'source_prefix_tokens': source_tokens,
              'source_word_type_rows': word_rows, 'book_reader_comparisons': comparisons,
              'books': receipts, 'source_free_controls': controls,
              'scope': 'Independent original-codepoint run counts, round-robin alias allocation, inherited limits and necessary capacity gates; no native census, source identification, language ban or phonetic confirmation.'}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    if args.controls:
        output = source_free_controls()
        (BASE / 'artifacts/VALIDATOR_CONTROLS.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
        print(json.dumps(output, sort_keys=True))
    else:
        main()

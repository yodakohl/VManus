from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import re

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
TOKEN = re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
BOOKS = ('b4', 'w1', 'bs1', 'gr1')
READERS = ('IT2a', 'RF1b', 'ZL3b')
FAMILIES = ('CYCLIC', 'BAG')


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def least_rotation(word):
    assert word
    doubled = word + word
    return min(doubled[j:j + len(word)] for j in range(len(word)))


def same_circle(first, second):
    if len(first) != len(second):
        return False
    doubled = first + first
    return any(doubled[j:j + len(first)] == second for j in range(len(first)))


def orbit_table(rows, family):
    # Group independently by bag, then explicit cyclic-equivalence membership;
    # a canonical rotation is not used as the membership test.
    occurrences = defaultdict(list)
    for row in rows:
        occurrences[tuple(row['units'])].append(row['id'])
    bags = defaultdict(list)
    for word in sorted(occurrences):
        bags[tuple(sorted(Counter(word).items()))].append(word)
    groups = []
    for frequency_signature, words in sorted(bags.items()):
        if family == 'BAG':
            signature = tuple(u for u, n in frequency_signature for _ in range(n))
            groups.append((signature, words))
        else:
            assert family == 'CYCLIC'
            classes = []
            for word in words:
                for cls in classes:
                    if same_circle(cls[0], word):
                        cls.append(word)
                        break
                else:
                    classes.append([word])
            groups.extend((least_rotation(cls[0]), cls) for cls in classes)
    table = []
    for signature, members in sorted(groups, key=lambda x: x[0]):
        entries = [{'word': list(w), 'count': len(occurrences[w]),
                    'source_ids': occurrences[w]} for w in sorted(members)]
        table.append({'signature': list(signature),
                      'count': sum(m['count'] for m in entries), 'members': entries})
    assert len({tuple(t['signature']) for t in table}) == len(table)
    counts = sorted((r['count'] for r in table), reverse=True)
    summary = {'groups': len(rows), 'raw_types': len(occurrences),
               'orbit_types': len(table), 'sorted_counts': counts,
               'largest_orbit_count': max(counts),
               'top10_orbit_count': sum(counts[:10])}
    return table, summary


def envelope(source, target):
    source = sorted(source, reverse=True)
    target = sorted(target, reverse=True)
    assert source and target and min(source) > 0 and min(target) > 0
    assert sum(source) == sum(target)
    n = sum(source)
    sp = bp = best = witness = witness_s = witness_b = 0
    for k in range(1, max(len(source), len(target)) + 1):
        if k <= len(source):
            sp += source[k - 1]
        if k <= len(target):
            bp += target[k - 1]
        if sp - bp > best:
            best, witness, witness_s, witness_b = sp - bp, k, sp, bp
    types = max(0, len(target) - len(source))
    needed = max(types, best)
    return {'N': n, 'type_lower': types, 'prefix_lower': best,
            'k_witness': witness, 'source_prefix_sum': witness_s,
            'native_prefix_sum': witness_b, 'replacement_lower': needed,
            'fraction': [needed, n],
            'status': 'EXCLUDED_BY_NECESSARY_COUNTS' if needed else 'NOT_EXCLUDED'}


def source_free_controls():
    orbit_words = orbit_checks = 0
    fixture_rows = []
    for length in range(1, 7):
        for word in itertools.product(range(3), repeat=length):
            rotations = {word[i:] + word[:i] for i in range(length)}
            assert least_rotation(word) == sorted(rotations)[0]
            assert all(same_circle(word, w) for w in rotations)
            bag = tuple(sorted(word))
            assert all(tuple(sorted(w)) == bag for w in rotations)
            fixture_rows.append({'id': 'fixture_' + str(orbit_words), 'units': list(word)})
            orbit_words += 1
            orbit_checks += len(rotations)
    assert not same_circle((0, 1, 2), (2, 1, 0))
    for family in FAMILIES:
        table, summary = orbit_table(fixture_rows, family)
        direct = defaultdict(Counter)
        for row in fixture_rows:
            w = tuple(row['units'])
            signature = min(w[i:] + w[:i] for i in range(len(w))) if family == 'CYCLIC' else tuple(sorted(w))
            direct[signature][w] += 1
        assert {tuple(r['signature']): {tuple(m['word']): m['count'] for m in r['members']}
                for r in table} == {s: dict(members) for s, members in direct.items()}
        assert sum(summary['sorted_counts']) == len(fixture_rows)
    assignments = repairs = 0
    for types in range(1, 5):
        for weights in itertools.product((1, 2), repeat=types):
            for destinations in itertools.product(range(types), repeat=types):
                grouped = Counter()
                for weight, destination in zip(weights, destinations):
                    grouped[destination] += weight
                counts = sorted(grouped.values(), reverse=True)
                assert envelope(weights, counts)['replacement_lower'] == 0
                assignments += 1
                # Every one-item move from a true coarsening has D <= 1.
                for old in range(len(counts)):
                    for new in range(len(counts) + 1):
                        changed = counts[:] + [0]
                        changed[old] -= 1
                        changed[new] += 1
                        changed = [v for v in changed if v]
                        assert envelope(weights, changed)['replacement_lower'] <= 1
                        repairs += 1
    # Necessary inequalities are not an integer coarsening solver.
    assert envelope([2, 2], [3, 1])['replacement_lower'] == 0
    assert tuple([3, 1]) not in {(4,), (2, 2)}
    assert envelope([2, 2], [2, 2])['k_witness'] == 0
    assert envelope([4], [1, 1, 1, 1])['replacement_lower'] == 3
    return {'status': 'PASS', 'native_data_read': False,
            'primary_runner_read_or_imported': False,
            'short_words': orbit_words, 'rotation_checks': orbit_checks,
            'coarsening_assignments': assignments, 'one_replacement_checks': repairs,
            'necessary_not_sufficient_fixture': True}


def main():
    for path, expected in read(BASE / 'src/REGISTRATION_LOCK.json')['hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    native = read(ROOT / 'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')
    allowed = {r['page'] for r in csv.DictReader(
        (ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),
        delimiter='\t')}
    sources = read(ROOT / 'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json')
    result = read(BASE / 'artifacts/RESULT.json')
    tables = read(BASE / 'artifacts/ORBIT_TABLES.json.gz')
    profiles = read(BASE / 'artifacts/SOURCE_PROFILES.json')
    assert result['status'] == 'ORBIT_COARSENING_ENVELOPES'
    assert set(native) == set(READERS) and set(sources) == set(BOOKS)
    expected_native = {f'{reader}_{panel}_{family}' for reader in READERS
                       for panel in ['FULL', 'FIRST8000'] for family in FAMILIES}
    assert set(result['native']) == expected_native and set(tables) == expected_native
    assert set(result['sources']) == set(BOOKS) and set(profiles) == set(BOOKS)
    assert set(result['comparisons']) == {f'{reader}_{family}_{book}' for reader in READERS
                                        for family in FAMILIES for book in BOOKS}
    groups = orbit_members = 0
    summaries = {}
    for reader in READERS:
        rows = native[reader]
        assert len(rows) >= 8000 and len({r['id'] for r in rows}) == len(rows)
        for row in rows:
            assert row['page'] in allowed and not row['page'].startswith('f84')
            assert row['page'] not in ['f1r', 'f116v'] and row['kind'] == 'P'
            assert row['left_separator'] == row['right_separator'] == 'DEFINITE_SPACE'
            parsed = TOKEN.findall(row['ivtff_group_raw'])
            assert parsed and parsed == row['units'] and ''.join(parsed) == row['ivtff_group_raw']
            groups += 1
        assert len({u for row in rows for u in row['units']}) == 22
        for panel, selected in [('FULL', rows), ('FIRST8000', rows[:8000])]:
            for family in FAMILIES:
                key = f'{reader}_{panel}_{family}'
                table, summary = orbit_table(selected, family)
                assert tables[key] == table, (key, 'orbit_members_or_support')
                assert result['native'][key] == summary, (key, 'summary')
                summaries[key] = summary
                orbit_members += sum(len(r['members']) for r in table)
    source_vectors = {}
    for book in BOOKS:
        ordered = [word for record in sources[book] for word in record['words']]
        assert len(ordered) >= 8000 and all(isinstance(w, str) and w for w in ordered)
        sample = ordered[:8000]
        digest = hashlib.sha256(json.dumps(sample, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        counts = Counter(sample)
        vector = sorted(counts.values(), reverse=True)
        profile = {'word_counts': [[word, n] for word, n in sorted(counts.items())],
                   'ordered_sample_sha256': digest}
        assert profiles[book] == profile, (book, 'profile')
        assert result['sources'][book] == {'groups': 8000, 'source_types': len(counts),
                                           'sorted_counts': vector, 'ordered_sample_sha256': digest}
        source_vectors[book] = vector
    decisions = {}
    for reader in READERS:
        for family in FAMILIES:
            vector = summaries[f'{reader}_FIRST8000_{family}']['sorted_counts']
            for book in BOOKS:
                key = f'{reader}_{family}_{book}'
                expected = envelope(source_vectors[book], vector)
                assert result['comparisons'][key] == expected, (key, 'comparison')
                decisions[key] = {'D': expected['replacement_lower'], 'status': expected['status']}
    controls = source_free_controls()
    output = {'status': 'PASS', 'original_native_groups_checked': groups,
              'native_panels': len(summaries), 'orbit_member_rows_checked': orbit_members,
              'source_prefix_groups_checked': 8000 * len(BOOKS), 'comparisons_checked': len(decisions),
              'comparisons': decisions, 'source_free_controls': controls,
              'scope': 'Independent orbit equivalence, exact source prefixes, all counts and necessary replacement bounds; not source identification, sufficient coarsening, estimated errors, phonetic or historical confirmation.'}
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

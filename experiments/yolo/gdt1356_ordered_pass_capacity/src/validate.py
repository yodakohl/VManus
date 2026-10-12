from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
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


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def leaf(row):
    return int(re.match(r'f(\d+)', row['page'])[1])


def cycles(word):
    intervals = tuple((i, j) for i in range(len(word))
                      for j in range(i + 1, len(word))
                      if word[i] == word[j] and len(set(word[i:j + 1])) > 1)

    @lru_cache(None)
    def suffix(begin):
        choices = [()]
        for i, j in intervals:
            if i >= begin:
                choices.append(((i, j),) + suffix(j))
        return min(choices, key=lambda p: (-len(p), p))

    return suffix(0)


def passes(word, rank):
    return 1 + sum(rank[a] > rank[b] for a, b in zip(word, word[1:]))


def pieces(word, rank):
    starts = [0] + [j for j in range(1, len(word))
                    if rank[word[j - 1]] > rank[word[j]]]
    stops = starts[1:] + [len(word)]
    return [list(word[i:j]) for i, j in zip(starts, stops)]


def support(word, rows):
    return {'word': list(word), 'count': len(rows),
            'physical_leaves': sorted({leaf(r) for r in rows}),
            'first_row': rows[0]}


def aggregate(words):
    edges = Counter((a, b) for w in words for a, b in zip(w, w[1:]) if a != b)
    pairs = {tuple(sorted((a, b))) for a, b in edges}
    total = sum(min(edges[a, b], edges[b, a]) for a, b in pairs)
    return {'lower': 1 + (total + len(words) - 1) // len(words),
            'sum_min_edges': total, 'type_count': len(words),
            'edges': [[a, b, n] for (a, b), n in sorted(edges.items())]}


def source_free_controls():
    checked = 0
    alphabet = (0, 1, 2)
    orders = list(itertools.permutations(alphabet))
    for length in range(1, 7):
        for word in itertools.product(alphabet, repeat=length):
            pack = cycles(word)
            assert all(word[i] == word[j] and len(set(word[i:j + 1])) > 1
                       for i, j in pack)
            assert all(a[1] <= b[0] for a, b in zip(pack, pack[1:]))
            # Independent earliest-finish scheduling verifies the maximum count.
            eligible = sorted(((j, i) for i in range(length)
                               for j in range(i + 1, length)
                               if word[i] == word[j] and len(set(word[i:j + 1])) > 1))
            endpoint = count = 0
            for end, begin in eligible:
                if begin >= endpoint:
                    count += 1
                    endpoint = end
            assert count == len(pack)
            # Independent exhaustive packing checks the lexicographic tie too.
            intervals = sorted((i, j) for j, i in eligible)
            all_packings = []
            for mask in range(1 << len(intervals)):
                selected = tuple(p for j, p in enumerate(intervals) if mask >> j & 1)
                if all(a[1] <= b[0] for a, b in zip(selected, selected[1:])):
                    all_packings.append(selected)
            assert pack == min(all_packings, key=lambda p: (-len(p), p))
            unequal = sum(a != b for a, b in zip(word, word[1:]))
            for order in orders:
                rank = {a: i for i, a in enumerate(order)}
                score = passes(word, rank)
                segmentation = pieces(word, rank)
                assert score == len(segmentation)
                assert tuple(u for part in segmentation for u in part) == word
                assert all(all(rank[a] <= rank[b] for a, b in zip(part, part[1:]))
                           for part in segmentation)
                assert score >= 1 + len(pack)
                revscore = passes(word[::-1], rank)
                assert score + revscore - 2 == unequal
                assert max(score, revscore) >= 1 + (unequal + 1) // 2
                checked += 1
    small = list(itertools.product(alphabet, repeat=1)) + list(itertools.product(alphabet, repeat=2))
    collections = 0
    for panel in itertools.combinations(small, 3):
        lower = aggregate(panel)['lower']
        for order in orders:
            rank = {a: i for i, a in enumerate(order)}
            assert lower <= max(passes(w, rank) for w in panel)
        collections += 1
    assert cycles(tuple('ABACA')) == ((0, 2), (2, 4))
    assert cycles(tuple('AAAA')) == ()
    return {'word_order_checks': checked, 'three_type_collections': collections}


def main():
    lock = read(BASE / 'src/REGISTRATION_LOCK.json')
    for path, expected in lock['hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    data = read(ROOT / 'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')
    allowed = {r['page'] for r in csv.DictReader(
        (ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),
        delimiter='\t')}
    result = read(BASE / 'artifacts/RESULT.json')
    assert result['status'] == 'CERTIFIED_ORDERED_PASS_INTERVALS'
    assert set(data) == {'IT2a', 'RF1b', 'ZL3b'}
    assert set(result['panels']) == {reader + '_' + part for reader in data for part in ['FULL', 'GE2']}
    receipts = {}
    original_groups = word_checks = interval_checks = 0
    for reader, rows in sorted(data.items()):
        whole = defaultdict(list)
        for row in rows:
            assert row['page'] in allowed and not row['page'].startswith('f84')
            assert row['page'] not in ['f1r', 'f116v'] and row['kind'] == 'P'
            assert row['left_separator'] == row['right_separator'] == 'DEFINITE_SPACE'
            tokens = TOKEN.findall(row['ivtff_group_raw'])
            assert tokens == row['units'] and ''.join(tokens) == row['ivtff_group_raw']
            assert tokens
            whole[tuple(tokens)].append(row)
            original_groups += 1
        for panel_name in ['FULL', 'GE2']:
            panel = {w: rr for w, rr in whole.items()
                     if panel_name == 'FULL' or len({leaf(r) for r in rr}) >= 2}
            words = sorted(panel)
            alphabet = sorted({a for w in words for a in w})
            assert len(alphabet) == 22
            name = reader + '_' + panel_name
            got = result['panels'][name]
            assert got['groups'] == sum(map(len, panel.values())) and got['types'] == len(panel)
            packs = {w: cycles(w) for w in words}
            cw = min(words, key=lambda w: (-len(packs[w]), w))
            cexpected = {**support(cw, panel[cw]), 'lower': 1 + len(packs[cw]),
                         'intervals': [list(p) for p in packs[cw]]}
            assert got['bounds']['cycle'] == cexpected, (name, 'cycle')
            interval_checks += len(packs[cw])
            reversible = [w for w in words if w[::-1] in panel]
            if reversible:
                def bound(w):
                    m = sum(a != b for a, b in zip(w, w[1:]))
                    return 1 + (m + 1) // 2
                rw = min(reversible, key=lambda w: (-bound(w), w))
                rexpected = {**support(rw, panel[rw]), 'lower': bound(rw),
                             'reverse_support': support(rw[::-1], panel[rw[::-1]])}
            else:
                rexpected = {'lower': 1}
            assert got['bounds']['reverse'] == rexpected, (name, 'reverse')
            agg = aggregate(words)
            assert got['bounds']['aggregate'] == agg, (name, 'aggregate')
            lower = max(1, cexpected['lower'], rexpected['lower'], agg['lower'])
            assert got['L'] == lower
            order = got['rank']
            assert len(order) == 22 and sorted(order) == alphabet
            rank = {a: i for i, a in enumerate(order)}
            scores = {w: passes(w, rank) for w in words}
            upper = max(scores.values())
            assert got['U'] == upper and lower <= upper and got['exact'] == (lower == upper)
            ht = Counter(scores.values())
            hn = Counter()
            for w in words:
                hn[scores[w]] += len(panel[w])
                word_checks += 1
            assert got['hist_type'] == {str(k): v for k, v in sorted(ht.items())}
            assert got['hist_token'] == {str(k): v for k, v in sorted(hn.items())}
            mw = min(w for w in words if scores[w] == upper)
            assert got['max_word'] == {**support(mw, panel[mw]), 'segments': pieces(mw, rank)}
            fallback = max(passes(w, {a: i for i, a in enumerate(alphabet)}) for w in words)
            planned = [k for k in [lower, lower + 1, lower + 2] if k < fallback]
            attempts = got['attempts']
            sat_seen = False
            for idx, attempt in enumerate(attempts):
                assert idx < len(planned) and attempt['K'] == planned[idx] and not sat_seen
                answer = attempt['answer'].lower()
                assert answer in ['sat', 'unsat', 'unknown']
                if answer == 'sat':
                    sat_seen = True
                    assert upper <= attempt['K']
            if not sat_seen:
                assert len(attempts) == len(planned) and order == alphabet and upper == fallback
            receipts[name] = {'L': lower, 'U': upper, 'exact': lower == upper,
                              'upper_rank_replayed': True, 'solver_unsat_used_as_proof': False}
    controls = source_free_controls()
    output = {'status': 'PASS', 'original_source_groups': original_groups,
              'whole_type_rank_checks': word_checks, 'closed_walk_witnesses': interval_checks,
              'panels': receipts, 'source_free_controls': controls,
              'scope': 'Independent bounds, source accounting and explicit upper-rank replay; no timed solver rerun, native values, historical or phonetic confirmation.'}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true', help='source-free fixtures only')
    args = parser.parse_args()
    if args.controls:
        output = {'status': 'PASS', 'native_data_read': False,
                  'primary_runner_read_or_imported': False, **source_free_controls()}
        (BASE / 'artifacts/VALIDATOR_CONTROLS.json').write_text(
            json.dumps(output, indent=2, sort_keys=True) + '\n')
        print(json.dumps(output, sort_keys=True))
    else:
        main()

#!/usr/bin/env python3
"""Independent regex domains and recomputation of the saved capacity census."""
import collections as C
import concurrent.futures
import gzip
import hashlib
import json
from pathlib import Path
import re
import feasibility as source

HERE = Path(__file__).resolve().parent


def load(name):
    raw = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def regex(written, classes):
    return re.compile(''.join('(?:' + '|'.join(re.escape(a) for a in
                      classes.get(ch, {'alternatives': [ch]})['alternatives']) + ')'
                      for ch in written))


def verify_book(args):
    book, ref, domain, rows, classes = args
    vocab = ref['counts']
    texts = set(domain)
    for row in rows:
        for n in row['neighbours'].values():
            if n is not None and n['native'] is not None:
                texts.add(n['native'])
    checked = {}
    patterns = {}
    for t in sorted(texts):
        p = patterns[t] = regex(t, classes)
        checked[t] = sorted((v for v in vocab if p.fullmatch(v)), key=lambda v: (-vocab[v], v))
    assert all(checked[t] == d for t, d in domain.items())
    bg = {(a, b): n for a, b, n in ref['bigrams']}
    raw = set(ref['written'])
    for row in rows:
        t, gold = row['native'], row['gold']
        cs = checked[t] if t is not None else []
        assert row['partition'] == ('UNKNOWN_WRITTEN' if t is None else
                                    'SHARED' if t in raw else 'NOVEL')
        assert row['domain_size'] == len(cs)
        top = cs[0] if cs else None
        assert row['frequency_choice'] == top
        ties = [c for c in cs if vocab[c] == vocab[top]] if cs else []
        assert row['frequency_ties'] == ties
        supports = {c: {} for c in cs}
        for side in ('left', 'right'):
            n = row['neighbours'][side]
            ns = checked[n['native']] if n is not None and n['native'] is not None else []
            if n:
                assert n['candidates'] == ns
            for c in cs:
                hits = [[v, bg[(v, c) if side == 'left' else (c, v)]] for v in ns
                        if (v, c) in bg] if side == 'left' else [
                        [v, bg[(c, v)]] for v in ns if (c, v) in bg]
                supports[c][side] = hits
        assert row['candidate_support'] == supports
        supported = [c for c in cs if supports[c]['left'] or supports[c]['right']]
        sole = supported[0] if len(supported) == 1 else None
        rc = (t is not None and gold is not None and patterns[t].fullmatch(gold) is not None)
        flags = dict(rule_covered=rc,
                     reference_covered=gold is not None and gold in vocab,
                     intersection_covered=gold is not None and gold in cs,
                     frequency_correct=gold is not None and gold == top,
                     gold_in_frequency_tie=gold is not None and gold in ties,
                     ambiguous=len(cs) > 1,
                     gold_covered_ambiguous=gold is not None and gold in cs and len(cs) > 1,
                     support_differs=0 < len(supported) < len(cs),
                     gold_sole_supported=gold is not None and gold == sole and len(cs) > 1,
                     wrong_sole_supported=sole is not None and sole != gold and len(cs) > 1,
                     support_repairs_frequency_error=(gold is not None and sole == gold
                                                     and top != gold and len(cs) > 1))
        assert all(row[k] == v for k, v in flags.items()), row['id']
    return dict(book=book, full_domain_checks=len(checked), rows=len(rows))


def main():
    result = load('FEASIBILITY_RESULT.json')
    for name, h in {**result['inputs'], **result['artifacts']}.items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == h
    refs, domains, rows = [load(n) for n in ('FEASIBILITY_REFERENCES.json.gz',
                                           'FEASIBILITY_DOMAINS.json.gz', 'FEASIBILITY_ROWS.json.gz')]
    books, rules = source.source_groups()  # shared projector replay, not independent paleography
    full = {w['id']: w for groups in books.values() for w in groups}
    expected_ids = {w['id'] for w in full.values() if w['selected']}
    assert len(rows) == len(expected_ids) == 11724
    assert {r['id'] for r in rows} == expected_ids
    for book, ref in refs.items():
        others = [g for b, g in books.items() if b != book]
        assert ref['counts'] == dict(C.Counter(w['expanded'] for g in others for w in g
                                              if '\uFFFC' not in w['expanded']))
        assert ref['written'] == sorted({''.join(w['native']) for g in others for w in g
                                        if None not in w['native']})
        bg = C.Counter()
        for groups in others:
            for i in range(1, len(groups)):
                a, b = groups[i-1:i+1]
                if (a['record'] is not None and a['record'] == b['record']
                    and '\uFFFC' not in a['expanded'] + b['expanded']):
                    bg[(a['expanded'], b['expanded'])] += 1
        assert ref['bigrams'] == [[a, b, n] for (a, b), n in sorted(bg.items())]
    positions = {w['id']: (g, i) for g in books.values() for i, w in enumerate(g)}
    for r in rows:
        w = full[r['id']]
        assert r['gold'] == (w['expanded'] if '\uFFFC' not in w['expanded'] else None)
        assert r['native_units'] == w['native'] and r['locator'] == w['locator']
        assert r['status'] == w['status'] and r['record'] == w['record']
        g, i = positions[r['id']]
        for side, delta in (('left', -1), ('right', 1)):
            n = g[i+delta] if 0 <= i+delta < len(g) else None
            if n is not None and (n['record'] is None or n['record'] != w['record']):
                n = None
            assert (r['neighbours'][side]['id'] if r['neighbours'][side] else None) == (n['id'] if n else None)
    jobs = [(b, refs[b], domains[b], [r for r in rows if r['book'] == b], rules['classes'])
            for b in books]
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
        checks = list(pool.map(verify_book, jobs))
    bools = [k for k, v in rows[0].items() if isinstance(v, bool)]
    for book, partitions in result['summaries'].items():
        for part, summary in partitions.items():
            rr = [r for r in rows if (book == 'ALL' or r['book'] == book)
                  and (part == 'ALL' or r['partition'] == part)]
            tt = C.defaultdict(list)
            for r in rr:
                if r['native'] is not None:
                    tt[(r['book'], r['native'])].append(r)
            assert summary['occurrences'] == len(rr) and summary['book_written_types'] == len(tt)
            assert summary['unresolved'] == sum(r['status'] == 'UNRESOLVED' for r in rr)
            assert summary['empty_domains'] == sum(r['domain_size'] == 0 for r in rr)
            assert summary['singleton_domains'] == sum(r['domain_size'] == 1 for r in rr)
            assert all(summary[k] == sum(r[k] for r in rr) for k in bools)
            assert summary['oracle_headroom_occurrences'] == sum(r['intersection_covered'] - r['frequency_correct'] for r in rr)
            for k, number in summary['type_macro'].items():
                answer = sum(sum(r[k] for r in v) / len(v) for v in tt.values()) / len(tt) if tt else None
                assert answer == number
    receipt = dict(status='CAPACITY_ACCOUNTING_PASS', rows=len(rows), book_checks=checks,
                   result_sha256=hashlib.sha256((HERE / 'FEASIBILITY_RESULT.json').read_bytes()).hexdigest(),
                   validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   scope='independent regex intersection and census arithmetic; projector reused; no model performance')
    novel = [r for r in rows if r['partition'] == 'NOVEL']
    receipt['posthoc_support_crosstab'] = {
        'frequency_wrong_gold_sole_supported': sum(r['support_repairs_frequency_error'] for r in novel),
        'frequency_correct_wrong_sole_supported': sum(r['frequency_correct'] and r['wrong_sole_supported'] for r in novel),
        'scope': 'descriptive cross-tab requested after census; no registered contextual ranker'}
    (HERE / 'FEASIBILITY_VALIDATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()

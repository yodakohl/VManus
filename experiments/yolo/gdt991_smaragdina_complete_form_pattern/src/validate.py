#!/usr/bin/env python3
"""No import of runner/pattern; reconstruct trees, replay positives, reverse negatives."""
import collections
import concurrent.futures
import csv
import datetime
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time
from reverse import check

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'


def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def put(name, obj):
    raw = (json.dumps(obj, separators=(',', ':')) + '\n').encode()
    (A / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)


def tree(node, order, cid, role=0, path=()):
    if isinstance(node, str):
        return [dict(root=node, role=role, clause=cid, path=list(path), terminal=True)]
    item = dict(root=node[0], role=0, clause=cid, path=list(path), terminal=False)
    children = [tree(child, order, cid, i, path + (i,)) for i, child in enumerate(node[1:], 1)]
    if node[0] in ('AND', 'IF', 'PURPOSE', 'BECAUSE'):
        return children[0] + [item] + children[1]
    if order.endswith('REVERSE'):
        children.reverse()
    flat = sum(children, [])
    return [item] + flat if order.startswith('PREFIX') else flat + [item]


def ground(events, words, forms):
    values = {(f['root'], f['role']): f['value'] for f in forms}
    assert len(values) == len(forms)
    assert set(values) == {(e['root'], e['role']) for e in events}
    strings = [values[(e['root'], e['role'])] for e in events]
    assert all(type(v) is str and v and '|' not in v for v in strings)
    assert ''.join(strings) == ''.join(words)
    assert set(itertools.accumulate(map(len, words))).issubset(set(itertools.accumulate(map(len, strings))))
    return values


def original(events, values, factor):
    roots, frames = factor['roots'], factor['frames']
    assert set(roots) == {e['root'] for e in events}
    assert all(type(v) is str and v for v in roots.values())
    assert len(set(roots.values())) == len(roots)
    assert set(frames) == {side + str(e['role']) for e in events if e['role'] for side in ('P', 'S')}
    for e in events:
        r = str(e['role'])
        actual = frames.get('P' + r, '') + roots[e['root']] + frames.get('S' + r, '')
        assert values[(e['root'], e['role'])] == actual


def reverse_job(job, deadline, cap):
    left = deadline - time.time()
    if left <= 0:
        return dict(status='UNKNOWN_REVERSE_QUEUE_LIMIT')
    try:
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'], input=json.dumps(job),
                           text=True, capture_output=True, timeout=min(left, cap))
        if p.returncode:
            return dict(status='ERROR_REVERSE_WORKER', returncode=p.returncode)
        return json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        return dict(status='UNKNOWN_REVERSE_LIMIT')


def main():
    if '--worker' in sys.argv:
        job = json.load(sys.stdin)
        print(json.dumps(check(job['events'], job['words'])))
        return
    for name, digest in read(E / 'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    own = read(E / 'src/SOURCE.json')
    source = read(ROOT / own['original_source'])
    streams = {}
    for v, spec in source['variants'].items():
        for w in source['writers']:
            events = sum((tree(c['tree'], w, c['id']) for c in spec['clauses']), [])
            assert events == spec['streams'][w]
            streams[v, w] = events
    old = read(ROOT / own['original_cases'])
    cases = read(A / 'PRIMARY_CASES.json.gz')
    assert len(cases) == len(old) == 32376
    assert [c['case'] for c in cases] == list(range(1, len(cases) + 1))
    panel = read(ROOT / own['paragraphs'])
    targets = {}
    for ed, ps in panel.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page'] != 'f116v'
            targets[ed, p['id']] = [x for line in p['lines'] for x in line['words']]
    jobs = []
    positives = full = 0
    alignment = []
    for prior, current in zip(old, cases):
        for k, val in prior.items():
            if k != 'status':
                assert current[k] == val, (current['case'], k)
        assert current['original_status'] == prior['status']
        if prior['status'] != 'UNKNOWN_UNRETAINED_SOLVER_RESULT':
            assert current['status'] == prior['status']
            continue
        events = streams[current['variant'], current['writer']]
        words = targets[current['edition'], current['paragraph']]
        outcome = current['pattern']
        if outcome['status'] == 'NO_COMPLETE_ROLE_FORM_PATTERN':
            jobs.append((current['case'], dict(events=events, words=words)))
        elif outcome['status'] == 'COMPLETE_ROLE_FORM_PATTERN_WITNESS':
            values = ground(events, words, outcome['forms'])
            positives += 1
            if outcome['factorization']['status'] == 'FULL_ORIGINAL_CODE_WITNESS':
                original(events, values, outcome['factorization'])
                full += 1
                start = 0
                ends = list(itertools.accumulate(map(len, words)))
                rows = []
                for e in events:
                    val = values[(e['root'], e['role'])]
                    wi = next(i for i, end in enumerate(ends) if end > start)
                    rows.append(dict(**e, value=val, start=start, end=start + len(val), word_index=wi, word=words[wi]))
                    start += len(val)
                alignment.append(dict(case=current['case'], edition=current['edition'], paragraph=current['paragraph'],
                                      variant=current['variant'], writer=current['writer'], alignment=rows,
                                      factorization=outcome['factorization']))
        else:
            assert outcome['status'].startswith(('UNKNOWN_', 'ERROR_'))
    deadline = read(A / 'EXECUTION_RECEIPT.json')['shared_deadline_unix']
    journal_path = A / 'REVERSE_JOURNAL.jsonl'
    if '--assemble' not in sys.argv:
        with journal_path.open('x') as journal:
            with concurrent.futures.ThreadPoolExecutor(max_workers=own['limits']['workers']) as pool:
                futures = {pool.submit(reverse_job, job, deadline, own['limits']['reverse_seconds']): cid for cid, job in jobs}
                for done, f in enumerate(concurrent.futures.as_completed(futures), 1):
                    row = dict(case=futures[f], outcome=f.result())
                    journal.write(json.dumps(row, separators=(',', ':')) + '\n')
                    journal.flush()
                    if done % 64 == 0 or done == len(jobs):
                        print(json.dumps(dict(reverse_completed=done, of=len(jobs), latest=row['outcome']['status'])), flush=True)
    reverse_rows = [json.loads(s) for s in journal_path.read_text().splitlines() if s.strip()]
    rev = {r['case']: r['outcome'] for r in reverse_rows}
    assert len(rev) == len(reverse_rows)
    checked = conflicts = 0
    for c in cases:
        if c['status'] != 'NO_COMPLETE_ROLE_FORM_PATTERN':
            assert c['case'] not in rev
            continue
        r = rev.pop(c['case'], dict(status='UNKNOWN_REVERSE_UNRETAINED'))
        c['reverse'] = r
        if r['status'] == 'REVERSE_EXHAUSTED':
            c['status'] = 'CONTRADICTED_COMPLETE_ROLE_FORM_PATTERN'
            checked += 1
        elif r['status'] == 'REVERSE_WITNESS':
            c['status'] = 'INVALID_PRIMARY_REVERSE_CONFLICT'
            ground(streams[c['variant'], c['writer']], targets[c['edition'], c['paragraph']], r['forms'])
            conflicts += 1
        else:
            c['status'] = 'PRIMARY_PATTERN_EXHAUSTION_UNCORROBORATED'
    assert not rev
    counts = dict(collections.Counter(c['status'] for c in cases))
    unresolved = 1980 - checked - full
    result = dict(experiment='GDT991', cases=len(cases), new_pattern_cases=1980, status_counts=counts,
                  new_corroborated_contradictions=checked, saved_pattern_witnesses=positives,
                  original_code_witness_cases=full, original_equations_remaining_unresolved=unresolved,
                  remaining_fraction=unresolved/1980, fixed_ninety_percent_stop=unresolved/1980 >= .9,
                  decision='INVALID_PRIMARY_REVERSE_CONFLICT' if conflicts else
                           'CONDITIONAL_COMPLETE_CODES' if full else
                           'STOP_UNRESOLVED_PATTERN_SEARCH' if unresolved/1980 >= .9 else
                           'NECESSARY_PATTERN_CONTRADICTIONS_NO_CODE',
                  independent_meaning_confirmation_capacity=0, confirmed_translated_words=0,
                  significance_claim=False, code_uniqueness_claim=False)
    validation = dict(status='FAIL' if conflicts else 'PASS', scope='case/source/positive replay and bounded separate reverse checks',
                      cases=len(cases), source_streams=len(streams), pattern_witnesses=positives, full_codes=full,
                      primary_negatives=len(jobs), corroborated_negatives=checked, conflicts=conflicts,
                      uncorroborated_negatives=len(jobs)-checked-conflicts,
                      author_independence=False, meaning_validation=False)
    put('CASES.json.gz', cases)
    put('RESULT.json', result)
    put('VALIDATION.json', validation)
    put('COMPLETE_ALIGNMENTS.json.gz', alignment)
    cols = ['case','edition','paragraph','leaf','variant','writer','original_status','status','source_forms','target_groups','independent_meaning_confirmation_capacity']
    with (A / 'CANDIDATES.tsv').open('w', newline='') as f:
        out = csv.DictWriter(f, cols, delimiter='\t', lineterminator='\n', extrasaction='ignore')
        out.writeheader()
        out.writerows(cases)
    receipt = read(A / 'EXECUTION_RECEIPT.json')
    receipt.update(validation_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    put('EXECUTION_RECEIPT.json', receipt)
    print(json.dumps(result, indent=2))
    print(json.dumps(validation, indent=2))
    if conflicts:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

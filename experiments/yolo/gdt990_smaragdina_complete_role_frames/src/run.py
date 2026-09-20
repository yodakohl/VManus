#!/usr/bin/env python3
"""Execute all frozen complete source/paragraph equations after publication."""
import concurrent.futures
import collections
import csv
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from model import necessary, solve

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'


def read(p):
    return json.loads(p.read_text())


def put(name, obj):
    data = (json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    (A / name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)


def isolated(job, deadline, limit):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return dict(status='UNKNOWN_QUEUE_LIMIT')
    timeout = min(limit, remaining)
    try:
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'],
                           input=json.dumps(job), text=True, capture_output=True, timeout=timeout)
        if p.returncode:
            return dict(status='ERROR_WORKER', returncode=p.returncode,
                        error_type=p.stderr.strip().splitlines()[-1][:160] if p.stderr.strip() else 'no_message')
        return json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        return dict(status='UNKNOWN_GLOBAL_LIMIT' if remaining < limit else 'UNKNOWN_PROCESS_LIMIT')
    except Exception as exc:
        return dict(status='ERROR_PROTOCOL', error_type=type(exc).__name__)


def main():
    if '--worker' in sys.argv:
        job = json.load(sys.stdin)
        print(json.dumps(solve(job['events'], job['words'], job['seconds'], project=True), separators=(',', ':')))
        return
    for path, digest in read(E / 'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    source = read(E / 'src/SOURCE.json')
    started = time.monotonic()
    started_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    paragraphs = read(ROOT / source['input_paragraphs'])
    cases, jobs, targets = [], [], {}
    limits = source['limits']
    deadline = started + limits['global_solver_seconds']
    for edition, panel in paragraphs.items():
        for p in panel:
            assert not p['page'].startswith('f84') and p['page'] != 'f116v'
            words = [w for line in p['lines'] for w in line['words']]
            assert len(words) == p['groups']
            targets[(edition, p['id'])] = words
            eligible = all(line['anchor_eligible'] for line in p['lines'])
            for variant, spec in source['variants'].items():
                pre = necessary(spec['streams'][source['writers'][0]], words) if eligible else None
                for writer in source['writers']:
                    row = dict(case=len(cases) + 1, edition=edition, paragraph=p['id'], page=p['page'],
                               leaf=p['leaf'], variant=variant, writer=writer, source_forms=spec['forms'],
                               source_root_types=spec['root_types'], target_groups=len(words),
                               independent_meaning_confirmation_capacity=0)
                    if not eligible:
                        row.update(status='UNKNOWN_SOURCE', ineligible_lines=[x['locus'] for x in p['lines'] if not x['anchor_eligible']])
                    elif pre['status'] != 'REQUIRES_FULL_EQUATION':
                        row.update(status=pre['status'], necessary=pre)
                    else:
                        row['status'] = 'PENDING'
                        jobs.append((len(cases), dict(events=spec['streams'][writer], words=words, seconds=limits['solver_seconds'])))
                    cases.append(row)
    print(json.dumps(dict(prepared_cases=len(cases), solver_jobs=len(jobs), necessary_statuses=dict(collections.Counter(c['status'] for c in cases)))), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=limits['workers']) as pool:
        futures = {pool.submit(isolated, job, deadline, limits['external_case_seconds']): i for i, job in jobs}
        for done, f in enumerate(concurrent.futures.as_completed(futures), 1):
            index = futures[f]
            cases[index].update(f.result())
            if done % 32 == 0 or done == len(jobs):
                print(json.dumps(dict(completed=done, of=len(jobs), latest=cases[index]['status'])), flush=True)
    counts = collections.Counter(c['status'] for c in cases)
    assert not counts['PENDING']
    computational = sum(n for k, n in counts.items() if k.startswith(('UNKNOWN_', 'ERROR_')) and k != 'UNKNOWN_SOURCE')
    result = dict(experiment='GDT990', cases=len(cases), solver_jobs=len(jobs), status_counts=dict(counts),
                  paragraph_counts={e: len(p) for e, p in paragraphs.items()},
                  conditional_witness_cases=counts['SAT'], computation_unknown_or_error_cases=computational,
                  decision='CONDITIONAL_COMPLETE_WRITING_CANDIDATES' if counts['SAT'] else
                           'NO_WITNESS_COMPUTATION_INCOMPLETE' if computational else 'NO_LITERAL_COMPLETE_WRITING_FIT',
                  independent_meaning_confirmation_capacity=0, confirmed_translated_words=0,
                  significance_claim=False, unique_inverse_decoding_claim=False)
    result['breakdown'] = {e: {v: {w: dict(collections.Counter(c['status'] for c in cases if c['edition'] == e and c['variant'] == v and c['writer'] == w))
                                 for w in source['writers']} for v in source['variants']} for e in paragraphs}
    put('CASES.json.gz', cases)
    put('RESULT.json', result)
    put('EXECUTION_RECEIPT.json', dict(started_utc=started_utc,
        completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), elapsed_seconds=time.monotonic() - started,
        limits=limits, preexisting_exposure=True, new_admissions=0, sealed_opened=False))
    columns = ['case', 'edition', 'paragraph', 'leaf', 'variant', 'writer', 'source_forms', 'source_root_types', 'target_groups', 'status', 'independent_meaning_confirmation_capacity']
    with (A / 'CANDIDATES.tsv').open('w', newline='') as f:
        table = csv.DictWriter(f, columns, delimiter='\t', lineterminator='\n', extrasaction='ignore')
        table.writeheader()
        table.writerows(cases)
    lines = ['# Conditional whole-source readings', '', 'All meanings below are source hypotheses, with code and reference ambiguity retained.']
    for c in cases:
        if c['status'] != 'SAT':
            continue
        lines += ['', f"## Case {c['case']}: {c['edition']} {c['paragraph']} / {c['variant']} / {c['writer']}", '',
                  '`' + ' '.join(targets[(c['edition'], c['paragraph'])]) + '`', '', '| Whole word | Source roots in order |', '|---|---|']
        for i, word in enumerate(targets[(c['edition'], c['paragraph'])]):
            roots = [r['root'] for r in c['witness']['alignment'] if r['word_index'] == i]
            lines.append(f"| {word} | {' + '.join(roots)} |")
        lines += ['', 'Complete source assertions:'] + ['- ' + r['content'] for r in source['variants'][c['variant']]['clauses']]
        lines += ['', 'All exact code values, frame values and alternative-witness queries are in CASES.json.gz.']
    if not counts['SAT']:
        lines += ['', 'No complete code witness. CANDIDATES.tsv retains every contradiction, unknown and error.']
    (A / 'COMPLETE_READINGS.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

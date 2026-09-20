#!/usr/bin/env python3
"""Run once; persist each completed case before assembly."""
import collections
import concurrent.futures
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from pattern import solve

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'


def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def put(name, obj):
    raw = (json.dumps(obj, separators=(',', ':')) + '\n').encode()
    (A / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)


def inputs():
    for name, digest in read(E / 'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    own = read(E / 'src/SOURCE.json')
    source = read(ROOT / own['original_source'])
    cases = read(ROOT / own['original_cases'])
    panel = read(ROOT / own['paragraphs'])
    targets = {}
    for ed, ps in panel.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page'] != 'f116v'
            targets[(ed, p['id'])] = [w for line in p['lines'] for w in line['words']]
    return own, source, cases, targets


def isolated(job, deadline, cap):
    left = deadline - time.time()
    if left <= 0:
        return dict(status='UNKNOWN_QUEUE_LIMIT')
    try:
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'], input=json.dumps(job),
                           text=True, capture_output=True, timeout=min(cap, left))
        if p.returncode:
            return dict(status='ERROR_WORKER', returncode=p.returncode,
                        error_type=p.stderr.strip().splitlines()[-1][:160] if p.stderr.strip() else 'no_message')
        return json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        return dict(status='UNKNOWN_EXTERNAL_LIMIT')
    except Exception as ex:
        return dict(status='ERROR_PROTOCOL', error_type=type(ex).__name__)


def assemble():
    own, source, cases, targets = inputs()
    rows = [json.loads(s) for s in (A / 'PATTERN_JOURNAL.jsonl').read_text().splitlines() if s.strip()]
    indexed = {r['case']: r['outcome'] for r in rows}
    assert len(indexed) == len(rows)
    for c in cases:
        old = c['status']
        c['original_status'] = old
        if old == 'UNKNOWN_UNRETAINED_SOLVER_RESULT':
            c['pattern'] = indexed.pop(c['case'], dict(status='UNKNOWN_NO_RETAINED_PATTERN'))
            c['status'] = c['pattern']['status']
            if c['status'] == 'COMPLETE_ROLE_FORM_PATTERN_WITNESS' and c['pattern']['factorization']['status'] == 'FULL_ORIGINAL_CODE_WITNESS':
                c['status'] = 'FULL_ORIGINAL_CODE_WITNESS'
        else:
            assert c['case'] not in indexed
    assert not indexed
    counts = dict(collections.Counter(c['status'] for c in cases))
    result = dict(experiment='GDT991', cases=len(cases), new_pattern_cases=1980,
                  saved_jobs=len(rows), status_counts=counts,
                  original_code_witness_cases=counts.get('FULL_ORIGINAL_CODE_WITNESS', 0),
                  independent_meaning_confirmation_capacity=0, confirmed_translated_words=0,
                  significance_claim=False, code_uniqueness_claim=False,
                  decision='AWAIT_SEPARATE_VALIDATION')
    put('PRIMARY_CASES.json.gz', cases)
    put('PRIMARY_RESULT.json', result)
    print(json.dumps(result, indent=2), flush=True)


def main():
    if '--worker' in sys.argv:
        job = json.load(sys.stdin)
        print(json.dumps(solve(**job), separators=(',', ':')))
        return
    if '--assemble' in sys.argv:
        assemble()
        return
    own, source, cases, targets = inputs()
    start = time.time()
    deadline = start + own['limits']['shared_target_seconds']
    jobs = []
    for c in cases:
        if c['status'] == 'UNKNOWN_UNRETAINED_SOLVER_RESULT':
            jobs.append((c['case'], dict(events=source['variants'][c['variant']]['streams'][c['writer']],
                       words=targets[(c['edition'], c['paragraph'])], seconds=own['limits']['pattern_seconds'],
                       factor_seconds=own['limits']['factor_seconds'], factor_nodes=own['limits']['factor_nodes'])))
    assert len(jobs) == 1980
    with (A / 'PATTERN_JOURNAL.jsonl').open('x') as journal:
        put('EXECUTION_RECEIPT.json', dict(started_utc=datetime.datetime.fromtimestamp(start, datetime.timezone.utc).isoformat(),
            shared_deadline_utc=datetime.datetime.fromtimestamp(deadline, datetime.timezone.utc).isoformat(),
            shared_deadline_unix=deadline, limits=own['limits'], target_jobs=len(jobs), completion='RUNNING'))
        print(json.dumps(dict(prepared_jobs=len(jobs), whole_cases=len(cases))), flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=own['limits']['workers']) as pool:
            futures = {pool.submit(isolated, job, deadline, own['limits']['external_pattern_seconds']): cid for cid, job in jobs}
            for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
                row = dict(case=futures[future], outcome=future.result())
                journal.write(json.dumps(row, separators=(',', ':')) + '\n')
                journal.flush()
                if done % 64 == 0 or done == len(jobs):
                    print(json.dumps(dict(completed=done, of=len(jobs), latest=row['outcome']['status'])), flush=True)
    receipt = read(A / 'EXECUTION_RECEIPT.json')
    receipt.update(completion='PRIMARY_COMPLETED', primary_elapsed_seconds=time.time() - start)
    put('EXECUTION_RECEIPT.json', receipt)
    assemble()


if __name__ == '__main__':
    main()

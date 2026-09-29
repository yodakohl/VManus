#!/usr/bin/env python3
"""Finite necessary consequences of the unchanged GDT963 equations."""
import collections
import concurrent.futures
import functools
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
PARENT = ROOT / 'experiments/yolo/gdt963_dioscorides_complete_content_code'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def save(name, value):
    blob = (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    (E / 'artifacts' / name).write_bytes(gzip.compress(blob, mtime=0) if name.endswith('.gz') else blob)


def ordered(values):
    return sorted(values, key=lambda v: (len(v), v))


def repeats(text):
    """Every repeated substring is a prefix of an adjacent suffix LCP."""
    suffixes = sorted(text[i:] for i in range(len(text)))
    values = set()
    for left, right in zip(suffixes, suffixes[1:]):
        j = 0
        while j < min(len(left), len(right)) and left[j] == right[j]:
            j += 1
            values.add(left[:j])
    return ordered(values)


def template(atoms, keep):
    result = [0]
    for atom in atoms:
        if atom in keep:
            if isinstance(result[-1], int):
                result.append([])
            result[-1].append(atom)
        else:
            if not isinstance(result[-1], int):
                result.append(0)
            result[-1] += 1
    if not isinstance(result[-1], int):
        result.append(0)
    return result


def fits(text, pattern, code):
    """Literal runs separated by lower-bounded spans; exact zero end gaps."""
    position = 0
    for k in range(1, len(pattern), 2):
        literal = ''.join(code[a] for a in pattern[k])
        minimum = position + pattern[k - 1]
        first = k == 1
        last = k == len(pattern) - 2
        if first and pattern[0] == 0:
            start = 0
            if not text.startswith(literal):
                return False
        elif last and pattern[-1] == 0:
            start = len(text) - len(literal)
            if start < minimum or not text.endswith(literal):
                return False
        else:
            start = text.find(literal, minimum)
            if start < 0:
                return False
        position = start + len(literal)
        if last and pattern[-1] == 0 and position != len(text):
            return False
    return len(text) - position >= pattern[-1]


class Limit(Exception):
    pass


def evaluate(atoms, text, evaluation_limit=250000):
    counts = collections.Counter(atoms)
    recurrent = sorted(a for a, count in counts.items() if count > 1)
    vocabulary = repeats(text)
    domains = {}
    initial = {}
    for atom in recurrent:
        bound = (len(text) - len(atoms) + counts[atom]) // counts[atom]
        pattern = template(atoms, {atom})
        values = [w for w in vocabulary if len(w) <= bound and fits(text, pattern, {atom: w})]
        domains[atom] = set(values)
        initial[atom] = values
    edges = sorted({tuple(sorted((a, b))) for a, b in zip(atoms, atoms[1:])
                    if a != b and a in domains and b in domains})
    patterns = {(a, b): template(atoms, {a, b}) for a, b in edges}
    calls = 0

    @functools.lru_cache(maxsize=100000)
    def compatible(a, u, b, v):
        nonlocal calls
        calls += 1
        if calls > evaluation_limit:
            raise Limit
        if u.startswith(v) or v.startswith(u):
            return False
        return fits(text, patterns[tuple(sorted((a, b)))], {a: u, b: v})

    trace = []
    empty = next((a for a in recurrent if not domains[a]), None)
    status = 'CONTRADICTED_ONE_ATOM' if empty else 'NECESSARY_DOMAINS_NONEMPTY'
    witnesses = {}
    if not empty:
        try:
            changed = True
            while changed:
                changed = False
                for left, right in edges:
                    for a, b in ((left, right), (right, left)):
                        removed = []
                        other = ordered(domains[b])
                        for u in ordered(domains[a]):
                            key = (a, b, u)
                            if witnesses.get(key) in domains[b]:
                                continue
                            support = next((v for v in other if compatible(a, u, b, v)), None)
                            if support is None:
                                removed.append(u)
                            else:
                                witnesses[key] = support
                        if removed:
                            trace.append(dict(atom=a, against=b, removed=removed,
                                              partner_count=len(other), partner_domain_sha256=digest(other)))
                            domains[a].difference_update(removed)
                            changed = True
                            if not domains[a]:
                                empty = a
                                status = 'CONTRADICTED_TWO_ATOM'
                                break
                    if empty:
                        break
                if empty:
                    break
        except Limit:
            status = 'UNKNOWN_EVALUATION_LIMIT'
    return dict(status=status, recurrent_types=len(recurrent), edges=[list(x) for x in edges],
                initial_domains=initial, deletion_trace=trace,
                final_domains={a: ordered(domains[a]) for a in recurrent},
                empty_atom=empty, pair_evaluations=calls, full_code_witness=False)


def isolated(job, spec, deadline):
    started = time.monotonic()
    remaining = deadline - started
    if remaining <= 0:
        return dict(status='UNKNOWN_RUN_WALL_LIMIT')
    try:
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--case'],
                              input=json.dumps(dict(atoms=job['atoms'], text=job['text'],
                                                    evaluation_limit=spec['pair_evaluation_limit'])),
                              text=True, capture_output=True,
                              timeout=min(spec['case_wall_seconds'], remaining))
        if proc.returncode:
            return dict(status='ERROR_PROCESS', returncode=proc.returncode)
        result = json.loads(proc.stdout)
    except subprocess.TimeoutExpired:
        result = dict(status='UNKNOWN_CASE_WALL_LIMIT' if remaining >= spec['case_wall_seconds']
                      else 'UNKNOWN_RUN_WALL_LIMIT')
    result['wall_seconds'] = time.monotonic() - started
    return result


def main():
    for path, expected in json.loads((E / 'src/PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    spec = json.loads((E / 'src/SPEC.json').read_text())
    source = json.loads((PARENT / 'src/SOURCE.json').read_text())
    frames = json.loads(gzip.decompress((PARENT / 'artifacts/TARGET_FRAMES.json.gz').read_bytes()))
    old = json.loads(gzip.decompress((PARENT / 'artifacts/ALL_LOCAL_CASES.json.gz').read_bytes()))
    assert len(frames) == 357 and len(old) == 1428
    assert all(not t['page'].startswith('f84') and t['page'] != 'f116v' for t in frames)
    targets = {t['id']: t for t in frames}
    records = {r['id']: r for r in source['records']}
    rows = []
    jobs = []
    for i, case in enumerate(old):
        row = {k: case[k] for k in ('edition', 'page', 'record', 'target_id', 'source_atoms', 'target_characters')}
        row['original_status'] = case['status']
        if case['status'] in ('UNKNOWN_SOURCE', 'CONTRADICTED_LENGTH_BOUND'):
            row['status'] = 'INHERITED_' + case['status']
        else:
            assert case['status'] in ('UNKNOWN_SOLVER', 'UNKNOWN_WALL_CEILING')
            row['status'] = 'PENDING'
            jobs.append((i, dict(atoms=records[row['record']]['atoms'], text=targets[row['target_id']]['text'])))
        rows.append(row)
    certificates = {}
    start = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=spec['workers']) as pool:
        futures = {pool.submit(isolated, job, spec, start + spec['run_wall_seconds']): i for i, job in jobs}
        for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
            index = futures[future]
            result = future.result()
            rows[index]['status'] = result['status']
            rows[index]['recurrent_types'] = result.get('recurrent_types')
            rows[index]['initial_domain_values'] = sum(map(len, result.get('initial_domains', {}).values()))
            rows[index]['final_domain_values'] = sum(map(len, result.get('final_domains', {}).values()))
            rows[index]['empty_atom'] = result.get('empty_atom')
            certificates[str(index)] = result
            if done % 40 == 0 or done == len(jobs):
                print(json.dumps(dict(completed=done, total=len(jobs), elapsed=time.monotonic()-start)), flush=True)
    elapsed = time.monotonic() - start
    save('CERTIFICATES.json.gz', certificates)
    save('CASES.json', rows)
    header = ['edition', 'page', 'record', 'original_status', 'status', 'source_atoms',
              'target_characters', 'recurrent_types', 'initial_domain_values', 'final_domain_values', 'empty_atom']
    (E / 'artifacts/CANDIDATES.tsv').write_text('\t'.join(header) + '\n' + '\n'.join(
        '\t'.join('NA' if r.get(k) is None else str(r[k]) for k in header) for r in rows) + '\n')
    by_edition = {}
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        literal = [t for t in frames if t['edition'] == edition and t['eligible']]
        counts = {rid: collections.Counter(r['status'] for r in rows if r['edition'] == edition and r['record'] == rid)
                  for rid in records}
        empty_roles = [rid for rid in records if not any(
            r['edition'] == edition and r['record'] == rid and not r['status'].startswith(('CONTRADICTED', 'INHERITED_'))
            for r in rows)]
        capacity = len({t['physical_leaf'] for t in literal}) >= 4
        by_edition[edition] = dict(status='NO_ORIGINAL_FOUR_LEAF_CAPACITY' if not capacity else
                                  'FIXED_COMPLETE_CONJUNCTION_CONTRADICTED' if empty_roles else
                                  'COMPLETE_CONJUNCTION_UNRESOLVED', role_statuses=counts,
                                  excluded_roles=empty_roles, literal_pages=len(literal))
    result = dict(status='FINITE_NECESSARY_CONSEQUENCES_COMPLETE', original_cases=len(rows),
                  newly_evaluated=len(jobs), statuses=collections.Counter(r['status'] for r in rows),
                  edition_results=by_edition, wall_seconds=elapsed, source_atoms_changed=0,
                  decoder_rules_changed=0, complete_witnesses=0, confirmed_words=0,
                  independent_confirmation_leaves=0, significance_claim=False)
    save('RESULT.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    if '--case' in sys.argv:
        print(json.dumps(evaluate(**json.load(sys.stdin)), ensure_ascii=False))
    else:
        main()

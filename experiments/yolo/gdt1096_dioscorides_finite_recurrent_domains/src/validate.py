#!/usr/bin/env python3
"""Independent domain enumeration and positional-DP certificate replay."""
import collections
import functools
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import time

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
PARENT = ROOT / 'experiments/yolo/gdt963_dioscorides_complete_content_code'


def order(xs):
    return sorted(xs, key=lambda x: (len(x), x))


def sha(xs):
    return hashlib.sha256(json.dumps(xs, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def recurrent_substrings(text):
    result = set()
    for width in range(1, len(text) // 2 + 1):
        counts = collections.Counter(text[i:i + width] for i in range(len(text) - width + 1))
        repeated = {w for w, n in counts.items() if n > 1}
        if not repeated:
            break
        result.update(repeated)
    return result


def compile_segments(atoms, keep):
    segments = []
    gap = 0
    run = []
    for a in atoms:
        if a in keep:
            run.append(a)
        else:
            if run:
                segments.append((gap, tuple(run)))
                run = []
                gap = 0
            gap += 1
    if run:
        segments.append((gap, tuple(run)))
        gap = 0
    return segments, gap


def matcher(text):
    @functools.lru_cache(maxsize=10000)
    def positions(word):
        values = []
        p = text.find(word)
        while p >= 0:
            values.append(p)
            p = text.find(word, p + 1)
        return tuple(values)

    def accepts(segments, tail, code):
        ends = {0}
        for gap, names in segments:
            word = ''.join(code[a] for a in names)
            starts = positions(word)
            if gap:
                earliest = min(ends) + gap
                ends = {p + len(word) for p in starts if p >= earliest}
            else:
                ends = {p + len(word) for p in starts if p in ends}
            if not ends:
                return False
        return (len(text) in ends) if tail == 0 else min(ends) + tail <= len(text)
    return accepts


def initial_domains(atoms, text):
    words = recurrent_substrings(text)
    accepts = matcher(text)
    domains = {}
    for a, count in sorted(collections.Counter(atoms).items()):
        if count > 1:
            segments, tail = compile_segments(atoms, {a})
            domains[a] = {w for w in words if accepts(segments, tail, {a: w})}
    return domains, accepts


def validate_certificate(atoms, text, cert, check_fixed_point=True):
    if 'initial_domains' not in cert:
        assert cert['status'] in ('UNKNOWN_CASE_WALL_LIMIT', 'UNKNOWN_RUN_WALL_LIMIT', 'ERROR_PROCESS')
        return 0
    # Each code occurs at least twice in disjoint target intervals, so width <= L/2.
    domains, accepts = initial_domains(atoms, text)
    assert cert['initial_domains'] == {a: order(v) for a, v in domains.items()}, 'initial domain completeness'
    edges = sorted({tuple(sorted((a, b))) for a, b in zip(atoms, atoms[1:])
                    if a != b and a in domains and b in domains})
    assert cert['edges'] == [list(e) for e in edges]
    patterns = {(a, b): compile_segments(atoms, {a, b}) for a, b in edges}

    @functools.lru_cache(maxsize=100000)
    def support(a, u, b, v):
        if u.startswith(v) or v.startswith(u):
            return False
        segments, tail = patterns[tuple(sorted((a, b)))]
        return accepts(segments, tail, {a: u, b: v})

    removed_count = 0
    for step in cert['deletion_trace']:
        a, b = step['atom'], step['against']
        assert tuple(sorted((a, b))) in patterns
        others = order(domains[b])
        assert len(others) == step['partner_count'] and sha(others) == step['partner_domain_sha256']
        assert len(step['removed']) == len(set(step['removed']))
        for u in step['removed']:
            assert u in domains[a]
            assert not any(support(a, u, b, v) for v in others), 'invalid domain deletion'
        domains[a].difference_update(step['removed'])
        removed_count += len(step['removed'])
    assert cert['final_domains'] == {a: order(v) for a, v in domains.items()}, 'final domain replay'
    empty = {a for a, values in domains.items() if not values}
    if cert['status'] == 'CONTRADICTED_ONE_ATOM':
        assert empty and not cert['deletion_trace']
    elif cert['status'] == 'CONTRADICTED_TWO_ATOM':
        assert empty and cert['deletion_trace']
    else:
        assert not empty and cert['status'] in ('NECESSARY_DOMAINS_NONEMPTY', 'UNKNOWN_EVALUATION_LIMIT')
    assert (cert['empty_atom'] in empty) if empty else cert['empty_atom'] is None
    if cert['status'] == 'NECESSARY_DOMAINS_NONEMPTY' and check_fixed_point:
        for a, b in edges:
            for x, y in ((a, b), (b, a)):
                for u in domains[x]:
                    assert any(support(x, u, y, v) for v in domains[y]), 'not an arc fixed point'
    assert cert['full_code_witness'] is False
    return removed_count


def controls():
    spec = importlib.util.spec_from_file_location('candidate_runner', E / 'src/run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tests = 0
    for n in range(8):
        for letters in itertools.product('ab', repeat=n):
            t = ''.join(letters)
            brute = {t[i:j] for i in range(len(t)) for j in range(i+1, len(t)+1)
                     if any(t.startswith(t[i:j], k) for k in range(i+1, len(t)))}
            assert set(module.repeats(t)) == brute
            tests += 1
    projection_tests = 0
    for n in range(1, 5):
        for atoms in itertools.product('ABX', repeat=n):
            for keep in ({'A'}, {'B'}, {'A', 'B'}):
                segments, tail = compile_segments(atoms, keep)
                pattern = module.template(atoms, keep)
                for code in ({'A': 'a', 'B': 'b'}, {'A': 'ab', 'B': 'ba'}, {'A': 'a', 'B': 'aa'}):
                    for m in range(7):
                        for letters in itertools.product('ab', repeat=m):
                            t = ''.join(letters)
                            assert module.fits(t, pattern, code) == matcher(t)(segments, tail, code)
                            projection_tests += 1
    positive = 0
    for n in range(4, 7):
        for atoms in itertools.product('ABX', repeat=n):
            counts = collections.Counter(atoms)
            if not (counts['A'] >= 2 and counts['B'] >= 2):
                continue
            code = {'A': 'a', 'B': 'b', 'X': 'cc'}
            text = ''.join(code[a] for a in atoms)
            cert = module.evaluate(atoms, text)
            assert cert['status'] == 'NECESSARY_DOMAINS_NONEMPTY'
            assert all(code[a] in words for a, words in cert['final_domains'].items())
            validate_certificate(atoms, text, cert)
            positive += 1
    atom_case = module.evaluate(list('ABAB'), 'abca')
    assert atom_case['status'] == 'CONTRADICTED_ONE_ATOM'
    validate_certificate(list('ABAB'), 'abca', atom_case)
    forged = module.evaluate(list('ABAB'), 'abab')
    forged['initial_domains']['A'] = []
    try:
        validate_certificate(list('ABAB'), 'abab', forged)
        raise RuntimeError('Incomplete initial domain accepted')
    except AssertionError:
        pass
    forged = module.evaluate(list('ABAB'), 'abab')
    forged['deletion_trace'] = [dict(atom='A', against='B', removed=['a'], partner_count=1,
                                    partner_domain_sha256=sha(['b']))]
    try:
        validate_certificate(list('ABAB'), 'abab', forged)
        raise RuntimeError('Compatible value deletion accepted')
    except AssertionError:
        pass
    output = dict(status='PASS_CONTROLS', repeated_substring_cases=tests,
                  independent_projection_comparisons=projection_tests, prefix_code_positive_cases=positive,
                  impossible_one_atom_case=1, invalid_certificates_rejected=2,
                  manuscript_data_opened=False, meaning_validation=False)
    (E / 'artifacts/CONTROL_RESULTS.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))


def main():
    started = time.monotonic()
    for path, expected in json.loads((E / 'src/PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    source = json.loads((PARENT/'src/SOURCE.json').read_text())
    frames = json.loads(gzip.decompress((PARENT/'artifacts/TARGET_FRAMES.json.gz').read_bytes()))
    old = json.loads(gzip.decompress((PARENT/'artifacts/ALL_LOCAL_CASES.json.gz').read_bytes()))
    targets = {t['id']:t for t in frames}
    records = {r['id']:r for r in source['records']}
    rows = json.loads((E/'artifacts/CASES.json').read_text())
    certificates = json.loads(gzip.decompress((E/'artifacts/CERTIFICATES.json.gz').read_bytes()))
    result = json.loads((E/'artifacts/RESULT.json').read_text())
    assert len(rows) == len(old) == 1428
    expected_keys = {str(i) for i,c in enumerate(old) if c['status'].startswith(('UNKNOWN_SOLVER','UNKNOWN_WALL'))}
    assert set(certificates) == expected_keys and len(expected_keys) == 341
    deleted = 0
    for i,(before,row) in enumerate(zip(old,rows)):
        for key in ('edition','page','record','target_id','source_atoms','target_characters'):
            assert row[key] == before[key]
        assert row['original_status'] == before['status']
        if str(i) not in certificates:
            assert row['status'] == 'INHERITED_'+before['status']
            continue
        cert = certificates[str(i)]
        assert row['status'] == cert['status']
        deleted += validate_certificate(records[row['record']]['atoms'], targets[row['target_id']]['text'], cert)
        assert row['initial_domain_values'] == sum(map(len,cert.get('initial_domains',{}).values()))
        assert row['final_domain_values'] == sum(map(len,cert.get('final_domains',{}).values()))
        assert row['empty_atom'] == cert.get('empty_atom')
    assert result['statuses'] == dict(collections.Counter(r['status'] for r in rows))
    assert result['complete_witnesses'] == result['confirmed_words'] == result['decoder_rules_changed'] == 0
    for edition,item in result['edition_results'].items():
        for rid in records:
            counts = collections.Counter(r['status'] for r in rows if r['edition']==edition and r['record']==rid)
            assert item['role_statuses'][rid] == dict(counts)
        live = {r['record'] for r in rows if r['edition']==edition and r['status'] in
                ('NECESSARY_DOMAINS_NONEMPTY','UNKNOWN_EVALUATION_LIMIT','UNKNOWN_CASE_WALL_LIMIT','UNKNOWN_RUN_WALL_LIMIT','ERROR_PROCESS')}
        empty = sorted(set(records)-live)
        assert sorted(item['excluded_roles']) == empty
        leaves={t['physical_leaf'] for t in frames if t['edition']==edition and t['eligible']}
        expected='NO_ORIGINAL_FOUR_LEAF_CAPACITY' if len(leaves)<4 else 'FIXED_COMPLETE_CONJUNCTION_CONTRADICTED' if empty else 'COMPLETE_CONJUNCTION_UNRESOLVED'
        assert item['status']==expected
    output=dict(status='PASS', original_cases_checked=len(rows), case_certificates_checked=len(certificates),
                independently_replayed_deletions=deleted, wall_seconds=time.monotonic()-started,
                full_code_witnesses=0, meaning_validation=False, scope='finite necessary consequence certificates, not decoder or meaning confirmation')
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    controls() if '--controls' in sys.argv else main()

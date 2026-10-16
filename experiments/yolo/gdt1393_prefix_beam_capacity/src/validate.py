#!/usr/bin/env python3
"""Independent full-sort beam and modular-fiber verifier; no producer imports."""
import argparse
from collections import deque
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import numpy as np

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'
R = E / 'runtime'


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def context(code, length, alphabet=27):
    if length == 0:
        return np.zeros_like(code)
    if length == 1:
        return 1 + code
    if length == 2:
        return 1 + alphabet + code
    return 1 + alphabet + alphabet**2 + code % (alphabet**3)


def beam(table, width, depth, alphabet=27):
    codes = np.array([0], dtype=np.int64)
    scores = np.array([0.0], dtype=np.float64)
    history = []
    for length in range(depth):
        # Context derives directly from the numeric prefix; no inherited context state.
        ctx = context(codes, length, alphabet)
        children = (codes[:, None] * alphabet + np.arange(alphabet)[None, :]).ravel()
        values = (scores[:, None] + table[ctx, :]).ravel()
        order = np.lexsort((children, -values))[:width]
        codes, scores = children[order], values[order]
        assert len(set(map(int, codes))) == len(codes)
        history.append((codes.copy(), scores.copy()))
    return history


def text_values(text):
    return [0 if c == ' ' else ord(c) - 96 for c in text]


def prefix_code(chars, alphabet=27):
    value = 0
    for c in chars:
        assert 0 <= c < alphabet
        value = alphabet * value + c
    return value


def scalar_score(table, chars, alphabet=27):
    score, prefix = 0.0, []
    for c in chars:
        last = prefix[-3:]
        idx = sum(alphabet**j for j in range(len(last))) + prefix_code(last, alphabet)
        score += float(table[idx, c])
        prefix.append(c)
    return score


def kernel_update(B, row, modulus=27):
    # Columns of B generate the fiber's homogeneous subgroup, possibly redundantly.
    n = len(B)
    d = [sum(row[k] * B[k][j] for k in range(n)) % modulus for j in range(n)]
    g = math.gcd(modulus, *d)
    if g == modulus:
        return g, [0] * n, [r[:] for r in B]
    j = next(j for j in range(n) if math.gcd(d[j], modulus) == g)
    inverse = pow(d[j] // g, -1, modulus)
    v = [B[k][j] * inverse % modulus for k in range(n)]
    assert sum(a*b for a, b in zip(row, v)) % modulus == g
    out = [[((modulus // g) * v[k] if l == j else B[k][l] - (d[l] // g) * v[k]) % modulus
            for l in range(n)] for k in range(n)]
    assert all(sum(row[k] * out[k][l] for k in range(n)) % modulus == 0 for l in range(n))
    return g, v, out


def group_generated(B, modulus=27):
    n = len(B)
    zero = (0,) * n
    found, queue = {zero}, deque([zero])
    while queue:
        x = queue.popleft()
        for j in range(n):
            y = tuple((x[k] + B[k][j]) % modulus for k in range(n))
            if y not in found:
                found.add(y)
                queue.append(y)
    return found


def free_prefix(case, depth):
    n = 23
    B = [[int(i == j) for j in range(n)] for i in range(n)]
    prev = [0] * 22
    gs = []
    for word in case['units'][:depth]:
        counts = [word.count(i) for i in range(22)]
        row = [a-b for a, b in zip(counts, prev)] + [1]
        g, _, B = kernel_update(B, row)
        gs.append(g)
        prev = counts
    assert any(B[i][j] % 3 for i in range(22) for j in range(23)), 'No valid-weight kernel direction'
    return gs


def controls():
    checks = 0
    # Tiny ternary trees, including exact ties, checked against Python tuple sorting.
    alphabet = 3
    rows = sum(alphabet**i for i in range(4))
    for uniform in (False, True):
        raw = np.ones((rows, alphabet)) if uniform else np.arange(1, rows*alphabet+1).reshape(rows, alphabet)
        table = np.log(raw / raw.sum(axis=1)[:, None])
        for width in (1, 4, 100):
            history = beam(table, width, 4, alphabet)
            kept = [()]
            for depth, (codes, scores) in enumerate(history, 1):
                options = [p+(c,) for p in kept for c in range(alphabet)]
                kept = sorted(options, key=lambda p: (-scalar_score(table, p, alphabet), p))[:width]
                assert list(map(int, codes)) == [prefix_code(p, alphabet) for p in kept]
                assert max(abs(float(s)-scalar_score(table,p,alphabet)) for p,s in zip(kept,scores)) < 1e-12
                checks += len(kept)
    # Exhaustively check fibers in two dimensions, including nonfree torsion.
    for rows in ([(1,0),(0,1)], [(3,0),(9,3),(0,9)], [(9,0),(3,0),(0,0)], [(6,3),(9,12)]):
        B = [[1,0],[0,1]]
        for row in rows:
            old = group_generated(B)
            g, v, new = kernel_update(B, row)
            assert group_generated(new) == {x for x in old if sum(a*b for a,b in zip(row,x)) % 27 == 0}
            for t in range(27//g):
                got = {tuple((x[k]+t*v[k])%27 for k in range(2)) for x in group_generated(new)}
                expected = {x for x in old if sum(a*b for a,b in zip(row,x)) % 27 == g*t}
                assert got == expected
                checks += len(got)
            B = new
    return {'status':'PASS_SOURCE_FREE_CONTROLS','checked_objects':checks,
            'beam_method':'full lexsort versus exhaustive Python tuple sorting',
            'fiber_method':'generator pivot versus explicit group enumeration',
            'truth_access':False}


def verify_source_only(output_dir):
    lock_path = E / 'CODE_LOCK.json'
    lock = read(lock_path)
    locked = {item['path']: item['sha256'] for item in lock['files']}
    old = ROOT / 'experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts'
    rank_path = ROOT / 'research_registry/proposals/production_origin_supply_20261003/C1064_PREFIX_RANK_RESULT_20261016.json'
    required = [E/'src/run.py', Path(__file__), E/'PREREGISTRATION.md', E/'METHOD.md', old/'MODELS.json', old/'CASES.json', rank_path]
    for path in required:
        key = str(path.relative_to(ROOT))
        assert key in locked and sha(path) == locked[key], key
    beams_path = A / 'BEAMS.json'
    beams = read(beams_path)
    assert beams['experiment_id'] == 'GDT1393'
    assert beams['width'] == 65536 and beams['depth'] == 10
    assert beams['lock_sha256'] == sha(lock_path)
    allowed_inputs = {str(path.relative_to(ROOT)) for path in required[-3:]}
    allowed_inputs.update(item['path'] for item in read(old/'MODELS.json')['models'])
    assert set(beams['input_hashes']) == allowed_inputs
    for path, expected in beams['input_hashes'].items():
        assert sha(ROOT / path) == expected, path
        assert locked[path] == expected
    assert beams['prefix_rank_sha256'] == sha(rank_path)
    rank = read(rank_path)
    assert len(rank['cases']) == 18
    assert all(c['snapshots']['10']['fully_free'] == 10 and c['snapshots']['10']['fully_determined'] == c['snapshots']['10']['partial'] == 0 for c in rank['cases'])
    old = ROOT / 'experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts'
    cases_path = old / 'CASES.json'
    assert sha(cases_path) == beams['cases_sha256']
    cases = read(cases_path)['cases']
    assert len(cases) == 18
    gs = {case['id']: free_prefix(case, 10) for case in cases}
    assert all(value == [1]*10 for value in gs.values())
    manifest_path = old / 'MODELS.json'
    manifest = read(manifest_path)
    expected_languages = {row['language']: row for row in manifest['models']}
    assert len(expected_languages) == len(beams['languages']) == 6
    assert {r['language'] for r in beams['languages']} == set(expected_languages)
    sets, validation = {}, []
    for entry in beams['languages']:
        lang = entry['language']
        model_path = ROOT / entry['model_path']
        assert entry['model_path'] == expected_languages[lang]['path']
        assert sha(model_path) == entry['model_sha256'] == expected_languages[lang]['sha256']
        assert locked[entry['model_path']] == entry['model_sha256']
        model = read(model_path)
        assert model['language'] == lang
        table = np.asarray(model['logp'], dtype=np.float64)
        assert table.shape == (20440, 27) and np.all(np.isfinite(table))
        assert float(np.max(np.abs(np.exp(table).sum(axis=1)-1))) < 1e-10
        history = beam(table, 65536, 10)
        assert len(entry['steps']) == len(history) == 10
        for depth, ((codes, scores), step) in enumerate(zip(history, entry['steps']), 1):
            assert step['depth'] == depth and step['count'] == len(codes)
            assert hashlib.sha256(np.ascontiguousarray(codes, dtype='<i8').tobytes()).hexdigest() == step['codes_rank_order_sha256']
            for name, value in [('score_min', scores.min()), ('score_max', scores.max()), ('score_mean', scores.mean())]:
                assert abs(float(value)-step[name]) < 1e-10, (lang, depth, name)
        codes, scores = history[-1]
        order = np.argsort(codes)
        codes, scores = codes[order], scores[order]
        cp, sp = output_dir / entry['final_codes_file'], output_dir / entry['final_scores_file']
        assert cp.name == entry['final_codes_file'] and sp.name == entry['final_scores_file']
        assert sha(cp) == entry['final_codes_sha256'] and sha(sp) == entry['final_scores_sha256']
        primary_codes = np.load(cp, allow_pickle=False)
        primary_scores = np.load(sp, allow_pickle=False)
        assert primary_codes.dtype == np.dtype('int64')
        assert primary_scores.dtype == np.dtype('float64')
        assert np.array_equal(codes, primary_codes)
        assert scores.shape == primary_scores.shape
        max_error = float(np.max(np.abs(scores-primary_scores)))
        assert max_error < 1e-10
        # Independently accumulate actual retained prefix likelihoods for bounded endpoints.
        for index in (0, len(codes)//2, len(codes)-1):
            value = int(codes[index]); chars = [0]*10
            for j in range(9,-1,-1):
                chars[j], value = value % 27, value // 27
            assert abs(scalar_score(table, chars)-float(scores[index])) < 1e-10
        sets[lang] = set(map(int, codes))
        validation.append({'language':lang, 'steps':10, 'final_prefixes':len(codes),
                           'max_score_error':max_error})
    return beams, sets, validation, gs


def validate(output_dir, truth_path):
    # Authoritative release metadata is checked without opening the truth file.
    seal_path, release_path = A/'BEAMS_SEAL.json', A/'TRUTH_RELEASE_RECEIPT.json'
    seal, release = read(seal_path), read(release_path)
    assert seal['beams_sha256'] == sha(A/'BEAMS.json')
    assert release['beams_seal_sha256'] == sha(seal_path)
    assert datetime.fromisoformat(seal['sealed_utc'].replace('Z','+00:00')) <= datetime.fromisoformat(release['released_utc'].replace('Z','+00:00'))
    beams, sets, language_checks, gs = verify_source_only(output_dir)
    # All six independent source-only beams and array comparisons are complete.
    assert sha(truth_path) == release['truth_sha256']
    truth = read(truth_path)
    comparison_path = A/'COMPARISON.json'
    comparison = read(comparison_path)
    old = ROOT/'experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts'
    cases_path = old/'CASES.json'
    public = {case['id']:case['units'] for case in read(cases_path)['cases']}
    assert len(truth['cases']) == len(public) == 18
    assert {case['id'] for case in truth['cases']} == set(public)
    expected = []
    for case in truth['cases']:
        assert case['units'] == public[case['id']]
        assert len(case['text']) == len(case['units']) and len(case['text']) >= 10
        chars = text_values(case['text'][:10])
        code = prefix_code(chars)
        membership = {lang: code in values for lang, values in sets.items()}
        expected.append({'id':case['id'], 'kind':case['kind'],
                         'message_length':len(case['text']), 'prefix_code':code,
                         'in_beams':membership, 'in_any_beam':any(membership.values())})
    assert comparison['cases'] == expected
    positives = [case for case in expected if case['kind'] == 'POSITIVE']
    negatives = [case for case in expected if case['kind'] == 'NEGATIVE']
    assert len(positives) == 12 and len(negatives) == 6
    pcount = sum(case['in_any_beam'] for case in positives)
    ncount = sum(case['in_any_beam'] for case in negatives)
    assert comparison['positive_cases'] == 12 and comparison['negative_cases'] == 6
    assert comparison['positive_prefix_hits'] == pcount and comparison['negative_prefix_hits'] == ncount
    status = 'PREFIX_GATE_PASS_RECOVERY_NOT_ESTABLISHED' if pcount == 12 else 'PREFIX_GATE_FAIL_NO_FULL_BEAM_ENGINE'
    assert comparison['status'] == status and comparison['experiment_id'] == 'GDT1393'
    for field, path in [('beams_sha256',A/'BEAMS.json'), ('beams_seal_sha256',seal_path),
                        ('truth_sha256',truth_path), ('cases_sha256',cases_path), ('lock_sha256',E/'CODE_LOCK.json')]:
        assert comparison[field] == sha(path)
    assert 'Necessary prefix retention only' in comparison['scope']
    assert comparison['decision'] == 'Stop this exact six-beam/width65536 forward proposal if any positive prefix was pruned; no width/restart/source repair.'
    result = {'experiment_id':'GDT1393', 'status':'PASS_INDEPENDENT_VALIDATION',
              'scientific_status':status, 'selection_method':'Full lexsort of every frontier; producer uses partial selection',
              'prefix_context_method':'Direct base27 suffix arithmetic plus scalar accumulation checks',
              'fiber_method':'Minimal3-adic-valuation modular generator elimination; independent of prior rank code',
              'first_ten_modular_image_g':gs, 'all_first_ten_have_27_choices':True,
              'valid_key_kernel_direction_checked':True, 'source_languages':language_checks,
              'positive_prefix_hits':pcount, 'positive_cases':12,
              'negative_prefix_hits':ncount, 'negative_cases':6,
              'all_case_records_match':True, 'truth_opened_after_source_only_recomputation':True,
              'historical_truth_previously_public':True,
              'source_free_controls':controls(),
              'pins':{'validator_sha256':sha(Path(__file__)), 'code_lock_sha256':sha(E/'CODE_LOCK.json'),
                      'beams_sha256':sha(A/'BEAMS.json'), 'beams_seal_sha256':sha(seal_path),
                      'release_receipt_sha256':sha(release_path), 'comparison_sha256':sha(comparison_path),
                      'truth_sha256':sha(truth_path), 'cases_sha256':sha(cases_path)},
              'limits':['No full recovery or native analysis.',
                        'The fixed width and source-only forward ranking are essential to this necessary gate.',
                        'Previously exposed controls do not become an independent blind sample.']}
    target = A/'VALIDATION.json'
    assert not target.exists()
    save(target, result)
    print(json.dumps({k:result[k] for k in ('status','scientific_status','positive_prefix_hits','negative_prefix_hits')}, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--controls', action='store_true')
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--truth', type=Path)
    args = p.parse_args()
    if args.controls:
        assert args.output_dir is None and args.truth is None
        print(json.dumps(controls(), sort_keys=True))
    else:
        assert args.output_dir is not None and args.truth is not None
        validate(args.output_dir, args.truth)

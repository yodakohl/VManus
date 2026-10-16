#!/usr/bin/env python3
"""Independent backward residue and complete-message accounting; no engine import.

Never opens generator truth without an explicit --unblind argument AND a frozen
recovery receipt. Pre-unblind checks use public model artifacts and toy fixtures.
"""
import argparse
from collections import Counter, defaultdict
import re
import random
import gzip
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = EXP.parents[2]


def load(path):
    path = Path(path)
    blob = path.read_bytes()
    return json.loads(gzip.decompress(blob) if path.suffix == '.gz' else blob)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def indexed(obj, n):
    return obj[str(n)] if isinstance(obj, dict) else obj[n]


def backward(shape, key, modulus=27, keep=False):
    """B[j,a,r] is suffix-residue r probability after previous unit a.

    Terminal arrays are residue-zero point masses. Unlike the engine's forward
    cumulative residue recursion, propagate required suffix sums backwards.
    """
    key = np.asarray(key, dtype=int)
    alphabet = len(key)
    total = np.zeros(modulus)
    lengths, tables = {}, {}
    for n in range(1, shape['L'] + 1):
        initial = np.asarray(indexed(shape['initial'], n), dtype=float)
        transition = np.asarray(indexed(shape['transition'], n), dtype=float)
        following = np.zeros((alphabet, modulus))
        following[:, 0] = 1.0
        saved = {n: following.copy()} if keep else None
        for j in range(n - 1, 0, -1):
            shifted = np.array([np.roll(following[b], int(key[b])) for b in range(alphabet)])
            following = transition[j - 1] @ shifted
            if keep:
                saved[j] = following.copy()
        mass = sum(initial[b] * np.roll(following[b], int(key[b])) for b in range(alphabet))
        lengths[n] = mass
        total += float(shape['p_len'][n]) * mass
        if keep:
            tables[n] = saved
    return total, lengths, tables


def packet_logp(shape, word):
    n = len(word)
    assert 1 <= n <= shape['L']
    value = math.log(shape['p_len'][n]) + math.log(indexed(shape['initial'], n)[word[0]])
    trans = indexed(shape['transition'], n)
    for j in range(1, n):
        value += math.log(trans[j - 1][word[j - 1]][word[j]])
    return value


def source_logp(table, chars):
    answer = 0.0
    for i, char in enumerate(chars):
        if i == 0:
            index = 0
        elif i == 1:
            index = 1 + chars[i - 1]
        elif i == 2:
            index = 28 + 27 * chars[i - 2] + chars[i - 1]
        else:
            index = 757 + 729 * chars[i - 3] + 27 * chars[i - 2] + chars[i - 1]
        answer += float(table[index][char])
    return answer


def logmeanexp(values):
    maximum = max(values)
    return maximum + math.log(sum(math.exp(v - maximum) for v in values)) - math.log(len(values))


def score(shape, tables, words, key, offset):
    z, _, _ = backward(shape, key)
    assert min(z) > 0
    states = [sum(key[x] for x in word) % 27 for word in words]
    prior = 0
    chars = []
    for state in states:
        chars.append((state - prior + offset) % 27)
        prior = state
    source_scores = [source_logp(table, chars) for table in tables]
    channel = sum(packet_logp(shape, word) - math.log(z[state]) for word, state in zip(words, states))
    return dict(chars=chars, states=states, source_ll=source_scores, mixture_ll=logmeanexp(source_scores), channel_ll=channel, total_ll=logmeanexp(source_scores) + channel)


def toy_controls():
    shape = dict(L=3, p_len=[0, .2, .3, .5], initial=[None, [.3, .7], [.4, .6], [.8, .2]],
                 transition=[None, [], [[[.1, .9], [.6, .4]]], [[[.2, .8], [.7, .3]], [[.9, .1], [.25, .75]]]])
    checked = 0
    for key in itertools.product(range(3), repeat=2):
        z, lengths, tables = backward(shape, key, modulus=3, keep=True)
        brute = np.zeros(3)
        for n in range(1, 4):
            local = np.zeros(3)
            for word in itertools.product(range(2), repeat=n):
                prob = math.exp(packet_logp(shape, word))
                residue = sum(key[x] for x in word) % 3
                brute[residue] += prob
                local[residue] += prob / shape['p_len'][n]
                # Independent exhaustive source-conditioned sequential sampler
                # factorization must telescope to P(word)/Z(residue).
                if z[residue] > 0:
                    branch = shape['p_len'][n] * lengths[n][residue] / z[residue]
                    remaining = residue
                    for pos, unit in enumerate(word):
                        previous = word[pos - 1] if pos else None
                        weights = indexed(shape['initial'], n) if pos == 0 else indexed(shape['transition'], n)[pos - 1][previous]
                        tail = tables[n][pos + 1]
                        masses = [weights[b] * tail[b, (remaining - key[b]) % 3] for b in range(2)]
                        branch *= masses[unit] / sum(masses)
                        remaining = (remaining - key[unit]) % 3
                    assert remaining == 0
                    assert math.isclose(branch, prob / z[residue], rel_tol=1e-12, abs_tol=1e-14)
                checked += 1
            assert np.allclose(local, lengths[n], rtol=1e-12, atol=1e-14)
        assert np.allclose(brute, z, rtol=1e-12, atol=1e-14)
        assert math.isclose(sum(z), 1, abs_tol=1e-12)
        for offset in range(3):
            for chars in itertools.product(range(3), repeat=3):
                prior = 0
                states = []
                for char in chars:
                    prior = (prior + char - offset) % 3
                    states.append(prior)
                decoded = [(state - (states[i-1] if i else 0) + offset) % 3 for i, state in enumerate(states)]
                assert decoded == list(chars)
                checked += 1
    # Full-message mixture differs from characterwise mixture.
    a, b = [.8, .2], [.1, .9]
    for msg in itertools.product(range(2), repeat=4):
        lls = [sum(math.log(p[c]) for c in msg) for p in [a, b]]
        exact = (math.prod(a[c] for c in msg) + math.prod(b[c] for c in msg)) / 2
        assert math.isclose(math.exp(logmeanexp(lls)), exact, rel_tol=1e-12)
        checked += 1
    # Exhaust the complete two-character source/channel mixture over all outputs.
    words = [w for n in range(1, 4) for w in itertools.product(range(2), repeat=n)]
    probabilities = {w: math.exp(packet_logp(shape, w)) for w in words}
    priors = [[.2, .3, .5], [.6, .1, .3]]
    transitions = [[[.2,.3,.5],[.1,.7,.2],[.6,.3,.1]],
                   [[.5,.3,.2],[.2,.4,.4],[.1,.1,.8]]]
    for key in itertools.product(range(3), repeat=2):
        z, _, _ = backward(shape, key, modulus=3)
        if min(z) == 0:
            continue
        for offset in range(3):
            mass = 0.0
            for first, second in itertools.product(words, repeat=2):
                r1 = sum(key[x] for x in first) % 3
                r2 = sum(key[x] for x in second) % 3
                c1, c2 = (r1+offset)%3, (r2-r1+offset)%3
                source = sum(priors[k][c1]*transitions[k][c1][c2] for k in range(2))/2
                channel = probabilities[first]*probabilities[second]/z[r1]/z[r2]
                mass += source*channel
                via_logs = logmeanexp([math.log(priors[k][c1])+math.log(transitions[k][c1][c2]) for k in range(2)]) + packet_logp(shape,first)+packet_logp(shape,second)-math.log(z[r1])-math.log(z[r2])
                assert math.isclose(math.exp(via_logs), source*channel, rel_tol=1e-12)
                checked += 1
            assert abs(mass-1) < 1e-12
    return {'status': 'PASS_SOURCE_FREE_INDEPENDENT_EXHAUSTIVE', 'checks': checked,
            'scope': 'Small finite backward-DP, exhaustive sampler probabilities, inverse states and whole-message mixture; no recovery claim.'}


def inspect_shape(shape):
    assert len(shape['signs']) == 22 and shape['L'] >= 27
    assert len(shape['p_len']) == shape['L'] + 1
    assert shape['p_len'][0] == 0
    assert all(p > 0 for p in shape['p_len'][1:])
    assert math.isclose(sum(shape['p_len']), 1, abs_tol=1e-12)
    for n in range(1, shape['L'] + 1):
        p = np.asarray(indexed(shape['initial'], n))
        assert p.shape == (22,) and np.all(p > 0) and abs(p.sum() - 1) < 1e-12
        t = np.asarray(indexed(shape['transition'], n))
        if n > 1:
            assert t.shape == (n-1, 22, 22) and np.all(t > 0)
            assert np.max(abs(t.sum(axis=2) - 1)) < 1e-12
    # Independently reconstruct every frozen >=4 M1 row from original counts.
    old = load(ROOT / 'experiments/yolo/gdt1308_whole_form_prediction/artifacts/MODEL.json')['IT2a']['m1']
    lookup = {tuple(r['context']): r['counts'] for r in old if r['context'][0] == 'B'}
    checked = 0
    for n in range(4, shape['L'] + 1):
        for pos in range(n):
            for previous in (['^'] if pos == 0 else shape['signs']):
                counts = lookup.get(('B', n, pos, previous), {})
                expected = np.array([(counts.get(s, 0) + .5) / (sum(counts.values()) + 11) for s in shape['signs']])
                observed = indexed(shape['initial'], n) if pos == 0 else indexed(shape['transition'], n)[pos-1][shape['signs'].index(previous)]
                assert np.allclose(observed, expected, rtol=1e-12, atol=1e-14), (n, pos, previous)
                checked += 1
    return checked


def validate_source_table(pack_path, table_path):
    """Rebuild training-prefix-only counts; no control suffix is inspected/output."""
    normalized = ' '.join(Path(pack_path).read_text().split())
    split = math.floor(.8 * len(normalized))
    prefix = normalized[:split]
    del normalized
    values = np.frombuffer(prefix.encode('ascii'), dtype=np.uint8).astype(np.int64)
    assert np.all((values == 32) | ((values >= 97) & (values <= 122)))
    values = np.where(values == 32, 0, values - 96)
    counts = np.zeros((20440, 27), dtype=np.int64)
    for order in range(4):
        if order == 0:
            contexts = np.zeros(len(values), dtype=np.int64)
        elif order == 1:
            contexts = 1 + values[:-1]
        elif order == 2:
            contexts = 28 + 27 * values[:-2] + values[1:-1]
        else:
            contexts = 757 + 729 * values[:-3] + 27 * values[1:-2] + values[2:-1]
        np.add.at(counts, (contexts, values[order:]), 1)
    expected = np.log((counts + .5) / (counts.sum(axis=1, keepdims=True) + 13.5))
    saved = load(table_path)
    actual = np.asarray(saved['logp'])
    assert actual.shape == (20440, 27)
    error = float(np.max(abs(actual - expected)))
    assert error < 1e-10, (table_path, error)
    assert np.max(abs(np.exp(actual).sum(axis=1) - 1)) < 1e-12
    return dict(language=saved['language'], training_characters=split,
                table_sha256=digest(table_path), pack_sha256=digest(pack_path),
                maximum_log_probability_error=error)


def key_identifiability(words, alphabet=22):
    previous = np.zeros(alphabet, dtype=np.int64)
    rows = []
    used = set()
    for word in words:
        current = np.bincount(word, minlength=alphabet)
        rows.append(list(current - previous) + [1])
        previous = current
        used.update(word)
    matrix = np.array(rows, dtype=np.int64) % 3
    pivot = 0
    for column in range(alphabet + 1):
        candidates = np.flatnonzero(matrix[pivot:, column])
        if not len(candidates):
            continue
        selected = pivot + int(candidates[0])
        matrix[[pivot, selected]] = matrix[[selected, pivot]]
        matrix[pivot] = matrix[pivot] * (1 if matrix[pivot, column] == 1 else 2) % 3
        for row in range(len(matrix)):
            if row != pivot and matrix[row, column]:
                matrix[row] = (matrix[row] - matrix[row, column] * matrix[pivot]) % 3
        pivot += 1
        if pivot == min(matrix.shape):
            break
    return dict(parameter_columns=alphabet + 1, rank_mod3=pivot,
                unused_unit_indices=sorted(set(range(alphabet)) - used),
                fixed_plaintext_unique_mod27_certified=(pivot == alphabet + 1),
                scope='Full rank certifies parameter uniqueness only conditional on one fixed complete plaintext and initial state0. Deficiency reported without kernel cardinality or global recovery claim.')


def verify_training_provenance(shape):
    provenance = shape['provenance']
    for entry in provenance['inputs']:
        assert digest(ROOT / entry['path']) == entry['sha256']
    # Independent selection from already guarded cache; never raw TSV.
    metadata = {}
    for phase in ['DISCOVERY', 'EVALUATION']:
        cached = load(ROOT / f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_IT2a.json')
        for line in cached['lines']:
            metadata[line['metadata']['locus']] = line['metadata']
    rows = load(ROOT / 'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')['IT2a']
    ids, lengths, counts = [], Counter(), defaultdict(Counter)
    for row in rows:
        meta = metadata[row['locus']]
        page = row['page']
        assert not page.startswith('f84') and page not in ('f1r', 'f116v')
        if meta['currier'] != 'B' or int(re.fullmatch(r'f([0-9]+).*', page).group(1)) % 2 != 1:
            continue
        assert row['kind'] == meta['kind'] == 'P'
        assert row['left_separator'] == row['right_separator'] == 'DEFINITE_SPACE'
        raw = row['ivtff_group_raw']
        # Count complete unit segmentations by suffix recurrence.
        suffix = {len(raw): [()]}
        for i in range(len(raw)-1, -1, -1):
            suffix[i] = [(sign,) + rest for sign in shape['signs'] if raw.startswith(sign, i)
                         for rest in suffix.get(i+len(sign), [])][:2]
        assert len(suffix[0]) == 1 and suffix[0][0] == tuple(row['units'])
        word = suffix[0][0]
        ids.append(row['id'])
        lengths[len(word)] += 1
        for pos, unit in enumerate(word):
            counts[(len(word), pos, word[pos-1] if pos else '^')][unit] += 1
    assert ids == provenance['source_ids']
    assert len(ids) == provenance['train_groups']
    assert dict(lengths) == {int(k): v for k, v in provenance['length_counts'].items()}
    recorded = {tuple(x['context'][1:]): x['counts'] for x in provenance['m1']}
    assert {key: dict(value) for key, value in counts.items()} == recorded
    assert shape['L'] == max(27, max(lengths))
    for n in range(1, shape['L']+1):
        assert abs(shape['p_len'][n] - (lengths[n]+.5)/(len(ids)+.5*shape['L'])) < 1e-14
        for pos in range(n):
            for previous in (['^'] if pos == 0 else shape['signs']):
                cell = counts.get((n, pos, previous), {})
                expected = [(cell.get(unit, 0)+.5)/(sum(cell.values())+11) for unit in shape['signs']]
                actual = indexed(shape['initial'], n) if pos == 0 else indexed(shape['transition'], n)[pos-1][shape['signs'].index(previous)]
                assert np.allclose(expected, actual, rtol=1e-12, atol=1e-14)
    return dict(train_groups=len(ids), all_length_context_rows=len(counts), selection='IT2a Currier B odd physical leaves only; complete exact unit parse and definite outer spaces')


def inspect_models(manifest_path):
    manifest = load(manifest_path)
    shape_path = ROOT / manifest['shape']['path']
    assert digest(shape_path) == manifest['shape']['sha256']
    shape = load(shape_path)
    training = verify_training_provenance(shape)
    long_rows = inspect_shape(shape)
    summaries = []
    for model in manifest['models']:
        path, source = ROOT / model['path'], ROOT / model['source_path']
        assert digest(path) == model['sha256']
        assert digest(source) == model['source_sha256']
        check = validate_source_table(source, path)
        assert check['training_characters'] == model['split_index'] == model['train_characters']
        summaries.append(check)
    return dict(status='PASS_PUBLIC_MODELS_ONLY', training=training, long_table_rows_checked=long_rows,
                source_tables=summaries, truth_opened=False)


def engine_json(command):
    completed = subprocess.run([str(x) for x in command], check=True, capture_output=True, text=True, timeout=120)
    return json.loads(completed.stdout)


def check_engine_normalizers(shape, engine, binary_model):
    keys = [[1] + [0] * 21, [0] * 21 + [1], list(range(22)),
            [(7*i + 4) % 27 for i in range(22)]]
    summaries = []
    scales = [a for a in range(27) if math.gcd(a, 27) == 1]
    for key in keys:
        expected, _, _ = backward(shape, key)
        response = engine_json([engine, '--normalizer', binary_model] + key)
        observed = np.asarray(response['Z'])
        assert observed.shape == (27,) and min(observed) > 0
        log_error = float(np.max(abs(np.log(observed) - np.log(expected))))
        assert log_error < 1e-8
        scale_errors = []
        for scale in scales:
            transformed, _, _ = backward(shape, [(scale*x) % 27 for x in key])
            error = float(np.max(abs(np.log(transformed[[(scale*r) % 27 for r in range(27)]]) - np.log(expected))))
            assert error < 1e-8
            scale_errors.append(error)
        summaries.append(dict(key=key, minimum_state_mass=float(min(expected)),
                              max_log_error=log_error, scale_count=len(scales),
                              max_scale_log_error=max(scale_errors)))
    return summaries


def conditioned_sample(shape, key, state, rng, prepared):
    total, by_length, tails = prepared
    def draw(masses):
        total_mass = math.fsum(float(p) for p in masses)
        assert total_mass > 0
        threshold = rng.random() * total_mass
        cumulative = 0.0
        for i, mass in enumerate(masses):
            cumulative += float(mass)
            if threshold < cumulative:
                return i
        return max(i for i, mass in enumerate(masses) if mass > 0)
    n = draw([0.] + [shape['p_len'][length] * by_length[length][state] for length in range(1, shape['L']+1)])
    remaining = state
    word = []
    for pos in range(n):
        probabilities = indexed(shape['initial'], n) if not pos else indexed(shape['transition'], n)[pos-1][word[-1]]
        masses = [probabilities[unit] * tails[n][pos+1][unit, (remaining-key[unit]) % 27] for unit in range(len(key))]
        chosen = draw(masses)
        word.append(chosen)
        remaining = (remaining-key[chosen]) % 27
    assert remaining == 0
    return word


def replay_generated(manifest, shape, truth, public_cases):
    """Reconstruct every RNG choice from released seed without generator import."""
    rng = random.Random(truth['seed'])
    generated = []
    for model in manifest['models']:
        text = ' '.join((ROOT / model['source_path']).read_text().split())
        assert hashlib.sha256(text.encode()).hexdigest() == model['collapsed_sha256']
        split = len(text)*4//5
        assert split == model['split_index']
        selected = []
        for n in (77, 120):
            starts = [i for i in range(split, len(text)-n+1) if text[i] != ' '
                      and (i == 0 or text[i-1] == ' ')
                      and all(i+n <= low or i >= high for low, high in selected)]
            start = starts[rng.randrange(len(starts))]
            selected.append((start, start+n))
            message = text[start:start+n]
            while True:
                key = [rng.randrange(27) for _ in shape['signs']]
                if any(k % 3 for k in key):
                    break
            offset = rng.randrange(27)
            prepared = backward(shape, key, keep=True)
            def encode(message):
                previous = 0
                words = []
                for char in message:
                    code = 0 if char == ' ' else ord(char)-96
                    previous = (previous+code-offset) % 27
                    words.append(conditioned_sample(shape, key, previous, rng, prepared))
                return words
            positive = dict(kind='POSITIVE', language=model['language'], length=n,
                            text=message, weights=key, b=offset,
                            fragment_start=start, fragment_end=start+n,
                            split_index=split, source_sha256=model['source_sha256'], collapsed_sha256=model['collapsed_sha256'], units=encode(message),
                            tag=model['language']+'_'+str(n))
            generated.append(positive)
            if n == 77:
                permutation = list(range(n))
                rng.shuffle(permutation)
                negative = ''.join(message[i] for i in permutation)
                generated.append(dict(kind='NEGATIVE', language=model['language'], length=n,
                                      text=negative, weights=key, b=offset,
                                      permutation=permutation, parent_tag=positive['tag'],
                                      units=encode(negative), tag=model['language']+'_negative'))
    rng.shuffle(generated)
    assert len(generated) == len(truth['cases']) == len(public_cases['cases']) == 18
    for i, (actual, saved, public) in enumerate(zip(generated, truth['cases'], public_cases['cases'])):
        expected_id = f'C{i:02d}'
        assert saved['id'] == public['id'] == expected_id
        for field, value in actual.items():
            assert saved[field] == value, (expected_id, field, 'generation replay mismatch')
        assert public['units'] == actual['units']
    return dict(status='EXACT_RELEASED_SEED_REPLAY', cases=18,
                independent_generator_imported=False, scope='Reproduces source offsets, nonoverlap, keys, offsets, permutations, conditional spellings and anonymous ordering.')


def unblind_checks(truth_path, recovery_path, recovery_lock_path, models_path, cases_path):
    # Explicit invocation after root unblind only. Verify output lock BEFORE truth.
    receipt = load(recovery_lock_path)
    expected = receipt.get('recovery_sha256')
    if expected is None and 'hashes' in receipt:
        expected = receipt['hashes'].get(str(recovery_path.relative_to(ROOT)))
    if expected is None:
        matching = [r for r in receipt.get('files', []) if r['path'] == str(recovery_path.relative_to(ROOT))]
        assert len(matching) == 1, 'Receipt must bind exact recovery file before truth access'
        expected = matching[0]['sha256']
    assert digest(recovery_path) == expected
    recovered = load(recovery_path)
    manifest, public = load(models_path), load(cases_path)
    shape = load(ROOT / manifest['shape']['path'])
    tables = [load(ROOT / m['path'])['logp'] for m in manifest['models']]
    truth = load(truth_path)
    assert truth['model_manifest_sha256'] == digest(models_path)
    replay = replay_generated(manifest, shape, truth, public)
    winners = recovered['cases']
    if isinstance(winners, dict):
        winners = [dict(id=k, **v) for k, v in winners.items()]
    by_id = {c['id']: c for c in winners}
    results = []
    for hidden, case in zip(truth['cases'], public['cases']):
        winner_record = by_id[case['id']]
        winner = winner_record.get('winner', winner_record)
        key = winner['weights']
        offset = winner['b']
        assert len(key) == 22 and all(isinstance(k, int) and 0 <= k < 27 for k in key)
        assert any(k % 3 for k in key) and isinstance(offset, int) and 0 <= offset < 27
        best = score(shape, tables, case['units'], key, offset)
        true_score = score(shape, tables, case['units'], hidden['weights'], hidden['b'])
        expected_chars = [0 if c == ' ' else ord(c)-96 for c in hidden['text']]
        assert true_score['chars'] == expected_chars
        assert abs(best['total_ll']-winner['score']) < 1e-7
        if 'source_characters' in winner:
            assert best['chars'] == winner['source_characters']
        for output_key, independent_key in [('source_mixture_logp','mixture_ll'), ('source_component_logp','source_ll')]:
            if output_key in winner:
                assert np.allclose(winner[output_key], best[independent_key], rtol=1e-10, atol=1e-8)
        if 'sum_log_shape' in winner:
            assert abs(winner['sum_log_shape']-sum(packet_logp(shape,w) for w in case['units'])) < 1e-8
        exact = best['chars'] == expected_chars
        delta = best['total_ll']-true_score['total_ll']
        results.append(dict(id=case['id'], kind=hidden['kind'], language=hidden['language'], length=hidden['length'],
                            exact_message=exact, matching_characters=sum(a==b for a,b in zip(best['chars'],expected_chars)),
                            exact_effective_parameters=(key==hidden['weights'] and offset==hidden['b']),
                            observed_message_equivalent_parameters=exact,
                            parameter_identifiability=key_identifiability(case['units']),
                            winning_score=best['total_ll'], true_score=true_score['total_ll'], score_difference=delta,
                            interpretation=('EXACT_MESSAGE' if exact else 'SEARCH_FAILURE_LOWER_SCORE' if delta < -1e-7 else 'BETTER_WRONG_WINNER_MODEL_OR_FINITE_MESSAGE_AMBIGUITY' if delta > 1e-7 else 'WRONG_TIED_MESSAGE_AMBIGUITY')))
    positives = [r for r in results if r['kind']=='POSITIVE']
    assert len(positives)==12
    return dict(status='PASS_SOURCE_AND_SCORE_VALIDATION_ONLY', replay=replay, cases=results,
                exact_positive_messages=sum(r['exact_message'] for r in positives),
                primary_recovery_gate=all(r['exact_message'] for r in positives),
                recovery_sha256=expected, truth_sha256=digest(truth_path),
                limits=['Negative controls cannot establish readability.', 'Source likelihood alone is not recovery success.', 'Key equivalence is assessed only for observed message; no native pilot or translated word.'])


def compare_engine_scores(shape, tables, fixture_cases, engine, binary_model, binary_cases):
    records = []
    for index, case in enumerate(fixture_cases['cases'][:2]):
        words = case['units']
        key = [(7*i+4) % 27 for i in range(22)]
        offset = 11
        expected = score(shape, tables, words, key, offset)
        actual = engine_json([engine, '--score', binary_model, binary_cases, index, offset] + key)
        assert abs(expected['total_ll']-actual['score']) < 1e-7
        assert expected['chars'] == actual['source_characters']
        assert np.max(abs(np.array(expected['source_ll'])-actual['source_component_logp'])) < 1e-7
        assert abs(expected['mixture_ll']-actual['source_mixture_logp']) < 1e-7
        # Scale permutes Z and packet states together, leaving channel LL fixed.
        differences = [sum(key[x] for x in word) % 27 for word in words]
        differences = [(r-(differences[i-1] if i else 0)) % 27 for i, r in enumerate(differences)]
        choices = []
        for scale in range(27):
            if math.gcd(scale, 27) != 1:
                continue
            scaled = [(scale*w) % 27 for w in key]
            for b in range(27):
                chars = [(scale*r+b) % 27 for r in differences]
                value = logmeanexp([source_logp(table, chars) for table in tables]) + expected['channel_ll']
                choices.append((value, scaled, b))
        maximum = max(x[0] for x in choices)
        orbit = engine_json([engine, '--orbit', binary_model, binary_cases, index] + key)
        assert abs(maximum-orbit['score']) < 1e-7
        direct = score(shape, tables, words, orbit['weights'], orbit['b'])
        assert abs(direct['total_ll']-orbit['score']) < 1e-7
        assert direct['chars'] == orbit['source_characters']
        records.append(dict(case_index=index, coordinate_score_error=actual['score']-expected['total_ll'],
                            orbit_score_error=orbit['score']-maximum, orbit_candidates=len(choices)))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--shape', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--models', type=Path)
    parser.add_argument('--engine', type=Path)
    parser.add_argument('--binary-model', type=Path)
    parser.add_argument('--unblind', type=Path)
    parser.add_argument('--recovery', type=Path)
    parser.add_argument('--recovery-lock', type=Path)
    parser.add_argument('--cases', type=Path)
    parser.add_argument('--fixture-cases', type=Path)
    parser.add_argument('--binary-cases', type=Path)
    args = parser.parse_args()
    result = toy_controls()
    if args.shape:
        shape = load(args.shape)
        result['long_table_rows_checked'] = inspect_shape(shape)
        key = [1] + [0]*21
        z, _, _ = backward(shape, key)
        assert min(z) > 0 and abs(sum(z)-1) < 1e-12
        result['single_invertible_key_Z'] = z.tolist()
        result['shape_sha256'] = digest(args.shape)
    if args.models:
        result['public_models'] = inspect_models(args.models)
    if args.engine:
        assert args.shape and args.binary_model
        result['engine_normalizers'] = check_engine_normalizers(load(args.shape), args.engine, args.binary_model)
    if args.fixture_cases:
        assert args.engine and args.shape and args.models and args.binary_cases
        manifest = load(args.models)
        tables = [load(ROOT / m['path'])['logp'] for m in manifest['models']]
        result['engine_scores'] = compare_engine_scores(load(args.shape), tables, load(args.fixture_cases), args.engine, args.binary_model, args.binary_cases)
    if args.unblind:
        assert args.recovery and args.recovery_lock and args.models and args.cases
        result['unblinded'] = unblind_checks(args.unblind, args.recovery.resolve(), args.recovery_lock, args.models, args.cases)
    result['validator_sha256'] = digest(Path(__file__))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

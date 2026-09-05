#!/usr/bin/env python3
"""Evaluate frozen GDT832 keys; never fit a key or select by held accuracy.

The complete fit lock is checked before opening any sealed plaintext or key.
Known word/paragraph boundaries are part of this control's public observation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parent
BASE = SRC.parent
ARMS = ('FULL', 'CUT', 'OFF', 'REWIRED')


def check(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value, check_only=False):
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()
    if check_only:
        check(Path(path).read_bytes() == data, 'Artifact replay mismatch: ' + Path(path).name)
    else:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(data)


@lru_cache(maxsize=100000)
def edit_distance(left, right):
    if left == right:
        return 0
    if len(left) > len(right):
        left, right = right, left
    previous = list(range(len(left)+1))
    for j, b in enumerate(right, 1):
        current = [j]
        for i, a in enumerate(left, 1):
            current.append(min(current[-1]+1, previous[i]+1,
                               previous[i-1]+(a != b)))
        previous = current
    return previous[-1]


def metrics(rows):
    """Rows contain truth/prediction words and precomputed independent flags."""
    correct = sum(r['truth'] == r['prediction'] for r in rows)
    distance = sum(edit_distance(r['truth'], r['prediction']) for r in rows)
    characters = sum(max(len(r['truth']), len(r['prediction'])) for r in rows)
    types = {}
    for row in rows:
        types.setdefault(row['truth'], []).append(row['truth'] == row['prediction'])
    return {'words': len(rows), 'exact_words': correct,
            'word_accuracy': correct/len(rows) if rows else None,
            'edit_distance': distance, 'character_denominator': characters,
            'character_accuracy': 1-distance/characters if characters else None,
            'truth_types': len(types), 'fully_correct_truth_types': sum(all(v) for v in types.values()),
            'truth_type_accuracy': sum(all(v) for v in types.values())/len(types) if types else None}


def check_key(key, candidates):
    expected = {f'{kind}{i:02d}' for kind, n in [('L', 26), ('S', 4), ('W', 8)] for i in range(n)}
    check(set(key) == expected, 'Complete typed 26/4/8 key')
    for kind, pool, n in [('L', list('abcdefghijklmnopqrstuvwxyz'), 26),
                          ('S', candidates['suffix_pool'], 4),
                          ('W', candidates['wholeword_pool'], 8)]:
        values = [key[f'{kind}{i:02d}'] for i in range(n)]
        check(all(isinstance(v, str) and v and v in pool for v in values), 'Candidate support: ' + kind)
        check(len(set(values)) == n, 'Injective within-role key: ' + kind)


def verify_fit_lock(world_ids, candidates):
    lock = read_json(BASE / 'artifacts/FIT_LOCK.json')
    check(len(lock['selected']) == len(world_ids)*5, 'All selected fits frozen before unblinding')
    check(len(lock['restarts']) == len(world_ids)*5*8, 'All restart fits frozen before unblinding')
    required = set(lock['selected']) | set(lock['restarts'])
    check(required <= set(lock['sha256']), 'Every fit path hash-bound')
    for relative, digest in lock['sha256'].items():
        path = (BASE / relative).resolve()
        check(path.is_relative_to(BASE), 'Fit path escapes experiment')
        check(sha(path) == digest, 'Frozen fit changed: ' + relative)
    selected = [read_json(BASE / name) for name in lock['selected']]
    restarts = [read_json(BASE / name) for name in lock['restarts']]
    expected = {(w, 'real', a) for w in world_ids for a in ARMS} | {(w, 'pseudo', 'FULL') for w in world_ids}
    signature = lambda f: (f['world_id'], f['condition'], f['arm'])
    check({signature(f) for f in selected} == expected and len(selected) == len(expected), 'Complete selected arm/world panel')
    for fit in selected + restarts:
        check_key(fit['key'], candidates)
        objective = fit['discovery_objective']
        check(all(math.isfinite(float(objective[k])) for k in ('language_nats', 'family_nats', 'total_nats')), 'Finite objective')
        check(abs(objective['language_nats'] + objective['family_nats']-objective['total_nats']) < 1e-5, 'Objective components sum')
    for selected_fit in selected:
        candidates_for_arm = [f for f in restarts if signature(f) == signature(selected_fit)]
        check(len(candidates_for_arm) == 8 and len({f['seed'] for f in candidates_for_arm}) == 8, 'Eight distinct restart seeds')
        best = max(f['discovery_objective']['total_nats'] for f in candidates_for_arm)
        check(abs(selected_fit['discovery_objective']['total_nats']-best) < 1e-7, 'Selection must maximize discovery objective')
        winner = min(candidates_for_arm, key=lambda f: (-f['discovery_objective']['total_nats'], f['start']))
        check(selected_fit['start'] == winner['start'], 'Ties select lowest start')
        check(any(f['key'] == selected_fit['key'] and f['seed'] == selected_fit['seed'] for f in candidates_for_arm), 'Selected key comes from frozen restart')
    return selected, lock


def original_discovery_inventory(source_truth):
    discovery = [p for p in source_truth['paragraphs'] if p['split'] == 'discovery']
    forms = {w for p in discovery for w in p['words']}
    # Ambiguous discovery analyses count as prior possible exposure.
    lemmas = {a for p in discovery for analyses in p['lemma_sets'] if analyses for a in analyses}
    return forms, lemmas


def verify_world_source(truth, source_truth):
    check(truth['paragraphs'] == source_truth['paragraphs'], 'World plaintext/annotations must match committed original source')
    by_id = {p['paragraph_id']: p for p in source_truth['paragraphs']}
    check(len(truth['pseudo_paragraphs']) == len(by_id), 'Complete pseudo source panel')
    for paragraph in truth['pseudo_paragraphs']:
        original = by_id[paragraph['paragraph_id']]
        order = paragraph['source_order_indices']
        check(sorted(order) == list(range(len(original['words']))), 'Pseudo order is a permutation')
        check(paragraph['split'] == original['split'], 'Pseudo partition unchanged')
        for field in ('words', 'lemma_sets', 'annotation_status', 'novel_form', 'novel_lemma', 'composed'):
            check(paragraph[field] == [original[field][i] for i in order], 'Pseudo annotations follow source words')


def recovery(ciphertext, truth_paragraphs, discovery_forms, discovery_lemmas, key, true_key, discovery_cipher):
    truth_by_id = {p['paragraph_id']: p for p in truth_paragraphs if p['split'] == 'held'}
    check(len(truth_by_id) == len(ciphertext['paragraphs']), 'Held paragraph inventory')
    rows, paragraphs, predicted_paragraphs = [], [], []
    observed_ids = []
    for paragraph in ciphertext['paragraphs']:
        pid = paragraph['paragraph_id']
        check(pid in truth_by_id, 'Cipher paragraph exists in sealed source')
        observed_ids.append(pid)
        truth = truth_by_id[pid]
        check(len(paragraph['words']) == len(truth['words']) == len(truth['lemma_sets']), 'Exact word alignment')
        local, predictions = [], []
        for encoded, actual, analyses in zip(paragraph['words'], truth['words'], truth['lemma_sets']):
            check(encoded and all(code in key for code in encoded), 'Observed primitive support')
            check(''.join(true_key[c] for c in encoded) == actual, 'Generator roundtrip at held word')
            prediction = ''.join(key[c] for c in encoded)
            composed = all(not c.startswith('W') for c in encoded)
            novel_form = composed and actual not in discovery_forms
            novel_lemma = composed and analyses is not None and len(analyses) == 1 and analyses[0] not in discovery_lemmas
            macro = any(c[0] in 'SW' for c in encoded)
            row = dict(truth=actual, prediction=prediction, novel_form=novel_form,
                       novel_lemma=novel_lemma, macro=macro,
                       macro_or_novel_composed=macro or novel_form)
            rows.append(row)
            local.append(row)
            predictions.append(prediction)
        paragraphs.append({'paragraph_id': pid, **metrics(local),
                           'exact_paragraph': predictions == truth['words']})
        predicted_paragraphs.append({'paragraph_id': pid, 'words': predictions})
    check(len(set(observed_ids)) == len(observed_ids), 'No repeated held paragraph')
    support = Counter(code for p in discovery_cipher['paragraphs'] for word in p['words'] for code in word)
    held_support = Counter(code for p in ciphertext['paragraphs'] for word in p['words'] for code in word)
    check(set(held_support) <= set(support), 'No held-only informative key rule')
    key_metrics = []
    for kind in ('L', 'S', 'W'):
        active = [c for c in support if c.startswith(kind)]
        mass = sum(support[c] for c in active)
        correct = sum(key[c] == true_key[c] for c in active)
        key_metrics.append({'kind': kind, 'discovery_supported_rules': len(active),
                            'exact_supported_rules': correct,
                            'supported_rule_accuracy': correct/len(active) if active else None,
                            'discovery_mass_accuracy': sum(support[c] for c in active if key[c] == true_key[c])/mass if mass else None})
    return {'all_words': metrics(rows),
            'novel_composed_forms': metrics([r for r in rows if r['novel_form']]),
            'novel_composed_lemmas': metrics([r for r in rows if r['novel_lemma']]),
            'macro_or_novel_composed': metrics([r for r in rows if r['macro_or_novel_composed']]),
            'macro_words': metrics([r for r in rows if r['macro']]),
            'key': key_metrics, 'paragraphs': paragraphs,
            'exact_paragraphs': sum(p['exact_paragraph'] for p in paragraphs)}, predicted_paragraphs


def context_shuffle_test(paragraphs, model, seed, count=999):
    """Freeze key first. Condition on within-paragraph word multisets."""
    observed = 0.0
    null = np.zeros(count, dtype=np.float64)
    for paragraph in paragraphs:
        words = paragraph['words']
        if not words:
            continue
        vocab = sorted(set(words))
        index = {w: i for i, w in enumerate(vocab)}
        ids = np.array([index[w] for w in words], dtype=np.int64)
        initial = np.array([model.log_unigram(w) for w in vocab], dtype=np.float64)
        transitions = np.array([[model.log_conditional(a, b) for b in vocab] for a in vocab], dtype=np.float64)
        observed += float(initial[ids[0]] + transitions[ids[:-1], ids[1:]].sum())
        # Same predeclared permutations across key/arm representations.
        salt = int.from_bytes(hashlib.sha256((str(seed)+'|'+paragraph['paragraph_id']).encode()).digest()[:8], 'big')
        rng = random.Random(salt)
        for iteration in range(count):
            order = list(range(len(words)))
            rng.shuffle(order)
            permuted = ids[order]
            null[iteration] += float(initial[permuted[0]] + transitions[permuted[:-1], permuted[1:]].sum())
    exceed = int(np.count_nonzero(null >= observed))
    return {'observed_nats': observed, 'shuffle_count': count,
            'null_greater_equal': exceed, 'upper_p': (1+exceed)/(count+1),
            'null_mean_nats': float(null.mean()), 'null_scores_nats': null.tolist(),
            'word_recovery_is_not_semantic_prose': True}


def objective_for_key(discovery, key, model, model_dir, arm, spec):
    """Independent Python replay of the C++ discovery objective."""
    language = 0.0
    source_types = set()
    for paragraph in discovery['paragraphs']:
        previous, previous_w = None, False
        for encoded in paragraph['words']:
            source_types.add(tuple(encoded))
            current_w = any(code.startswith('W') for code in encoded)
            word = ''.join(key[code] for code in encoded)
            cut = arm == 'CUT' and (current_w or previous_w)
            language += model.log_conditional(None if cut else previous, word)
            previous, previous_w = word, current_w
    family_score = 0.0
    if arm != 'OFF':
        path = Path(model_dir) / ('family_rewired.tsv' if arm == 'REWIRED' else 'family_real.tsv')
        memberships = {}
        with path.open(newline='') as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                memberships[model.words[int(row['word_id'])]] = set(row['lemma_ids'].split(',')) - {''}
        groups = defaultdict(list)
        for word in sorted(source_types):
            if len(word)-1 >= spec['source_family']['minimum_shared_prefix_atoms']:
                groups[word[:-1]].append(word)
        for members in groups.values():
            degree = len(members)-1
            if not degree:
                continue
            for a, b in itertools.combinations(members, 2):
                left, right = ''.join(key[c] for c in a), ''.join(key[c] for c in b)
                if left != right and memberships.get(left, set()) & memberships.get(right, set()):
                    family_score += 1/degree
        family_score *= spec['source_family']['lambda_nats']
    return {'language_nats': language, 'family_nats': family_score,
            'total_nats': language+family_score}


def decide(results, world_ids, spec):
    thresholds = spec['recovery']
    order = spec['order_control']
    incremental = spec['incremental_information']
    by = {(r['world_id'], r['condition'], r['arm']): r for r in results}
    recovery_pass = True
    context_pass = True
    for world in world_ids:
        full = by[(world, 'real', 'FULL')]
        m = full['recovery']
        checks = [m['all_words']['word_accuracy'] >= thresholds['minimum_full_word_accuracy_each_key'],
                  m['all_words']['character_accuracy'] >= thresholds['minimum_full_character_accuracy_each_key'],
                  m['novel_composed_forms']['word_accuracy'] is not None and m['novel_composed_forms']['word_accuracy'] >= thresholds['minimum_full_novel_composed_form_accuracy_each_key'],
                  m['novel_composed_lemmas']['word_accuracy'] is not None and m['novel_composed_lemmas']['word_accuracy'] >= thresholds['minimum_full_novel_composed_lemma_accuracy_each_key']]
        recovery_pass &= all(checks)
        context_pass &= full['context_test']['upper_p'] <= order['real_p_max']
        context_pass &= by[(world, 'pseudo', 'FULL')]['context_test']['upper_p'] > order['pseudo_p_must_exceed']
    gains = {}
    for arm in ('CUT', 'OFF'):
        differences = [by[(world, 'real', 'FULL')]['recovery']['macro_or_novel_composed']['word_accuracy']-
                       by[(world, 'real', arm)]['recovery']['macro_or_novel_composed']['word_accuracy'] for world in world_ids]
        gains[arm] = {'per_world': differences, 'mean': sum(differences)/len(differences),
                      'pass': min(differences) >= incremental['minimum_each_key_gain']-1e-12 and
                      sum(differences)/len(differences) >= incremental['minimum_mean_full_minus_'+arm.lower()]-1e-12}
    gain_pass = all(g['pass'] for g in gains.values())
    status = ('CONTROL_RECOVERY_FAIL' if not recovery_pass else
              'CONTROL_RECOVERED_NO_JOINT_GAIN' if not gain_pass else
              'JOINT_GAIN_WITH_ORDER_CONTROL_FAIL' if not context_pass else
              'JOINT_CONTROL_RECOVERY_AND_GAIN_PASS')
    return {'status': status, 'recovery_pass': bool(recovery_pass),
            'context_discrimination_pass': bool(context_pass), 'joint_gain_pass': bool(gain_pass),
            'gains': gains, 'three_keys_are_not_independent_sources': True,
            'three_pseudotexts_do_not_estimate_false_positive_rate': True,
            'voynich_reading': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', required=True, type=Path)
    parser.add_argument('--model-dir', required=True, type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    encoder = read_json(SRC / 'ENCODER_SPEC.json')
    spec = read_json(SRC / 'SPEC.json')
    for relative, expected in read_json(SRC / 'PREREG_LOCK.json')['sha256'].items():
        path = (BASE / relative).resolve()
        check(path.is_relative_to(BASE) and sha(path) == expected, 'Preregistration binding')
    capacity_path = args.data_dir / 'prepared/ACTIVE_RULE_CAPACITY.json'
    capacity = read_json(capacity_path if capacity_path.exists() else args.data_dir / 'prepared/CAPACITY.json')
    if capacity['status'] not in ('SOURCE_CAPACITY_PASS', 'ACTIVE_RULE_SOURCE_CAPACITY_PASS'):
        result = {'status': 'CAPACITY_STOP', 'sealed_truth_opened': False,
                  'fits_evaluated': 0, 'voynich_reading': False}
        write_json(BASE / 'artifacts/EVALUATION.json', result, args.check)
        print(json.dumps(result, sort_keys=True))
        return 0
    candidates = read_json(args.data_dir / 'prepared/candidates.json')
    fits, lock = verify_fit_lock(encoder['world_seeds'], candidates)
    # No sealed material has been opened above this point.
    for relative, expected in read_json(SRC / 'PREREG_LOCK.json')['held_commitments'].items():
        check(sha(args.data_dir / relative) == expected, 'Held ciphertext commitment after fit freeze')
    commitments = read_json(SRC / 'PREREG_LOCK.json')['sealed_commitments']
    expected_truth_paths = {'sealed/source_truth.json'} | {f'sealed/world_{w}_truth.json' for w in encoder['world_seeds']}
    check(set(commitments) == expected_truth_paths, 'Complete prior truth commitments')
    for relative, expected in commitments.items():
        check(sha(args.data_dir / relative) == expected, 'Sealed truth commitment after complete fit freeze')
    check(sha(args.data_dir / 'sealed/source_truth.json') == capacity['source_truth_sha256'], 'Committed original plaintext and annotations')
    source_truth = read_json(args.data_dir / 'sealed/source_truth.json')
    forms, lemmas = original_discovery_inventory(source_truth)
    from reference_model import load_model
    model = load_model(args.model_dir)
    results = []
    for fit in sorted(fits, key=lambda f: (f['world_id'], f['condition'], f['arm'])):
        world = fit['world_id']
        truth = read_json(args.data_dir / f'sealed/world_{world}_truth.json')
        verify_world_source(truth, source_truth)
        stem = f'world_{world}' + ('_pseudo' if fit['condition'] == 'pseudo' else '')
        discovery = read_json(args.data_dir / f'prepared/{stem}_discovery.json')
        held = read_json(args.data_dir / f'prepared/{stem}_held.json')
        truth_rows = truth['pseudo_paragraphs'] if fit['condition'] == 'pseudo' else truth['paragraphs']
        recovered, decoded = recovery(held, truth_rows, forms, lemmas, fit['key'], truth['decode_map'], discovery)
        entry = {'world_id': world, 'condition': fit['condition'], 'arm': fit['arm'],
                 'selected_seed': fit['seed'], 'recovery': recovered}
        replayed = objective_for_key(discovery, fit['key'], model, args.model_dir, fit['arm'], spec)
        for part in replayed:
            check(abs(replayed[part]-fit['discovery_objective'][part]) < 1e-4,
                  'Independent discovery-objective replay: ' + part)
        oracle = objective_for_key(discovery, truth['decode_map'], model, args.model_dir, fit['arm'], spec)
        entry['oracle_objective'] = oracle
        entry['selected_minus_oracle'] = replayed['total_nats']-oracle['total_nats']
        entry['selected_discovery_objective_replayed'] = replayed
        if fit['arm'] == 'FULL':
            entry['context_test'] = context_shuffle_test(decoded, model, spec['order_control']['seed'], spec['order_control']['shuffles'])
        results.append(entry)
    result = {'schema': 'GDT832_EVALUATION_V1', **decide(results, encoder['world_seeds'], spec),
              'fits_evaluated': len(results), 'fit_lock_sha256': sha(BASE / 'artifacts/FIT_LOCK.json'),
              'sealed_truth_opened': True, 'results': results}
    write_json(BASE / 'artifacts/EVALUATION.json', result, args.check)
    print(json.dumps({k: v for k, v in result.items() if k != 'results'}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

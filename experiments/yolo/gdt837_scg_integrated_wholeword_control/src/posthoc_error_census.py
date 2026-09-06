#!/usr/bin/env python3
"""Post-result census of already locked GDT837 keys; no fitting or scoring.

This diagnostic is outside the preregistration. It counts active package
differences in all 48 saved restarts and attributes the six selected keys'
literal word errors. It does not change the registered recovery decision.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
EXPECTED_FIT_LOCK = 'e25befd85b812a33c5ef600b5de4383367164a35f105409a53c3cfba9f8ff4a9'
EXPECTED_PREREG_LOCK = '4abc3a794f2d070f2560f8d0319f7043de670f32d2488cc886eb05b12f365d8b'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def frozen_inputs(data):
    require(sha(data / 'src/PREREG_LOCK.json') == EXPECTED_PREREG_LOCK, 'Original preregistration unchanged')
    require(sha(data / 'artifacts/FIT_LOCK.json') == EXPECTED_FIT_LOCK, 'Original complete fit lock unchanged')
    reg, lock, spec = [read(data / name) for name in
                       ('src/PREREG_LOCK.json', 'artifacts/FIT_LOCK.json', 'src/SPEC.json')]
    for field, parent in [('sha256', data), ('upstream_sha256', ROOT),
                          ('held_commitments', data), ('confirmation_commitments', data)]:
        for relative, digest in reg[field].items():
            path = (parent / relative).resolve()
            require(path.is_relative_to(parent.resolve()), 'Registered path containment')
            require(sha(path) == digest, 'Original registered bytes unchanged: ' + relative)
    restarts = sorted(f'artifacts/fits/world_{w}_{a}_start{s}.json'
                      for w in spec['world_ids'] for a in spec['arms'] for s in spec['starts'])
    selected = sorted(f'artifacts/fits/world_{w}_{a}_selected.json'
                      for w in spec['world_ids'] for a in spec['arms'])
    require(len(restarts) == 48 and len(selected) == 6, 'Original panel sizes')
    require(lock['restarts'] == restarts and lock['selected'] == selected and
            set(lock['sha256']) == set(restarts + selected), 'Exact frozen path inventory')
    require(lock['spec_sha256'] == sha(data / 'src/SPEC.json'), 'Original policy binding')
    for relative, digest in lock['sha256'].items():
        require(sha(data / relative) == digest, 'Locked fit bytes unchanged')
    result = read(data / 'artifacts/RESULT.json')
    require(result['fit_lock_sha256'] == EXPECTED_FIT_LOCK and
            result['prereg_lock_sha256'] == EXPECTED_PREREG_LOCK, 'Result binds original locks')
    return spec, lock, result


def signature(key, truth, active):
    return tuple(sorted((truth[code]['role'], truth[code]['output'],
                         key[code]['role'], key[code]['output'])
                        for code in active if key[code] != truth[code]))


def packages(sig):
    return [{'true_role': a, 'true_output': b, 'fitted_role': c, 'fitted_output': d}
            for a, b, c, d in sig]


def split_census(cipher, source, key, truth):
    mismatched = {code for code in truth if key[code] != truth[code]}
    counts, groups, pairs = Counter(), Counter(), Counter()
    hits, errors, occurrences = Counter(), Counter(), Counter()
    require(len(cipher['paragraphs']) == len(source), 'Complete source unit alignment')
    for coded, gold in zip(cipher['paragraphs'], source):
        require(coded['paragraph_id'] == gold['paragraph_id'] and
                len(coded['words']) == len(gold['words']), 'Exact source unit and word alignment')
        local_errors = 0
        for codes, word in zip(coded['words'], gold['words']):
            require(''.join(truth[code]['output'] for code in codes) == word,
                    'Independent original-spelling roundtrip')
            predicted = ''.join(key[code]['output'] for code in codes)
            affected = set(codes) & mismatched
            bad = predicted != word
            counts['words'] += 1
            counts['wrong_words'] += bad
            counts['untouched_words'] += not affected
            counts['untouched_wrong_words'] += bad and not affected
            counts['affected_words'] += bool(affected)
            counts['affected_but_correct_words'] += bool(affected) and not bad
            local_errors += bad
            for code in affected:
                hits[code] += 1
                errors[code] += bad
                occurrences[code] += codes.count(code)
            if bad:
                require(bool(affected), 'Every wrong word has a mismatched package')
                groups[signature(key, truth, affected)] += 1
                pairs[word, predicted] += 1
        counts['source_sentences'] += 1
        counts['wrong_source_sentences'] += local_errors > 0
    require(sum(groups.values()) == counts['wrong_words'], 'Disjoint error attribution exhausts all wrong words')
    return {
        **dict(counts), 'exact_words': counts['words'] - counts['wrong_words'],
        'wrong_form_pairs': len(pairs),
        'package_counts': [{'code': code, 'true': truth[code], 'fitted': key[code],
                            'atom_occurrences': occurrences[code], 'words_containing_package': hits[code],
                            'wrong_words_containing_package': errors[code]}
                           for code in sorted(hits)],
        'disjoint_wrong_word_groups': [{'mismatched_packages': packages(sig), 'words': count}
                                      for sig, count in sorted(groups.items())],
        'top_wrong_form_pairs': [{'original': a, 'fitted': b, 'words': count}
                                 for (a, b), count in sorted(pairs.items(), key=lambda item: (-item[1], item[0]))[:12]],
    }


def census(data):
    spec, lock, result = frozen_inputs(data)
    source = read(data / 'confirmation/source_truth.json.gz')
    raw = {split: [p for p in source['paragraphs'] if p['split'] == split]
           for split in ('discovery', 'held')}
    worlds = {}
    for world in spec['world_ids']:
        truth = read(data / f'confirmation/world_{world}_truth.json.gz')['decode_map']
        cipher = {split: read(data / f'prepared/world_{world}_{split}.json.gz')
                  for split in ('discovery', 'held')}
        active = {code for p in cipher['discovery']['paragraphs'] for word in p['words'] for code in word}
        held_active = {code for p in cipher['held']['paragraphs'] for word in p['words'] for code in word}
        require(held_active <= active, 'No held-only active package')
        worlds[world] = truth, cipher, active
    classes = defaultdict(list)
    for relative in lock['restarts']:
        fit = read(data / relative)
        truth, _, active = worlds[fit['world_id']]
        classes[signature(fit['key'], truth, active)].append(
            {k: fit[k] for k in ('world_id', 'arm', 'start')})
    selected = []
    for relative in lock['selected']:
        fit = read(data / relative)
        world, arm = fit['world_id'], fit['arm']
        truth, cipher, active = worlds[world]
        splits = {split: split_census(cipher[split], raw[split], fit['key'], truth)
                  for split in ('discovery', 'held')}
        row = next(row for row in result['condition_results'] if (row['world_id'], row['arm']) == (world, arm))
        require(splits['held']['words'] == row['recovery']['all']['words'] and
                splits['held']['exact_words'] == row['recovery']['all']['exact_words'],
                'Independent census agrees with frozen held recovery')
        selected.append({'world_id': world, 'arm': arm, 'selected_start': fit['start'],
                         'active_packages': len(active),
                         'mismatched_packages': packages(signature(fit['key'], truth, active)),
                         'splits': splits})
    # Recheck immutable commitments after all reads; no historical artifact is rewritten.
    frozen_inputs(data)
    return {
        'schema': 'GDT837_POSTHOC_ERROR_CENSUS_V1', 'status': 'POSTHOC_CENSUS_REPLAY_PASS',
        'outside_preregistration': True, 'registered_scientific_status_unchanged': result['status'],
        'fit_lock_sha256': EXPECTED_FIT_LOCK, 'prereg_lock_sha256': EXPECTED_PREREG_LOCK,
        'result_sha256': sha(data / 'artifacts/RESULT.json'), 'source_sha256': sha(Path(__file__)),
        'restart_maps_censused': len(lock['restarts']), 'selected_maps_censused': len(selected),
        'all_active_packages_correct_restarts': len(classes.get((), [])),
        'active_mismatch_classes': [
            {'mismatched_packages': packages(sig), 'restarts': len(identities),
             'by_arm': dict(sorted(Counter(item['arm'] for item in identities).items())),
             'fit_identities': identities} for sig, identities in sorted(classes.items())],
        'selected_error_census': selected,
        'new_fits': 0, 'new_objective_evaluations': 0, 'new_key_selections': 0,
        'inactive_package_differences_excluded': True,
        'interpretation_limit': 'Literal fixed-map error attribution only; no causal orthography claim, suffix repair, control pass, or Voynich reading',
        'check_mode': 'Recompute independently of the fitter/evaluator and require identical diagnostic bytes; not a second independent implementation',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=BASE)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = census(args.data_dir)
    path = args.data_dir / 'artifacts/POSTHOC_ERROR_CENSUS.json'
    raw = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
    if args.check:
        require(path.read_bytes() == raw, 'Posthoc diagnostic byte replay')
    else:
        path.write_bytes(raw)
    print(json.dumps({'status': result['status'], 'restart_maps': result['restart_maps_censused'],
                      'all_active_packages_correct_restarts': result['all_active_packages_correct_restarts'],
                      'classes': [{k: row[k] for k in ('mismatched_packages', 'restarts', 'by_arm')}
                                  for row in result['active_mismatch_classes']],
                      'selected_first_split_counts': {split: {k: value[k] for k in ('words', 'wrong_words', 'affected_words', 'untouched_wrong_words')}
                                                     for split, value in result['selected_error_census'][0]['splits'].items()}}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

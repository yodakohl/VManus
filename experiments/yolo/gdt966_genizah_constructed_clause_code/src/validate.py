#!/usr/bin/env python3
"""Independent GDT966 source, certificate, code and artifact validator.

Does not import the GDT966 runner. The historical GDT900 enumerator is loaded
only to replay claimed exhaustive results. No timings enter the output receipt.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import importlib.util
import itertools
import json
import sys
import time
import unicodedata
from fractions import Fraction
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
ART = E / 'artifacts'
P905 = ROOT / 'experiments/yolo/gdt905_joint_cv_complete_passage_candidates'
REVIEWED_SPEC = '15cecdcd70307bad9e386581e72c06ddd769a1d29187b95f3a0fbaab40a1fe17'
SOURCE_HASH = '8e2246879c5b2dd1e8f00600fda7f8110c997c0cdaed4f56cb07ff003f23ed36'
ALPHABET = 'acdefghiklmnopqrstxy'
EDITION_ORDER = ('IT2a', 'RF1b', 'ZL3b')
CHECKS = []

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(value, message):
    if not value:
        raise ValueError(message)

def check(name, value, **details):
    CHECKS.append({'name': name, 'ok': bool(value), **details})

def read_table(path):
    with path.open(encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        return reader.fieldnames, list(reader)

def unitize(word):
    output = []
    for char in unicodedata.normalize('NFD', word):
        if unicodedata.combining(char):
            require(bool(output), 'orphan source mark')
            output[-1] += char
        else:
            require('\u05d0' <= char <= '\u05ea', 'non-Hebrew source base')
            output.append(char)
    return output

def source_replay():
    spec, source = read(E / 'src/SPEC.json'), read(E / 'src/SOURCE.json')
    check('reviewed_source_and_spec_bytes', digest(E / 'src/SPEC.json') == REVIEWED_SPEC and
          digest(E / 'src/SOURCE.json') == SOURCE_HASH and spec['source_sha256'] == SOURCE_HASH and
          REVIEWED_SPEC in (E / 'src/SOURCE_REVIEW.md').read_text(encoding='utf-8'))
    blocks = source['transcription']
    require([b['face'] for b in blocks] == ['recto', 'verso', 'verso, right margin'], 'source faces')
    for block, count in zip(blocks, (21, 21, 4)):
        require([line['n'] for line in block['lines']] == list(range(1, count + 1)), 'source line numbering')
    r, v, _ = [[line['text'] for line in block['lines']] for block in blocks]
    require(r[4].startswith('אלכוך.') and r[12].endswith('אלרמֹאן') and
            v[4].endswith('אלספרגֹל') and v[14].startswith('אלתֹפאחֹ'), 'named head boundaries')
    spans = [r[4:12] + [r[12].split('אלרמֹאן')[0].rstrip()],
             ['אלרמֹאן'] + r[13:] + v[:4] + [v[4].split('אלספרגֹל')[0].rstrip()],
             ['אלספרגֹל'] + v[5:14]]
    records, errors = {}, []
    ids = ['PEACH', 'POMEGRANATE', 'QUINCE']
    require([item['id'] for item in source['records']] == ids, 'source records')
    for rid, lines, stored in zip(ids, spans, source['records']):
        words = ' '.join(lines).replace('.', '').replace(';', '').split()
        graph_words = [unitize(w) for w in words]
        stream = [u for word in graph_words for u in word]
        rebuilt = {'lines': lines, 'words': words, 'grapheme_words': graph_words,
                   'word_count': len(words), 'grapheme_count': len(stream),
                   'unit_counts': dict(collections.Counter(stream)), 'word_type_count': len(set(words))}
        errors.extend(rid + ':' + key for key, value in rebuilt.items() if stored.get(key) != value)
        records[rid] = rebuilt
    vocabulary = sorted({w for record in records.values() for w in record['words']})
    inventory = sorted({u for w in vocabulary for u in unitize(w)})
    check('full_transcription_record_reconstruction', not errors, errors=errors,
          words=[records[k]['word_count'] for k in ids],
          clusters=[records[k]['grapheme_count'] for k in ids])
    check('source_vocabulary_and_mark_inventory', len(vocabulary) == 157 and len(inventory) == 32 and
          spec['source_vocabulary'] == vocabulary and spec['source_units'] == inventory and
          all(unicodedata.normalize('NFD', w) == w for w in vocabulary))
    pointer_errors = []
    for category in ('heads', 'modifiers', 'predicates'):
        for option in spec[category]:
            if any(w not in vocabulary for w in option['words']):
                pointer_errors.append(category + ':' + option['id'] + ':unattested')
            expected_evidence = []
            for word in option['words']:
                occurrences = [{'record': rid, 'first_word_1based': index + 1, 'last_word_1based': index + 1}
                               for rid in ids for index, value in enumerate(records[rid]['words']) if value == word]
                expected_evidence.append({'word': word, 'occurrences': occurrences})
            if option.get('word_evidence', []) != expected_evidence:
                pointer_errors.append(category + ':' + option['id'] + ':occurrences')
    for extension in spec['extensions']:
        expected_evidence = []
        for rid in ids:
            words = records[rid]['words']; size = len(extension['words'])
            for index in range(len(words) - size + 1):
                if words[index:index + size] == extension['words']:
                    expected_evidence.append({'record': rid, 'first_word_1based': index + 1,
                                              'last_word_1based': index + size})
        if extension['source_evidence'] != expected_evidence or not expected_evidence:
            pointer_errors.append(extension['id'] + ':exact_extension_interval')
    check('all_slot_and_extension_source_pointers', not pointer_errors, errors=pointer_errors)
    require(spec['channel']['target_alphabet'] == ALPHABET, 'fixed target alphabet')
    products = []
    for head in spec['heads']:
        for modifier in spec['modifiers']:
            for predicate in spec['predicates']:
                for extension in spec['extensions']:
                    if extension['kind'] == 'conditional' and modifier['id'] != 'NONE':
                        continue
                    derivation = {'head': head['id'], 'modifier': modifier['id'],
                                  'predicate': predicate['id'], 'extension': extension['id']}
                    words = sum((x['words'] for x in (head, modifier, predicate, extension)), [])
                    label = ':'.join(derivation.values())
                    noun = ' '.join(x for x in (modifier['working_translation'], head['working_translation']) if x)
                    translation = 'The ' + noun + ' is ' + predicate['working_translation'] + '. ' + extension['working_translation']
                    products.append({'id': label, 'derivation': derivation, 'words': words,
                                     'word_count': len(words), 'grapheme_words': [unitize(w) for w in words],
                                     'working_translation': translation,
                                     'status': 'ELIGIBLE' if 12 <= len(words) <= 24 else 'OUTSIDE_REGISTERED_WORD_COUNT'})
    used_words = {w for product in products for w in product['words']}
    used_units = {u for w in used_words for u in unitize(w)}
    check('all_81_generated_paragraphs', len(products) == 81 and len({tuple(p['words']) for p in products}) == 81 and
          read(ART / 'GENERATED_PARAGRAPHS.json') == products and
          collections.Counter(p['word_count'] for p in products) == {12: 9, 13: 24, 14: 15, 15: 12, 16: 12, 17: 3, 18: 6},
          products=len(products), used_forms=len(used_words), used_units=len(used_units),
          unobserved_in_language=sorted(set(inventory) - used_units))
    return spec, products

def prefix_legal(code, inventory):
    if not isinstance(code, dict) or not set(code) <= set(inventory):
        return False
    values = list(code.values())
    if any(not isinstance(word, str) or not word or set(word) - set(ALPHABET) for word in values):
        return False
    return not any(a.startswith(b) or b.startswith(a)
                   for index, a in enumerate(values) for b in values[index + 1:])

def completable(code, inventory):
    if not prefix_legal(code, inventory):
        return False
    if set(code) == set(inventory):
        return True
    return sum((Fraction(1, len(ALPHABET) ** len(value)) for value in code.values()), Fraction(0)) < 1

def complete_with_trie(observed, inventory):
    """Independent trie construction of the frozen deterministic representative."""
    if not completable(observed, inventory):
        return None
    missing = sorted(set(inventory) - set(observed))
    if not missing:
        return dict(observed)
    trie = {}
    for value in observed.values():
        node = trie
        for char in value:
            node = node.setdefault(char, {})
        node[None] = True
    queue = collections.deque([('', trie)])
    branch = None
    while queue and branch is None:
        prefix, node = queue.popleft()
        for char in ALPHABET:
            if char not in node:
                branch = prefix + char
                break
            if None not in node[char]:
                queue.append((prefix + char, node[char]))
    require(branch is not None, 'Kraft/trie completion disagreement')
    width = 0
    while len(ALPHABET) ** width < len(missing):
        width += 1
    endings = itertools.product(ALPHABET, repeat=width)
    result = dict(observed)
    for unit, ending in zip(missing, endings):
        result[unit] = branch + ''.join(ending)
    return result

def completion_checks(inventory):
    full_tree = dict(zip(inventory[:len(ALPHABET)], ALPHABET))
    open_tree = dict(zip(inventory[:len(ALPHABET) - 1], ALPHABET[:-1]))
    completed = complete_with_trie(open_tree, inventory)
    check('independent_completion_capacity_self_checks', not completable(full_tree, inventory) and
          completed is not None and set(completed) == set(inventory) and prefix_legal(completed, inventory) and
          all(completed[k] == v for k, v in open_tree.items()))

def targets_replay():
    cache = read(P905 / 'artifacts/TARGET.json')
    scope = {}
    for edition, panel in cache['panels'].items():
        scope[edition] = {'total': len(panel), 'selected': sum(12 <= len(row['words']) <= 24 for row in panel),
                          'excluded': [{'paragraph_id': row['paragraph_id'], 'word_count': len(row['words']),
                                        'reason': 'OUTSIDE_REGISTERED_12_24_GROUP_SCOPE'}
                                       for row in panel if not 12 <= len(row['words']) <= 24]}
    check('original_905_scope_and_exclusions', read(P905 / 'artifacts/SCOPE.json') == scope)
    targets = []
    for edition in EDITION_ORDER:
        for row in sorted(cache['panels'][edition], key=lambda row: row['paragraph_id']):
            require(not row['page'].startswith('f84') and row['page'] != 'f116v', 'forbidden target page')
            if 12 <= len(row['words']) <= 24:
                targets.append({'id': edition + ':' + row['paragraph_id'], 'edition': edition, **row})
    check('all_49_original_target_selections', collections.Counter(t['edition'] for t in targets) ==
          {'IT2a': 41, 'RF1b': 5, 'ZL3b': 3} and len({t['paragraph_id'] for t in targets}) == 41 and
          len({t['physical_folio'] for t in targets}) == 15,
          targets=len(targets), by_edition=dict(collections.Counter(t['edition'] for t in targets)))
    expected_scope = {'targets': [{k: v for k, v in row.items() if k != 'words'} for row in targets],
                      'parent_scope': 'GDT905 artifacts/SCOPE.json unchanged; all49 original selectedcases',
                      'source_products': 81, 'cases': 3969, 'independent_confirmation_capacity': 0}
    check('registered_target_scope_receipt', read(ART / 'SCOPE.json') == expected_scope)
    return targets

def prediction(target, product):
    return {'id': target['id'] + '|' + product['id'], 'target_id': target['id'], 'edition': target['edition'],
            'page': target['page'], 'physical_folio': target['physical_folio'], 'source_id': product['id'],
            'required_word_count': product['word_count'],
            'required_characters': sum(len(word) for word in product['grapheme_words']),
            'required_distinct_units': len({u for word in product['grapheme_words'] for u in word}),
            'required_complete_source': 'GENERATED_PARAGRAPHS.json#' + product['id'],
            'required_relation': 'EXACT_WORD_EQUATIONS_GLOBAL_PREFIX_FREE_CODE_FULL32_COMPLETION',
            'independent_confirmation_capacity': 0}

def equality_labels(words):
    previous, output = [], []
    for word in words:
        if word not in previous:
            previous.append(word)
        output.append(previous.index(word))
    return output

def prefix_length(left, right):
    index = 0
    while index < min(len(left), len(right)) and left[index] == right[index]:
        index += 1
    return index

def certificates(target, product):
    groups, words = product['grapheme_words'], target['words']
    if any(not word or not word.isascii() or not word.isalpha() or not word.islower() for word in words):
        return {'status': 'UNKNOWN_SOURCE', 'contradictions': [{'kind': 'NONLITERAL_TARGET'}]}
    failures = []
    outside = sorted(set(''.join(words)) - set(ALPHABET))
    if outside:
        failures.append({'kind': 'TARGET_ALPHABET', 'characters': outside})
    if len(groups) != len(words):
        failures.append({'kind': 'WORD_COUNT', 'required': len(groups), 'observed': len(words)})
    else:
        for index in range(len(words)):
            if len(groups[index]) > len(words[index]):
                failures.append({'kind': 'NONEMPTY_WORD_LENGTH', 'position': index + 1,
                                 'required': len(groups[index]), 'observed': len(words[index])})
        source_pattern, target_pattern = equality_labels(product['words']), equality_labels(words)
        if source_pattern != target_pattern:
            failures.append({'kind': 'WHOLE_WORD_EQUALITY', 'required': source_pattern, 'observed': target_pattern})
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                x, y, a, b = groups[i], groups[j], words[i], words[j]
                source_xy, source_yx = x == y[:len(x)], y == x[:len(y)]
                target_xy, target_yx = a == b[:len(a)], b == a[:len(b)]
                if source_xy != target_xy or source_yx != target_yx:
                    failures.append({'kind': 'WORD_PREFIX_ORDER', 'positions': [i + 1, j + 1]})
                for kind, left, right, observed_left, observed_right in (
                    ('SHARED_PREFIX_LENGTH', x, y, a, b),
                    ('SHARED_SUFFIX_LENGTH', x[::-1], y[::-1], a[::-1], b[::-1])):
                    required, observed = prefix_length(left, right), prefix_length(observed_left, observed_right)
                    if required > observed:
                        failures.append({'kind': kind, 'positions': [i + 1, j + 1],
                                         'required': required, 'observed': observed})
    return {'status': 'CONTRADICTED_NECESSARY' if failures else 'NEEDS_EXACT_SEARCH', 'contradictions': failures}

def engine():
    folder = ROOT / 'experiments/yolo/gdt900_cumanicus_complete_trilingual_tables/src'
    sys.path.insert(0, str(folder)); sys.setrecursionlimit(10000)
    spec = importlib.util.spec_from_file_location('gdt966_validation_gdt900', folder / 'run.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def rendered(code, product):
    return [''.join(code[u] for u in word) for word in product['grapheme_words']]

def witness_valid(witness, product, target, inventory):
    observed, completed = witness.get('observed_code'), witness.get('completed_code')
    used = {u for word in product['grapheme_words'] for u in word}
    return (isinstance(observed, dict) and set(observed) == used and prefix_legal(observed, inventory) and
            isinstance(completed, dict) and set(completed) == set(inventory) and prefix_legal(completed, inventory) and
            completed == complete_with_trie(observed, inventory) and
            witness.get('unobserved_units') == sorted(set(inventory) - used) and
            witness.get('source_id') == product['id'] and witness.get('target_id') == target['id'] and
            rendered(completed, product) == target['words'])

def as_table(rows, fields):
    return [{key: '' if row.get(key) is None else str(row.get(key, '')) for key in fields} for row in rows]

def artifact_replay(spec, products, targets):
    names = ('NECESSARY_CASES.json', 'ALL_CASES.json', 'WITNESSES.json', 'FIXED_KEY_TRANSFER.json',
             'CANDIDATE_TABLE.tsv', 'EQUIVALENT_OBSERVATIONS.json', 'RESULT.json')
    missing = [name for name in names if not (ART / name).is_file()]
    check('complete_evaluation_artifacts', not missing, missing=missing)
    if missing:
        return {'evaluation': 'NOT_READY', 'missing': missing}
    predictions = [prediction(target, product) for target in targets for product in products]
    fields, table = read_table(ART / 'PREDICTIONS.tsv')
    check('all_3969_preregistered_predictions', fields == list(predictions[0]) and
          table == as_table(predictions, fields) and len(predictions) == 3969)
    expected = [dict(prediction(target, product), **certificates(target, product))
                for target in targets for product in products]
    check('all_applicable_necessary_certificates', read(ART / 'NECESSARY_CASES.json') == expected,
          cases=len(expected), statuses=dict(collections.Counter(row['status'] for row in expected)))
    cases = read(ART / 'ALL_CASES.json')
    require(len(cases) == len(expected), 'final case denominator')
    pmap, tmap = {p['id']: p for p in products}, {t['id']: t for t in targets}
    inventory = spec['source_units']; errors, incomplete = [], []; verified_exhaustive = 0
    old = None
    for original, case in zip(expected, cases):
        cid = original['id']; status = case.get('status')
        if original['status'] != 'NEEDS_EXACT_SEARCH':
            if case != original:
                errors.append(cid + ':fixed_necessary_or_unknown_case_changed')
            continue
        if any(case.get(key) != value for key, value in original.items() if key != 'status'):
            errors.append(cid + ':prediction_or_certificate_changed')
        product, target = pmap[original['source_id']], tmap[original['target_id']]
        witnesses = case.get('witnesses', [])
        if not isinstance(witnesses, list):
            errors.append(cid + ':witness_list'); continue
        unique = set()
        for witness in witnesses:
            if not witness_valid(witness, product, target, inventory):
                errors.append(cid + ':invalid_exact_completed_witness')
            unique.add(json.dumps(witness.get('observed_code'), sort_keys=True, ensure_ascii=False))
        if len(unique) != len(witnesses) or len(witnesses) > 16:
            errors.append(cid + ':observed_key_multiplicity')
        done = case.get('complete_enumeration')
        if status == 'UNSAT_EXACT':
            valid_status = done is True and not witnesses and 'limit' not in case
        elif status == 'SAT_COMPLETE_ENUMERATION':
            valid_status = done is True and 1 <= len(witnesses) < 16 and 'limit' not in case
        elif status == 'SAT_INCOMPLETE_ENUMERATION':
            valid_status = done is False and 1 <= len(witnesses) <= 16 and case.get('limit') in (
                '16_OBSERVED_KEYS', 'LOCAL_2_SECONDS', 'GLOBAL_BUDGET')
            if case.get('limit') == '16_OBSERVED_KEYS':
                valid_status = valid_status and len(witnesses) == 16
        elif status == 'UNKNOWN_COMPUTATION':
            valid_status = done is False and not witnesses and case.get('limit') in ('LOCAL_2_SECONDS', 'GLOBAL_BUDGET')
        elif status == 'UNKNOWN_GLOBAL_BUDGET':
            valid_status = done is False and not witnesses
        else:
            valid_status = False
        if not valid_status:
            errors.append(cid + ':status_or_unknown_accounting')
        if status in ('UNSAT_EXACT', 'SAT_COMPLETE_ENUMERATION'):
            if old is None:
                old = engine()
            replay = []
            try:
                equations = [(word, target['words'][index]) for index, word in enumerate(product['grapheme_words'])]
                for observed in old.solve_words(equations, time.monotonic() + 2):
                    if completable(observed, inventory):
                        replay.append(observed)
                        if len(replay) > len(witnesses):
                            break
                if replay != [w['observed_code'] for w in witnesses]:
                    errors.append(cid + ':false_exhaustive_result')
                else:
                    verified_exhaustive += 1
            except old.Budget:
                incomplete.append(cid)
    witness_count = sum(len(row.get('witnesses', [])) for row in cases)
    exact_case_count = sum(row['status'] == 'NEEDS_EXACT_SEARCH' for row in expected)
    check('all_final_cases_and_exact_witnesses', not errors, error_count=len(errors), errors=errors[:60],
          exact_witnesses_exercised=witness_count)
    check('claimed_exhaustive_search_replay', not incomplete,
          verified_cases=verified_exhaustive, incomplete=incomplete,
          exercised=bool(verified_exhaustive or incomplete),
          execution_scope='NO_EXACT_CASES' if not exact_case_count else 'CLAIMED_EXHAUSTIVE_RESULTS_ONLY')
    witnesses = []
    for case in cases:
        for local in case.get('witnesses', []):
            witnesses.append({'id': 'W' + str(len(witnesses) + 1).zfill(6), 'case_id': case['id'], **local})
    check('all_witness_receipts', read(ART / 'WITNESSES.json') == witnesses, witnesses=len(witnesses))
    transfers = []
    case_map = {case['id']: case for case in cases}
    for witness in witnesses:
        seed = case_map[witness['case_id']]
        # This is one frozen complete key. It never quantifies over other completions.
        for target in targets:
            if target['edition'] != seed['edition']:
                continue
            matches = [p['id'] for p in products if tuple(rendered(witness['completed_code'], p)) == tuple(target['words'])]
            transfers.append({'witness_id': witness['id'], 'target_id': target['id'],
                              'physical_folio': target['physical_folio'],
                              'same_physical_folio': target['physical_folio'] == seed['physical_folio'],
                              'source_ids': matches,
                              'status': 'EXACT_FIXED_COMPLETION_READING' if matches else 'NO_READING_UNDER_THIS_COMPLETION',
                              'independent_confirmation_capacity': 0})
    check('all_frozen_completed_key_transfers', read(ART / 'FIXED_KEY_TRANSFER.json') == transfers,
          rows=len(transfers), exercised=bool(witnesses),
          execution_scope='FIXED_COMPLETIONS_ONLY' if witnesses else 'EMPTY_RECEIPT_ONLY_NO_WITNESSES')
    candidate_rows = [{'id': row['id'], 'target_id': row['target_id'], 'source_id': row['source_id'],
                       'status': row['status'],
                       'contradictions': json.dumps(row['contradictions'], ensure_ascii=False, separators=(',', ':')),
                       'witness_count': len(row.get('witnesses', [])),
                       'complete_enumeration': row.get('complete_enumeration', 'NA'),
                       'independent_confirmation_capacity': 0} for row in cases]
    fields, actual_table = read_table(ART / 'CANDIDATE_TABLE.tsv')
    check('complete_candidate_table', fields == list(candidate_rows[0]) and
          actual_table == as_table(candidate_rows, fields), rows=len(actual_table))
    grouped = collections.defaultdict(list)
    for row in cases:
        signature = json.dumps({'status': row['status'], 'contradictions': row['contradictions']},
                               sort_keys=True, separators=(',', ':'))
        grouped[signature].append(row['id'])
    expected_groups = [{'observation': json.loads(key), 'cases': grouped[key]} for key in sorted(grouped)]
    check('equivalent_observations_preserve_every_case', read(ART / 'EQUIVALENT_OBSERVATIONS.json') == expected_groups,
          groups=len(expected_groups))
    result = read(ART / 'RESULT.json')
    transfer_ids = sorted({row['witness_id'] for row in transfers if row['source_ids'] and not row['same_physical_folio']})
    required = {'status': 'FINITE_CONSTRUCTION_EVALUATED', 'cases': 3969, 'source_products': 81, 'targets': 49,
                'counts': dict(collections.Counter(row['status'] for row in cases)),
                'exact_cases': sum(row['status'] == 'NEEDS_EXACT_SEARCH' for row in expected),
                'observed_code_witnesses': len(witnesses),
                'witnesses_transferring_to_other_physical_leaf': transfer_ids,
                'observation_groups': len(expected_groups), 'confirmed_words': 0, 'independent_confirmation_capacity': 0}
    check('result_reconciliation_and_claim_limits', all(result.get(key) == value for key, value in required.items()))
    return {'evaluation': 'ALL_CASES_CHECKED', 'cases': len(cases), 'source_products': len(products),
            'targets': len(targets), 'counts': required['counts'], 'exact_cases': required['exact_cases'],
            'witnesses': len(witnesses), 'fixed_completion_transfer_rows': len(transfers),
            'exact_solver_execution': 'NOT_NEEDED_NO_EXACT_CASES' if not exact_case_count else 'SEE_EXHAUSTIVE_REPLAY_CHECK',
            'witness_execution': 'NOT_EXERCISED_NO_WITNESSES' if not witnesses else 'EXACT_CODES_AND_FIXED_COMPLETIONS_CHECKED',
            'incomplete_exhaustive_replays': len(incomplete)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true', help='validate source and hashes without parsing target data')
    args = parser.parse_args(); summary = {}
    try:
        lock_path = E / 'PREREG_LOCK.json'; errors = []
        if lock_path.exists():
            for relative, expected in read(lock_path)['files'].items():
                path = ROOT / relative
                if not path.is_file() or digest(path) != expected:
                    errors.append(relative)
            check('frozen_input_hashes', not errors, errors=errors)
        else:
            check('frozen_input_hashes', args.source_only, state='NOT_REGISTERED')
        spec, products = source_replay()
        completion_checks(spec['source_units'])
        if args.source_only:
            summary = {'evaluation': 'SOURCE_ONLY_NOT_TARGET_VALIDATED'}
        else:
            require(lock_path.exists() and not errors, 'valid registration lock required for target validation')
            summary = artifact_replay(spec, products, targets_replay())
    except Exception as error:
        check('validation_execution', False, error_type=type(error).__name__,
              message=str(error).replace(str(ROOT), '<repo>'))
    ok = all(item['ok'] for item in CHECKS)
    status = 'SOURCE_VALIDATION_PASS' if ok and args.source_only else 'VALIDATION_PASS' if ok else 'VALIDATION_FAIL'
    if summary.get('incomplete_exhaustive_replays'):
        status = 'VALIDATION_INCOMPLETE'
    if summary.get('evaluation') == 'NOT_READY':
        status = 'VALIDATION_NOT_READY'
    output = {'experiment_id': 'GDT966', 'status': status,
              'independent_algorithm': 'full source and occurrence replay; finite product reconstruction; original cache selection; independent necessary certificates; exact trie/Kraft completion; full witness and frozen-key transfer replay',
              'checks': CHECKS, 'summary': summary,
              'claim_ceiling': 'Validation of this finite model only. Source/computation unknowns remain unknown; fixed-completion failure does not exclude other completions. No confirmed meaning.'}
    (ART / 'VALIDATION.json').write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'checks': len(CHECKS),
                      'failed_checks': [item['name'] for item in CHECKS if not item['ok']], **summary}, ensure_ascii=False))
    return 0 if status in ('VALIDATION_PASS', 'SOURCE_VALIDATION_PASS') else 1

if __name__ == '__main__':
    raise SystemExit(main())

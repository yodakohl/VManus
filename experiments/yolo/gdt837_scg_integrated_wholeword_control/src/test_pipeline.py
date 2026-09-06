#!/usr/bin/env python3
"""Invented-fixture checks for the GDT837 wrapper; never opens control data.

Engine mutation/cache tests remain in the byte-frozen GDT836 suite.  This
suite exercises the new compression, provenance, pairing and decision layer.
"""
from __future__ import annotations

from copy import deepcopy
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SRC = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location('gdt837_test_' + name, SRC / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def toy_key():
    values = ([('L', letter) for letter in 'abcdefghijklmnopqrstuvwxyz'] +
              [('S', suffix) for suffix in ('am', 'as', 'em', 'es')] +
              [('W', word) for word in ('ab', 'ac', 'an', 'at', 'de', 'ex', 'ne', 'si')])
    return {f'X{i:02d}': {'role': role, 'output': value}
            for i, (role, value) in enumerate(values)}


def toy_pairs(spec):
    fits = []
    for world in spec['world_ids']:
        for start in spec['starts']:
            for arm in ('RELAXED', 'STRICT'):
                final = toy_key()
                if arm == 'STRICT':
                    final['X00']['output'], final['X01']['output'] = 'b', 'a'
                fits.append({'world_id': world, 'start': start, 'arm': arm,
                             'status': 'FIT_COMPLETE',
                             'initial_key': toy_key(), 'key': final,
                             'initialization_attempts': start + 1,
                             'initialization_seed': 837500000 + 100 * world + start,
                             'search_seed': 837000000 + 100 * world + start,
                             'discovery_objective': {'total_nats': -12.5,
                                'language_nats': -12.5, 'family_nats': 0.0}})
    return fits


def engine_output():
    lines = ['SCORE\t-12.5\t-12.5\t0', 'PROPOSALS\t60000',
             'INITIALIZATION_ATTEMPTS\t3', 'INITIALIZATION_SEED\t837501700',
             'SEARCH_SEED\t837001700', 'PRIORITY_REJECTIONS\t12']
    key = toy_key()
    for index in range(38):
        row = key[f'X{index:02d}']
        lines.append(f'INITIAL\t{index}\t{row["role"]}\t{row["output"]}')
    key['X00']['output'], key['X01']['output'] = 'b', 'a'
    for index in range(38):
        row = key[f'X{index:02d}']
        lines.append(f'{index}\t{row["role"]}\t{row["output"]}')
    return lines


class PipelineTests(unittest.TestCase):
    def test_runner_rejects_incomplete_unpaired_or_seed_changed_panels(self):
        runner = module('run')
        spec = {'world_ids': [17, 29, 41], 'arms': ['RELAXED', 'STRICT'],
                'starts': list(range(8))}
        fits = toy_pairs(spec)
        runner.check_pairs(fits, spec)
        invalid = [fits[:-1], fits + [deepcopy(fits[0])]]
        duplicate = deepcopy(fits)
        duplicate[-1] = deepcopy(duplicate[0])
        invalid.append(duplicate)
        for field in ('initial_key', 'initialization_attempts'):
            changed = deepcopy(fits)
            if field == 'initial_key':
                changed[1][field]['X24']['output'] = 'z'
                changed[1][field]['X25']['output'] = 'y'
            else:
                changed[1][field] += 1
            invalid.append(changed)
        for field in ('search_seed', 'initialization_seed'):
            changed = deepcopy(fits)
            for fit in changed[:2]:
                fit[field] += 1
            invalid.append(changed)
        for value in (0, 1001, True, 1.0):
            changed = deepcopy(fits)
            for fit in changed[:2]:
                fit['initialization_attempts'] = value
            invalid.append(changed)
        changed = deepcopy(fits)
        changed[-1]['status'] = 'INITIALIZATION_STOP'
        invalid.append(changed)
        for field in ('total_nats', 'language_nats', 'family_nats'):
            for value in (float('nan'), float('inf'), -float('inf')):
                changed = deepcopy(fits)
                changed[-1]['discovery_objective'][field] = value
                invalid.append(changed)
        for index, changed in enumerate(invalid):
            with self.subTest(case=index), self.assertRaises(ValueError):
                runner.check_pairs(changed, spec)

    def test_selection_uses_only_complete_paired_discovery_panel_and_first_tied_start(self):
        runner = module('run')
        spec = {'world_ids': [17, 29, 41], 'arms': ['RELAXED', 'STRICT'],
                'starts': [7, 5, 2, 0, 1, 3, 4, 6],
                'optimizer': {'annealing_steps': 60000, 'polish_sweeps': 4}}
        with tempfile.TemporaryDirectory() as tmp:
            exp = Path(tmp)
            runner.save(exp / 'src/SPEC.json', spec)
            fits = toy_pairs(spec)
            paths = []
            for fit in fits:
                score = (-10.0 if fit['start'] in (2, 5) else -99.0) if fit['arm'] == 'RELAXED' else (20.0 if fit['start'] == 4 else -99.0)
                fit['discovery_objective'] = {'total_nats': score, 'language_nats': score, 'family_nats': 0.0}
                path = exp / f'artifacts/fits/world_{fit["world_id"]}_{fit["arm"]}_start{fit["start"]}.json'
                runner.save(path, fit)
                paths.append(path)
            last_contents = paths[-1].read_bytes()
            paths[-1].unlink()
            with self.assertRaises((FileNotFoundError, ValueError)):
                runner.lock_fits(spec, exp=exp)
            self.assertFalse((exp / 'artifacts/FIT_LOCK.json').exists())
            self.assertEqual(list((exp / 'artifacts/fits').glob('*_selected.json')), [])
            paths[-1].write_bytes(last_contents)
            stopped = deepcopy(fits[-1])
            stopped['status'] = 'INITIALIZATION_STOP'
            runner.save(paths[-1], stopped)
            with self.assertRaises(ValueError):
                runner.lock_fits(spec, exp=exp)
            self.assertFalse((exp / 'artifacts/FIT_LOCK.json').exists())
            paths[-1].write_bytes(last_contents)
            selected_paths = {exp / f'artifacts/fits/world_{w}_{a}_selected.json'
                              for w in spec['world_ids'] for a in spec['arms']}
            allowed_reads = set(paths) | selected_paths | {exp / 'src/SPEC.json'}
            original_open = Path.open
            reads = []

            def guarded_open(path, mode='r', *args, **kwargs):
                if 'r' in mode or '+' in mode:
                    if Path(path) not in allowed_reads:
                        raise AssertionError('Selection attempted a non-fit/non-spec read')
                    reads.append(Path(path))
                return original_open(path, mode, *args, **kwargs)

            with mock.patch.object(Path, 'open', guarded_open):
                lock = runner.lock_fits(spec, exp=exp)
            self.assertEqual(len(lock['restarts']), 48)
            self.assertEqual(len(lock['selected']), 6)
            self.assertTrue(lock['paired_initializations_identical'])
            self.assertEqual(set(lock['sha256']), set(lock['restarts'] + lock['selected']))
            self.assertTrue(set(paths) <= set(reads))
            for relative, digest in lock['sha256'].items():
                self.assertEqual(digest, runner.sha(exp / relative))
            for relative in lock['selected']:
                selected = runner.read_json(exp / relative)
                self.assertEqual(selected['start'], 2 if selected['arm'] == 'RELAXED' else 4)

    def test_registered_lock_check_rejects_missing_hashes_and_nonwinning_selection(self):
        runner = module('run')
        spec = {'world_ids': [17, 29, 41], 'arms': ['RELAXED', 'STRICT'],
                'starts': list(range(8)),
                'optimizer': {'annealing_steps': 60000, 'polish_sweeps': 4}}
        with tempfile.TemporaryDirectory() as tmp:
            exp = Path(tmp)
            runner.save(exp / 'src/SPEC.json', spec)
            fits = toy_pairs(spec)
            for fit in fits:
                runner.save(exp / f'artifacts/fits/world_{fit["world_id"]}_{fit["arm"]}_start{fit["start"]}.json', fit)
            lock = runner.lock_fits(spec, exp=exp)
            def check_lock():
                with mock.patch.object(runner, 'EXP', exp), \
                     mock.patch.object(runner, 'verify_registration'), \
                     mock.patch.object(sys, 'argv', ['run.py', '--check']), \
                     mock.patch('builtins.print'):
                    return runner.main()
            self.assertEqual(check_lock(), 0)
            modified = deepcopy(lock)
            del modified['sha256'][modified['selected'][0]]
            runner.save(exp / 'artifacts/FIT_LOCK.json', modified)
            with self.assertRaisesRegex(ValueError, 'fit lock inventory'):
                check_lock()
            modified = deepcopy(lock)
            modified['paired_initializations_identical'] = False
            runner.save(exp / 'artifacts/FIT_LOCK.json', modified)
            with self.assertRaisesRegex(ValueError, 'fit lock inventory'):
                check_lock()
            # Merely updating a selected file's hash cannot authorize a worse tie choice.
            selected_path = lock['selected'][0]
            first = runner.read_json(exp / selected_path)
            nonwinner = deepcopy(first)
            nonwinner['start'] = 1
            nonwinner['initialization_attempts'] = 2
            nonwinner['search_seed'] += 1
            nonwinner['initialization_seed'] += 1
            runner.save(exp / selected_path, nonwinner)
            modified = deepcopy(lock)
            modified['sha256'][selected_path] = runner.sha(exp / selected_path)
            runner.save(exp / 'artifacts/FIT_LOCK.json', modified)
            with self.assertRaisesRegex(ValueError, 'discovery winner mismatch'):
                check_lock()
            runner.save(exp / selected_path, first)
            runner.save(exp / 'artifacts/FIT_LOCK.json', lock)
            restart_path = exp / lock['restarts'][0]
            restart_path.write_bytes(restart_path.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'fit lock bytes'):
                check_lock()

    def test_evaluator_checks_all_fits_and_strict_initializations_before_confirmation(self):
        runner, prepare, evaluator = module('run'), module('prepare'), module('evaluate')
        validator = module('validate')
        spec = {'world_ids': [17, 29, 41], 'arms': ['RELAXED', 'STRICT'],
                'starts': list(range(8)),
                'optimizer': {'annealing_steps': 60000, 'polish_sweeps': 4,
                              'initialization_cap': 1000}}
        candidates = {'suffix_pool': ['am', 'as', 'em', 'es'],
                      'wholeword_pool': ['ab', 'ac', 'an', 'at', 'de', 'ex', 'ne', 'si']}
        with tempfile.TemporaryDirectory() as tmp:
            exp = Path(tmp)
            runner.save(exp / 'src/SPEC.json', spec)
            runner.save(exp / 'prepared/CAPACITY.json', {'status': 'SOURCE_CAPACITY_PASS'})
            runner.save(exp / 'prepared/candidates.json', candidates)
            (exp / 'invented-upstream.txt').write_text('Invented upstream binding\n')
            runner.save(exp / 'src/PREREG_LOCK.json', {
                'sha256': {'src/SPEC.json': runner.sha(exp / 'src/SPEC.json')},
                'upstream_sha256': {'invented-upstream.txt': runner.sha(exp / 'invented-upstream.txt')}})
            for world in spec['world_ids']:
                prepare.write_json(exp / f'prepared/world_{world}_discovery.json.gz', {
                    'world_id': world, 'split': 'discovery', 'unit_type': 'source_sentence',
                    'paragraphs': [{'paragraph_id': 'invented',
                                    'words': [['X00', 'X04'], ['X30']]}]})
            fits = toy_pairs(spec)
            for fit in fits:
                fit.update(schema='GDT837_FIT_V1', proposals=60000, priority_rejections=0,
                           input_hashes={'spec_sha256': runner.sha(exp / 'src/SPEC.json'),
                           'cipher_sha256': runner.sha(exp / f'prepared/world_{fit["world_id"]}_discovery.json.gz')})
                runner.save(exp / f'artifacts/fits/world_{fit["world_id"]}_{fit["arm"]}_start{fit["start"]}.json', fit)
            lock = runner.lock_fits(spec, exp=exp)
            original = {relative: (exp / relative).read_bytes() for relative in lock['sha256']}
            def reject_before_confirmation(expected_error, independent_error):
                with mock.patch.object(evaluator, 'ROOT', exp), \
                     mock.patch.object(evaluator, 'load_confirmation', side_effect=AssertionError('Forbidden confirmation access')) as confirmation, \
                     mock.patch.object(evaluator, 'reference_module', side_effect=AssertionError('Forbidden model evaluation')):
                    with self.assertRaisesRegex((ValueError, FileNotFoundError), expected_error):
                        evaluator.evaluate(exp, exp / 'never-built-model')
                    confirmation.assert_not_called()
                with mock.patch.object(validator, 'ROOT', exp), \
                     mock.patch.object(sys, 'argv', ['validate.py', '--data-dir', str(exp)]), \
                     mock.patch.object(validator, 'confirmation_bindings', side_effect=AssertionError('Forbidden independent confirmation access')) as confirmation, \
                     mock.patch.object(validator, 'source_audit', side_effect=AssertionError('Forbidden independent source evaluation')):
                    with self.assertRaisesRegex((ValueError, FileNotFoundError), independent_error):
                        validator.main()
                    confirmation.assert_not_called()
            # A complete valid invented panel reaches the boundary exactly once.
            with mock.patch.object(evaluator, 'ROOT', exp), \
                 mock.patch.object(evaluator, 'load_confirmation', side_effect=RuntimeError('CONFIRMATION_BOUNDARY')) as confirmation:
                with self.assertRaisesRegex(RuntimeError, 'CONFIRMATION_BOUNDARY'):
                    evaluator.evaluate(exp, exp / 'never-built-model')
                confirmation.assert_called_once()
            with mock.patch.object(validator, 'ROOT', exp), \
                 mock.patch.object(sys, 'argv', ['validate.py', '--data-dir', str(exp)]), \
                 mock.patch.object(validator, 'confirmation_bindings', side_effect=RuntimeError('INDEPENDENT_CONFIRMATION_BOUNDARY')) as confirmation:
                with self.assertRaisesRegex(RuntimeError, 'INDEPENDENT_CONFIRMATION_BOUNDARY'):
                    validator.main()
                confirmation.assert_called_once()
            lock_path = exp / 'artifacts/FIT_LOCK.json'
            lock_path.unlink()
            reject_before_confirmation('FIT_LOCK', 'FIT_LOCK')
            changed = deepcopy(lock)
            del changed['sha256'][changed['selected'][0]]
            runner.save(lock_path, changed)
            reject_before_confirmation('Exactly all fit hashes', 'Exact 54-file hash coverage')
            runner.save(lock_path, lock)
            (exp / lock['restarts'][-1]).write_bytes(original[lock['restarts'][-1]] + b' ')
            reject_before_confirmation('Frozen fit bytes', 'Every fit and selection immutable')
            (exp / lock['restarts'][-1]).write_bytes(original[lock['restarts'][-1]])
            runner.save(exp / 'artifacts/RUN_STOP.json', {'status': 'INITIALIZATION_STOP'})
            reject_before_confirmation('Initialization stop forbids confirmation', 'No initialization-stop override')
            (exp / 'artifacts/RUN_STOP.json').unlink()
            # Equal, individually legal initial keys are insufficient: W priority
            # must hold independently for every saved initialization in both arms.
            changed = deepcopy(lock)
            for arm in ('RELAXED', 'STRICT'):
                relative = f'artifacts/fits/world_17_{arm}_start0.json'
                fit = runner.read_json(exp / relative)
                fit['initial_key']['X01']['output'] = 'e'
                fit['initial_key']['X04']['output'] = 'b'
                runner.save(exp / relative, fit)
                changed['sha256'][relative] = runner.sha(exp / relative)
            runner.save(lock_path, changed)
            reject_before_confirmation('Every saved common initialization satisfies mandatory W', 'All 48 saved initializations satisfy W priority')

    def test_fit_job_records_initialization_stop_without_scoring_or_key_selection(self):
        runner = module('run')
        spec = {'world_ids': [17], 'arms': ['RELAXED', 'STRICT'], 'starts': [0],
                'optimizer': {'annealing_steps': 60000, 'polish_sweeps': 4}}
        with tempfile.TemporaryDirectory() as tmp:
            plan = list(runner.fit_plan(spec))[0]
            plan.update(binary='invented-binary', model='invented-model', projection='invented-projection',
                        raw=str(Path(tmp) / 'engine.tsv'), output=str(Path(tmp) / 'fit.json'),
                        input_hashes={'invented': 'value'})
            stopped = runner.subprocess.CompletedProcess([], 2, '', 'INITIALIZATION_STOP\n')
            with mock.patch.object(runner.subprocess, 'run', return_value=stopped), \
                 mock.patch.object(runner, 'parse_result', side_effect=AssertionError('Stopped fit must not parse a key')):
                self.assertEqual(runner.fit_job(plan), 'INITIALIZATION_STOP')
            output = runner.read_json(plan['output'])
            self.assertEqual(output['initialization_attempts'], 1000)
            self.assertNotIn('key', output)
            self.assertNotIn('discovery_objective', output)
            Path(plan['output']).unlink()
            failed = runner.subprocess.CompletedProcess([], 2, '', 'unexpected engine error\n')
            with mock.patch.object(runner.subprocess, 'run', return_value=failed):
                with self.assertRaisesRegex(RuntimeError, 'engine failure'):
                    runner.fit_job(plan)
            self.assertFalse(Path(plan['output']).exists())
            Path(plan['raw']).write_text('\n'.join(engine_output()) + '\n')
            completed = runner.subprocess.CompletedProcess([], 0, '', '')
            with mock.patch.object(runner.subprocess, 'run', return_value=completed) as call:
                self.assertEqual(runner.fit_job(plan), 'FIT_COMPLETE')
            self.assertEqual(call.call_args.args[0][3:9],
                             ['RELAXED', '837001700', '837501700', '0', '60000', '4'])
            self.assertEqual(runner.read_json(plan['output'])['initial_key'], toy_key())
            Path(plan['output']).unlink()
            plan['search_seed'] += 1
            with mock.patch.object(runner.subprocess, 'run', return_value=completed):
                with self.assertRaisesRegex(ValueError, 'engine seed mismatch'):
                    runner.fit_job(plan)
            self.assertFalse(Path(plan['output']).exists())

    def test_projection_preserves_sentence_resets_and_compressed_provenance(self):
        runner, prepare = module('run'), module('prepare')
        value = {'split': 'discovery', 'unit_type': 'source_sentence', 'paragraphs': [
            {'paragraph_id': 'invented-1', 'words': [['X00', 'X01'], ['X30'], ['X00', 'X01']]},
            {'paragraph_id': 'invented-2', 'words': [['X30'], ['X02']]},
            {'paragraph_id': 'invented-3', 'words': [['X02']]},
        ]}
        candidates = {'suffix_pool': ['am', 'as', 'em', 'es'],
                      'wholeword_pool': ['ab', 'ac', 'an', 'at', 'de', 'ex', 'ne', 'si']}
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'toy_discovery.json.gz'
            target = Path(tmp) / 'projection.txt'
            prepare.write_json(source, value)
            metadata = runner.projection(source, candidates, target)
            expected = ('SUFFIX 4\nam as em es\nWHOLE 8\nab ac an at de ex ne si\n'
                        'WORDS 3\n2 2 0 1\n2 1 2\n2 1 30\n'
                        'TRANSITIONS 3\n0 2 1\n2 0 1\n2 1 1\nFAMILIES 0\n')
            self.assertEqual(target.read_text(), expected)
            self.assertEqual(metadata['word_types'], 3)
            self.assertEqual(metadata['word_tokens'], 6)
            self.assertEqual(metadata['source_sentence_units'], 3)
            self.assertEqual(metadata['transition_types'], 3)
            self.assertEqual(metadata['atom_incidence_entries'], 4)
            self.assertEqual(metadata['cipher_sha256'], runner.sha(source))
            self.assertEqual(metadata['cipher_uncompressed_sha256'],
                             hashlib.sha256(prepare.canonical_json_bytes(value)).hexdigest())
            self.assertEqual(metadata['projection_sha256'], runner.sha(target))
            self.assertEqual(runner.read_json(source), value)
            original = source.read_bytes()
            source.write_bytes(original[:4] + b'\x01' + original[5:])
            changed = runner.projection(source, candidates, target)
            self.assertNotEqual(changed['cipher_sha256'], metadata['cipher_sha256'])
            for field in metadata.keys() - {'cipher_sha256'}:
                self.assertEqual(changed[field], metadata[field])

    def test_discovery_guard_precedes_read_and_payload_guard_precedes_words(self):
        runner, prepare = module('run'), module('prepare')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'projection.txt'
            held = Path(tmp) / 'toy_held.json.gz'
            with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('forbidden file read')):
                with self.assertRaisesRegex(ValueError, 'discovery filename'):
                    runner.projection(held, {}, target)
            source = Path(tmp) / 'toy_discovery.json.gz'
            for payload in ({'split': 'held', 'unit_type': 'source_sentence'},
                            {'split': 'discovery', 'unit_type': 'historical_paragraph'}):
                prepare.write_json(source, payload)
                with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, 'payload'):
                    runner.projection(source, {}, target)
                self.assertFalse(target.exists())
            for words in ([[]], [['L00']], [['X38']]):
                prepare.write_json(source, {'split': 'discovery', 'unit_type': 'source_sentence',
                                            'paragraphs': [{'paragraph_id': 'invented', 'words': words}]})
                with self.subTest(words=words), self.assertRaises(ValueError):
                    runner.projection(source, {}, target)

    def test_engine_result_parser_preserves_initial_key_and_numeric_metadata(self):
        runner = module('run')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'invented.tsv'
            path.write_text('\n'.join(engine_output()) + '\n')
            parsed = runner.parse_result(path)
            self.assertEqual(parsed['initial_key'], toy_key())
            self.assertNotEqual(parsed['key'], parsed['initial_key'])
            self.assertEqual(parsed['discovery_objective'],
                             {'total_nats': -12.5, 'language_nats': -12.5, 'family_nats': 0.0})
            self.assertEqual({k: parsed[k] for k in ('proposals', 'initialization_attempts',
                             'initialization_seed', 'search_seed', 'priority_rejections')},
                             {'proposals': 60000, 'initialization_attempts': 3,
                              'initialization_seed': 837501700, 'search_seed': 837001700,
                              'priority_rejections': 12})
            malformed = [engine_output()[1:], engine_output()[:6] + engine_output()[7:],
                         engine_output()[:-1], engine_output() + [engine_output()[6]],
                         engine_output() + [engine_output()[-1]],
                         engine_output() + ['PROPOSALS\t5'],
                         engine_output() + [engine_output()[0]],
                         engine_output() + ['INITIAL\t38\tL\ta']]
            malformed.extend([[score] + engine_output()[1:] for score in
                              ('SCORE\t-12.5', 'SCORE\tnan\tnan\t0',
                               'SCORE\tinf\tinf\t0', 'SCORE\t1e999\t0\t0',
                               'SCORE\t-12.5\t-12.5\t0\textra')])
            for index, lines in enumerate(malformed):
                path.write_text('\n'.join(lines) + '\n')
                with self.subTest(case=index), self.assertRaises(ValueError):
                    runner.parse_result(path)

    def test_fit_plan_pairs_full_panel_and_fixed_budgets(self):
        runner = module('run')
        spec = {'world_ids': [17, 29, 41], 'arms': ['RELAXED', 'STRICT'],
                'starts': list(range(8)), 'optimizer': {'annealing_steps': 60000, 'polish_sweeps': 4}}
        plans = list(runner.fit_plan(spec))
        self.assertEqual(len(plans), 48)
        identities = {(p['world_id'], p['arm'], p['start']) for p in plans}
        self.assertEqual(len(identities), 48)
        for world in spec['world_ids']:
            for start in spec['starts']:
                pair = [p for p in plans if p['world_id'] == world and p['start'] == start]
                self.assertEqual({p['arm'] for p in pair}, {'RELAXED', 'STRICT'})
                left, right = ({k: v for k, v in p.items() if k != 'arm'} for p in pair)
                self.assertEqual(left, right)
                self.assertEqual((left['steps'], left['sweeps']), (60000, 4))
                self.assertEqual(left['search_seed'], 837000000 + 100 * world + start)
                self.assertEqual(left['initialization_seed'], 837500000 + 100 * world + start)
                self.assertNotEqual(left['search_seed'], left['initialization_seed'])

    def test_paired_initialization_compares_full_keys_attempts_and_seeds(self):
        evaluator = module('evaluate')
        spec = {'world_ids': [17, 29, 41], 'starts': [0, 1, 2]}
        fits = toy_pairs(spec)
        self.assertNotEqual(fits[0]['key'], fits[1]['key'])
        self.assertEqual(evaluator.check_paired_initializations(fits, spec), 9)
        for field in ('initial_key', 'initialization_attempts',
                      'initialization_seed', 'search_seed'):
            changed = deepcopy(fits)
            if field == 'initial_key':
                # Full-inventory comparison includes values absent from any toy text.
                changed[1][field]['X24']['output'] = 'z'
                changed[1][field]['X25']['output'] = 'y'
            else:
                changed[1][field] += 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                evaluator.check_paired_initializations(changed, spec)
        for changed in (fits[:-1], fits + [deepcopy(fits[0])]):
            with self.subTest(size=len(changed)), self.assertRaises(ValueError):
                evaluator.check_paired_initializations(changed, spec)
        for attempts in (0, 1001, True):
            changed = deepcopy(fits)
            changed[0]['initialization_attempts'] = attempts
            changed[1]['initialization_attempts'] = attempts
            with self.subTest(attempts=attempts), self.assertRaises(ValueError):
                evaluator.check_paired_initializations(changed, spec)

    def test_deterministic_gzip_and_all_json_readers(self):
        prepare = module('prepare')
        evaluator = module('evaluate')
        validator = module('validate')
        value = {'split': 'discovery', 'unit_type': 'source_sentence',
                 'paragraphs': [{'paragraph_id': 'invented-é',
                                 'words': [['X00', 'X01'], ['X30']]}]}
        reverse_order = dict(reversed(list(value.items())))
        canonical = prepare.canonical_json_bytes(value)
        self.assertEqual(canonical, prepare.canonical_json_bytes(reverse_order))
        self.assertTrue(canonical.endswith(b'\n'))
        compressed = prepare.gzip_json_bytes(value)
        self.assertEqual(compressed, prepare.gzip_json_bytes(reverse_order))
        self.assertEqual(compressed[:4], b'\x1f\x8b\x08\x00')
        self.assertEqual(compressed[4:8], b'\x00' * 4)
        self.assertEqual(gzip.decompress(compressed), canonical)
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / ('toy_discovery' + suffix)
                     for suffix in ('.json', '.json.gz')]
            for path in paths:
                prepare.write_json(path, value)
                prepare.write_json(path, reverse_order, check=True)
                for reader in (prepare.read_json, evaluator.read_json, validator.obj):
                    with self.subTest(reader=reader.__module__, suffix=path.suffix):
                        self.assertEqual(reader(path), value)
            self.assertEqual(paths[0].read_bytes(), canonical)
            self.assertEqual(paths[1].read_bytes(), compressed)
            metadata = prepare.gzip_metadata(paths[1])
            self.assertEqual(metadata, {
                'compressed_sha256': hashlib.sha256(compressed).hexdigest(),
                'compressed_bytes': len(compressed),
                'uncompressed_sha256': hashlib.sha256(canonical).hexdigest(),
                'uncompressed_bytes': len(canonical),
            })
            paths[1].write_bytes(compressed[:-3])
            with self.assertRaises((EOFError, OSError, ValueError)):
                prepare.read_json(paths[1])

    def test_gzip_provenance_binds_container_bytes_and_rejects_timestamp(self):
        prepare = module('prepare')
        evaluator = module('evaluate')
        validator = module('validate')
        value = {'split': 'discovery', 'paragraphs': []}
        compressed = prepare.gzip_json_bytes(value)
        changed_header = compressed[:4] + b'\x01' + compressed[5:]
        self.assertEqual(gzip.decompress(compressed), gzip.decompress(changed_header))
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / 'one_discovery.json.gz'
            changed = Path(tmp) / 'two_discovery.json.gz'
            original.write_bytes(compressed)
            changed.write_bytes(changed_header)
            for reader in (prepare.read_json, evaluator.read_json, validator.obj):
                self.assertEqual(reader(original), reader(changed))
            for digest in (prepare.sha, evaluator.sha, validator.sha):
                self.assertEqual(digest(original), hashlib.sha256(compressed).hexdigest())
                self.assertEqual(digest(changed), hashlib.sha256(changed_header).hexdigest())
                self.assertNotEqual(digest(original), digest(changed))
            with self.assertRaisesRegex(ValueError, 'Noncanonical gzip header'):
                prepare.gzip_metadata(changed)
            with self.assertRaisesRegex(ValueError, 'Reproduction mismatch'):
                prepare.write_json(changed, value, check=True)

    def test_source_metadata_selects_before_decoding_excluded_payload(self):
        validator = module('validate')
        excluded = (b'# text = \xff deliberately undecodable\n'
                    b'# reference = ittb-forma-s1\n'
                    b'not a valid token row\xff\n\n')
        admitted = (b'# text = Rosa est.\n'
                    b'# reference = ittb-scg-s1\n'
                    b'# sent_id = invented-source-unit\n'
                    b'1\tRosa\trosa\tNOUN\t_\t_\t0\troot\t_\t_\n'
                    b'2\test\tsum\tAUX\t_\t_\t1\tcop\t_\t_\n'
                    b'3\t.\t.\tPUNCT\t_\t_\t1\tpunct\t_\t_\n\n')
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'invented.conllu'
            source.write_bytes(excluded + admitted + excluded)
            rows = list(validator.scg_sentences(source))
        self.assertEqual(len(rows), 1)
        number, comments, tokens = rows[0]
        self.assertEqual(number, 1)
        self.assertEqual(comments['text'], 'Rosa est.')
        self.assertEqual([r[1] for r in tokens], ['Rosa', 'est', '.'])

    def test_wholeword_priority_counts_occurrences_and_absent_owners(self):
        evaluator = module('evaluate')
        key = toy_key()
        cipher = {'paragraphs': [
            {'words': [['X00', 'X01'], ['X30'], ['X00', 'X01'], ['X02']]},
            {'words': [['X00', 'X01']]},
        ]}
        audit = evaluator.priority_audit(cipher, key)
        self.assertEqual(audit, {'words': 5, 'word_types': 3,
                                'violating_words': 3, 'violating_types': 1,
                                'passes_W_precedence': False})
        # The W owner need not appear anywhere for its mandatory priority to apply.
        cipher['paragraphs'][0]['words'].remove(['X30'])
        audit = evaluator.priority_audit(cipher, key)
        self.assertEqual((audit['words'], audit['violating_words'],
                          audit['violating_types']), (4, 3, 1))
        key['X30']['output'] = 'ae'
        self.assertTrue(evaluator.priority_audit(cipher, key)['passes_W_precedence'])
        key['X31']['output'] = 'ae'
        with self.assertRaisesRegex(ValueError, 'Wholeword injection'):
            evaluator.priority_audit(cipher, key)

    def test_decision_separates_recovery_from_gain_and_checks_every_key(self):
        evaluator = module('evaluate')
        spec = {'world_ids': [17, 29, 41], 'overall_recovery': {
            'minimum_word_accuracy_each_key': .95,
            'minimum_character_accuracy_each_key': .99,
            'minimum_novel_form_accuracy_each_key': .90,
            'minimum_novel_lemma_accuracy_each_key': .90}, 'constraint_gain': {
                'minimum_mean_held_word_gain': .01,
                'minimum_each_key_held_word_gain': .0}}
        def panel():
            return [{'world_id': world, 'arm': arm, 'recovery': {
                'all': {'word_accuracy': 1.0, 'character_accuracy': 1.0},
                'novel_forms': {'word_accuracy': 1.0},
                'novel_lemmas': {'word_accuracy': 1.0}},
                'all_identifiable_role_outputs_correct': True,
                'priority': {'discovery': {'passes_W_precedence': True},
                             'held': {'passes_W_precedence': True}}}
                    for world in spec['world_ids'] for arm in ('RELAXED', 'STRICT')]
        rows = panel()
        decision = evaluator.decide(rows, spec)
        self.assertEqual(decision['status'], 'FRESH_RECOVERY_PASS_NO_DEMONSTRATED_CONSTRAINT_GAIN')
        self.assertTrue(decision['relaxed_recovery_pass'])
        # RELAXED failure is compatible with STRICT recovery and a causal gain.
        for row in rows:
            if row['arm'] == 'RELAXED':
                row['recovery']['all']['word_accuracy'] = .80
                row['all_identifiable_role_outputs_correct'] = False
        decision = evaluator.decide(rows, spec)
        self.assertEqual(decision['status'], 'FRESH_RECOVERY_PASS_WITH_CONSTRAINT_GAIN')
        self.assertFalse(decision['relaxed_recovery_pass'])
        # Strong average gain cannot hide a negative gain on any key.
        rows[-1]['recovery']['all']['word_accuracy'] = .95
        rows[-2]['recovery']['all']['word_accuracy'] = 1.0
        decision = evaluator.decide(rows, spec)
        self.assertTrue(decision['strict_recovery_pass'])
        self.assertGreater(decision['mean_held_word_gain'], .01)
        self.assertFalse(decision['constraint_gain_demonstrated'])
        # Exactly the preregistered boundaries pass; no relaxed-arm priority gate.
        rows = panel()
        for row in rows:
            if row['arm'] == 'STRICT':
                row['recovery']['all'].update(word_accuracy=.95, character_accuracy=.99)
                row['recovery']['novel_forms']['word_accuracy'] = .90
                row['recovery']['novel_lemmas']['word_accuracy'] = .90
            else:
                row['priority']['held']['passes_W_precedence'] = False
        self.assertTrue(evaluator.decide(rows, spec)['strict_recovery_pass'])
        self.assertTrue(evaluator.decide(rows, spec)['relaxed_recovery_pass'])
        mutations = [('all', 'word_accuracy', .949999),
                     ('all', 'character_accuracy', .989999),
                     ('novel_forms', 'word_accuracy', .899999),
                     ('novel_lemmas', 'word_accuracy', .899999),
                     ('novel_forms', 'word_accuracy', None)]
        for subset, metric, value in mutations:
            changed = deepcopy(rows)
            changed[-1]['recovery'][subset][metric] = value
            with self.subTest(subset=subset, metric=metric, value=value):
                self.assertEqual(evaluator.decide(changed, spec)['status'], 'STRICT_RECOVERY_FAIL')
        for split in ('discovery', 'held'):
            changed = deepcopy(rows)
            changed[-1]['priority'][split]['passes_W_precedence'] = False
            with self.subTest(split=split):
                self.assertEqual(evaluator.decide(changed, spec)['status'], 'STRICT_RECOVERY_FAIL')
        changed = deepcopy(rows)
        changed[-1]['all_identifiable_role_outputs_correct'] = False
        self.assertEqual(evaluator.decide(changed, spec)['status'], 'STRICT_RECOVERY_FAIL')
        for changed in (rows[:-1], rows + [deepcopy(rows[0])]):
            with self.assertRaisesRegex(ValueError, 'Complete selected evaluation panel'):
                evaluator.decide(changed, spec)

    def test_word_metric_preserves_literal_uv_and_word_boundaries(self):
        evaluator = module('evaluate')
        # Counts are calculated by hand, including a deletion and a substitution.
        result = evaluator.word_metrics([('uva', 'uva'), ('uva', 'vva'), ('est', 'es')])
        self.assertEqual(result['exact_words'], 1)
        self.assertEqual(result['edit_distance'], 2)
        self.assertEqual(result['character_denominator'], 9)
        self.assertEqual(result['word_accuracy'], 1 / 3)
        self.assertEqual(result['character_accuracy'], 1 - 2 / 9)
        self.assertEqual(result['fully_correct_truth_types'], 0)
        self.assertIsNone(evaluator.word_metrics([])['word_accuracy'])

    def test_common_identifiability_ignores_hidden_roles_and_unused_values(self):
        evaluator, validator = module('evaluate'), module('validate')
        candidates = {'suffix_pool': ['a', 'am', 'as', 'em'],
                      'wholeword_pool': ['ab', 'ac', 'an', 'at', 'de', 'ex', 'ne', 'si']}
        key = toy_key()
        key['X03'] = {'role': 'S', 'output': 'a'}
        key['X26'] = {'role': 'L', 'output': 'd'}
        cipher = {'paragraphs': [{'words': [['X01', 'X02', 'X04', 'X03']]}]}
        def verify(expected_options):
            result = evaluator.identifiability(cipher, key, candidates)
            independent = validator.active_role_equivalence(cipher, key, candidates)
            self.assertEqual(independent, {name: result[name] for name in independent})
            self.assertEqual(result['role_options']['X03'], expected_options)
            changed = deepcopy(key)
            # Every supplied true role may change; only observed emissions are evidence.
            for row in changed.values():
                row['role'] = 'W'
            for code in result['inactive_ids']:
                changed[code]['output'] = 'unobserved-value-must-not-constrain-role-options'
            self.assertEqual(evaluator.identifiability(cipher, changed, candidates), result)
        verify(['L', 'S'])
        # A distinct observed atom already owns literal "a", excluding L by injection.
        cipher['paragraphs'][0]['words'].append(['X00'])
        verify(['S'])


def main():
    parser = argparse.ArgumentParser(add_help=False)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write-report', action='store_true')
    mode.add_argument('--check-report', action='store_true')
    options, arguments = parser.parse_known_args()
    program = unittest.main(argv=[sys.argv[0], *arguments], exit=False)
    result = program.result
    if options.write_report or options.check_report:
        report = {
            'schema': 'GDT837_INVENTED_PIPELINE_TESTS_V1',
            'status': 'INVENTED_PIPELINE_TESTS_PASS' if result.wasSuccessful() else 'INVENTED_PIPELINE_TESTS_FAIL',
            'tests_run': result.testsRun,
            'failed_test_ids': [test.id() for test, _ in result.failures],
            'error_test_ids': [test.id() for test, _ in result.errors],
            'skipped_test_ids': [test.id() for test, _ in result.skipped],
            'test_names': unittest.defaultTestLoader.getTestCaseNames(PipelineTests),
            'data_scope': 'Invented fixtures only; no real source, control ciphertext, held text, or confirmation truth read',
            'engine_scope': 'The unchanged GDT836 engine has a separate nine-fixture suite; this wrapper suite executes no real initializer or decoder',
            'source_sha256': {f'src/{name}.py': hashlib.sha256((SRC / f'{name}.py').read_bytes()).hexdigest()
                              for name in ('test_pipeline', 'prepare', 'run', 'evaluate', 'validate')},
        }
        path = SRC.parent / 'artifacts/TESTS.json'
        raw = (json.dumps(report, indent=2, sort_keys=True) + '\n').encode()
        if options.check_report:
            if path.read_bytes() != raw:
                raise ValueError('Invented-test report replay mismatch')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())

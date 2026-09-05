#!/usr/bin/env python3
"""Independent guarded-source and literal-display validation; never validates meanings."""
import argparse
import copy
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
READERS = ['zl3b_clean', 'it2a_clean', 'rf1b_clean']
META = ['page', 'locus', 'line_number', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean']
DISPLAY = ['page', 'locus', 'kind', 'reader', 'model', 'source_text', 'tokens',
           'hypothesis_positions_1based', 'literal_hypotheses_json', 'confidence']
SCOPE = ('f1r f4r f10r f11r f13r f17r f18r f20v f24v f31r f55v f56r f66r '
         'f67r2 f68r1 f69v f70v1 f70v2 f71v f72r1 f72r2 f72r3 f75r f76r '
         'f77r f81r f81v f82r f83r f88r f88v f89r1 f89r2 f95v1 f95v2 '
         'f21r f32v f100v f101r').split()
TARGETS = ['otchol', 'cthar', 'okaiin']
SHARED = {'otchol': 'dieses?', 'cthar': 'Wurzel?', 'chol': 'trocken?', 'dan': 'sehr wenig?',
          'dain': 'wenig?', 'daiin': 'viel?', 'daiiin': 'sehr viel?'}
MODELS = {'N': {'okaiin': 'Pulver?'}, 'G': {'okaiin': 'ist?'}}
TIMING = 'EXPLORATORY_MODELS_BEFORE_AGENT_TRANSFER_REVIEW__ASSEMBLY_AFTER_CONTEXT_INSPECTION'


def require(test, message):
    if not test:
        raise ValueError(message)


def equal(actual, expected, message):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def query(path, columns, artifact=False):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in SCOPE:
        command.extend(['--allow', page])
    command.extend(['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r'])
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    stats = [json.loads(s[12:]) for s in proc.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    require(len(stats) == 1, 'Missing or duplicate guard statistics')
    if artifact:
        require(stats[0]['skipped_forbidden'] == stats[0]['skipped_not_allowed'] == 0,
                'Artifact contains a sealed or out-of-scope row')
    table = csv.DictReader(io.StringIO(proc.stdout), delimiter='\t')
    equal(table.fieldnames, columns, 'Unexpected projection schema')
    rows = list(table)
    require(len(rows) == stats[0]['selected'], 'Projection count mismatch')
    require(all(set(r) == set(columns) and all(isinstance(v, str) for v in r.values()) for r in rows),
            'Malformed projected row')
    if not artifact:
        require({r['page'] for r in rows} == set(SCOPE), 'Incomplete 39-selector source coverage')
        require(len({r['locus'] for r in rows}) == len(rows), 'Duplicate source locus')
    return rows, {'command': command, 'stats': stats[0], 'projection_sha256': sha(proc.stdout.encode())}


def sources(spec):
    expected_spec = {'design_timing': TIMING, 'target_wholes': TARGETS, 'complete_page': 'f17r',
                     'source_selectors': SCOPE, 'sealed_data': ['f84', 'f84r'],
                     'shared_hypotheses': SHARED, 'models': MODELS, 'confidence': 'C0_UNCONFIRMED',
                     'unknown_policy': 'BRACKET_EACH_UNMAPPED_WHOLE',
                     'word_order': 'SOURCE_ORDER_NO_INSERTED_CONNECTIVES',
                     'new_admissions': 0, 'new_semantic_promotions': 0}
    equal(spec, expected_spec, 'Fixed scope, models, order policy, or C0 ceiling changed')
    equal(list(spec['models']), ['N', 'G'], 'Model display order changed')
    paths = ['experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv',
             'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv']
    admissions = []
    for path in paths:  # Admission metadata, not manuscript payload.
        with (ROOT / path).open() as handle:
            admissions.append(list(csv.DictReader(handle, delimiter='\t')))
    old, extra = admissions
    equal([r['source_selector'] for r in old], SCOPE[:35], 'Original selectors differ')
    equal([r['source_selector'] for r in extra], SCOPE[35:], 'Four extra selectors differ')
    require(len({r['physical_page'] for r in old}) == 30 and
            len({r['physical_page'] for r in old + extra}) == 34, 'Physical-page scope differs')
    require(all(r['decision'] == 'ADMITTED' for r in extra), 'Unadmitted extra selector')
    primary, first = query('transcription/voynich_zl3b_lines.tsv', META)
    alternate, second = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *READERS])
    cross = {r['locus']: r for r in alternate}
    require(set(cross) == {r['locus'] for r in primary}, 'Alternate source coverage differs')
    joined = []
    for row in primary:
        other = cross[row['locus']]
        require(other['page'] == row['page'] and other['zl3b_clean'] == row['eva_clean'], 'Source join differs')
        joined.append(dict(row, **{r: other[r] for r in READERS}))
    return joined, [first, second]


def validate(contexts, trials, result, source, guards, spec_hash):
    selected = []
    for row in source:
        hits = set().union(*(set(row[r].split()) for r in READERS)) & set(TARGETS)
        if row['page'] == 'f17r' or hits:
            selected.append(row)
    equal(contexts, selected, 'Context selection, source fields, repetitions, or alternate readings differ')
    f17 = [row['locus'] for row in selected if row['page'] == 'f17r']
    equal(f17, ['f17r.' + str(i) for i in range(1, 14)], 'Incomplete f17r page')
    require(len(selected) == 54 and len(trials) == 324, 'Expected 54 contexts / 324 displays')
    index = 0
    for row in selected:
        for reader in READERS:
            words = row[reader].split()
            for model in ('N', 'G'):
                mapping = dict(SHARED, **MODELS[model])
                expected = {'page': row['page'], 'locus': row['locus'], 'kind': row['kind'],
                            'reader': reader, 'model': model, 'source_text': row[reader],
                            'tokens': str(len(words)), 'confidence': 'C0_UNCONFIRMED',
                            'hypothesis_positions_1based': ','.join(str(i) for i, w in enumerate(words, 1)
                                                                  if w in mapping),
                            'literal_hypotheses_json': [mapping[w] if w in mapping else '[' + w + ']'
                                                        for w in words]}
                actual = dict(trials[index])
                actual['literal_hypotheses_json'] = json.loads(actual['literal_hypotheses_json'])
                equal(actual, expected, 'Tokenwise literal display/order differs at ' + row['locus'] + '/' + reader + '/' + model)
                index += 1
    local = [{k: row[k] for k in ['page', 'locus', 'kind', *READERS]} for row in selected
             if row['kind'] != 'P' and any('okaiin' in row[r].split() for r in READERS)]
    expected_result = {
        'experiment_id': 'GDT813', 'status': 'CONTEXT_AND_LITERAL_DISPLAY_ONLY', 'design_timing': TIMING,
        'source_selectors': SCOPE, 'visual_page_keys': 34, 'source_loci': len(source),
        'context_loci': len(selected), 'display_rows': index, 'complete_f17r_loci': f17,
        'counts_by_alternate_reading': {r: {w: sum(row[r].split().count(w) for row in source)
                                          for w in TARGETS} for r in READERS},
        'non_P_okaiin_contexts': local, 'guarded_queries': guards, 'spec_sha256': spec_hash,
        'new_admissions': 0, 'meanings_validated': False, 'dictionary_changed': False,
        'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0,
        'selection_limit': 'Full f17r plus whole matching loci elsewhere; not full external paragraphs.',
        'alternate_readings_not_independent_witnesses': True, 'sealed_data': ['f84', 'f84r']}
    equal(result, expected_result, 'Result counts, non-prose contexts, provenance, or semantic ceiling differ')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare validation result without writing')
    args = parser.parse_args()
    spec_raw = (EXP / 'src/SPEC.json').read_bytes()
    source, guards = sources(json.loads(spec_raw))
    relative = str(EXP.relative_to(ROOT)) + '/artifacts/'
    contexts, context_guard = query(relative + 'CONTEXTS.tsv', META + READERS, artifact=True)
    trials, trial_guard = query(relative + 'LITERAL_TRIALS.tsv', DISPLAY, artifact=True)
    result = json.loads((EXP / 'artifacts/RESULT.json').read_bytes())
    validate(contexts, trials, result, source, guards, sha(spec_raw))
    rejected = []
    for mutation in ('missing_standalone_label', 'missing_rf_variant', 'inserted_copula_in_N'):
        changed_contexts, changed_trials = copy.deepcopy(contexts), copy.deepcopy(trials)
        if mutation == 'missing_standalone_label':
            require(any(r['locus'] == 'f88v.14' for r in changed_contexts), 'Label fixture absent')
            changed_contexts = [r for r in changed_contexts if r['locus'] != 'f88v.14']
        elif mutation == 'missing_rf_variant':
            changed_trials = [r for r in changed_trials if not (r['locus'] == 'f17r.7' and r['reader'] == 'rf1b_clean')]
            require(len(changed_trials) == len(trials) - 2, 'RF fixture absent')
        else:
            row = next(r for r in changed_trials if r['locus'] == 'f17r.11' and r['model'] == 'N')
            values = json.loads(row['literal_hypotheses_json'])
            values.insert(3, 'ist?')
            row['literal_hypotheses_json'] = json.dumps(values, ensure_ascii=False)
        try:
            validate(changed_contexts, changed_trials, result, source, guards, sha(spec_raw))
        except ValueError:
            rejected.append(mutation)
        else:
            raise ValueError('Negative mutation accepted: ' + mutation)
    names = ['CONTEXTS.tsv', 'LITERAL_TRIALS.tsv', 'RESULT.json']
    report = {'status': 'PASS_INDEPENDENT_SOURCE_AND_LITERAL_DISPLAY_ONLY', 'experiment_id': 'GDT813',
              'runner_imported_or_called': False, 'source_selectors': SCOPE, 'source_loci': len(source),
              'context_loci': len(contexts), 'display_rows': len(trials), 'complete_f17r_loci': 13,
              'guarded_source_queries': guards, 'guarded_artifact_queries': [context_guard, trial_guard],
              'all_reader_fields_including_empty_preserved': True, 'fixed_models_checked': ['N', 'G'],
              'tokenwise_json_lists_and_order_checked': True, 'confidence': 'C0_UNCONFIRMED',
              'negative_mutations_in_memory_only_rejected': rejected, 'spec_sha256': sha(spec_raw),
              'artifact_sha256': {n: sha((EXP / 'artifacts' / n).read_bytes()) for n in names},
              'validator_sha256': sha(Path(__file__).read_bytes()), 'new_admissions': 0,
              'meanings_validated': False, 'dictionary_changed': False,
              'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0,
              'images_inspected_by_validator': 0, 'design_chronology_independently_validated': False}
    payload = json.dumps(report, indent=2, sort_keys=True) + '\n'
    target = EXP / 'artifacts/VALIDATION.json'
    if args.check:
        require(target.read_text() == payload, 'Saved validation result differs')
    else:
        target.write_text(payload)
    print(json.dumps({k: report[k] for k in ('status', 'context_loci', 'display_rows',
          'negative_mutations_in_memory_only_rejected')}, sort_keys=True))


if __name__ == '__main__':
    main()

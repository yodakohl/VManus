#!/usr/bin/env python3
"""Independently validate family-context sources, not meanings; --check writes nothing."""
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
READINGS = ('zl3b_clean', 'it2a_clean', 'rf1b_clean')
FORMS = ('dan', 'dain', 'daiin', 'daiiin')
SCOPE = ('f1r f4r f10r f11r f13r f17r f18r f20v f24v f31r f55v f56r '
         'f66r f67r2 f68r1 f69v f70v1 f70v2 f71v f72r1 f72r2 f72r3 '
         'f75r f76r f77r f81r f81v f82r f83r f88r f88v f89r1 f89r2 '
         'f95v1 f95v2 f21r f32v f100v f101r').split()
OLD_SCOPE = 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv'
FIELDS = ['page', 'locus', 'line_number', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def equal(actual, expected, message):
    require(encoded(actual) == encoded(expected), message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def projection(path, columns):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for selector in SCOPE:
        command.extend(['--allow', selector])
    command.extend(['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r'])
    proc = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    stats = [json.loads(line.removeprefix('GUARD_STATS ')) for line in proc.stderr.splitlines()
             if line.startswith('GUARD_STATS ')]
    require(len(stats) == 1, 'Missing or duplicate guard statistics')
    table = csv.DictReader(io.StringIO(proc.stdout), delimiter='\t')
    equal(table.fieldnames, columns, 'Guard returned unexpected fields')
    rows = list(table)
    require(len(rows) == stats[0]['selected'], 'Guard row count mismatch')
    require({r['page'] for r in rows} == set(SCOPE), 'Guard selector coverage mismatch')
    require(len({r['locus'] for r in rows}) == len(rows), 'Duplicate projected locus')
    require(all(set(r) == set(columns) and all(isinstance(v, str) for v in r.values())
                for r in rows), 'Malformed source row')
    return rows, {'command': command, 'stats': stats[0], 'projection_sha256': sha(proc.stdout.encode())}


def source_expectations():
    # Admission metadata contain no mixed manuscript payload.
    with (ROOT / OLD_SCOPE).open() as handle:
        old = list(csv.DictReader(handle, delimiter='\t'))
    with (EXP / 'src/PAGE_ADMISSIONS.tsv').open() as handle:
        extra = list(csv.DictReader(handle, delimiter='\t'))
    equal([r['source_selector'] for r in old], SCOPE[:35], 'Original 35-selector scope changed')
    equal([r['source_selector'] for r in extra], SCOPE[35:], 'Four extra selectors changed')
    require(len({r['physical_page'] for r in old}) == 30, 'Original physical-page count')
    require(len({r['physical_page'] for r in old + extra}) == 34, 'Combined physical-page count')
    require(all(r['decision'] == 'ADMITTED' for r in extra), 'Unadmitted extra selector')
    require(len(set(SCOPE)) == 39 and not any(s.startswith('f84') for s in SCOPE), 'Scope or seals')
    lines, primary_guard = projection('transcription/voynich_zl3b_lines.tsv', FIELDS)
    variants, alternate_guard = projection('transcription/voynich_cross_transcription_lines.tsv',
                                           ['page', 'locus', *READINGS])
    alternatives = {r['locus']: r for r in variants}
    require(set(alternatives) == {r['locus'] for r in lines}, 'Alternate locus coverage differs')
    for row in lines:
        alt = alternatives[row['locus']]
        require(alt['page'] == row['page'] and alt['zl3b_clean'] == row['eva_clean'], 'Source join differs')
        require(row['paragraph_start'] in ('0', '1') and row['paragraph_end'] in ('0', '1'), 'Paragraph flags')
        row.update({reader: alt[reader] for reader in READINGS})

    # Independent partition: adjacent source rows connect only within one P block.
    # No builder import, call, generated block ID, or mutable paragraph accumulator.
    cuts = [0]
    for index in range(1, len(lines)):
        left, right = lines[index - 1:index + 1]
        if left['page'] == right['page']:
            require(int(left['line_number']) < int(right['line_number']), 'Non-increasing source order')
        connected = (left['page'] == right['page'] and left['kind'] == right['kind'] == 'P'
                     and left['paragraph_end'] == '0' and right['paragraph_start'] == '0')
        if not connected:
            cuts.append(index)
    cuts.append(len(lines))
    selected, events = [], []
    for start, stop in zip(cuts, cuts[1:]):
        group = lines[start:stop]
        hits = []
        for reader in READINGS:
            previous = None
            for row in group:
                for position, token in enumerate(row[reader].split(), start=1):
                    if token in FORMS:
                        reasons = []
                        if token in {'dan', 'daiiin'}:
                            reasons.append('RARE_ENDPOINT')
                        if previous is not None and previous[2] in FORMS:
                            reasons.append('ADJACENT_FAMILY')
                        if previous is None and group[0]['kind'] == 'P' and group[0]['paragraph_start'] == '1':
                            reasons.append('PROSE_PARAGRAPH_INITIAL')
                        if reasons:
                            hits.append({'reader': reader, 'locus': row['locus'], 'position_1based': position,
                                         'token': token, 'previous': previous, 'reasons': reasons})
                    previous = [row['locus'], position, token]
        if hits:
            if group[0]['kind'] == 'P':
                require(group[0]['paragraph_start'] == group[-1]['paragraph_end'] == '1',
                        'Selected prose is not bounded by explicit source paragraph flags')
            else:
                require(len(group) == 1, 'Non-prose block combines independent loci')
            selected.append({'page': group[0]['page'], 'kind': group[0]['kind'], 'lines': group, 'triggers': hits})
            events.extend(hits)
    require(len(selected) == 15 and sum(len(b['lines']) for b in selected) == 83, 'Expected 15 blocks / 83 loci')
    counts = {reader: {form: sum(row[reader].split().count(form) for row in lines)
                       for form in FORMS} for reader in READINGS}
    frames = []
    for row in lines:
        positions = {}
        for reader in READINGS:
            tokens = row[reader].split()
            positions[reader] = [i for i, pair in enumerate(zip(tokens, tokens[1:]), start=1)
                                 if pair[0] == 'chol' and pair[1] in FORMS]
        if any(positions.values()):
            frames.append({'source_line': row, 'chol_positions_1based': positions})
    require(len(frames) == 11, 'Expected 11 complete within-locus chol contexts')
    contexts = {'selection_rule': 'FAMILY_PROBE_DESIGN.md', 'blocks': selected}
    result = {
        'status': 'WHOLE_FAMILY_CONTEXTS_ONLY_NO_SEMANTIC_WINNER',
        'design_timing': 'POST_RESULT_EXTENSION_BEFORE_39_SELECTOR_EXTRACTION',
        'source_selectors': SCOPE, 'visual_page_keys': 34, 'new_admissions': 0,
        'sealed_data': ['f84', 'f84r'], 'source_loci': len(lines),
        'counts_by_alternate_reading': counts, 'selected_blocks': len(selected),
        'selected_loci': sum(len(b['lines']) for b in selected), 'triggers': events,
        'guarded_queries': [primary_guard, alternate_guard],
        'alternate_readings_not_independent_witnesses': True, 'meanings_validated': False,
        'dictionary_changed': False, 'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0,
        'shared_chol_frame_followup': {
            'timing': 'POST_CONTEXT_DESCRIPTIVE_QUERY',
            'rule': 'All within-locus exact chol plus family pairs in any reading; no cross-line search.',
            'semantics': 'chol=dry is conditional, not independently confirmed',
            'complete_paragraphs_claimed': False, 'frames': frames}}
    return contexts, result


def validate(contexts, result, expected_contexts, expected_result):
    equal(contexts, expected_contexts, 'Complete source blocks, readers, positions, or triggers differ')
    equal(result, expected_result, 'Result coverage, provenance, chol frames, or semantic ceiling differ')


def negative_checks(contexts, result, expected_contexts, expected_result):
    rejected = []
    for mutation in ('lost_repetition', 'omitted_rf_variant', 'collapsed_rf_boundary',
                     'truncated_paragraph', 'omitted_zero_hit_chol_reader'):
        changed_contexts, changed_result = copy.deepcopy(contexts), copy.deepcopy(result)
        row = next(r for b in changed_contexts['blocks'] for r in b['lines'] if r['locus'] == 'f32v.8')
        if mutation == 'lost_repetition':
            for key in ('eva_clean', *READINGS):
                require('daiin daiin' in row[key], 'Negative repetition fixture absent')
                row[key] = row[key].replace('daiin daiin', 'daiin', 1)
        elif mutation == 'omitted_rf_variant':
            del row['rf1b_clean']
        elif mutation == 'collapsed_rf_boundary':
            require(row['rf1b_clean'] != row['zl3b_clean'], 'Negative RF difference fixture absent')
            row['rf1b_clean'] = row['zl3b_clean']
        elif mutation == 'truncated_paragraph':
            changed_contexts['blocks'][0]['lines'].pop()
        else:
            frame = next(f for f in changed_result['shared_chol_frame_followup']['frames']
                         if f['source_line']['locus'] == 'f18r.2')
            require(frame['chol_positions_1based']['rf1b_clean'] == [], 'Zero-hit fixture absent')
            del frame['chol_positions_1based']['rf1b_clean']
        try:
            validate(changed_contexts, changed_result, expected_contexts, expected_result)
        except ValueError:
            rejected.append(mutation)
        else:
            raise ValueError('Negative mutation unexpectedly accepted: ' + mutation)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare saved validation without writing')
    args = parser.parse_args()
    expected_contexts, expected_result = source_expectations()
    files = ['FAMILY_CONTEXTS.json', 'FAMILY_PROBE_RESULT.json']
    raw = [(EXP / 'artifacts' / name).read_bytes() for name in files]
    contexts, result = map(json.loads, raw)
    validate(contexts, result, expected_contexts, expected_result)
    rejected = negative_checks(contexts, result, expected_contexts, expected_result)
    report = {
        'status': 'PASS_INDEPENDENT_SOURCE_CHECK_ONLY', 'builder_imported_or_called': False,
        'scope_selectors': SCOPE, 'source_loci': expected_result['source_loci'],
        'guarded_queries': expected_result['guarded_queries'],
        'selected_blocks': 15, 'selected_loci': 83,
        'selected_prose_paragraphs': sum(b['kind'] == 'P' for b in contexts['blocks']),
        'selected_nonprose_loci': sum(b['kind'] != 'P' for b in contexts['blocks']),
        'trigger_events': len(expected_result['triggers']), 'shared_chol_complete_loci': 11,
        'all_reader_fields_and_zero_hit_readings_preserved': True,
        'counts_by_alternate_reading': expected_result['counts_by_alternate_reading'],
        'negative_mutations_in_memory_only_rejected': rejected,
        'source_artifact_sha256': dict(zip(files, map(sha, raw))),
        'validator_sha256': sha(Path(__file__).read_bytes()),
        'image_bodies_opened': 0, 'new_admissions': 0,
        'meanings_validated': False, 'dictionary_changed': False,
        'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0,
        'design_timing_independently_validated': False}
    payload = json.dumps(report, indent=2, sort_keys=True) + '\n'
    target = EXP / 'artifacts/FAMILY_VALIDATION.json'
    if args.check:
        require(target.read_text() == payload, 'Saved independent validation differs')
    else:
        target.write_text(payload)
    print(json.dumps({k: report[k] for k in ('status', 'selected_blocks', 'selected_loci',
          'shared_chol_complete_loci', 'negative_mutations_in_memory_only_rejected')}, sort_keys=True))


if __name__ == '__main__':
    main()

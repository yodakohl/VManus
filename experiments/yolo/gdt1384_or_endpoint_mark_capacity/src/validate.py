#!/usr/bin/env python3
"""Independent fixed-expansion audit using regex streaks, not the runner.

Reads only the six bound, previously guarded JSON caches. This program tests
source fidelity and a necessary formal capacity condition, never meanings.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

B = Path(__file__).resolve().parents[1]
ROOT = B.parents[2]
EXPANSION = {
    'or': ['OR'], 'dalor': ['DAL', 'OR'], 'orar': ['OR', 'AR'],
    'oraiin': ['OR', 'AIIN'], 'orain': ['OR', 'AIN'],
}
READERS = {'IT2a', 'ZL3b', 'RF1b'}


class ValidationError(Exception):
    pass


class Audit:
    def __init__(self):
        self.checks = 0
        self.stages = []

    def check(self, condition, description):
        self.checks += 1
        if not condition:
            raise ValidationError(description)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def streaks(groups):
    """Encode each line independently; barriers prevent illicit joins.

    One tape position corresponds to one expanded component (or a separator
    barrier). A regex maximal match directly supplies its provenance slice.
    """
    tape, pointers = [], []
    for ordinal, group in enumerate(groups):
        if ordinal:
            previous = groups[ordinal - 1]
            if not (previous['right_separator'] == 'DEFINITE_SPACE'
                    and group['left_separator'] == 'DEFINITE_SPACE'):
                tape.append('|')
                pointers.append(None)
        for component_index, component in enumerate(
                EXPANSION.get(group['ivtff_group_raw'], ['OPAQUE'])):
            tape.append('1' if component == 'OR' else '0')
            pointers.append({
                'source_group_id': group['source_group_id'],
                'component_index': component_index,
            })
    text = ''.join(tape)
    matches = [pointers[m.start():m.end()] for m in re.finditer('1+', text)]
    return text.count('1'), matches


def fixture_groups(words, seams):
    if len(seams) != max(0, len(words) - 1):
        raise ValidationError('Control seam count does not match words')
    return [{
        'source_group_id': f'control|G{i + 1:03d}',
        'ivtff_group_raw': word,
        'left_separator': 'LINE_START' if i == 0 else seams[i - 1],
        'right_separator': 'LINE_END' if i + 1 == len(words) else seams[i],
    } for i, word in enumerate(words)]


def check_controls(audit):
    fixtures = [
        ('paired_endpoints', ['dalor', 'orar'], ['DEFINITE_SPACE'], [2]),
        ('three_components', ['dalor', 'or', 'oraiin'],
         ['DEFINITE_SPACE', 'DEFINITE_SPACE'], [3]),
        ('three_free', ['or', 'or', 'or'],
         ['DEFINITE_SPACE', 'DEFINITE_SPACE'], [3]),
        ('ar_breaks', ['orar', 'or'], ['DEFINITE_SPACE'], [1, 1]),
        ('drawing_breaks', ['or', 'or'], ['DRAWING_INTERRUPTION'], [1, 1]),
        ('uncertainty_breaks', ['or', 'or'], ['UNCERTAIN_SMALL_SPACE'], [1, 1]),
        ('dor_opaque', ['dor', 'or'], ['DEFINITE_SPACE'], [1]),
        ('oror_opaque', ['oror'], [], []),
        ('two_marked_links', ['dalor', 'orar', 'dalor', 'orar'],
         ['DEFINITE_SPACE'] * 3, [2, 2]),
        ('ain_is_not_aiin', ['orain'], [], [1]),
        ('exact_raw_only', ['OR', 'or?'], ['DEFINITE_SPACE'], []),
    ]
    own = []
    for name, words, seams, expected in fixtures:
        actual = [len(run) for run in streaks(fixture_groups(words, seams))[1]]
        audit.check(actual == expected, f'Source-free control failed: {name}')
        own.append({'name': name, 'expected_run_lengths': expected,
                    'actual_run_lengths': actual})
    # Catch using just one side of an inter-group seam.
    for side in ['left_separator', 'right_separator']:
        groups = fixture_groups(['or', 'or'], ['DEFINITE_SPACE'])
        groups[1 if side == 'left_separator' else 0][side] = 'UNCERTAIN_SMALL_SPACE'
        actual = [len(run) for run in streaks(groups)[1]]
        audit.check(actual == [1, 1], f'Both-seam requirement: {side}')
        own.append({'name': 'one_sided_' + side,
                    'expected_run_lengths': [1, 1], 'actual_run_lengths': actual})
    # No line state is carried into a second invocation.
    a = streaks(fixture_groups(['dalor'], []))[1]
    b = streaks(fixture_groups(['oraiin'], []))[1]
    audit.check([len(x) for x in a + b] == [1, 1], 'Physical line reset')

    controls = read(B / 'artifacts/CONTROLS.json')
    audit.check(controls['experiment_id'] == 'GDT1384', 'Controls experiment ID')
    signatures = set()
    names = set()
    for case in controls['cases']:
        name = case['name']
        audit.check(name not in names, 'Unique named runner controls')
        names.add(name)
        words, seams = case['raw_groups'], case['seams']
        actual = [len(run) for run in streaks(fixture_groups(words, seams))[1]]
        audit.check(actual == case['expected_run_lengths'], f'Control truth: {name}')
        audit.check(actual == case['actual_run_lengths'], f'Control reported actual: {name}')
        audit.check(case['pass'] is True, f'Control reported pass: {name}')
        signatures.add((tuple(words), tuple(seams), tuple(actual)))
    for name, words, seams, expected in fixtures[:9]:
        # The additional explicit-AR example may use a different equivalent
        # sequence; independently check ours without dictating its spelling.
        if name == 'two_marked_links':
            continue
        audit.check((tuple(words), tuple(seams), tuple(expected)) in signatures,
                    f'Required named control coverage: {name}')
    audit.check(controls['all_pass'] is True, 'All runner controls passed')
    audit.stages.append('Independent controls and recorded runner controls')
    return own


def reconstruct(audit, contract):
    audit.check(contract['schema_version'] == 1, 'Contract schema')
    audit.check(contract['experiment_id'] == 'GDT1384', 'Contract experiment ID')
    audit.check(contract['finite_expansion'] == EXPANSION, 'Exactly fixed P2 expansion')
    audit.check(contract['maximum_or_run'] == 2 and contract['kind'] == 'P',
                'Fixed cap and prose scope')
    audit.check(contract['sealed_data'].get('f84') == 'FORBIDDEN'
                and contract['sealed_data'].get('f84r') == 'FORBIDDEN', 'Explicit seals')
    audit.check(len(contract['inputs']) == 6, 'Six bound caches')
    frequencies = Counter(item['reader'] for item in contract['inputs'])
    audit.check(set(frequencies) == READERS and set(frequencies.values()) == {2},
                'Two caches per alternate reading')
    audit.check(len({item['path'] for item in contract['inputs']}) == 6,
                'Distinct source cache paths')
    audit.check(sha(ROOT / contract['candidate_file']) == contract['candidate_sha256'],
                'Candidate source hash')
    result = {reader: {
        'prose_lines': 0, 'raw_groups': 0, 'or_components': 0,
        'run_lengths': Counter(), 'max_run': 0,
        'violating_runs': 0, 'multiple_runs': [],
    } for reader in sorted(READERS)}
    seen_lines, seen_groups = set(), set()
    inputs = {}
    for item in contract['inputs']:
        path, reader = item['path'], item['reader']
        actual_hash = sha(ROOT / path)
        audit.check(actual_hash == item['sha256'], f'Source hash: {path}')
        inputs[path] = actual_hash
        cache = read(ROOT / path)
        columns = cache['group_columns']
        required = {'source_group_id', 'source_group_index', 'ivtff_group_raw',
                    'left_separator', 'right_separator'}
        audit.check(set(columns) == required and len(columns) == len(required),
                    f'Source group columns: {path}')
        for line in cache['lines']:
            metadata = line['metadata']
            page, locus = metadata['page'], metadata['locus']
            audit.check(not page.startswith('f84') and page not in {'f1r', 'f116v'},
                        'Forbidden source page')
            audit.check(metadata['edition'] == reader, 'Reader matches bound cache')
            if metadata['kind'] != 'P':
                continue
            audit.check((reader, locus) not in seen_lines, 'No duplicate prose line')
            seen_lines.add((reader, locus))
            groups = []
            for raw in line['groups']:
                audit.check(len(raw) == len(columns), 'Full group source fields')
                groups.append(dict(zip(columns, raw)))
            audit.check(len(groups) == int(metadata['source_group_count']),
                        'Complete original prose line')
            audit.check([int(g['source_group_index']) for g in groups]
                        == list(range(1, len(groups) + 1)), 'Consecutive original group indices')
            for group in groups:
                identity = group['source_group_id']
                audit.check(identity not in seen_groups, 'No duplicate original group')
                seen_groups.add(identity)
            tally = result[reader]
            tally['prose_lines'] += 1
            tally['raw_groups'] += len(groups)
            component_count, runs = streaks(groups)
            tally['or_components'] += component_count
            for run in runs:
                length = len(run)
                tally['run_lengths'][str(length)] += 1
                tally['max_run'] = max(tally['max_run'], length)
                tally['violating_runs'] += int(length >= 3)
                if length >= 2:
                    tally['multiple_runs'].append({
                        'page': page, 'locus': locus, 'source': path,
                        'length': length, 'components': run,
                        'raw_line': [g['ivtff_group_raw'] for g in groups],
                        'group_ids': [g['source_group_id'] for g in groups],
                        'separators': [[g['left_separator'], g['right_separator']]
                                       for g in groups],
                    })
    for tally in result.values():
        tally['run_lengths'] = dict(tally['run_lengths'])
        tally['multiple_runs'].sort(key=lambda c: (
            c['page'], c['locus'], c['components'][0]['source_group_id'],
            c['components'][0]['component_index']))
        audit.check(sum(int(k) * count for k, count in tally['run_lengths'].items())
                    == tally['or_components'], 'All OR components occur in one streak')
    audit.stages.append('Six source hashes, exact full-line intake and regex streak reconstruction')
    return result, inputs


def main():
    audit = Audit()
    out = {'experiment_id': 'GDT1384', 'status': 'FAIL',
           'qualification': 'Independent source and necessary-capacity reconstruction only; '
                            'no word meaning, endpoint ownership, or full grammar validation.',
           'method': 'Regex maximal streaks on per-line component tapes with explicit '
                     'two-sided separator barriers and parallel provenance positions.'}
    try:
        contract_path = B / 'src/CONTRACT.json'
        contract = read(contract_path)
        own_controls = check_controls(audit)
        expected, inputs = reconstruct(audit, contract)
        actual = read(B / 'artifacts/RESULT.json')
        audit.check(actual['schema_version'] == 1, 'Result schema version')
        audit.check(actual['experiment_id'] == 'GDT1384', 'Result experiment identity')
        audit.check(actual['contract_sha256'] == sha(contract_path), 'Result contract binding')
        audit.check(set(actual['by_reader']) == READERS, 'All readers reported separately')
        for reader in sorted(READERS):
            for key, value in expected[reader].items():
                audit.check(actual['by_reader'][reader].get(key) == value,
                            f'Exact result comparison: {reader}/{key}')
        status = ('CAP_VIOLATION' if any(x['violating_runs'] for x in expected.values())
                  else 'NO_CAP_VIOLATION_IN_FIXED_SAME_LINE_SCOPE')
        audit.check(actual['status'] == status, 'Exact fixed scientific decision')
        audit.stages.append('Every count, maximal streak, source witness and decision agrees')
        out.update(status='PASS', source_hashes=inputs,
                   source_free_controls=own_controls,
                   contract_sha256=sha(contract_path),
                   validator_sha256=sha(Path(__file__)),
                   necessary_capacity_status=status,
                   readers={r: {k: v for k, v in x.items() if k != 'multiple_runs'}
                            for r, x in expected.items()})
    except ValidationError as exc:
        out['failure'] = str(exc)
    except Exception as exc:
        # Do not copy absolute machine paths from filesystem exceptions into
        # a publication artifact. The exception class identifies the failure.
        out['failure'] = 'Unexpected validation error: ' + type(exc).__name__
    out['checks'] = audit.checks
    out['completed_stages'] = audit.stages
    (B / 'artifacts/VALIDATION.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': out['status'], 'checks': audit.checks,
                      'failure': out.get('failure')}, sort_keys=True))
    return 0 if out['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

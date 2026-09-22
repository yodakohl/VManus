#!/usr/bin/env python3
"""GDT1037: fixed-denotation collisions under two literal raw context bits.

--self-test never loads manuscript or lexical source files.
--execute requires a remotely verified public hash lock before reading them.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re
import subprocess
import sys


def find_repo_root(start):
    for candidate in (start, *start.parents):
        if (candidate / 'AGENTS.md').is_file() and (candidate / '.git').exists():
            return candidate
    raise RuntimeError('VManus repository root not found')


ROOT = find_repo_root(Path(__file__).resolve())
EXP = Path(__file__).resolve().parents[1]
EXP_REL = EXP.relative_to(ROOT).as_posix()
STATES = (
    ('LINE_START', True, False),
    ('PREV_DY', False, True),
    ('OTHER', False, False),
)
PANELS = ('RAW_EXACT', 'LITERAL_LINES')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, timeout=40)
    require(result.returncode == 0, 'Git registration check failed: ' + ' '.join(args[:2]))
    return result.stdout


def rooted(path):
    relative = Path(path)
    require(not relative.is_absolute() and '..' not in relative.parts, 'Non-repository path in contract')
    resolved = (ROOT / relative).resolve()
    require(resolved.is_relative_to(ROOT), 'Contract path escapes repository')
    return resolved


def verify_registration(spec):
    """Read metadata first; no source/target bytes until public lock is proven."""
    registration = spec['registration']
    lock_path = EXP / registration['lock']
    receipt = load(EXP / registration['receipt'])
    lock_bytes = lock_path.read_bytes()
    require(set(registration['receipt_fields']) <= set(receipt), 'Incomplete public receipt')
    commit = receipt['public_commit']
    require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit), 'Public commit must be full SHA1')
    require(receipt['lock_sha256'] == sha(lock_bytes), 'Public receipt/lock hash mismatch')
    require(isinstance(receipt['verified_utc'], str) and bool(receipt['verified_utc']), 'Missing publication verification time')
    public_ref = registration['public_ref']
    remote_lines = git('ls-remote', '--exit-code', registration['remote'], public_ref).decode().splitlines()
    matches = [line.split()[0] for line in remote_lines if line.split()[1:] == [public_ref]]
    require(len(matches) == 1 and re.fullmatch(r'[0-9a-f]{40}', matches[0]), 'Ambiguous public ref')
    remote_commit = matches[0]
    # No fetch or branch mutation: missing commit objects fail closed.
    git('merge-base', '--is-ancestor', commit, remote_commit)
    lock_rel = lock_path.relative_to(ROOT).as_posix()
    require(git('show', commit + ':' + lock_rel) == lock_bytes, 'Lock differs from public commit')
    lock = json.loads(lock_bytes)
    files = lock['files']
    require(isinstance(files, dict), 'Lock files must be a hash mapping')
    required = {EXP_REL + '/' + name for name in registration['required_experiment_files']}
    required.add(spec['packet']['path'])
    required.update(record['path'] for record in spec['records'])
    required.update(record['path'] for record in spec['bound_metadata'])
    require(required <= set(files), 'Public lock misses required files: ' + ', '.join(sorted(required - set(files))))
    expected = {spec['packet']['path']: spec['packet']['sha256']}
    expected.update({record['path']: record['sha256'] for record in spec['records']})
    expected.update({record['path']: record['sha256'] for record in spec['bound_metadata']})
    for path, digest in expected.items():
        require(files[path] == digest, 'SPEC/lock hash disagreement: ' + path)
    # Public registration is now proven; bound source bytes may be hashed/read.
    for path, digest in sorted(files.items()):
        require(isinstance(digest, str) and re.fullmatch(r'[0-9a-f]{64}', digest), 'Invalid lock digest')
        require(sha(rooted(path).read_bytes()) == digest, 'Current file hash mismatch: ' + path)
        require(sha(git('show', commit + ':' + path)) == digest, 'Public file hash mismatch: ' + path)
    return {'public_commit': commit,
            'lock_sha256': sha(lock_bytes), 'verified_utc': receipt['verified_utc'],
            'remote_reachability_verified': True, 'all_locked_current_and_commit_hashes_verified': True}


def triple(entry):
    return {key: entry[key] for key in ('value', 'type', 'denotation')}


def lexical_map(entries):
    output = {}
    for entry in entries:
        require(entry['form'] not in output, 'Duplicate lexical form within fixed family')
        output[entry['form']] = dict(entry)
    return output


def extract_entries(sources, spec):
    a0, a1, b0, b1 = [sources[key] for key in ('II', 'III', 'IV', 'V')]
    A = lexical_map(a0['lexicon'] + a1['new_lexicon'])
    changed = a1['explicit_new_branch_before_any_semantic_test']['changed_entry']
    require(changed['form'] == 'qoky', 'Unexpected changed-entry target')
    for field in ('value', 'type', 'denotation'):
        A['qoky'][field] = changed['new_' + field]
    B = lexical_map(b1['frozen_parent_lexicon'] + b1['new_lexicon'])
    old_B = lexical_map(b0['lexicon'])
    require(all(triple(entry) == triple(B[word]) for word, entry in old_B.items()), 'B parent entry changed')
    require(len(A) == 67 and len(B) == 59 and len(A.keys() | B.keys()) == 113, 'Whole lexicon size mismatch')
    shared = sorted(A.keys() & B.keys())
    require(shared == sorted(spec['semantic_conflict_forms']), 'Shared forms differ from fixed semantic review')
    receipt = load(rooted(spec['semantic_review']['receipt']))
    reviewed = {row['form']: row for row in receipt['rows']}
    require(set(reviewed) == set(shared), 'Incomplete semantic intersection receipt')
    for word in shared:
        require(triple(A[word]) == reviewed[word]['A'] and triple(B[word]) == reviewed[word]['B'],
                'Fixed semantic receipt differs: ' + word)
    return {'A': A, 'B': B}


def state_for(index, previous):
    first = index == 0
    prior_dy = False if first else previous.endswith('dy')
    state = 'LINE_START' if first else ('PREV_DY' if prior_dy else 'OTHER')
    return state, {'LINE_START': first, 'PREV_LITERAL_DY': prior_dy}


def annotate_paragraph(paragraph, record, entries, receipt):
    # Metadata admission before materializing any selected line's words.
    require(not paragraph['page'].startswith('f84') and paragraph['page'] != 'f116v', 'Forbidden selector')
    require(paragraph['id'] == record['paragraph'], 'Paragraph owner mismatch')
    positions = []
    for line_number, line in enumerate(paragraph['lines'], 1):
        require(not line['locus'].split('.')[0].startswith('f84') and line['locus'].split('.')[0] != 'f116v', 'Forbidden locus')
        words, ids = line['words'], line['source_ids']
        require(len(words) == len(ids), 'Word/source-ID length mismatch')
        for index, (word, source_id) in enumerate(zip(words, ids)):
            require(isinstance(word, str) and isinstance(source_id, str), 'Raw word and ID must be strings')
            previous = None if index == 0 else words[index - 1]
            state, context = state_for(index, previous)
            lexical = entries[record['family']][word]
            positions.append({'section': record['section'], 'family': record['family'],
                'paragraph': paragraph['id'], 'page': paragraph['page'], 'locus': line['locus'],
                'physical_line_index': line_number, 'index_in_line': index + 1,
                'paragraph_position': len(positions) + 1, 'source_id': source_id, 'raw': word,
                'predecessor_raw': previous, 'anchor_eligible': line.get('anchor_eligible'),
                'state': state, 'context': context, 'fixed_entry': triple(lexical)})
    require(len(positions) == paragraph['groups'] == record['groups'] == len(receipt), 'Whole paragraph length mismatch')
    for position, old in zip(positions, receipt):
        require(old['position'] == position['paragraph_position'], 'Receipt position mismatch')
        require(old.get('form', old.get('raw_form')) == position['raw'], 'Receipt raw form mismatch')
        require(old['value'] == position['fixed_entry']['value'], 'Receipt fixed value mismatch')
    return {'section': record['section'], 'family': record['family'], 'paragraph': paragraph['id'],
            'page': paragraph['page'], 'leaf': paragraph['leaf'], 'groups': paragraph['groups'],
            'positions': positions}


def panel_tables(positions, entries, reviewed_forms):
    forms = sorted(entries['A'].keys() | entries['B'].keys())
    all_cells, shared_cells, collisions, results = {}, {}, {}, {}
    reviewed = set(reviewed_forms)
    for panel in PANELS:
        observed = positions if panel == 'RAW_EXACT' else [row for row in positions if row['anchor_eligible'] is True]
        buckets = {}
        for row in observed:
            buckets.setdefault((row['raw'], row['state'], row['family']), []).append(row['source_id'])
        cells, bad = [], []
        for word, (state, start, prev_dy) in itertools.product(forms, STATES):
            aa = buckets.get((word, state, 'A'), [])
            bb = buckets.get((word, state, 'B'), [])
            conflict = word in reviewed and bool(aa) and bool(bb)
            cell = {'form': word, 'state': state, 'context': {'LINE_START': start, 'PREV_LITERAL_DY': prev_dy},
                    'A_count': len(aa), 'B_count': len(bb), 'A_source_ids': aa, 'B_source_ids': bb,
                    'semantic_pair_conflict': word in reviewed, 'collision': conflict}
            cells.append(cell)
            if conflict:
                bad.append({**cell, 'A_entry': triple(entries['A'][word]), 'B_entry': triple(entries['B'][word]),
                            'cross_family_pairs': [{'A_source_id': a, 'B_source_id': b} for a in aa for b in bb]})
        all_cells[panel] = cells
        shared_cells[panel] = [row for row in cells if row['form'] in reviewed]
        collisions[panel] = bad
        decision = ('REFUTED_FIXED_CONTEXT_JOIN' if bad else 'COMPATIBLE_FIXED_CONTEXT_TABLE') if panel == 'RAW_EXACT' else (
            'REFUTED_FIXED_CONTEXT_JOIN_ON_LITERAL_LINES' if bad else 'NO_LITERAL_CONFLICT_NOT_FULL_CODE')
        results[panel] = {'positions': len(observed), 'A_positions': sum(row['family'] == 'A' for row in observed),
            'B_positions': sum(row['family'] == 'B' for row in observed), 'fixed_form_denominator': len(forms),
            'fixed_shared_form_denominator': len(reviewed), 'context_cell_denominator': len(cells),
            'shared_context_cell_denominator': len(shared_cells[panel]), 'collision_cells': len(bad),
            'colliding_forms': sorted({row['form'] for row in bad}),
            'cross_family_collision_pairs': sum(len(row['cross_family_pairs']) for row in bad), 'decision': decision}
    return all_cells, shared_cells, collisions, results


def execute(spec, registration):
    require(spec['context']['states'] == [
        {'id': name, 'LINE_START': start, 'PREV_LITERAL_DY': prev}
        for name, start, prev in STATES], 'SPEC/program context mismatch')
    sources = {record['section']: load(rooted(record['path'])) for record in spec['records']}
    entries = extract_entries(sources, spec)
    packet = load(rooted(spec['packet']['path']))
    wanted = {record['paragraph'] for record in spec['records']}
    owned = {}
    for paragraph in packet[spec['scope']['reader']]:
        if paragraph['id'] not in wanted:
            continue
        require(not paragraph['page'].startswith('f84') and paragraph['page'] != 'f116v', 'Forbidden selected page')
        require(paragraph['id'] not in owned, 'Duplicate selected paragraph')
        owned[paragraph['id']] = paragraph
    require(set(owned) == wanted and len(owned) == 4, 'Incomplete selected scope')
    scope = [annotate_paragraph(owned[record['paragraph']], record, entries, sources[record['section']][record['receipt']])
             for record in spec['records']]
    positions = [row for paragraph in scope for row in paragraph['positions']]
    require(len(positions) == 183 and len({row['source_id'] for row in positions}) == 183, 'Position/source-ID completeness mismatch')
    for family, expected in [('A', 95), ('B', 88)]:
        require(sum(row['family'] == family for row in positions) == expected, 'Family position count mismatch')
        require({row['raw'] for row in positions if row['family'] == family} == set(entries[family]), 'Whole lexical scope mismatch')
    cells, shared, collisions, results = panel_tables(positions, entries, spec['semantic_conflict_forms'])
    return {'SCOPE.json': scope, 'ENTRIES.json': entries, 'ALL_CONTEXT_CELLS.json': cells,
        'SHARED_CONTEXT_CELLS.json': shared, 'COLLISIONS.json': collisions,
        'RESULT.json': {'experiment': 'GDT1037', 'panels': results, 'source_positions': {'A': 95, 'B': 88},
            'source_forms': {'A': 67, 'B': 59, 'union': 113, 'shared': 13}, 'states': [state[0] for state in STATES],
            'registration': registration, 'confirmed_words': 0, 'independent_meaning_capacity': 0,
            'semantic_inequality_basis': spec['semantic_review'], 'significance_claim': False}}


def self_test():
    require(state_for(0, None) == ('LINE_START', {'LINE_START': True, 'PREV_LITERAL_DY': False}), 'Start fixture')
    suffixes = {'ady': True, 'x@100;dy': True, 'xdy@100;': False, 'x[dy]': False,
                'xDY': False, 'xｄｙ': False, '@163;s': False, 'dy': True}
    for word, expected in suffixes.items():
        require(state_for(1, word)[1]['PREV_LITERAL_DY'] is expected, 'Raw suffix fixture')
    fake_entry = lambda word: {'value': word, 'type': 'synthetic', 'denotation': 'synthetic ' + word}
    words = ['ady', 'x', 'zdy', 'xdy@100;', 'u', 'x@100;dy', 'x', 'taildy']
    entries = {'A': {word: fake_entry(word) for word in set(words)}, 'B': {'x': fake_entry('B_x'), 'only_B': fake_entry('only_B')}}
    lines = [(['ady', 'x', 'zdy'], True), (['xdy@100;', 'u'], False), (['x@100;dy', 'x'], 1), (['taildy'], None)]
    paragraph = {'id': 'f1r|synthetic', 'page': 'f1r', 'leaf': 1, 'groups': len(words), 'lines': []}
    receipt, flat = [], []
    for i, (raw, anchor) in enumerate(lines, 1):
        paragraph['lines'].append({'locus': 'f1r.' + str(i), 'words': raw,
            'source_ids': ['SYN:A:' + str(i) + ':' + str(j) for j in range(len(raw))], 'anchor_eligible': anchor})
        for word in raw:
            receipt.append({'position': len(receipt) + 1, 'form': word, 'value': word})
    record = {'section': 'SYN_A', 'family': 'A', 'paragraph': paragraph['id'], 'groups': len(words)}
    scope = annotate_paragraph(paragraph, record, entries, receipt)
    rows = scope['positions']
    require(rows[0]['raw'] == 'ady' and rows[0]['state'] == 'LINE_START', 'Current dy is not previous dy')
    require(rows[1]['state'] == 'PREV_DY' and rows[2]['state'] == 'OTHER', 'Within-line predecessor fixture')
    require(rows[3]['state'] == 'LINE_START' and rows[3]['predecessor_raw'] is None, 'Physical-line reset fixture')
    require(rows[4]['raw'] == 'u' and rows[4]['state'] == 'OTHER', 'Entity suffix kept raw')
    require(rows[6]['state'] == 'PREV_DY' and rows[6]['anchor_eligible'] == 1, 'Uncertainty preserved')
    second = {**paragraph, 'id': 'f2r|synthetic', 'page': 'f2r', 'leaf': 2, 'groups': 1,
              'lines': [{'locus': 'f2r.1', 'words': ['x'], 'source_ids': ['SYN:B:1:0'], 'anchor_eligible': True}]}
    br = {'section': 'SYN_B', 'family': 'B', 'paragraph': second['id'], 'groups': 1}
    bscope = annotate_paragraph(second, br, entries, [{'position': 1, 'form': 'x', 'value': 'B_x'}])
    require(bscope['positions'][0]['state'] == 'LINE_START', 'Folio reset fixture')
    b_same = dict(bscope['positions'][0], source_id='SYN:B:2:0', state='PREV_DY',
                  context={'LINE_START': False, 'PREV_LITERAL_DY': True}, anchor_eligible=False)
    all_rows = rows + bscope['positions'] + [b_same]
    cells, shared, collisions, summary = panel_tables(all_rows, entries, ['x'])
    require(len(cells['RAW_EXACT']) == len(entries['A'].keys() | entries['B'].keys()) * 3, 'All forms/cells retained')
    require(len(shared['RAW_EXACT']) == 3 and len(collisions['RAW_EXACT']) == 1, 'Shared collision fixture')
    require(collisions['RAW_EXACT'][0]['state'] == 'PREV_DY' and len(collisions['RAW_EXACT'][0]['cross_family_pairs']) == 2, 'Every collision pair retained')
    require(not collisions['LITERAL_LINES'] and summary['LITERAL_LINES']['positions'] == 4, 'Literal is True, no uncertainty deletion')
    require(any(row['form'] == 'only_B' and row['A_count'] == row['B_count'] == 0 for row in cells['RAW_EXACT']), 'Absent forms remain in denominator')
    require(len(rows) == len(words) and rows[3]['raw'] == 'xdy@100;', 'No raw normalization')
    bad = {**paragraph, 'page': 'f84r'}
    try:
        annotate_paragraph(bad, record, entries, receipt)
    except RuntimeError:
        pass
    else:
        raise RuntimeError('Forbidden selector accepted')
    return {'status': 'PASS', 'target_read': False, 'synthetic_positions': len(all_rows),
            'fixtures': ['current_dy_at_start', 'literal_ascii_suffix', 'raw_entity_and_uncertainty',
                         'physical_line_reset', 'folio_reset', 'all_context_cells', 'all_collision_pairs',
                         'literal_true_identity', 'unshared_zero_cells', 'forbidden_selector']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--self-test', action='store_true')
    actions.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False))
        return 0
    spec = load(EXP / 'src/SPEC.json')
    registration = verify_registration(spec)
    outputs = execute(spec, registration)
    directory = EXP / 'artifacts'
    directory.mkdir(exist_ok=True)
    for name, data in outputs.items():
        (directory / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(outputs['RESULT.json'], ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, KeyError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print('GDT1037 STOP: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)

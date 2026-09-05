#!/usr/bin/env python3
"""Extract predeclared whole-family contexts; --check replays source, not meaning."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
FAMILY = ('dan', 'dain', 'daiin', 'daiiin')
READERS = ('zl3b_clean', 'it2a_clean', 'rf1b_clean')
BASE = 'transcription/voynich_zl3b_lines.tsv'
CROSS = 'transcription/voynich_cross_transcription_lines.tsv'
ADMISSIONS = 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv'
META = ['page', 'locus', 'line_number', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def query(path, columns, pages):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in pages:
        command += ['--allow', page]
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(s[12:]) for s in result.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    require(len(stats) == 1, 'Missing selector-first guard statistics')
    reader = csv.DictReader(io.StringIO(result.stdout), delimiter='\t')
    require(reader.fieldnames == columns, 'Projection schema differs')
    rows = list(reader)
    require(len(rows) == stats[0]['selected'], 'Guard count differs')
    require({r['page'] for r in rows} == set(pages), 'Unexpected or missing selector')
    require(len({r['locus'] for r in rows}) == len(rows), 'Duplicate locus')
    return rows, {'command': command, 'stats': stats[0], 'projection_sha256': digest(result.stdout.encode())}


def build():
    # These are admission metadata, not unguarded mixed manuscript payloads.
    with (ROOT / ADMISSIONS).open() as handle:
        old = list(csv.DictReader(handle, delimiter='\t'))
    with (EXP / 'src/PAGE_ADMISSIONS.tsv').open() as handle:
        new = list(csv.DictReader(handle, delimiter='\t'))
    require(len(old) == 35 and len({r['physical_page'] for r in old}) == 30, 'Original admission scope')
    require(len(new) == 4 and all(r['decision'] == 'ADMITTED' for r in new), 'Extra admission scope')
    pages = [r['source_selector'] for r in old + new]
    require(len(set(pages)) == 39 and not any(p.startswith('f84') for p in pages), 'Sealed/duplicate selector')
    rows, base_guard = query(BASE, META, pages)
    alternate, cross_guard = query(CROSS, ['page', 'locus', *READERS], pages)
    cross = {r['locus']: r for r in alternate}
    require(set(cross) == {r['locus'] for r in rows}, 'Alternate locus coverage differs')
    for row in rows:
        require(cross[row['locus']]['page'] == row['page'], 'Cross-reader page mismatch')
        require(cross[row['locus']]['zl3b_clean'] == row['eva_clean'], 'ZL source mismatch')
        row.update({key: cross[row['locus']][key] for key in READERS})
    blocks = []
    current = []
    for row in rows:
        if current and (row['page'] != current[-1]['page'] or row['kind'] != 'P'
                        or row['paragraph_start'] == '1'):
            blocks.append(current)
            current = []
        if row['kind'] != 'P':
            blocks.append([row])
        else:
            current.append(row)
            if row['paragraph_end'] == '1':
                blocks.append(current)
                current = []
    if current:
        blocks.append(current)
    require(sum(map(len, blocks)) == len(rows), 'Block reconstruction lost source loci')
    counts = {reader: Counter() for reader in READERS}
    events = []
    selected = []
    for block in blocks:
        triggers = []
        for reader in READERS:
            words = [(row['locus'], i + 1, token) for row in block
                     for i, token in enumerate(row[reader].split())]
            counts[reader].update(w[2] for w in words if w[2] in FAMILY)
            for i, (locus, position, token) in enumerate(words):
                if token not in FAMILY:
                    continue
                reasons = []
                if token in ('dan', 'daiiin'):
                    reasons.append('RARE_ENDPOINT')
                if i and words[i - 1][2] in FAMILY:
                    reasons.append('ADJACENT_FAMILY')
                if i == 0 and block[0]['kind'] == 'P' and block[0]['paragraph_start'] == '1':
                    reasons.append('PROSE_PARAGRAPH_INITIAL')
                if reasons:
                    event = {'reader': reader, 'locus': locus, 'position_1based': position,
                             'token': token, 'previous': list(words[i - 1]) if i else None,
                             'reasons': reasons}
                    triggers.append(event)
                    events.append(event)
        if triggers:
            selected.append({'page': block[0]['page'], 'kind': block[0]['kind'],
                             'triggers': triggers, 'lines': block})
    result = {'status': 'WHOLE_FAMILY_CONTEXTS_ONLY_NO_SEMANTIC_WINNER',
              'design_timing': 'POST_RESULT_EXTENSION_BEFORE_39_SELECTOR_EXTRACTION',
              'source_selectors': pages, 'visual_page_keys': 34, 'new_admissions': 0,
              'sealed_data': ['f84', 'f84r'], 'source_loci': len(rows),
              'counts_by_alternate_reading': {r: {f: counts[r][f] for f in FAMILY} for r in READERS},
              'selected_blocks': len(selected), 'selected_loci': sum(len(b['lines']) for b in selected),
              'triggers': events, 'guarded_queries': [base_guard, cross_guard],
              'alternate_readings_not_independent_witnesses': True,
              'meanings_validated': False, 'dictionary_changed': False,
              'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0}
    # Explicit retrospective same-head follow-up; not part of the original
    # endpoint/pair/paragraph-initial selection and not independent evidence.
    chol_frames = []
    for row in rows:
        positions = {}
        for reader in READERS:
            words = row[reader].split()
            positions[reader] = [i + 1 for i in range(len(words) - 1)
                                 if words[i] == 'chol' and words[i + 1] in FAMILY]
        if any(positions.values()):
            chol_frames.append({'source_line': row, 'chol_positions_1based': positions})
    result['shared_chol_frame_followup'] = {
        'timing': 'POST_CONTEXT_DESCRIPTIVE_QUERY',
        'rule': 'All within-locus exact chol plus family pairs in any reading; no cross-line search.',
        'semantics': 'chol=dry is conditional, not independently confirmed',
        'complete_paragraphs_claimed': False, 'frames': chol_frames}
    contexts = {'selection_rule': 'FAMILY_PROBE_DESIGN.md', 'blocks': selected}
    return {'FAMILY_CONTEXTS.json': contexts, 'FAMILY_PROBE_RESULT.json': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    artifacts = build()
    for name, value in artifacts.items():
        payload = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
        target = EXP / 'artifacts' / name
        if args.check:
            require(target.is_file() and target.read_bytes() == payload, f'Replay mismatch: {name}')
        else:
            target.write_bytes(payload)
    result = artifacts['FAMILY_PROBE_RESULT.json']
    print(json.dumps({key: result[key] for key in ('status', 'source_loci', 'selected_blocks',
          'selected_loci', 'counts_by_alternate_reading')}, sort_keys=True))


if __name__ == '__main__':
    main()

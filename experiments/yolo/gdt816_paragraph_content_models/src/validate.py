#!/usr/bin/env python3
"""Independently check fixed paragraph trials against guarded source projections."""
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
PARAGRAPHS = [['f88r', 18, 22], ['f77r', 25, 37], ['f24v', 1, 5], ['f75r', 32, 46]]
LABELS = ['f88r.15', 'f77r.3']
WHOLES = ['okol', 'chor', 'ychey', 'otedy', 'qokain', 'solkeey']
SHARED = {'otchol': 'dieses?', 'cthar': 'Wurzel?', 'chol': 'trocken?',
          'dan': 'sehr wenig?', 'dain': 'wenig?', 'daiin': 'viel?', 'daiiin': 'sehr viel?'}
COMMON = {'chor': 'Blätter?', 'ychey': 'Saft?', 'otedy': 'Quelle?', 'qokain': 'Wasser?', 'solkeey': 'Dampf?'}
MODELS = {'Q_JOINT': COMMON | {'okaiin': 'warm?', 'okol': 'Kraut?'},
          'R_JOINT': COMMON | {'okaiin': 'dessen?', 'okol': 'Pflanze?'}}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_tsv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def query(path, columns, pages):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in pages:
        command += ['--allow', page]
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    process = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    stats = [json.loads(line[12:]) for line in process.stderr.splitlines() if line.startswith('GUARD_STATS ')]
    require(len(stats) == 1, 'Unique guarded-query statistics missing')
    projection = csv.DictReader(io.StringIO(process.stdout), delimiter='\t')
    require(projection.fieldnames == columns, 'Projection schema differs')
    rows = list(projection)
    require(len(rows) == stats[0]['selected'] == 1062 and {r['page'] for r in rows} == set(pages), 'Scope coverage')
    require(len({r['locus'] for r in rows}) == len(rows), 'Duplicate source locus')
    return rows, {'command': command, 'stats': stats[0],
                  'projection_sha256': hashlib.sha256(process.stdout.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without writing any file')
    args = parser.parse_args()
    prior = json.loads((ROOT / 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json').read_text())
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    admissions = read_tsv(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    extra = read_tsv(ROOT / 'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv')
    pages = prior['source_selectors']
    require(len(pages) == len(set(pages)) == 39 and not any(p.startswith('f84') for p in pages), 'Scope/seals')
    require(set(pages) == {r['source_selector'] for r in admissions + extra} and len(admissions) == 35 and
            len(extra) == 4 and all(r['decision'] == 'ADMITTED' for r in extra), 'Admission metadata differs')
    require(prior['shared_hypotheses'] == SHARED and spec['models'] == MODELS, 'Fixed whole-word meanings changed')
    require(spec['paragraphs'] == PARAGRAPHS and spec['labels'] == LABELS and spec['new_wholes'] == WHOLES, 'Design changed')
    require(spec['joint_quality_frame'] == 'MEDICAL_HUMORAL_COMPLEXION_NOT_PHYSICAL_TEMPERATURE_OR_DRYING' and
            spec['frame_declaration_timing'] == 'POST_EXTERNAL_CLARIFICATION_NOT_PREREGISTERED_SUCCESS' and
            spec['agent_Q_frames_agree'] is False, 'Joint frame or declaration timing changed')
    require(spec['sealed_data'] == prior['sealed_data'] == ['f84', 'f84r'] and
            spec['confidence'] == 'C0_UNCONFIRMED' and spec['new_admissions'] == 0 and
            spec['dictionary_changed'] is False and spec['meanings_validated'] is False, 'Claim limits changed')
    require({w for w in MODELS['Q_JOINT'] if MODELS['Q_JOINT'][w] != MODELS['R_JOINT'][w]} ==
            {'okol', 'okaiin'} and all('qokaiin' not in model for model in MODELS.values()), 'World differences or alias')
    rows, guard1 = query('transcription/voynich_zl3b_lines.tsv',
                        ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean'], pages)
    alternate, guard2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *READERS], pages)
    by = {r['locus']: r for r in rows}
    require(set(by) == {r['locus'] for r in alternate}, 'Reader coverage differs')
    for row in alternate:
        require(by[row['locus']]['page'] == row['page'] and by[row['locus']]['eva_clean'] == row[READERS[0]], 'Reader join')
        by[row['locus']].update({reader: row[reader] for reader in READERS})
    position = {r['locus']: i for i, r in enumerate(rows)}
    focal, counts = [], []
    document = '# GDT816 complete focal reader\n\nEvery source line in four paragraphs and two labels; no fluent translation.\n\n'
    for page, start, end in PARAGRAPHS:
        first, last = f'{page}.{start}', f'{page}.{end}'
        block = rows[position[first]:position[last] + 1]
        require([r['locus'] for r in block] == [f'{page}.{n}' for n in range(start, end + 1)] and
                all(r['kind'] == 'P' and r['page'] == page for r in block), 'Complete contiguous P loci')
        require(block[0]['paragraph_start'] == block[-1]['paragraph_end'] == '1' and
                all(r['paragraph_start'] == '0' for r in block[1:]) and
                all(r['paragraph_end'] == '0' for r in block[:-1]), 'Exact P start/end boundary flags')
        focal += block
        counts.append(dict(page=page, first=first, last=last, loci=len(block),
                           tokens={reader: sum(len(r[reader].split()) for r in block) for reader in READERS}))
        document += f'## {first}--{last}\n\n'
        for row in block:
            document += row['locus'] + ' ZL: `' + row[READERS[0]] + '`\n'
            for reader in READERS[1:]:
                if row[reader] != row[READERS[0]]:
                    document += reader + ': `' + row[reader] + '`\n'
            document += '\n'
    for locus, word in zip(LABELS, ['okol', 'otedy']):
        require(by[locus]['kind'] == 'L' and all(by[locus][r].split() == [word] for r in READERS), 'Separate whole label')
        focal.append(by[locus])
        document += f'## {locus} [separate L]\n\n' + word + '\n\n'
    focal_ids = {r['locus'] for r in focal}
    external = [r for r in rows if r['locus'] not in focal_ids and
                any(w in WHOLES for reader in READERS for w in r[reader].split())]
    require(len(focal) == len(focal_ids) == 40 and len(external) == 94, 'Focal/external exact coverage')
    require([r['locus'] for r in external if r['kind'] != 'P'] == ['f69v.2', 'f71v.12', 'f89r2.10'], 'Non-P concordance')
    require([r['locus'] for r in external if any('solkeey' in r[k].split() for k in READERS)] ==
            ['f81v.19', 'f83r.52'], 'External exact solkeey')
    require([by['f75r.35'][r].split().count('qokain') for r in READERS] == [3, 2, 3] and
            by['f75r.35'][READERS[1]].split()[-3] == 'qokar', 'Repeated qokain and IT qokar')
    require(all(by['f77r.34'][r].split().count('qokaiin') == 3 for r in READERS), 'Distinct repeated qokaiin')
    require(all(by['f88r.19'][r].split().count('qoekol') == 2 for r in READERS), 'Repeated qoekol')
    require(by['f81v.1']['paragraph_start'] == by['f81v.9']['paragraph_end'] ==
            by['f81v.10']['paragraph_start'] == '1', 'External P boundary')
    require(all('otedy' not in by[f'f81v.{n}'][r].split() for n in range(1, 10) for r in READERS),
            'Claimed source absence inside complete f81v first P differs')
    require(all('qokain okaiin' in by['f81v.6'][r] for r in READERS) and
            all('otedy' in by['f95v2.1'][r].split() for r in READERS), 'External exact pairs/nouns')

    def record(row):
        return {key: row[key] for key in ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end']} | {
            'readings_json': json.dumps({reader: row[reader] for reader in READERS}, ensure_ascii=False)}

    literals = []
    for row in focal:
        for reader in READERS:
            for model in ['Q_JOINT', 'R_JOINT']:
                values = SHARED | MODELS[model]
                literal = [values.get(word, '[' + word + ']') for word in row[reader].split()]
                literals.append(dict(page=row['page'], locus=row['locus'], kind=row['kind'], reader=reader, model=model,
                    source_text=row[reader], literal_json=json.dumps(literal, ensure_ascii=False), confidence='C0_UNCONFIRMED'))
    result = dict(experiment_id='GDT816', status='FIXED_NOUN_TRIALS_NOT_TRANSLATION', source_selectors=pages,
        visual_page_keys=34, source_loci=1062, paragraphs=counts, focal_loci=40, literal_rows=240, external_loci=94,
        external_nonP_loci=['f69v.2', 'f71v.12', 'f89r2.10'], new_wholes=WHOLES, guarded_queries=[guard1, guard2],
        joint_quality_frame='MEDICAL_HUMORAL_COMPLEXION_NOT_PHYSICAL_TEMPERATURE_OR_DRYING',
        frame_declaration_timing='POST_EXTERNAL_CLARIFICATION_NOT_PREREGISTERED_SUCCESS', agent_Q_frames_agree=False,
        sealed_data=['f84', 'f84r'], new_admissions=0, dictionary_changed=False, meanings_validated=False,
        confirmed_lexemes=0, confirmed_plaintext_clauses=0)
    expected = [[record(r) for r in focal], [record(r) for r in external], literals, document.rstrip() + '\n', result]
    actual = [read_tsv(EXP / 'artifacts' / name) for name in ('FOCAL.tsv', 'EXTERNAL.tsv', 'LITERAL_TRIALS.tsv')]
    actual += [(EXP / 'artifacts/FULL_READER.md').read_text(), json.loads((EXP / 'artifacts/RESULT.json').read_text())]

    def audit(payload):
        require(payload == expected, 'Independent source, literal, reader or claim reconstruction differs')

    audit(actual)
    packet = read_tsv(EXP / 'src/RELATION_PACKET.tsv')
    require([(r['pivot_locus'], r['target_locus']) for r in packet] ==
            [('f88r.19', 'f88r.22'), ('f77r.25', 'f77r.27'), ('f77r.25', 'f77r.35'),
             ('f75r.43', 'f75r.45')], 'Four explicit R candidate bindings differ')
    gate_process = subprocess.run(['./vmanus-exp', 'check-edge-packet',
        str((EXP / 'src/RELATION_PACKET.tsv').relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    gate = json.loads(gate_process.stdout)
    require(gate == json.loads((EXP / 'artifacts/EDGE_GATE.json').read_text()) and
            gate['packet_rows'] == 4 and gate['eligible_edges'] == 0 and gate['score_ready'] is False,
            'Exploratory bindings received semantic credit or gate artifact differs')
    controls = []
    for name in ('DELETE_DUPLICATE_QOKAIN', 'QOKAIIN_WATER_ALIAS', 'LOSE_RING_RECORD', 'R_SOURCE_TO_WATER'):
        altered = copy.deepcopy(actual)
        if name == 'DELETE_DUPLICATE_QOKAIN':
            row = next(r for r in altered[0] if r['locus'] == 'f75r.35')
            readings = json.loads(row['readings_json'])
            words = readings[READERS[0]].split()
            words.pop(words.index('qokain'))
            readings[READERS[0]] = ' '.join(words)
            row['readings_json'] = json.dumps(readings, ensure_ascii=False)
        elif name == 'QOKAIIN_WATER_ALIAS':
            row = next(r for r in altered[2] if r['locus'] == 'f77r.34')
            row['literal_json'] = row['literal_json'].replace('[qokaiin]', 'Wasser?', 1)
        elif name == 'LOSE_RING_RECORD':
            altered[1] = [r for r in altered[1] if r['locus'] != 'f69v.2']
        else:
            row = next(r for r in altered[2] if r['locus'] == 'f77r.25' and r['model'] == 'R_JOINT')
            row['literal_json'] = row['literal_json'].replace('Quelle?', 'Wasser?', 1)
        try:
            audit(altered)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('Negative control escaped: ' + name)
    validation = dict(experiment_id='GDT816', status='PASS', focal_loci=40, external_loci=94, literal_rows=240,
        complete_source_P_paragraphs=4, separate_L_records=2, source_bound_full_reader=True,
        negative_controls_rejected=controls, independent_raw_guarded_queries=True, runner_imported_or_called=False,
        joint_frame_and_declaration_timing_retained=True, external_source_absence_checked=True,
        relation_gate_recomputed=True, eligible_relation_edges=0,
        meanings_validated=False, historical_or_image_claims_validated=False)
    payload = json.dumps(validation, indent=2, sort_keys=True) + '\n'
    target = EXP / 'artifacts/VALIDATION.json'
    if args.check:
        require(target.read_text() == payload, 'Stored validation differs')
    else:
        target.write_text(payload)
    print('PASS: 40 focal loci, 94 external loci, 240 literals; four mutations rejected; source checks only')


if __name__ == '__main__':
    main()

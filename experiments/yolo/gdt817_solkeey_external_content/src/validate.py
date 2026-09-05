#!/usr/bin/env python3
"""Independent source, fixed-sense and bounded-challenge reconstruction only."""
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
PAGES = ['f77r', 'f81v', 'f83r']
PARAGRAPHS = [['f77r', 25, 37], ['f81v', 10, 27], ['f83r', 52, 55]]
WHOLES = ['okol', 'chor', 'ychey', 'otedy', 'qokain', 'solkeey']
SHARED = {'otchol': 'dieses?', 'cthar': 'Wurzel?', 'chol': 'trocken?',
          'dan': 'sehr wenig?', 'dain': 'wenig?', 'daiin': 'viel?', 'daiiin': 'sehr viel?'}
COMMON = {'chor': 'Blätter?', 'ychey': 'Saft?', 'otedy': 'Quelle?', 'qokain': 'Wasser?', 'solkeey': 'Dampf?'}
MODELS = {'Q_JOINT': COMMON | {'okaiin': 'warm?', 'okol': 'Kraut?'},
          'R_JOINT': COMMON | {'okaiin': 'dessen?', 'okol': 'Pflanze?'}}
ADDITIONS = {'chedy': 'wird?', 'ol': 'oder?'}
SENSES = {'chedy': 'BECOMES_CHANGE_OF_STATE_NOT_IS_OR_AUXILIARY_OR_MAKES',
          'ol': 'ALTERNATIVE_COORDINATION_NOT_AND_WITH_FROM_OR_OIL'}
FRAME = 'MEDICAL_HUMORAL_COMPLEXION_NOT_PHYSICAL_TEMPERATURE_OR_DRYING'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, ensure_ascii=False)


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
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    inherited_path = 'experiments/yolo/gdt816_paragraph_content_models/src/SPEC.json'
    previous = json.loads((ROOT / inherited_path).read_text())
    older = json.loads((ROOT / 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json').read_text())
    admissions = read_tsv(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    extra = read_tsv(ROOT / 'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv')
    pages = older['source_selectors']
    require(len(pages) == len(set(pages)) == 39 and not any(p.startswith('f84') for p in pages), 'Scope/seals')
    require(set(pages) == {r['source_selector'] for r in admissions + extra} and len(admissions) == 35 and
            len(extra) == 4 and all(r['decision'] == 'ADMITTED' for r in extra), 'Admission metadata differs')
    require(spec['pages'] == PAGES and set(PAGES) <= set(pages) and spec['paragraphs'] == PARAGRAPHS, 'Focal scope')
    require(spec['inherited_model_spec'] == inherited_path and previous['new_wholes'] == WHOLES and
            previous['models'] == MODELS and older['shared_hypotheses'] == SHARED, 'Inherited fixed words')
    require(previous['joint_quality_frame'] == FRAME and previous['agent_Q_frames_agree'] is False and
            previous['frame_declaration_timing'] == 'POST_EXTERNAL_CLARIFICATION_NOT_PREREGISTERED_SUCCESS', 'Frame debt')
    require(spec['additions'] == ADDITIONS and spec['fixed_senses'] == SENSES and spec['challenge_patterns'] ==
            ['EXACT_CHEDY_DUPLICATE', 'EXACT_OL_DUPLICATE', 'KNOWN_NOUN_CHEDY_KNOWN_NOUN', 'NON_P_ADDITION'], 'New fixed senses')
    require(spec['sealed_data'] == previous['sealed_data'] == older['sealed_data'] == ['f84', 'f84r'] and
            spec['confidence'] == 'C0_UNCONFIRMED' and spec['new_admissions'] == 0 and
            spec['dictionary_changed'] is False and spec['meanings_validated'] is False, 'Claim ceiling')
    rows, guard1 = query('transcription/voynich_zl3b_lines.tsv',
                        ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean'], pages)
    alternate, guard2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *READERS], pages)
    by = {r['locus']: r for r in rows}
    require(set(by) == {r['locus'] for r in alternate}, 'Reader coverage')
    for row in alternate:
        require(by[row['locus']].get('page') == row['page'] and by[row['locus']]['eva_clean'] == row[READERS[0]], 'Reader join')
        by[row['locus']].update({reader: row[reader] for reader in READERS})
    position = {r['locus']: i for i, r in enumerate(rows)}
    focal, counts, trials = [], [], []
    for page, start, end in PARAGRAPHS:
        first, last = f'{page}.{start}', f'{page}.{end}'
        block = rows[position[first]:position[last] + 1]
        require([r['locus'] for r in block] == [f'{page}.{n}' for n in range(start, end + 1)] and
                all(r['kind'] == 'P' and r['page'] == page for r in block), 'Complete contiguous P block')
        require(block[0]['paragraph_start'] == block[-1]['paragraph_end'] == '1' and
                all(r['paragraph_start'] == '0' for r in block[1:]) and
                all(r['paragraph_end'] == '0' for r in block[:-1]), 'P boundary flags')
        focal += block
        counts.append(dict(page=page, first=first, last=last, loci=len(block),
                           tokens={rd: sum(len(r[rd].split()) for r in block) for rd in READERS}))
        for row in block:
            for rd in READERS:
                words = row[rd].split()
                for world in MODELS:
                    base = SHARED | MODELS[world]
                    extended = base | ADDITIONS
                    trials.append(dict(page=page, locus=row['locus'], reader=rd, world=world, source_text=row[rd],
                        base_json=encode([base.get(w, '[' + w + ']') for w in words]),
                        extended_json=encode([extended.get(w, '[' + w + ']') for w in words]), confidence='C0_UNCONFIRMED'))
    page_rows = [r for r in rows if r['page'] in PAGES]
    require(len(focal) == 35 and len(page_rows) == 133 and len(trials) == 210, 'Coverage counts')
    document = '# GDT817 complete three-page source reader\n\nAll P/L records and differing alternate readings; no decoded sentence boundaries.\n\n'
    for row in page_rows:
        document += f"{row['locus']} [{row['kind']}; start={row['paragraph_start']}; end={row['paragraph_end']}] ZL: `{row[READERS[0]]}`\n"
        for rd in READERS[1:]:
            if row[rd] != row[READERS[0]]:
                document += rd + ': `' + row[rd] + '`\n'
        document += '\n'
    inventory, challenges = [], []
    for row in rows:
        for rd in READERS:
            words = row[rd].split()
            for whole in ['chedy', 'ol']:
                indices = [i + 1 for i, word in enumerate(words) if word == whole]
                if indices:
                    inventory.append(dict(page=row['page'], locus=row['locus'], kind=row['kind'], reader=rd,
                                          whole=whole, ordinals_json=encode(indices)))
            candidates = [(i, 0, 'EXACT_' + a.upper() + '_DUPLICATE', [a, b])
                          for i, (a, b) in enumerate(zip(words, words[1:])) if a in ADDITIONS and a == b]
            candidates += [(i, 1, 'KNOWN_NOUN_CHEDY_KNOWN_NOUN', [a, b, c])
                           for i, (a, b, c) in enumerate(zip(words, words[1:], words[2:]))
                           if a in WHOLES and b == 'chedy' and c in WHOLES]
            if row['kind'] != 'P':
                candidates += [(i, 2, 'NON_P_ADDITION', [w]) for i, w in enumerate(words) if w in ADDITIONS]
            if candidates:
                hits = [dict(pattern=kind, first_ordinal=i + 1, words=words)
                        for i, _, kind, words in sorted(candidates, key=lambda item: item[:2])]
                challenges.append(dict(page=row['page'], locus=row['locus'], kind=row['kind'], reader=rd,
                                       source_text=row[rd], hits_json=encode(hits)))
    require(len(inventory) == 511 and len(challenges) == 20 and len({r['locus'] for r in challenges}) == 10, 'Bounded deck')
    require(all(by['f81r.4'][rd].split()[2:4] == ['ol', 'ol'] for rd in READERS) and
            by['f81r.5'][READERS[0]].split()[3:6] == ['ol', 'ol', 'olaiin'] and
            all(by['f81r.5'][rd].split()[3:6] == ['ol'] * 3 for rd in READERS[1:]), 'Source duplicates or split erased')
    require(all(not any(w in {'qokain', 'otedy', 'okaiin'} for w in by[f'f83r.{i}'][rd].split())
                for i in range(52, 56) for rd in READERS), 'Invented f83 focal source/water/okaiin')
    result = dict(experiment_id='GDT817', status='CONCRETE_BECOMES_OR_TRIALS_NOT_TRANSLATION', source_selectors=pages,
        source_loci=1062, page_reader_loci=133, focal_loci=35, literal_rows=210, paragraphs=counts, challenge_rows=20,
        challenge_loci=10, addition_inventory_rows=511, guarded_queries=[guard1, guard2], joint_quality_frame=FRAME,
        fixed_senses=SENSES, challenge_coverage='PREDECLARED_PATTERNS_NOT_ALL_OCCURRENCES_SEMANTICALLY_READ',
        sealed_data=['f84', 'f84r'], new_admissions=0, dictionary_changed=False, confirmed_lexemes=0,
        confirmed_plaintext_clauses=0, meanings_validated=False)

    def record(row):
        return {k: row[k] for k in ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end']} | {
            'readings_json': encode({rd: row[rd] for rd in READERS})}

    expected = [[record(r) for r in page_rows], [record(r) for r in focal], trials, challenges, inventory,
                document.rstrip() + '\n', result]
    actual = [read_tsv(EXP / 'artifacts' / name) for name in
              ['PAGES.tsv', 'FOCAL.tsv', 'LITERAL_TRIALS.tsv', 'CHALLENGES.tsv', 'ADDITION_INVENTORY.tsv']]
    actual += [(EXP / 'artifacts/FULL_READER.md').read_text(), json.loads((EXP / 'artifacts/RESULT.json').read_text())]

    def audit(payload):
        require(payload == expected, 'Independent source/literal/deck/reader reconstruction differs')

    audit(actual)
    gate_run = subprocess.run(['./vmanus-exp', 'check-edge-packet',
        str((EXP / 'src/RELATION_PACKET.tsv').relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    gate = json.loads(gate_run.stdout)
    require(gate == json.loads((EXP / 'artifacts/EDGE_GATE.json').read_text()) and
            gate['packet_rows'] == 3 and gate['eligible_edges'] == 0 and gate['score_ready'] is False,
            'Exploratory edge gate changed or received semantic credit')
    controls = []
    for name in ['DROP_REPEATED_OL', 'BECOMES_TO_IS', 'QOKAIIN_WATER_ALIAS', 'ERASE_SPLIT_ALTERNATE', 'INVENT_F83_WATER']:
        changed = copy.deepcopy(actual)
        if name == 'DROP_REPEATED_OL':
            row = next(r for r in changed[3] if r['locus'] == 'f81r.4')
            row['source_text'] = row['source_text'].replace('ol ol', 'ol', 1)
        elif name in ['BECOMES_TO_IS', 'QOKAIIN_WATER_ALIAS']:
            row = next(r for r in changed[2] if r['locus'] == ('f77r.35' if name == 'BECOMES_TO_IS' else 'f77r.34'))
            before, after = ('wird?', 'ist?') if name == 'BECOMES_TO_IS' else ('[qokaiin]', 'Wasser?')
            row['extended_json'] = row['extended_json'].replace(before, after, 1)
        elif name == 'ERASE_SPLIT_ALTERNATE':
            row = next(r for r in changed[0] if r['locus'] == 'f81v.10')
            readings = json.loads(row['readings_json'])
            readings[READERS[2]] = readings[READERS[2]].replace('ote y', 'otedy', 1)
            row['readings_json'] = encode(readings)
        else:
            row = next(r for r in changed[2] if r['locus'] == 'f83r.52')
            row['extended_json'] = row['extended_json'].replace('[qekey]', 'Wasser?', 1)
        try:
            audit(changed)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('Negative mutation escaped: ' + name)
    validation = dict(experiment_id='GDT817', status='PASS', focal_loci=35, page_reader_loci=133, literal_rows=210,
        challenge_loci=10, challenge_rows=20, addition_inventory_rows=511, source_bound_full_reader=True,
        independent_raw_guarded_queries=True, runner_imported_or_called=False, negative_controls_rejected=controls,
        meanings_validated=False, historical_or_image_claims_validated=False, all_addition_occurrences_semantically_read=False,
        relation_gate_recomputed=True, eligible_relation_edges=0)
    payload = json.dumps(validation, indent=2, sort_keys=True) + '\n'
    target = EXP / 'artifacts/VALIDATION.json'
    if args.check:
        require(target.read_text() == payload, 'Stored validation differs')
    else:
        target.write_text(payload)
    print('PASS: 35 focal, 133 page records, 210 paired displays; five mutations rejected; no semantic validation')


if __name__ == '__main__':
    main()

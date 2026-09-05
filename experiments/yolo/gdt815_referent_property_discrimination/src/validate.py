#!/usr/bin/env python3
"""Independent guarded source/content checks; no historical or semantic validation."""
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
SHARED = {'otchol': 'dieses?', 'cthar': 'Wurzel?', 'chol': 'trocken?',
          'dan': 'sehr wenig?', 'dain': 'wenig?', 'daiin': 'viel?', 'daiiin': 'sehr viel?'}
MODELS = {'N': 'Pulver?', 'G': 'ist?', 'Q': 'warm?', 'R': 'dessen?', 'K': 'kalt?', 'B': 'bitter?'}
CARD_LOCI = [('F17_ROOT', ['f17r.11']), ('OKOL_PROPERTY_OR_GENITIVE', ['f24v.4']),
             ('YCHEY_PROPERTY_OR_POSSESSION', ['f88r.22']), ('OTEDY_PROPERTY_OR_GENITIVE', ['f75r.45']),
             ('OTY_CROSS_LINE', ['f21r.8', 'f21r.9']), ('READER_SPECIFIC_HEAD', ['f81v.4', 'f81v.5']),
             ('AIN_SCALAR', ['f76r.32']), ('SOLITARY_LABEL', ['f88v.14']),
             ('SCALAR_LABEL', ['f89r1.14']), ('ASTRAL_LABEL', ['f72r3.12'])]
LINKS = [('okol', 'f88r.15', 'f88r.19', 'f88r.22', 'SAME_SOURCE_PARAGRAPH_NOT_PROVEN_ANTECEDENT'),
         ('otedy', 'f77r.3', 'f77r.25', 'f77r.27', 'SAME_SOURCE_PARAGRAPH_NOT_PROVEN_ANTECEDENT'),
         ('oty', 'f70v2.5', 'f21r.8', 'f21r.9', 'CROSS_PAGE_WRITTEN_HEAD_NOT_NAMED_REFERENT')]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_tsv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def query(path, columns, pages):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in pages:
        command.extend(['--allow', page])
    command.extend(['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r'])
    process = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    stats = [json.loads(line[12:]) for line in process.stderr.splitlines() if line.startswith('GUARD_STATS ')]
    require(len(stats) == 1, 'Missing unique raw-selector guard statistics')
    projection = csv.DictReader(io.StringIO(process.stdout), delimiter='\t')
    require(projection.fieldnames == columns, 'Raw projection schema changed')
    rows = list(projection)
    require(len(rows) == stats[0]['selected'] == 1062, 'Guarded coverage changed')
    require({r['page'] for r in rows} == set(pages), 'Projection scope changed')
    require(len({r['locus'] for r in rows}) == len(rows), 'Duplicate raw source locus')
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
    require(set(pages) == {r['source_selector'] for r in admissions + extra}, 'Admission selectors differ')
    require(len(admissions) == 35 and len(extra) == 4 and all(r['decision'] == 'ADMITTED' for r in extra), 'Admissions')
    require(prior['shared_hypotheses'] == SHARED and spec['models'] == MODELS, 'Fixed meanings changed')
    require(spec['cards'] == [[name, loci] for name, loci in CARD_LOCI], 'Declared cards changed')
    require(spec['carrier_links'] == [dict(zip(['carrier', 'label', 'prose', 'target', 'relation'], link))
                                    for link in LINKS], 'Declared carrier links changed')
    require(spec['sealed_data'] == prior['sealed_data'] == ['f84', 'f84r'] and
            spec['confidence'] == 'C0_UNCONFIRMED' and spec['new_admissions'] == 0 and
            spec['dictionary_changed'] is False and spec['meaning_validation'] is False, 'Claim limits changed')
    base, guard1 = query('transcription/voynich_zl3b_lines.tsv',
                        ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean'], pages)
    alternate, guard2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *READERS], pages)
    by = {row['locus']: row for row in base}
    require(set(by) == {r['locus'] for r in alternate}, 'Alternate source coverage')
    for row in alternate:
        require(by[row['locus']]['page'] == row['page'] and
                by[row['locus']]['eva_clean'] == row['zl3b_clean'], 'Reader join')
        by[row['locus']].update({reader: row[reader] for reader in READERS})

    def paragraph(a, b):
        require(by[a]['page'] == by[b]['page'] and by[a]['kind'] == by[b]['kind'] == 'P', 'P endpoints')
        prose = [r for r in base if r['page'] == by[a]['page'] and r['kind'] == 'P']
        indices = {r['locus']: i for i, r in enumerate(prose)}
        start = max(i for i in range(indices[a] + 1) if prose[i]['paragraph_start'] == '1')
        end = next(i for i in range(start, len(prose)) if prose[i]['paragraph_end'] == '1')
        require(start <= indices[a] <= indices[b] <= end and
                not any(r['paragraph_start'] == '1' for r in prose[start + 1:end + 1]), 'Same P span')
        return [prose[start]['locus'], prose[end]['locus']]

    spans = [paragraph('f88r.19', 'f88r.22'), paragraph('f77r.25', 'f77r.27'), paragraph('f21r.8', 'f21r.9')]
    require(spans == [['f88r.18', 'f88r.22'], ['f77r.25', 'f77r.37'], ['f21r.8', 'f21r.12']], 'P boundaries')
    correction = {r: {'f81v.4_last_word': by['f81v.4'][r].split()[-1],
                      'f81v.5_first_two': by['f81v.5'][r].split()[:2]} for r in READERS}
    require([correction[r]['f81v.4_last_word'] for r in READERS] == ['chcthy', 'chckhy', 'chckhy'] and
            [correction[r]['f81v.5_first_two'] for r in READERS] == [['okaiin', 'daiin'], ['okaiin', 'daiin'],
                                                                  ['kaiin', 'aiin']], 'Specific reader correction')
    expected_cards, expected_trials, expected_links = [], [], []
    for name, loci in CARD_LOCI:
        for reader in READERS:
            lines = [by[locus][reader] for locus in loci]
            card = dict(card_id=name, page=by[loci[0]]['page'], source_loci=','.join(loci),
                        kind=by[loci[0]]['kind'], reader=reader, source_lines_json=json.dumps(lines, ensure_ascii=False))
            expected_cards.append(card)
            for model, gloss in MODELS.items():
                words = [word for line in lines for word in line.split()]
                literal = [gloss if word == 'okaiin' else SHARED.get(word, '[' + word + ']') for word in words]
                expected_trials.append(card | {'model': model, 'literal_hypotheses_json': json.dumps(literal,
                                               ensure_ascii=False), 'confidence': 'C0_UNCONFIRMED'})
    for carrier, label, prose, target, relation in LINKS:
        require(by[label]['kind'] == 'L', 'Independent label source kind')
        for reader in READERS:
            require(by[label][reader].split() == [carrier] and carrier in by[prose][reader].split() and
                    'okaiin' in by[target][reader].split(), 'Carrier whole identity')
            if carrier == 'oty':
                require(by[prose][reader].split()[-1] == carrier and
                        by[target][reader].split()[0] == 'okaiin', 'Exact cross-line pair')
            expected_links.append(dict(carrier=carrier, label_locus=label, prose_locus=prose, target_locus=target,
                reader=reader, label_text=by[label][reader], prose_text=by[prose][reader], target_text=by[target][reader],
                relation=relation, referent_identity='UNIDENTIFIED'))
    expected_result = dict(experiment_id='GDT815', status='SOURCE_CARDS_NOT_SEMANTIC_VALIDATION',
        source_selectors=pages, visual_page_keys=34, source_loci=1062, construction_cards=10, source_card_rows=30,
        literal_rows=180, carrier_links=3, carrier_reader_rows=9, f81v_correction=correction,
        guarded_queries=[guard1, guard2], new_admissions=0, confirmed_lexemes=0, confirmed_plaintext_clauses=0,
        dictionary_changed=False, meanings_validated=False, no_score_no_ranking=True, sealed_data=['f84', 'f84r'])
    expected = [expected_cards, expected_trials, expected_links, expected_result]
    actual = [read_tsv(EXP / 'artifacts' / name) for name in ('CARDS.tsv', 'LITERAL_TRIALS.tsv', 'CARRIER_LINKS.tsv')]
    actual.append(json.loads((EXP / 'artifacts/RESULT.json').read_text()))

    def audit(payload):
        require(payload == expected, 'Exact independent source/literal/claim reconstruction differs')

    audit(actual)
    annotations = read_tsv(EXP / 'src/CARRIER_LINKS.tsv')
    require(len(annotations) == 9, 'Audit bridge rows')
    for link in annotations:
        for reader_name in link['exact_readers'].split(','):
            reader = {'ZL3b': READERS[0], 'IT2a': READERS[1], 'RF1b': READERS[2]}[reader_name]
            for side in ('source', 'target'):
                words = [w for locus in link[side + '_locus'].split(',') for w in by[locus][reader].split()]
                excerpt = link[side + '_excerpt'].replace(' / ', ' ').split()
                require(any(words[i:i + len(excerpt)] == excerpt for i in range(len(words))), 'Audit excerpt changed')
            if link['relation_kind'] == 'EARLIER_WORD_IN_SAME_P_PARAGRAPH':
                paragraph(link['source_locus'], link['target_locus'])
    controls = []
    for name in ('READER_SMOOTHING', 'BITTER_TO_WARM', 'FALSE_CARRIER_IDENTITY'):
        changed = copy.deepcopy(actual)
        if name == 'READER_SMOOTHING':
            row = next(r for r in changed[0] if r['card_id'] == 'READER_SPECIFIC_HEAD' and r['reader'] == READERS[2])
            lines = json.loads(row['source_lines_json'])
            lines[1] = 'okaiin daiin ' + ' '.join(lines[1].split()[2:])
            row['source_lines_json'] = json.dumps(lines, ensure_ascii=False)
        elif name == 'BITTER_TO_WARM':
            row = next(r for r in changed[1] if r['card_id'] == 'F17_ROOT' and r['model'] == 'B')
            row['literal_hypotheses_json'] = row['literal_hypotheses_json'].replace('bitter?', 'warm?')
        else:
            changed[2][0]['referent_identity'] = 'CONFIRMED_ROOT'
        try:
            audit(changed)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('Negative mutation escaped: ' + name)
    validation = dict(experiment_id='GDT815', status='PASS', source_card_rows=30, literal_rows=180,
        carrier_reader_rows=9, audit_bridge_rows=9, source_paragraph_spans=spans,
        negative_controls_rejected=controls, independent_raw_guarded_queries=True,
        runner_imported_or_called=False, meanings_validated=False, historic_or_image_claims_validated=False)
    payload = json.dumps(validation, indent=2, sort_keys=True) + '\n'
    path = EXP / 'artifacts/VALIDATION.json'
    if args.check:
        require(path.read_text() == payload, 'Stored validation differs')
    else:
        path.write_text(payload)
    print('PASS: 30 source cards, 180 literals, 9 carrier rows; three mutations rejected; no meaning validation')


if __name__ == '__main__':
    main()

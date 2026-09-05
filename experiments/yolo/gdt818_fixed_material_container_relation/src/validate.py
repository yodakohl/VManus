#!/usr/bin/env python3
"""Independently reconstruct selected source blocks and fixed four-world trials."""
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
PARAGRAPHS = [['f77r', 25, 37], ['f81v', 10, 27], ['f83r', 52, 55]]
SHARED = {'otchol': 'dieses?', 'cthar': 'Wurzel?', 'chol': 'trocken?',
          'dan': 'sehr wenig?', 'dain': 'wenig?', 'daiin': 'viel?', 'daiiin': 'sehr viel?'}
BASE_R = {'okaiin': 'dessen?', 'okol': 'Pflanze?', 'chor': 'Blätter?', 'ychey': 'Saft?',
          'otedy': 'Quelle?', 'qokain': 'Wasser?', 'solkeey': 'Dampf?'}
WORLDS = {'V_BECOMES': {'solkeey': 'Dampf?', 'chedy': 'wird?'},
          'B_BECOMES': {'solkeey': 'Becken?', 'chedy': 'wird?'},
          'V_CONTAINS': {'solkeey': 'Dampf?', 'chedy': 'enthält?'},
          'B_CONTAINS': {'solkeey': 'Becken?', 'chedy': 'enthält?'}}
SENSES = {'Dampf?': 'AQUEOUS_VAPOUR_NOT_GENERIC_EMISSION_OR_MIXTURE',
          'Becken?': 'OPEN_PHYSICAL_CONTAINER_NOT_ITS_CONTENT_OR_BATHING',
          'wird?': 'BECOMES_CHANGE_INTO_RESULT_NOT_IS_OR_AUXILIARY',
          'enthält?': 'PHYSICALLY_CONTAINS_NOT_OWNS_FILLS_OR_BECOMES_FILLED'}
TAIL = ['sheedy', 'qokaiin', 'chedaiin', 'chealy']
CONTINUATION_FOCUS = ['sheedy', 'chedaiin', 'chealy']
CONTINUATION_MODELS = {
    'IF_AIR_IS_COLD': {'sheedy': 'wenn?', 'qokaiin': 'Luft?', 'chedaiin': 'ist?', 'chealy': 'kalt?'},
    'WITH_UNNAMED_CONTENT': {'sheedy': 'mit?'}}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def enc(value):
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
    old_path = 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json'
    previous_path = 'experiments/yolo/gdt816_paragraph_content_models/src/SPEC.json'
    old = json.loads((ROOT / old_path).read_text())
    previous = json.loads((ROOT / previous_path).read_text())
    admissions = read_tsv(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    extra = read_tsv(ROOT / 'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv')
    pages = old['source_selectors']
    require(len(pages) == len(set(pages)) == 39 and not any(p.startswith('f84') for p in pages), 'Scope/seals')
    require(set(pages) == {r['source_selector'] for r in admissions + extra} and len(admissions) == 35 and
            len(extra) == 4 and all(r['decision'] == 'ADMITTED' for r in extra), 'Admission metadata')
    require(spec['scope_spec'] == old_path and spec['inherited_spec'] == previous_path and
            old['shared_hypotheses'] == SHARED and previous['models']['R_JOINT'] == BASE_R, 'Inherited fixed R')
    require(spec['focal_paragraphs'] == PARAGRAPHS and spec['worlds'] == WORLDS and
            spec['fixed_senses'] == SENSES and spec['tail'] == TAIL, 'Worlds or tail changed')
    require(spec['contact_words'] == ['chedy', 'qokain'] and spec['contact_distances'] == [1, 2] and
            spec['duplicate_whole'] == 'chedy' and spec['ol_trial_inherited'] is False, 'Contact design or ol adoption')
    require(spec['sealed_data'] == old['sealed_data'] == previous['sealed_data'] == ['f84', 'f84r'] and
            spec['confidence'] == 'C0_UNCONFIRMED' and spec['new_admissions'] == 0 and
            spec['dictionary_changed'] is False and spec['meanings_validated'] is False, 'Claim ceiling')
    base = SHARED | BASE_R
    require(not ({'ol', *TAIL} & set(base)), 'Unknown words improperly mapped')
    rows, guard1 = query('transcription/voynich_zl3b_lines.tsv',
                        ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean'], pages)
    alternate, guard2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *READERS], pages)
    by = {r['locus']: r for r in rows}
    require(set(by) == {r['locus'] for r in alternate}, 'Reader coverage')
    for row in alternate:
        require(by[row['locus']]['page'] == row['page'] and by[row['locus']]['eva_clean'] == row[READERS[0]], 'Reader join')
        by[row['locus']].update({rd: row[rd] for rd in READERS})
    # Independently split each page's P stream; all non-P records remain separate.
    blocks = [[r] for r in rows if r['kind'] != 'P']
    for page in pages:
        prose = [r for r in rows if r['page'] == page and r['kind'] == 'P']
        if not prose:
            continue
        cuts = [0] + [i for i in range(1, len(prose)) if prose[i]['paragraph_start'] == '1' or
                      prose[i - 1]['paragraph_end'] == '1'] + [len(prose)]
        blocks += [prose[a:b] for a, b in zip(cuts, cuts[1:])]
    position = {r['locus']: i for i, r in enumerate(rows)}
    blocks.sort(key=lambda block: position[block[0]['locus']])
    require(sum(map(len, blocks)) == 1062, 'Global record conservation')
    block_for = {r['locus']: block for block in blocks for r in block}
    focal = [f'{page}.{i}' for page, start, end in PARAGRAPHS for i in range(start, end + 1)]
    for page, start, end in PARAGRAPHS:
        require([r['locus'] for r in block_for[f'{page}.{start}']] ==
                [f'{page}.{i}' for i in range(start, end + 1)], 'Complete focal source P')
    hits, tails = [], []
    tail_pairs = list(zip(TAIL, TAIL[1:]))
    for row in rows:
        for rd in READERS:
            words = row[rd].split()
            candidates = [(i, gap, 'CONTACT_DISTANCE_' + str(gap), gap)
                          for gap in (1, 2) for i, (a, b) in enumerate(zip(words, words[gap:]))
                          if (a, b) in [('chedy', 'qokain'), ('qokain', 'chedy')]]
            candidates += [(i, 3, 'EXACT_CHEDY_DUPLICATE', 1) for i, pair in enumerate(zip(words, words[1:]))
                           if pair == ('chedy', 'chedy')]
            for i, _, pattern, gap in sorted(candidates, key=lambda item: item[:2]):
                hits.append(dict(page=row['page'], locus=row['locus'], reader=rd, pattern=pattern,
                    first_ordinal=str(i + 1), last_ordinal=str(i + gap + 1), words_json=enc(words[i:i + gap + 1])))
            for i, pair in enumerate(zip(words, words[1:])):
                if pair in tail_pairs:
                    tails.append(dict(page=row['page'], locus=row['locus'], reader=rd, first_ordinal=str(i + 1),
                                      last_ordinal=str(i + 2), words_json=enc(list(pair))))
    trigger = {r['locus'] for r in hits}
    require(trigger == {'f72r3.26', 'f75r.16', 'f75r.22', 'f75r.33', 'f76r.23', 'f77r.35', 'f83r.16'} and
            len(hits) == 21 and len(tails) == 6 and {r['locus'] for r in tails} == {'f77r.35'}, 'Contact/tail coverage')
    selected = [b for b in blocks if any(r['locus'] in trigger | set(focal) for r in b)]
    require(len(selected) == 8 and sum(map(len, selected)) == 115, 'Selected complete context coverage')
    require(all(b[0]['kind'] != 'P' or b[0]['paragraph_start'] == b[-1]['paragraph_end'] == '1'
                for b in selected), 'Only selected P must have both boundaries')
    f76 = block_for['f76r.23']
    require(len(f76) == 29 and f76[0]['locus'] == 'f76r.1' and f76[-1]['locus'] == 'f76r.38' and
            all(r['kind'] == 'P' for r in f76), 'Interleaved labels split or entered the P stream')
    require(by['f77r.35'][READERS[2]].split()[4:] == ['sheedy', 'qotaiin', 'che', 'aiin', 'chealy'], 'RF tail smoothed')
    metadata, contexts, trials = [], [], []
    document = '# GDT818 complete comparison reader\n\nExact source paragraphs / entire non-P records; no decoded sentence boundaries.\nR wholes fixed; ol unknown. Four trial worlds are alternatives, not four votes.\n\n'

    def source_record(row):
        return {k: row[k] for k in ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end']} | {
            'readings_json': enc({rd: row[rd] for rd in READERS})}

    for block in selected:
        first, last = block[0], block[-1]
        bid = first['locus'] + '--' + last['locus']
        metadata.append(dict(block_id=bid, page=first['page'], kind=first['kind'], first=first['locus'],
            last=last['locus'], loci=str(len(block)), focal=str(int(first['locus'] in focal)),
            triggers_json=enc([r['locus'] for r in block if r['locus'] in trigger]),
            tokens_json=enc({rd: sum(len(r[rd].split()) for r in block) for rd in READERS})))
        document += '## ' + bid + '\n\n'
        for row in block:
            contexts.append({'block_id': bid} | source_record(row))
            document += row['locus'] + ' ZL: `' + row[READERS[0]] + '`\n'
            for rd in READERS[1:]:
                if row[rd] != row[READERS[0]]:
                    document += rd + ': `' + row[rd] + '`\n'
            document += '\n'
            if row['locus'] in focal:
                for rd in READERS:
                    for world, delta in WORLDS.items():
                        mapping = base | delta
                        trials.append(dict(page=row['page'], locus=row['locus'], reader=rd, world=world,
                            source_text=row[rd], literal_json=enc([mapping.get(w, '[' + w + ']') for w in row[rd].split()]),
                            confidence='C0_UNCONFIRMED'))
    tail_rows = [source_record(by['f77r.35'])]
    result = dict(experiment_id='GDT818', status='FIXED_FOUR_WORLDS_NOT_TRANSLATION', source_selectors=pages,
        source_loci=1062, focal_loci=35, literal_rows=420, context_blocks=8, context_loci=115, contact_rows=21,
        contact_loci=7, tail_pair_rows=6, tail_loci=1, guarded_queries=[guard1, guard2], fixed_senses=SENSES,
        sealed_data=['f84', 'f84r'], new_admissions=0, dictionary_changed=False, confirmed_lexemes=0,
        confirmed_plaintext_clauses=0, meanings_validated=False,
        selection_limit='SAME_RECORD_FIXED_DISTANCE_CONTACTS; NOT_ALL_CHEDY_OR_TAIL_SINGLETONS',
        literal_limit='FOCAL_35_LOCI_ONLY; CONTEXTS_AND_TAIL_ROWS_RETAIN_SOURCE_ALL_READERS')
    expected = [metadata, contexts, hits, tails, tail_rows, trials, document.rstrip() + '\n', result]
    actual = [read_tsv(EXP / 'artifacts' / name) for name in
              ['BLOCKS.tsv', 'CONTEXTS.tsv', 'HITS.tsv', 'TAIL_HITS.tsv', 'TAIL_ROWS.tsv', 'LITERAL_TRIALS.tsv']]
    actual += [(EXP / 'artifacts/FULL_READER.md').read_text(), json.loads((EXP / 'artifacts/RESULT.json').read_text())]
    continuation = [by[c['locus']] for c in alternate if
                    any(w in CONTINUATION_FOCUS for rd in READERS for w in c[rd].split())]
    continuation_trials = []
    for row in continuation:
        for rd in READERS:
            for proposal, mapping in CONTINUATION_MODELS.items():
                continuation_trials.append(dict(page=row['page'], locus=row['locus'], reader=rd, proposal=proposal,
                    source_text=row[rd], literal_json=enc([mapping.get(w, '[' + w + ']') for w in row[rd].split()]),
                    confidence='C0_COMPLETION_MOTIVATED_NOT_WORD_EVIDENCE'))
    require(len(continuation) == 29 and len(continuation_trials) == 174, 'Bounded continuation coverage')
    continuation_result = dict(experiment_id='GDT818', status='POST_READING_CONTINUATION_TRIALS',
        focus_wholes=CONTINUATION_FOCUS, proposals=CONTINUATION_MODELS, context_loci=29, literal_rows=174,
        guarded_queries=[guard1, guard2], scope_limit='WHOLE_ROWS_NOT_ALL_PARAGRAPHS_OR_QOKAIIN_SINGLETONS',
        meanings_validated=False, new_admissions=0, dictionary_changed=False, confirmed_lexemes=0,
        sealed_data=['f84', 'f84r'])
    expected += [[source_record(r) for r in continuation], continuation_trials, continuation_result]
    actual += [read_tsv(EXP / 'artifacts/CONTINUATION_CONTEXTS.tsv'),
               read_tsv(EXP / 'artifacts/CONTINUATION_TRIALS.tsv'),
               json.loads((EXP / 'artifacts/CONTINUATION_RESULT.json').read_text())]

    def audit(payload):
        require(payload == expected, 'Independent source/block/literal reconstruction differs')

    audit(actual)
    controls = []
    for name in ['WATER_ALIAS', 'DELETE_DOUBLET', 'CONTAINS_TO_FILLS', 'TRANSLATE_TAIL',
                 'DROP_NONFOCAL_CONTACT', 'EXTENSION_RF_ALIAS']:
        changed = copy.deepcopy(actual)
        if name == 'DELETE_DOUBLET':
            row = next(r for r in changed[1] if r['locus'] == 'f76r.23')
            readings = json.loads(row['readings_json'])
            readings[READERS[0]] = readings[READERS[0]].replace('chedy chedy', 'chedy', 1)
            row['readings_json'] = enc(readings)
        elif name == 'DROP_NONFOCAL_CONTACT':
            changed[2] = [r for r in changed[2] if r['locus'] != 'f75r.16']
        elif name == 'EXTENSION_RF_ALIAS':
            row = next(r for r in changed[9] if r['locus'] == 'f77r.35' and r['reader'] == READERS[2] and
                       r['proposal'] == 'IF_AIR_IS_COLD')
            row['literal_json'] = row['literal_json'].replace('[qotaiin]', 'Luft?', 1)
        else:
            row = next(r for r in changed[5] if r['locus'] == 'f77r.35' and r['world'] == 'B_CONTAINS')
            before, after = {'WATER_ALIAS': ('[qokaiin]', 'Wasser?'), 'CONTAINS_TO_FILLS': ('enthält?', 'füllt?'),
                             'TRANSLATE_TAIL': ('[sheedy]', 'beim Abkühlen?')}[name]
            row['literal_json'] = row['literal_json'].replace(before, after, 1)
        try:
            audit(changed)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('Negative mutation escaped: ' + name)
    gate_process = subprocess.run(['./vmanus-exp', 'check-edge-packet',
        str((EXP / 'src/RELATION_PACKET.tsv').relative_to(ROOT))], cwd=ROOT,
        capture_output=True, text=True, check=False)
    gate = json.loads(gate_process.stdout)
    require(gate_process.returncode != 0 and gate['status'] == 'INVALID_PACKET' and
            gate['packet_rows'] == 4 and gate['eligible_edges'] == 0 and gate['score_ready'] is False,
            'Expected unscorable four-alternative relation packet changed')
    require(gate_process.stdout == (EXP / 'artifacts/EDGE_GATE.json').read_text(),
            'Stored GDT388 JSON differs from independent CLI recomputation')
    validation = dict(experiment_id='GDT818', status='PASS', context_blocks=8, context_loci=115, focal_loci=35,
        literal_rows=420, contact_rows=21, contact_loci=7, tail_pair_rows=6, tail_loci=1,
        continuation_context_loci=29, continuation_literal_rows=174, continuation_models_separate_from_main=True,
        continuation_scope_all_qokaiin_or_complete_paragraphs=False,
        independent_raw_guarded_queries=True, runner_imported_or_called=False, negative_controls_rejected=controls,
        meanings_validated=False, historical_or_image_claims_validated=False, GDT388_gates_recomputed=True,
        GDT388_status='INVALID_PACKET', GDT388_eligible_edges=0, GDT388_score_ready=False)
    payload = json.dumps(validation, indent=2, sort_keys=True) + '\n'
    target = EXP / 'artifacts/VALIDATION.json'
    if args.check:
        require(target.read_text() == payload, 'Stored validation differs')
    else:
        target.write_text(payload)
    print('PASS: 8 blocks/115 loci/420 main trials; 29 continuation loci/174 trials; six mutations rejected; source only')


if __name__ == '__main__':
    main()

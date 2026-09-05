#!/usr/bin/env python3
"""Independent guarded-source reconstruction; never imports/executes the runner."""
import argparse
import copy
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file() and (p / '.git').exists())
ART = HERE.parent / 'artifacts'
OLD = 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json'
READERS = ['zl3b_clean', 'it2a_clean', 'rf1b_clean']
BASE = 'page,locus,line_number,kind,paragraph_start,paragraph_end,eva_clean'.split(',')
SHARED = dict(zip(['otchol', 'cthar', 'chol', 'dan', 'dain', 'daiin', 'daiiin'],
                  ['dieses?', 'Wurzel?', 'trocken?', 'sehr wenig?', 'wenig?', 'viel?', 'sehr viel?']))
MODELS = {m: {'okaiin': v} for m, v in zip('NGQR', ['Pulver?', 'ist?', 'warm?', 'dessen?'])}
BCOLS = 'page,block_id,kind,boundary_status,first_locus,last_locus,loci,target_loci,context_parent,selection'.split(',')
CCOLS = BASE + READERS + ['block_id', 'context_parent', 'boundary_status']
TCOLS = 'page,target_locus,kind,source_loci,reader,model,source_lines_json,literal_hypotheses_json,confidence'.split(',')


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def table(text):
    reader = csv.DictReader(io.StringIO(text), delimiter='\t')
    rows = list(reader)
    require(all(None not in r and None not in r.values() for r in rows), 'malformed TSV')
    return {'columns': reader.fieldnames, 'rows': rows}


def query(path, columns, selectors):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    command += [value for page in selectors for value in ('--allow', page)]
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    process = subprocess.run(command, cwd=ROOT, capture_output=True, check=True,
                             env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    require(process.stderr.startswith(b'GUARD_STATS '), 'missing guard statistics')
    projection = table(process.stdout.decode())
    require(projection['columns'] == columns, 'guard projection schema')
    require(json.loads(process.stderr[len(b'GUARD_STATS '):])['selected'] == len(projection['rows']), 'guard row count')
    return projection['rows'], {'command': command, 'projection_sha256': digest(process.stdout),
                               'stats': json.loads(process.stderr[len(b'GUARD_STATS '):])}


def independently_expected():
    old = json.loads((ROOT / OLD).read_text())
    selectors = old['source_selectors']
    require(len(selectors) == len(set(selectors)) == 39, 'inherited selector scope')
    require(not any(p.startswith('f84') for p in selectors), 'sealed selector')
    require(old['sealed_data'] == ['f84', 'f84r'], 'inherited seal')
    require(old['shared_hypotheses'] == SHARED, 'seven inherited whole-word hypotheses')
    require(old['models'] == {m: MODELS[m] for m in 'NG'}, 'unchanged N/G')
    require(old['complete_page'] == 'f17r' and old['confidence'] == 'C0_UNCONFIRMED', 'inherited full page/confidence')
    model_spec = dict(confidence='C0_UNCONFIRMED', models=MODELS, shared_source=OLD,
        reference_sense='ANAPHORIC_GENITIVE_POSSESSOR_NOT_PARTITIVE_OR_ORIGIN',
        quality_sense='WARM_PROPERTY_NOT_HEATED_ACTION_OR_HOT_III',
        card_selection='ANY_READER_EXACT_OKAIIN_LOCUS; PREFIX_PREVIOUS_P_LOCUS_IN_SAME_BLOCK_IF_TARGET_STARTS_ANY_READING',
        word_order='SOURCE_ORDER_ONE_JSON_ITEM_PER_TOKEN_UNKNOWN_BRACKETED', meanings_validated=False)
    source, g1 = query('transcription/voynich_zl3b_lines.tsv', BASE, selectors)
    alternate, g2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus'] + READERS, selectors)
    keys = lambda rows: [(r['page'], r['locus']) for r in rows]
    require(len(set(keys(source))) == len(source) and keys(source) == keys(alternate), 'source/alternate keys')
    require(set(r['page'] for r in source) == set(selectors), 'source scope coverage')
    for row, other in zip(source, alternate):
        require(row['eva_clean'] == other['zl3b_clean'], 'ZL source agreement')
        row.update({reader: other[reader] for reader in READERS})
    hit = lambda row: any('okaiin' in row[reader].split() for reader in READERS)
    spans, pending, previous_page = [], [], None
    def finish():
        if pending:
            spans.append(pending[:])
            pending.clear()
    for index, row in enumerate(source):
        if row['page'] != previous_page:
            finish()
        previous_page = row['page']
        if row['kind'] == 'P':
            if row['paragraph_start'] == '1':
                finish()
            pending.append(index)
            if row['paragraph_end'] == '1':
                finish()
        else:
            if row['kind'] != 'L':
                finish()
            spans.append([index])
    finish()
    spans.sort(key=lambda span: span[0])
    chosen = [s for s in spans if source[s[0]]['page'] == 'f17r' or any(hit(source[i]) for i in s)]
    parents = {}
    for span in chosen[:]:
        if source[span[0]]['kind'] == 'P':
            for index in range(span[0] + 1, span[-1]):
                if source[index]['kind'] == 'L':
                    parents[index] = f"{source[span[0]]['locus']}--{source[span[-1]]['locus']}"
                    if [index] not in chosen:
                        chosen.append([index])
    chosen.sort(key=lambda span: span[0])
    blocks, contexts, trials, cards, target_loci = [], [], [], [], []
    md = ['# GDT814 complete source-block reader', '',
          'Exploratory source text, not a translation. ZL3b is printed in full;',
          'every differing alternate line follows. TSV retains all three readings.',
          'Interleaved L records stay separate from the source-flagged prose stream.', '']
    for span in chosen:
        rows = [source[i] for i in span]
        first, last = rows[0], rows[-1]
        block_id = first['locus'] + '--' + last['locus']
        boundary = ('SOURCE_PARAGRAPH_BOTH_MARKED' if first['paragraph_start'] == last['paragraph_end'] == '1'
                    else 'SOURCE_BLOCK_BOUNDARY_INCOMPLETE') if first['kind'] == 'P' else 'NON_P_RECORD'
        targets = [r['locus'] for r in rows if hit(r)]
        parent = parents.get(span[0], '')
        selection = 'FULL_F17R' if first['page'] == 'f17r' else ('ANY_READER_EXACT_OKAIIN' if targets else 'INTERLEAVED_L_CONTEXT')
        values = [first['page'], block_id, first['kind'], boundary, first['locus'], last['locus'],
                  str(len(rows)), ','.join(targets), parent, selection]
        blocks.append(dict(zip(BCOLS, values)))
        contexts.extend(dict(r, block_id=block_id, boundary_status=boundary, context_parent=parent) for r in rows)
        md += [f"## {block_id} [{first['kind']}; {boundary}]", '', '```text']
        md += [f"{r['locus']}  {r['zl3b_clean']}" for r in rows] + ['```', '']
        differences = [f"- {r['locus']} {reader}: `{r[reader]}`" for r in rows
                       for reader in READERS[1:] if r[reader] != r['zl3b_clean']]
        if differences:
            md += differences + ['']
        if parent:
            md += [f'Separate L record interleaved in source ordering within {parent}.', '']
        for position, row in enumerate(rows):
            if not hit(row):
                continue
            target_loci.append(row['locus'])
            prefix = row['kind'] == 'P' and position > 0 and any(row[r].split()[:1] == ['okaiin'] for r in READERS)
            card = rows[position - 1:position + 1] if prefix else [row]
            loci = [r['locus'] for r in card]
            cards.append(dict(target_locus=row['locus'], source_loci=loci))
            for reader in READERS:
                lines = [r[reader] for r in card]
                for model, additions in MODELS.items():
                    lexicon = dict(SHARED, **additions)
                    literal = [lexicon.get(token, f'[{token}]') for line in lines for token in line.split()]
                    values = [row['page'], row['locus'], row['kind'], ','.join(loci), reader, model,
                              json.dumps(lines, ensure_ascii=False), json.dumps(literal, ensure_ascii=False), 'C0_UNCONFIRMED']
                    trials.append(dict(zip(TCOLS, values)))
    incomplete = [b['block_id'] for b in blocks if b['kind'] == 'P' and b['boundary_status'] != 'SOURCE_PARAGRAPH_BOTH_MARKED']
    interleaved = [source[i]['locus'] for i in sorted(parents)]
    result = dict(experiment_id='GDT814', status='COMPLETE_SOURCE_BLOCKS_NOT_SEMANTIC_VALIDATION',
        source_selectors=selectors, visual_page_keys=34, source_loci=len(source), source_blocks=len(spans),
        selected_blocks=len(blocks), selected_prose_blocks=sum(b['kind'] == 'P' for b in blocks),
        selected_loci=len(contexts), boundary_incomplete_blocks=incomplete, exact_okaiin_loci_any_reader=target_loci,
        construction_cards=cards, interleaved_L_context_records=interleaved, literal_trial_rows=len(trials),
        guarded_queries=[g1, g2], new_admissions=0, sealed_data=['f84', 'f84r'], meanings_validated=False,
        confirmed_lexemes=0, confirmed_plaintext_clauses=0, dictionary_changed=False,
        alternate_readings_not_independent_witnesses=True)
    require((len(spans), len(blocks), len(contexts), len(cards), len(trials)) == (513, 37, 176, 30, 360), 'declared count regression')
    require(result['selected_prose_blocks'] == 20 and len(interleaved) == 9 and not incomplete, 'paragraph/label separation')
    return {'BLOCKS.tsv': {'columns': BCOLS, 'rows': blocks}, 'CONTEXTS.tsv': {'columns': CCOLS, 'rows': contexts},
            'LITERAL_TRIALS.tsv': {'columns': TCOLS, 'rows': trials}, 'SOURCE_READER.md': '\n'.join(md),
            'RESULT.json': result, 'MODEL_SPEC.json': model_spec}


def compare(actual, expected):
    require(actual.keys() == expected.keys(), 'artifact inventory')
    for name in expected:
        require(packed(actual[name]) == packed(expected[name]), f'{name}: independent reconstruction differs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify without writing any file')
    args = parser.parse_args()
    expected = independently_expected()
    paths = {name: (HERE if name == 'MODEL_SPEC.json' else ART) / name for name in expected}
    actual = {n: table(p.read_text()) if n.endswith('.tsv') else
              (json.loads(p.read_text()) if n.endswith('.json') else p.read_text()) for n, p in paths.items()}
    compare(actual, expected)
    negatives = []
    for name in ['F76R_PROSE_FRAGMENT', 'REFERENCE_CHANGED_TO_PARTITIVE', 'RF_VARIANT_SMOOTHED']:
        damaged = copy.deepcopy(actual)
        if name == 'F76R_PROSE_FRAGMENT':
            b = next(b for b in damaged['BLOCKS.tsv']['rows'] if b['block_id'] == 'f76r.1--f76r.38')
            b.update(first_locus='f76r.11', last_locus='f76r.13', loci='3')
        elif name == 'REFERENCE_CHANGED_TO_PARTITIVE':
            damaged['MODEL_SPEC.json']['models']['R']['okaiin'] = 'davon?'
        else:
            r = next(r for r in damaged['CONTEXTS.tsv']['rows'] if r['locus'] == 'f81v.5')
            require(r['rf1b_clean'] != r['zl3b_clean'], 'RF negative-test must alter data')
            r['rf1b_clean'] = r['zl3b_clean']
        try:
            compare(damaged, expected)
        except AssertionError:
            negatives.append({'test': name, 'rejected': True})
        else:
            raise AssertionError(f'negative test accepted: {name}')
    blanks = [{'locus': r['locus'], 'reader': reader} for r in expected['CONTEXTS.tsv']['rows']
              for reader in READERS if r[reader] == '']
    require(blanks, 'empty alternate reading must be retained and tested')
    report = dict(experiment_id='GDT814', status='PASS_SOURCE_AND_SOFTWARE_CHECKS_ONLY', meanings_validated=False,
        independent_of_runner=True, fresh_guarded_queries=2, selected_blocks=37, selected_prose_blocks=20,
        selected_nonprose_blocks=17, selected_loci=176, construction_cards=30, literal_trial_rows=360,
        exact_artifact_checks=list(expected), empty_readings_preserved=blanks, negative_tests=negatives,
        artifact_sha256={n: digest(p.read_bytes()) for n, p in paths.items()},
        validator_sha256=digest(Path(__file__).read_bytes()), inherited_spec_sha256=digest((ROOT / OLD).read_bytes()))
    destination = ART / 'VALIDATION.json'
    if args.check:
        require(destination.exists() and packed(json.loads(destination.read_text())) == packed(report), 'VALIDATION.json stale/missing')
    else:
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': report['status'], 'negative_tests_rejected': len(negatives), 'check_only': args.check}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

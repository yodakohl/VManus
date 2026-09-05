#!/usr/bin/env python3
"""Expand exact okaiin contexts to source blocks; preserve all alternate readings."""
import argparse
import csv
import importlib.util
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
PRIOR = ROOT / 'experiments/yolo/gdt813_f17_content_word_transfer'
loader = importlib.util.spec_from_file_location('gdt812_query', ROOT /
    'experiments/yolo/gdt812_additional_page_semantic_bridge/src/family_probe.py')
guard = importlib.util.module_from_spec(loader)
loader.loader.exec_module(guard)
READERS = ['zl3b_clean', 'it2a_clean', 'rf1b_clean']
META = ['page', 'locus', 'line_number', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean']


def tsv(rows, columns):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def build():
    prior = json.loads((PRIOR / 'src/SPEC.json').read_text())
    pages = prior['source_selectors']
    guard.require(len(set(pages)) == 39 and prior['sealed_data'] == ['f84', 'f84r'] and
                  not any(p.startswith('f84') for p in pages), 'Scope/seals differ')
    rows, base_guard = guard.query('transcription/voynich_zl3b_lines.tsv', META, pages)
    alts, cross_guard = guard.query('transcription/voynich_cross_transcription_lines.tsv',
                                   ['page', 'locus', *READERS], pages)
    cross = {r['locus']: r for r in alts}
    guard.require(set(cross) == {r['locus'] for r in rows}, 'Alternate coverage')
    for row in rows:
        other = cross[row['locus']]
        guard.require(other['page'] == row['page'] and other['zl3b_clean'] == row['eva_clean'], 'Reader join')
        row.update({r: other[r] for r in READERS})
    blocks, current = [], []
    for row in rows:
        if current and (row['page'] != current[-1]['page'] or row['kind'] not in ('P', 'L')
                        or (row['kind'] == 'P' and row['paragraph_start'] == '1')):
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
    guard.require(sum(map(len, blocks)) == len(rows), 'Block conservation')
    order = {r['locus']: i for i, r in enumerate(rows)}
    blocks.sort(key=lambda b: order[b[0]['locus']])
    selected_prose = [b for b in blocks if b[0]['kind'] == 'P' and
                      (b[0]['page'] == 'f17r' or any('okaiin' in r[k].split()
                       for r in b for k in READERS))]
    kept, inventory, reader = [], [], ['# GDT814 complete source-block reader', '',
        'Exploratory source text, not a translation. ZL3b is printed in full;',
        'every differing alternate line follows. TSV retains all three readings.',
        'Interleaved L records stay separate from the source-flagged prose stream.', '']
    for block in blocks:
        hits = [r['locus'] for r in block if any('okaiin' in r[k].split() for k in READERS)]
        parent = next((b[0]['locus'] + '--' + b[-1]['locus'] for b in selected_prose
                       if block[0]['kind'] == 'L' and b[0]['page'] == block[0]['page'] and
                       order[b[0]['locus']] < order[block[0]['locus']] < order[b[-1]['locus']]), '')
        if not hits and block[0]['page'] != 'f17r' and not parent:
            continue
        first, last = block[0], block[-1]
        key = first['locus'] + '--' + last['locus']
        boundary = ('NON_P_RECORD' if first['kind'] != 'P' else
                    'SOURCE_PARAGRAPH_BOTH_MARKED' if first['paragraph_start'] == last['paragraph_end'] == '1'
                    else 'SOURCE_BLOCK_BOUNDARY_INCOMPLETE')
        entry = {'page': first['page'], 'block_id': key, 'kind': first['kind'], 'boundary_status': boundary,
                 'first_locus': first['locus'], 'last_locus': last['locus'], 'loci': len(block),
                 'selection': 'FULL_F17R' if first['page'] == 'f17r' else
                              'ANY_READER_EXACT_OKAIIN' if hits else 'INTERLEAVED_L_CONTEXT',
                 'target_loci': ','.join(hits), 'context_parent': parent}
        inventory.append(entry)
        kept.extend(dict(r, block_id=key, boundary_status=boundary, context_parent=parent) for r in block)
        reader.extend(['## ' + key + ' [' + first['kind'] + '; ' + boundary + ']', '', '```text'])
        reader.extend(r['locus'] + '  ' + r['zl3b_clean'] for r in block)
        reader.extend(['```', ''])
        differences = [r['locus'] + ' ' + alt + ': `' + r[alt] + '`'
                       for r in block for alt in READERS[1:] if r[alt] != r['zl3b_clean']]
        if differences:
            reader.extend('- ' + d for d in differences)
            reader.append('')
        if parent:
            reader.extend(['Separate L record interleaved in source ordering within ' + parent + '.', ''])
    model_spec = json.loads((EXP / 'src/MODEL_SPEC.json').read_text())
    guard.require(model_spec['models'] == {'N': {'okaiin': 'Pulver?'}, 'G': {'okaiin': 'ist?'},
                  'Q': {'okaiin': 'warm?'}, 'R': {'okaiin': 'dessen?'}}, 'Declared models changed')
    trials, cards = [], []
    for index, row in enumerate(kept):
        if not any('okaiin' in row[r].split() for r in READERS):
            continue
        window = [row]
        if row['kind'] == 'P' and index and kept[index - 1]['block_id'] == row['block_id'] and any(
                row[r].split()[:1] == ['okaiin'] for r in READERS):
            window.insert(0, kept[index - 1])
        cards.append({'target_locus': row['locus'], 'source_loci': [r['locus'] for r in window]})
        for alt in READERS:
            words = [w for line in window for w in line[alt].split()]
            for model, specific in model_spec['models'].items():
                mapping = prior['shared_hypotheses'] | specific
                trials.append({'page': row['page'], 'target_locus': row['locus'], 'kind': row['kind'],
                    'source_loci': ','.join(r['locus'] for r in window), 'reader': alt, 'model': model,
                    'source_lines_json': json.dumps([r[alt] for r in window], ensure_ascii=False),
                    'literal_hypotheses_json': json.dumps([mapping.get(w, '[' + w + ']') for w in words],
                                                         ensure_ascii=False),
                    'confidence': model_spec['confidence']})
    report = {'experiment_id': 'GDT814', 'status': 'COMPLETE_SOURCE_BLOCKS_NOT_SEMANTIC_VALIDATION',
              'source_selectors': pages, 'visual_page_keys': 34, 'source_loci': len(rows),
              'source_blocks': len(blocks), 'selected_blocks': len(inventory), 'selected_loci': len(kept),
              'selected_prose_blocks': sum(e['kind'] == 'P' for e in inventory),
              'construction_cards': cards, 'literal_trial_rows': len(trials),
              'interleaved_L_context_records': [e['first_locus'] for e in inventory if e['context_parent']],
              'boundary_incomplete_blocks': [e['block_id'] for e in inventory
                                            if e['boundary_status'] == 'SOURCE_BLOCK_BOUNDARY_INCOMPLETE'],
              'exact_okaiin_loci_any_reader': [r['locus'] for r in kept
                                             if any('okaiin' in r[k].split() for k in READERS)],
              'guarded_queries': [base_guard, cross_guard], 'sealed_data': ['f84', 'f84r'],
              'alternate_readings_not_independent_witnesses': True, 'new_admissions': 0,
              'meanings_validated': False, 'dictionary_changed': False,
              'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0}
    block_columns = [k for k in inventory[0] if k != 'selection'] + ['selection']
    return {'BLOCKS.tsv': tsv(inventory, block_columns),
            'CONTEXTS.tsv': tsv(kept, META + READERS + ['block_id', 'context_parent', 'boundary_status']),
            'LITERAL_TRIALS.tsv': tsv(trials, list(trials[0])),
            'SOURCE_READER.md': '\n'.join(reader).rstrip() + '\n',
            'RESULT.json': json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n'}, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    payloads, report = build()
    for name, content in payloads.items():
        path = EXP / 'artifacts' / name
        if args.check:
            guard.require(path.read_text() == content, 'Replay differs: ' + name)
        else:
            path.write_text(content)
    print(json.dumps({k: report[k] for k in ['status', 'selected_blocks', 'selected_loci',
          'selected_prose_blocks', 'boundary_incomplete_blocks']}))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Retain all exact content-word contexts and two literal hypothetical displays."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
UPSTREAM = ROOT / 'experiments/yolo/gdt812_additional_page_semantic_bridge'
module_spec = importlib.util.spec_from_file_location('gdt812_guard_helper', UPSTREAM / 'src/family_probe.py')
guard = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(guard)
READERS = ['zl3b_clean', 'it2a_clean', 'rf1b_clean']
META = ['page', 'locus', 'line_number', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean']


def tsv(rows, fields):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    with (ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv').open() as handle:
        old = list(csv.DictReader(handle, delimiter='\t'))
    with (UPSTREAM / 'src/PAGE_ADMISSIONS.tsv').open() as handle:
        extra = list(csv.DictReader(handle, delimiter='\t'))
    pages = [r['source_selector'] for r in old + extra]
    guard.require(pages == spec['source_selectors'] and len(set(pages)) == 39, 'Admission selectors differ')
    guard.require(len({r['physical_page'] for r in old + extra}) == 34, 'Visual page-key count')
    guard.require(all(r['decision'] == 'ADMITTED' for r in extra), 'Extra admission is not recorded')
    guard.require(spec['sealed_data'] == ['f84', 'f84r'] and not any(p.startswith('f84') for p in pages), 'Sealed selector')
    rows, provenance = guard.query('transcription/voynich_zl3b_lines.tsv', META, pages)
    alternate, cross_provenance = guard.query('transcription/voynich_cross_transcription_lines.tsv',
                                             ['page', 'locus', *READERS], pages)
    cross = {r['locus']: r for r in alternate}
    guard.require(set(cross) == {r['locus'] for r in rows}, 'Reader locus coverage')
    for row in rows:
        variant = cross[row['locus']]
        guard.require(variant['page'] == row['page'] and variant['zl3b_clean'] == row['eva_clean'], 'Reader join')
        row.update({r: variant[r] for r in READERS})
    contexts = [row for row in rows if row['page'] == spec['complete_page'] or
                any(word in spec['target_wholes'] for reader in READERS for word in row[reader].split())]
    displays = []
    for row in contexts:
        for reader in READERS:
            words = row[reader].split()
            for model, specific in spec['models'].items():
                mapping = spec['shared_hypotheses'] | specific
                displays.append({'page': row['page'], 'locus': row['locus'], 'kind': row['kind'],
                                 'reader': reader, 'model': model, 'source_text': row[reader],
                                 'tokens': len(words), 'hypothesis_positions_1based': ','.join(str(i + 1)
                                  for i, word in enumerate(words) if word in mapping),
                                 'literal_hypotheses_json': json.dumps([mapping.get(w, '[' + w + ']')
                                   for w in words], ensure_ascii=False), 'confidence': spec['confidence']})
    counts = {r: {w: sum(row[r].split().count(w) for row in rows) for w in spec['target_wholes']} for r in READERS}
    local = [{key: row[key] for key in ['page', 'locus', 'kind', *READERS]} for row in contexts
             if row['kind'] != 'P' and any('okaiin' in row[r].split() for r in READERS)]
    result = {'experiment_id': 'GDT813', 'status': 'CONTEXT_AND_LITERAL_DISPLAY_ONLY',
              'design_timing': spec['design_timing'], 'source_selectors': pages, 'visual_page_keys': 34,
              'source_loci': len(rows), 'context_loci': len(contexts), 'display_rows': len(displays),
              'complete_f17r_loci': [row['locus'] for row in contexts if row['page'] == 'f17r'],
              'counts_by_alternate_reading': counts, 'non_P_okaiin_contexts': local,
              'guarded_queries': [provenance, cross_provenance],
              'spec_sha256': hashlib.sha256((EXP / 'src/SPEC.json').read_bytes()).hexdigest(),
              'new_admissions': 0, 'meanings_validated': False, 'dictionary_changed': False,
              'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0,
              'selection_limit': 'Full f17r plus whole matching loci elsewhere; not full external paragraphs.',
              'alternate_readings_not_independent_witnesses': True, 'sealed_data': spec['sealed_data']}
    return {'CONTEXTS.tsv': tsv(contexts, META + READERS),
            'LITERAL_TRIALS.tsv': tsv(displays, list(displays[0])),
            'RESULT.json': json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n'}, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    payloads, result = build()
    for name, payload in payloads.items():
        target = EXP / 'artifacts' / name
        if args.check:
            guard.require(target.is_file() and target.read_text() == payload, 'Replay differs: ' + name)
        else:
            target.write_text(payload)
    print(json.dumps({key: result[key] for key in ('status', 'context_loci', 'display_rows', 'counts_by_alternate_reading')}))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Fixed seven-locus projection and exact whole-form capacity; no semantics."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DECISION = 'research_registry/decisions/idea521_embedded_pair_development_decision_20260922.md'
OLD = 'experiments/yolo/gdt1026_rota_crossleaf_frozen_meanings/src/SOURCE.json'
LOCUS = ['f83r.47', 'f83r.48', 'f83r.49', 'f83r.52', 'f83r.53', 'f83r.54', 'f83r.55']
UNITS = {'F83_Q1': LOCUS[:3], 'F83_Q2': LOCUS[3:]}


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main():
    # Persist decision and input bindings before selecting any target bodies.
    paths = [f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{reader}.json'
             for reader in ['ZL3b', 'IT2a', 'RF1b'] for split in ['DISCOVERY', 'EVALUATION']]
    bindings = {path: sha(path) for path in [DECISION, OLD, *paths]}
    write('EXTRACTION_RECEIPT.json', {
        'status': 'EXPLORATORY_PREDECLARED_COMPLETE_PAIRED_SCOPE',
        'selected_loci': LOCUS, 'units': UNITS,
        'source_bindings': bindings,
        'new_values_cap': 8, 'production_cap': 2, 'binding_cap': 4,
        'alias_cap': 0, 'group_packing_cap': 0,
        'sealed': ['f84', 'f84r'], 'new_admission': False,
        'prior_project_exposure': True, 'independent_confirmation_capacity': 0,
        'RF1b_boundary': 'Externally bounded same-locus projection; no RF paragraph flags.'})
    old = json.loads((ROOT / OLD).read_text())
    lexicon = old['frozen_family']['all71_entries_unchanged'] | old['new20_lexicon']
    assert len(lexicon) == 91
    write('FROZEN_LEXICON.json', lexicon)
    source, capacity = {}, {}
    for reader in ['ZL3b', 'IT2a', 'RF1b']:
        selected = {}
        for split in ['DISCOVERY', 'EVALUATION']:
            path = f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{reader}.json'
            data = json.loads((ROOT / path).read_text())
            for line in data['lines']:
                meta = line['metadata']
                if meta['page'] != 'f83r' or meta['locus'] not in LOCUS:
                    continue
                assert meta['locus'] not in selected
                selected[meta['locus']] = {'metadata': meta, 'groups': [dict(zip(data['group_columns'], row)) for row in line['groups']]}
        assert set(selected) == set(LOCUS)
        source[reader] = [selected[locus] for locus in LOCUS]
        words = [g['ivtff_group_raw'] for line in source[reader] for g in line['groups']]
        counts = collections.Counter(words)
        unknown = {word: count for word, count in sorted(counts.items()) if word not in lexicon}
        capacity[reader] = {'groups': len(words), 'types': len(counts),
            'known_positions': sum(count for word, count in counts.items() if word in lexicon),
            'known_types': len(set(words) & set(lexicon)),
            'new_whole_types_required': len(unknown), 'unknown_occurrences': unknown,
            'fits_eight_new_values': len(unknown) <= 8,
            'scope': 'two whole records' if reader != 'RF1b' else 'external same-locus projection'}
    write('SOURCE.json', source)
    write('CAPACITY.json', capacity)
    print(json.dumps(capacity, indent=2))
    for reader, lines in source.items():
        for line in lines:
            print(reader, line['metadata']['locus'], ' '.join(g['ivtff_group_raw'] for g in line['groups']))


if __name__ == '__main__':
    main()

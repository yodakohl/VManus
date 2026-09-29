#!/usr/bin/env python3
"""Validate S document copies and receipts; never execute a meaning hypothesis."""
from pathlib import Path
from collections import Counter
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    receipt = json.loads((HERE / 'S_RECEIPTS.json').read_text())
    for item in receipt['sources'] + receipt['outputs']:
        path = ROOT / item['path']
        assert path.is_file(), item['path']
        assert digest(path) == item['sha256'], item['path']
        assert path.stat().st_size == item['bytes'], item['path']
    copy = json.loads((HERE / 'S_CLOCK_COMPLETE_ACCOUNT.json').read_text())
    source = json.loads((ROOT / copy['source']['path']).read_text())
    assert digest(ROOT / copy['source']['path']) == copy['source']['sha256']
    for key, value in copy['copied_fields'].items():
        assert value == source[key], key
    target = source['selected_target']
    zl = target['full_record']
    it = target['alternatives']['IT2a'][0]
    zl_words = [w for line in zl['lines'] for w in line['words']]
    it_words = [w for line in it['lines'] for w in line['words']]
    assert len(zl_words) == zl['groups'] == 40
    assert len(it_words) == it['groups'] == 42
    assert len(set(zl_words)) == len(source['lexicon']) == 33
    assert sum(n == 1 for n in Counter(zl_words).values()) == 27
    assert target['alternatives']['RF1b'] == []
    lex = {x['form']: x for x in source['lexicon']}
    assert set(lex) == set(zl_words)
    for form, item in lex.items():
        assert item['positions'] == [i + 1 for i, w in enumerate(zl_words) if w == form]
    consumed = []
    for production in source['whole_paragraph_productions']:
        positions = production['positions']
        assert production['raw_words'] == [zl_words[i - 1] for i in positions]
        assert production['value_sequence'] == [lex[zl_words[i - 1]]['value'] for i in positions]
        consumed.extend(positions)
    assert sorted(consumed) == list(range(1, 41))
    assert len(source['binding_assumptions']) == 20
    preflight = json.loads((HERE / 'S_DOM_PREFLIGHT.json').read_text())
    assert preflight['input'] == copy['source']
    expected_y = [x for x in source['lexicon'] if x['form'].endswith('y')]
    assert [x['base'] for x in preflight['y_rows']] == expected_y
    assert len(expected_y) == 9
    for row in preflight['y_rows']:
        predicted = row['base']['form'][:-1] + 'aiin'
        assert row['predicted_surface'] == predicted
        assert row['present_in_fixed33'] == (predicted in lex)
        assert row['fixed33_counterpart'] == lex.get(predicted)
    assert [x['base']['form'] for x in preflight['y_rows'] if x['collection_return_selected']] == ['shckhy', 'chckhy', 'alolshey']
    assert [x['predicted_surface'] for x in preflight['y_rows'] if x['present_in_fixed33']] == ['chckhaiin']
    assert preflight['other_aiin_entries_left_atomic'] == [lex[x] for x in ['aiin', 'qokaiin', 'chaiin']]
    result = {
        'status': 'PASS_DOCUMENT_INTEGRITY_ONLY',
        'source_files_bound': len(receipt['sources']),
        'output_files_bound': len(receipt['outputs']),
        'clock_groups': {'ZL3b': 40, 'IT2a': 42, 'RF1b': 'NO_WHOLE_RECORD'},
        'clock_exact_forms': 33,
        'clock_singletons': 27,
        'old_productions': 4,
        'old_bindings': 20,
        'fixed_inventory_y_forms': 9,
        'selected_collection_return_types': 3,
        'paired_counterparts_within_fixed33': ['chckhaiin'],
        'outside_inventory_surface_comparison': 'NOT_PERFORMED',
        'meaning_tests': 0,
        'confirmed_meanings': 0,
        'claim_ceiling': 'Literal document copying and supplied inventory only; no semantic derivation, new corpus census, historical proof or independent corroboration.'
    }
    (HERE / 'S_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()

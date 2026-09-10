#!/usr/bin/env python3
"""Audit source geometry/pixels and retention of uncertainty, not palaeography."""
import argparse
import hashlib
import json
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-source', type=Path,
                        help='Optional original public JPEG; verifies actual crop pixels.')
    args = parser.parse_args()
    get = lambda name: json.loads((BASE / name).read_text())
    native = get('artifacts/NATIVE_SOURCE.json')
    localization = get('artifacts/LOCALIZATION_CORRECTION.json')
    result = get('artifacts/RESULT.json')
    panels = localization['panels']
    assert localization['source_sha256'] == native['source_sha256']
    assert localization['prior_crop_status'] == 'INPUT_CROP_MISLOCALIZED'
    expected_boxes = [[3300, 850, 4600, 2500], [3300, 2500, 4600, 4200],
                      [3300, 4200, 4600, 5900], [3300, 5900, 4600, 7500]]
    assert [p['source_box'] for p in panels] == expected_boxes
    assert result['published_display_rows'] == 24
    assert result['published_question_mark_only_middle_labels'] == ['m', 'n', 'q']
    for field in ('body_paragraphs_queried', 'progressive_key_cases_tested',
                  'confirmed_meanings', 'native_complete_tables'):
        assert result[field] == 0
    assert result['native_ordinal_row_count'] is None
    assert result['hypothesis_refuted'] is False
    a, b = get('src/READER_A_LOCALIZED.json'), get('src/READER_B_LOCALIZED.json')
    assert {r['display_row'] for r in a['rows']} == set(range(1, 25))
    assert {r['published_slot'] for r in b['rows']} == set(range(1, 25))
    assert all(r['fixed_eva'] is None for r in a['rows'])
    assert all(r['accepted_eva'] is None for r in b['rows'])
    assert not a['complete_single_valued_table'] and not b['complete_single_valued_table']
    from PIL import Image
    for p in panels:
        path = ROOT / p['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == p['sha256']
        with Image.open(path) as im:
            x0, y0, x1, y1 = p['source_box']
            assert im.size == (x1-x0, y1-y0)
    checked = 0
    if args.native_source:
        assert hashlib.sha256(args.native_source.read_bytes()).hexdigest() == native['source_sha256']
        with Image.open(args.native_source) as original:
            assert list(original.size) == native['source_size']
            for p in panels:
                with Image.open(ROOT / p['path']) as published:
                    crop = original.crop(p['source_box'])
                    assert crop.mode == published.mode
                    assert crop.tobytes() == published.tobytes()
                    checked += 1
    validation = {
        'status': 'PASS', 'scope': 'source hashes, registered crop geometry, retained uncertainty and conditional stop',
        'original_pixel_panels_checked': checked,
        'palaeography_validation': 'manual reader records, not established by this script',
        'software_independence': 'separate check code by root; native reading B independent of root reading',
        'meaning_validation': 'NOT_TESTED'
    }
    print(json.dumps(validation))
    target = BASE / 'artifacts/VALIDATION.json'
    if checked or not target.exists():
        target.write_text(json.dumps(validation, indent=2) + '\n')

if __name__ == '__main__':
    main()

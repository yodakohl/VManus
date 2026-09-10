#!/usr/bin/env python3
"""Replay the source checkpoint. No body-text loader or decoder exists here."""
import hashlib
import json
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]

def read(relative):
    return json.loads((BASE / relative).read_text())

def main():
    source_records = read('artifacts/SOURCE_MANIFEST.json')
    source_records += read('artifacts/LOCALIZATION_CORRECTION.json')['panels']
    for record in source_records:
        path = ROOT / record['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], path.name
    a = read('src/READER_A_LOCALIZED.json')
    b = read('src/READER_B_LOCALIZED.json')
    editorial = read('src/READER_B.json')['rows']
    assert [r['display_row'] for r in editorial] == list(range(1, 25))
    assert len(a['rows']) == len(b['rows']) == 24
    assert not a['complete_single_valued_table']
    assert not b['complete_single_valued_table']
    result = {
        'experiment': 'GDT912',
        'status': 'SOURCE_TABLE_INCOMPLETE_NO_BODY_TEST',
        'article_figures_verified': 3,
        'corrected_native_panels_verified': 4,
        'published_display_rows': len(editorial),
        'published_question_mark_only_middle_labels': [
            r['published_left'] for r in editorial
            if r['published_middle_description'] == 'printed question mark only'],
        'native_complete_tables': 0,
        'native_ordinal_row_count': None,
        'readers': ['A/root', 'B'],
        'reader_independence_limit': 'Both exposed to the same published reconstruction; independent judgments, not blind rediscovery.',
        'prior_crop_status': read('artifacts/LOCALIZATION_CORRECTION.json')['prior_crop_status'],
        'body_paragraphs_queried': 0,
        'progressive_key_cases_tested': 0,
        'confirmed_meanings': 0,
        'hypothesis_refuted': False,
        'interpretation': 'Missing source table and meaning binding; not negative evidence from a completed cipher test.'
    }
    (BASE / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()

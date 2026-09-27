#!/usr/bin/env python3
"""Validate intake receipts, not historical readings or semantic truth."""
import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def check_receipt(receipt):
    relative = Path(receipt['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    data = (BASE / relative).read_bytes()
    assert len(data) == receipt['bytes'], str(relative)
    assert hashlib.sha256(data).hexdigest() == receipt['sha256'], str(relative)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-sources', action='store_true')
    args = parser.parse_args()
    packet = json.loads((BASE / 'HISTORICAL_EXPECTATIONS_RESULT_20260927.json').read_text())
    for receipt in packet['bound_public_files']:
        check_receipt(receipt)
    review = json.loads((BASE / 'HISTORICAL_EXPECTATIONS_REVIEW_20260927.json').read_text())
    assert review['required_corrections'] == []
    for receipt in review['reviewed_artifacts']:
        relative = Path(receipt['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        report = BASE.parents[2] / relative
        assert hashlib.sha256(report.read_bytes()).hexdigest() == receipt['sha256']
    assert len(packet['selected_entries']) == 3
    assert packet['new_external_folio_images'] == 2
    assert packet['new_target_admissions'] == []
    assert packet['confirmed_words'] == 0
    assert packet['wider_witness_search_selected'] is False
    if args.local_sources:
        for receipt in packet['local_source_receipts']:
            check_receipt(receipt)
        chapter = packet['megenberg_chapter']
        source = (BASE / chapter['source_path']).read_text()
        a, b = chapter['unicode_character_bounds']
        fragment = source[a:b]
        assert fragment.startswith('Chapter / Strophe: 48')
        assert 'Mandragora' in fragment and 'Chapter / Strophe:' not in fragment[1:]
        assert source[b:].startswith('Chapter / Strophe: 49')
        assert hashlib.sha256(fragment.encode()).hexdigest() == chapter['html_fragment_sha256']
    print(json.dumps({'status': 'PASS_RECEIPT_INTEGRITY_ONLY',
                      'public_receipts': len(packet['bound_public_files']),
                      'local_source_receipts_checked': len(packet['local_source_receipts']) if args.local_sources else 0,
                      'limit': 'No mechanical proof of readings, visual ownership, exposure history or meanings.'}, indent=2))


if __name__ == '__main__':
    main()

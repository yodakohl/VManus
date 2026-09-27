#!/usr/bin/env python3
"""Check bound intake receipts; cannot validate visual truth or translation."""
import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-sources', action='store_true')
    args = parser.parse_args()
    packet = json.loads((BASE / 'DIAGRAM_RELATION_SOURCE_INTAKE_RESULT_20260927.json').read_text())
    checked = []
    for receipt in packet['bound_public_files']:
        path = BASE / receipt['path']
        assert path.is_relative_to(BASE) and '..' not in Path(receipt['path']).parts
        assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt['sha256'], receipt['path']
        checked.append(receipt['path'])
    review = json.loads((BASE / 'DIAGRAM_RELATION_SOURCE_INTAKE_REVIEW_20260927.json').read_text())
    report = BASE / review['reviewed_root_report']['path']
    assert hashlib.sha256(report.read_bytes()).hexdigest() == review['reviewed_root_report']['sha256']
    assert review['root_corrections_required'] == []
    assert len(packet['sources']) == 2
    assert sum(row['selected_complete_images'] for row in packet['sources']) == 2
    assert packet['new_target_access'] == []
    assert packet['confirmed_words'] == 0
    assert packet['score_ready_relation_packet'] is False
    if args.local_sources:
        for source in packet['sources']:
            for receipt in source['local_files']:
                path = BASE / receipt['path']
                assert path.is_relative_to(BASE) and '..' not in Path(receipt['path']).parts
                assert path.stat().st_size == receipt['bytes'], receipt['path']
                assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt['sha256'], receipt['path']
                checked.append(receipt['path'])
    print(json.dumps({'status': 'PASS_RECEIPT_INTEGRITY_ONLY', 'checked_files': len(checked),
                      'local_sources_checked': args.local_sources,
                      'limit': 'No mechanical verification of image observations, access history, meanings or provenance authenticity.'}, indent=2))


if __name__ == '__main__':
    main()

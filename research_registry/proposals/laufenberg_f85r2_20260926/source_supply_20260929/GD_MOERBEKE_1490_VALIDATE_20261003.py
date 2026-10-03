"""Verify source receipts and preserved draft bytes; does not validate Latin.

Optional --cache DIR checks previously downloaded public HTML/JPG files.
No downloads or target-manuscript access. Library images must not be published.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    base = Path(__file__).parent
    result = json.loads((base / 'GD_MOERBEKE_1490_RESULT_20261003.json').read_text())
    receipts = json.loads((base / 'GD_MOERBEKE_1490_RECEIPTS_20261003.json').read_text())['receipts']
    chapter = (base / 'GD_MOERBEKE_1490_CHAPTER_XLII_20261003.md').read_bytes()
    assert sha(chapter) == result['transcription_sha256'], 'current chapter hash'
    marker = b'## Explicit informed native-review errata,'
    assert chapter.count(marker) == 1, 'explicit errata boundary'
    original = chapter.split(marker)[0].rstrip(b'\n') + b'\n'
    assert sha(original) == result['earlier_frozen_transcription_sha256'], 'preserved original'
    assert result['no_target_test'] and result['no_target_or_reserve_access']
    assert result['registered_questions'][2]['uncertain_expansion_status'].startswith('WITHDRAWN')
    assert len({r['name'] for r in receipts}) == len(receipts), 'unique receipt identities'
    checked = 0
    if args.cache:
        cached = set()
        for path in args.cache.iterdir():
            if path.is_file() and path.suffix.lower() in {'.html', '.jpg'}:
                data = path.read_bytes()
                cached.add((len(data), sha(data)))
        for receipt in receipts:
            assert (receipt['bytes'], receipt['sha256']) in cached, receipt['name']
            checked += 1
    print(json.dumps({'status': 'PASS', 'source_receipts_checked': checked,
                      'cache_check': 'RUN' if args.cache else 'NOT_RUN',
                      'original_draft_preserved': True,
                      'scope': 'bytes and correction bookkeeping only; not Latin or meaning'}, indent=2))


if __name__ == '__main__':
    main()

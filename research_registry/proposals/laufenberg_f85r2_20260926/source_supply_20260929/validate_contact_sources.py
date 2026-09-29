"""Validate source coverage/receipts, not the handwritten text or meanings."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bnf-images', type=Path)
    parser.add_argument('--producer-images', type=Path)
    args = parser.parse_args()
    declared = json.loads((HERE / 'BNF_CONTACT_SOURCE_RECEIPTS.json').read_text())
    assert [r['folio'] for r in declared] == [
        '27v', '28r', '29v', '121r', '123v', '134v', '156v']
    mirrors = json.loads((HERE / 'BNF_CONTACT_MIRROR_RECEIPTS.json').read_text())
    success = [r for r in mirrors if r['status'] == 'DOWNLOADED']
    assert {r['folio'] for r in success} == {'027v', '028r', '029v', '156v'}
    assert len(success) == 4
    producer = json.loads((HERE / 'C_IMAGE_RECEIPTS.json').read_text())
    assert len(producer) == 13
    assert len({r['file'] for r in producer}) == 13
    assert all(r['url'].startswith('https://') for r in producer)
    assert all(len(r['sha256']) == 64 for r in success + producer)
    checked = 0
    for directory, rows, key in [(args.bnf_images, success, 'folio'),
                                 (args.producer_images, producer, 'file')]:
        if directory is None:
            continue
        for row in rows:
            name = row[key] + '_commons.jpg' if key == 'folio' else row[key]
            data = (directory / name).read_bytes()
            assert len(data) == row['bytes'], name
            assert hashlib.sha256(data).hexdigest() == row['sha256'], name
            checked += 1
    print(json.dumps({
        'status': 'PASS_SOURCE_BOOKKEEPING_ONLY',
        'declared_bnf_folios': 7, 'viewed_bnf_folios': 4,
        'unavailable_bnf_folios': ['121r', '123v', '134v'],
        'producer_image_receipts': len(producer), 'image_bytes_checked': checked,
        'meaning_validation': False, 'voynich_fixed_semantic_tests': 0,
        'confirmed_words': 0,
    }, indent=2))


if __name__ == '__main__':
    main()

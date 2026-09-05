#!/usr/bin/env python3
"""Check public canvas labels; fetch metadata only, never image bodies."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare saved result without writing')
    args = parser.parse_args()
    source = json.loads((BASE / 'src/CORRECTED_CANVAS_METADATA.json').read_text())
    if source['source'] != 'https://collections.library.yale.edu/manifests/2002046':
        raise ValueError('Unexpected metadata source')
    with urlopen(source['source'], timeout=30) as response:
        raw = response.read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != source['source_sha256']:
        raise ValueError('Live metadata changed; inspect before updating its recorded hash')
    manifest = json.loads(raw)
    wanted = {'1006194', '1006203', '1006204'}
    rows = []
    for canvas in manifest['items']:
        key = canvas['id'].rsplit('/', 1)[-1]
        if key in wanted:
            rows.append({'id': key, 'label': canvas['label']['none'][0],
                         'width': canvas['width'], 'height': canvas['height']})
    if rows != source['canvases']:
        raise ValueError('Selected canvas labels or dimensions differ')
    labels = {row['id']: row['label'] for row in rows}
    if labels['1006203'] != '71v and 72r' or labels['1006204'] != '72v (part)':
        raise ValueError('The proposed side correction is not supported')
    report = {'status': 'PASS_METADATA_SIDE_CORRECTION_ONLY', 'source_sha256': digest,
              'selected_canvas_ids': sorted(wanted), 'wrong_f72r_parent': '1006204',
              'correct_f72r_parent': '1006203', 'image_bodies_opened': 0,
              'word_meanings_validated': False, 'full_foldout_review_validated': False}
    payload = json.dumps(report, indent=2, sort_keys=True) + '\n'
    target = BASE / 'artifacts/CANVAS_CORRECTION_VALIDATION.json'
    if args.check:
        if target.read_text() != payload:
            raise ValueError('Saved metadata-validation result differs')
    else:
        target.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()

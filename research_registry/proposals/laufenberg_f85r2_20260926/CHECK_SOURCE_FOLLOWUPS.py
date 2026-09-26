#!/usr/bin/env python3
"""Check the frozen source follow-up packet, not its readings or meanings."""
import argparse
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-cached-images', action='store_true')
    parser.add_argument('--output', default='SOURCE_FOLLOWUP_INTEGRITY_RESULT.json')
    args = parser.parse_args()
    checks = []

    def check(label, value):
        checks.append({'check': label, 'pass': bool(value)})

    def hashed(path, expected, label):
        check(label, path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected)

    def read(name):
        return json.loads((BASE / name).read_text())

    manifest = read('SOURCE_FOLLOWUP_MANIFEST.json')
    for row in manifest['files']:
        hashed(ROOT / row['path'], row['sha256'], row['path'])

    speech = read('PERSONIFIED_SPEECH_SOURCE_PUBLIC_RECEIPTS.json')
    composite = read('COMPOSITE_SOURCE_SEARCH_RECEIPTS.json')
    autumn = read('AUTUMN_CLOSE_RECEIPTS.json')
    complexion = read('COMPLEXION_FIGURES_RECEIPTS.json')
    cava = read('CAVA_NATIVE_RECEIPTS.json')
    for kind in ('decision', 'report'):
        hashed(ROOT / speech[kind + '_path'], speech[kind + '_sha256'], 'speech:' + kind)
    hashed(ROOT / speech['line_inventory']['path'], speech['line_inventory']['sha256'], 'speech:inventory')
    for name, digest in composite['packet_hashes_excluding_receipt'].items():
        hashed(BASE / name, digest, 'composite:' + name)
    for packet in (autumn, complexion):
        for row in packet['bound_files']:
            hashed(ROOT / row['path'], row['sha256'], packet['packet'] + ':' + row['path'])
    for row in cava['frozen_documents'] + cava['prior_frozen_hashes']:
        hashed(ROOT / row['path'], row['sha256'], 'cava:' + row['path'])

    inventory = (BASE / 'PERSONIFIED_SPEECH_LINE_INVENTORY.md').read_text()
    counts = {161: 16, 162: 6, 163: 23, 164: 21, 165: 9, 166: 23, 167: 8, 168: 22}
    observed = re.findall(r'^\| (\d{3})\.P(\d{2}) \|', inventory, re.M)
    expected = [(str(scan), f'{line:02d}') for scan, total in counts.items()
                for line in range(1, total + 1)]
    check('all128 physical line IDs once and in order', observed == expected)
    check('six heading rows leave122 verse rows', len(observed) - 6 == 122)
    check('eight fixed speech scans', speech['scan_scope']['planned_and_inspected_new_complete_scans'] ==
          [f'{i:05d}' for i in range(161, 169)])
    check('eight composite candidates retained', len(composite['candidate_ledger']) == 8)
    check('two composite source images', len(composite['images']) == 2)
    check('Autumn distinct extension six lines', autumn['observed_lines'] == 6 and
          autumn['parent_packet_retroactively_changed'] is False)
    check('Autumn26 main plus2 caption', autumn['autumn_main_verse_count'] == 26 and
          autumn['caption_verse_count'] == 2)
    check('allfour complexion figures on three viewed pages', len(complexion['figures']) == 4 and
          complexion['viewed_labels'] == ['92r', '92v', '93r'])
    check('complexion93v remains unopened', complexion['unopened_label'] == '93v')
    check('Cava access failure preserves zero observations', cava['status'] ==
          'ACCESS_FAILURE_BEFORE_NATIVE_INSPECTION' and cava['image_files_viewed'] == 0 and
          cava['native_observations_completed'] == 0)

    images = [(ROOT / row['cache_path'], row['sha256']) for row in speech['images']]
    images += [(ROOT / row['cache_path'], row['sha256']) for row in complexion['images']]
    images += [(BASE / row['cache'], row['sha256']) for row in composite['images']]
    images += [(BASE / 'external_cache/heat_winter_augsburg1491_00169.jpg', autumn['image_sha256'])]
    if args.verify_cached_images:
        for path, digest in images:
            hashed(path, digest, 'cached image:' + path.name)
    check('no target or reserve access in source packets',
          speech['compliance']['target_queries'] == 0 and
          composite['scope']['new_target_data'] == 0 and
          composite['scope']['reserve_access'] == 0 and
          autumn['target_access'] == 0 and autumn['reserve_access'] is False and
          complexion['target_access'] == 0 and cava['target_data_or_images'] == 0)
    result = {'status': 'PASS' if all(row['pass'] for row in checks) else 'FAIL',
              'claim_ceiling': 'file identity, source scope and line inventory; not native readings, historical truth or translation',
              'image_mode': 'cached bytes' if args.verify_cached_images else 'not checked',
              'images_checked': len(images) if args.verify_cached_images else 0,
              'checks': checks}
    (BASE / args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'claim_ceiling', 'images_checked')}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()

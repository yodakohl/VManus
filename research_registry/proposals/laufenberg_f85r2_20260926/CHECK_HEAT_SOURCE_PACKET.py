#!/usr/bin/env python3
"""Verify source packet integrity, not native readings or semantic truth."""
import argparse
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify-cached-images', action='store_true')
    ap.add_argument('--output', default='HEAT_SOURCE_INTEGRITY_RESULT.json')
    args = ap.parse_args()
    checks = []
    image_checks = []

    def check(name, condition):
        checks.append({'check': name, 'pass': bool(condition)})

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    packets = {}
    for name in ('HIPPOCRATIC_HEAT_SOURCE', 'HEAT_PRINT_PARALLEL',
                 'HEAT_WINTER_EXTENSION'):
        receipt = json.loads((BASE / (name + '_RECEIPTS.json')).read_text())
        packets[name] = receipt
        if 'frozen_files' in receipt:
            for entry in receipt['frozen_files']:
                path = ROOT / entry['path']
                check(name + ':' + path.name, digest(path) == entry['sha256'])
        else:
            for kind in ('decision', 'report'):
                path = BASE / (name + '_' + kind.upper() + '.md')
                check(name + ':' + kind, digest(path) == receipt[kind + '_sha256'])
        for row in receipt['images']:
            if 'cache_path' in row:
                path = ROOT / row['cache_path']
            else:
                path = BASE / row['cache_relative_to_dossier']
            entry = {'packet': name, 'file': path.name}
            if args.verify_cached_images:
                ok = path.is_file() and digest(path) == row['sha256']
                check(name + ':image:' + path.name, ok)
                entry['status'] = 'PASS' if ok else 'FAIL'
            else:
                entry['status'] = 'NOT_CHECKED'
            image_checks.append(entry)

    initial = packets['HEAT_PRINT_PARALLEL']
    extended = packets['HEAT_WINTER_EXTENSION']
    check('initial fixed171-175', initial['fixed_scans'] ==
          ['00171', '00172', '00173', '00174', '00175'])
    check('initial Winter stays incomplete', initial['Winter']['complete'] is False)
    check('initial following unit64', sum(initial['following_complete_unit']
          ['verse_counts_by_scan'].values()) == 64)
    check('separate extension169-171', extended['scope'] == ['00169', '00170', '00171'])
    for kind, suffix in [('decision', 'DECISION.md'), ('report', 'REPORT.md'),
                         ('receipt', 'RECEIPTS.json')]:
        check('previous packet unchanged:' + kind,
              digest(BASE / ('HEAT_PRINT_PARALLEL_' + suffix)) ==
              extended['previous_packet_unchanged'][kind + '_sha256'])
    report = (BASE / 'HEAT_WINTER_EXTENSION_REPORT.md').read_text()
    main_ids = re.findall(r'^\| W(\d+) \| 0017[01] \|', report, re.M)
    voice_ids = re.findall(r'^\| V(\d+) \| 00170 \|', report, re.M)
    check('complete34 main verse rows', main_ids == [str(i) for i in range(1, 35)])
    check('complete2 voice rows', voice_ids == ['1', '2'])
    check('extension two acquisitions', extended['compliance']['new_images'] == 2)
    check('no target inputs', not extended['compliance']['target_input'])
    check('no confirmed words', extended['confirmed_target_meanings'] == 0)
    check('Hippocratic whole13-15', packets['HIPPOCRATIC_HEAT_SOURCE']
          ['hippocrates']['units_used'] == ['I.13', 'I.14', 'I.15'])
    sch = (BASE / 'SCHERMAR_COMPARATOR_REPORT.md').read_text()
    fact = sch.split('## Primary catalogue facts\n\n', 1)[1].split('(Catalogue-derived', 1)[0]
    check('Schermar actual fact paragraph under200', len(fact.split()) <= 200)
    result = {
        'status': 'PASS' if all(x['pass'] for x in checks) else 'FAIL',
        'claim_ceiling': 'integrity/scope/verse inventory, not native reading or meaning',
        'checks': checks, 'image_checks': image_checks,
        'image_mode': 'cached bytes required' if args.verify_cached_images else 'not checked',
        'schermar_actual_fact_paragraph_words': len(fact.split()),
        'frozen_author_word_count_is_correct': len(fact.split()) == 106,
    }
    (BASE / args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks),
                      'images_verified': sum(x['status'] == 'PASS' for x in image_checks),
                      'schermar_words': len(fact.split())}))
    if result['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

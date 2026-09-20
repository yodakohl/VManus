#!/usr/bin/env python3
"""Validate inventory/receipt consistency, not historical or visual meaning."""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def main():
    p = json.loads((BASE / 'TROTULA_COMPLETE_CONTENT_20260920.json').read_text())
    report = ROOT / p['report_path']
    rows = []
    for line in report.read_text().splitlines():
        match = re.match(r'^\| ((?:IV|V|VI)\d\d) \| (.*) \|$', line)
        if match:
            rows.append({'id': match[1], 'content': match[2]})
    expected = [f'{ch}{i:02d}' for ch,n in [('IV',18),('V',19),('VI',6)]
                for i in range(1,n+1)]
    checks = {
        'report_identity': hashlib.sha256(report.read_bytes()).hexdigest() == p['report_sha256'],
        'all_declared_inventory_units': [r['id'] for r in rows] == expected,
        'inventory_replays': rows == p['source_rows'],
        'three_native_source_pages': [(r['scan'],r['printed_page'],r['native_viewed'])
            for r in p['source']['images']] == [(11,7,True),(12,8,True),(13,9,True)],
        'public_source_receipts': all(r['url'].startswith('https://api.digitale-sammlungen.de/')
            and re.fullmatch(r'[0-9a-f]{64}',r['sha256']) and r['bytes'] > 0
            for r in p['source']['images']),
        'two_exposed_target_pages': [r['selector'] for r in p['target_images']] == ['f82r','f83r']
            and all(r['native_viewed'] and r['prior_project_exposure'] for r in p['target_images']),
        'no_new_admission_reserve_or_meaning': all(p[k] == 0 for k in
            ['new_admissions','reserve_accesses','confirmed_voynich_words','independent_meaning_capacity'])
            and not p['target_word_values_assigned'] and not p['f116v_admitted']
            and p['sealed_selectors'] == ['f84','f84r'],
        'edition_limit_retained': not p['source']['pre1420_wording_and_order_verified'],
    }
    result = {'status':'PASS' if all(checks.values()) else 'FAIL',
              'scope':'Same-author inventory/receipt consistency only; no semantic or visual certification',
              'checks':checks,'source_inventory_units':len(rows)}
    (BASE / 'TROTULA_COMPLETE_CONTENT_VALIDATION_20260920.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert all(checks.values())


if __name__ == '__main__':
    main()

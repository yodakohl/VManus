#!/usr/bin/env python3
"""Validate fixed population and reproduced join; does not validate human vision."""
import csv
import hashlib
import json

from run import BASE, SOURCE, main as run_main, read_tsv


def main() -> int:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '8fff37db44c619c21b86422125e985d105bed5e2a6b6cd66e650390477c9d4f0'
    p = BASE / 'src/PAGE_ADMISSIONS.tsv'
    assert hashlib.sha256(p.read_bytes()).hexdigest() == '11a7f948c78f24841e6775278538640bceed584a96a37b5fad00bf69280cc1cf'
    visual = BASE / 'artifacts/BLIND_VISUAL.tsv'
    source_images = BASE / 'artifacts/SOURCE.tsv'
    assert hashlib.sha256(visual.read_bytes()).hexdigest() == '3a0c973f0522027c4d18dfdb745a868eee90d2cd3732538e765a1659dac2aed9'
    assert hashlib.sha256(source_images.read_bytes()).hexdigest() == '636639660ded6b1da0e9bf7e127c7f9dc1d70ea28950f69d861af4256acd4f20'
    image_rows = read_tsv(source_images)
    assert len(image_rows) == 23
    assert all(row['image_url'].startswith('https://collections.library.yale.edu/iiif/2/') and len(row['sha256']) == 64 for row in image_rows)
    result = BASE / 'artifacts/RESULTS.tsv'
    old = result.read_bytes() if result.exists() else b''
    run_main()
    assert result.read_bytes() == old, 'result changed on independent rerun'
    with result.open(newline='') as file:
        rows = list(csv.DictReader(file, delimiter='\t'))
    assert len(rows) == 23
    assert all(row['folio'] not in {'f84', 'f84r'} for row in rows)
    assert {row['decision'] for row in rows} <= {'SUPPORT', 'CONFLICT', 'UNDECIDABLE'}
    assert sum(row['decision'] == 'SUPPORT' for row in rows) == 0
    assert sum(row['decision'] == 'CONFLICT' for row in rows) == 13
    assert sum(row['decision'] == 'UNDECIDABLE' for row in rows) == 10
    payload = {
        'experiment_id': 'GDT1087', 'status': 'PASS', 'rows': 23,
        'checks': ['fixed GDT1062 claim hash', 'fixed admission hash',
                   'frozen blind visual hash', 'frozen Yale source hash',
                   'official image URLs', 'deterministic 23-row join',
                   'f84/f84r excluded', 'decision counts'],
        'limit': 'human botanical morphology not machine validated',
    }
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(payload, indent=2) + '\n')
    print('PASS 23 source rows, fixed admissions, frozen blind inventory and deterministic join; visual judgments remain human')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

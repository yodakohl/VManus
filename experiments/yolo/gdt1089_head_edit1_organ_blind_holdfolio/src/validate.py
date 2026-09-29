#!/usr/bin/env python3
"""Validate frozen source, blind tables, deterministic join and manifest hashes."""
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in BASE.parents if (p / 'AGENTS.md').is_file() and (p / '.git').exists())
ART, SRC = BASE / 'artifacts', BASE / 'src'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with path.open(newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))

def main():
    manifest = json.loads((BASE / 'experiment.json').read_text())
    assert manifest['experiment_id'] == 'GDT1089'
    assert manifest['sealed_data']['f84'] == manifest['sealed_data']['f84r'] == 'FORBIDDEN'
    for entry in manifest['inputs'] + manifest['outputs']:
        p = ROOT / entry['path']
        assert p.is_file() and sha(p) == entry['sha256'], str(p)
    source = rows(ART / 'SOURCE.tsv')
    folios = [x['folio'] for x in rows(SRC / 'BLIND_IMAGE_LIST.tsv')]
    assert [x['folio'] for x in source] == folios and len(folios) == 38
    assert sum(x['scope'] == 'NEW_GDT1089' for x in source) == 11
    assert all(x['image_url'].startswith('https://collections.library.yale.edu/iiif/2/') for x in source)
    assert all(x['folio'] not in ('f84', 'f84r') for x in source)
    for row in source:
        cache = Path(tempfile.gettempdir()) / 'gdt1089_blind_images' / (row['folio'] + '.jpg')
        if cache.is_file():
            assert sha(cache) == row['sha256']
    result_before = (ART / 'RESULT.json').read_bytes()
    pairs_before = (ART / 'PAIR_DECISIONS.tsv').read_bytes()
    subprocess.run([sys.executable, str(SRC / 'run.py')], check=True, stdout=subprocess.DEVNULL)
    assert (ART / 'RESULT.json').read_bytes() == result_before
    assert (ART / 'PAIR_DECISIONS.tsv').read_bytes() == pairs_before
    result = json.loads(result_before)
    assert len(rows(ART / 'PAIR_DECISIONS.tsv')) == 50
    assert result['counts']['all']['TARGET'] and result['counts']['all']['CONTROL']
    assert result['hashes']['BLIND_A.tsv'] == sha(ART / 'BLIND_A.tsv')
    assert result['hashes']['BLIND_B.tsv'] == sha(ART / 'BLIND_B.tsv')
    print('PASS GDT1089: 38 authorized image sources; two 38-row blind inventories; 50 fixed pair/control decisions; deterministic replay; sealed folios untouched')

if __name__ == '__main__':
    main()

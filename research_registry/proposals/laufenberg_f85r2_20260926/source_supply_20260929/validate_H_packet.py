#!/usr/bin/env python3
"""Replay compact historical-source artifacts; no Voynich inputs are opened."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    receipt = json.loads((HERE / 'H_SOURCE_RECEIPTS.json').read_text())
    checked = []
    for row in receipt['files']:
        if row['file'].endswith('.zif'):
            continue  # Public acquisition provenance retained, raw bytes not published.
        path = HERE / row['file']
        assert sha(path.read_bytes()) == row['sha256'], row['file']
        if 'image_dimensions' in row:
            with Image.open(path) as im:
                assert list(im.size) == row['image_dimensions']
        checked.append(row['file'])
    source = json.loads((HERE / 'H_SOURCE_METADATA.json').read_text())['source_edition']
    path = ROOT / source['existing_cache']
    if not path.exists():
        request = urllib.request.Request(source['url'], headers={'User-Agent': 'VManus-source-replay'})
        with urllib.request.urlopen(request, timeout=45) as response:
            blob = response.read()
        assert sha(blob) == source['sha256'], 'Public source changed'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    assert sha(path.read_bytes()) == source['sha256']
    subprocess.run([sys.executable, str(HERE / 'H_EXTRACT_SOURCE.py')], check=True)
    replayed = []
    for row in receipt['files']:
        if row['file'].startswith('H_DIOSCORIDES_'):
            assert sha((HERE / row['file']).read_bytes()) == row['sha256'], row['file']
            replayed.append(row['file'])
    assert len(replayed) == 6
    result = dict(status='PASS', compact_receipt_files_checked=len(checked),
                  extraction_artifacts_replayed=len(replayed), complete_critical_entries=2,
                  medieval_folios=4, medieval_manuscripts=1,
                  full_medieval_kyklaminos_entry_available=False,
                  meaning_verified=False, target_access=False,
                  checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (HERE / 'H_ROOT_VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

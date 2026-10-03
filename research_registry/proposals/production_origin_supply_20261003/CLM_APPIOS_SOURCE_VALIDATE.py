#!/usr/bin/env python3
"""Replay source-byte/coverage checks, not Latin reading correctness."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from PIL import Image

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--cache', type=Path, required=True,
               help='directory containing the four acquisition receipt cache basenames')
a = p.parse_args()
base = Path(__file__).resolve().parent
root = base.parents[2]
sha = lambda x: hashlib.sha256(x.read_bytes()).hexdigest()
seal = json.loads((base / 'CLM_APPIOS_SOURCE_SEAL.json').read_text())
checks = {}
for row in seal['files']:
    checks['seal:' + Path(row['path']).name] = sha(root / row['path']) == row['sha256']
receipt = json.loads((base / 'CLM_APPIOS_SOURCE_ACQUISITION.json').read_text())
for row in [receipt['manifest']] + receipt['requests']:
    source = a.cache / Path(row['cache_path']).name
    checks[source.name] = sha(source) == row['sha256'] and source.stat().st_size == row['bytes']
text = (base / 'CLM_APPIOS_SOURCE_NATIVE_B.md').read_text()
checks['complete_line_inventory'] = re.findall(r'^(\d{2}) ', text, re.M) == [f'{i:02}' for i in range(1,15)]
with Image.open(a.cache / 'canvas7_original.jpg') as im:
    checks['original_dimensions'] = im.size == (1707, 2531)
print(json.dumps({'status': 'PASS' if all(checks.values()) else 'FAIL',
                  'scope': 'frozen bytes and coverage only; no native reading validation',
                  'checks': checks}, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)

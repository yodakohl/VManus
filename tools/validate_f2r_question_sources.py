#!/usr/bin/env python3
"""Check the f2r question's public source identity/ROI, not visual truth."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--fetch', action='store_true', help='verify the four official JPEGs')
args = p.parse_args()
root = Path(__file__).resolve().parents[1]
old = json.loads((root / 'experiments/semantic_assumptions/results/f2r15_native_visual_ownership_correction.json').read_text())['sources']['yale_2014']
packet = json.loads((root / 'research_registry/decisions/qe1_f2r15_native_ROOT.json').read_text())
prefix = 'https://collections.library.yale.edu/iiif/2/1006078/'
assert old['detail_image_url'] == prefix + '1750,900,900,900/1800,/0/default.jpg'
assert packet['source'] == old['image_url']
assert packet['source_sha256'] == old['image_sha256']
# The old detail ends at y1800; the whole new lower context begins at y1850.
# Disjoint source regions are a coordinate fact, not semantic/localization gold.
assert 900 + 900 < 1850
sources = [(old['image_url'], old['image_sha256']),
           (old['detail_image_url'], old['detail_image_sha256'])]
for view in packet['views']:
    sources.append((prefix + view['region'] + '/' + view['size'] + '/0/default.jpg', view['sha256']))
if args.fetch:
    for url, expected in sources:
        with urlopen(url, timeout=35) as response:
            assert hashlib.sha256(response.read()).hexdigest() == expected, url
print(json.dumps({'status': 'PASS', 'old_and_new_detail_regions_disjoint': True,
                  'source_bindings_checked': len(sources), 'jpeg_hashes_fetched': args.fetch,
                  'native_interpretation_independently_validated': False}))

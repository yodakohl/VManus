#!/usr/bin/env python3
"""Fetch only one registered overview and one frozen native IIIF rectangle."""
import datetime
import hashlib
import io
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
spec = json.loads((D / 'src/SPEC.json').read_text())
lock = json.loads((D / 'src/PROTOCOL_LOCK.json').read_text())
for path, digest in lock['pins'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
stage, = sys.argv[1:]
assert stage in ('overview', 'detail')
receipt = D / 'artifacts' / (stage.upper() + '_SOURCE.json')
image = D / 'artifacts' / ('original_f14v.jpg' if stage == 'overview' else 'native_detail.jpg')
assert not receipt.exists() and not image.exists(), 'No repeated acquisition'
if stage == 'overview':
    url = spec['overview_url']
    expected = spec['overview_dimensions']
else:
    assert (D / 'artifacts/OVERVIEW_SOURCE.json').exists()
    crop = json.loads((D / 'artifacts/CROP_SCOPE.json').read_text())
    x, y, w, h = crop['region']
    assert all(type(v) is int for v in [x, y, w, h])
    assert x >= 0 and y >= 0 and w > 0 and h > 0 and x + w <= 2812 and y + h <= 3772
    url = spec['detail_url_template'].format(region=','.join(map(str, crop['region'])))
    expected = [w, h]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with urlopen(Request(url, headers={'User-Agent': 'VManus source research'}), timeout=30) as response:
    assert response.status == 200 and response.headers.get_content_type() == 'image/jpeg'
    assert response.geturl() == url
    data = response.read(12000000)
assert len(data) < 12000000
with Image.open(io.BytesIO(data)) as im:
    assert list(im.size) == expected and im.format == 'JPEG'
image.write_bytes(data)
record = {'url': url, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
          'width': expected[0], 'height': expected[1],
          'path': str(image.relative_to(ROOT)), 'fetched_at': started,
          'role': 'Unaltered official original image response; no OCR or enhancement.'}
receipt.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))

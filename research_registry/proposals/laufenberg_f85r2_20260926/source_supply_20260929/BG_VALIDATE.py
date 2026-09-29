#!/usr/bin/env python3
"""Validate BG's sole photographic source and declared scope; not interpretation."""
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parent
receipt = json.loads((base / 'BG_SOURCE_RECEIPT.json').read_text())
manifest_bytes = (base / 'BG_MANIFEST.json').read_bytes()
assert hashlib.sha256(manifest_bytes).hexdigest() == receipt['manifest_sha256']
manifest = json.loads(manifest_bytes)
canvases = manifest['sequences'][0]['canvases']
assert len(canvases) == 1
assert canvases[0]['@id'] == receipt['canvas']
service = canvases[0]['images'][0]['resource']['service']
assert service['@id'] + '/full/full/0/default.jpg' == receipt['image_url']
assert receipt['image_file'] == 'BG_M0007149.jpg'
photo = (base / receipt['image_file']).read_bytes()
assert photo.startswith(b'\xff\xd8') and photo.endswith(b'\xff\xd9')
assert len(photo) == receipt['image_bytes']
assert hashlib.sha256(photo).hexdigest() == receipt['image_sha256']
assert manifest['license'] == receipt['license']
result = json.loads((base / 'BG_RESULT.json').read_text())
assert result['native_image_count'] == 1 and len(result['four_forms']) == 4
assert result['confirmed_words'] == result['independent_target_confirmation_leaves'] == 0
assert not result['target_access'] and not result['complete_manuscript_leaf']
print(json.dumps({'status': 'SOURCE_IDENTITY_AND_SCOPE_PASS', 'images': 1,
                  'native_interpretation_validated': False,
                  'phase_owner_or_meaning_validated': False}, indent=2))

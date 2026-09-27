#!/usr/bin/env python3
"""Check published source receipts/transcript accounting, never semantic truth."""
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
result = json.loads((HERE / 'PLANET_CHILD_PARALLEL_RESULT.json').read_text())
for path, digest in result['files'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
receipts = json.loads((HERE / 'PLANET_CHILD_EXTERNAL_PARALLEL_RECEIPTS.json').read_text())
for path, info in receipts['owned_artifacts'].items():
    blob = (ROOT / path).read_bytes()
    assert len(blob) == info['bytes']
    assert hashlib.sha256(blob).hexdigest() == info['sha256']
text = (HERE / 'PLANET_CHILD_BERLIN_ROOT_NATIVE.md').read_text()
unit = text.split('~~~')[1]
left = unit.split('23rA\n')[1].split('23rB\n')[0]
right = unit.split('23rB\n')[1]
assert [int(n) for n in re.findall(r'^(\d{2}) ', left, re.M)] == list(range(1, 26))
assert [int(n) for n in re.findall(r'^(\d{2}) ', right, re.M)] == list(range(1, 16))
assert unit.count('22vBfinal: Das') == 1
assert result['berlin_conclusion_baselines'] == 1 + 25 + 15
assert [(r['folio'], r['canvas_number']) for r in receipts['images']] == [('22v',48),('23r',49)]
assert result['registered572source_changed'] is False
assert result['independent_textual_origin_established'] is False
cached = 0
for source in [receipts['manifest']] + receipts['images']:
    path = ROOT / source['path']
    if path.exists():
        blob = path.read_bytes()
        assert len(blob) == source['bytes']
        assert hashlib.sha256(blob).hexdigest() == source['sha256']
        cached += 1
print(json.dumps({'status':'PASS_RECEIPTS_AND_BASELINE_ACCOUNTING_ONLY',
                  'bound_public_files':len(result['files']),
                  'baseline_positions':41,'available_source_caches_hash_checked':cached,
                  'limit':'No automatic native transcription, historical interpretation or Voynich meaning validation.'}))

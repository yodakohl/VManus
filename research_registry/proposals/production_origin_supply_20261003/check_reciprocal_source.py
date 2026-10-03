"""Check saved evidence bytes; does not validate historical interpretation."""
from pathlib import Path
import hashlib
import json

base = Path(__file__).resolve().parent
receipt = json.loads((base / 'RECIPROCAL_SOURCE_RECEIPT.json').read_text())
for name, expected in receipt['public_bindings'].items():
    assert hashlib.sha256((base / name).read_bytes()).hexdigest() == expected, name
checked = missing = 0
for item in receipt['sources']:
    assert item['url'].startswith('https://api.digitale-sammlungen.de/iiif/')
    path = base / 'runtime' / 'reciprocal_source' / item['cache_name']
    if not path.exists():
        missing += 1
        continue
    data = path.read_bytes()
    assert len(data) == item['bytes'], item['cache_name']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['cache_name']
    checked += 1
print(json.dumps({'public_bindings': 'PASS', 'source_bytes_checked': checked,
                  'source_files_not_cached': missing,
                  'native_transcription_and_target_meaning': 'NOT_VALIDATED'}))

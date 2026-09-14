"""Verify registered scope and source bytes; does not validate manual readings."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

base = Path(__file__).resolve().parent
source = json.loads((base / 'SOURCE.json').read_text())
result = json.loads((base / 'RESULT.json').read_text())
assert hashlib.sha256((base / 'DECISION.md').read_bytes()).hexdigest() == source['preregistration_sha256']
assert [p['label'] for p in source['pages']] == result['selected_pages'] == ['f.50r', 'f.50v']
for page in source['pages']:
    with urlopen(page['image'], timeout=30) as response:
        assert hashlib.sha256(response.read()).hexdigest() == page['sha256']
assert result['voynich_target_access'] is False and result['voynich_meanings'] == 0
print('PASS: fixed source pair and received bytes; manual readings not independently validated')

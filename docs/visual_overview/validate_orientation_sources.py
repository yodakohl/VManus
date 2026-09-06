"""Verify cached original bytes against the recorded orientation source metadata."""
import hashlib
import json
from pathlib import Path
from PIL import Image

base = Path(__file__).resolve().parent
sources = json.loads((base / 'ORIENTATION_2026-09-06_SOURCES.json').read_text())
for row in sources['source_images']:
    image_path = base / 'runtime' / row['cache_filename']
    data = image_path.read_bytes()
    assert len(data) == row['bytes'], row['canvas_id']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['canvas_id']
    with Image.open(image_path) as im:
        assert im.size == (row['width'], row['height']), row['canvas_id']
    assert row['viewed'] is True
print('PASS: three cached originals match recorded bytes, hashes and dimensions; judgments not validated')

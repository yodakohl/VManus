"""Verify cached original bytes against the recorded orientation source metadata."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

base = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('source_file', nargs='?', default='ORIENTATION_2026-09-06_SOURCES.json')
args = parser.parse_args()
sources = json.loads((base / args.source_file).read_text())
for row in sources['source_images']:
    image_path = base / 'runtime' / row['cache_filename']
    data = image_path.read_bytes()
    assert len(data) == row['bytes'], row['canvas_id']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['canvas_id']
    with Image.open(image_path) as im:
        assert im.size == (row['width'], row['height']), row['canvas_id']
    assert row['viewed'] is True
print(f"PASS: {len(sources['source_images'])} cached originals match recorded bytes, hashes and dimensions; judgments not validated")

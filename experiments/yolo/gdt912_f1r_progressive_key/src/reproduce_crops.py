#!/usr/bin/env python3
"""Recreate registered native crops from the hash-bound public original JPEG."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
BASE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('native_source', type=Path)
parser.add_argument('output_directory', type=Path)
parser.add_argument('--include-mislocalized', action='store_true')
args = parser.parse_args()
native = json.loads((BASE / 'artifacts/NATIVE_SOURCE.json').read_text())
assert hashlib.sha256(args.native_source.read_bytes()).hexdigest() == native['source_sha256']
panels = json.loads((BASE / 'artifacts/LOCALIZATION_CORRECTION.json').read_text())['panels']
if args.include_mislocalized:
    panels += native['panels']
args.output_directory.mkdir(parents=True, exist_ok=True)
with Image.open(args.native_source) as original:
    for panel in panels:
        destination = args.output_directory / Path(panel['path']).name
        if destination.exists():
            raise FileExistsError(destination.name)
        original.crop(panel['source_box']).save(destination)
print(json.dumps({'panels_recreated': len(panels), 'transform': 'exact pixel crop only'}))

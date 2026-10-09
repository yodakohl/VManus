#!/usr/bin/env python3
"""Retrieve the same explicit public-domain edition; never silently replace snapshot."""
from pathlib import Path
import argparse,hashlib,json,urllib.parse,urllib.request
D=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
receipt=json.loads((D/'RECEIPT.json').read_text())
for item in receipt['files']:
    destination=args.output/Path(item['path']).name
    assert not destination.exists(),destination.name
    with urllib.request.urlopen(item['url'],timeout=40) as response: content=response.read()
    destination.write_bytes(content)
    observed=hashlib.sha256(content).hexdigest()
    print(json.dumps({'file':destination.name,'sha256':observed,'matches_snapshot':observed==item['sha256']}))

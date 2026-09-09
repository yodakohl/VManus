#!/usr/bin/env python3
"""Rebuild the original source snapshot from original receipts and acquired HTML.

Acquire public captures into a separate working cache first. This tool copies
only byte-identical original successful bodies into a new cache, preserving
original missing/failure decisions and exact receipt bytes. It does not fetch
the network, change the source pool, or copy modern edition text into the repo.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

SUCCESS = {'ACQUIRED', 'ACQUIRED_FROM_IDENTICAL_CAPTURE_CACHE'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def replay(receipts, captures, cdx, acquired, output):
    bundle = json.loads(receipts.read_bytes())
    capture_raw, cdx_raw = captures.read_bytes(), cdx.read_bytes()
    capture_data = json.loads(capture_raw)
    if bundle['schema'] != 'gdt895-original-receipts-v1':
        raise ValueError('wrong original receipt bundle schema')
    if digest(cdx_raw) != capture_data['cdx_sha256']:
        raise ValueError('CDX byte binding mismatch')
    source_ids = {r['id']: r for r in capture_data['records']}
    receipt_rows, bodies = {}, []
    for item in bundle['records']:
        filename = item['filename']
        if not re.fullmatch('[0-9]{4}\\.json', filename) or filename in receipt_rows:
            raise ValueError('unsafe or duplicate original receipt name')
        raw = item['raw_utf8'].encode('utf-8')
        if digest(raw) != item['sha256']:
            raise ValueError('original receipt byte binding mismatch')
        receipt = json.loads(raw)
        ident = filename[:-5]
        if (receipt['id'] != ident or ident not in source_ids
                or receipt['title'] != source_ids[ident]['title']
                or receipt['selected'] != source_ids[ident]['selected']
                or receipt['status'] == 'PENDING'):
            raise ValueError('original receipt identity or completion mismatch')
        receipt_rows[filename] = raw
        if receipt['status'] in SUCCESS:
            relative = 'html/' + ident + '.html'
            if receipt['file'] != relative:
                raise ValueError('unsafe original body path')
            path = acquired / relative
            body = path.read_bytes()
            if digest(body) != receipt['sha256'] or len(body) != receipt['bytes']:
                raise ValueError('acquired body differs from original capture: ' + ident)
            bodies.append((relative, path))
    if {p[:-5] for p in receipt_rows} != set(source_ids):
        raise ValueError('original receipt universe incomplete')
    if output.resolve() == acquired.resolve() or (output.exists() and any(output.iterdir())):
        raise ValueError('replay output must be an empty, separate cache')
    # All inputs have been checked before creating the exact replay snapshot.
    (output / 'receipts').mkdir(parents=True, exist_ok=True)
    (output / 'html').mkdir()
    (output / 'CAPTURES.json').write_bytes(capture_raw)
    (output / 'CDX_ALL.raw').write_bytes(cdx_raw)
    for filename, raw in receipt_rows.items():
        (output / 'receipts' / filename).write_bytes(raw)
    for relative, path in bodies:
        shutil.copyfile(path, output / relative)
    return {'status': 'ORIGINAL_RECEIPT_CACHE_REPLAYED',
            'receipts': len(receipt_rows), 'identical_html_bodies': len(bodies),
            'capture_sha256': digest(capture_raw), 'cdx_sha256': digest(cdx_raw),
            'receipt_bundle_sha256': digest(receipts.read_bytes())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipts', type=Path, required=True)
    parser.add_argument('--captures', type=Path, required=True)
    parser.add_argument('--cdx', type=Path, required=True)
    parser.add_argument('--acquired-cache', type=Path, required=True)
    parser.add_argument('--replay-cache', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.receipts, args.captures, args.cdx,
                            args.acquired_cache, args.replay_cache)))


if __name__ == '__main__':
    main()

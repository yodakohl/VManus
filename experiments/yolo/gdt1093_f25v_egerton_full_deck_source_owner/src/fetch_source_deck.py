#!/usr/bin/env python3
"""Fetch the fixed Egerton source deck; never accesses Voynich material."""
import csv
import hashlib
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]
RUNTIME = BASE / 'runtime'
MANIFEST = 'https://bl.digirati.io/iiif/ark:/81055/vdc_100058663072.0x000001'
MANIFEST_SHA = 'b3d45df72bd2bd8dbdfa15e6f94168c7af4aa21c11441f1e42c6c796d7eb5ac4'


def fetch_one(row):
    dest = RUNTIME / f"{row['index']:03d}.jpg"
    if dest.exists():
        data = dest.read_bytes()
    else:
        for attempt in range(4):
            try:
                resp = requests.get(row['thumbnail_url'], timeout=35)
                resp.raise_for_status()
                data = resp.content
                Image.open(io.BytesIO(data)).verify()
                dest.write_bytes(data)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(attempt + 1)
    Image.open(io.BytesIO(data)).verify()
    return {**row, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    RUNTIME.mkdir(exist_ok=True)
    data = requests.get(MANIFEST, timeout=40).content
    assert hashlib.sha256(data).hexdigest() == MANIFEST_SHA
    manifest = json.loads(data)
    assert len(manifest['items']) == 309
    rows = []
    for i, canvas in enumerate(manifest['items']):
        body = canvas['items'][0]['items'][0]['body']
        service = body['service'][0]['@id']
        rows.append({'index': i, 'label': canvas['label']['en'][0],
                     'canvas_id': canvas['id'],
                     'thumbnail_url': service + '/full/320,/0/default.jpg',
                     'native_url': service + '/full/1500,/0/default.jpg'})
    out = [None] * len(rows)
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(fetch_one, row): row['index'] for row in rows}
        for future in as_completed(futures):
            out[futures[future]] = future.result()
    with (BASE/'src/SOURCE_DECK.tsv').open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['index','label','canvas_id','thumbnail_url','native_url','bytes','sha256'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(out)
    for start in range(0, len(out), 40):
        subset = out[start:start+40]
        sheet = Image.new('RGB', (8*220, 5*270), 'white')
        draw = ImageDraw.Draw(sheet)
        for k, row in enumerate(subset):
            im = Image.open(RUNTIME / f"{row['index']:03d}.jpg").convert('RGB')
            im.thumbnail((210,235))
            x=(k%8)*220; y=(k//8)*270
            sheet.paste(im,(x+(210-im.width)//2,y))
            draw.text((x+4,y+239),f"{row['index']} {row['label']}",fill='black')
        sheet.save(RUNTIME / f'CONTACT_{start//40+1:02d}.jpg',quality=88)
    print({'manifest_sha256':MANIFEST_SHA,'canvases':len(out),'sheets':(len(out)+39)//40})


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Recreate coordinate plates and optional labeled centerpixel review overlays."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cache-dir', type=Path, default=Path('.cache/gdt830_native'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--overlays', action='store_true')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('DejaVuSans.ttf', 14)
    labels = []
    if args.overlays:
        for role in ['CAL', 'HELD']:
            with (ROOT / f'src/ANNOTATIONS_{role}.tsv').open() as f:
                labels.extend(csv.DictReader(f, delimiter='\t'))
    tiles = json.loads((ROOT / 'src/TILES.json').read_text())
    for source in json.loads((ROOT / 'src/SOURCES.json').read_text()):
        path = args.cache_dir / source['filename']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
        im = Image.open(path).convert('RGB')
        for t in (t for t in tiles if t['page'] == source['page']):
            x, y = t['x0'], t['y0']
            native = im.crop((x, y, x+192, y+192))
            assert hashlib.sha256(native.tobytes()).hexdigest() == t['tile_rgb_sha256']
            tid = t['tile_id']
            native.save(args.out / (tid+'.png'))
            plate = Image.new('RGB', (840,840), 'white')
            plate.paste(native.resize((768,768), Image.Resampling.NEAREST), (48,48))
            d = ImageDraw.Draw(plate)
            d.text((48,10), tid+' | native tile 192 x 192 | x/y ticks outside source', font=font, fill='black')
            for value in range(0,193,16):
                pos = 48+4*value
                d.line((pos,40,pos,47), fill='black')
                d.text((pos-10,24), str(value), font=font, fill='black')
                d.line((40,pos,47,pos), fill='black')
                d.text((6,pos-8), str(value), font=font, fill='black')
            plate.save(args.out / (tid+'_coords.png'))
            if args.overlays:
                for r in (r for r in labels if r['tile_id'] == tid):
                    px, py = 50+4*int(r['x']), 50+4*int(r['y'])
                    color = 'blue' if r['label'] == 'ink' else 'magenta'
                    d.ellipse((px-9,py-9,px+9,py+9), outline=color, width=2)
                    d.text((px+11,py-9), r['label_id'].rsplit('_',1)[-1], fill=color, font=font)
                plate.save(args.out / (tid+'_review.png'))


if __name__ == '__main__':
    main()

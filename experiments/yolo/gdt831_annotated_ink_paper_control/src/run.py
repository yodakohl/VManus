#!/usr/bin/env python3
"""GDT831: scalar calibration, then separately invoked held-label evaluation."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image
from measure import tile_scores

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['label_id', 'tile_id', 'page', 'role', 'label', 'x', 'y', 'score']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2) + '\n').encode()


def tsv_bytes(rows):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=FIELDS, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    return out.getvalue().encode()


def read_tsv(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def verify_lock():
    lock = json.loads((ROOT / 'src/PREREG_LOCK.json').read_text())
    for relative, expected in lock['sha256'].items():
        assert digest(ROOT / relative) == expected, f'Preregistration changed: {relative}'
    return lock


def inventory():
    tiles = json.loads((ROOT / 'src/TILES.json').read_text())
    by_tile = {t['tile_id']: t for t in tiles}
    labels = read_tsv(ROOT / 'src/ANNOTATIONS_CAL.tsv') + read_tsv(ROOT / 'src/ANNOTATIONS_HELD.tsv')
    assert len(tiles) == 24 and len(labels) == 192
    assert len({r['label_id'] for r in labels}) == len(labels)
    assert {t['page'] for t in tiles} == {'f76r', 'f77r', 'f81r', 'f83r'}
    for t in tiles:
        rr = [r for r in labels if r['tile_id'] == t['tile_id']]
        assert len(rr) == 8 and sum(r['label'] == 'ink' for r in rr) == 4
        assert sum(r['label'] == 'paper' for r in rr) == 4
        assert len({(r['x'], r['y']) for r in rr}) == 8
    for r in labels:
        t = by_tile[r['tile_id']]
        assert r['page'] == t['page'] and r['role'] == t['role']
        assert 0 <= int(r['x']) < 192 and 0 <= int(r['y']) < 192
    return tiles, labels


def extract(tiles, labels, cache, fetch):
    sources = {s['page']: s for s in json.loads((ROOT / 'src/SOURCES.json').read_text())}
    rows = []
    for page in sorted({r['page'] for r in labels}):
        source = sources[page]
        path = cache / source['filename']
        if not path.exists() and fetch:
            cache.mkdir(parents=True, exist_ok=True)
            data = urlopen(source['url'], timeout=90).read()
            assert hashlib.sha256(data).hexdigest() == source['sha256']
            path.write_bytes(data)
        assert digest(path) == source['sha256']
        assert path.stat().st_size == source['bytes']
        im = Image.open(path).convert('RGB')
        assert im.size == (source['width'], source['height'])
        for tile in (t for t in tiles if t['page'] == page):
            x, y = tile['x0'], tile['y0']
            crop = im.crop((x, y, x+192, y+192))
            assert hashlib.sha256(crop.tobytes()).hexdigest() == tile['tile_rgb_sha256']
            scores = tile_scores(im, tile)
            for label in (r for r in labels if r['tile_id'] == tile['tile_id']):
                row = {key: label[key] for key in FIELDS if key != 'score'}
                row['score'] = float(scores[int(label['y']), int(label['x'])])
                rows.append(row)
    return sorted(rows, key=lambda r: r['label_id'])


def metrics(rows, threshold, group, ink_min, paper_min):
    result = []
    for name in sorted({r[group] for r in rows}):
        group_rows = [r for r in rows if r[group] == name]
        ink = [r for r in group_rows if r['label'] == 'ink']
        paper = [r for r in group_rows if r['label'] == 'paper']
        tp = sum(float(r['score']) >= threshold for r in ink)
        tn = sum(float(r['score']) < threshold for r in paper)
        recall, specificity = tp/len(ink), tn/len(paper)
        result.append(dict(id=name, n_ink=len(ink), n_paper=len(paper), tp=tp,
                           fn=len(ink)-tp, tn=tn, fp=len(paper)-tn,
                           ink_recall=recall, paper_specificity=specificity,
                           **{'pass': recall >= ink_min and specificity >= paper_min}))
    return result


def summarize_calibration(rows, spec):
    selected = None
    for value in spec['threshold_grid_hundredths']:
        threshold = value / 100
        pages = metrics(rows, threshold, 'page', .90, .95)
        if all(p['paper_specificity'] >= .95 for p in pages):
            selected = threshold
            break
    pages = metrics(rows, selected, 'page', .90, .95) if selected is not None else []
    tiles = metrics(rows, selected, 'tile_id', .75, .75) if selected is not None else []
    passed = selected is not None and all(p['pass'] for p in pages + tiles)
    return dict(selected_threshold=selected, calibration_pages=pages, tiles=tiles,
                calibration_pass=passed, features_sha256=hashlib.sha256(tsv_bytes(rows)).hexdigest())


def evaluate(cal, held, calibration):
    threshold = calibration['selected_threshold']
    hp = metrics(held, threshold, 'page', .90, .95) if held else []
    ht = metrics(held, threshold, 'tile_id', .75, .75) if held else []
    held_pass = bool(held) and all(p['pass'] for p in hp+ht)
    status = ('CALIBRATION_STOP' if not calibration['calibration_pass'] else
              'RESTRICTED_POINT_CONTROL_PASS' if held_pass else 'HELD_POINT_CONTROL_FAIL')
    return dict(status=status, selected_threshold=threshold,
                calibration_pass=calibration['calibration_pass'], held_pass=held_pass,
                calibration_pages=calibration['calibration_pages'], held_pages=hp,
                tiles=calibration['tiles']+ht,
                baselines={'all_paper': {'ink_recall': 0, 'paper_specificity': 1, 'pass': False},
                           'all_ink': {'ink_recall': 1, 'paper_specificity': 0, 'pass': False}},
                counts={'labels_total': 192, 'calibration_labels': len(cal), 'held_labels_scored': len(held)})


def emit(name, data, check=False):
    path = ROOT / 'artifacts' / name
    if check:
        assert path.read_bytes() == data, f'Artifact mismatch: {name}'
    else:
        path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--calibrate', action='store_true')
    mode.add_argument('--evaluate', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--cache-dir', type=Path, default=Path('.cache/gdt830_native'))
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    verify_lock()
    tiles, labels = inventory()
    spec = json.loads((ROOT / 'src/SPEC.json').read_text())
    if args.calibrate or args.check:
        cal = extract(tiles, [r for r in labels if r['role'] == 'calibration'], args.cache_dir, args.fetch)
        calibration = summarize_calibration(cal, spec)
        emit('FEATURES_CAL.tsv', tsv_bytes(cal), args.check)
        emit('CALIBRATION.json', json_bytes(calibration), args.check)
        if args.calibrate:
            print(json.dumps(calibration, sort_keys=True))
            return
    else:
        cal = read_tsv(ROOT / 'artifacts/FEATURES_CAL.tsv')
        calibration = json.loads((ROOT / 'artifacts/CALIBRATION.json').read_text())
        assert calibration == summarize_calibration(cal, spec)
        assert digest(ROOT / 'artifacts/FEATURES_CAL.tsv') == calibration['features_sha256']
    held = []
    if calibration['calibration_pass']:
        held = extract(tiles, [r for r in labels if r['role'] == 'held_labels'], args.cache_dir, args.fetch)
    result = evaluate(cal, held, calibration)
    emit('FEATURES.tsv', tsv_bytes(cal+held), args.check)
    emit('RESULT.json', json_bytes(result), args.check)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

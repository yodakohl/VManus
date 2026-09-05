#!/usr/bin/env python3
"""Independent label, arithmetic and optional native-pixel validator.

No imports from runner/measurement code. Center-pixel replay uses NumPy
neighborhood medians, independently of Pillow's implementation. Run after
preregistration and release of the registered annotations only.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(__file__).resolve().parent
BASE = SRC.parent
PAGES = {'f76r': 'calibration', 'f77r': 'calibration',
         'f81r': 'held_labels', 'f83r': 'held_labels'}
GRID = [i / 100 for i in range(2, 31)]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_tsv(path):
    with Path(path).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def center_score(rgb33):
    """One source center; 33px contains the full 16px support halo."""
    check(np.shape(rgb33) == (33, 33, 3), 'Center neighborhood must be 33x33 RGB')
    gray = np.rint(np.asarray(rgb33, dtype=np.float32).mean(axis=2)).astype(np.uint8)
    windows = np.lib.stride_tricks.sliding_window_view(gray, (3, 3))
    smooth = np.median(windows, axis=(-2, -1)).astype(np.uint8)
    b = np.float32(np.median(smooth))
    s = np.float32(smooth[15, 15])
    return float(np.float32(b - s) / np.maximum(b, np.float32(1)))


def metrics(rows, threshold, identifier, tile=False):
    ink = [r for r in rows if r['label'] == 'ink']
    paper = [r for r in rows if r['label'] == 'paper']
    check(ink and paper, 'Both label classes required')
    tp = sum(float(r['score']) >= threshold for r in ink)
    fp = sum(float(r['score']) >= threshold for r in paper)
    recall, specificity = tp / len(ink), (len(paper)-fp) / len(paper)
    return dict(id=identifier, n_ink=len(ink), n_paper=len(paper), tp=tp,
                fn=len(ink)-tp, tn=len(paper)-fp, fp=fp, ink_recall=recall,
                paper_specificity=specificity,
                **{'pass': recall >= (0.75 if tile else 0.90)
                   and specificity >= (0.75 if tile else 0.95)})


def reconstruct_result(features, tiles):
    """Reconstruct gates without reading the recorded threshold or result."""
    calibration = [r for r in features if r['role'] == 'calibration']
    held = [r for r in features if r['role'] == 'held_labels']
    threshold = next((t for t in GRID if all(
        metrics([r for r in calibration if r['page'] == p], t, p)
        ['paper_specificity'] >= 0.95 for p in ('f76r', 'f77r'))), None)
    calibration_pages, held_pages, tile_metrics = [], [], []
    calibration_pass = held_pass = False
    if threshold is not None:
        calibration_pages = [metrics([r for r in calibration if r['page'] == p],
                                     threshold, p) for p in ('f76r', 'f77r')]
        tile_metrics = [metrics([r for r in calibration if r['tile_id'] == t['tile_id']],
                                threshold, t['tile_id'], tile=True)
                        for t in tiles if t['role'] == 'calibration']
        calibration_pass = all(m['pass'] for m in calibration_pages + tile_metrics)
        if calibration_pass:
            check(len(held) == 96, 'Passing calibration requires all 96 held labels')
            held_pages = [metrics([r for r in held if r['page'] == p], threshold, p)
                          for p in ('f81r', 'f83r')]
            held_tiles = [metrics([r for r in held if r['tile_id'] == t['tile_id']],
                                  threshold, t['tile_id'], tile=True)
                          for t in tiles if t['role'] == 'held_labels']
            tile_metrics += held_tiles
            held_pass = all(m['pass'] for m in held_pages + held_tiles)
    if not calibration_pass:
        check(not held, 'Held features must not be measured after calibration stop')
    status = ('CALIBRATION_STOP' if not calibration_pass else
              'RESTRICTED_POINT_CONTROL_PASS' if held_pass else 'HELD_POINT_CONTROL_FAIL')
    return dict(status=status, selected_threshold=threshold,
                calibration_pages=calibration_pages, held_pages=held_pages,
                tiles=tile_metrics, calibration_pass=calibration_pass,
                held_pass=held_pass,
                baselines={'all_paper': {'ink_recall': 0, 'paper_specificity': 1, 'pass': False},
                           'all_ink': {'ink_recall': 1, 'paper_specificity': 0, 'pass': False}},
                counts={'labels_total': 192, 'calibration_labels': 96,
                        'held_labels_scored': len(held)})


def compare(expected, actual, location='result'):
    """Every reconstructed field must agree; extra explanatory fields allowed."""
    if isinstance(expected, dict):
        check(isinstance(actual, dict), location + ': expected object')
        for key, value in expected.items():
            check(key in actual, location + ': missing ' + key)
            compare(value, actual[key], location + '.' + key)
    elif isinstance(expected, list):
        check(isinstance(actual, list) and len(expected) == len(actual), location + ': list length')
        if expected and isinstance(expected[0], dict) and 'id' in expected[0]:
            expected = sorted(expected, key=lambda r: r['id'])
            actual = sorted(actual, key=lambda r: r['id'])
        for i, (a, b) in enumerate(zip(expected, actual)):
            compare(a, b, location + '[' + str(i) + ']')
    elif isinstance(expected, bool) or expected is None:
        check(actual is expected, location + ': boolean/null mismatch')
    elif isinstance(expected, (int, float)):
        check(isinstance(actual, (int, float)) and not isinstance(actual, bool)
              and math.isfinite(actual) and abs(expected-actual) <= 1e-10,
              location + ': numeric mismatch')
    else:
        check(actual == expected, location + ': value mismatch')


def validate_inventory(tiles, sources, labels):
    check(len(tiles) == 24, 'Exactly 24 registered tiles')
    tile_map = {t['tile_id']: t for t in tiles}
    source_map = {s['page']: s for s in sources}
    check(len(tile_map) == 24, 'Unique tile IDs')
    check(len(sources) == 4 and set(source_map) == set(PAGES), 'Four admitted sources only')
    check(Counter(t['page'] for t in tiles) == Counter({p: 6 for p in PAGES}), 'Six tiles per page')
    for tile in tiles:
        check(tile['page'] in PAGES and tile['role'] == PAGES[tile['page']], 'Tile role')
        source = source_map[tile['page']]
        check(tile['width'] == tile['height'] == 192, 'Native 192px tiles')
        check(tile['source_sha256'] == source['sha256'], 'Tile source binding')
        check(16 <= tile['x0'] and tile['x0'] + 208 <= source['width'] and
              16 <= tile['y0'] and tile['y0'] + 208 <= source['height'], 'Real source halo bounds')
    check(len(labels) == 192 and len({r['label_id'] for r in labels}) == 192,
          'Exactly 192 uniquely identified labels')
    seen = set()
    for row in labels:
        check(row['tile_id'] in tile_map, 'Label tile exists')
        tile = tile_map[row['tile_id']]
        check(row['page'] == tile['page'] and row['role'] == tile['role'], 'Label provenance')
        check(row['label'] in ('ink', 'paper'), 'Registered label classes')
        x, y = int(row['x']), int(row['y'])
        check(0 <= x < 192 and 0 <= y < 192, 'Label center in native tile')
        key = (row['page'], tile['x0']+x, tile['y0']+y)
        check(key not in seen, 'No repeated source center')
        seen.add(key)
    counts = Counter((r['tile_id'], r['label']) for r in labels)
    check(counts == Counter({(tid, label): 4 for tid in tile_map
                             for label in ('ink', 'paper')}), 'Four ink/four paper per tile')
    return tile_map, source_map


def validate_artifacts(cache_dir=None):
    lock = json.loads((SRC / 'PREREG_LOCK.json').read_text())['sha256']
    check(isinstance(lock, dict) and lock, 'Nonempty registration lock')
    for relative, expected in lock.items():
        path = BASE / relative
        check(path.resolve().is_relative_to(BASE), 'Lock path escapes experiment')
        check(digest(path) == expected, 'Registration hash: ' + relative)
    required = ['PREREGISTRATION.md', 'src/TILES.json', 'src/SOURCES.json', 'src/SPEC.json',
                'src/ANNOTATIONS_CAL.tsv', 'src/ANNOTATIONS_HELD.tsv',
                'src/measure.py', 'src/run.py', 'src/validate.py', 'src/test_measurement.py']
    check(set(required) <= set(lock), 'Lock must bind registration, annotations and executable code')
    spec = json.loads((SRC / 'SPEC.json').read_text())
    compare({'halo': 16, 'smooth_median_size': 3, 'background_median_size': 31,
             'threshold_grid_hundredths': list(range(2, 31)),
             'page_min_ink_recall': .90, 'page_min_paper_specificity': .95,
             'tile_min_ink_recall': .75, 'tile_min_paper_specificity': .75}, spec, 'spec')
    tiles = json.loads((SRC / 'TILES.json').read_text())
    sources = json.loads((SRC / 'SOURCES.json').read_text())
    cal_labels = read_tsv(SRC / 'ANNOTATIONS_CAL.tsv')
    held_labels = read_tsv(SRC / 'ANNOTATIONS_HELD.tsv')
    check(len(cal_labels) == len(held_labels) == 96, '96 labels per role')
    check(all(r['role'] == 'calibration' for r in cal_labels), 'Calibration file role')
    check(all(r['role'] == 'held_labels' for r in held_labels), 'Held file role')
    labels = cal_labels + held_labels
    tile_map, source_map = validate_inventory(tiles, sources, labels)
    label_map = {r['label_id']: r for r in labels}
    features = read_tsv(BASE / 'artifacts/FEATURES.tsv')
    check(len(features) in (96, 192), 'Measured label capacity')
    check(len({r['label_id'] for r in features}) == len(features), 'Unique feature IDs')
    for row in features:
        check(row['label_id'] in label_map, 'Feature labels are registered')
        expected = label_map[row['label_id']]
        for key in ('tile_id', 'page', 'role', 'label', 'x', 'y'):
            check(row[key] == expected[key], 'Feature label binding: ' + key)
        check(math.isfinite(float(row['score'])), 'Finite score')
    check({r['label_id'] for r in features if r['role'] == 'calibration'} ==
          {r['label_id'] for r in cal_labels}, 'All calibration labels scored exactly once')
    if len(features) == 192:
        check({r['label_id'] for r in features} == set(label_map), 'All held labels included')
    cal_features = read_tsv(BASE / 'artifacts/FEATURES_CAL.tsv')
    compare(sorted([r for r in features if r['role'] == 'calibration'], key=lambda r: r['label_id']),
            sorted(cal_features, key=lambda r: r['label_id']), 'calibration feature freeze')
    result = reconstruct_result(features, tiles)
    compare(result, json.loads((BASE / 'artifacts/RESULT.json').read_text()))
    cal_expected = {key: result[key] for key in
                    ('selected_threshold', 'calibration_pages', 'calibration_pass')}
    cal_expected['tiles'] = [m for m in result['tiles'] if
                              tile_map[m['id']]['role'] == 'calibration']
    cal_expected['features_sha256'] = digest(BASE / 'artifacts/FEATURES_CAL.tsv')
    compare(cal_expected, json.loads((BASE / 'artifacts/CALIBRATION.json').read_text()), 'calibration')
    replayed = 0
    if cache_dir is not None:
        for page, source in source_map.items():
            filename = Path(source['filename'])
            check(filename.name == str(filename), 'Source filename must be a basename')
            path = Path(cache_dir) / filename
            check(path.stat().st_size == source['bytes'], 'Source byte count: ' + page)
            check(digest(path) == source['sha256'], 'Source JPEG hash: ' + page)
            with Image.open(path) as opened:
                check(opened.size == (source['width'], source['height']), 'Native dimensions')
                image = opened.convert('RGB')
                for tile in (t for t in tiles if t['page'] == page):
                    x0, y0 = tile['x0'], tile['y0']
                    rgb = np.asarray(image.crop((x0, y0, x0+192, y0+192)))
                    check(hashlib.sha256(rgb.tobytes()).hexdigest() == tile['tile_rgb_sha256'],
                          'Unmodified native tile hash: ' + tile['tile_id'])
                for row in (r for r in features if r['page'] == page):
                    tile = tile_map[row['tile_id']]
                    x, y = tile['x0']+int(row['x']), tile['y0']+int(row['y'])
                    neighborhood = np.asarray(image.crop((x-16, y-16, x+17, y+17)))
                    score = center_score(neighborhood)
                    check(abs(score-float(row['score'])) <= 1e-11,
                          'Independent native-pixel score: ' + row['label_id'])
                    replayed += 1
    return dict(status='PASS', experiment='GDT831', registration_hashes_verified=len(lock),
                registered_labels=192, registered_tiles=24, features_verified=len(features),
                result_status=result['status'], selected_threshold=result['selected_threshold'],
                native_sources_verified=4 if cache_dir is not None else 0,
                native_tile_hashes_verified=24 if cache_dir is not None else 0,
                independent_center_pixels_replayed=replayed,
                physical_ink_or_chronology_validated=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare existing validation artifact')
    parser.add_argument('--cache-dir', type=Path, help='Replay native source hashes and center scores')
    args = parser.parse_args()
    result = validate_artifacts(args.cache_dir)
    path = BASE / 'artifacts/VALIDATION.json'
    if args.check:
        expected = json.loads(path.read_text())
        compared = dict(result)
        if args.cache_dir is None:
            for key in ('native_sources_verified', 'native_tile_hashes_verified',
                        'independent_center_pixels_replayed'):
                del compared[key]
        compare(compared, expected, 'validation')
    else:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

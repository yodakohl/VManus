#!/usr/bin/env python3
"""Synthetic controls only: no manuscript images, annotations or output masks."""
import copy
import unittest

import numpy as np
from PIL import Image

import measure
import run
import validate


def textured_paper(size=96, seed=831):
    """Sloped brown field, correlated grain, spatial texture and sparse outliers."""
    yy, xx = np.indices((size, size))
    rng = np.random.default_rng(seed)
    field = (177 + .11*xx + .06*yy + 2*np.sin(xx/7) + 1.5*np.cos(yy/9)
             + rng.integers(-5, 6, (size, size)))
    rgb = np.stack((field+25, field, field-20), axis=2)
    for y, x, offset in ((23, 25, 35), (27, 61, -35), (64, 69, 30), (67, 22, -30)):
        if y < size and x < size:
            rgb[y, x] += offset
    return np.clip(np.rint(rgb), 0, 255).astype(np.uint8)


def stroke_fixture(width=4, orientation='vertical', factor=.55):
    rgb = textured_paper()
    yy, xx = np.indices(rgb.shape[:2])
    center = rgb.shape[0]//2
    start = center-width//2
    if orientation == 'vertical':
        support = (xx >= start) & (xx < start+width)
    elif orientation == 'horizontal':
        support = (yy >= start) & (yy < start+width)
    elif orientation == 'diagonal':
        support = np.abs((xx-yy)/np.sqrt(2)) <= width/2
    else:
        raise ValueError(orientation)
    rgb[support] = np.rint(rgb[support].astype(float)*factor).astype(np.uint8)
    return rgb, support


def synthetic_rows():
    tiles, rows = [], []
    for page, role in validate.PAGES.items():
        for ordinal in range(6):
            tid = page + '_synthetic_' + str(ordinal)
            tiles.append(dict(tile_id=tid, page=page, role=role))
            for label in ('ink', 'paper'):
                for point in range(4):
                    rows.append(dict(label_id=tid+'_'+label+str(point), tile_id=tid,
                                     page=page, role=role, label=label, x=point,
                                     y=1 if label == 'ink' else 2,
                                     score=.40 if label == 'ink' else 0.0))
    return tiles, rows


class MeasurementControls(unittest.TestCase):
    def test_textured_blank_not_classified_as_ink(self):
        rgb = textured_paper()
        score = measure.score_rgb(rgb)[16:-16, 16:-16]
        self.assertGreater(float(np.std(score)), .001)
        self.assertLess(float((score >= .10).mean()), .005)

    def test_planted_stroke_cores_across_widths_and_orientations(self):
        for orientation in ('vertical', 'horizontal', 'diagonal'):
            for width in range(2, 11):
                with self.subTest(orientation=orientation, width=width):
                    rgb, support = stroke_fixture(width, orientation)
                    score = measure.score_rgb(rgb)
                    self.assertTrue(support[48, 48])
                    self.assertGreater(float(score[48, 48]), .25)
                    self.assertFalse(support[22, 60])
                    self.assertLess(float(score[22, 60]), .06)

    def test_multiplicative_light_field_approximately_preserves_core_contrast(self):
        rgb, _ = stroke_fixture(5, 'diagonal')
        yy, xx = np.indices(rgb.shape[:2])
        light = .55 + .20*xx/(rgb.shape[1]-1) + .10*yy/(rgb.shape[0]-1)
        dimmed = np.rint(rgb.astype(float)*light[..., None]).astype(np.uint8)
        original = measure.score_rgb(rgb)
        changed = measure.score_rgb(dimmed)
        self.assertLess(abs(float(original[48, 48])-float(changed[48, 48])), .025)
        self.assertGreater(float(changed[48, 48]), .25)

    def test_dense_region_exposes_median_background_limit(self):
        rgb = np.full((96, 96, 3), 220, dtype=np.uint8)
        rgb[20:76, 20:76] = 100
        score = measure.score_rgb(rgb)
        # The physical planted support contains this point, but the detector
        # cannot distinguish an extended constant dark field from local paper.
        self.assertEqual(float(score[48, 48]), 0.0)
        self.assertFalse(bool(score[48, 48] >= .10))

    def test_actual_halo_matches_larger_image_interior(self):
        rgb = textured_paper(128)
        rgb[31:106, 63:68] = np.rint(rgb[31:106, 63:68]*.5).astype(np.uint8)
        original = rgb.copy()
        image = Image.fromarray(rgb)
        tile = dict(x0=32, y0=32, width=64, height=64)
        cropped = measure.tile_scores(image, tile)
        direct = measure.score_rgb(rgb)[32:96, 32:96]
        self.assertEqual(cropped.shape, (64, 64))
        np.testing.assert_array_equal(cropped, direct)
        np.testing.assert_array_equal(rgb, original)
        np.testing.assert_array_equal(np.asarray(image), original)
        with self.assertRaises(AssertionError):
            measure.tile_scores(image, dict(x0=15, y0=32, width=64, height=64))

    def test_independent_numpy_median_center_reconstruction(self):
        rng = np.random.default_rng(8311)
        arrays = [rng.integers(40, 241, size=(33, 33, 3), dtype=np.uint8),
                  stroke_fixture(3, 'vertical')[0][32:65, 32:65],
                  textured_paper()[32:65, 32:65]]
        for rgb in arrays:
            with self.subTest(array_sum=int(rgb.sum())):
                self.assertEqual(validate.center_score(rgb), float(measure.score_rgb(rgb)[16, 16]))


class DecisionControls(unittest.TestCase):
    @staticmethod
    def both_implementations(rows, tiles):
        cal = [r for r in rows if r['role'] == 'calibration']
        calibration = run.summarize_calibration(cal, {'threshold_grid_hundredths': list(range(2, 31))})
        held = [r for r in rows if r['role'] == 'held_labels'] if calibration['calibration_pass'] else []
        actual = run.evaluate(cal, held, calibration)
        expected = validate.reconstruct_result(cal+held, tiles)
        validate.compare(expected, actual)
        return actual

    def test_two_nonconstant_classes_pass_and_constant_baselines_fail(self):
        tiles, rows = synthetic_rows()
        result = self.both_implementations(rows, tiles)
        self.assertEqual(result['status'], 'RESTRICTED_POINT_CONTROL_PASS')
        self.assertEqual(result['selected_threshold'], .02)
        self.assertFalse(result['baselines']['all_ink']['pass'])
        self.assertFalse(result['baselines']['all_paper']['pass'])

    def test_threshold_follows_worst_calibration_page_and_inclusive_comparison(self):
        tiles, rows = synthetic_rows()
        for row in rows:
            if row['page'] == 'f77r' and row['label'] == 'paper':
                row['score'] = .12
        result = self.both_implementations(rows, tiles)
        self.assertEqual(result['selected_threshold'], .13)
        self.assertEqual(result['status'], 'RESTRICTED_POINT_CONTROL_PASS')

    def test_calibration_specificity_or_recall_failure_stops_before_held(self):
        tiles, original = synthetic_rows()
        for failure in ('no_threshold', 'no_ink_recall'):
            rows = copy.deepcopy(original)
            for row in rows:
                if row['role'] == 'calibration':
                    if failure == 'no_threshold' and row['label'] == 'paper':
                        row['score'] = .40
                    if failure == 'no_ink_recall' and row['label'] == 'ink':
                        row['score'] = .01
            result = self.both_implementations(rows, tiles)
            self.assertEqual(result['status'], 'CALIBRATION_STOP')
            self.assertEqual(result['counts']['held_labels_scored'], 0)
            self.assertEqual(result['held_pages'], [])

    def test_held_failure_cannot_retune_threshold_or_hide_weak_tile(self):
        tiles, rows = synthetic_rows()
        for row in rows:
            if row['tile_id'] == 'f81r_synthetic_0' and row['label'] == 'ink' and int(row['x']) < 2:
                row['score'] = .01
        result = self.both_implementations(rows, tiles)
        self.assertEqual(result['selected_threshold'], .02)
        # 22/24 ink recall clears the page gate; 2/4 fails the tile gate.
        self.assertTrue(next(m for m in result['held_pages'] if m['id'] == 'f81r')['pass'])
        self.assertEqual(result['status'], 'HELD_POINT_CONTROL_FAIL')
        altered = copy.deepcopy(result)
        altered['selected_threshold'] = .01
        with self.assertRaises(ValueError):
            validate.compare(result, altered)


if __name__ == '__main__':
    unittest.main(verbosity=2)

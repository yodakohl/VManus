#!/usr/bin/env python3
"""Synthetic instrument controls; no manuscript pixels or bitmap outputs."""

import json
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import measure


SPEC = json.loads(Path(__file__).with_name('SPEC.json').read_text())


def vertical_fixture(paper_rgb=(240, 200, 160), width=4, height=48,
                     image_width=96, period=16, factor=0.5):
    paper = np.broadcast_to(np.asarray(paper_rgb, dtype=float),
                            (height, image_width, 3)).copy()
    pixels = paper.copy()
    for x in range(5, image_width - width, period):
        pixels[:, x:x + width] *= factor
    return pixels, paper


def assay(pixels, paper):
    return measure.patch_assay(pixels, paper, 0.35, 0.65, SPEC)


class SyntheticMeasurementControls(unittest.TestCase):
    def test_known_log_contrast_on_white_and_brown_paper(self):
        for rgb in ((240, 240, 240), (220, 180, 140)):
            with self.subTest(paper=rgb):
                pixels, paper = vertical_fixture(paper_rgb=rgb)
                ink, nuisance, core, reason = assay(pixels, paper)
                expected = np.log((np.asarray(rgb) + 1) /
                                  (np.asarray(rgb) * 0.5 + 1))
                self.assertEqual(reason, 'PASS')
                np.testing.assert_allclose(ink, expected, atol=6e-13, rtol=0)
                self.assertGreaterEqual(core, SPEC['minimum_core_pixels'])
                self.assertEqual(len(ink), len(SPEC['ink_features']))
                self.assertEqual(len(nuisance), len(SPEC['nuisance_features']))

    def test_multiplicative_lighting_is_paper_normalized(self):
        pixels, paper = vertical_fixture()
        ink1, nuisance1, core1, reason1 = assay(pixels, paper)
        ink2, nuisance2, core2, reason2 = assay(pixels * 0.5, paper * 0.5)
        self.assertEqual((reason1, reason2), ('PASS', 'PASS'))
        self.assertEqual(core1, core2)
        # The prescribed +1 pseudocount prevents exact scale invariance.
        # At paper levels >=160, a 50% lighting change moves this ratio
        # by less than 0.007 log units; raw channel darkness changes 50%.
        np.testing.assert_allclose(ink1, ink2, atol=0.007, rtol=0)
        index = SPEC['nuisance_features'].index('paper_R')
        self.assertAlmostEqual(nuisance2[index], nuisance1[index] * 0.5,
                               places=11)

    def test_blank_sparse_and_insufficient_paper_are_rejected(self):
        paper = np.full((48, 96, 3), 240.0)
        ink, nuisance, core, reason = assay(paper.copy(), paper)
        self.assertEqual((ink, nuisance, core, reason),
                         ([], [], 0, 'INSUFFICIENT_VERTICAL_CORE'))

        sparse = paper.copy()
        sparse[10:18, 20:24] = 120
        ink, nuisance, core, reason = assay(sparse, paper)
        self.assertEqual(reason, 'INSUFFICIENT_VERTICAL_CORE')
        self.assertLess(core, SPEC['minimum_core_pixels'])
        self.assertEqual((ink, nuisance), ([], []))

        crowded, crowded_paper = vertical_fixture(width=8, period=10)
        ink, nuisance, core, reason = assay(crowded, crowded_paper)
        self.assertGreaterEqual(core, SPEC['minimum_core_pixels'])
        self.assertEqual(reason, 'INSUFFICIENT_PAPER')
        self.assertEqual((ink, nuisance), ([], []))

    def test_horizontal_bars_and_short_vertical_marks_are_excluded(self):
        paper = np.full((48, 96, 3), 240.0)
        horizontal = paper.copy()
        horizontal[10:14, 8:88] = 120
        horizontal[30:34, 8:88] = 120
        _, _, core, reason = assay(horizontal, paper)
        self.assertEqual((core, reason), (0, 'INSUFFICIENT_VERTICAL_CORE'))

        short_marks = paper.copy()
        for y in (8, 20, 32):
            for x in (10, 30, 50, 70):
                short_marks[y:y + 3, x:x + 4] = 120
        _, _, core, reason = assay(short_marks, paper)
        self.assertEqual((core, reason), (0, 'INSUFFICIENT_VERTICAL_CORE'))

    def test_width_and_occupancy_are_nuisance_not_ink_features(self):
        ink_values = []
        nuisance_values = []
        for width in (3, 7):
            pixels, paper = vertical_fixture(width=width)
            ink, nuisance, _, reason = assay(pixels, paper)
            self.assertEqual(reason, 'PASS')
            ink_values.append(ink)
            nuisance_values.append(dict(zip(SPEC['nuisance_features'],
                                            nuisance)))
        np.testing.assert_allclose(ink_values[0], ink_values[1], atol=0, rtol=0)
        self.assertEqual(nuisance_values[0]['mean_run_width'], 3)
        self.assertEqual(nuisance_values[1]['mean_run_width'], 7)
        self.assertGreater(nuisance_values[1]['ink_fraction'],
                           nuisance_values[0]['ink_fraction'])
        self.assertEqual(nuisance_values[0]['log_core_count'],
                         nuisance_values[1]['log_core_count'])
        self.assertEqual(nuisance_values[0]['x_normalized'], 0.35)
        self.assertEqual(nuisance_values[0]['y_normalized'], 0.65)

    def test_extract_window_numbering_coverage_and_native_bounds(self):
        pixels, _ = vertical_fixture(paper_rgb=(240, 240, 240), width=3,
                                    period=10, height=64, image_width=300)
        images = {'synthetic': Image.fromarray(pixels.astype(np.uint8))}
        row = dict(page='synthetic', row_id='synthetic:R001',
                   source_ordinal=1, x0=17, y0=10, x1=268, y1=50)
        result = measure.extract(images, [row], SPEC)
        self.assertEqual(len(result), SPEC['windows_per_row'])
        self.assertEqual([r['column'] for r in result], list(range(12)))
        self.assertEqual([r['patch_id'] for r in result],
                         [f'synthetic:R001:W{column:02d}'
                          for column in range(12)])
        self.assertEqual(sum(r['patch_width'] for r in result), 251)
        for column, record in enumerate(result):
            self.assertEqual(record['valid'], 1)
            self.assertEqual(record['patch_height'], 40)
            self.assertEqual(record['source_ordinal'], 1)
            a, b = column * 251 // 12, (column + 1) * 251 // 12
            self.assertEqual(record['patch_width'], b - a)
            nuisance = dict(zip(SPEC['nuisance_features'],
                                json.loads(record['nuisance_json'])))
            self.assertAlmostEqual(nuisance['x_normalized'],
                                   (17 + (a + b) / 2) / 300, places=11)
            self.assertAlmostEqual(nuisance['y_normalized'], 30 / 64,
                                   places=11)
            expected = np.log(241 / 121)
            np.testing.assert_allclose(json.loads(record['ink_json']),
                                       [expected] * 3, atol=6e-13, rtol=0)
        for changed in ({'x0': -1}, {'x1': 301}, {'y0': -1},
                        {'y1': 65}, {'x0': 268}, {'y0': 50}):
            with self.subTest(invalid_bounds=changed):
                with self.assertRaisesRegex(ValueError, 'Row bounds'):
                    measure.extract(images, [dict(row, **changed)], SPEC)

        # Exercise the actual paper estimator over the full accepted width
        # interval, not only patch_assay supplied with perfect paper values.
        # A previous 9px max filter biased widths9/10 despite fixed true ink.
        # Strokes are away from strip edges; edge extrapolation is untested.
        low, high = SPEC['horizontal_run_width']
        for width in range(low, high + 1):
            with self.subTest(end_to_end_stroke_width=width):
                pixels = np.full((48, 1200, 3), 240, dtype=np.uint8)
                for x in range(10, 1200, 40):
                    pixels[:, x:x + width] = 120
                image = Image.fromarray(pixels)
                full_row = dict(page='synthetic', row_id='synthetic:R002',
                                source_ordinal=2, x0=0, y0=0,
                                x1=1200, y1=48)
                extracted = measure.extract({'synthetic': image},
                                            [full_row], SPEC)
                self.assertEqual(len(extracted), SPEC['windows_per_row'])
                for record in extracted:
                    self.assertEqual(record['valid'], 1)
                    np.testing.assert_allclose(
                        json.loads(record['ink_json']),
                        [np.log(241 / 121)] * 3, atol=0.01, rtol=0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

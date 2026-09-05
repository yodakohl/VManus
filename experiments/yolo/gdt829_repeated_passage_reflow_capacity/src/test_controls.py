#!/usr/bin/env python3
"""Synthetic controls for the actual extraction pipeline; no manuscript reads.

All source rows below are fabricated. Fictional f9xxx selectors provide only
the syntax needed to exercise page/leaf handling. Importing the runner does
not invoke its guarded source query or main function.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
IMPORT = importlib.util.spec_from_file_location('gdt829_control_runner', HERE / 'run.py')
RUN = importlib.util.module_from_spec(IMPORT)
IMPORT.loader.exec_module(RUN)
SPEC = json.loads((HERE / 'SPEC.json').read_text())
LEFT = 'abcdefghijkn'
RIGHT = 'opqrstuvwxya'


def line(page, number, groups, *, start=False, end=False, kind='P', hand='1',
         edition='ZL3b', row_number=None, gaps=None):
    """Make complete atlas-shaped rows without using the atlas or its builder."""
    gaps = gaps if gaps is not None else ['DEFINITE_SPACE'] * (len(groups) - 1)
    assert len(gaps) == len(groups) - 1
    locus = f'{page}.{number}'
    records = []
    for index, raw in enumerate(groups, 1):
        records.append(dict(
            source_group_id=f'{edition}|{locus}|G{index:03d}',
            edition=edition, locus=locus, page=page, section='SYNTHETIC',
            currier='CONTROL', hand=hand, code='=' + kind, kind=kind,
            source_row_index=str(number if row_number is None else row_number),
            source_group_index=str(index), source_group_count=str(len(groups)),
            paragraph_start=str(int(start)), paragraph_end=str(int(end)),
            left_separator='LINE_START' if index == 1 else gaps[index - 2],
            right_separator='LINE_END' if index == len(groups) else gaps[index - 1],
            ivtff_group_raw=raw))
    return records


def passage(page, final, *, ending='l', body='z', left=LEFT, right=RIGHT,
            hand='1', edition='ZL3b', uncertain=False):
    gap = 'UNCERTAIN_SMALL_SPACE' if uncertain else 'DEFINITE_SPACE'
    common = dict(hand=hand, edition=edition)
    if final:
        return (line(page, 1, [left, body + ending], start=True, gaps=[gap], **common)
                + line(page, 2, [right], end=True, **common))
    return line(page, 1, [left, body + ending, right], start=True, end=True,
                gaps=[gap, 'DEFINITE_SPACE'], **common)


def pipeline(rows):
    records = RUN.records(rows)
    base, scaffold_stats = RUN.scaffold(records)
    masked, layouts, edition_stats = [], {}, {}
    for edition in SPEC['editions']:
        segments, stats = RUN.edition_segments(records, base, edition)
        occurrences, positions, _ = RUN.occurrences(segments, edition, SPEC['flank_atoms'])
        masked.extend(occurrences)
        layouts.update(positions)
        edition_stats[edition] = stats
    recurrent, pairs, components, counts = RUN.capacity(masked, layouts, SPEC)
    return dict(masked=masked, layouts=layouts, recurrent=recurrent, pairs=pairs,
                components=components, counts=counts, scaffold=scaffold_stats,
                edition_stats=edition_stats)


class SyntheticPipelineControls(unittest.TestCase):
    def test_reflow_retains_changed_and_unchanged_endings(self):
        results = []
        for ending in ['m', 'l']:
            with self.subTest(final_ending=ending):
                result = pipeline(passage('f9001r', True, ending=ending)
                                  + passage('f9002r', False))
                self.assertEqual(len(result['masked']), 2)
                self.assertEqual(len(result['recurrent']), 2)
                self.assertEqual(len(result['pairs']), 1)
                self.assertEqual(result['counts']['ZL3b']['independent_primary_upper_bound'], 1)
                self.assertEqual(sorted(x['line_final'] for x in result['layouts'].values()), [0, 1])
                results.append(result)
        # Actual terminal value must not alter the selected masked records or capacity.
        self.assertEqual(results[0], results[1])

    def test_one_flank_atom_and_case_change_prevent_matching(self):
        for replacement in [dict(left=LEFT[:-1] + 'x'), dict(right='O' + RIGHT[1:])]:
            with self.subTest(replacement=replacement):
                result = pipeline(passage('f9001r', True)
                                  + passage('f9002r', False, **replacement))
                self.assertEqual(len(result['masked']), 2)
                self.assertEqual(result['pairs'], [])
                self.assertEqual(result['recurrent'], [])

    def test_uncertain_gap_is_preserved_without_primary_capacity(self):
        result = pipeline(passage('f9001r', True, uncertain=True)
                          + passage('f9002r', False, uncertain=True))
        self.assertEqual(len(result['pairs']), 1)
        self.assertEqual(result['counts']['ZL3b']['independent_primary_upper_bound'], 0)
        self.assertTrue(all('UNCERTAIN_SMALL_SPACE' in r['left_json'] for r in result['masked']))
        self.assertTrue(all(r['primary_certain'] == 0 for r in result['masked']))
        mismatch = pipeline(passage('f9001r', True, uncertain=True)
                            + passage('f9002r', False))
        self.assertEqual(mismatch['recurrent'], [])

    def test_paragraph_nonprose_omission_and_page_barriers_prevent_joining(self):
        page = 'f9001r'
        cases = {
            'paragraph': line(page, 1, [LEFT, 'zl'], start=True, end=True)
                         + line(page, 2, [RIGHT], start=True, end=True),
            'nonprose': line(page, 1, [LEFT, 'zl'], start=True)
                        + line(page, 2, ['x'], kind='L')
                        + line(page, 3, [RIGHT], end=True),
            'missing_locus': line(page, 1, [LEFT, 'zl'], start=True)
                             + line(page, 3, [RIGHT], end=True, row_number=2),
            'missing_row': line(page, 1, [LEFT, 'zl'], start=True)
                           + line(page, 2, [RIGHT], end=True, row_number=3),
            'panel_change': line('f9001r1', 1, [LEFT, 'zl'], start=True)
                            + line('f9001r2', 2, [RIGHT], end=True),
            'unclosed': line(page, 1, [LEFT, 'zl', RIGHT], start=True),
        }
        for name, rows in cases.items():
            with self.subTest(barrier=name):
                self.assertEqual(pipeline(rows)['masked'], [])

    def test_drawing_interruptions_prevent_joining(self):
        for barrier in ['DRAWING_INTERRUPTION', 'DRAWING_INTERRUPTION_UNALIGNED']:
            with self.subTest(barrier=barrier):
                rows = line('f9001r', 1, [LEFT, 'zl', RIGHT], start=True, end=True,
                            gaps=['DEFINITE_SPACE', barrier])
                self.assertEqual(pipeline(rows)['masked'], [])

    def test_opaque_entities_and_malformed_constructs(self):
        raw = 'A@152;[l:m]{x}<note>z'
        parsed = RUN.atoms(raw)
        self.assertEqual([atom for atom, _, _ in parsed], ['A', '@152;', '[l:m]', '{x}', '<note>', 'z'])
        self.assertTrue(all(raw[start:end] == atom for atom, start, end in parsed))
        result = pipeline(passage('f9001r', True, body='q@152;', ending='m')
                          + passage('f9002r', False, body='q@152;'))
        self.assertEqual(result['counts']['ZL3b']['independent_primary_upper_bound'], 1)
        self.assertTrue(all(json.loads(r['body_json']) == ['q', '@152;'] for r in result['masked']))
        opaque_terminal = line('f9001r', 1, [LEFT, 'z[l:m]', RIGHT], start=True, end=True)
        self.assertEqual(pipeline(opaque_terminal)['masked'], [])
        for malformed in ['@152', '@x;', '[x', '[x}', 'x]', '{x', '<x']:
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                RUN.atoms(malformed)

    def test_shared_leaf_recto_verso_merges_context_components(self):
        family_a = passage('f9001r', True, body='z') + passage('f9002r', False, body='z')
        family_b = passage('f9001v', True, body='w') + passage('f9003r', False, body='w')
        result = pipeline(family_a + family_b)
        counts = result['counts']['ZL3b']
        self.assertEqual(counts['recurrent_families'], 2)
        self.assertEqual(counts['cross_layout_pairs'], 2)
        self.assertEqual(counts['components'], 1)
        self.assertEqual(counts['independent_primary_upper_bound'], 1)
        self.assertEqual(json.loads(result['components'][0]['leaves_json']), ['f9001', 'f9002', 'f9003'])

    def test_different_and_unknown_hands_do_not_supply_primary_pairs(self):
        for hands in [('1', '2'), ('', ''), ('?', '?'), ('NA', 'NA')]:
            with self.subTest(hands=hands):
                result = pipeline(passage('f9001r', True, hand=hands[0])
                                  + passage('f9002r', False, hand=hands[1]))
                self.assertEqual(len(result['pairs']), 1)
                self.assertEqual(result['pairs'][0]['same_known_hand'], 0)
                self.assertEqual(result['counts']['ZL3b']['independent_primary_upper_bound'], 0)

    def test_alternate_layout_scaffold_preserves_missing_marker_and_line_limits(self):
        primary = passage('f9001r', True)
        alternate = passage('f9001r', True, edition='IT2a')
        for row in alternate:
            row['paragraph_start'] = row['paragraph_end'] = '0'
        retained = pipeline(primary + alternate)
        self.assertEqual(retained['edition_stats']['IT2a']['retained_segments'], 1)
        self.assertEqual(retained['edition_stats']['IT2a']['paragraph_marker_disagreements'], 2)
        self.assertEqual(sum(r['edition'] == 'IT2a' for r in retained['masked']), 1)
        for failure in ['missing_line', 'native_row_gap']:
            with self.subTest(failure=failure):
                changed = copy.deepcopy(alternate)
                if failure == 'missing_line':
                    changed = [row for row in changed if row['locus'].endswith('.1')]
                else:
                    for row in changed:
                        if row['locus'].endswith('.2'):
                            row['source_row_index'] = '3'
                result = pipeline(primary + changed)
                self.assertEqual(result['edition_stats']['IT2a']['retained_segments'], 0)
                self.assertFalse(any(r['edition'] == 'IT2a' for r in result['masked']))

    def test_capacity_boundary_uses_distinct_components(self):
        rows = []
        for index in range(32):
            body = 'z' + chr(ord('A') + index // 26) + chr(ord('A') + index % 26)
            rows += passage(f'f{9100 + 2 * index}r', True, body=body)
            rows += passage(f'f{9101 + 2 * index}r', False, body=body)
            if index in [30, 31]:
                result = pipeline(rows)
                counts = result['counts']['ZL3b']
                self.assertEqual(counts['independent_primary_upper_bound'], index + 1)
                self.assertEqual(counts['status'], 'CAPACITY_FAIL_UPPER_BOUND' if index == 30
                                 else 'POTENTIALLY_FEASIBLE_ONLY')
        design = RUN.exact_power(32)
        self.assertEqual(design['upper_critical'], 24)
        self.assertLess(design['size'], .01)
        self.assertGreater(design['power'], .8)


if __name__ == '__main__':
    unittest.main()

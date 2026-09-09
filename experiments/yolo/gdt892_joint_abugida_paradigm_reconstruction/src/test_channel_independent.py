#!/usr/bin/env python3
"""Compare independently fixture-locked control encoder with the solver channel.

Exhaustive fixed panel: every a-z word of lengths 1 through 3, all six inherent
vowels. No control plaintext, key generation, fitting or source selection.
"""
import itertools
import hashlib
import unittest
from unittest.mock import patch
import core
import make_control as independent


class IndependentChannelTests(unittest.TestCase):
    def test_independent_fixtures(self):
        self.assertEqual(independent.self_test()['status'], 'PASS')

    def test_all_words_lengths_one_through_three(self):
        count = 0
        for n in (1, 2, 3):
            for letters in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=n):
                word = ''.join(letters)
                for inherent in 'aeiouy':
                    parts = tuple(independent.components(word, inherent))
                    self.assertEqual(parts, core.components(word, inherent), (word, inherent))
                    self.assertEqual(core.decode_components(parts, inherent), word, (word, inherent))
                    count += 1
        self.assertEqual(count, 109668)

    def test_normalization_explicit_panel(self):
        panel = [('ĀVĒ', 'ave'), ('ÆŒJUV', 'aeoejuv'),
                 ('a\u0304e\u0306', 'ae'), ('Iūlius', 'iulius'),
                 ('Jūlius', 'julius'), ('VŪ', 'vu'), ('ȳ', 'y'),
                 ('ā-ē', 'a-e'), ('123', '123')]
        for raw, expected in panel:
            self.assertEqual(independent.normalize(raw), expected)
            self.assertEqual(core.normalize(raw), expected)

    def test_held_coverage_all_inherent(self):
        discovery = independent.used_components(['ba', 'be'])
        self.assertTrue(independent.covered_for_all_inherent(['babe'], discovery))
        self.assertFalse(independent.covered_for_all_inherent(['bi'], discovery))
        self.assertFalse(independent.covered_for_all_inherent(['b'], discovery))
        self.assertFalse(independent.covered_for_all_inherent(['a'], discovery))
        # Covering under one inherent value does not establish all-six coverage.
        partial = {v: set(s) for v, s in discovery.items()}
        partial['y'].remove('V:a')
        self.assertFalse(independent.covered_for_all_inherent(['ba'], partial))

    def test_complete_mwt_exclusion(self):
        ordinary = '\n'.join('%d\tba\tba\tNOUN\t_\t_\t0\troot\t_\t_' % i for i in range(1, 7))
        punct = '\n7\t.\t.\tPUNCT\t_\t_\t1\tpunct\t_\t_'
        mwt = '\n1-2\tbaba\t_\t_\t_\t_\t_\t_\t_\t_'
        raw = ('# sent_id = ordinary\n' + ordinary + punct + '\n\n' +
               '# sent_id = mwt\n' + ordinary + mwt + '\n\n').encode()
        with patch.object(independent, 'SOURCE_SHA256', hashlib.sha256(raw).hexdigest()):
            with patch.object(independent.Path, 'read_bytes', return_value=raw):
                rows = list(independent.source_sentences('synthetic-fixture.conllu'))
        self.assertEqual(rows, [('ordinary', ['ba'] * 6)])


if __name__ == '__main__':
    unittest.main(verbosity=2)

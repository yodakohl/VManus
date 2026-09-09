#!/usr/bin/env python3
"""Source-intake boundary and fidelity tests; no target data."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import source


def element(text):
    return ET.fromstring('<ab xmlns="%s" type="recipe">%s</ab>' % (source.TEI, text))


class SourceTests(unittest.TestCase):
    def test_inline_notes_pb_tails(self):
        e = element('A<ingredient en="secret">pfel</ingredient>n<note>EDITOR WORDS</note> sa<pb n="PRIVATE"/>ft')
        self.assertEqual(source.mixed_text(e), 'Apfeln saft')

    def test_titles_remain_in_position(self):
        e = element('<opener>Ein <title key="English">guot <dish>muos</dish></title> wil</opener> haben')
        self.assertEqual(source.mixed_text(e), 'Ein guot muos wil haben')

    def test_unknown_and_uncertain_fail_closed(self):
        for tag in ('choice', 'supplied', 'unclear', 'gap', 'unexpected'):
            with self.assertRaises(ValueError):
                source.mixed_text(element('<%s>word</%s>' % (tag, tag)))

    def test_authorial_alternatives_kept(self):
        e = element('<alternative>wein oder wasser</alternative> und <title type="none" key="NO"/>milch')
        self.assertEqual(source.mixed_text(e), 'wein oder wasser und milch')

    def test_no_gap_bridging(self):
        raw = 'ab[editor]cd...ef…gh[nested[x]]ij'
        self.assertEqual([s for a, b, s in source.split_segments(raw)], ['ab', 'cd', 'ef', 'gh', 'ij'])
        for a, b, text in source.split_segments(raw):
            self.assertEqual(raw[a:b], text)
        self.assertEqual([s for a, b, s in source.split_segments('ab[unfinished')], ['ab'])
        self.assertEqual([s for a, b, s in source.split_segments('a]b')], ['a', 'b'])

    def test_unicode_normalization_and_original_spans(self):
        raw = 'A\u0304, Œ ß UV ij 12²—İ!'
        words, spans = source.tokenize(raw)
        self.assertEqual(words, ['ā', 'œ', 'ß', 'uv', 'ij', '12²', 'i\u0307'])
        self.assertEqual(spans[0], [0, 2])
        self.assertEqual([raw[a:b] for a, b in spans], ['A\u0304', 'Œ', 'ß', 'UV', 'ij', '12²', 'İ'])

    def test_nested_recipes_once(self):
        root = ET.fromstring('<TEI xmlns="%s"><text><body><div><ab type="recipe" xml:id="a">one <ab type="recipe" xml:id="b">two</ab> three</ab><ab type="recipe" xml:id="c">four</ab></div></body></text></TEI>' % source.TEI)
        recipes = list(source.top_recipes(root))
        self.assertEqual([r.get(source.XML_ID) for r in recipes], ['a', 'c'])
        self.assertEqual(source.mixed_text(recipes[0]), 'one two three')

    def test_literal_lacuna(self):
        for raw in ('w[…]rd', '[...]', '[text …]'):
            self.assertIsNotNone(source.LACUNA.search(raw))

    def test_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'fixture.txt'
            p.write_bytes(b'original')
            self.assertEqual(source.verified(p, hashlib.sha256(b'original').hexdigest()), b'original')
            with self.assertRaises(ValueError):
                source.verified(p, hashlib.sha256(b'changed').hexdigest())


if __name__ == '__main__':
    unittest.main(verbosity=2)

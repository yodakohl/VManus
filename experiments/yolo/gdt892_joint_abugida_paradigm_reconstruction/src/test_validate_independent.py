"""Invented fixtures only: parser, full-word CV scan and independent grammar."""
import unittest
import validate as v


def row(n, word, upos='NOUN'):
    return '\t'.join([str(n), word, word, upos, '_', '_', '0', 'root', '_', '_'])


def sentence(sid, words, extra=''):
    return '# sent_id = ' + sid + '\n' + '\n'.join(row(i, w) for i, w in enumerate(words, 1)) + ('\n' + extra if extra else '')


def grammar():
    # One tag X, roots are one or more X tokens through recursive dependency.
    return {'tags': [['X']], 'start': 1, 'productions': [
        {'lhs': 1, 'rhs': [['N', 0]]},
        {'lhs': 0, 'rhs': [['T', 0]]},
        {'lhs': 0, 'rhs': [['T', 0], ['N', 0]]}]}


class IndependentTests(unittest.TestCase):
    def test_cv_fixtures(self):
        cases = [('bra', 'a', ['C:b', 'VIRAMA', 'C:r']),
                 ('ae', 'e', ['CARRIER', 'V:a', 'CARRIER']),
                 ('qu', 'a', ['C:q', 'V:u']),
                 ('bai', 'a', ['C:b', 'CARRIER', 'V:i']),
                 ('juv', 'u', ['C:j', 'C:v', 'VIRAMA'])]
        for word, vowel, expected in cases:
            self.assertEqual(v.encode_parts(word, vowel), expected)
        with self.assertRaises(ValueError):
            v.encode_parts('a-b', 'a')

    def test_normalization(self):
        self.assertEqual(v.normalized('ĀVĒ'), 'ave')
        self.assertEqual(v.normalized('ÆŒJUV'), 'aeoejuv')

    def test_complete_sentence_exclusions(self):
        six = ['ba'] * 6
        blocks = [sentence('ok', six, row(7, '.', 'PUNCT')),
                  sentence('mwt', six, row('1-2', 'baba')),
                  sentence('badlex', ['ba'] * 5 + ['12']),
                  sentence('short', ['ba'] * 5),
                  sentence('long', ['ba'] * 17),
                  sentence('empty_node_ok', six, row('1.1', 'ghost')),
                  sentence('final_without_blank', six)]
        eligible, counts = v.parse_source('\n\n'.join(blocks).encode())
        self.assertEqual([sid for sid, _ in eligible], ['ok', 'empty_node_ok', 'final_without_blank'])
        self.assertEqual(counts['source_blocks_examined'], 7)
        self.assertEqual(counts['excluded_mwt_sentences'], 1)
        self.assertEqual(counts['excluded_invalid_sentences'], 1)
        self.assertEqual(counts['excluded_length_sentences'], 2)
        self.assertEqual(len(eligible[0][1]), 6)

    def test_independent_complete_grammar(self):
        g = grammar()
        self.assertTrue(v.accepts_reference(g, [[('X',)]] * 6))
        self.assertFalse(v.accepts_reference(g, [[('X',)], [('Y',)]]))
        self.assertFalse(v.accepts_reference(g, []))
        # Require an ordered two-tag production, no skipping and no tag mixing.
        g = {'tags': [['N'], ['V']], 'start': 2, 'productions': [
            {'lhs': 2, 'rhs': [['T', 0], ['T', 1]]}]}
        self.assertTrue(v.accepts_reference(g, [[('N',)], [('V',)]]))
        self.assertFalse(v.accepts_reference(g, [[('V',)], [('N',)]]))
        self.assertFalse(v.accepts_reference(g, [[('N',)], [('V',)], [('V',)]]))

    def test_all_vowels_coverage_and_source_order(self):
        cache = {'forms': ['ba', 'be'], 'analyses': {'ba': [('X',)], 'be': [('X',)]},
                 'grammar': grammar()}
        # Discovery 'ba' does not include V:e for inherent a. Reject a whole
        # 'be' sentence; following 'ba' sentence still qualifies, preserving D.
        rows = [('D' + str(i), ['ba'] * 6) for i in range(12)]
        rows += [('reject', ['be'] * 6), ('held', ['ba'] * 6)]
        counts, traversal = v.select_all(rows, cache)
        self.assertEqual(counts['discovery_selected'], 12)
        self.assertEqual(counts['held_selected'], 1)
        self.assertEqual(counts['held_component_coverage_declines'], 1)
        self.assertEqual(counts['grammar_admitted'], 14)
        self.assertTrue(traversal['full_source_exhausted'])
        self.assertEqual(traversal['eligible_sentences_examined'], 14)


if __name__ == '__main__':
    unittest.main()

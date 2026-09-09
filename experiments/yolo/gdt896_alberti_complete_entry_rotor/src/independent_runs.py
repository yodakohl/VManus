"""Independent source projection, conservative run language, forward encoder.

Pure functions: no source files, manuscript packets, or network access.
The run language forgets ring consistency; acceptance is NOT a rotor solution.
"""
from itertools import groupby
import re

LETTERS = 'abcdefgilmnopqrstuxz'
OUTER = LETTERS + '1234'
assert len(LETTERS) == 20 and len(set(OUTER)) == 24


def source_projection(entries):
    """Preserve entry IDs and aliases; perform only literal j->i and v->u.

    Input: iterable of dicts with unique 'id' and list/tuple 'words'.
    Output: {'entries': [{'id', 'plain'}], 'exclusions': [{'id', 'reason'}]}.
    Input words are the already frozen ASCII-lowercase GDT895 words. No
    abbreviation expansion, h-deletion, case folding, or punctuation cleaning.
    """
    accepted, excluded, seen = [], [], set()
    for entry in entries:
        identifier, words = entry['id'], entry['words']
        if identifier in seen:
            raise ValueError('duplicate entry ID')
        seen.add(identifier)
        if not isinstance(words, (list, tuple)):
            raise ValueError('words must be a list or tuple')
        if not words:
            excluded.append({'id': identifier, 'reason': 'empty_entry'})
            continue
        if any(not isinstance(w, str) or re.fullmatch('[a-z]+', w) is None
               for w in words):
            excluded.append({'id': identifier, 'reason': 'not_frozen_ascii_words'})
            continue
        plain = ''.join(words).replace('j', 'i').replace('v', 'u')
        bad = sorted(set(plain) - set(LETTERS))
        if bad:
            excluded.append({'id': identifier, 'reason': 'outer_alphabet_violation',
                             'characters': bad})
        else:
            accepted.append({'id': identifier, 'plain': plain})
    return {'entries': accepted, 'exclusions': excluded}


def _index(j):
    if isinstance(j, str) and j in LETTERS and len(j) == 1:
        return LETTERS.index(j)
    if type(j) is int and 0 <= j < 20:
        return j
    raise ValueError('index must be one ordinary outer letter or integer0..19')


def run_accepts(cipher, plain, j):
    """Exact membership in the independent-run relaxation, not in the cipher.

    Initial c^r emits j^(r-1). Each subsequent maximal run of length r emits
    some y^r OR j^(r-1). State is a set of consumed plaintext positions.
    Every cipher run and every plaintext letter must be consumed.
    """
    j = _index(j)
    if not isinstance(cipher, str) or re.fullmatch('[a-z]*', cipher) is None:
        raise ValueError('cipher must be lowercase ASCII')
    if not isinstance(plain, str) or any(c not in LETTERS for c in plain):
        raise ValueError('plain must already use the20-letter outer alphabet')
    if not cipher:
        return False
    runs = [sum(1 for _ in group) for _, group in groupby(cipher)]
    n, size = len(cipher), len(plain)
    if not n - len(runs) <= size <= n - 1:
        return False
    index_letter = LETTERS[j]
    first = runs[0] - 1
    if plain[:first] != index_letter * first:
        return False
    reachable = {first}
    # Same-letter suffix lengths permit constant-time block comparisons.
    same = [0] * (size + 1)
    for pos in range(size - 1, -1, -1):
        same[pos] = 1 + (same[pos + 1] if pos + 1 < size and
                        plain[pos] == plain[pos + 1] else 0)
    minimum_left = sum(r - 1 for r in runs[1:])
    maximum_left = sum(runs[1:])
    for width in runs[1:]:
        minimum_left -= width - 1
        maximum_left -= width
        next_positions = set()
        for pos in reachable:
            if pos < size and same[pos] >= width:
                next_positions.add(pos + width)
            count = width - 1
            if count == 0 or (pos < size and plain[pos] == index_letter and
                              same[pos] >= count):
                next_positions.add(pos + count)
        reachable = {pos for pos in next_positions
                     if pos + minimum_left <= size <= pos + maximum_left}
        if not reachable:
            return False
    return size in reachable


def forward_encode(plain, key, index, initial, controls_before_position=None):
    """Encode using an explicit control plan, with no inferred/fitted choices.

    key maps ciphertext characters to distinct ring positions0..23 (possibly
    partial); index is an ordinary outer letter or0..19; initial is one mapped
    ciphertext character. controls_before_position maps offsets0..len(plain)
    to lists of digit POSITIONS20..23, not numeric digit values1..4.
    Repeated and trailing controls are allowed in the declared mechanical
    superset. Unmapped required output positions raise, never invent glyphs.
    """
    j = _index(index)
    if not isinstance(plain, str) or any(c not in LETTERS for c in plain):
        raise ValueError('invalid projected plaintext')
    if any(not isinstance(c, str) or re.fullmatch('[a-z]', c) is None or
           type(p) is not int or not 0 <= p < 24 for c, p in key.items()):
        raise ValueError('invalid ring key')
    if len(set(key.values())) != len(key):
        raise ValueError('noninjective ring')
    if initial not in key:
        raise ValueError('unmapped initial indicator')
    controls = {} if controls_before_position is None else controls_before_position
    for pos, digits in controls.items():
        if type(pos) is not int or not 0 <= pos <= len(plain):
            raise ValueError('control offset outside complete plaintext')
        if not isinstance(digits, (list, tuple)) or any(
                type(d) is not int or not 20 <= d < 24 for d in digits):
            raise ValueError('controls must be digit positions20..23')
    inverse = {p: c for c, p in key.items()}
    output = [initial]
    shift = (j - key[initial]) % 24
    for offset in range(len(plain) + 1):
        for digit in controls.get(offset, ()):
            position = (digit - shift) % 24
            if position not in inverse:
                raise ValueError('control requires an unobserved ring position')
            symbol = inverse[position]
            output.append(symbol)
            shift = (j - key[symbol]) % 24
        if offset < len(plain):
            position = (LETTERS.index(plain[offset]) - shift) % 24
            if position not in inverse:
                raise ValueError('payload requires an unobserved ring position')
            output.append(inverse[position])
    return ''.join(output)


def self_test():
    import itertools
    import unittest

    class Tests(unittest.TestCase):
        def test_projection(self):
            rows = [{'id': 'one', 'words': ['jvus', 'a']},
                    {'id': 'alias', 'words': ['iuus', 'a']},
                    {'id': 'whole_reject', 'words': ['a', 'ha']},
                    {'id': 'no_unicode_clean', 'words': ['á']},
                    {'id': 'no_casefold', 'words': ['A']}]
            actual = source_projection(rows)
            self.assertEqual(actual['entries'], [
                {'id': 'one', 'plain': 'iuusa'}, {'id': 'alias', 'plain': 'iuusa'}])
            self.assertEqual(len(actual['exclusions']), 3)

        def test_initial_and_whole_consumption(self):
            self.assertTrue(run_accepts('xxx', 'bb', 'b'))
            self.assertFalse(run_accepts('xxx', 'aa', 'b'))
            self.assertFalse(run_accepts('xxx', 'bbb', 'b'))
            self.assertTrue(run_accepts('xy', '', 'b'))
            self.assertFalse(run_accepts('', '', 'b'))

        def test_relaxation_is_not_rotor(self):
            self.assertTrue(run_accepts('xyyx', 'b', 'b'))
            # Exact rotor would need both x->y and y->x to be controls.
            # Summing their relative-position equations gives d1+d2=2j mod24.
            self.assertFalse(any((d1 + d2 - 2) % 24 == 0
                                 for d1 in range(20, 24) for d2 in range(20, 24)))

        def test_dfa_against_direct_generated_language(self):
            for lengths in itertools.product(range(1, 4), repeat=3):
                cipher = ''.join(c * n for c, n in zip('xyx', lengths))
                emitted = {'b' * (lengths[0] - 1)}
                for n in lengths[1:]:
                    choices = ['a' * n, 'b' * n, 'b' * (n - 1)]
                    emitted = {p + suffix for p in emitted for suffix in choices}
                for n in range(len(cipher)):
                    for letters in itertools.product('ab', repeat=n):
                        plain = ''.join(letters)
                        self.assertEqual(run_accepts(cipher, plain, 'b'), plain in emitted)

        def test_encoder_known_examples_and_partial_key(self):
            key = {c: i for i, c in enumerate('abcdefghijklmnopqrstuvwx')}
            self.assertEqual(forward_encode('b', key, 'b', 'a'), 'aa')
            self.assertEqual(forward_encode('b', key, 'b', 'a', {0: [20]}), 'att')
            self.assertEqual(forward_encode('b', {'a': 0}, 'b', 'a'), 'aa')
            with self.assertRaises(ValueError):
                forward_encode('b', {'a': 0}, 'b', 'a', {0: [20]})

        def test_encoder_direct_anchor_decoder(self):
            ring = 'abcdefghijklmnopqrstuvwx'
            key = {c: i for i, c in enumerate(ring)}
            for j in range(20):
                for plan in ({}, {0: [20, 23], 2: [21], 4: [22, 20]}):
                    cipher = forward_encode('abiu', key, j, 'q', plan)
                    anchor, decoded = cipher[0], []
                    for c in cipher[1:]:
                        value = (key[c] - key[anchor] + j) % 24
                        if value >= 20:
                            anchor = c
                        else:
                            decoded.append(LETTERS[value])
                    self.assertEqual(''.join(decoded), 'abiu')
                    self.assertTrue(run_accepts(cipher, 'abiu', j))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


if __name__ == '__main__':
    import sys
    if sys.argv[1:] != ['--self-test']:
        raise SystemExit('usage: independent_runs.py --self-test')
    raise SystemExit(0 if self_test() else 1)

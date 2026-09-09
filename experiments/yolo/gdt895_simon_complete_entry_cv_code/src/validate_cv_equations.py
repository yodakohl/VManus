"""Independent fixed-entry CV audit by binary length equations.

No target/cache access. Deadlines are absolute time.monotonic() values.
COMPLETE covers observed codebooks, not identities of unused codewords.
This local kernel cannot certify a globally assigned multi-paragraph panel.
"""
from collections import Counter
import itertools
import re
import time

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
VOWELS = 'aeiouy'


def components(word, inherent):
    """Independent transcription of the frozen GDT892 CV transformation."""
    result = []
    offset = 0
    while offset < len(word):
        letter = word[offset]
        offset += 1
        if letter in VOWELS:
            result.append('CARRIER')
            vowel = letter
        else:
            result.append('C:' + letter)
            if offset == len(word) or word[offset] not in VOWELS:
                result.append('VIRAMA')
                continue
            vowel = word[offset]
            offset += 1
        if vowel != inherent:
            result.append('V:' + vowel)
    return tuple(result)


def extendible(codebook):
    values = list(codebook.values())
    if len(values) > 27 or len(values) != len(set(values)):
        return False
    if any(len(v) not in (1, 2) or any(c not in ALPHABET for c in v)
           for v in values):
        return False
    singles = {v for v in values if len(v) == 1}
    if any(v[0] in singles for v in values if len(v) == 2):
        return False
    # Fill all remaining leaves at depth two. Adding singletons cannot increase
    # capacity. Therefore this maximum is both necessary and sufficient.
    return len(singles) + 26 * (26 - len(singles)) >= 27


def fixed_entry_solutions(source_words, cipher_words, inherent, deadline=None):
    """Return all observed component->code maps, or an explicitly partial set.

    Solves sum(count(component) * x_component) = ciphertext_length -
    component_count, for x in {0,1}. No enumeration of unobserved lengths.
    Input strings must already be strictly projected; no normalization occurs.
    """
    if inherent not in VOWELS or len(inherent) != 1:
        raise ValueError('invalid inherent vowel')
    source_words, cipher_words = tuple(source_words), tuple(cipher_words)
    if any(not isinstance(w, str) or re.fullmatch('[a-z]+', w) is None
           for w in source_words + cipher_words):
        raise ValueError('words must be nonempty lowercase ASCII')
    result = {'status': 'COMPLETE', 'solutions': [],
              'stats': {'nodes': 0, 'length_solutions': 0}}

    def expired():
        if deadline is not None and time.monotonic() >= deadline:
            result['status'] = 'UNKNOWN_BUDGET'
            return True
        return False

    if expired() or len(source_words) != len(cipher_words):
        return result
    streams = [components(w, inherent) for w in source_words]
    names = sorted({c for row in streams for c in row})
    indices = {c: i for i, c in enumerate(names)}
    equations = []
    for stream, cipher in zip(streams, cipher_words):
        counts = Counter(indices[c] for c in stream)
        required = len(cipher) - len(stream)
        if required < 0 or required > len(stream):
            return result
        equations.append((tuple(counts.items()), required))

    def propagate(values):
        while True:
            if expired():
                return False
            changed = False
            for terms, required in equations:
                remainder = required - sum(a * values[i] for i, a in terms
                                           if values[i] >= 0)
                unknown = [(i, a) for i, a in terms if values[i] < 0]
                capacity = sum(a for i, a in unknown)
                if not 0 <= remainder <= capacity:
                    return False
                if unknown and remainder in (0, capacity):
                    forced = int(remainder == capacity)
                    for i, a in unknown:
                        values[i] = forced
                    changed = True
            if not changed:
                return True

    def reconstruct(values):
        codebook = {}
        for stream, cipher in zip(streams, cipher_words):
            if expired():
                return
            pos = 0
            for component in stream:
                width = 1 + values[indices[component]]
                code = cipher[pos:pos + width]
                pos += width
                if component in codebook and codebook[component] != code:
                    return
                codebook[component] = code
            if pos != len(cipher):
                return
        if extendible(codebook):
            result['solutions'].append(dict(sorted(codebook.items())))

    def visit(values):
        if expired():
            return
        result['stats']['nodes'] += 1
        if not propagate(values):
            return
        unknown = [i for i, v in enumerate(values) if v < 0]
        if not unknown:
            result['stats']['length_solutions'] += 1
            reconstruct(values)
            return
        # Prefer a variable in the most nearly forced residual equation.
        candidates = []
        for terms, required in equations:
            pending = [(i, a) for i, a in terms if values[i] < 0]
            if pending:
                remainder = required - sum(a * values[i] for i, a in terms
                                           if values[i] >= 0)
                total = sum(a for i, a in pending)
                candidates.extend((min(remainder, total - remainder),
                                   len(pending), -a, i) for i, a in pending)
        selected = min(candidates)[3]
        for bit in (0, 1):
            if expired():
                return
            child = values.copy()
            child[selected] = bit
            visit(child)

    visit([-1] * len(names))
    return result


def self_test():
    import unittest

    class Tests(unittest.TestCase):
        def test_component_examples(self):
            self.assertEqual(components('baeb', 'a'),
                             ('C:b', 'CARRIER', 'V:e', 'C:b', 'VIRAMA'))
            self.assertEqual(components('ey', 'y'),
                             ('CARRIER', 'V:e', 'CARRIER'))

        def test_multiple_lengths(self):
            r = fixed_entry_solutions(['b'], ['xyz'], 'a')
            self.assertEqual(r['status'], 'COMPLETE')
            self.assertEqual(r['solutions'], [
                {'C:b': 'x', 'VIRAMA': 'yz'},
                {'C:b': 'xy', 'VIRAMA': 'z'}])

        def test_joint_equations_and_prefix_conflict(self):
            self.assertEqual(fixed_entry_solutions(['ba', 'b'], ['x', 'xyz'], 'a')
                             ['solutions'], [{'C:b': 'x', 'VIRAMA': 'yz'}])
            self.assertEqual(fixed_entry_solutions(['ba', 'b'], ['x', 'xxy'], 'a')
                             ['solutions'], [])
            self.assertEqual(fixed_entry_solutions(['ba', 'ba'], ['x', 'y'], 'a')
                             ['solutions'], [])
            self.assertEqual(fixed_entry_solutions(['ba', 'ca'], ['x', 'x'], 'a')
                             ['solutions'], [])

        def test_capacity(self):
            self.assertFalse(extendible({str(i): c for i, c in enumerate(ALPHABET)}))
            self.assertTrue(extendible({str(i): c for i, c in enumerate(ALPHABET[:-1])}))
            self.assertTrue(extendible({}))

        def test_deadline_and_input(self):
            self.assertEqual(fixed_entry_solutions(['ba'], ['x'], 'a', 0)['status'],
                             'UNKNOWN_BUDGET')
            with self.assertRaises(ValueError):
                fixed_entry_solutions(['Bá'], ['x'], 'a')

        def test_exhaustive_tiny_codebook_oracle(self):
            # Independent direct assignment oracle: enumerate actual short
            # strings, not length equations, on a two-character fixture alphabet.
            src = ['be', 'b']
            parts = [('C:b', 'V:e'), ('C:b', 'VIRAMA')]
            names = ['C:b', 'V:e', 'VIRAMA']
            pool = ['x', 'y', 'xx', 'xy', 'yx', 'yy']
            expected = {}
            for chosen in itertools.permutations(pool, 3):
                if any(a != b and b.startswith(a) for a in chosen for b in chosen):
                    continue
                mapping = dict(zip(names, chosen))
                words = tuple(''.join(mapping[c] for c in p) for p in parts)
                expected.setdefault(words, set()).add(tuple(sorted(mapping.items())))
            self.assertTrue(expected)
            for words, maps in expected.items():
                actual = fixed_entry_solutions(src, words, 'a')
                self.assertEqual(actual['status'], 'COMPLETE')
                self.assertEqual({tuple(sorted(m.items())) for m in actual['solutions']}, maps)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


if __name__ == '__main__':
    import sys
    if sys.argv[1:] != ['--self-test']:
        raise SystemExit('usage: validate_cv_equations.py --self-test')
    raise SystemExit(0 if self_test() else 1)

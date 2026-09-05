#!/usr/bin/env python3
"""Meaningful toy checks only; never loads historical control data."""

from collections import Counter
import csv
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference_model as model


class ReferenceModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="gdt832-reference-toy-")
        cls.directory = Path(cls.scratch.name)
        cls.sentences = [["a", "b", "a", "b"], ["a", "c"], ["d", "c"], ["b", "d"]]
        cls.reference = cls.directory / "reference.jsonl"
        cls.reference.write_text("".join(json.dumps(row) + "\n" for row in cls.sentences))
        cls.families = cls.directory / "families.json"
        cls.families.write_text(json.dumps({
            "a": ["first|NOUN", "second|VERB"],
            "b": ["first|NOUN"],
            "c": ["second|VERB"],
            "d": ["third|ADJ"],
            "unobserved": ["fourth|NOUN"],
        }))
        cls.output = cls.directory / "model"
        cls.metadata = model.build(cls.reference, cls.families, cls.output)
        cls.reader = model.load_model(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.reader.log_character.cache_clear()
        cls.reader.log_unigram.cache_clear()
        cls.scratch.cleanup()

    def test_character_rows_are_normalized_and_unknown_context_backs_off(self):
        values = self.reader.char_logp
        maximum_error = 0.0
        for offset in range(0, len(values), model.OUTPUT_COUNT):
            total = sum(math.exp(x) for x in values[offset:offset + model.OUTPUT_COUNT])
            maximum_error = max(maximum_error, abs(total - 1.0))
        self.assertLess(maximum_error, 2e-7)
        # No z appears in reference, so zzz must fall back to order zero.
        offset = ((25 * 28 + 25) * 28 + 25) * 27
        global_counts = Counter()
        for sentence in self.sentences:
            for word in sentence:
                global_counts.update(ord(c) - ord("a") for c in word)
                global_counts[model.EOS] += 1
        total = sum(global_counts.values())
        for output in range(27):
            expected = math.log((global_counts[output] + 0.1) / (total + 2.7))
            self.assertAlmostEqual(values[offset + output], expected, places=6)
        # An absent length-three context ending in BOS,BOS uses that observed suffix.
        suffix_offset = ((0 * 28 + model.BOS) * 28 + model.BOS) * 27
        initial_offset = ((model.BOS * 28 + model.BOS) * 28 + model.BOS) * 27
        self.assertEqual(list(values[suffix_offset:suffix_offset + 27]),
                         list(values[initial_offset:initial_offset + 27]))

    def test_probability_mass_and_absolute_discount(self):
        reader = self.reader
        vocabulary_mass = sum(math.exp(reader.log_unigram(word)) for word in reader.words)
        character_vocabulary_mass = sum(math.exp(reader.log_character(word)) for word in reader.words)
        tail_mass = 0.03 * (1.0 - character_vocabulary_mass)
        self.assertAlmostEqual(vocabulary_mass + tail_mass, 1.0, places=12)
        self.assertGreater(tail_mass, 0.0)
        for previous in reader.words:
            total = reader.outcounts[previous]
            multiplier = (0.5 * reader.distinct[previous] / total) if total else 1.0
            conditional_mass = sum(math.exp(reader.log_conditional(previous, word))
                                   for word in reader.words)
            self.assertAlmostEqual(conditional_mass + multiplier * tail_mass, 1.0, places=12)
        # a has two b successors and one c successor, with D=.5.
        self.assertEqual(reader.outcounts["a"], 3)
        self.assertEqual(reader.distinct["a"], 2)
        expected = (2 - 0.5) / 3 + (0.5 * 2 / 3) * math.exp(reader.log_unigram("b"))
        self.assertAlmostEqual(math.exp(reader.log_conditional("a", "b")), expected, places=12)

    def test_unknown_word_eos_and_unseen_previous_word(self):
        reader = self.reader
        unknown = "zzzz"
        self.assertTrue(math.isfinite(reader.log_unigram(unknown)))
        self.assertAlmostEqual(reader.log_unigram(unknown),
                               math.log(0.03) + reader.log_character(unknown), places=12)
        self.assertEqual(reader.log_conditional(None, unknown), reader.log_unigram(unknown))
        self.assertEqual(reader.log_conditional("neverobserved", unknown), reader.log_unigram(unknown))
        # EOS is mandatory even for a one-letter word.
        initial = ((27 * 28 + 27) * 28 + 27) * 27
        after_a = ((27 * 28 + 27) * 28 + 0) * 27
        expected = reader.char_logp[initial] + reader.char_logp[after_a + 26]
        self.assertEqual(reader.log_character("a"), expected)
        self.assertTrue(math.isfinite(reader.log_unigram("")))
        # Log-domain evaluation must not underflow on long unseen words.
        self.assertTrue(math.isfinite(reader.log_unigram("z" * 2000)))

    def test_word_order_changes_full_score_without_changing_unigrams(self):
        first = ["a", "b", "a", "b"]
        second = ["a", "a", "b", "b"]
        self.assertEqual(Counter(first), Counter(second))
        self.assertGreater(self.reader.paragraph_score(first), self.reader.paragraph_score(second))
        self.assertAlmostEqual(
            self.reader.paragraph_score(first, [True] * len(first)),
            self.reader.paragraph_score(second, [True] * len(second)), places=12,
        )
        # Sentence adjacency is not an extra training pair: b→a count is one.
        self.assertEqual(self.reader.bigrams[("b", "a")], 1)
        self.assertNotIn(("c", "d"), self.reader.bigrams)

    def test_same_plaintext_has_same_score_across_cipher_chunkings(self):
        arrangements = [[["a", "b"], ["a", "b"]], [["a"], ["b", "a", "b"]]]
        decoded = [[word for chunk in arrangement for word in chunk] for arrangement in arrangements]
        self.assertEqual(self.reader.paragraph_score(decoded[0]), self.reader.paragraph_score(decoded[1]))
        words = decoded[0]
        count = Counter(words)
        pairs = Counter(zip(words, words[1:]))
        factored = sum(number * self.reader.log_unigram(word) for word, number in count.items())
        factored += sum(number * (self.reader.log_conditional(a, b) - self.reader.log_unigram(b))
                        for (a, b), number in pairs.items())
        self.assertAlmostEqual(factored, self.reader.paragraph_score(words), places=12)
        self.assertEqual(self.reader.paragraph_score([]), 0.0)
        with self.assertRaises(ValueError):
            self.reader.paragraph_score(words, [False])

    def test_degree_preserving_rewiring_is_deterministic(self):
        edges = [(word, word % 5) for word in range(15)]
        edges += [(word, (word + 1) % 5) for word in range(15)]
        rewired, metadata = model.rewire_edges(edges)
        self.assertEqual((rewired, metadata), model.rewire_edges(reversed(edges)))
        self.assertEqual(len(rewired), len(set(rewired)))
        self.assertEqual(Counter(word for word, _ in edges), Counter(word for word, _ in rewired))
        self.assertEqual(Counter(lemma for _, lemma in edges), Counter(lemma for _, lemma in rewired))
        self.assertEqual(metadata["attempted_swaps"], 20 * len(edges))
        self.assertGreater(metadata["successful_swaps"], 0)
        self.assertGreater(metadata["fraction_changed"], 0)
        complete = [(word, lemma) for word in range(3) for lemma in range(2)]
        unchanged, counts = model.rewire_edges(complete)
        self.assertEqual(unchanged, complete)
        self.assertEqual(counts["successful_swaps"], 0)
        self.assertEqual(counts["fraction_changed"], 0.0)

    def test_exported_family_degrees_vocabulary_scope_and_binary_format(self):
        graphs = []
        for filename in ("family_real.tsv", "family_rewired.tsv"):
            with (self.output / filename).open() as stream:
                graph = [(int(row["word_id"]), int(lemma))
                         for row in csv.DictReader(stream, delimiter="\t")
                         for lemma in row["lemma_ids"].split(",") if lemma]
            graphs.append(graph)
        self.assertEqual(Counter(word for word, _ in graphs[0]), Counter(word for word, _ in graphs[1]))
        self.assertEqual(Counter(lemma for _, lemma in graphs[0]), Counter(lemma for _, lemma in graphs[1]))
        self.assertEqual(self.metadata["family_forms_outside_reference"], 1)
        self.assertNotIn("unobserved", self.reader.words)
        self.assertNotIn("fourth|NOUN", self.metadata["lemma_names_by_id"])
        self.assertEqual((self.output / "char_logp.bin").stat().st_size, 28 ** 3 * 27 * 4)
        self.assertNotIn(str(self.directory), (self.output / "model_meta.json").read_text())

    def test_bad_inputs_and_sealed_directory_are_rejected(self):
        malformed = self.directory / "malformed.jsonl"
        malformed.write_text('["Latin"]\n')
        with self.assertRaises(ValueError):
            model.build(malformed, self.families, self.directory / "bad")
        with self.assertRaises(ValueError):
            model.build(self.directory / "sealed" / "reference.jsonl", self.families,
                        self.directory / "bad")
        with self.assertRaises(ValueError):
            self.reader.log_unigram("x-y")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""C++/Python contract tests using entirely invented toy data and keys.

No experiment prepared/, world files, source control text, or sealed data is
read. All generated models, projections, binaries, and outputs are temporary.
"""

from collections import Counter
import csv
from itertools import combinations
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import reference_model
import run as orchestration


class DecoderToyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("g++") is None:
            raise unittest.SkipTest("g++ is required for the C++ contract checks")
        cls.scratch = tempfile.TemporaryDirectory(prefix="gdt832-decoder-toy-")
        cls.directory = Path(cls.scratch.name)
        cls.candidates = {
            "suffix_pool": ["a", "ae", "am", "as", "e", "em", "i", "is", "o", "os", "um", "us"],
            "wholeword_pool": ["et", "in", "non", "est", "ad", "quod", "ut", "per", "rosa", "vita", "aqua", "bona"],
        }
        cls.key = {f"L{i:02d}": chr(ord("a") + i) for i in range(26)}
        cls.key.update({f"S{i:02d}": value for i, value in enumerate(["ae", "am", "is", "us"])})
        cls.key.update({f"W{i:02d}": value for i, value in enumerate(cls.candidates["wholeword_pool"][:8])})
        cls.paragraphs = [
            ["rosa", "et", "rosae", "amat", "aquam", "in", "aqua", "zora", "rosa"],
            ["vita", "vitae", "est", "bona", "et", "aqua", "aquae"],
            ["rosae", "rosa", "non", "mala", "aqua", "aquam"],
        ]
        # These short sentences are fabricated for tests, not quotations.
        reference_sentences = [
            ["rosa", "rosae", "amat", "aquam", "et", "vita", "est", "bona"],
            ["rosae", "rosa", "amat", "vitam", "in", "aqua"],
            ["vita", "vitae", "et", "rosa", "est", "bona"],
            ["aqua", "aquae", "non", "est", "mala"],
            ["rosa", "et", "rosae", "in", "aqua"],
        ] * 3
        cls.reference_path = cls.directory / "toy_reference.jsonl"
        cls.reference_path.write_text("".join(json.dumps(p) + "\n" for p in reference_sentences))
        family_data = {
            "rosa": ["rosa|NOUN"], "rosae": ["rosa|NOUN"],
            "vita": ["vita|NOUN"], "vitae": ["vita|NOUN"], "vitam": ["vita|NOUN"],
            "aqua": ["aqua|NOUN"], "aquae": ["aqua|NOUN"], "aquam": ["aqua|NOUN"],
            "bona": ["bonus|ADJ"], "mala": ["malus|ADJ"], "amat": ["amo|VERB"],
        }
        cls.family_path = cls.directory / "toy_families.json"
        cls.family_path.write_text(json.dumps(family_data))
        cls.model_path = cls.directory / "model"
        reference_model.build(cls.reference_path, cls.family_path, cls.model_path)
        cls.model = reference_model.load(cls.model_path)
        cls.family_maps = {}
        for mode, filename in [("real", "family_real.tsv"), ("rewired", "family_rewired.tsv")]:
            memberships = {}
            with (cls.model_path / filename).open() as stream:
                for row in csv.DictReader(stream, delimiter="\t"):
                    word = cls.model.words[int(row["word_id"])]
                    memberships[word] = {int(value) for value in row["lemma_ids"].split(",") if value}
            cls.family_maps[mode] = memberships
        cls.mixed = [[cls.encode(word, mixed=True) for word in p] for p in cls.paragraphs]
        cls.literal = [[cls.encode(word, mixed=False) for word in p] for p in cls.paragraphs]
        cls.projections = {}
        for label, paragraphs in [("mixed", cls.mixed), ("literal", cls.literal)]:
            discovery = cls.directory / f"toy_{label}_discovery.json"
            discovery.write_text(json.dumps({"split": "discovery", "paragraphs": [
                {"id": f"toy_{i}", "words": paragraph} for i, paragraph in enumerate(paragraphs)
            ]}))
            projection = cls.directory / f"toy_{label}_projection.txt"
            orchestration.projection(discovery, cls.candidates, projection)
            cls.projections[label] = projection
        cls.binary = cls.directory / "decoder_check"
        subprocess.run([
            "g++", "-std=c++17", "-O1", "-DGDT832_CHECK_DELTAS",
            str(Path(__file__).with_name("decoder.cpp")), "-o", str(cls.binary),
        ], check=True, capture_output=True, text=True)
        cls.serial = 0

    @classmethod
    def tearDownClass(cls):
        cls.model.log_character.cache_clear()
        cls.model.log_unigram.cache_clear()
        cls.scratch.cleanup()

    @classmethod
    def encode(cls, word, *, mixed):
        if mixed:
            for code, output in cls.key.items():
                if code.startswith("W") and output == word:
                    return [code]
            for code, output in cls.key.items():
                if code.startswith("S") and word.endswith(output) and len(word) - len(output) >= 3:
                    return [f"L{ord(char)-ord('a'):02d}" for char in word[:-len(output)]] + [code]
        return [f"L{ord(char)-ord('a'):02d}" for char in word]

    def cpp_score(self, arm, key=None, label="mixed", expect_success=True):
        type(self).serial += 1
        key = self.key if key is None else key
        key_path = self.directory / f"toy_key_{self.serial}.tsv"
        key_path.write_text("".join(f"{code}\t{value}\n" for code, value in sorted(key.items())))
        output = self.directory / f"toy_score_{self.serial}.tsv"
        completed = subprocess.run([
            str(self.binary), "--score", str(self.model_path), str(self.projections[label]),
            arm, str(key_path), str(output),
        ], capture_output=True, text=True)
        if not expect_success:
            self.assertNotEqual(completed.returncode, 0, "malformed score request was accepted")
            return None
        self.assertEqual(completed.returncode, 0, completed.stderr)
        actual_key, scores, proposals = orchestration.parse_cpp(output)
        self.assertEqual(actual_key, key)
        self.assertEqual(proposals, 0)
        return scores

    def independent_score(self, paragraphs, key, arm):
        language = 0.0
        for paragraph in paragraphs:
            previous = None
            previous_whole = False
            for atoms in paragraph:
                word = "".join(key[atom] for atom in atoms)
                whole = len(atoms) == 1 and atoms[0].startswith("W")
                context = None if arm == "CUT" and (whole or previous_whole) else previous
                language += self.model.log_conditional(context, word)
                previous, previous_whole = word, whole
        # Independently enumerate the raw-family definition; do not reuse run.source_families.
        types = sorted({tuple(word) for paragraph in paragraphs for word in paragraph})
        pairs = [(a, b) for a, b in combinations(types, 2)
                 if len(a) >= 4 and len(a) == len(b) and a[:-1] == b[:-1]]
        degrees = Counter(word for pair in pairs for word in pair)
        family = 0.0
        memberships = self.family_maps["rewired" if arm == "REWIRED" else "real"]
        if arm != "OFF":
            for first, second in pairs:
                a, b = ("".join(key[atom] for atom in word) for word in (first, second))
                if a != b and memberships.get(a, set()) & memberships.get(b, set()):
                    family += 8.0 / max(degrees[first], degrees[second])
        return {"language_nats": language, "family_nats": family, "total_nats": language + family}

    def assert_scores_equal(self, first, second):
        for component in ("language_nats", "family_nats", "total_nats"):
            self.assertAlmostEqual(first[component], second[component], places=8, msg=component)

    def test_all_four_objectives_match_independent_python(self):
        for arm in ("FULL", "CUT", "OFF", "REWIRED"):
            with self.subTest(arm=arm):
                actual = self.cpp_score(arm)
                expected = self.independent_score(self.mixed, self.key, arm)
                self.assert_scores_equal(actual, expected)
                self.assertTrue(all(math.isfinite(x) for x in actual.values()))
        self.assertGreater(self.cpp_score("FULL")["family_nats"], 0.0)
        self.assertEqual(self.cpp_score("OFF")["family_nats"], 0.0)
        # zora is absent from the reference and occurs before another word.
        self.assertNotIn("zora", self.model.ids)
        self.assertEqual(self.model.log_conditional("zora", "rosa"), self.model.log_unigram("rosa"))

    def test_language_is_identical_for_same_plaintext_from_different_segmentation(self):
        mixed = self.cpp_score("FULL")
        literal = self.cpp_score("FULL", label="literal")
        self.assertAlmostEqual(mixed["language_nats"], literal["language_nats"], places=8)
        direct = sum(self.model.paragraph_score(p) for p in self.paragraphs)
        self.assertAlmostEqual(mixed["language_nats"], direct, places=8)

    def test_cut_resets_only_boundaries_touching_wholeword_atoms(self):
        full = self.cpp_score("FULL")
        cut = self.cpp_score("CUT")
        self.assertNotAlmostEqual(full["language_nats"], cut["language_nats"], places=6)
        self.assertEqual(full["family_nats"], cut["family_nats"])
        self.assertAlmostEqual(self.cpp_score("FULL", label="literal")["language_nats"],
                               self.cpp_score("CUT", label="literal")["language_nats"], places=8)
        # Suffix-only boundaries retain word context, including rosa -> rosae.
        index = self.paragraphs[2].index("rosa")
        self.assertFalse(any(atom.startswith("W") for atom in self.mixed[2][index - 1]))
        self.assertFalse(any(atom.startswith("W") for atom in self.mixed[2][index]))

    def test_unused_letter_key_equivalence_preserves_objective(self):
        observed = {atom for p in self.mixed for word in p for atom in word}
        self.assertNotIn("L09", observed)
        self.assertNotIn("L10", observed)
        changed = dict(self.key)
        changed["L09"], changed["L10"] = changed["L10"], changed["L09"]
        self.assert_scores_equal(self.cpp_score("FULL"), self.cpp_score("FULL", changed))

    def test_incremental_mutations_full_recompute_and_final_key_score(self):
        for arm in ("FULL", "CUT", "OFF", "REWIRED"):
            with self.subTest(arm=arm):
                output = self.directory / f"toy_mutations_{arm}.tsv"
                completed = subprocess.run([
                    str(self.binary), str(self.model_path), str(self.projections["mixed"]),
                    arm, "941", "1", "2200", "1", str(output),
                ], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                key, score, proposals = orchestration.parse_cpp(output)
                self.assertGreaterEqual(proposals, 2200)
                self.assertEqual(set(key[f"L{i:02d}"] for i in range(26)), set("abcdefghijklmnopqrstuvwxyz"))
                for prefix, count, pool in (("S", 4, self.candidates["suffix_pool"]),
                                            ("W", 8, self.candidates["wholeword_pool"])):
                    values = {key[f"{prefix}{i:02d}"] for i in range(count)}
                    self.assertEqual(len(values), count)
                    self.assertTrue(values <= set(pool))
                self.assert_scores_equal(score, self.independent_score(self.mixed, key, arm))
                self.assert_scores_equal(score, self.cpp_score(arm, key))

    def test_score_mode_rejects_invalid_arms_and_typed_key_indices(self):
        self.cpp_score("UNREGISTERED", expect_success=False)
        invalid = dict(self.key)
        del invalid["W00"]
        invalid["S04"] = self.candidates["suffix_pool"][0]
        self.cpp_score("FULL", invalid, expect_success=False)
        repeated = dict(self.key)
        repeated["S01"] = repeated["S00"]
        self.cpp_score("FULL", repeated, expect_success=False)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""GDT833 intervention checks on invented fixtures only.

These tests never open experiment prepared/, runtime/, world, or sealed data.
Any files they create, including tiny language models, live in a temporary
directory. Synthetic score direction is a software property, not a result on
the registered historical control.
"""

from collections import Counter
import copy
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parent
PREDECESSOR_SOURCE = SOURCE.parents[1] / "gdt832_joint_family_context_control" / "src"


def import_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def toy_spec():
    return {
        "letter_alphabet": "abcdefghijklmnopqrstuvwxyz",
        "suffix_values": ["um", "is", "ae", "us"],
        "wholeword_values": ["et", "in", "non", "est", "ad", "quod", "ut", "per"],
        "suffix_minimum_stem_characters": 3,
    }


class PairedReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepare = import_source("gdt833_toy_prepare", SOURCE / "prepare.py")
        cls.evaluate = import_source("gdt833_toy_evaluate", SOURCE / "evaluate.py")
        cls.reference_model = import_source(
            "gdt833_toy_reference_model", PREDECESSOR_SOURCE / "reference_model.py"
        )

    def test_pair_changes_only_v_without_reordering_or_mutating_input(self):
        original = [["vita", "uva", "zeta", "et"], ["vulva", "vivit", "in", "aqua"], []]
        frozen = copy.deepcopy(original)
        native, collapsed = self.prepare.pair_reference(original)
        self.assertEqual(original, frozen)
        self.assertEqual(native, frozen)
        self.assertEqual([len(s) for s in collapsed], [len(s) for s in frozen])
        changed = 0
        for source_sentence, target_sentence in zip(frozen, collapsed):
            for source_word, target_word in zip(source_sentence, target_sentence):
                self.assertEqual(len(source_word), len(target_word))
                self.assertEqual(target_word, source_word.replace("v", "u"))
                for old, new in zip(source_word, target_word):
                    if old != new:
                        self.assertEqual((old, new), ("v", "u"))
                        changed += 1
        self.assertEqual(changed, sum(word.count("v") for sentence in frozen for word in sentence))
        before = Counter("".join(word for sentence in frozen for word in sentence))
        after = Counter("".join(word for sentence in collapsed for word in sentence))
        self.assertEqual(after["v"], 0)
        self.assertEqual(after["u"], before["u"] + before["v"])
        self.assertEqual(after["z"], before["z"])
        # Copying must not share nested mutable sentence lists with gold.
        native[0].append("extra")
        collapsed[1].append("extra")
        self.assertEqual(original, frozen)

    def test_one_global_key_is_bijective_and_preserves_unchanged_gold(self):
        spec = toy_spec()
        key = self.prepare.make_key(17, spec)
        self.assertEqual(key, self.prepare.make_key(17, spec))
        self.assertNotEqual(key, self.prepare.make_key(29, spec))
        self.assertEqual(set(key), {f"{prefix}{i:02d}" for prefix, count in (("L", 26), ("S", 4), ("W", 8))
                                    for i in range(count)})
        for prefix, outputs in (("L", spec["letter_alphabet"]), ("S", spec["suffix_values"]),
                                ("W", spec["wholeword_values"])):
            values = [value for code, value in key.items() if code.startswith(prefix)]
            self.assertEqual(len(values), len(set(values)))
            self.assertEqual(set(values), set(outputs))
        gold = ["vita", "zeta", "civis", "et", "dominus", "rosae", "vita"]
        frozen = list(gold)
        cipher = [self.prepare.encode_word(word, key, spec) for word in gold]
        self.assertEqual(cipher[0], cipher[-1])
        self.assertEqual(["".join(key[code] for code in encoded) for encoded in cipher], gold)
        self.prepare.pair_reference([gold])
        self.assertEqual(gold, frozen)
        self.assertIn("v", "".join(gold))
        self.assertIn("z", "".join(gold))

    def test_reference_pair_cannot_change_world_or_control_spelling(self):
        paragraphs = [
            {"paragraph_id": "toy_one", "split": "discovery", "words": ["vita", "et", "zeta"]},
            {"paragraph_id": "toy_two", "split": "held", "words": ["vita", "civis", "rosae"]},
        ]
        frozen = copy.deepcopy(paragraphs)
        first_payloads, first_truth = self.prepare.build_world(17, paragraphs, toy_spec())
        self.prepare.pair_reference([["vulva", "vivit"], ["zeta", "est"]])
        second_payloads, second_truth = self.prepare.build_world(17, paragraphs, toy_spec())
        self.assertEqual(first_payloads, second_payloads)
        self.assertEqual(first_truth, second_truth)
        self.assertEqual(paragraphs, frozen)
        self.assertEqual(first_truth["paragraphs"], frozen)
        key = first_truth["decode_map"]
        # The same source word crosses the split under exactly the same key.
        self.assertEqual(first_payloads["discovery"]["paragraphs"][0]["words"][0],
                         first_payloads["held"]["paragraphs"][0]["words"][0])
        for split, payload in first_payloads.items():
            for paragraph in payload["paragraphs"]:
                expected = next(p["words"] for p in frozen if p["paragraph_id"] == paragraph["paragraph_id"])
                self.assertEqual(["".join(key[code] for code in word) for word in paragraph["words"]], expected)

    def test_legal_global_v_z_swap_moves_both_letter_values(self):
        spec = toy_spec()
        key = self.prepare.make_key(17, spec)
        frozen_key = dict(key)
        swapped = self.evaluate.swap_vz(key)
        v_code = next(code for code, value in key.items() if code.startswith("L") and value == "v")
        z_code = next(code for code, value in key.items() if code.startswith("L") and value == "z")
        self.assertEqual(key, frozen_key)
        self.assertEqual(swapped[v_code], "z")
        self.assertEqual(swapped[z_code], "v")
        self.assertEqual(Counter(swapped.values()), Counter(key.values()))
        self.assertEqual({code for code in key if key[code] != swapped[code]}, {v_code, z_code})
        self.assertEqual({code: value for code, value in swapped.items() if code[0] != "L"},
                         {code: value for code, value in key.items() if code[0] != "L"})
        gold = ["vita", "zeta", "et"]
        cipher = [self.prepare.encode_word(word, key, spec) for word in gold]
        self.assertEqual(["".join(swapped[code] for code in word) for word in cipher], ["zita", "veta", "et"])
        self.assertEqual(gold, ["vita", "zeta", "et"])

    def test_toy_reference_intervention_can_reverse_legal_mutant_preference(self):
        # Deliberately fabricated fixture: common v-words and one rare z-word.
        sentences = [["vita", "verba", "vivit"]] * 20 + [["zeta", "est", "una"]]
        native, collapsed = self.prepare.pair_reference(sentences)
        with tempfile.TemporaryDirectory(prefix="gdt833-intervention-toy-") as scratch:
            directory = Path(scratch)
            families = directory / "empty_families.json"
            families.write_text("{}\n")
            models = {}
            for arm, reference in (("NATIVE", native), ("COLLAPSED", collapsed)):
                source = directory / f"toy_{arm}.jsonl"
                source.write_text("".join(json.dumps(s) + "\n" for s in reference))
                output = directory / f"toy_{arm}_model"
                self.reference_model.build(source, families, output)
                models[arm] = self.reference_model.load(output)
            gold = ["vita"]
            spec = toy_spec()
            key = self.prepare.make_key(17, spec)
            mutant = self.evaluate.swap_vz(key)
            cipher = [self.prepare.encode_word(word, key, spec) for word in gold]
            rival = ["".join(mutant[code] for code in word) for word in cipher]
            self.assertEqual(rival, ["zita"])
            native_gap = models["NATIVE"].paragraph_score(gold) - models["NATIVE"].paragraph_score(rival)
            collapsed_gap = models["COLLAPSED"].paragraph_score(gold) - models["COLLAPSED"].paragraph_score(rival)
            self.assertGreater(native_gap, 0)
            self.assertLess(collapsed_gap, 0)
            self.assertEqual(models["NATIVE"].metadata["N"], models["COLLAPSED"].metadata["N"])
            self.assertEqual(gold, ["vita"])
            for model in models.values():
                model.log_character.cache_clear()
                model.log_unigram.cache_clear()

    def test_word_metrics_do_not_normalize_gold_v_to_u(self):
        pairs = [("vita", "uita"), ("zeta", "zeta")]
        frozen = copy.deepcopy(pairs)
        metrics = self.evaluate.word_metrics(pairs)
        self.assertEqual(pairs, frozen)
        self.assertEqual(metrics["word_accuracy"], 0.5)
        self.assertEqual(metrics["character_accuracy"], 0.875)


class PairedFitterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = import_source("gdt833_toy_runner", SOURCE / "run.py")

    @staticmethod
    def scheduling_spec():
        return {
            "world_ids": [17, 29], "reference_conditions": ["NATIVE", "COLLAPSED"],
            "starts": [0, 1, 2], "optimizer": {"annealing_steps": 15, "polish_sweeps": 2},
        }

    def test_reference_arms_have_identical_discovery_search_budgets_and_seeds(self):
        spec = self.scheduling_spec()
        before = copy.deepcopy(spec)
        jobs = list(self.runner.fit_plan(spec))
        self.assertEqual(spec, before)
        self.assertEqual(len(jobs), 12)
        keyed = {(j["world_id"], j["reference_condition"], j["start"]): j for j in jobs}
        self.assertEqual(len(keyed), len(jobs))
        for world in spec["world_ids"]:
            for start in spec["starts"]:
                native, collapsed = (keyed[(world, arm, start)] for arm in spec["reference_conditions"])
                for name in ("seed", "steps", "sweeps", "engine_arm"):
                    self.assertEqual(native[name], collapsed[name])
                self.assertEqual(native["steps"], 15)
                self.assertEqual(native["sweeps"], 2)
                self.assertEqual(native["engine_arm"], "OFF")
        # Frequency initialization is reference-dependent; equality of starting
        # keys or recovered outputs is deliberately not a paired-design condition.
        for condition in spec["reference_conditions"]:
            self.assertEqual(len({j["seed"] for j in jobs if j["reference_condition"] == condition}), 6)

    def test_restart_selection_uses_discovery_maximum_and_never_reads_held(self):
        spec = self.scheduling_spec()
        with tempfile.TemporaryDirectory(prefix="gdt833-selection-toy-") as scratch:
            exp = Path(scratch)
            (exp / "src").mkdir()
            (exp / "src/SPEC.json").write_text(json.dumps(spec))
            fits_dir = exp / "artifacts/fits"
            fits_dir.mkdir(parents=True)
            allowed_reads = {exp / "src/SPEC.json"}
            for plan in self.runner.fit_plan(spec):
                arm, start, world = plan["reference_condition"], plan["start"], plan["world_id"]
                # Native deliberately ties starts 1/2; lowest start must win.
                objective = ([11.0, 20.0, 20.0] if arm == "NATIVE" else [7.0, 6.0, 3.0])[start]
                record = {**plan, "key": {"fixture": f"{arm}_{start}"},
                          "discovery_objective": {"total_nats": objective, "language_nats": objective, "family_nats": 0.0}}
                path = fits_dir / f"world_{world}_{arm}_start{start}.json"
                path.write_text(json.dumps(record))
                allowed_reads.add(path)
                allowed_reads.add(fits_dir / f"world_{world}_{arm}_selected.json")
            # An attractive held ranking exists only as a trap, not an input.
            (exp / "toy_held_trap.json").write_text(json.dumps({"prefer_start": 2, "score": 999999}))
            original_text, original_bytes = Path.read_text, Path.read_bytes
            reads = []

            def checked_text(path, *args, **kwargs):
                self.assertIn(path, allowed_reads, f"unexpected selector read: {path.name}")
                reads.append(path)
                return original_text(path, *args, **kwargs)

            def checked_bytes(path, *args, **kwargs):
                self.assertIn(path, allowed_reads, f"unexpected selector hash read: {path.name}")
                reads.append(path)
                return original_bytes(path, *args, **kwargs)

            with mock.patch.object(Path, "read_text", checked_text), mock.patch.object(Path, "read_bytes", checked_bytes):
                lock = self.runner.select_and_lock(spec, exp=exp)
            self.assertEqual(len(lock["restarts"]), 12)
            self.assertEqual(len(lock["selected"]), 4)
            self.assertEqual(lock["spec_sha256"], hashlib.sha256((exp / "src/SPEC.json").read_bytes()).hexdigest())
            for relative in lock["selected"]:
                selected = json.loads((exp / relative).read_text())
                expected_start = 1 if selected["reference_condition"] == "NATIVE" else 0
                self.assertEqual(selected["start"], expected_start)
            for relative, expected_hash in lock["sha256"].items():
                self.assertEqual(hashlib.sha256((exp / relative).read_bytes()).hexdigest(), expected_hash)
            self.assertTrue(reads)
            self.assertNotIn(exp / "toy_held_trap.json", reads)


if __name__ == "__main__":
    unittest.main()

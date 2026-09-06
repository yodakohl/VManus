#!/usr/bin/env python3
"""Wholeword-precedence invariants on invented fixtures; no control data read."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parent


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


class WholewordPrecedenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_source("gdt835_toy_runner", SOURCE / "run.py")
        cls.validator = load_source("gdt835_toy_validator", SOURCE / "validate.py")

    @staticmethod
    def key(whole="abcam"):
        return {
            "A": {"role": "L", "output": "a"},
            "B": {"role": "L", "output": "b"},
            "C": {"role": "L", "output": "c"},
            "M": {"role": "L", "output": "m"},
            "D": {"role": "L", "output": "d"},
            "S": {"role": "S", "output": "am"},
            "W": {"role": "W", "output": whole},
        }

    @staticmethod
    def paragraphs(*paragraphs):
        return [{"paragraph_id": f"toy_{index}", "words": words}
                for index, words in enumerate(paragraphs)]

    def audit(self, paragraphs, key):
        original_paragraphs, original_key = copy.deepcopy(paragraphs), copy.deepcopy(key)
        result = self.runner.audit_words(paragraphs, key)
        independent = self.validator.wholeword_precedence({"paragraphs": paragraphs}, key)
        self.assertEqual(paragraphs, original_paragraphs)
        self.assertEqual(key, original_key)
        for first, second in (("words", "word_occurrences"), ("word_types", "word_types"),
                              ("violating_words", "violating_word_occurrences"),
                              ("violating_types", "violating_word_types"),
                              ("passes_W_precedence", "pass")):
            self.assertEqual(result[first], independent[second])
        observed = {(tuple(row["atoms"]), row["decoded"], row["required_W"], row["occurrences"])
                    for row in result["violations"]}
        checked = {(tuple(row["atoms"]), row["decoded_output"], row["required_wholeword_code"], row["occurrences"])
                   for row in independent["violations"]}
        self.assertEqual(observed, checked)
        return result

    def test_active_wholeword_and_both_composed_aliases_count_all_occurrences(self):
        literal, suffixed = ["A", "B", "C", "A", "M"], ["A", "B", "C", "S"]
        paragraphs = self.paragraphs([["W"], literal, suffixed], [literal, suffixed, suffixed])
        result = self.audit(paragraphs, self.key())
        self.assertEqual(result["words"], 6)
        self.assertEqual(result["word_types"], 3)
        self.assertEqual(result["violating_words"], 5)
        self.assertEqual(result["violating_types"], 2)
        self.assertFalse(result["passes_W_precedence"])
        self.assertEqual(len(result["alias_classes"]), 1)
        alias = result["alias_classes"][0]
        self.assertEqual(alias["decoded"], "abcam")
        self.assertEqual({tuple(row["atoms"]): row["occurrences"] for row in alias["spellings"]},
                         {tuple(literal): 2, tuple(suffixed): 3, ("W",): 1})
        self.assertEqual({row["required_W"] for row in result["violations"]}, {"W"})

    def test_inactive_assigned_wholeword_forbids_composition_without_observed_alias(self):
        result = self.audit(self.paragraphs([["A", "B", "C", "A", "M"]]), self.key())
        self.assertFalse(result["passes_W_precedence"])
        self.assertEqual(result["violating_words"], 1)
        self.assertEqual(result["alias_classes"], [])
        self.assertEqual(result["violations"][0]["required_W"], "W")

    def test_pure_composed_alias_is_diagnostic_not_a_wholeword_failure(self):
        result = self.audit(self.paragraphs([["A", "B", "C", "A", "M"], ["A", "B", "C", "S"]]),
                            self.key(whole="different"))
        self.assertTrue(result["passes_W_precedence"])
        self.assertEqual(result["violating_words"], 0)
        self.assertEqual(result["violating_types"], 0)
        self.assertEqual(len(result["alias_classes"]), 1)
        self.assertEqual(result["alias_classes"][0]["decoded"], "abcam")

    def test_correct_singleton_carrier_and_longer_prefix_word_pass(self):
        result = self.audit(self.paragraphs([["W"], ["W"], ["A", "B", "C", "A", "M", "D"]]), self.key())
        self.assertTrue(result["passes_W_precedence"])
        self.assertEqual(result["words"], 3)
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["alias_classes"], [])

    def test_ordered_atom_sequence_is_preserved(self):
        key = self.key(whole="ab")
        paragraphs = self.paragraphs([["A", "B"], ["B", "A"], ["A", "B"]])
        result = self.audit(paragraphs, key)
        self.assertEqual(result["word_types"], 2)
        self.assertEqual(result["violating_words"], 2)
        self.assertEqual(result["violating_types"], 1)
        self.assertEqual(result["violations"][0]["atoms"], ["A", "B"])
        self.assertEqual(result["alias_classes"], [])

    def test_only_candidate_keys_own_wholeword_values_apply(self):
        # ut belongs to the historical control's published planted deck, but is
        # deliberately absent from this invented candidate key's W outputs.
        key = self.key(whole="different")
        key.update({"U": {"role": "L", "output": "u"}, "T": {"role": "L", "output": "t"}})
        result = self.audit(self.paragraphs([["U", "T"]]), key)
        self.assertTrue(result["passes_W_precedence"])
        self.assertEqual(result["violations"], [])
        # Conversely, arbitrary assigned abcam is enforced even though it is
        # not a planted historical W value; no truth deck is a detector input.
        self.assertFalse(self.audit(self.paragraphs([["A", "B", "C", "A", "M"]]), self.key())["passes_W_precedence"])

    def test_opaque_identifier_renaming_does_not_change_detection(self):
        original = self.key()
        names = {name: f"X{index:02d}" for index, name in enumerate(reversed(list(original)))}
        changed_key = {names[code]: value for code, value in original.items()}
        paragraph = [["W"], ["A", "B", "C", "S"]]
        changed = [[names[code] for code in word] for word in paragraph]
        first = self.audit(self.paragraphs(paragraph), original)
        second = self.audit(self.paragraphs(changed), changed_key)
        for field in ("words", "word_types", "violating_words", "violating_types", "passes_W_precedence"):
            self.assertEqual(first[field], second[field])
        self.assertEqual(second["violations"][0]["required_W"], names["W"])

    def test_duplicate_wholeword_outputs_are_rejected_even_when_unused(self):
        key = self.key()
        key["SECOND_UNUSED_W"] = {"role": "W", "output": "abcam"}
        paragraphs = self.paragraphs([["D"]])
        with self.assertRaises(ValueError):
            self.runner.audit_words(paragraphs, key)
        with self.assertRaises(ValueError):
            self.validator.wholeword_precedence({"paragraphs": paragraphs}, key)

    def test_empty_text_and_empty_atom_sequences_are_rejected(self):
        for paragraphs in ([], self.paragraphs([]), self.paragraphs([[]])):
            with self.subTest(paragraphs=paragraphs):
                with self.assertRaises(ValueError):
                    self.runner.audit_words(paragraphs, self.key())
                with self.assertRaises(ValueError):
                    self.validator.wholeword_precedence({"paragraphs": paragraphs}, self.key())

    def test_discovery_gate_locks_complete_toy_panel_without_reading_confirmation(self):
        with tempfile.TemporaryDirectory(prefix="gdt835-stage-gate-toy-") as scratch:
            root = Path(scratch)
            experiment, previous = root / "audit", root / "old"
            (experiment / "src").mkdir(parents=True)
            (previous / "artifacts/fits").mkdir(parents=True)
            (previous / "prepared").mkdir()
            spec = {"world_ids": [17, 29, 41], "arms": ["TYPED", "BLIND"], "starts": list(range(8))}

            def write(path, value):
                path.write_text(json.dumps(value, sort_keys=True) + "\n")

            def digest(path):
                return hashlib.sha256(path.read_bytes()).hexdigest()

            spec_path = experiment / "src/SPEC.json"
            write(spec_path, spec)
            restart_paths, hashes, allowed = [], {}, {spec_path}
            for world in spec["world_ids"]:
                for arm in spec["arms"]:
                    prefix = "typed_" if arm == "TYPED" else ""
                    cipher = previous / f"prepared/world_{world}_{prefix}discovery.json"
                    write(cipher, {"world_id": world, "split": "discovery",
                                   "paragraphs": self.paragraphs([["W"]])})
                    allowed.add(cipher)
                    for start in spec["starts"]:
                        relative = f"artifacts/fits/world_{world}_{arm}_start{start}.json"
                        path = previous / relative
                        write(path, {"world_id": world, "arm": arm, "start": start, "key": self.key()})
                        restart_paths.append(relative)
                        hashes[relative] = digest(path)
                        allowed.add(path)
            fit_lock = previous / "artifacts/FIT_LOCK.json"
            write(fit_lock, {"restarts": restart_paths, "sha256": hashes})
            allowed.add(fit_lock)
            trap = root / "confirmation_truth_trap.json"
            write(trap, {"must_not_be_read": True})
            registration = experiment / "src/PREREG_LOCK.json"
            write(registration, {
                "code_sha256": {"src/SPEC.json": digest(spec_path)},
                "discovery_input_sha256": {p.relative_to(root).as_posix(): digest(p) for p in allowed},
                # A deliberately invalid confirmation hash must not be checked
                # in the discovery stage; that would require opening the trap.
                "confirmation_input_sha256": {trap.name: "DO_NOT_INSPECT_IN_GATE"},
            })
            allowed.add(registration)
            allowed.add(experiment / "artifacts/GATE.json")
            original_text, original_bytes = Path.read_text, Path.read_bytes
            accesses = []

            def read_text(path, *args, **kwargs):
                self.assertIn(path, allowed, f"unlicensed gate payload read: {path.name}")
                accesses.append(path)
                return original_text(path, *args, **kwargs)

            def read_bytes(path, *args, **kwargs):
                self.assertIn(path, allowed, f"unlicensed gate hash read: {path.name}")
                accesses.append(path)
                return original_bytes(path, *args, **kwargs)

            with mock.patch.multiple(self.runner, E=experiment, ROOT=root, OLD=previous), \
                    mock.patch.object(Path, "read_text", read_text), \
                    mock.patch.object(Path, "read_bytes", read_bytes):
                result = self.runner.gate()
            self.assertEqual(result["keys"], 48)
            self.assertEqual(result["compatible_keys"], 48)
            self.assertFalse(result["truth_labels_used"])
            self.assertFalse(result["held_payload_used"])
            self.assertFalse(result["language_model_used"])
            self.assertFalse(result["new_key_selection"])
            lock = json.loads((experiment / "artifacts/GATE_LOCK.json").read_text())
            self.assertEqual(lock["fit_paths"], sorted(restart_paths))
            self.assertEqual(lock["gate_sha256"], digest(experiment / "artifacts/GATE.json"))
            self.assertNotIn(trap, accesses)


if __name__ == "__main__":
    unittest.main()

"""Invented-only tests; importing validate performs no source/target reads."""
import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("independent_gdt894_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def line(number, words):
    return [dict(source_group_id=f"invented:{number}:{index}", edition="RF1b", page="f103v",
                 locus=f"f103v.{number}", kind="P", source_group_index=str(index),
                 source_group_count=str(len(words)),
                 left_separator="LINE_START" if index == 1 else "DEFINITE_SPACE",
                 right_separator="LINE_END" if index == len(words) else "DEFINITE_SPACE",
                 ivtff_group_raw=word)
            for index, word in enumerate(words, 1)]


def fixture():
    rows = line(1, ["aa", "kk", "bb"]) + line(2, ["mm", "nn"]) + line(3, ["cc", "kk", "dd"])
    prediction = dict(anchor=dict(edition="RF1b", page="f103v",
                                  source_group_ids=[row["source_group_id"] for row in rows[3:5]],
                                  cipher_words=["mm", "nn"], source_words=["alpha", "beta"]),
                      conditional_map={"mm": "alpha", "nn": "beta", "kk": "known"},
                      horizons=dict(preceding=dict(offsets=[-3, -2, -1], source_words=["u", "known", "v"]),
                                    following=dict(offsets=[1, 2, 3], source_words=["w", "known", "x"])))
    return prediction, rows


class IndependentValidatorTests(unittest.TestCase):
    def test_full_bidirectional_safe_run_and_nearest_first(self):
        prediction, rows = fixture()
        result = validator.evaluate(prediction, list(reversed(rows)))
        self.assertEqual(result["status"], validator.COMPATIBLE)
        before = result["directions"]["preceding"]
        self.assertEqual([row["offset"] for row in before["comparisons"]], [-1, -2, -3])
        self.assertEqual([row["cipher_word"] for row in before["comparisons"]], ["bb", "kk", "aa"])
        self.assertEqual([row["source_word"] for row in before["comparisons"]], ["v", "known", "u"])
        self.assertEqual(before["comparisons"][1]["condition"], "KNOWN_MATCH")

    def test_known_mismatch_in_both_code_cases(self):
        for target_code in ("zz", "kk"):
            prediction, rows = fixture()
            prediction["horizons"]["following"]["source_words"][0] = "alpha"
            rows[5]["ivtff_group_raw"] = target_code
            result = validator.evaluate(prediction, rows)
            self.assertEqual(result["status"], validator.CONTRADICTED)
            self.assertEqual(result["directions"]["following"]["contradictions"][0]["condition"], "KNOWN_MISMATCH")

    def test_unknown_source_forbids_known_code(self):
        prediction, rows = fixture()
        prediction["horizons"]["following"]["source_words"][1] = "newword"
        result = validator.evaluate(prediction, rows)
        self.assertEqual(result["directions"]["following"]["contradictions"][0]["condition"], "FORBIDDEN_KNOWN_CODE")

    def test_no_new_map_or_unknown_repetition_test(self):
        prediction, rows = fixture()
        prediction["horizons"]["following"]["source_words"] = ["unmapped", "known", "unmapped"]
        frozen = copy.deepcopy(prediction)
        result = validator.evaluate(prediction, rows)
        self.assertEqual(result["status"], validator.COMPATIBLE)
        self.assertEqual(prediction, frozen)

    def test_nonliteral_barrier_stops_before_later_contradiction(self):
        prediction, rows = fixture()
        rows[5]["ivtff_group_raw"] = "c?"
        prediction["horizons"]["following"]["source_words"][1] = "alpha"
        result = validator.evaluate(prediction, rows)
        after = result["directions"]["following"]
        self.assertEqual(result["status"], validator.UNKNOWN)
        self.assertEqual(after["barrier"], {"offset": 1, "reason": "NONLITERAL_GROUP"})
        self.assertEqual(after["comparisons"], [])

    def test_safe_contradiction_survives_later_barrier(self):
        prediction, rows = fixture()
        prediction["horizons"]["following"]["source_words"][0] = "alpha"
        rows[6]["ivtff_group_raw"] = "*"
        after = validator.evaluate(prediction, rows)["directions"]["following"]
        self.assertEqual(after["status"], validator.CONTRADICTED)
        self.assertEqual(after["checked_positions"], 1)
        self.assertEqual(after["barrier"], {"offset": 2, "reason": "NONLITERAL_GROUP"})

    def test_backward_uncertain_edge_does_not_skip(self):
        prediction, rows = fixture()
        rows[2]["left_separator"] = "UNCERTAIN_SPACE"
        before = validator.evaluate(prediction, rows)["directions"]["preceding"]
        self.assertEqual(before["checked_positions"], 1)
        self.assertEqual(before["barrier"], {"offset": -2, "reason": "NONDEFINITE_SEPARATOR"})

    def test_line_boundary_both_fields_required(self):
        for index, field in ((4, "right_separator"), (5, "left_separator")):
            prediction, rows = fixture()
            rows[index][field] = "DEFINITE_SPACE"
            after = validator.evaluate(prediction, rows)["directions"]["following"]
            self.assertEqual(after["barrier"], {"offset": 1, "reason": "NONDEFINITE_SEPARATOR"})

    def test_missing_numeric_line_is_a_barrier(self):
        prediction, rows = fixture()
        for row in rows[5:]:
            row["locus"] = "f103v.4"
        after = validator.evaluate(prediction, rows)["directions"]["following"]
        self.assertEqual(after["barrier"], {"offset": 1, "reason": "MISSING_NUMERIC_LINE"})

    def test_wholeline_counts_checked_before_kind_and_raw(self):
        prediction, rows = fixture()
        rows[-1]["source_group_count"] = "4"
        rows[5]["kind"], rows[5]["ivtff_group_raw"] = "LABEL", "?"
        after = validator.evaluate(prediction, rows)["directions"]["following"]
        self.assertEqual(after["barrier"], {"offset": 1, "reason": "INVALID_LINE_COUNTS"})

    def test_missing_group_is_a_count_barrier(self):
        prediction, rows = fixture()
        rows.pop(6)
        after = validator.evaluate(prediction, rows)["directions"]["following"]
        self.assertEqual(after["barrier"], {"offset": 1, "reason": "INVALID_LINE_COUNTS"})

    def test_kind_barrier_before_raw(self):
        prediction, rows = fixture()
        rows[5]["kind"], rows[5]["ivtff_group_raw"] = "L", "?"
        after = validator.evaluate(prediction, rows)["directions"]["following"]
        self.assertEqual(after["barrier"], {"offset": 1, "reason": "NON_P_KIND"})

    def test_folio_edge_is_unknown(self):
        prediction, rows = fixture()
        prediction["horizons"]["following"]["offsets"].append(4)
        prediction["horizons"]["following"]["source_words"].append("z")
        result = validator.evaluate(prediction, rows)
        self.assertEqual(result["status"], validator.UNKNOWN)
        self.assertEqual(result["directions"]["following"]["barrier"], {"offset": 4, "reason": "FOLIO_EDGE"})

    def test_empty_source_horizon_is_not_a_contradiction(self):
        prediction, rows = fixture()
        prediction["horizons"] = {name: {"offsets": [], "source_words": []}
                                  for name in ("preceding", "following")}
        result = validator.evaluate(prediction, rows)
        self.assertEqual(result["status"], validator.COMPATIBLE)
        self.assertTrue(all(value["checked_positions"] == 0 for value in result["directions"].values()))

    def test_global_duplicate_id_or_malformed_locus_is_invalid(self):
        for key, value in (("source_group_id", "invented:2:1"), ("locus", "f103v.other")):
            prediction, rows = fixture()
            rows[-1][key] = value
            with self.assertRaisesRegex(validator.InvalidPacket, "INVALID_TARGET_SCHEMA"):
                validator.evaluate(prediction, rows)

    def test_anchor_cannot_be_repaired_or_reordered(self):
        for mutate in (lambda p, r: p["anchor"]["source_group_ids"].reverse(),
                       lambda p, r: r[3].update(ivtff_group_raw="different"),
                       lambda p, r: r[3].update(source_group_count="99"),
                       lambda p, r: p["anchor"]["source_words"].reverse()):
            prediction, rows = fixture()
            mutate(prediction, rows)
            with self.assertRaises(validator.InvalidPacket):
                validator.evaluate(prediction, rows)

    def test_noninjective_map_and_source_offset_shift_rejected(self):
        prediction, rows = fixture()
        prediction["conditional_map"]["zz"] = "alpha"
        with self.assertRaisesRegex(validator.InvalidPacket, "NONINJECTIVE"):
            validator.evaluate(prediction, rows)
        prediction, rows = fixture()
        prediction["horizons"]["following"]["offsets"] = [2, 3, 4]
        with self.assertRaisesRegex(validator.InvalidPacket, "NONCONTIGUOUS_SOURCE"):
            validator.evaluate(prediction, rows)


if __name__ == "__main__":
    print(json.dumps({"validation": "INVENTED_ROWS_ONLY",
                      "validator_sha256": sha256((HERE / "validate.py").read_bytes()).hexdigest()}), flush=True)
    unittest.main()

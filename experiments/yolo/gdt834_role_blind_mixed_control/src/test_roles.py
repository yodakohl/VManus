#!/usr/bin/env python3
"""Independent GDT834 toy checks; no prepared, fitted, or truth files read."""

from collections import Counter
import copy
import importlib.util
from itertools import combinations, product
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def candidates():
    suffixes = ["a", "ae", "am", "as", "e", "em", "i", "is", "o", "os", "um", "us"]
    wholes = ["et", "in", "non", "est", "ad", "quod", "ut", "per", "longissimo"]
    for a, b in product("abcdefghijklmnopqrstuvwxyz", repeat=2):
        word = a + b
        if word not in wholes:
            wholes.append(word)
        if len(wholes) == 128:
            break
    return {"suffix_pool": suffixes, "wholeword_pool": wholes}


class RoleInferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = module("gdt834_toy_audit", SOURCE / "role_audit.py")
        cls.evaluate = module("gdt834_toy_evaluate", SOURCE / "evaluate.py")
        cls.validate = module("gdt834_toy_validator", SOURCE / "validate.py")
        cls.runner = module("gdt834_toy_runner", SOURCE / "run.py")

    def test_position_domains_and_exact_counts_match_exhaustive_small_case(self):
        paragraphs = [[[0, 0, 0, 1], [2]]]
        domains, events = self.audit.infer_domains(paragraphs, 4)
        self.assertEqual(domains, [{"L"}, {"L", "S"}, {"L", "W"}, {"L", "S", "W"}])
        counts = self.audit.assignment_counts(domains, list(map(bool, events)), (2, 1, 1))
        legal = [roles for roles in product("LSW", repeat=4)
                 if Counter(roles) == Counter({"L": 2, "S": 1, "W": 1})
                 and all(role in domain for role, domain in zip(roles, domains))]
        self.assertEqual(counts["complete_role_assignments"], len(legal))
        self.assertEqual(counts["observable_role_assignments"], len({roles[:3] for roles in legal}))
        self.assertEqual(len(legal), 3)

    def test_nominal_unused_slots_leave_219_completions_of_67_active_partitions(self):
        # Invented observations, not the predecessor's actual token data.
        paragraph = [[i, (i + 1) % 24, (i + 2) % 24, 24 + i % 3] for i in range(24)]
        paragraph.extend([[i] for i in range(27, 35)])
        domains, events = self.audit.infer_domains([paragraph])
        counts = self.audit.assignment_counts(domains, list(map(bool, events)))
        self.assertEqual(counts["unused_slots"], 3)
        self.assertEqual(counts["complete_role_assignments"], 219)
        self.assertEqual(counts["observable_role_assignments"], 67)
        permutation = list(range(38))
        random.Random(711).shuffle(permutation)
        changed = [[[permutation[symbol] for symbol in word] for word in paragraph]]
        moved_domains, moved_events = self.audit.infer_domains(changed)
        moved_counts = self.audit.assignment_counts(moved_domains, list(map(bool, moved_events)))
        self.assertEqual(counts, moved_counts)

    def test_same_emission_equivalence_excludes_unused_roles_and_values(self):
        pools = candidates()
        key = {f"X{i:02d}": {"role": "L", "output": letter}
               for i, letter in enumerate("bacdefghijklmnopqrstuvwxyz")}
        key.update({f"X{26+i:02d}": {"role": "S", "output": value}
                    for i, value in enumerate(["ae", "am", "is", "us"])})
        key.update({f"X{30+i:02d}": {"role": "W", "output": value}
                    for i, value in enumerate(pools["wholeword_pool"][:8])})
        cipher = {"paragraphs": [{"words": [["X00", "X00", "X00", "X01"], ["X30"]]}]}
        first = self.evaluate.identifiability(cipher, key, pools)
        independent = self.validate.active_role_equivalence(cipher, key, pools)
        for field in ("role_options", "identifiable_ids", "ambiguous_ids", "inactive_ids"):
            self.assertEqual(first[field], independent[field])
        self.assertEqual(first["role_options"]["X00"], ["L"])
        self.assertEqual(first["role_options"]["X01"], ["L", "S"])
        self.assertEqual(first["role_options"]["X30"], ["W"])
        self.assertEqual(first["feasible_active_role_assignments"], 2)
        self.assertEqual(set(first["identifiable_ids"]), {"X00", "X30"})
        self.assertEqual(len(first["inactive_ids"]), 35)
        altered = copy.deepcopy(key)
        for identifier in first["inactive_ids"]:
            altered[identifier] = {"role": "MUST_NOT_BE_READ", "output": "outside_every_pool"}
        # Even the role labels of active truth rows must not determine their roles.
        for identifier in first["role_options"]:
            altered[identifier]["role"] = "MUST_NOT_BE_READ"
        self.assertEqual(first, self.evaluate.identifiability(cipher, altered, pools))
        second = self.validate.active_role_equivalence(cipher, altered, pools)
        for field in ("role_options", "identifiable_ids", "ambiguous_ids", "inactive_ids"):
            self.assertEqual(first[field], second[field])

    def test_anonymous_audit_and_projection_refuse_held_or_typed_inputs(self):
        with self.assertRaises(ValueError):
            self.audit.anonymous_payload_audit({"split": "held", "paragraphs": []})
        with self.assertRaises(ValueError):
            self.audit.anonymous_payload_audit({"split": "discovery", "paragraphs": [{"words": [["L00"]]}]})
        with tempfile.TemporaryDirectory(prefix="gdt834-source-guard-toy-") as scratch:
            directory = Path(scratch)
            # A held filename must be rejected before even attempting to open it.
            with mock.patch.object(Path, "read_text", side_effect=AssertionError("held read attempted")):
                with self.assertRaises(ValueError):
                    self.runner.projection(directory / "toy_held.json", candidates(), directory / "out", "BLIND")
            disguised = directory / "toy_discovery.json"
            disguised.write_text(json.dumps({"split": "held"}))
            with self.assertRaises(ValueError):
                self.runner.projection(disguised, candidates(), directory / "out", "BLIND")

    def test_independent_decisions_agree_on_baseline_priority_and_identifiable_role_gate(self):
        # Only public numerical registration is read; every score row is invented.
        spec = json.loads((SOURCE / "SPEC.json").read_text())
        limits = spec["overall_recovery"]
        rows = [{
            "world_id": world, "arm": arm,
            "recovery": {
                "all": {"word_accuracy": limits["minimum_word_accuracy_each_key"],
                        "character_accuracy": limits["minimum_character_accuracy_each_key"]},
                "novel_forms": {"word_accuracy": limits["minimum_novel_form_accuracy_each_key"]},
                "novel_lemmas": {"word_accuracy": limits["minimum_novel_lemma_accuracy_each_key"]},
            },
            "all_identifiable_role_outputs_correct": True,
        } for world in spec["world_ids"] for arm in spec["arms"]]

        def check_decision(case, status):
            result = self.evaluate.decide(case, spec)
            self.assertEqual(result, self.validate.scientific_decision(case, spec))
            self.assertEqual(result, self.evaluate.decide(list(reversed(case)), spec))
            self.assertEqual(result["status"], status)
            return result

        check_decision(rows, "ROLE_BLIND_RECOVERY_PASS")
        role_failure = copy.deepcopy(rows)
        next(row for row in role_failure if row["arm"] == "BLIND")["all_identifiable_role_outputs_correct"] = False
        failed = check_decision(role_failure, "ROLE_BLIND_RECOVERY_FAIL")
        self.assertTrue(failed["typed_recovery_pass"] and failed["blind_recovery_pass"])
        self.assertFalse(failed["blind_identifiable_role_output_pass"])
        baseline_failure = copy.deepcopy(role_failure)
        typed = next(row for row in baseline_failure if row["arm"] == "TYPED")
        typed["recovery"]["all"]["word_accuracy"] -= 0.000001
        check_decision(baseline_failure, "BASELINE_RECOVERY_FAIL")
        missing_novelty = copy.deepcopy(rows)
        next(row for row in missing_novelty if row["arm"] == "BLIND")["recovery"]["novel_forms"]["word_accuracy"] = None
        check_decision(missing_novelty, "ROLE_BLIND_RECOVERY_FAIL")


class RoleEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("g++") is None:
            raise unittest.SkipTest("g++ is required")
        cls.runner = module("gdt834_engine_toy_runner", SOURCE / "run.py")
        old_source = SOURCE.parents[1] / "gdt832_joint_family_context_control/src/reference_model.py"
        cls.reference = module("gdt834_toy_reference", old_source)
        cls.scratch = tempfile.TemporaryDirectory(prefix="gdt834-engine-toy-")
        cls.directory = Path(cls.scratch.name)
        cls.pools = candidates()
        sentences = [["rosa", "et", "rosae", "aqua", "aquam", "ax"],
                     ["vita", "vitae", "non", "aqua", "et"],
                     ["longissimo", "est", "bona", "rosa"]] * 3
        source = cls.directory / "toy_reference.jsonl"
        source.write_text("".join(json.dumps(row) + "\n" for row in sentences))
        families = cls.directory / "toy_families.json"
        families.write_text("{}\n")
        cls.model_path = cls.directory / "toy_model"
        cls.reference.build(source, families, cls.model_path)
        cls.model = cls.reference.load(cls.model_path)
        typed = [("L", c) for c in "abcdefghijklmnopqrstuvwxyz"]
        typed += [("S", s) for s in ["ae", "am", "is", "us"]]
        typed += [("W", w) for w in cls.pools["wholeword_pool"][:8]]
        shuffle = list(range(38))
        random.Random(711).shuffle(shuffle)
        cls.key = {f"X{shuffle[i]:02d}": {"role": role, "output": output}
                   for i, (role, output) in enumerate(typed)}
        cls.inverse = {(row["role"], row["output"]): identifier for identifier, row in cls.key.items()}
        cls.paragraphs = sentences[:2]

        def encode(word):
            if ("W", word) in cls.inverse:
                return [cls.inverse[("W", word)]]
            for suffix in ["ae", "am", "is", "us"]:
                if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                    return [cls.inverse[("L", c)] for c in word[:-len(suffix)]] + [cls.inverse[("S", suffix)]]
            return [cls.inverse[("L", c)] for c in word]

        cls.cipher = {"split": "discovery", "paragraphs": [
            {"words": [encode(word) for word in paragraph]} for paragraph in cls.paragraphs]}
        cls.discovery = cls.directory / "toy_discovery.json"
        cls.discovery.write_text(json.dumps(cls.cipher))
        cls.projection = cls.directory / "toy_projection.txt"
        cls.runner.projection(cls.discovery, cls.pools, cls.projection, "BLIND")
        cls.binary = cls.directory / "decoder"
        subprocess.run(["g++", "-std=c++17", "-O1", "-DGDT832_CHECK_DELTAS",
                        str(SOURCE / "decoder.cpp"), "-o", str(cls.binary)], check=True, capture_output=True)
        cls.serial = 0

    @classmethod
    def tearDownClass(cls):
        cls.model.log_character.cache_clear()
        cls.model.log_unigram.cache_clear()
        cls.scratch.cleanup()

    def score(self, key, *, success=True, projection=None):
        type(self).serial += 1
        key_path = self.directory / f"toy_key_{self.serial}.tsv"
        key_path.write_text("".join(f"{int(identifier[1:])}\t{row['role']}\t{row['output']}\n"
                                    for identifier, row in sorted(key.items())))
        output = self.directory / f"toy_score_{self.serial}.tsv"
        completed = subprocess.run([str(self.binary), "--score", str(self.model_path),
                                    str(projection or self.projection), "BLIND", str(key_path), str(output)],
                                   capture_output=True, text=True)
        if not success:
            self.assertNotEqual(completed.returncode, 0, "illegal role key accepted")
            return
        self.assertEqual(completed.returncode, 0, completed.stderr)
        recovered, scores, _ = self.runner.parse_result(output, "BLIND")
        self.assertEqual(recovered, key)
        expected = sum(self.model.paragraph_score([
            "".join(key[code]["output"] for code in word) for word in paragraph["words"]])
                       for paragraph in self.cipher["paragraphs"])
        self.assertAlmostEqual(scores["language_nats"], expected, places=8)
        self.assertEqual(scores["family_nats"], 0.0)
        return scores

    def test_blind_roles_and_language_score_ignore_opaque_id_order(self):
        self.score(self.key)
        self.assertTrue(any(int(code[1:]) < 26 and row["role"] != "L" for code, row in self.key.items()))

    def test_feasible_random_initialization_respects_all_roles_before_optimization(self):
        starts = []
        for ordinal, seed in enumerate((17, 29, 17)):
            output = self.directory / f"toy_initial_{ordinal}.tsv"
            completed = subprocess.run([str(self.binary), str(self.model_path), str(self.projection),
                                        "BLIND", str(seed), "1", "0", "0", str(output)],
                                       capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            key, scores, proposals = self.runner.parse_result(output, "BLIND")
            self.assertEqual(proposals, 0)
            self.assertEqual(Counter(row["role"] for row in key.values()), Counter({"L": 26, "S": 4, "W": 8}))
            for role in ("L", "S", "W"):
                values = [row["output"] for row in key.values() if row["role"] == role]
                self.assertEqual(len(values), len(set(values)))
            for paragraph in self.cipher["paragraphs"]:
                for word in paragraph["words"]:
                    for position, code in enumerate(word):
                        role = key[code]["role"]
                        if role == "W":
                            self.assertEqual(len(word), 1)
                        elif role == "S":
                            self.assertEqual(position, len(word) - 1)
                            self.assertGreaterEqual(len(word), 4)
                            self.assertTrue(all(key[previous]["role"] == "L" for previous in word[:-1]))
            self.assertAlmostEqual(scores["total_nats"], self.score(key)["total_nats"], places=8)
            starts.append(key)
        self.assertEqual(starts[0], starts[2])
        self.assertNotEqual(starts[0], starts[1])

    def test_illegal_role_positions_injectivity_and_nominal_capacities_are_rejected(self):
        key = copy.deepcopy(self.key)
        internal = self.inverse[("L", "r")]
        suffix = self.inverse[("S", "ae")]
        key[internal], key[suffix] = key[suffix], key[internal]
        self.score(key, success=False)
        key = copy.deepcopy(self.key)
        short_final = self.inverse[("L", "x")]
        unused_suffix = self.inverse[("S", "us")]
        key[short_final], key[unused_suffix] = key[unused_suffix], key[short_final]
        self.score(key, success=False)
        key = copy.deepcopy(self.key)
        key[self.inverse[("W", "in")]] = dict(key[self.inverse[("W", "et")]])
        self.score(key, success=False)
        key = copy.deepcopy(self.key)
        key[self.inverse[("S", "us")]] = {"role": "W", "output": "longissimo"}
        self.score(key, success=False)

    def test_infeasible_position_capacity_stops_before_search(self):
        source = self.directory / "toy_impossible_discovery.json"
        source.write_text(json.dumps({"split": "discovery", "paragraphs": [{
            "words": [[f"X{i:02d}" for i in range(28)]]}]}))
        projected = self.directory / "toy_impossible_projection.txt"
        self.runner.projection(source, self.pools, projected, "BLIND")
        completed = subprocess.run([str(self.binary), str(self.model_path), str(projected),
                                    "BLIND", "17", "0", "0", "0", str(self.directory / "impossible.tsv")],
                                   capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("infeasible role capacities", completed.stderr)

    def test_cross_role_swaps_long_emissions_and_incremental_cache(self):
        harness = self.directory / "toy_cache_harness.cpp"
        harness.write_text('#define main included_decoder_main\n#include "' + str(SOURCE / "decoder.cpp") + '"\n#undef main\n' + r'''
int main(int argc,char**argv) {
    try {
        Ref r(argv[1]);Problem p(argv[2]);p.configure(true);Search s(r,p,"OFF",17);
        ifstream f(argv[3]);for(int a=0;a<38;a++)f>>s.key[a];
        if(!f||!s.legal())throw runtime_error("bad harness initial key");
        s.rebuild();s.savebest();
        int S=stoi(argv[4]),W=stoi(argv[5]),unusedA=stoi(argv[6]),unusedB=stoi(argv[7]),longword=stoi(argv[8]);
        auto verify=[&]() {
            double before=s.score;auto old=s.decoded;auto edges=s.edgevalues;s.rebuild();
            if(abs(before-s.score)>1e-8)throw runtime_error("independent score rebuild mismatch");
            for(size_t i=0;i<old.size();i++)if(old[i].word!=s.decoded[i].word||old[i].id!=s.decoded[i].id||abs(old[i].uni-s.decoded[i].uni)>1e-10)throw runtime_error("decoded cache mismatch");
            for(size_t i=0;i<edges.size();i++)if(abs(edges[i]-s.edgevalues[i])>1e-9)throw runtime_error("edge cache mismatch");
            if(!s.legal())throw runtime_error("mutation broke legality");
        };
        int swaps=0;
        for(int i=0;i<500;i++) {
            for(auto pair:vector<pair<int,int>>{{S,unusedA},{W,unusedB}}) {
                int a=pair.first,b=pair.second;
                if(!s.change({{a,s.key[b]},{b,s.key[a]}},0,true))throw runtime_error("legal cross-role swap rejected");
                swaps++;verify();
                if(!s.change({{a,s.key[b]},{b,s.key[a]}},0,true))throw runtime_error("cross-role inverse rejected");
                swaps++;verify();
            }
            int old=s.key[W];
            if(!s.change({{W,longword}},0,true))throw runtime_error("long output rejected");verify();
            if(!s.change({{W,old}},0,true))throw runtime_error("long output inverse rejected");verify();
        }
        s.optimize(3000,1);verify();s.write(argv[9]);
        cout<<"CROSS_ROLE_SWAPS\t"<<swaps<<"\n";return 0;
    }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}
}
''')
        binary = self.directory / "toy_cache_harness"
        subprocess.run(["g++", "-std=c++17", "-O1", "-DGDT832_CHECK_DELTAS", str(harness), "-o", str(binary)],
                       check=True, capture_output=True)
        generic = []
        for index in range(38):
            row = self.key[f"X{index:02d}"]
            generic.append(ord(row["output"]) - ord("a") if row["role"] == "L" else
                           26 + self.pools["suffix_pool"].index(row["output"]) if row["role"] == "S" else
                           38 + self.pools["wholeword_pool"].index(row["output"]))
        key_path = self.directory / "toy_generic_key.txt"
        key_path.write_text(" ".join(map(str, generic)))
        output = self.directory / "toy_cache_result.tsv"
        indices = [int(self.inverse[value][1:]) for value in [("S", "ae"), ("W", "et"), ("L", "j"), ("L", "k")]]
        completed = subprocess.run([str(binary), str(self.model_path), str(self.projection), str(key_path),
                                    *map(str, indices), str(38 + self.pools["wholeword_pool"].index("longissimo")), str(output)],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("CROSS_ROLE_SWAPS\t2000", completed.stdout)
        key, scores, proposals = self.runner.parse_result(output, "BLIND")
        self.assertGreaterEqual(proposals, 4000)
        independently_scored = self.score(key)
        self.assertAlmostEqual(scores["total_nats"], independently_scored["total_nats"], places=8)


if __name__ == "__main__":
    unittest.main()

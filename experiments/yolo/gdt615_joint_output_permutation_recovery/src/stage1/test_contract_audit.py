#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

if __package__:
    from .contract_audit import DECISION_INFEASIBLE, audit
else:
    from contract_audit import DECISION_INFEASIBLE, audit


HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / ".git").exists())


class ContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit(ROOT)

    def test_hash_bound_replay_and_decision(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(self.result["decision"], DECISION_INFEASIBLE)
        self.assertEqual(self.result["stage0_replay"]["mapping_rows"], 34)
        self.assertEqual(self.result["stage0_replay"]["merge_rows"], 64)
        self.assertEqual(self.result["stage0_replay"]["raw_supported_count"], 55)
        self.assertEqual(self.result["stage0_replay"]["raw_unsupported_count"], 9)
        self.assertTrue(all(row["hash_match"] for row in self.result["input_hashes"]))

    def test_every_unsupported_merge_has_both_cases_and_Ey_is_minimal(self):
        rows = self.result["two_case_audit"]
        self.assertEqual(len(rows), 9)
        for row in rows:
            self.assertIn("default_case", row)
            self.assertIn("paid_case", row)
            self.assertTrue(row["paid_or_default_case_partition_is_complete"])
            self.assertFalse(row["raw_composition_in_train_substrings"])

        witnesses = self.result["minimal_witnesses"]
        self.assertEqual(len(witnesses), 1)
        witness = witnesses[0]
        self.assertEqual(witness["rank"], 14)
        self.assertEqual(witness["merge"], "Ey")
        self.assertEqual(witness["left_child"], "E")
        self.assertEqual(witness["right_child"], "y")
        self.assertEqual(witness["raw_unoverridden_child_composition"], "hoi")
        self.assertEqual(witness["inclusive_recursive_merge_subtree_ranks"], [14])
        self.assertEqual(witness["proper_merge_descendant_ranks"], [])
        self.assertEqual(witness["default_case"]["result_from_raw_absence_alone"], "IMPOSSIBLE")
        self.assertEqual(
            witness["paid_case"][
                "result_invariant_across_raw_and_effective_descendant_readings"
            ],
            "IMPOSSIBLE",
        )

    def test_only_gate_changes_remove_the_Ey_contradiction(self):
        readings = self.result["alternative_readings"]
        compatible = [row for row in readings if not row["changes_a_registered_gate"]]
        changed = [row for row in readings if row["changes_a_registered_gate"]]
        self.assertTrue(compatible)
        self.assertTrue(changed)
        self.assertTrue(
            all(not row["removes_the_singleton_Ey_contradiction"] for row in compatible)
        )
        self.assertTrue(
            all(row["removes_the_singleton_Ey_contradiction"] for row in changed)
        )


if __name__ == "__main__":
    unittest.main()

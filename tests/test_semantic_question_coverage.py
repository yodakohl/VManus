import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import semantic_question_coverage as coverage


class _Connection:
    def close(self):
        pass


class SemanticQuestionCoverageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.cards = [
            {"id": "SEM:source", "claim": "source only", "claim_type": "semantic_model",
             "cases": [{"id": "CASE:source"}]},
            {"id": "SEM:assessed", "claim": "assessed claim", "claim_type": "semantic_model",
             "cases": [{"id": "CASE:assessed"}]},
            {"id": "SEM:formal", "claim": "formal claim", "claim_type": "formal_role",
             "cases": [{"id": "CASE:formal"}]},
            {"id": "SEM:other", "claim": "other assessed", "claim_type": "lexical_hypothesis",
             "cases": [{"id": "CASE:other"}]},
        ]
        self.failure_rows = [{"id": "FAIL:1:v1", "decision_key": "Q:1", "previous_revision": None, "targets": ["SEM:assessed"]}, {"id": "FAIL:2:v1", "decision_key": "Q:2", "previous_revision": None, "targets": ["SEM:other"]}, {"id": "FAIL:formal:v1", "decision_key": "Q:F", "previous_revision": None, "targets": ["SEM:formal"]}]
        self.assessments = {
            "SEM:source": [],
            "SEM:assessed": [{"id": "FAIL:1:v1", "decision_key": "Q:1", "targets": ["SEM:assessed"]}],
            "SEM:formal": [{"id": "FAIL:formal:v1", "decision_key": "Q:F", "targets": ["SEM:formal"]}],
            "SEM:other": [{"id": "FAIL:2:v1", "decision_key": "Q:2", "targets": ["SEM:other"]}],
        }

    def run_view(self, *args, **kwargs):
        def scoped(_root, card):
            return self.assessments[card["id"]]
        def read_rows(path):
            return self.failure_rows if str(path).endswith("semantic_failure_decisions.jsonl") else self.cards
        with patch.object(coverage.registry, "read_jsonl", side_effect=read_rows), \
             patch.object(coverage.ideas, "connect", return_value=_Connection()), \
             patch.object(coverage.ideas, "scoped_assessments", side_effect=scoped):
            return coverage.get_page(self.root, *args, **kwargs)

    def test_source_case_only_is_reported_without_question(self):
        result = self.run_view(without_question=True)
        source = next(x for x in result["results"] if x["id"] == "SEM:source")
        self.assertEqual(source["source_case_count"], 1)
        self.assertEqual(source["scoped_question_ids"], [])

    def test_default_includes_source_case_only(self):
        result = self.run_view()
        self.assertIn("SEM:source", {x["id"] for x in result["results"]})

    def test_without_question_selects_only_unassessed(self):
        result = self.run_view(without_question=True)
        self.assertEqual({x["id"] for x in result["results"]}, {"SEM:source"})

    def test_formal_default_excluded_and_include_formal_restores_it(self):
        self.assertNotIn("SEM:formal", {x["id"] for x in self.run_view()["results"]})
        self.assertIn("SEM:formal", {x["id"] for x in self.run_view(include_formal=True)["results"]})
        self.assertNotIn("SEM:formal", {x["id"] for x in self.run_view(without_question=True)["results"]})
        self.assertEqual({x["id"] for x in self.run_view(without_question=True, include_formal=True)["results"]}, {"SEM:source"})

    def test_filter_precedes_pagination(self):
        result = self.run_view("assessed", limit=1, offset=0)
        self.assertEqual(result["matched"], 2)
        self.assertEqual(result["results"][0]["id"], "SEM:assessed")
        self.assertEqual(result["next_offset"], 1)

    def test_question_without_targets_is_rejected(self):
        self.failure_rows[0]["targets"] = []
        with self.assertRaisesRegex(ValueError, "at least one target"):
            self.run_view("no-match")

    def test_shared_question_counts_bindings_and_question_separately(self):
        shared = {"id": "FAIL:shared:v1", "decision_key": "Q:shared",
                  "previous_revision": None,
                  "targets": ["SEM:assessed", "SEM:other"]}
        self.failure_rows = [shared]
        self.assessments["SEM:assessed"] = [shared]
        self.assessments["SEM:other"] = [shared]
        result = self.run_view()
        self.assertEqual(result["card_question_binding_count"], 2)
        self.assertEqual(result["unique_scoped_question_count"], 1)

    def test_stale_or_dangling_binding_is_not_silently_omitted(self):
        def broken(_root, _card):
            raise ValueError("stale scoped assessment")
        def read_rows(path):
            return self.failure_rows if str(path).endswith("semantic_failure_decisions.jsonl") else self.cards
        with patch.object(coverage.registry, "read_jsonl", side_effect=read_rows), \
             patch.object(coverage.ideas, "connect", return_value=_Connection()), \
             patch.object(coverage.ideas, "scoped_assessments", side_effect=broken):
            with self.assertRaisesRegex(ValueError, "stale"):
                coverage.get_page(self.root, without_question=True)

class SemanticQuestionCoverageRealBindingTests(unittest.TestCase):
    def test_real_public_binding_rejects_stale_card(self):
        from tools import semantic_ideas, semantic_identity
        card = {"id": "SEM:fixture", "claim": "fixture meaning",
                "claim_type": "lexical_hypothesis", "member_ids": [],
                "evidence": [], "cases": []}
        decision = {"id": "Q:fixture:v1", "decision_key": "Q:fixture",
                    "previous_revision": None, "targets": [card["id"]],
                    "status": "reviewed_scoped_context",
                    "card_basis": {card["id"]: semantic_ideas.card_basis(card)},
                    "effective_basis": {card["id"]: semantic_identity.effective_basis(card)}}
        altered = dict(card, claim="changed fixture meaning")

        class FakeConnection:
            def execute(self, sql, args=()):
                class Result:
                    def fetchone(inner):
                        return (json.dumps(altered),)
                return Result()
            def close(self):
                pass

        with patch.object(semantic_ideas, "connect", return_value=FakeConnection()), \
             patch.object(coverage.registry, "read_jsonl", return_value=[decision]):
            with self.assertRaisesRegex(ValueError, "stale scoped assessment"):
                semantic_ideas.scoped_assessments(Path("."), card)

    def test_dangling_target_is_rejected_before_filtering(self):
        from unittest.mock import patch
        failures = [{"id": "FAIL:dangling:v1", "decision_key": "Q:dangling",
                     "previous_revision": None, "targets": ["SEM:missing"]}]
        cards = [{"id": "SEM:present", "claim": "present claim",
                  "claim_type": "semantic_model", "cases": [{"id": "CASE:present"}]}]
        def read_rows(path):
            return failures if str(path).endswith("semantic_failure_decisions.jsonl") else cards
        with patch.object(coverage.registry, "read_jsonl", side_effect=read_rows), \
             patch.object(coverage.ideas, "connect", return_value=_Connection()):
            with self.assertRaisesRegex(ValueError, "target is missing"):
                coverage.get_page(Path("."), query="no-match", without_question=True)


if __name__ == "__main__":
    unittest.main()

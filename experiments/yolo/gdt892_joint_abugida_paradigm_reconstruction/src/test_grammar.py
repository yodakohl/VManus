"""Invented-tree checks for the independently implemented grammar component."""

import importlib.util
from itertools import product
import json
from pathlib import Path
import unittest


_SPEC = importlib.util.spec_from_file_location("gdt892_grammar", Path(__file__).with_name("grammar.py"))
grammar = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(grammar)


def word(word_id, head, upos, **feats):
    return {"id": word_id, "form": "invented", "lemma": "invented", "upos": upos,
            "feats": feats, "head": head, "deprel": "root" if head == 0 else "dep"}


def lattice(*words):
    return [{grammar.tag_of(item)} for item in words]


class GrammarTests(unittest.TestCase):
    def setUp(self):
        self.subject = word(1, 2, "NOUN", Case="Nom", Number="Sing")
        self.verb = word(2, 0, "VERB", Number="Sing", Person="3", VerbForm="Fin", Mood="Ind")
        self.object = word(3, 2, "NOUN", Case="Acc", Number="Sing")
        self.sentence = {"id": "invented-transitive", "words": [self.subject, self.verb, self.object]}
        self.g = grammar.build_grammar([self.sentence])

    def test_registered_projection_and_missing_fields(self):
        self.assertEqual(grammar.tag_of(self.subject), ("NOUN", "Nom", "Sing", "_", "_", "_"))
        richer = dict(self.subject, feats=dict(self.subject["feats"], Gender="Fem", Tense="Past"))
        self.assertEqual(grammar.tag_of(richer), grammar.tag_of(self.subject))

    def test_complete_source_sentence_is_recognized(self):
        self.assertTrue(grammar.accepts(self.g, lattice(self.subject, self.verb, self.object)))
        self.assertFalse(grammar.accepts(self.g, lattice(self.subject, self.verb)))
        self.assertFalse(grammar.accepts(self.g, lattice(self.verb, self.object)))

    def test_ambiguous_whole_analyses_are_alternatives(self):
        ambiguous = lattice(self.object, self.verb, self.object)
        ambiguous[0].add(grammar.tag_of(self.subject))
        self.assertTrue(grammar.accepts(self.g, ambiguous))
        ambiguous[0].remove(grammar.tag_of(self.subject))
        self.assertFalse(grammar.accepts(self.g, ambiguous))

    def test_fields_are_not_crossed_between_analyses(self):
        wrong_case = word(1, 2, "NOUN", Case="Acc", Number="Sing")
        wrong_number = word(1, 2, "NOUN", Case="Nom", Number="Plur")
        candidate = lattice(self.subject, self.verb, self.object)
        candidate[0] = {grammar.tag_of(wrong_case), grammar.tag_of(wrong_number)}
        self.assertFalse(grammar.accepts(self.g, candidate))

    def test_negative_order_and_extra_word(self):
        self.assertFalse(grammar.accepts(self.g, lattice(self.object, self.verb, self.subject)))
        self.assertFalse(grammar.accepts(self.g, lattice(self.subject, self.object, self.verb)))
        self.assertFalse(grammar.accepts(self.g, lattice(self.subject, self.verb, self.object, self.subject)))

    def test_paragraph_concatenation_consumes_complete_sentences(self):
        candidate = lattice(self.subject, self.verb, self.object) * 3
        self.assertTrue(grammar.accepts(self.g, candidate))
        self.assertFalse(grammar.accepts(self.g, candidate[:-1]))

    def test_source_provenance_and_json_roundtrip(self):
        copied = json.loads(json.dumps(self.g))
        self.assertTrue(grammar.accepts(copied, lattice(self.subject, self.verb, self.object)))
        for rule in copied["productions"]:
            self.assertEqual(rule["source_sentence_ids"], ["invented-transitive"])
        self.assertEqual({row["kind"] for row in copied["productions"]},
                         {"dependency", "sentence_root", "paragraph_concatenation"})

    def test_rules_merge_provenance_without_lexicalization(self):
        second = json.loads(json.dumps(self.sentence))
        second["id"] = "invented-other-lexemes"
        for item in second["words"]:
            item["lemma"] = item["form"] = "different"
        combined = grammar.build_grammar([self.sentence, second])
        self.assertEqual(len(combined["productions"]), len(self.g["productions"]))
        for rule in combined["productions"]:
            self.assertEqual(rule["source_sentence_ids"],
                             ["invented-other-lexemes", "invented-transitive"])

    def test_nonprojective_complete_tree_is_excluded(self):
        # 1->3 crosses 2->4; subtree rooted at3 has positions1,3.
        bad = {"id": "crossed", "words": [word(1, 3, "NOUN"), word(2, 4, "NOUN"),
                                                 word(3, 0, "VERB"), word(4, 3, "NOUN")]}
        g = grammar.build_grammar([bad, self.sentence])
        self.assertEqual(g["excluded_sentences"], [{"id": "crossed", "reason": "nonprojective"}])
        self.assertEqual(g["source_sentence_ids"], ["invented-transitive"])

    def test_missing_punctuation_head_is_not_reattached(self):
        # Original token2 has been removed; token3 must not be reattached to1.
        bad = {"id": "removed-head", "words": [word(1, 0, "VERB"), word(3, 2, "NOUN")]}
        g = grammar.build_grammar([bad])
        self.assertEqual(g["excluded_sentences"], [{"id": "removed-head", "reason": "missing_head"}])
        self.assertFalse(grammar.accepts(g, lattice(word(1, 0, "VERB"))))

    def test_nonconsecutive_ids_with_intact_heads_are_allowed(self):
        valid = {"id": "punctuation-gap", "words": [word(1, 3, "NOUN"), word(3, 0, "VERB")]}
        g = grammar.build_grammar([valid])
        self.assertEqual(g["counts"]["included_sentences"], 1)
        self.assertTrue(grammar.accepts(g, lattice(*valid["words"])))

    def test_disconnected_cycle_is_excluded(self):
        bad = {"id": "cycle", "words": [word(1, 0, "VERB"), word(2, 3, "NOUN"), word(3, 2, "NOUN")]}
        self.assertEqual(grammar.build_grammar([bad])["excluded_sentences"][0]["reason"], "cycle")

    def test_root_and_id_integrity(self):
        fixtures = [
            ("roots", [word(1, 0, "NOUN"), word(2, 0, "VERB")], "root_count"),
            ("duplicate", [word(1, 0, "NOUN"), word(1, 0, "VERB")], "duplicate_word_id"),
            ("self", [word(1, 1, "NOUN")], "self_head"),
            ("order", [word(2, 0, "VERB"), word(1, 2, "NOUN")], "non_source_order"),
        ]
        for name, words, reason in fixtures:
            with self.subTest(name=name):
                g = grammar.build_grammar([{"id": name, "words": words}])
                self.assertEqual(g["excluded_sentences"][0]["reason"], reason)

    def test_real_left_recursion_terminates_and_generalizes(self):
        leaf = word(1, 0, "NOUN", Case="Nom")
        recursive = {"id": "left-recursive", "words": [word(1, 2, "NOUN", Case="Nom"),
                                                               word(2, 0, "NOUN", Case="Nom")]}
        g = grammar.build_grammar([{"id": "leaf", "words": [leaf]}, recursive])
        tag_id = g["tags"].index(list(grammar.tag_of(leaf)))
        self.assertTrue(any(rule["lhs"] == tag_id and rule["rhs"] == [["N", tag_id], ["T", tag_id]]
                            for rule in g["productions"]))
        self.assertTrue(grammar.accepts(g, lattice(leaf) * 12))
        self.assertFalse(grammar.accepts(g, lattice(leaf) * 5 + lattice(self.verb)))

    def test_unknown_empty_and_invalid_analyses(self):
        self.assertFalse(grammar.accepts(self.g, []))
        self.assertFalse(grammar.accepts(self.g, [set()]))
        with self.assertRaises(ValueError):
            grammar.accepts(self.g, [{("NOUN",)}])

    def test_duplicate_source_ids_are_provenance_error(self):
        with self.assertRaises(ValueError):
            grammar.build_grammar([self.sentence, self.sentence])

    def test_earley_matches_independent_bounded_language_enumeration(self):
        leaf = word(1, 0, "NOUN", Case="Nom", Number="Sing")
        recursive = {"id": "recursive", "words": [dict(leaf, head=2), dict(leaf, id=2)]}
        g = grammar.build_grammar([self.sentence, {"id": "leaf", "words": [leaf]}, recursive])
        maximum = 5
        languages = [set() for _ in g["by_lhs"]]
        changed = True
        # Independently enumerate terminal strings by expanding whole CFG
        # productions to a fixed point; this uses no Earley chart or states.
        while changed:
            changed = False
            for rule in g["productions"]:
                options = [({(value,)} if kind == "T" else set(languages[value]))
                           for kind, value in rule["rhs"]]
                for pieces in product(*options):
                    value = tuple(item for piece in pieces for item in piece)
                    if len(value) <= maximum and value not in languages[rule["lhs"]]:
                        languages[rule["lhs"]].add(value)
                        changed = True
        for length in range(1, maximum + 1):
            for sequence in product(range(len(g["tags"])), repeat=length):
                analyses = [{tuple(g["tags"][tag])} for tag in sequence]
                self.assertEqual(grammar.accepts(g, analyses), sequence in languages[g["start"]], sequence)
        alternatives = list(range(1, 1 << len(g["tags"])))
        for masks in product(alternatives, repeat=3):
            domains = [{index for index in range(len(g["tags"])) if mask & (1 << index)} for mask in masks]
            expected = any(sequence in languages[g["start"]] for sequence in product(*domains))
            analyses = [{tuple(g["tags"][tag]) for tag in domain} for domain in domains]
            self.assertEqual(grammar.accepts(g, analyses), expected, masks)

    def test_projectivity_matches_independent_arc_crossings(self):
        # Include artificial root0 in the crossing criterion.  This also
        # catches an arc passing over a root/head outside its own subtree.
        for heads in product(range(5), repeat=4):
            if sum(head == 0 for head in heads) != 1:
                continue
            intact = True
            for start in range(1, 5):
                path = set()
                current = start
                while current:
                    if current in path:
                        intact = False
                        break
                    path.add(current)
                    current = heads[current - 1]
                if not intact:
                    break
            if not intact:
                continue
            arcs = [tuple(sorted((index + 1, head))) for index, head in enumerate(heads)]
            crossing = any(a < c < b < d or c < a < d < b
                           for a, b in arcs for c, d in arcs)
            sentence = {"id": "arc-fixture", "words": [word(index + 1, head, "NOUN")
                                                          for index, head in enumerate(heads)]}
            checked, reason = grammar._checked_tree(sentence)
            self.assertEqual(checked is not None, not crossing, heads)
            if crossing:
                self.assertEqual(reason, "nonprojective")


if __name__ == "__main__":
    unittest.main()

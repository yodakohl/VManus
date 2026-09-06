"""Explicit identity is constrained, source-bound navigation, never meaning proof."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from tools import semantic_identity as identity


class SemanticIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.report = self.root / 'report.md'
        self.report.write_text('The two proposed glosses are the same.\nA rival stays distinct.\n')
        self.cards = [self.card(x) for x in ('A', 'B', 'C', 'D')]
        self.log = self.root / 'decisions.jsonl'

    def card(self, identifier):
        return {'id': identifier, 'claim': identifier + ' proposed gloss',
                'claim_type': 'lexical_hypothesis', 'member_ids': ['SOURCE:' + identifier],
                'evidence': [{'path': 'report.md', 'line': 1,
                              'quote': 'The two proposed glosses are the same.'}],
                'cases': [], 'status': 'unconfirmed', 'ready': False}

    def decision(self, identifier, members, relation='equivalent_proposition',
                 status='approved', key=None, previous=None):
        by_id = {c['id']: c for c in self.cards}
        return {'id': identifier, 'decision_key': key or identifier,
                'previous_revision': previous, 'relation': relation, 'status': status,
                'member_ids': list(members), 'reviewer': 'independent reviewer',
                'reason': 'The exact source states the same scoped proposition.',
                'card_basis': {i: identity.original_basis(by_id[i]) for i in members},
                'effective_basis': {i: identity.effective_basis(by_id[i]) for i in members},
                'evidence': [{'path': 'report.md', 'line': 1,
                              'quote': 'The two proposed glosses are the same.',
                              'sha256': hashlib.sha256(self.report.read_bytes()).hexdigest()}]}

    def index(self, decisions, **kwargs):
        return identity.build_index(self.cards, decisions, self.root, **kwargs)

    def test_only_approved_equivalence_and_no_card_mutation(self):
        original = copy.deepcopy(self.cards)
        ds = [self.decision('ab', 'AB'), self.decision('bc', 'BC', status='proposed'),
              self.decision('cd', 'CD', relation='specializes')]
        index = self.index(ds)
        mapping = index.lookup_cards('ABCD')
        self.assertEqual(mapping['A'], mapping['B'])
        self.assertNotEqual(mapping['B'], mapping['C'])
        self.assertNotEqual(mapping['C'], mapping['D'])
        self.assertEqual(self.cards, original)
        self.assertEqual(index.page_relations()[0]['relation'], 'specializes')
        self.assertNotIn('status', index.get_group(mapping['A']))

    def test_transitive_nonidentity_blockers_both_orders(self):
        for relation in ('alternative_to', 'related_not_equivalent'):
            ds = [self.decision('ab', 'AB'), self.decision('bc', 'BC'),
                  self.decision('ac', 'AC', relation=relation)]
            for ordered in (ds, list(reversed(ds))):
                with self.subTest(relation=relation), self.assertRaisesRegex(ValueError, 'nonidentity'):
                    self.index(ordered)
        # Rejected equivalence does not impose a nonidentity edge.
        self.index([self.decision('ab', 'AB'), self.decision('bc', 'BC'),
                    self.decision('ac', 'AC', status='rejected')])

    def test_append_revision_preserves_history_and_retracts_union(self):
        first = self.decision('r1', 'AB', key='pair-ab')
        identity.append_decision(self.root, self.log, first, self.cards)
        old = self.log.read_bytes()
        second = self.decision('r2', 'AB', status='rejected', key='pair-ab', previous='r1')
        identity.append_decision(self.root, self.log, second, self.cards)
        self.assertTrue(self.log.read_bytes().startswith(old))
        rows = identity.read_decisions(self.log)
        self.assertEqual(len(rows), 2)
        index = self.index(rows)
        self.assertNotEqual(index.lookup_cards('AB')['A'], index.lookup_cards('AB')['B'])
        with self.assertRaisesRegex(ValueError, 'revision chain'):
            self.index([first, self.decision('r3', 'AB', key='pair-ab')])

    def test_invalid_append_has_no_partial_log(self):
        identity.append_decision(self.root, self.log, self.decision('ab', 'AB'), self.cards)
        identity.append_decision(self.root, self.log, self.decision('bc', 'BC'), self.cards)
        old = self.log.read_bytes()
        with self.assertRaisesRegex(ValueError, 'nonidentity'):
            identity.append_decision(self.root, self.log,
                                     self.decision('ac', 'AC', relation='alternative_to'), self.cards)
        self.assertEqual(self.log.read_bytes(), old)

    def test_original_and_effective_basis_fail_closed(self):
        decision = self.decision('ab', 'AB')
        original = copy.deepcopy(self.cards)
        self.cards[0]['cases'].append({'scope': 'q13 only'})
        with self.assertRaisesRegex(ValueError, 'original card basis'):
            self.index([decision])
        self.cards = original
        self.cards[0]['source_original_assertion'] = {'claim': self.cards[0]['claim'],
                                                      'claim_type': self.cards[0]['claim_type']}
        self.cards[0]['claim'] = 'a different effective scoped claim'
        self.assertEqual(identity.original_basis(self.cards[0]), decision['card_basis']['A'])
        with self.assertRaisesRegex(ValueError, 'effective proposition'):
            self.index([decision])

    def test_source_hash_quote_and_path_validation(self):
        d = self.decision('ab', 'AB')
        bad = copy.deepcopy(d); bad['evidence'][0]['quote'] = 'invented'
        with self.assertRaisesRegex(ValueError, 'inexact'):
            self.index([bad])
        bad = copy.deepcopy(d); bad['evidence'][0]['path'] = '../private.md'
        with self.assertRaisesRegex(ValueError, 'within root'):
            self.index([bad])
        self.report.write_text('Changed source.\n')
        with self.assertRaisesRegex(ValueError, 'stale evidence'):
            self.index([d])

    def test_exact_lines_reject_prefix_and_accept_bom_multiline_newline(self):
        decision = self.decision('ab', 'AB')
        decision['evidence'][0]['quote'] = 'The two proposed'
        with self.assertRaisesRegex(ValueError, 'inexact source quote'):
            self.index([decision])
        self.report.write_bytes(b'\xef\xbb\xbfFirst full line.\nSecond full line.\n')
        decision['evidence'][0].update(
            quote='First full line.\nSecond full line.\n',
            sha256=hashlib.sha256(self.report.read_bytes()).hexdigest())
        self.index([decision])
        decision['evidence'][0]['quote'] = 'First full line.\nSecond full'
        with self.assertRaisesRegex(ValueError, 'inexact source quote'):
            self.index([decision])

    def test_archive_disables_entire_judgment_without_invented_subgroup(self):
        d = self.decision('abc', 'ABC')
        index = self.index([d], archived_ids={'B'})
        mapping = index.lookup_cards('ABC')
        self.assertIsNone(mapping['B'])
        self.assertNotEqual(mapping['A'], mapping['C'])
        self.assertEqual(index.inactive_decision_ids, ('abc',))
        self.cards = [c for c in self.cards if c['id'] != 'B']
        self.index([d], archived_ids={'B'})

    def test_schema_unknown_cards_duplicate_ids_and_independent_keys(self):
        d = self.decision('ab', 'AB')
        with self.assertRaisesRegex(ValueError, 'duplicate decision'):
            self.index([d, d])
        bad = copy.deepcopy(d); bad['member_ids'] = ['A', 'A']
        with self.assertRaisesRegex(ValueError, 'duplicate member'):
            self.index([bad])
        self.cards = [c for c in self.cards if c['id'] != 'B']
        with self.assertRaisesRegex(ValueError, 'unknown decision card'):
            self.index([d])

    def test_ten_thousand_card_navigation_is_bounded_and_deterministic(self):
        cards = [self.card(f'CARD{i:05}') for i in range(10000)]
        a = identity.build_index(cards, [], self.root)
        b = identity.build_index(reversed(cards), [], self.root)
        self.assertEqual(a.counts['groups'], 10000)
        self.assertEqual(a.page_groups(5000, 8), b.page_groups(5000, 8))
        self.assertEqual(len(a.page_groups(5000, 8)), 8)
        with self.assertRaises(ValueError):
            a.page_groups(limit=101)
        with self.assertRaises(ValueError):
            a.lookup_cards([c['id'] for c in cards[:101]])
        group = a.page_groups()[0]['id']
        self.assertEqual(len(a.get_group(group)['member_ids']), 1)


if __name__ == '__main__':
    unittest.main()

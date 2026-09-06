"""Source assessments stay contextual; local and indexed views retain their contracts."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import semantic_ideas as ideas


class SemanticIdeasContextTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'reports').mkdir()
        (self.root / 'reports/gdt123_proposal.md').write_text('A candidate denotes powder.\n')
        (self.root / 'reports/gdt124_proposal.md').write_text('A candidate denotes powder.\n')
        (self.root / 'research_registry/decisions').mkdir(parents=True)
        self.inventory = self.root / 'research_registry/semantic_inventory.jsonl'
        records = [
            {'id': 'SOURCE1'}, {'id': 'SOURCE2'},
            {'id': 'GDT123', 'title': 'A bounded source experiment',
             'review_status': 'reviewed', 'source_status': 'capacity_stop',
             'blockers': ['No independent paired observation'],
             'reopen': {'policy': 'all_of', 'all_of': ['An independent owned pair'],
                        'not_sufficient': ['A different model fit']}},
            {'id': 'GDT124', 'title': 'Another source experiment',
             'source_status': 'source_report_rejected', 'blockers': ['Failed control'],
             'reopen': {'policy': 'new_data_only', 'all_of': ['New source evidence']}},
        ]
        self.inventory.write_text(''.join(json.dumps(r) + '\n' for r in records))
        for relative in ideas.REVIEWS:
            (self.root / relative).write_text(json.dumps({'cards': [], 'dispositions': []}))

    def card(self, identifier='CARD1', source='SOURCE1', experiment=123, **overrides):
        result = dict(
            id=identifier, claim='The candidate denotes powder.',
            claim_type='lexical_hypothesis', member_ids=[source],
            evidence=[dict(path=f'reports/gdt{experiment}_proposal.md', line=1,
                           quote='A candidate denotes powder.')],
            status='unconfirmed', ready=False,
            scope={'register': 'Herbal', 'test_contract': f'GDT{experiment}'},
        )
        result.update(overrides)
        return result

    def build(self, cards):
        (self.root / ideas.REVIEWS[0]).write_text(
            json.dumps({'cards': cards, 'dispositions': []}))
        return ideas.build(self.root)

    def test_assessment_cli_keeps_blockers_and_gates_contextual(self):
        self.build([self.card()])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            ideas.main(['--show', 'CARD1', '--field', 'assessments'], root=self.root)
        result = json.loads(output.getvalue())
        self.assertEqual(result['matched'], 1)
        self.assertIn('not automatic verdicts', result['scope'])
        assessment = result['items'][0]
        self.assertEqual(assessment['id'], 'GDT123')
        self.assertEqual(assessment['blockers'], ['No independent paired observation'])
        self.assertEqual(assessment['reopen']['all_of'], ['An independent owned pair'])
        self.assertEqual(assessment['reopen']['not_sufficient'], ['A different model fit'])
        claim = ideas.show(self.root, 'CARD1')
        self.assertEqual(claim['status'], 'unconfirmed')
        self.assertIs(claim['ready'], False)
        self.assertNotIn('blockers', claim)
        self.assertNotIn('reopen', claim)

    def test_same_assertion_preserves_conflicting_source_scopes_and_assessments(self):
        second = self.card('CARD2', 'SOURCE2', 124,
                           scope={'register': 'Biological', 'test_contract': 'GDT124'},
                           source_polarity='source_report_rejected',
                           failure_reason='Failed control under the second source contract.')
        self.build([self.card(), second])
        row = ideas.get_page(self.root)['results'][0]
        self.assertEqual(row['status'], 'unconfirmed')
        cases = ideas.show(self.root, row['id'], field='cases')['items']
        self.assertEqual({c['scope']['register'] for c in cases}, {'Herbal', 'Biological'})
        rejected = next(c for c in cases if c['id'] == 'CARD2')
        self.assertEqual(rejected['failure_reason'], second['failure_reason'])
        assessments = ideas.show(self.root, row['id'], field='assessments')['items']
        self.assertEqual({a['source_status'] for a in assessments},
                         {'capacity_stop', 'source_report_rejected'})
        self.assertNotIn('failure_reason', ideas.show(self.root, row['id']))

    def test_local_rejected_status_survives_and_stale_local_quote_blocks_cached_view(self):
        self.build([])
        runtime = self.root / 'research_registry/runtime'
        runtime.mkdir()
        source = self.root / 'reports/local_proposal.md'
        source.write_text('The local candidate denotes a root.\n')
        local = self.card('LOCAL1', 'LOCAL_SOURCE',
                          claim='The local candidate denotes a root.',
                          status='source_report_rejected',
                          evidence=[dict(path='reports/local_proposal.md', line=1,
                                         quote='The local candidate denotes a root.')])
        (runtime / 'clean_local_review.json').write_text(json.dumps({'cards': [local]}))
        with patch('tools.semantic_inventory.local_items', return_value=[{'id': 'LOCAL_SOURCE'}]):
            row = ideas.get_page(self.root)['results'][0]
            self.assertTrue(row['local_only'])
            self.assertEqual(row['status'], 'source_report_rejected')
            self.assertEqual(ideas.show(self.root, 'LOCAL1')['status'], 'source_report_rejected')
            source.write_text('The local candidate now denotes a leaf.\n')
            with self.assertRaisesRegex(ValueError, 'source quote mismatch'):
                ideas.get_page(self.root)

    def test_ten_thousand_claims_use_bounded_cached_index_pages(self):
        self.build([self.card(f'CARD{i:05}', claim=f'Candidate {i:05} denotes powder.')
                    for i in range(10000)])
        first = ideas.get_page(self.root, limit=20)
        self.assertEqual(first['matched'], 10000)
        self.assertEqual(len(first['results']), 20)
        read_jsonl = ideas.registry.read_jsonl

        def forbid_snapshot_materialization(path):
            if Path(path) == self.root / ideas.DATA:
                self.fail('A cached indexed page must not deserialize the complete card snapshot')
            return read_jsonl(path)

        # Hash validation still reads source bytes; this checks bounded card
        # materialization, not a misleading constant-time filesystem claim.
        with patch.object(ideas.registry, 'read_jsonl', side_effect=forbid_snapshot_materialization):
            second = ideas.get_page(self.root, limit=20, offset=first['next_offset'])
            last = ideas.get_page(self.root, limit=20, offset=9995)
            found = ideas.get_page(self.root, query='09999', limit=2)
        self.assertEqual(len(second['results']), 20)
        self.assertFalse({c['id'] for c in first['results']} & {c['id'] for c in second['results']})
        self.assertEqual(len(last['results']), 5)
        self.assertIsNone(last['next_offset'])
        self.assertEqual(found['matched'], 1)
        self.assertEqual(found['results'][0]['claim'], 'Candidate 09999 denotes powder.')


if __name__ == '__main__':
    unittest.main()

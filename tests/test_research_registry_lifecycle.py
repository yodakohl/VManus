"""Authored registry lifecycle contracts, using synthetic temporary data only."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import research_registry as registry


def imported(identifier='IP001', **updates):
    row = dict(id=identifier, kind='idea', aliases=[], title='Imported fixture',
               summary='Synthetic import only.', source_status='IMPORTED',
               scope='unknown', review_status='imported_unreviewed', verdict='unreviewed',
               blockers=[], reopen=dict(policy='unreviewed', all_of=[], not_sufficient=[]),
               relations=[], sources=[], events=[])
    row.update(updates)
    return row


class RegistryLifecycleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        registry.write_snapshot(self.root, [imported()])
        registry.build_index(self.root)
        self.proposal = dict(title='Authored fixture', summary='A synthetic proposal.',
                             design=dict(mechanism='Fixed transformation', unit='Whole group',
                                         contrast='Different inputs', prediction='Same outcome',
                                         scope='Synthetic'))

    def review(self, **updates):
        row = dict(record_id='IP001', scope='semantic', verdict='untested',
                   reason='Synthetic review rationale.', reviewer='fixture-reviewer',
                   blockers=[], relations=[],
                   reopen=dict(policy='conditional', not_sufficient=['More unqualified data'],
                               all_of=[dict(id='independent_source', change='new_data',
                                            detail='Independent source required.',
                                            evidence=['docs/report.md'],
                                            fact=dict(key='coverage', op='gte', value=3))]))
        row.update(updates)
        return row

    def evidence(self):
        path = self.root / 'docs/report.md'
        path.parent.mkdir(exist_ok=True)
        path.write_text('Synthetic source version one.\n')
        return path

    def test_add_ids_are_unique_stable_and_collision_does_not_overwrite(self):
        first = registry.add_idea(self.root, self.proposal)['id']
        second = registry.add_idea(self.root, self.proposal)['id']
        self.assertEqual((first, second), ('IDEA000001', 'IDEA000002'))
        path = self.root / registry.DIRECTORY / 'ideas.jsonl'
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            registry.add_idea(self.root, dict(self.proposal, id=first))
        self.assertEqual(path.read_bytes(), before)
        registry.build_index(self.root)
        self.assertEqual(registry.show(self.root, first)['id'], first)
        self.assertEqual(registry.show(self.root, second)['id'], second)

    def test_authored_records_survive_snapshot_and_mocked_refresh(self):
        identifier = registry.add_idea(self.root, self.proposal)['id']
        authored = self.root / registry.DIRECTORY / 'ideas.jsonl'
        before = authored.read_bytes()
        registry.write_snapshot(self.root, [imported('IP002')])
        self.assertEqual(registry.show(self.root, identifier)['id'], identifier)
        with patch('tools.research_registry_import.import_records', return_value=[imported('IP003')]) as load, \
             patch('tools.research_registry_import.import_manifest', return_value={'sources': []}) as manifest:
            registry.refresh(self.root)
        load.assert_called_once_with(self.root)
        manifest.assert_called_once_with(self.root)
        self.assertEqual(authored.read_bytes(), before)
        self.assertEqual(registry.show(self.root, identifier)['id'], identifier)
        self.assertEqual(registry.show(self.root, 'IP003')['id'], 'IP003')
        with self.assertRaises((KeyError, ValueError)):
            registry.show(self.root, 'IP002')

    def test_duplicate_design_navigation_never_merges_authored_proposals(self):
        first = registry.add_idea(self.root, self.proposal)['id']
        variant = dict(self.proposal, title='Different title, same declared design',
                       design={key: '  ' + value.upper() + '  ' for key, value in self.proposal['design'].items()})
        second = registry.add_idea(self.root, variant)['id']
        result = registry.duplicates(self.root, proposal=self.proposal)
        self.assertEqual({x['id'] for x in result['same_declared_design']}, {first, second})
        self.assertEqual(result['decision'], 'CANDIDATES_ONLY_NO_AUTOMATIC_MERGE')
        self.assertEqual(len(registry.read_jsonl(self.root / registry.DIRECTORY / 'ideas.jsonl')), 2)

    def test_review_revision_chain_retains_old_bytes_and_uses_last_decision(self):
        self.evidence()
        registry.append_review(self.root, self.review())
        path = self.root / registry.DIRECTORY / 'curation.jsonl'
        first_bytes = path.read_bytes()
        first_row = registry.read_jsonl(path)[0]
        result = registry.append_review(self.root, self.review(verdict='nonconfirming', reason='Second synthetic assessment.'))
        rows = registry.read_jsonl(path)
        self.assertTrue(path.read_bytes().startswith(first_bytes))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], first_row)
        self.assertEqual(rows[1]['previous_sha256'], hashlib.sha256(registry.canonical(first_row).encode()).hexdigest())
        self.assertTrue(result['previous_review_preserved'])
        self.assertEqual(registry.show(self.root, 'IP001')['verdict'], 'nonconfirming')
        first_page=registry.page_field(self.root,'IP001','reviews',limit=1)
        self.assertEqual(first_page['total'],2)
        self.assertEqual(first_page['next_offset'],1)
        self.assertEqual(first_page['items'][0],first_row)
        second_page=registry.page_field(self.root,'IP001','reviews',limit=1,offset=1)
        self.assertEqual(second_page['items'][0]['verdict'],'nonconfirming')
        self.assertIsNone(second_page['next_offset'])

    def test_invalid_review_rolls_back_history_and_readable_decision(self):
        self.evidence()
        registry.append_review(self.root, self.review())
        path = self.root / registry.DIRECTORY / 'curation.jsonl'
        before = path.read_bytes()
        for updates in [dict(verdict='MADE_UP_VERDICT'),
                        dict(relations=[dict(type='related_to', target='MISSING')]),
                        dict(reopen=dict(policy='invented', all_of=[], not_sufficient=[]))]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                registry.append_review(self.root, self.review(**updates))
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(registry.show(self.root, 'IP001')['verdict'], 'untested')
        self.assertEqual(registry.check_registry(self.root)['status'], 'PASS')

    def test_related_cycles_allowed_but_identity_cycle_review_rolls_back(self):
        registry.write_snapshot(self.root, [imported('IP001'), imported('IP002')])
        self.evidence()
        registry.append_review(self.root, self.review(relations=[dict(type='related_to', target='IP002')]))
        registry.append_review(self.root, self.review(record_id='IP002', relations=[dict(type='related_to', target='IP001')]))
        self.assertEqual(registry.check_registry(self.root)['status'], 'PASS')
        registry.append_review(self.root, self.review(relations=[dict(type='duplicate_of', target='IP002')]))
        path = self.root / registry.DIRECTORY / 'curation.jsonl'
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            registry.append_review(self.root, self.review(record_id='IP002', relations=[dict(type='supersedes', target='IP001')]))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(registry.check_registry(self.root)['status'], 'PASS')

    def test_changed_evidence_marks_review_stale_and_never_verifies_facts(self):
        path = self.evidence()
        registry.append_review(self.root, self.review())
        fresh = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
        self.assertEqual(fresh['decision'], 'RECONSIDERATION_REVIEW_REQUIRED')
        path.write_text('Synthetic source version two: changed claims.\n')
        stale = registry.reconsider(self.root, 'IP001', ['new_data'], ['docs/report.md'])
        self.assertEqual(stale['decision'], 'SOURCE_REVIEW_REQUIRED')
        self.assertEqual(registry.show(self.root, 'IP001')['review'], 'stale_review')
        for result in (fresh, stale):
            self.assertIs(result['approved'], False)
            self.assertTrue(result['conditions'])
            self.assertTrue(all(x['verification'] == 'UNVERIFIED_CONTENT' for x in result['conditions']))

    def test_changed_import_source_blocks_cache_until_mocked_refresh(self):
        path = self.evidence()
        manifest = {'sources': [dict(path='docs/report.md', sha256=registry.digest(path))]}
        registry.write_snapshot(self.root, [imported(title='Oldsourcefixture')], manifest)
        registry.build_index(self.root)
        path.write_text('Changed synthetic imported metadata.\n')
        with self.assertRaises(ValueError):
            registry.search(self.root, 'Oldsourcefixture')
        fresh_manifest = {'sources': [dict(path='docs/report.md', sha256=registry.digest(path))]}
        with patch('tools.research_registry_import.import_records', return_value=[imported(title='Newsourcefixture')]), \
             patch('tools.research_registry_import.import_manifest', return_value=fresh_manifest):
            registry.refresh(self.root)
        self.assertEqual([x['id'] for x in registry.search(self.root, 'Newsourcefixture')['results']], ['IP001'])
        self.assertEqual(registry.search(self.root, 'Oldsourcefixture')['results'], [])


if __name__ == '__main__':
    unittest.main()

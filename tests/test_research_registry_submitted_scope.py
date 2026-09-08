"""Submitted classification is navigation metadata, independent of review scope."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools import research_registry as registry


class SubmittedScopeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        registry.write_snapshot(self.root, [])
        self.design = dict(mechanism='Compose', unit='Whole', contrast='Override',
                           prediction='Nominated response')

    def add(self, scope='semantic'):
        return registry.add_idea(self.root, dict(title='Synthetic proposal',
            summary='Fixed lexical content.', scope=scope, design=self.design))['id']

    def review(self, identifier):
        return registry.append_review(self.root, dict(record_id=identifier,
            reviewer='test', reason='Method needs a nominated contrast.', scope='method',
            verdict='not_tested', blockers=[dict(code='missing_design')], relations=[],
            assessment_basis='primary_source_review',
            reopen=dict(policy='conditional', all_of=[], not_sufficient=['Same design'])))

    def test_review_lifecycle_preserves_canonical_fingerprints_and_fts(self):
        identifier = self.add()
        base = registry._base_records(self.root)[identifier]
        fingerprint = registry.record_fingerprint(base)
        design_hash = registry.design_fingerprint(base)
        authored = (self.root / registry.DIRECTORY / 'ideas.jsonl').read_bytes()
        self.review(identifier)
        card = registry.show(self.root, identifier)
        self.assertEqual((card['scope'], card['submitted_scope']), ('method', 'semantic'))
        self.assertEqual((card['verdict'], card['review']), ('not_tested', 'curated'))
        self.assertEqual(card['blockers'], [dict(code='missing_design')])
        self.assertEqual(card['reopen_policy'], 'conditional')
        self.assertEqual(registry.search(self.root, scope='semantic')['matched'], 0)
        self.assertEqual(registry.search(self.root, submitted_scope='semantic')['matched'], 1)
        assembled = registry._assemble(self.root)[identifier]
        self.assertNotIn('submitted_scope', assembled)
        with registry._connect(self.root) as con:
            stored = con.execute('SELECT signature,payload FROM records WHERE id=?', (identifier,)).fetchone()
            body = con.execute('SELECT body FROM search WHERE id=?', (identifier,)).fetchone()[0]
        self.assertEqual(stored['signature'], design_hash)
        self.assertEqual(json.loads(stored['payload'])['design'], self.design)
        self.assertEqual(body, registry.canonical(assembled))
        self.assertNotIn('submitted_scope', json.loads(body))
        self.review(identifier)
        reviews = registry.read_jsonl(self.root / registry.DIRECTORY / 'curation.jsonl')
        self.assertEqual(len(reviews), 2)
        self.assertIsNotNone(reviews[1]['previous_sha256'])
        self.assertTrue(all(r['basis_sha256'] == fingerprint for r in reviews))
        self.assertEqual(authored, (self.root / registry.DIRECTORY / 'ideas.jsonl').read_bytes())
        self.assertEqual(registry.record_fingerprint(registry._base_records(self.root)[identifier]), fingerprint)
        self.assertEqual(registry.show(self.root, identifier)['review'], 'curated')

    def test_intersection_pagination_and_nonsemantic_exclusions(self):
        first, second, third = [self.add() for _ in range(3)]
        structural, unknown = self.add('structural'), self.add('unknown')
        # Imported metadata is not an authored submission, even if its status mimics one.
        imported = dict(registry._base_records(self.root)[first], id='GDT999',
                        kind='attempt', source_status='NEW_PROPOSAL')
        registry.write_snapshot(self.root, [imported])
        self.review(first)
        self.review(second)
        page = registry.search(self.root, submitted_scope='semantic', scope='method',
                               blocker='missing_design', limit=1, offset=1)
        self.assertEqual(page['matched'], 2)
        self.assertEqual([r['id'] for r in page['results']], [second])
        self.assertIsNone(page['next_offset'])
        self.assertEqual(registry.search(self.root, submitted_scope='semantic', limit=1)['next_offset'], 1)
        self.assertEqual(registry.search(self.root, submitted_scope='semantic')['matched'], 3)
        self.assertEqual(registry.search(self.root, scope='semantic')['matched'], 2)
        self.assertEqual(registry.show(self.root, structural)['submitted_scope'], 'structural')
        self.assertEqual(registry.show(self.root, unknown)['submitted_scope'], 'unknown')
        self.assertNotIn('submitted_scope', registry.show(self.root, 'GDT999'))
        self.assertEqual(registry.search(self.root, submitted_scope='unknown')['matched'], 1)

    def test_cli_and_invalid_option(self):
        identifier = self.add()
        self.review(identifier)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(registry.main(['search', '--submitted-scope', 'semantic',
                                           '--scope', 'method'], root=self.root), 0)
        self.assertEqual(json.loads(output.getvalue())['results'][0]['id'], identifier)
        with self.assertRaises(ValueError):
            registry.search(self.root, submitted_scope='invented')
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            registry.main(['search', '--submitted-scope', 'invented'], root=self.root)
        self.assertEqual(caught.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
